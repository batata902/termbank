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