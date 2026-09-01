from src import User

import socket
import threading

HELP: str = '''[CB] LISTA DE COMANDOS
SALDO - Exibe o saldo existente na usa conta corrente
INFO - Exibe as informaçẽos da sua sessão atual
TRANSF destiny value - Transfere dinheiro para o destino especificado
UPDATE key - Cria uma chave de transferencia para a sua conta\n$> '''

class Bank:
    def __init__(self, host: str = '0.0.0.0', port=9000):
        self.threads = []
        self.host = host
        self.port = port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.sock.bind((host, port))

        self.sock.listen(10)

        self.start_server()

    def start_server(self):
        print(f'[+] Serviço CryptaBank iniciado em {self.host} na porta {self.port}')
        while True:
            con, client = self.sock.accept()
            t = threading.Thread(target=self.handle_login, args=(con, client))
            t.start()

            self.threads.append(t)

    def handle_login(self, con: socket.socket, client):
        con.send('username: '.encode('utf-8'))
        username: str = con.recv(1024).decode('utf-8').strip()
        con.send('password: '.encode('utf-8'))
        password: str = con.recv(1024).decode('utf-8').strip()

        user: User = User.log_in(username, password)
        if not user:
            con.send('[ERROR] Invalid username or password\n'.encode('utf-8'))
            con.close()
            return
        
        con.send('[OK] Welcome to CryptaBank Systems!\n'
                 'Digite HELP para opções de comando\n'
                 '$> '.encode('utf-8'))

        self.handle_user(user, con)


    def handle_user(self, user: User, con: socket.socket):
        while True:
            cmd: str = con.recv(1024).decode('utf-8').strip().upper()

            if cmd == 'HELP':
                con.send(HELP.encode('utf-8'))
                continue

            elif cmd == 'SALDO':
                saldo: str = f'{(user.currency / 100):.2f}'.replace('.', ',')
                con.send(
                    f'[INFO] Saldo atual: {saldo}\n$> '.encode('utf-8')
                    )
                continue

            elif cmd == 'INFO':
                saldo: str = f'{(user.currency / 100):.2f}'.replace('.', ',')
                infos: str = f'[id]: {user.id}\n[Username]: {user.username}\n[Currency]: {saldo}\n$> '
                con.send(infos.encode('utf-8'))
                continue

            elif cmd.startswith('UDPATE'):
                key = cmd.split(' ')[1]

                success: bool = user.update_key(key)
                if not success:
                    con.send('[ERROR] A chave não pode ser atualizada.\n$> '.encode('utf-8'))
                else:
                    con.send(f'[INFO] chave atualizada com sucesso -> {user.key}'.encode('utf-8'))

                continue

            else:
                con.send('Comando não encontrado\n'.encode('utf-8'))
                continue
