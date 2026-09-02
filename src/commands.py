from src import bank, User, Transfers
from src.utils import Response, AC

def require_auth(f):
    def wrapper(session: User, *args, **kwargs):
        if not User.load_user(session.id):
            return Response.render_response('Not authorized', 'E')
        return f(session, *args, **kwargs)
    return wrapper


@bank.command('HELP', help='Exibe essa mensagem')
@require_auth
def help(_session, _args) -> bytes:
    return Response.render_response({'help': bank.help()}, 'S')

@bank.command('SALDO', help='Exibe o saldo da sua conta')
@require_auth
def saldo(session: User, _) -> bytes:
    saldo_ = f'{(session.currency / 100):.2f}'.replace('.', ',')

    return  Response.render_response({'currency': saldo_}, 'S')


@bank.command('INFO', help='Exibe as informações da sua conta')
@require_auth
def info(session: User, _) -> bytes:
    saldo = f'{(session.currency / 100):.2f}'.replace('.', ',')
    infos = {
        'id': session.id, 
        'username': session.username, 
        'currency': saldo, 
        'key': session.key
        }

    return Response.render_response(infos, 'S')    


@bank.command('UPDATE', help='Atualiza a sua chave de transferência')
@require_auth
def update_key(session: User, args: list[str]) -> bytes:
    if len(args) == 1:
        key: str = args[0]

        success: bool = session.update_key(key)
        if not success:
            return Response.render_response({'error': 'A chave não pode ser atualizada.'}, 'E')
        
        return Response.render_response({'key': session.key}, 'S')
    elif len(args) > 1:
        return Response.render_response({'error': 'UPDATE command takes only 1 argumment'}, 'E')

    return Response.render_response({'error': 'UPDATE command takes at least 1 argumment'}, 'E')


@bank.command('TRANSFER', help='Transfere valor x para a conta y (Ex: TRANSFER conta_y valor_x)')
@require_auth
def transfer(session: User, args: list) -> bytes:
    if len(args) == 2:
        destiny = args[0] 

        try:
            value = int(float(args[1]) * 100)
        except ValueError:
            return Response.render_response({'error': 'Invalid value'}, 'E')

        if session.transfer(destiny, value):
            return Response.render_response(f'Transferência para {destiny} no valor de R$ {value / 100} bem sucedida', 'S')
        
        return Response.render_response({'error': f'Não é possível transferir R$ {value / 100} para {destiny}.'}, 'E')

    return Response.render_response({'error': 'Invalid argumments number'}, 'E')


@bank.command('LIST_T', help='Lista todas as transferências realizadas')
@require_auth
def list_transfers(session: User, _) -> bytes:
    transfers: list[dict[str, str]] = Transfers.list_user_transfs(session.id)

    for t in transfers:
        if t['source'] == session.id:
            t['flow'] = 'out'
            t['source'] = session.username
            t['destiny'] = User.load_user(t['destiny']).username

        if t['destiny'] == session.id:
            t['flow'] = 'in'
            t['destiny'] = session.username
            t['source'] = User.load_user(t['source']).username

        t['value'] = int(t['value']) / 100

    return Response.render_response(transfer, 'S')
