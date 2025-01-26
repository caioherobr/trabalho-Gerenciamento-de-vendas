import tkinter as tk

janela = tk.Tk()
janela.title("Terminal de Vendas")

label = tk.Label(janela, text="Olá, Usuario faça login!")
label.pack(padx=40, pady=40)

botao = tk.Button(janela, text="Login!")
botao.pack()

janela.mainloop()