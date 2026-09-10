from app.api import api
from app.cryptacommuni import access
from app.views import login_required

from flask import jsonify, request

@api.route('/cards', methods=['GET', 'POST'])
@login_required
def cards():
    if request.method == 'GET':
        cards_: dict = access.send_recv('CARDS')
        return jsonify(cards_['data']), 200

    holder = request.json.get('holder')

    create_card: dict = access.send_recv(f'CREATE card {holder}')

    return jsonify(create_card), 200

@api.route('/balance')
@login_required
def balance():
    balance_ = access.send_recv('BALANCE')

    return jsonify(balance_), 200

@api.route('/transactions')
@login_required
def transactions():
    transactions_ = access.send_recv('TRANSACTIONS')

    return jsonify(transactions_['data']), 200

@api.route('/transfers', methods=['POST'])
@login_required
def transfer():
    destiny: str = request.json.get('destination')
    value: str = request.json.get('value')

    value: float = float(value)
    response = access.send_recv(f'TRANSFER {destiny} {value}')

    if response['status'] == 100:
        return jsonify(error='Não foi possível fazer a transferencia'), 400
    
    return jsonify(response), 200

