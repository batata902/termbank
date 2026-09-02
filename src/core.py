from src import User
from src.utils import Response

import socket
import threading

BANNER: str = 'CryptaBank Account System :: v1.0 :: CBAS\n'

HELP: list[dict[str, str]] = []

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
        con.send(BANNER.encode('utf-8'))

        username: str = ''
        password: str = ''
        while True:
            data = con.recv(1024).decode('utf-8').strip().split()
            if not data:
                return

            cmd = data[0].upper()
            args = data[1:]

            if username and cmd != 'PASSWORD':
                response = Response.render_response({'error':'After LOGIN command, PASSWORD is required.'}, 'E')

                con.send(response)
                con.close()

                return

            if cmd == 'LOGIN':
                username = args[0]

                con.send(b'OK\n')
                continue

            if cmd == 'PASSWORD':
                password = args[0]

                user: User = User.log_in(username, password)
                if not user:
                    response = Response.render_response({'error': 'Invalid username or password'}, 'E')
                    con.send(response)
                    con.close()
                    return
                
                con.send('SUCCESS\n'.encode('utf-8'))

                return self.handle_user(user, con)

    def command(self, cmd: str, help: str = ''):
        def wrapper(func):
            global HELP
            HELP.append({cmd: help})

            self.commands[cmd] = func

            return func
        return wrapper


    def handle_user(self, user: User, con: socket.socket):
        while True:
            data: bytes = con.recv(1024)

            if not data:
                con.close()
                return

            data: str = data.decode('utf-8').strip().split()

            cmd = data[0].upper()
            args = data[1:]

            if cmd == 'EXIT':
                con.send(b'Bye')
                con.close()
                return

            func = self.commands.get(cmd)

            if not func:
                response = Response.render_response('Invalid command', 'E')
                con.send(response)
                continue

            response = func(user, args)
            con.send(response)

            

