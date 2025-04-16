import tkinter as tk
from tkinter import messagebox

from src.cliente import *

class Cliente:
    def __init__(self):
        self.servidor = Servidor()
        self.codigo_2fa_usado_no_entrar = ''
        self.pbkdf2_codigo_2fa_usado_no_entrar = ''

    def cadastrar(self, nome_usuario, telefone_celular, senha):
        if len(nome_usuario) < 3:
            messagebox.showerror("Erro", "Nome de usuário muito curto. Deve ter pelo menos 3 caracteres.")
            return
        if self.servidor.localizar_nome_usuarios(nome_usuario):
            messagebox.showerror("Erro", "Nome de usuário já existe.")
            return
        if not telefone_celular.isdigit():
            messagebox.showerror("Erro", "Telefone celular deve conter apenas números.")
            return
        if len(telefone_celular) < 11:
            messagebox.showerror("Erro", "Número de telefone celular inválido.")
            return

        salt = nome_usuario[::-1]
        chave_PBKDF2 = PBKDF2(senha, salt, 32, count=10000, hmac_hash_module=SHA512)
        self.servidor.cadastrar_novo_usuario(nome_usuario, telefone_celular, chave_PBKDF2, salt)
        messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso.")

    def entrar(self, nome_usuario, senha):
        usuario = self.servidor.localizar_nome_usuarios(nome_usuario)
        if not usuario:
            messagebox.showerror("Erro", "Usuário não cadastrado.")
            return

        salt = nome_usuario[::-1]
        chave_PBKDF2 = PBKDF2(senha, salt, 32, count=10000, hmac_hash_module=SHA512)

        sucesso_entrar = self.servidor.entrar(usuario, chave_PBKDF2)
        if sucesso_entrar:
            self.codigo_2fa_usado_no_entrar = sucesso_entrar
            messagebox.showinfo("Sucesso", "Login realizado com sucesso.")
            return True
        else:
            return False

    def enviar_mensagem(self, usuario_atual, usuario_destino, mensagem):
        salt = usuario_atual[::-1]
        codigo_pbkdf2 = PBKDF2(self.codigo_2fa_usado_no_entrar, salt, 32, count=10000, hmac_hash_module=SHA512)
        mensagem_cifrada = self.servidor.enviar_mensagem(usuario_atual, usuario_destino, mensagem, codigo_pbkdf2)
        messagebox.showinfo("Sucesso", "Mensagem enviada com sucesso.")
        return mensagem_cifrada

    def visualizar_mensagens(self, usuario):
        lista_msgs = self.servidor.imprimir_mensagems(usuario)
        if not lista_msgs:
            messagebox.showinfo("Info", "Você ainda não recebeu mensagens.")
            return
        mensagens = "\n".join([f"De: {msg[0]}\nMensagem: {msg[1]}" for msg in lista_msgs])
        messagebox.showinfo("Mensagens", mensagens)

class InterfaceGrafica:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ToyWhats")
        
        self.cliente = Cliente()
        
        self.current_frame = None
        
        self.create_main_frame()
    
    def create_main_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack()

        label_bem_vindo = tk.Label(self.current_frame, text="Bem vindo ao ToyWhats!", font=("Arial", 16))
        label_bem_vindo.pack(pady=10)

        botao_cadastrar = tk.Button(self.current_frame, text="Cadastrar-se", command=self.create_cadastro_frame)
        botao_cadastrar.pack(pady=5)

        botao_entrar = tk.Button(self.current_frame, text="Entrar no ToyWhats", command=self.create_login_frame)
        botao_entrar.pack(pady=5)

        botao_sair = tk.Button(self.current_frame, text="Sair", command=self.root.destroy)
        botao_sair.pack(pady=5)

    def create_cadastro_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack()

        label_nome_usuario = tk.Label(self.current_frame, text="Nome de Usuário:")
        label_nome_usuario.grid(row=0, column=0, padx=10, pady=5)
        self.entry_nome_usuario = tk.Entry(self.current_frame)
        self.entry_nome_usuario.grid(row=0, column=1, padx=10, pady=5)

        label_telefone_celular = tk.Label(self.current_frame, text="Telefone Celular (apenas números):")
        label_telefone_celular.grid(row=1, column=0, padx=10, pady=5)
        self.entry_telefone_celular = tk.Entry(self.current_frame)
        self.entry_telefone_celular.grid(row=1, column=1, padx=10, pady=5)

        label_senha = tk.Label(self.current_frame, text="Senha:")
        label_senha.grid(row=2, column=0, padx=10, pady=5)
        self.entry_senha = tk.Entry(self.current_frame, show="*")
        self.entry_senha.grid(row=2, column=1, padx=10, pady=5)

        botao_cadastrar = tk.Button(self.current_frame, text="Cadastrar", command=self.cadastrar)
        botao_cadastrar.grid(row=3, columnspan=2, padx=10, pady=10)

        botao_voltar = tk.Button(self.current_frame, text="Voltar", command=self.create_main_frame)
        botao_voltar.grid(row=4, columnspan=2, padx=10, pady=10)

    def create_login_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack()

        label_nome_usuario = tk.Label(self.current_frame, text="Nome de Usuário:")
        label_nome_usuario.grid(row=0, column=0, padx=10, pady=5)
        self.entry_nome_usuario = tk.Entry(self.current_frame)
        self.entry_nome_usuario.grid(row=0, column=1, padx=10, pady=5)

        label_senha = tk.Label(self.current_frame, text="Senha:")
        label_senha.grid(row=1, column=0, padx=10, pady=5)
        self.entry_senha = tk.Entry(self.current_frame, show="*")
        self.entry_senha.grid(row=1, column=1, padx=10, pady=5)

        botao_entrar = tk.Button(self.current_frame, text="Entrar", command=self.entrar)
        botao_entrar.grid(row=2, columnspan=2, padx=10, pady=10)

        botao_voltar = tk.Button(self.current_frame, text="Voltar", command=self.create_main_frame)
        botao_voltar.grid(row=3, columnspan=2, padx=10, pady=10)

    def create_enviar_mensagem_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack()

        label_usuario_destino = tk.Label(self.current_frame, text="Usuário Destino:")
        label_usuario_destino.grid(row=0, column=0, padx=10, pady=5)

        # Obter a lista de usuários disponíveis
        usuarios_disponiveis = self.cliente.servidor.exibir_usuarios_cadastrados()
        
        # Se não houver usuários disponíveis, mostrar uma mensagem e retornar
        if not usuarios_disponiveis:
            messagebox.showinfo("Info", "Não há usuários disponíveis para enviar mensagens.")
            return

        # Variável de controle para a lista suspensa
        self.selected_user = tk.StringVar(self.current_frame)
        self.selected_user.set(usuarios_disponiveis[0])  # Definir o primeiro usuário como padrão

        # Lista suspensa para selecionar o usuário destino
        dropdown_usuario_destino = tk.OptionMenu(self.current_frame, self.selected_user, *usuarios_disponiveis)
        dropdown_usuario_destino.grid(row=0, column=1, padx=10, pady=5)

        label_mensagem = tk.Label(self.current_frame, text="Mensagem:")
        label_mensagem.grid(row=1, column=0, padx=10, pady=5)
        self.entry_mensagem = tk.Entry(self.current_frame)
        self.entry_mensagem.grid(row=1, column=1, padx=10, pady=5)

        botao_enviar = tk.Button(self.current_frame, text="Enviar Mensagem", command=self.enviar_mensagem)
        botao_enviar.grid(row=2, columnspan=2, padx=10, pady=10)

        botao_voltar = tk.Button(self.current_frame, text="Voltar", command=self.create_main_frame)
        botao_voltar.grid(row=3, columnspan=2, padx=10, pady=10)

    def create_visualizar_mensagens_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack()

        label_usuario_atual = tk.Label(self.current_frame, text="Usuário Atual:")
        label_usuario_atual.grid(row=0, column=0, padx=10, pady=5)
        self.entry_usuario_atual = tk.Entry(self.current_frame)
        self.entry_usuario_atual.grid(row=0, column=1, padx=10, pady=5)

        botao_visualizar = tk.Button(self.current_frame, text="Visualizar Mensagens", command=self.visualizar_mensagens)
        botao_visualizar.grid(row=1, columnspan=2, padx=10, pady=10)

        botao_voltar = tk.Button(self.current_frame, text="Voltar", command=self.create_main_frame)
        botao_voltar.grid(row=2, columnspan=2, padx=10, pady=10)

    def cadastrar(self):
        nome_usuario = self.entry_nome_usuario.get()
        telefone_celular = self.entry_telefone_celular.get()
        senha = self.entry_senha.get()
        self.cliente.cadastrar(nome_usuario, telefone_celular, senha)

    def entrar(self):
        nome_usuario = self.entry_nome_usuario.get()
        senha = self.entry_senha.get()
        sucesso = self.cliente.entrar(nome_usuario, senha)
        if sucesso:
            self.create_enviar_mensagem_frame()

    def enviar_mensagem(self):
        usuario_atual = self.entry_usuario_atual.get()
        usuario_destino = self.entry_usuario_destino.get()
        mensagem = self.entry_mensagem.get()
        self.cliente.enviar_mensagem(usuario_atual, usuario_destino, mensagem)

    def visualizar_mensagens(self):
        usuario_atual = self.entry_usuario_atual.get()
        self.cliente.visualizar_mensagens(usuario_atual)

if __name__ == "__main__":
    app = InterfaceGrafica()
    app.root.mainloop()

