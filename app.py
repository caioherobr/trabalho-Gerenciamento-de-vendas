from flask import Flask, render_template
import mysql.connector

app = Flask(__name__)

# Configurações do banco de dados
db_config = {
    'host': 'senacvendas2024.mysql.database.azure.com',         # Endereço do servidor MySQL
    'user': 'adminvendas',       # Substitua pelo seu usuário MySQL
    'password': 'Senac@vendas',     # Substitua pela sua senha MySQL
    'database': 'login_senha'      # Nome do banco de dados
}

@app.route("/")
def index():
    # Conectar ao banco
    conexao = mysql.connector.connect(**db_config)
    cursor = conexao.cursor(dictionary=True)  # Retorna os resultados como dicionários
    
    # Realizar consulta SQL
    cursor.execute("SELECT * FROM vendas")
    vendas = cursor.fetchall()  # Buscar todos os registros da tabela
    
    # Fechar conexão
    cursor.close()
    conexao.close()
    
    # Passar os dados para o frontend
    return render_template("/vendas.html", vendas=vendas)

if __name__ == "__main__":
    app.run(debug=True)