from src import bank, User, Transfers
from src.utils import Text, AC

def require_auth(f):
    def wrapper(session: User, *args, **kwargs):
        if not User.load_user(session.id):
            return Text.render_response('Not authorized', 'E')
        return f(session, *args, **kwargs)
    return wrapper

@bank.command('HELP', help='Exibe essa mensagem')
@require_auth
def help(_session, _args) -> bytes:
    return Text.render_response(bank.help(), 'R')

@bank.command('SALDO', help='Exibe o saldo da sua conta')
@require_auth
def saldo(session: User, _) -> bytes:
    saldo_ = f'{(session.currency / 100):.2f}'.replace('.', ',')

    return  Text.render_response(f'Saldo atual: R$ {saldo_}', 'R')


@bank.command('INFO', help='Exibe as informações da sua conta')
@require_auth
def info(session: User, _) -> bytes:
    saldo = f'{(session.currency / 100):.2f}'.replace('.', ',')
    infos = f'- id: {session.id}\n- Username: {session.username}\n- Currency: R$ {saldo}\n- Key: {session.key}'

    return Text.render_response(infos, 'R')    


@bank.command('UPDATE', help='Atualiza a sua chave de transferência')
@require_auth
def update_key(session: User, args: list[str]) -> bytes:
    if len(args) == 1:
        key: str = args[0]

        success: bool = session.update_key(key)
        if not success:
            return Text.render_response('A chave não pode ser atualizada.', 'E')
        
        return Text.render_response(f'chave atualizada com sucesso -> {session.key}', 'I')
    elif len(args) > 1:
        return Text.render_response('UPDATE command takes only 1 argumment', 'E')

    return Text.render_response('UPDATE command takes at least 1 argumment', 'E')


@bank.command('TRANSFER', help='Transfere valor x para a conta y (Ex: TRANSFER conta_y valor_x)')
@require_auth
def transfer(session: User, args: list) -> bytes:
    if len(args) == 2:
        destiny = args[0] 

        try:
            value = int(args[1])
        except ValueError:
            return Text.render_response(f'Invalid value {value}', 'E')

        if session.transfer(destiny, value):
            return Text.render_response(f'Transferência para {destiny} no valor de R$ {value} bem sucedida', 'S')
        
        return Text.render_response(f'Erro ao transferir R$ {value} para {destiny}.', 'E')

    return Text.render_response('Invalid argumments number', 'E')


@bank.command('LIST_T', help='Lista todas as transferências realizadas')
@require_auth
def list_transfers(session: User, _) -> bytes:
    transfers: list[Transfers] = Transfers.list_user_transfs(session.id)

    response = ''
    for t in transfers:
        prefix: str = f'[{AC.G}+{AC.E}]'
        if t['source'] == session.id:
            prefix = f'[{AC.R}-{AC.E}]'
        response += f'{prefix} id: {t['id']} - source: {t['source']} - destiny: {t['destiny']} - value: {int(t['value']) / 100}\n'

    return Text.render_response(response, 'R')
