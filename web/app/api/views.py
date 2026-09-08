from app.api import api

import socket
from flask import jsonify
from contextlib import contextmanager

@contextmanager
def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', '9000'))

    try:
        yield s
    finally:
        s.close()


@api.route('/cards')
def cards():
    return