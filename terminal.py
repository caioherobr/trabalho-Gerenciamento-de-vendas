import tkinter as tk
import tkinter.messagebox as messagebox
import mysql.connector
from datetime import datetime

# Configuração de conexão com o banco de dados
db_config = {
    'host': 'gerenciavendas.mysql.database.azure.com',
    'user': 'adm',
    'password': 'aluno@123',
    'database': 'gerenciamento'
}

# Funções do banco de dados (MySQL)
def verificar_login(mydb, nome_usuario, senha):
    try:
        mycursor = mydb.cursor()
        consulta = "SELECT username, password, role FROM usuarios WHERE username = %s"
        mycursor.execute(consulta, (nome_usuario,))
        resultado = mycursor.fetchone()
        
        if resultado:
            senha_armazenada = resultado[1]  # Senha armazenada no banco (em texto claro)
            if senha == senha_armazenada:  # Comparando senhas em texto claro
                if resultado[2] == 'vendedor':  # Verificando o papel do usuário
                    return True
        return False
    except mysql.connector.Error as err:
        print(f"Erro ao verificar login: {err}")
        return False

def inserir_venda(mydb, data, valor, vendedor_id):
    try:
        mycursor = mydb.cursor()
        consulta = "INSERT INTO vendas (data, valor, vendedor_id) VALUES (%s, %s, %s)"
        mycursor.execute(consulta, (data, valor, vendedor_id))
        mydb.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Erro ao inserir venda: {err}")
        mydb.rollback()
        return False

def obter_id_usuario(mydb, nome_usuario):
    try:
        mycursor = mydb.cursor()
        consulta = "SELECT id FROM usuarios WHERE username = %s"
        mycursor.execute(consulta, (nome_usuario,))
        resultado = mycursor.fetchone()
        if resultado:
            return resultado[0]
        else:
            return None
    except mysql.connector.Error as err:
        print(f"Erro ao obter id do usuario: {err}")
        return None

class TelaLogin:
    def __init__(self, master):
        self.master = master
        master.title("Login")
        master.geometry("300x200")
        self.master.protocol("WM_DELETE_WINDOW", self.fechar)

        self.label_usuario = tk.Label(master, text="Usuário:")
        self.label_usuario.pack(pady=5)
        self.entry_usuario = tk.Entry(master)
        self.entry_usuario.pack(pady=5)

        self.label_senha = tk.Label(master, text="Senha:")
        self.label_senha.pack(pady=5)
        self.entry_senha = tk.Entry(master, show="*")
        self.entry_senha.pack(pady=5)

        self.botao_login = tk.Button(master, text="Login", command=self.fazer_login)
        self.botao_login.pack(pady=10)

    def fazer_login(self):
        nome_usuario = self.entry_usuario.get()
        senha = self.entry_senha.get()
        
        if not nome_usuario or not senha:
            messagebox.showerror("Erro", "Por favor, preencha os campos de usuário e senha.")
            return
        
        # Conectar ao banco de dados
        try:
            mydb = mysql.connector.connect(**db_config)  # Usando db_config para conectar ao banco
            
            # Verificar login
            if verificar_login(mydb, nome_usuario, senha):
                messagebox.showinfo("Sucesso", "Login realizado com sucesso!")
                self.master.destroy()  # Fechar a tela de login
                self.abrir_tela_vendas(nome_usuario, mydb)  # Abrir a tela de vendas
            else:
                messagebox.showerror("Erro", "Usuário ou senha inválidos.")
        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao conectar ao banco de dados: {err}")
    
    def abrir_tela_vendas(self, usuario_logado, mydb):
        root_vendas = tk.Tk()
        app_vendas = TelaVendas(root_vendas, usuario_logado, mydb)
        root_vendas.mainloop()

    def fechar(self):
        self.master.quit()

class TelaVendas:
    def __init__(self, master, usuario_logado, mydb):
        self.master = master
        master.title("Terminal de Vendas - Input de Vendas")
        self.usuario_logado = usuario_logado
        self.mydb = mydb
        master.geometry("400x300")
        padding = {'padx': 10, 'pady': 5}

        # Widgets de input de vendas
        self.label_valor = tk.Label(master, text="Valor Unitário:")
        self.label_valor.grid(row=0, column=0, **padding, sticky=tk.W)
        self.entry_valor = tk.Entry(master)
        self.entry_valor.grid(row=0, column=1, **padding, sticky=tk.E)

        # Botão de salvar venda
        self.botao_salvar = tk.Button(master, text="Salvar Venda", command=self.salvar_venda)
        self.botao_salvar.grid(row=1, column=0, pady=(15, 5), sticky=tk.W)

        # Botão de logout, ao lado do botão de salvar
        self.botao_logout = tk.Button(master, text="Logout", command=self.logoutx)
        self.botao_logout.grid(row=1, column=1, pady=(15, 5), padx=(10, 0), sticky=tk.E)  # Coloca à direita do botão de salvar

    def salvar_venda(self):
        try:
            valor_str = self.entry_valor.get()  # Pega o valor como string
            if not valor_str:  # Verifica se o campo está vazio
                raise ValueError("O campo Valor Unitário não pode estar vazio.")
            valor = float(valor_str)
            data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            usuario_id = obter_id_usuario(self.mydb, self.usuario_logado)

            if usuario_id is not None:
                if inserir_venda(self.mydb, data_atual, valor, usuario_id):
                    messagebox.showinfo("Sucesso", "Venda salva com sucesso!")
                    self.entry_valor.delete(0, tk.END)  # Limpa o campo
                else:
                    messagebox.showerror("Erro", "Erro ao salvar a venda.")
            else:
                messagebox.showerror("Erro", "Erro ao obter ID do usuário.")
        except ValueError as e:  # Captura o erro específico de valor
            messagebox.showerror("Erro", str(e))  # Mostra a mensagem de erro

    def logoutx(self):
        # Fecha a janela de vendas
        self.master.quit()
        self.master.destroy()
        
        # Cria a janela de login
        root_login = tk.Tk()  # A variável root_login precisa ser criada antes de ser usada
        app_login = TelaLogin(root_login)  # Instanciando a classe TelaLogin, passando root_login como parâmetro
        root_login.mainloop()  # Inicia o loop da janela de login
        



def main():
    root = tk.Tk()
    app = TelaLogin(root)
    root.mainloop()

if __name__ == "__main__":
    main()
