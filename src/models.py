from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from hashlib import sha256

@contextmanager
def db():
    conn = sqlite3.connect('src/database/database.db')
    conn.row_factory = sqlite3.Row

    cur = conn.cursor()

    try:
        yield conn, cur
    finally:
        conn.close()

@dataclass
class User:
    id: int
    username: str
    password: str
    _currency: int
    key: str

    @property
    def currency(self) -> int:
        with db() as (_, cur):
            self._currency = cur.execute('SELECT currency FROM users WHERE id = ?', (self.id,)).fetchone()['currency']
        return self._currency

    @currency.setter
    def currency(self, value: int):
        if not value:
            raise ValueError('Currency não pode ser vazia')

        self._currency = value

        
    @classmethod
    def load_user(cls, user_id: int) -> User | None:
        with db() as (_, cur):
            user = cur.execute('SELECT * FROM users WHERE id=?;', (user_id,)).fetchone()
        if not user:
            return None

        return cls(
            id = user['id'],
            username = user['username'],
            password = user['password'],
            _currency = user['currency'],
            key = user['key']
            )   

    @classmethod
    def log_in(cls, username: str, password: str) -> User | None:
        with db() as (_, cur):
            user = cur.execute('SELECT * FROM users WHERE username=?;', (username,)).fetchone()

        if not user:
            return None
        
        if user['password'] == sha256(password.encode('utf-8')).hexdigest():
            return cls.load_user(user['id'])

    def update_key(self, key) -> bool:
        with db() as (conn, cur):
            try:
                cur.execute('UPDATE users SET key=? WHERE id=?', (key, self.id))
                conn.commit()
            except sqlite3.IntegrityError:
                return False

        self.key = key
        return True


    def transfer(self, destiny, value) -> bool:
        with db() as (conn, cur):
            try:
                cur.execute('BEGIN IMMEDIATE') # Impede race conditions aqui
                dest = cur.execute('SELECT * FROM users WHERE key=?;', (destiny,)).fetchone()

                if dest:
                    cur.execute('UPDATE users SET currency=currency - ? WHERE id=?', (value, self.id))
                    if cur.rowcount == 0:
                        conn.rollback()
                        return False

                    cur.execute('UPDATE users SET currency=currency + ? WHERE id=?', (value, dest['id']))

                    conn.commit()
                    self._currency -= int(value)

                    return True
                
            except (sqlite3.Error, ValueError):
                conn.rollback()
                return False

        return False

@dataclass
class Transfers:
    id: int
    source: str
    destiny: str
    value: int

    @classmethod
    def get_transfer(cls, t_id: str) -> Transfers | None:
        with db() as (_, cur):
            t = cur.execute('SELECT * FROM transfers WHERE id=?', (t_id,)).fetchone()
        if t:
            return cls(
                id = t['id'],
                source = t['source'],
                destiny = t['destiny'],
                value = t['value']
            )
        return None

    @classmethod
    def list_user_transfs