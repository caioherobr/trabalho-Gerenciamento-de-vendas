from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import mysql.connector
import os


app = Flask(__name__)
app.secret_key = os.urandom(24)  # Chave segura para a sessão

db_config = {
    'host': 'gerenciavendas.mysql.database.azure.com',
    'user': 'adm',
    'password': 'aluno@123',
    'database': 'gerenciamento'
}


def executar_sql(comando, parametros=None):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(comando, parametros)
        conn.commit()
        return cursor
    except mysql.connector.Error as err:
        print(f"Erro: {err}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def conectar_bd():
    return mysql.connector.connect(**db_config)

@app.route("/")
def index():
    return render_template('login.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/validar', methods=['POST'])
def validar():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            conn = conectar_bd()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM usuarios WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            user = cursor.fetchone()
        except mysql.connector.Error as e:
            print(f"Erro no banco de dados: {e}")
            user = None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['user_role'] = user['role']
    
    
            if user['role'] == 'rh':
                return redirect('/rh')
            elif user['role'] in ['vendedor', 'gerente']:
                return redirect('/vendas')
            else:
                return render_template('login.html', error='Papel do usuário inválido!')
        else:
            return render_template('login.html', error='Credenciais inválidas!')

@app.route('/rh')
def rh():
    user_role = session.get('user_role')  # Obtém o papel do usuário
    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)
    if user_role=='rh':
        return render_template('rh.html')
    else:
        return redirect('/login')


@app.route('/vendas')
def todas_as_vendas():
    user_role = session.get('user_role')  # Obtém o papel do usuário
    if not user_role:
        return redirect(url_for('login'))
    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)

    vendas = []  # Inicializa a lista de vendas como vazia

    if user_role == 'vendedor':
        query = """
            SELECT usuarios.username AS vendedor, vendas.id, vendas.data, vendas.valor
            FROM vendas 
            INNER JOIN usuarios ON vendas.vendedor_id = usuarios.id
            WHERE vendedor_id = %s
            ORDER BY usuarios.username ASC
        """
        cursor.execute(query, (session['user_id'],))
        vendas = cursor.fetchall()  # Busca os resultados da consulta
    elif user_role == 'gerente':
        query = """
            SELECT usuarios.username AS vendedor, vendas.id, vendas.data, vendas.valor
            FROM vendas 
            INNER JOIN usuarios ON vendas.vendedor_id = usuarios.id
            ORDER BY usuarios.username ASC
        """
        cursor.execute(query)
        vendas = cursor.fetchall()  # Busca os resultados da consulta

    conn.close()  # Fecha a conexão com o banco de dados
    return render_template('relatorio_vendas.html', vendas=vendas)

@app.route('/rank')
def rank_vendedores():
    user_role = session.get('user_role')
    if not user_role:
        return redirect(url_for('login'))

    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT 
         DENSE_RANK() OVER (ORDER BY SUM(vendas.valor) DESC) as ranking,
        usuarios.username AS vendedor, 
        COUNT(vendas.id) AS total_vendas, 
        SUM(vendas.valor) AS valor_total 
        FROM vendas 
        INNER JOIN usuarios ON vendas.vendedor_id = usuarios.id 
        GROUP BY usuarios.username 
        ORDER BY valor_total DESC


    """
    cursor.execute(query)
    rank = cursor.fetchall()
    conn.close()
    
    return render_template('rank_vendedores.html', rank=rank)


@app.route('/total')
def total_vendas():
    user_role = session.get('user_role')
    if not user_role:
        return redirect(url_for('login'))  # Redireciona para login se o papel não estiver na sessão

    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)

    if user_role == 'gerente':
        query = """
            SELECT SUM(valor) AS total_geral, COUNT(id) AS total_vendas
            FROM vendas
        """
        cursor.execute(query)
    elif user_role == 'vendedor':
        query = """
            SELECT SUM(valor) AS total_geral, COUNT(id) AS total_vendas
            FROM vendas
            WHERE vendedor_id = %s
        """
        cursor.execute(query, (session['user_id'],))  # Passa o vendedor_id do usuário atual
    else:
        return redirect(url_for('login'))  # Redireciona para login se o papel for inválido

    total = cursor.fetchone()
    conn.close()
    return render_template('total_geral.html', total=total)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/atualizar', methods=['POST'])
def atualizar_senha():
    # Recebe os dados em formato JSON da requisição AJAX
    data = request.get_json()

    username = data['username']
    nova_senha = data['password']
    
    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)
    
    # Consulta SQL para atualizar a senha do usuário
    sql = "UPDATE usuarios SET password = %s WHERE username = %s"
    
    try:
        cursor.execute(sql, (nova_senha, username))
        
        if cursor.rowcount > 0:  # Se a atualização afetou alguma linha
            conn.commit()  # Commit da transação
            return jsonify({"message": f"Senha do usuário '{username}' atualizada com sucesso para '{nova_senha}'."})
        else:
            return jsonify({"message": "Usuário não encontrado ou nenhum dado alterado."})
    
    except Exception as e:
        conn.rollback()  # Reverte qualquer mudança não confirmada
        return jsonify({"message": f"Erro ao tentar atualizar a senha: {str(e)}"})
    
    finally:
        cursor.close()
        conn.close()

    
@app.route('/consultar', methods=['POST'])
def consultar_usuario():
    userInput = request.form.get('userInput')  # Corrigido para 'userInput'

    # Verifica se o username foi enviado
    if not userInput:
        return jsonify({"erro": "O campo username é obrigatório."}), 400

    try:
        # Conectar ao banco de dados
        conn = conectar_bd()
        cursor = conn.cursor(dictionary=True)

        # Consulta SQL
        sql = "SELECT username, password, role FROM usuarios WHERE username = %s"
        cursor.execute(sql, (userInput,))  # Usamos 'userInput' aqui
        usuario = cursor.fetchone()

        # Fechar conexão
        cursor.close()
        conn.close()

        # Verificar se o usuário foi encontrado
        if usuario:
            return jsonify({
                "username": usuario["username"],
                "password": usuario["password"],
                "role": usuario["role"]
            })

        # Usuário não encontrado
        return jsonify({"erro": "Usuário não encontrado."}), 404

    except Exception as e:
        return jsonify({"erro": f"Erro ao consultar o banco de dados: {str(e)}"}), 500



@app.route('/deletar', methods=['POST'])
def deletar_usuario():
    # Recebe o JSON enviado pelo frontend
    data = request.get_json()  # Aqui usamos get_json para acessar o conteúdo JSON
    username = data.get('usernamedel')  # Acessa o campo 'usernamedel'

    if not username:
        return jsonify({"message": "O nome de usuário é obrigatório!"}), 400

    try:
        # Conectar ao banco de dados
        conn = conectar_bd()
        cursor = conn.cursor(dictionary=True)

        # Consulta SQL para verificar se o usuário existe
        sql = "SELECT username, password, role FROM usuarios WHERE username = %s"
        cursor.execute(sql, (username,))
        usuario = cursor.fetchone()

        # Verifica se o usuário foi encontrado
        if not usuario:
            cursor.close()
            conn.close()
            return jsonify({"message": "Usuário não encontrado."}), 404

        # Deletar o usuário
        sql = "DELETE FROM usuarios WHERE username = %s"

        cursor.execute(sql, (username,))
        conn.commit()  # Commit da transação

        if cursor.rowcount > 0:
            cursor.close()
            conn.close()
            return jsonify({"message": f"Usuário '{username}' deletado com sucesso!"}), 200
        else:
            cursor.close()
            conn.close()
            return jsonify({"message": "Erro ao deletar usuário."}), 500

    except Exception as e:
        # Se houver algum erro, retorna uma mensagem de erro genérica
        return jsonify({"message": f"Erro ao processar a solicitação: {str(e)}"}), 500


@app.route('/addvendedor', methods=['POST'])
def adicionar_vendedor():
    username = request.form['username']
    password = request.form['password']
    role = 'vendedor'
    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)

    # Verificar se o nome de usuário ou senha já existe
    cursor.execute("SELECT * FROM usuarios WHERE username = %s OR password = %s", (username, password))
    user_exists = cursor.fetchone()
    conn.commit()

    if user_exists:
        mensagem = "Erro: Nome de usuário ou senha já existe!"
    elif username == password:
        mensagem = "Erro: Nome de usuário não pode ser igual à senha!"
    else:
        # SQL para inserir o usuário como vendedor
        sql = "INSERT INTO usuarios (username, password, role) VALUES (%s, %s, %s)"
        cursor.execute(sql, (username, password, role))

        
        if cursor.rowcount != 0:
            mensagem = f"Usuário Vendedor '{username}' adicionado com sucesso!"
        else:
            mensagem = "Erro: Usuário não pode ser adicionado."
    
    # Renderiza a página 'rh.html' com a mensagem
    return render_template('rh.html', mensagem=mensagem)


@app.route('/addgerente', methods=['POST'])
def adicionar_gerente():
    username = request.form['username']
    password = request.form['password']
    role = 'gerente'
    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)

    # Verificar se o nome de usuário ou senha já existe
    cursor.execute("SELECT * FROM usuarios WHERE username = %s OR password = %s", (username, password))
    user_exists = cursor.fetchone()

    if user_exists:
        mensagem = "Erro: Nome de usuário ou senha já existe!"
    elif username == password:
        mensagem = "Erro: Nome de usuário não pode ser igual à senha!"
    else:
        # SQL para inserir o usuário como gerente
        sql = "INSERT INTO usuarios (username, password, role) VALUES (%s, %s, %s)"
        cursor.execute(sql, (username, password, role))
        
        if cursor.rowcount != 0:
            mensagem = f"Usuário Gerente '{username}' adicionado com sucesso!"
        else:
            mensagem = "Erro: Usuário não pode ser adicionado."
    
    # Renderiza a página 'rh.html' com a mensagem
    return render_template('rh.html', mensagem=mensagem)

@app.route("/addg")
def addg():
    return render_template('add_gerente.html')

@app.route("/addv")
def addv():
    return render_template('add_vendedor.html')


if __name__ == '__main__':
    app.run(debug=True)
