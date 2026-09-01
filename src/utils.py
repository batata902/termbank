class AC:
    R = '\033[31m'
    G = '\033[32m'
    Y = '\033[33m'
    B = '\033[34m'
    E = '\033[m'

class Text:
    @staticmethod # flags = 'E': Erro, 'S': Sucesso, 'I': Info, 'R': Response
    def render_response(text: str, flag: str) -> bytes:
        fac: str = ''
        if flag[0] == 'E':
            fac = f'[ {AC.R}ERROR{AC.E} ] {text}'
        elif flag[0] == 'S':
            fac = f'[ {AC.G}SUCCESS{AC.E} ] {text}'
        elif flag[0] == 'I':
            fac = f'[ {AC.Y}INFO{AC.E} ] {text}'
        else:
            fac = f'[ {AC.G}RESPONSE{AC.E} ]\n{text}'

        fac += '\n$> '

        return fac.encode('utf-8')