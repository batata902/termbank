from src import User
from src.utils import Text

import socket
import threading

BANNER: str = f''

HELP: str = ''

class Bank:
    def __init__(self):
        self.threads: list = []

        self.commands: dict = {}

    def help(self) -> str:
        return HELP

    def config_sock(self, host, port) -> socket.socket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.bind((host, port))
        sock.listen(10)

        return sock

    def start_server(self, host: str = '0.0.0.0', port=9000):
        sock = self.config_sock(host, port)

        print(f'[+] Serviço CryptaBank iniciado em {host} na porta {port}')
        while True:
            con, client = sock.accept()
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

    def command(self, cmd: str, help: str = ''):
        def wrapper(func):
            global HELP
            self.commands[cmd] = func
            HELP += f'{cmd} - {help}\n'
            return func
        return wrapper


    def handle_user(self, user: User, con: socket.socket):
        while True:
            data: str = con.recv(1024).decode('utf-8').strip().split()
            if not data:
                con.close()
                return

            cmd = data[0].upper()
            args = data[1:]

            func = self.commands.get(cmd)

            if not func:
                response = Text.render_response('Invalid command', 'E')
                con.send(response)
                continue

            response = func(user, args)
            con.send(response)

            

