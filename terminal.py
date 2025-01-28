import tkinter as tk
import tkinter.messagebox as messagebox
import mysql.connector
from datetime import datetime
from tkinter import ttk

# Configuração de conexão com o banco de dados
db_config = {
    'host': 'gerenciavendas2.mysql.database.azure.com',
    'user': 'adm',
    'password': 'aluno@123',
    'database': 'gerenciamento'
}

# Definição de cores e estilos - Cores mais vibrantes e sólidas
COLORS = {
    'background': '#E8EAF6',  # Azul claro sólido
    'primary': '#3F51B5',     # Azul índigo
    'secondary': '#536DFE',   # Azul mais vibrante
    'text': '#1A237E',        # Azul escuro para texto
    'button': '#304FFE',      # Azul vibrante para botões
    'button_hover': '#1A237E', # Azul escuro para hover
    'frame_bg': '#C5CAE9'     # Azul mais claro para frames
}

# [Mantidas as funções de banco de dados originais]
def verificar_login(mydb, nome_usuario, senha):
    try:
        mycursor = mydb.cursor()
        consulta = "SELECT username, password, role FROM usuarios WHERE username = %s"
        mycursor.execute(consulta, (nome_usuario,))
        resultado = mycursor.fetchone()
        
        if resultado:
            senha_armazenada = resultado[1]
            if senha == senha_armazenada:
                if resultado[2] == 'vendedor':
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
        master.title("Sistema de Vendas - Login")
        
        # Configuração da janela
        window_width = 400
        window_height = 300
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        master.geometry(f'{window_width}x{window_height}+{x}+{y}')
        master.configure(bg=COLORS['background'])
        self.master.protocol("WM_DELETE_WINDOW", self.fechar)

        # Estilo para os widgets ttk
        self.style = ttk.Style()
        self.style.configure('TFrame', background=COLORS['frame_bg'])
        self.style.configure('TLabel', 
                           background=COLORS['frame_bg'],
                           foreground=COLORS['text'],
                           font=('Helvetica', 10))
        self.style.configure('TEntry', 
                           fieldbackground='white',
                           borderwidth=2)
        self.style.configure('Login.TButton',
                           background=COLORS['button'],
                           foreground='white',
                           padding=(20, 10),
                           font=('Helvetica', 10, 'bold'))

        # Frame principal com cor sólida
        self.main_frame = ttk.Frame(master, style='TFrame')
        self.main_frame.pack(expand=True, fill='both', padx=40, pady=40)

        # Título
        self.title_label = tk.Label(self.main_frame,
                                  text="Login do Sistema",
                                  font=('Helvetica', 18, 'bold'),
                                  bg=COLORS['frame_bg'],
                                  fg=COLORS['primary'])
        self.title_label.pack(pady=(0, 30))

        # Frame para campos de entrada
        self.input_frame = ttk.Frame(self.main_frame)
        self.input_frame.pack(fill='x', padx=20)

        # Campo usuário
        self.label_usuario = ttk.Label(self.input_frame,
                                     text="Usuário:",
                                     style='TLabel',
                                     font=('Helvetica', 12))
        self.label_usuario.pack(anchor='w')
        
        self.entry_usuario = ttk.Entry(self.input_frame,
                                     width=30,
                                     font=('Helvetica', 12))
        self.entry_usuario.pack(fill='x', pady=(5, 15))

        # Campo senha
        self.label_senha = ttk.Label(self.input_frame,
                                   text="Senha:",
                                   style='TLabel',
                                   font=('Helvetica', 12))
        self.label_senha.pack(anchor='w')
        
        self.entry_senha = ttk.Entry(self.input_frame,
                                   show="•",
                                   width=30,
                                   font=('Helvetica', 12))
        self.entry_senha.pack(fill='x', pady=(5, 20))

        # Botão personalizado
        self.login_button = tk.Button(self.input_frame,
                                    text="Entrar",
                                    command=self.fazer_login,
                                    bg=COLORS['button'],
                                    fg='white',
                                    font=('Helvetica', 12, 'bold'),
                                    relief='flat',
                                    padx=20,
                                    pady=10,
                                    cursor='hand2')
        self.login_button.pack(fill='x')
        
        # Adiciona efeito hover ao botão
        self.login_button.bind('<Enter>', lambda e: self.login_button.configure(
            bg=COLORS['button_hover']))
        self.login_button.bind('<Leave>', lambda e: self.login_button.configure(
            bg=COLORS['button']))

    def fazer_login(self):
        nome_usuario = self.entry_usuario.get()
        senha = self.entry_senha.get()
        
        if not nome_usuario or not senha:
            messagebox.showerror("Erro", "Por favor, preencha os campos de usuário e senha.")
            return
        
        try:
            mydb = mysql.connector.connect(**db_config)
            if verificar_login(mydb, nome_usuario, senha):
                messagebox.showinfo("Sucesso", "Login realizado com sucesso!")
                self.master.destroy()
                self.abrir_tela_vendas(nome_usuario, mydb)
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
        self.usuario_logado = usuario_logado
        self.mydb = mydb
        
        master.title("Sistema de Vendas - Terminal")
        
        # Configuração da janela
        window_width = 500
        window_height = 400
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        master.geometry(f'{window_width}x{window_height}+{x}+{y}')
        master.configure(bg=COLORS['background'])

        # Frame principal
        self.main_frame = tk.Frame(master, bg=COLORS['frame_bg'])
        self.main_frame.pack(expand=True, fill='both', padx=40, pady=40)

        # Cabeçalho
        self.header_frame = tk.Frame(self.main_frame, bg=COLORS['frame_bg'])
        self.header_frame.pack(fill='x', pady=(0, 30))

        self.title_label = tk.Label(self.header_frame,
                                  text="Terminal de Vendas",
                                  font=('Helvetica', 18, 'bold'),
                                  bg=COLORS['frame_bg'],
                                  fg=COLORS['primary'])
        self.title_label.pack(side='left')

        self.user_label = tk.Label(self.header_frame,
                                 text=f"Usuário: {usuario_logado}",
                                 font=('Helvetica', 12),
                                 bg=COLORS['frame_bg'],
                                 fg=COLORS['text'])
        self.user_label.pack(side='right')

        # Frame para entrada de valor
        self.input_frame = tk.Frame(self.main_frame, bg=COLORS['frame_bg'])
        self.input_frame.pack(fill='x', padx=20)

        self.label_valor = tk.Label(self.input_frame,
                                  text="Valor da Venda:",
                                  font=('Helvetica', 12),
                                  bg=COLORS['frame_bg'],
                                  fg=COLORS['text'])
        self.label_valor.pack(anchor='w')
        
        self.entry_valor = ttk.Entry(self.input_frame,
                                   width=30,
                                   font=('Helvetica', 12))
        self.entry_valor.pack(fill='x', pady=(5, 20))

        # Frame para botões
        self.button_frame = tk.Frame(self.main_frame, bg=COLORS['frame_bg'])
        self.button_frame.pack(fill='x', padx=20)

        # Botões personalizados
        self.salvar_button = tk.Button(self.button_frame,
                                     text="Registrar Venda",
                                     command=self.salvar_venda,
                                     bg=COLORS['button'],
                                     fg='white',
                                     font=('Helvetica', 12, 'bold'),
                                     relief='flat',
                                     padx=20,
                                     pady=10,
                                     cursor='hand2')
        self.salvar_button.pack(side='left')

        self.logout_button = tk.Button(self.button_frame,
                                     text="Sair",
                                     command=self.logoutx,
                                     bg=COLORS['button'],
                                     fg='white',
                                     font=('Helvetica', 12, 'bold'),
                                     relief='flat',
                                     padx=20,
                                     pady=10,
                                     cursor='hand2')
        self.logout_button.pack(side='right')

        # Adiciona efeito hover aos botões
        for button in [self.salvar_button, self.logout_button]:
            button.bind('<Enter>', lambda e, b=button: b.configure(
                bg=COLORS['button_hover']))
            button.bind('<Leave>', lambda e, b=button: b.configure(
                bg=COLORS['button']))

    def salvar_venda(self):
        try:
            valor_str = self.entry_valor.get()
            if not valor_str:
                raise ValueError("O campo Valor da Venda não pode estar vazio.")
            valor = float(valor_str)
            data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            usuario_id = obter_id_usuario(self.mydb, self.usuario_logado)

            if usuario_id is not None:
                if inserir_venda(self.mydb, data_atual, valor, usuario_id):
                    messagebox.showinfo("Sucesso", "Venda registrada com sucesso!")
                    self.entry_valor.delete(0, tk.END)
                else:
                    messagebox.showerror("Erro", "Erro ao registrar a venda.")
            else:
                messagebox.showerror("Erro", "Erro ao obter ID do usuário.")
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

    def logoutx(self):
        self.master.quit()
        self.master.destroy()
        root_login = tk.Tk()
        app_login = TelaLogin(root_login)
        root_login.mainloop()

def main():
    root = tk.Tk()
    app = TelaLogin(root)
    root.mainloop()

if __name__ == "__main__":
    main()