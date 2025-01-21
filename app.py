from flask import Flask, render_template, request, redirect, url_for, session
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

def conectar_bd():
    return mysql.connector.connect(**db_config)

@app.route("/")
def index():
    return render_template('index.html')

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
            return redirect('/vendas')
        else:
            return render_template('login.html', error='Credenciais inválidas!')
    
    return render_template('login.html')

@app.route('/vendas')
def todas_as_vendas():
    user_role = session.get('user_role')  # Obtém o papel do usuário
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
    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT usuarios.username AS vendedor, COUNT(vendas.id) AS total_vendas, SUM(vendas.valor) AS valor_total
        FROM vendas
        INNER JOIN usuarios ON vendas.vendedor_id = usuarios.id
        GROUP BY usuarios.username
        ORDER BY total_vendas DESC
    """
    cursor.execute(query)
    rank = cursor.fetchall()
    conn.close()
    return render_template('rank_vendedores.html', rank=rank)

@app.route('/total')
def total_vendas():
    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT SUM(valor) AS total_geral, COUNT(id) AS total_vendas
        FROM vendas
    """
    cursor.execute(query)
    total = cursor.fetchone()
    conn.close()
    return render_template('total_geral.html', total=total)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
