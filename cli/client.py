import socket
import json
import argparse
import sys
import os
from glob import glob

# Cores para o terminal
R = '\033[31m'  # Vermelho (Erro)
G = '\033[32m'  # Verde (Sucesso)
E = '\033[m'    # Reset
C = '\033[36m'  # Ciano (Menus/Destaques)

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

            # Tenta autenticar via argumento se foi passado
            if self.session_file:
                if not self._import_session_from_file(self.session_file):
                    print(self.format_error("Falha ao importar sessão da linha de comando. Indo para o menu manual."))
                    if not self.auth_menu():
                        return
            else:
                if not self.auth_menu():
                    return
            
            self.main_menu()

        except ConnectionRefusedError:
            print(self.format_error(f"Conexão recusada pelo servidor em {self.addr}:{self.port}"))
        except socket.timeout:
            print(self.format_error(f"Tempo limite de conexão excedido ({self.addr}:{self.port})"))
        except Exception as e:
            print(self.format_error(f"Erro inesperado: {e}"))
        finally:
            if self.sock:
                self.sock.close()

    def _send_and_recv(self, command: str) -> dict:
        """Helper para enviar comandos e receber o JSON parseado."""
        try:
            self.sock.send(command.encode('utf-8'))
            raw_data = self.sock.recv(4096).decode('utf-8')
            
            if not raw_data:
                print(self.format_error("A conexão com o servidor foi perdida."))
                sys.exit(1)

            return json.loads(raw_data)
        except json.JSONDecodeError:
            print(self.format_error('Resposta inválida (JSON) do servidor'), file=sys.stderr)
            return {"status": 100, "data": "Erro de decodificação do servidor"}
        except Exception as e:
            print(self.format_error(f'Erro durante envio do comando: {e}'), file=sys.stderr)
            return {"status": 100, "data": str(e)}

    def _import_session_from_file(self, filepath: str) -> bool:
        """Lê o arquivo e envia para o servidor."""
        try:
            with open(filepath, 'r') as f:
                session_data = f.read().strip()
            
            response = self._send_and_recv(f'IMPORT {session_data}')
            
            if response.get('status') == 100:
                print(self.format_error('Erro ao importar a sessão: ' + str(response.get('data'))))
                return False
            
            print(self.format_success('Sessão importada com sucesso! Bem-vindo de volta.'))
            return True
        except FileNotFoundError:
            print(self.format_error(f"Arquivo '{filepath}' não encontrado."))
            return False

    def auth_menu(self) -> bool:
        """Menu interativo de autenticação."""
        while True:
            print(f"\n{C}=== CryptaBank - Login ==={E}")
            print("1. Fazer Login (Usuário e Senha)")
            print("2. Importar arquivo de sessão (.dat)")
            print("0. Sair")
            
            try:
                escolha = input("Escolha uma opção: ").strip()
            except EOFError:
                return False

            if escolha == '1':
                if self.do_login():
                    input(f"\n{C}[Pressione Enter para continuar...]{E}")
                    os.system('clear' if os.name == 'posix' else 'cls')
                    return True
            elif escolha == '2':
                if self.interactive_import():
                    input(f"\n{C}[Pressione Enter para continuar...]{E}")
                    os.system('clear' if os.name == 'posix' else 'cls')
                    return True
            elif escolha == '0':
                return False
            else:
                print(self.format_error("Opção inválida!"))
            
            # Se falhar no login ou errar a opção, pausa e limpa a tela para tentar de novo
            input(f"\n{C}[Pressione Enter para tentar novamente...]{E}")
            os.system('clear' if os.name == 'posix' else 'cls')

    def interactive_import(self) -> bool:
        """Menu para listar e escolher arquivo de importação de sessão."""
        dat_files = glob("*.dat")
        
        print(f"\n{C}--- Arquivos de sessão encontrados ---{E}")
        if not dat_files:
            print("Nenhum arquivo .dat encontrado no diretório atual.")
            print("[M] Digitar o caminho manualmente")
        else:
            for i, f in enumerate(dat_files):
                print(f"[{i+1}] {f}")
            print("[M] Digitar o caminho manualmente")
        print("[0] Voltar")

        escolha = input("Escolha uma opção: ").strip().lower()
        
        if escolha == '0':
            return False
        
        filepath = ""
        if escolha == 'm':
            filepath = input("Digite o caminho completo para o arquivo de sessão: ").strip()
        elif escolha.isdigit() and 1 <= int(escolha) <= len(dat_files):
            filepath = dat_files[int(escolha) - 1]
        else:
            print(self.format_error("Opção inválida."))
            return False

        if not filepath:
            return False

        return self._import_session_from_file(filepath)

    def do_login(self) -> bool:
        try:
            user_input = input('Username: ').strip()
            
            # Envia username
            self.sock.send(f'LOGIN {user_input}'.encode('utf-8'))
            raw_res = self.sock.recv(1024).decode('utf-8').strip()
            if not raw_res: return False
            res = json.loads(raw_res)
            
            if res.get('data') == 'OK':
                pass_input = input('Password: ').strip()
                # Envia senha
                self.sock.send(f'PASSWORD {pass_input}'.encode('utf-8'))
                raw_res = self.sock.recv(1024).decode('utf-8').strip()
                res = json.loads(raw_res)
                
                if res.get('data') == 'WELCOME':
                    print(self.format_success('Autenticado com sucesso!'))
                    return True
            
            print(self.format_error('Usuário ou senha inválidos.'))
            return False
                
        except EOFError:
            print("\nOperação cancelada pelo usuário.")
            sys.exit(0)
        except json.JSONDecodeError:
            print(self.format_error("Resposta inesperada do servidor durante o login."))
            return False

    def main_menu(self) -> None:
        """Menu principal abstraído com as operações bancárias."""
        # Limpa a tela logo que entra no menu principal
        os.system('clear' if os.name == 'posix' else 'cls')

        while True:
            print(f"\n{C}=== CryptaBank - Menu Principal ==={E}")
            print("1. Ver Saldo")
            print("2. Ver Informações da Conta")
            print("3. Realizar Transferência")
            print("4. Extrato de Transferências")
            print("5. Atualizar Chave de Transferência")
            print("6. Exportar Sessão")
            print("0. Sair")

            try:
                escolha = input("\nEscolha uma opção: ").strip()
            except EOFError:
                print(self.format_success('\nConexão encerrada pelo usuário'))
                break

            if escolha == '0':
                print(self.format_success('Conexão encerrada'))
                break

            # Limpa a tela (o menu sai) para mostrar apenas o resultado do comando
            os.system('clear' if os.name == 'posix' else 'cls')

            # Mapeamento das opções
            if escolha == '1':
                self._handle_command('BALANCE')
            elif escolha == '2':
                self._handle_command('INFO')
            elif escolha == '3':
                self.interactive_transfer()
            elif escolha == '4':
                self._handle_command('LIST_T')
            elif escolha == '5':
                self.interactive_update_key()
            elif escolha == '6':
                self.interactive_export()
            else:
                print(self.format_error("Opção inválida!"))

            # Segura a tela para o usuário ler o que o servidor respondeu
            input(f"\n{C}[Pressione Enter para continuar...]{E}")
            # Limpa a tela novamente para desenhar um novo Menu Principal limpo
            os.system('clear' if os.name == 'posix' else 'cls')

    def _handle_command(self, cmd: str):
        """Envia um comando simples e lida com a resposta padrão."""
        response = self._send_and_recv(cmd)
        if response.get('status') == 100:
            print(self.format_error(response.get('data', 'Unknown Error')))
        else:
            print(self.format_success(response.get('data', '')))

    def interactive_transfer(self):
        print(f"\n{C}--- Nova Transferência ---{E}")
        destiny = input("Conta de destino: ").strip()
        if not destiny: return
        
        value = input("Valor a transferir (Ex: 150.50): ").strip()
        if not value: return

        # Envia o comando no formato original esperado pelo servidor
        cmd = f"TRANSFER {destiny} {value}"
        self._handle_command(cmd)

    def interactive_update_key(self):
        print(f"\n{C}--- Atualizar Chave ---{E}")
        new_key = input("Digite a nova chave: ").strip()
        if not new_key: return
        
        cmd = f"UPDATE {new_key}"
        self._handle_command(cmd)

    def interactive_export(self):
        print(f"\n{C}--- Exportar Sessão ---{E}")
        response = self._send_and_recv('EXPORT')
        
        if response.get('status') == 100:
            print(self.format_error(response.get('data', 'Erro ao gerar exportação.')))
            return

        data = response.get('data', '')
        
        default_name = "session.dat"
        filepath = input(f"Digite o caminho para salvar o arquivo (Enter para './{default_name}'): ").strip()
        
        if not filepath:
            filepath = default_name

        try:
            with open(filepath, 'w') as f:
                f.write(data)
            print(self.format_success(f'Sessão salva com sucesso em -> {filepath}'))
        except Exception as e:
            print(self.format_error(f"Falha ao salvar o arquivo: {e}"))

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