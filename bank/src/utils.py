import json

class AC:
    R = '\033[31m'
    G = '\033[32m'
    Y = '\033[33m'
    B = '\033[34m'
    E = '\033[m'

class Response:
    @staticmethod # flags = 'E': Erro, 'S': Sucesso
    def render_response(data: str, flag: str) -> bytes:
        response = {}

        if flag == 'E':
            response['status'] = 100 # Error
            response['data'] = data

        elif flag == 'S':
            response['status'] = 200 # Success
            response['data'] = data
     
        res: str = json.dumps(response) + '\n'
        return res.encode('utf-8')


import random

def luhn_checksum(card_number_str):
    digits = [int(x) for x in card_number_str]
    checksum = 0
    # Processa da direita para a esquerda
    for i, digit in enumerate(reversed(digits)):
        if i % 2 == 1:
            double = digit * 2
            checksum += double - 9 if double > 9 else double
        else:
            checksum += digit
    return checksum % 10

def gerar_cartao(prefixo, tamanho=16):
    # Gera números aleatórios até o penúltimo dígito
    qtd_aleatoria = tamanho - len(prefixo) - 1
    parcial = prefixo + "".join([str(random.randint(0, 9)) for _ in range(qtd_aleatoria)])
    
    # Calcula o dígito verificador (último dígito)
    for digito_verificador in range(10):
        teste = parcial + str(digito_verificador)
        if luhn_checksum(teste) == 0:
            return teste

# Exemplo de uso: Prefixo '4' para Visa
# cartao_gerado = gerar_cartao("4", 16)
