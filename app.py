from flask import Flask, render_template, request, redirect, session
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
def vendas():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_role = session['user_role']
    vendas = []

    try:
        conn = conectar_bd()
        cursor = conn.cursor(dictionary=True)
        
        if user_role == 'vendedor':
            # Mostra todas as vendas relacionadas ao vendedor
            query = """
                SELECT usuarios.username AS vendedor, vendas.id, vendas.data, vendas.valor
                FROM vendas 
                INNER JOIN usuarios ON vendas.vendedor_id = usuarios.id
                WHERE vendedor_id = %s
                ORDER BY usuarios.username ASC
            """
            cursor.execute(query, (session['user_id'],))
        
        elif user_role == 'gerente':
            # Mostra todas as vendas de todos os vendedores
            query = """
                SELECT usuarios.username AS vendedor, vendas.id, vendas.data, vendas.valor
                FROM vendas 
                INNER JOIN usuarios ON vendas.vendedor_id = usuarios.id
                ORDER BY usuarios.username ASC
            """
            cursor.execute(query)
        
        else:
            return redirect('/login')

        vendas = cursor.fetchall()
    
    except mysql.connector.Error as e:
        print(f"Erro no banco de dados: {e}")
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('vendas.html', vendas=vendas)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
