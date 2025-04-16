import pyotp
import qrcode
from termcolor import colored
from Crypto.Protocol.KDF import scrypt

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
                    print(colored('> Código incorreto, tente novamente!', 'red'))
                else:
                    return autenticacao
            else:
                print(colored('> Senha incorreta, tente novamente!\n', 'red'))
                return False

    def enviar_mensagem(self, usuario_remetente, usuario_destinatario, mensagem_cifrada, mensagem_completa):
        nova_mensagem = Mensagem(usuario_remetente, usuario_destinatario, mensagem_cifrada, mensagem_completa)
        self.mensagens.append(nova_mensagem)
        return mensagem_completa

## ------------
## Utilitários:
## ------------

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
            print(colored('\nUtilize o QRCode abaixo para realizar a Autentificação 2FA', 'magenta'))
            qr.print_ascii()

        while True:
            codigo_2FA = input('- Digite o código 2FA: ')

            totp = pyotp.TOTP(chave_segredo, interval=30, digits=6)
            if totp.verify(codigo_2FA):
                self.codigo_2fa_usado_no_entrar = codigo_2FA
                return codigo_2FA
            else:
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
