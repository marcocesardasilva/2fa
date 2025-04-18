import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText
import pyotp
import qrcode
from termcolor import colored
from Crypto.Protocol.KDF import scrypt
from Crypto.Cipher import AES
from Crypto.Hash import SHA512
from Crypto.Protocol.KDF import PBKDF2
from getpass import getpass
import json
from base64 import b64decode, b64encode
import time
import sys

class Usuario:
    def __init__(self, nome_usuario, numero_celular, autentificador, hash_senha):
        self.nome_usuario = nome_usuario
        self.numero_celular = numero_celular
        self.autentificador = autentificador
        self.hash_senha = hash_senha

class Mensagem:
    def __init__(self, usuario_remetente, usuario_destinatario, mensagem_cifrada, mensagem_completa):
        self.usuario_remetente = usuario_remetente
        self.usuario_destinatario = usuario_destinatario
        self.mensagem_cifrada = mensagem_cifrada
        self.mensagem_completa = mensagem_completa

class Servidor:
    def __init__(self):
        self.usuarios = []
        self.mensagens = []
        self.qtd_vezes_logadas = {}

    def cadastrar_novo_usuario(self, nome: str, telefone_celular: str, chave: str, salt: str):
        chave_criptografada = self.criptografar(nome, chave)
        autentificador = self.gerar_autentificador(nome)

        novo_usuario = Usuario(nome, telefone_celular, autentificador, chave_criptografada)
        self.usuarios.append(novo_usuario)
        self.salvar_dados_usuario(nome, telefone_celular, chave_criptografada, salt)

    def criptografar(self, usuario: str, token: str):
        salt = usuario[::-1] + usuario + usuario[::-1]
        chave_criptografada = scrypt(token, salt, 16, N=2**14, r=8, p=1)
        return chave_criptografada

    def entrar(self, usuario: Usuario, token: str):
        hash_senha_input = self.criptografar(usuario.nome_usuario, token)

        while True:
            if usuario.hash_senha == hash_senha_input:
                try:
                    self.qtd_vezes_logadas[usuario] += 1
                    qtd_logadas = self.qtd_vezes_logadas[usuario]
                except:
                    qtd_logadas = 1
                    self.qtd_vezes_logadas[usuario] = qtd_logadas

                autenticacao = self.printar_qrcode(usuario.autentificador[0], usuario.autentificador[1], qtd_logadas)
                if autenticacao == False:
                    messagebox.showerror("Erro", "Código incorreto, tente novamente!")
                else:
                    return autenticacao
            else:
                messagebox.showerror("Erro", "Senha incorreta, tente novamente!")
                return False

    def enviar_mensagem(self, usuario_remetente, usuario_destinatario, mensagem_cifrada, mensagem_completa):
        nova_mensagem = Mensagem(usuario_remetente, usuario_destinatario, mensagem_cifrada, mensagem_completa)
        self.mensagens.append(nova_mensagem)
        return mensagem_completa

    def localizar_mensagens(self, nome: str):
        retorno = False
        for mensagem in self.mensagens:
            if mensagem.usuario_destinatario == nome:
                retorno = True
        return retorno

    def retornar_mensagens(self, nome:str):
        lista_msgs = []
        for mensagem in self.mensagens:
            if mensagem.usuario_destinatario == nome:
                retorno = (mensagem.usuario_remetente, mensagem.mensagem_completa)
                lista_msgs.append(retorno)
        return lista_msgs

    def localizar_nome_usuarios(self, nome: str):
        for usuario in self.usuarios:
            if usuario.nome_usuario == nome:
                return usuario
        return None

    def localizar_telefone(self, numero: str):
        for telefone in self.usuarios:
            if telefone.numero_celular == numero:
                return telefone
        return None

    def salvar_dados_usuario(self, nome: str, telefone_celular: str, chave: str, salt: str):
        historico = open("data\historico_dados_usuarios.csv", "a+")
        linha=str(nome)+","+str(telefone_celular)+","+str(chave)+","+str(salt)+"\n"
        historico.write(linha)
        historico.close()

    def guardar_mensagens(self, usuario_remetente: str, usuario_destinatario: str, mensagem_cifrada: str):
        historico = open("data\historico_mensagens_usuarios.csv", "a+")
        linha=str(usuario_remetente)+","+str(usuario_destinatario)+","+str(mensagem_cifrada)+"\n"
        historico.write(linha)
        historico.close()

    def gerar_autentificador(self, nome_usuario: str):
        # Gera uma chave secreta aleatória para o usuário
        chave_segredo = pyotp.random_base32()

        # Cria um objeto TOTP (Time-based One-Time Password)
        totp = pyotp.TOTP(chave_segredo, interval=30, digits=6)

        # # Cria uma URL de provisionamento
        url_configuracao_auth = totp.provisioning_uri(nome_usuario, issuer_name="Segurança 2FA")

        # Retorna a URL de provisionamento
        return url_configuracao_auth, chave_segredo

    def printar_qrcode(self, url_configuracao_auth: any, chave_segredo: any, qtd_logadas: int):
        # Cria o QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=1,
            border=1,
        )
        qr.add_data(url_configuracao_auth)
        qr.make(fit=True)

        # Imprime o QRCode
        if qtd_logadas == 1:
            messagebox.showinfo("Código 2FA", "Utilize o QRCode abaixo para realizar a Autentificação 2FA")
            qr.print_ascii()

        while True:
            codigo_2FA = simpledialog.askstring("Código 2FA", "Digite o código 2FA: ")

            totp = pyotp.TOTP(chave_segredo, interval=30, digits=6)
            if totp.verify(codigo_2FA):
                return codigo_2FA
            else:
                messagebox.showerror("Erro", "Código incorreto, tente novamente!")
                return False

    def exibir_usuarios_cadastrados(self, usuario_atual: str):
        usuarios_disponiveis = []
        for usuario in self.usuarios:
            if usuario.nome_usuario != usuario_atual:
                usuarios_disponiveis.append(usuario.nome_usuario)
        if usuarios_disponiveis == []:
            return None
        else:
            return usuarios_disponiveis

    def retornar_celular_destino(self, usuario_destino: str):
        for usuario in self.usuarios:
            if usuario.nome_usuario != usuario_destino:
                return usuario.numero_celular

class Cliente:
    def __init__(self):
        self.servidor = Servidor()
        self.codigo_2fa_usado_no_entrar = ''
        self.pbkdf2_codigo_mensagem = ''
        self.root = tk.Tk()
        self.root.title("Segurança 2FA")
        self.root.geometry("800x600")

    def abrir_menu_principal(self):
        while True:
            print('\n------------------------------------------------------------------------------------------------')
            print('Bem vindo ao Segurança 2FA\n')
            print(colored('Menu Principal:\nPara "Cadastrar-se" digite 1, "Fazer login" digite 2, "Sair" digite 3.', 'blue'))

            opcoes = {
                1: self.cadastrar,
                2: self.entrar
            }

            while True:
                try:
                    escolha = str(input('\nDigite o número da sua escolha: '))
                    if escolha == '3':
                        sys.exit()
                    elif int(escolha) and 1 <= int(escolha) <= 3:
                        break
                    else:
                        raise Exception
                except Exception:
                    print(colored('\n> Por favor, escolha uma opção válida!', 'red'))

            opcoes[int(escolha)]()

    def cadastrar(self):
        print(colored('\nRealize seu Cadastro no sistema!\n > Para "voltar", digite 0.\n', 'blue'))

        while True:
            usuario = input('Nome de Usuário: ')
            # Da a chance de voltar ao Menu principal
            if usuario == '0':
                return
            # Validação 1: verifica se o usuário já existe
            if self.servidor.localizar_nome_usuarios(usuario) == None and len(usuario) >= 3:
                break
            else:
                print(colored('\n> Usuário já existente ou demasiadamente curto, tente novamente.', 'red'))

        while True:
            while True:
                # Validação 2: verifica se o telefone_celular possui somente números
                try:
                    telefone_celular = input('Telefone Celular com DDD (apenas números): ')
                    # Da a chance de voltar ao Menu principal
                    if telefone_celular == '0':
                        return

                    if int(telefone_celular):
                        break
                    else:
                        raise Exception
                except Exception:
                    print(colored('\n> O Telefone Celular deve possuir apenas números, tente novamente.', 'red'))

            # Validação 3: verifica se o Telefone Celular já esta cadastrado e possui ddd + 9 dígitos
            if self.servidor.localizar_telefone(telefone_celular) == None and 11 <= len(telefone_celular) <= 12:
                break
            else:
                print(colored('\n> O Telefone Celular já está cadastrado ou está incorreto, tente novamente.', 'red'))

        senha = input('Defina sua Senha: ')
        # Da a chance de voltar ao Menu principal
        if senha == '0':
            self.abrir_menu_principal()

        # Chama o servidor pra fazer o cadastro
        salt = usuario[::-1]
        chave_PBKDF2 = PBKDF2(senha, salt, 32, count=10000, hmac_hash_module=SHA512)
        self.servidor.cadastrar_novo_usuario(usuario, telefone_celular, chave_PBKDF2, salt)
        print(colored('> Usuário cadastrado com Sucesso! \n', 'green'))

    def entrar(self):
        print(colored('\nRealize seu login!\n > Para "voltar", digite 0.\n', 'blue'))

        usuario = input('Nome de Usuário: ')
        # Da a chance de voltar ao Menu principal
        if usuario == '0':
            self.abrir_menu_principal()

        # Validação: verifica se o usuário está cadastrado no sistema
        usuario_localizado = self.servidor.localizar_nome_usuarios(usuario)
        if usuario_localizado == None:
            print(colored('\n> Usuário não cadastrado, cadastre-se e tente novamente.\n','red'))
            return

        senha = getpass('Senha: ')
        # Da a chance de voltar ao Menu principal
        if senha == '0':
            self.abrir_menu_principal()

        salt = usuario[::-1]
        chave_PBKDF2 = PBKDF2(senha, salt, 32, count=10000, hmac_hash_module=SHA512)

        sucesso_entrar = self.servidor.entrar(usuario_localizado, chave_PBKDF2)
        if sucesso_entrar != False:
            self.codigo_2fa_usado_no_entrar = sucesso_entrar
            print(colored('Login realizado com Sucesso! \n','green'))
            self.abrir_menu_usuario(usuario_localizado)
        else:
            return

    def abrir_menu_usuario(self, usuario: Usuario):
        usuario_localizado = usuario
        print(colored('\n-\nMenu do Usuário:\n-\nPara "Visualizar Mensagens" digite 1, para "Enviar Mensagens" digite 2, "Sair" digite 0.\n', 'blue'))
        # Usuário escolhe se quer enviar ou visualizar mensagens
        while True:
            try:
                escolha = str(input('Digite o número da sua escolha: '))
                if (int(escolha) and 0<= int(escolha) <= 2) or escolha == '0':
                    break
                else:
                    raise Exception
            except Exception:
                print(colored('\n> Por favor, escolha uma opção válida!', 'red'))

        if int(escolha) == 0 or escolha == '0':
            self.abrir_menu_principal()
        elif int(escolha) == 1:
            self.visualizar_mensagens(usuario_localizado)
        elif int(escolha) == 2:
            self.iniciar_envio_de_mensagens(usuario_localizado)
        else:
            print(colored('\n> Por favor, escolha uma opção válida!', 'red'))

    def iniciar_envio_de_mensagens(self, usuario: Usuario):
        print(colored('\n-\nAmbiente de envio de mensagens!\n > Para "voltar", digite 0.\n-', 'blue'))

        while True:
            # Verifica e printa Usuários disponíveis
            usuario_atual = usuario.nome_usuario
            usuarios_disponiveis = self.servidor.exibir_usuarios_cadastrados(usuario_atual)
            if usuarios_disponiveis == None:
                print(colored('\nNão há usuários para enviar mensagens :(\nEstamos te redirecionando ao Menu do Usuário...\n\n', 'red'))
                time.sleep(7)
                self.abrir_menu_usuario(usuario)
            else:
                print(colored('\nOs usuários disponíveis para enviar mensagens são:', 'magenta'))
                for i in range (len(usuarios_disponiveis)):
                    print(i+1, '-', usuarios_disponiveis[i])
                print('')

            while True:
                # Seleciona Usuário para enviar mensagem
                destinatario_input = input('Digite o valor do destinatário escolhido: ')

                try:
                    opcao = int(destinatario_input)
                    if usuarios_disponiveis[opcao-1] in (usuarios_disponiveis) or opcao == 0:
                        break
                    else:
                        raise Exception
                except Exception:
                    print(colored('\n> Opção inválida, tente novamente.', 'red'))

            if destinatario_input == '0':
                self.abrir_menu_usuario(usuario)
            else:
                usuario_destino = usuarios_disponiveis[opcao-1]
                print(colored(f'\nO usuário escolhido foi "{usuario_destino}".', 'green'))

                # Cria as chaves e salt
                salt = usuario_atual[::-1] + usuario_atual + usuario_atual[::-1]

                numero_celular_destino = self.servidor.retornar_celular_destino(usuario_destino)

                codigo_pbkdf2 = PBKDF2(numero_celular_destino, salt, 32, count=10000, hmac_hash_module=SHA512)
                self.pbkdf2_codigo_mensagem = codigo_pbkdf2

                mensagem = input('Digite sua mensagem: ')
                if mensagem == '0':
                    return
                else:
                    # Criptogra com GCM
                    cipher = AES.new(codigo_pbkdf2, AES.MODE_GCM)
                    header = b'header'
                    cipher.update(header)
                    b_mensagem = mensagem.encode('utf-8')
                    ciphertext, tag = cipher.encrypt_and_digest(b_mensagem)

                    json_k = [ 'nonce', 'header', 'ciphertext', 'tag' ]
                    json_v = [ b64encode(x).decode('utf-8') for x in [cipher.nonce, header, ciphertext, tag ]]
                    mensagem_completa = json.dumps(dict(zip(json_k, json_v)))

                    # Envia mensagem para o Servidor
                    print('Mensagem criptografada e enviada com sucesso: ', ciphertext, '\n')
                    self.servidor.enviar_mensagem(usuario_atual, usuario_destino, ciphertext, mensagem_completa)
                    self.servidor.guardar_mensagens(usuario_atual, usuario_destino, ciphertext)

    def visualizar_mensagens(self, usuario: Usuario):
        print(colored('\n-\nAmbiente de visualização de mensagens!\n > Para "voltar", digite 0.\n-\n', 'blue'))

        possui_mensagem = self.servidor.localizar_mensagens(usuario.nome_usuario)

        if possui_mensagem is True:
            print(colored('Você recebeu as seguintes mensagens:\n', 'magenta'))

            lista_msgs = self.servidor.retornar_mensagens(usuario.nome_usuario)
            for mensagem in lista_msgs:
                texto_mensagem = str(mensagem[1])
                # Descriptografando resposta do servidor
                try:
                    b64 = json.loads(texto_mensagem)
                    json_k = [ 'nonce', 'header', 'ciphertext', 'tag' ]
                    jv = {k:b64decode(b64[k]) for k in json_k}

                    # Descriptografia com GCM
                    salt = mensagem[0][::-1] + mensagem[0] + mensagem[0][::-1]
                    numero_celular_destino = self.servidor.retornar_celular_destino(usuario.nome_usuario)
                    codigo_pbkdf2 = PBKDF2(numero_celular_destino, salt, 32, count=10000, hmac_hash_module=SHA512)

                    cipher = AES.new(codigo_pbkdf2, AES.MODE_GCM, nonce=jv['nonce'])
                    cipher.update(jv['header'])
                    mensagem_decifrada = cipher.decrypt_and_verify(jv['ciphertext'], jv['tag'])

                    print(f'Você recebeu mensagens dê {mensagem[0]}.')
                    print('A mensagem cifrada é: ', jv['ciphertext'])
                    print('A mensagem decifrada é:', mensagem_decifrada.decode("utf-8"),'\n')

                except (ValueError, KeyError):
                    print('Ops! Houve um erro na descriptografia.')    

            while True:
                voltar = input('- Terminou de ler suas mensagens? Digite 0 para voltar: ')
                if voltar == '0':
                    self.abrir_menu_usuario(usuario)
                else:
                    print(colored('\n> Opção inválida, tente novamente.', 'red'))
        else:
            print(colored('Você ainda não recebeu mensagens :(\nEstamos te redirecionando ao Menu do Usuário...\n\n', 'red'))
            time.sleep(7)
            self.abrir_menu_usuario(usuario)

cliente = Cliente()
cliente.abrir_menu_principal()
cliente.root.mainloop()

