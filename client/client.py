import socket
import json
import argparse
import sys
import os

R = '\033[31m'
G = '\033[32m'
E = '\033[m'

class BankCli:
    def __init__(self, addr: str, port: int, session_file: str = None):
        self.addr: str = addr
        self.port: int = port
        self.session_file: str = session_file
        self.sock: socket.socket = None

    def connect_and_run(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            self.sock.settimeout(10.0) 
            self.sock.connect((self.addr, self.port))
            self.sock.settimeout(None) 
            
            banner: str = self.sock.recv(4096).decode('utf-8').strip()
            if banner:
                print(banner)

            if not self.authenticate():
                return
            
            self.command_loop()

        except ConnectionRefusedError:
            print(self.format_error(f"Conexão recusada pelo servidor em {self.addr}:{self.port}"))
        except socket.timeout:
            print(self.format_error(f"Tempo limite de conexão excedido ({self.addr}:{self.port})"))
        except Exception as e:
            print(self.format_error(f"Erro inesperado: {e}"))
        finally:
            if self.sock:
                self.sock.close()

    def authenticate(self) -> bool:
        """Lida com a importação de sessão ou login interativo."""
        if self.session_file:
            try:
                with open(self.session_file, 'r') as f:
                    session = f.read().strip()
                
                self.sock.send(f'IMPORT {session}'.encode('utf-8'))
                response = json.loads(self.sock.recv(4096).decode('utf-8'))
                
                if response.get('status') == 100:
                    print(self.format_error('Erro ao importar a sessão'))
                    return False
                
                print(self.format_success('Sessão importada com sucesso'))
                return True
                
            except FileNotFoundError:
                print(self.format_error(f"Arquivo de sessão '{self.session_file}' não encontrado."))
                return False
            except json.JSONDecodeError:
                print(self.format_error("Resposta inválida do servidor ao importar sessão."))
                return False
        else:
            logged_in: bool = False
            while not logged_in:
                logged_in = self.do_login()
                if logged_in:
                    print(self.format_success('Welcome'))
                    return True
                print(self.format_error('Usuário ou senha inválidos. Tente novamente.'))
        return False

    def do_login(self) -> bool:
        try:
            user_input = input('username: ').strip()
            self.sock.send(f'LOGIN {user_input}'.encode('utf-8'))
            
            raw_res = self.sock.recv(1024).decode('utf-8').strip()
            if not raw_res:
                return False
                
            res = json.loads(raw_res)
            
            if res.get('data') == 'OK':
                pass_input = input('password: ').strip()
                self.sock.send(f'PASSWORD {pass_input}'.encode('utf-8'))
                
                raw_res = self.sock.recv(1024).decode('utf-8').strip()
                res = json.loads(raw_res)
                
                if res.get('data') == 'WELCOME':
                    return True
                    
        except EOFError: # Captura Ctrl+D
            print("\nOperação cancelada pelo usuário.")
            sys.exit(0)
        except json.JSONDecodeError:
            print(self.format_error("Resposta inesperada do servidor durante o login."))
            
        return False

    def command_loop(self) -> None:
        while True:
            try:
                cmd: str = input('$> ').strip()
            except EOFError:
                print(self.format_success('\nConexão encerrada pelo usuário'))
                break

            if not cmd:
                continue

            cmd_lower = cmd.lower()
            if cmd_lower == 'exit':
                print(self.format_success('Conexão encerrada'))
                break
            
            if cmd_lower == 'clear':
                os.system('clear' if os.name == 'posix' else 'cls')
                continue

            try:
                self.sock.send(cmd.encode('utf-8'))
                raw_data = self.sock.recv(4096).decode('utf-8')
                
                if not raw_data:
                    print(self.format_error("A conexão com o servidor foi perdida."))
                    break

                response = json.loads(raw_data)
                
                if response.get('status') == 100:
                    print(self.format_error(response.get('data', 'Unknown Error')), file=sys.stderr)
                    continue

                if cmd.upper() == 'EXPORT':
                    with open('session.dat', 'w') as f:
                        f.write(response.get('data', ''))
                    print(self.format_success('Sessão salva -> session.dat'))
                    continue

                print(self.format_success(response.get('data', '')))

            except json.JSONDecodeError:
                print(self.format_error('Resposta inválida (JSON) do servidor'), file=sys.stderr)
            except Exception as e:
                print(self.format_error(f'Erro durante envio do comando: {e}'), file=sys.stderr)

    def format_error(self, msg: str) -> str:
        return f'[{R}Err{E}] {msg}'

    def format_success(self, msg) -> str:
        response: str = ''

        if isinstance(msg, dict):
            for key, item in msg.items():
                response += f'[{G}+{E}] {key} - {item}\n'

        elif isinstance(msg, list):
            for dic in msg:
                if isinstance(dic, dict):
                    flow = dic.get('flow', '')
                    if flow == 'in':
                        response += f'[{G}+{E}] '
                    elif flow == 'out':
                        response += f'[{R}-{E}] '
                    else:
                        response += f'[{G}+{E}] '
                        
                    response += ' :: '.join([f"{k} - {v}" for k, v in dic.items()]) + '\n'
                else:
                    response += f'[{G}+{E}] {dic}\n'

        elif isinstance(msg, str):
            response = f'[{G}+{E}] {msg}'

        return response.strip()


def main():
    parser = argparse.ArgumentParser(description="Cliente para o servidor CryptaBank")
    parser.add_argument('addr', type=str, help='Endereço ip do servidor da CryptaBank')
    # O default e o nargs='?' são necessários para que o usuário não seja obrigado a passar a porta
    parser.add_argument('port', type=int, nargs='?', default=9000, help='Porta do servidor CryptaBank (default=9000)')
    parser.add_argument('-s', '--session', type=str, help='Carrega um arquivo de sessão para o CryptaBank')
    
    args = parser.parse_args()

    bank = BankCli(addr=args.addr, port=args.port, session_file=args.session)
    
    try:
        bank.connect_and_run()
    except KeyboardInterrupt:
        print('\nO usuário escolheu sair (Ctrl+C)')
        sys.exit(0)

if __name__ == '__main__':
    main()