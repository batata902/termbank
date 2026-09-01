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
    currency: int
    key: str

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
            currency = user['currency'],
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
