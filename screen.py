import tkinter as tk
from tkinter import messagebox
from screeninfo import get_monitors

def mostrar_login():
    # Esconde a janela de cadastro e mostra a janela de login
    frame_cadastro.pack_forget()
    frame_login.pack(expand=True)

def mostrar_cadastro():
    # Esconde a janela de login e mostra a janela de cadastro
    frame_login.pack_forget()
    frame_cadastro.pack(expand=True)

def entrar():
    # Lógica para o botão Entrar
    usuario = entry_usuario.get()
    senha = entry_senha.get()
    messagebox.showinfo("Login", f"Usuário: {usuario}\nSenha: {senha}")

def cadastrar():
    # Lógica para o botão Cadastre-se
    usuario = entry_cadastro_usuario.get()
    email = entry_cadastro_email.get()
    senha = entry_cadastro_senha.get()
    messagebox.showinfo("Cadastro", f"Usuário: {usuario}\nEmail: {email}\nSenha: {senha}")

def sair():
    # Lógica para o botão Sair
    root.destroy()

# Cria a janela principal
root = tk.Tk()
root.title("SafeChat")

# Obtém as dimensões da área de trabalho (excluindo a barra de tarefas)
monitor = get_monitors()[0]
screen_width = monitor.width
screen_height = monitor.height

# Configura a janela para o tamanho da área de trabalho
root.geometry(f"{screen_width}x{screen_height}+0+0")

# Frame de login
frame_login = tk.Frame(root)
frame_login.pack(expand=True)

# Mensagem de boas-vindas
label_bem_vindo = tk.Label(frame_login, text="Bem vindo ao SafeChat", font=("Helvetica", 24))
label_bem_vindo.pack(pady=20)

# Campo de entrada para usuário
frame_usuario = tk.Frame(frame_login)
frame_usuario.pack(pady=5)
label_usuario = tk.Label(frame_usuario, text="Usuário:", font=("Helvetica", 14))
label_usuario.pack(side=tk.LEFT)
entry_usuario = tk.Entry(frame_usuario, font=("Helvetica", 14))
entry_usuario.pack(side=tk.LEFT)

# Campo de entrada para senha
frame_senha = tk.Frame(frame_login)
frame_senha.pack(pady=5)
label_senha = tk.Label(frame_senha, text="Senha:", font=("Helvetica", 14))
label_senha.pack(side=tk.LEFT)
entry_senha = tk.Entry(frame_senha, show='*', font=("Helvetica", 14))
entry_senha.pack(side=tk.LEFT)

# Botões de Entrar e Sair
frame_botoes = tk.Frame(frame_login)
frame_botoes.pack(pady=20)

button_entrar = tk.Button(frame_botoes, text="Entrar", font=("Helvetica", 14), command=entrar)
button_entrar.pack(side=tk.LEFT, padx=10)

button_sair = tk.Button(frame_botoes, text="Sair", font=("Helvetica", 14), command=sair)
button_sair.pack(side=tk.LEFT, padx=10)

# Texto de cadastro
label_cadastro = tk.Label(frame_login, text="Ainda não é cadastrado?", font=("Helvetica", 14))
label_cadastro.pack(pady=10)

button_cadastrar = tk.Button(frame_login, text="Cadastre-se", font=("Helvetica", 14), command=mostrar_cadastro)
button_cadastrar.pack(pady=5)

# Frame de cadastro
frame_cadastro = tk.Frame(root)

# Mensagem de cadastro
label_informe_dados = tk.Label(frame_cadastro, text="Informe seus dados para cadastro", font=("Helvetica", 24))
label_informe_dados.pack(pady=20)

# Campo de entrada para usuário no cadastro
frame_cadastro_usuario = tk.Frame(frame_cadastro)
frame_cadastro_usuario.pack(pady=5)
label_cadastro_usuario = tk.Label(frame_cadastro_usuario, text="Usuário:", font=("Helvetica", 14))
label_cadastro_usuario.pack(side=tk.LEFT)
entry_cadastro_usuario = tk.Entry(frame_cadastro_usuario, font=("Helvetica", 14))
entry_cadastro_usuario.pack(side=tk.LEFT)

# Campo de entrada para email no cadastro
frame_cadastro_email = tk.Frame(frame_cadastro)
frame_cadastro_email.pack(pady=5)
label_cadastro_email = tk.Label(frame_cadastro_email, text="Email:", font=("Helvetica", 14))
label_cadastro_email.pack(side=tk.LEFT)
entry_cadastro_email = tk.Entry(frame_cadastro_email, font=("Helvetica", 14))
entry_cadastro_email.pack(side=tk.LEFT)

# Campo de entrada para senha no cadastro
frame_cadastro_senha = tk.Frame(frame_cadastro)
frame_cadastro_senha.pack(pady=5)
label_cadastro_senha = tk.Label(frame_cadastro_senha, text="Senha:", font=("Helvetica", 14))
label_cadastro_senha.pack(side=tk.LEFT)
entry_cadastro_senha = tk.Entry(frame_cadastro_senha, show='*', font=("Helvetica", 14))
entry_cadastro_senha.pack(side=tk.LEFT)

# Botões de cadastrar e voltar
frame_cadastro_botoes = tk.Frame(frame_cadastro)
frame_cadastro_botoes.pack(pady=20)

button_cadastrar = tk.Button(frame_cadastro_botoes, text="Cadastrar", font=("Helvetica", 14), command=cadastrar)
button_cadastrar.pack(side=tk.LEFT, padx=10)

button_voltar = tk.Button(frame_cadastro_botoes, text="Voltar", font=("Helvetica", 14), command=mostrar_login)
button_voltar.pack(side=tk.LEFT, padx=10)

# Executa a aplicação
root.mainloop()
