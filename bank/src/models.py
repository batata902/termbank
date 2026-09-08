from __future__ import annotations

from src.utils import gerar_cartao

import random
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
        value = int(value)

        if value > self.currency:
            return False
        
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

                    cur.execute('INSERT INTO transfers(source, destiny, value) VALUES(?, ?, ?)', (self.id, dest['id'], value))

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
            t = cur.execute('SELECT t.id, t.value u.username AS source, u2.username AS destiny FROM transfers t JOIN users u ON u.id=t.source JOIN users u2 ON u2.id=t.destiny WHERE t.id=?', (t_id,)).fetchone()
        if t:
            return cls(
                id = t['id'],
                source = t['source'],
                destiny = t['destiny'],
                value = t['value']
            )
        return None

    @classmethod
    def list_user_transfs(cls, user_id: str) -> list[Transfers]:
        with db() as (_, cur):
            query = cur.execute('SELECT * FROM transfers WHERE source=? OR destiny=?', (user_id, user_id)).fetchall()
        transfs = [dict(row) for row in query]

        return transfs


@dataclass
class Cards:
    id: int
    holder: str
    number: str
    cvv: str
    brand: str
    exp: str
    blocked: bool
    balance: int
    owner_id: int

    @classmethod
    def get_card(cls, card_id: int) -> Cards | None:
        with db() as (_, cur):
            card = cur.execute('SELECT * FROM cards WHERE id=?;', (card_id,)).fetchone()

            if not card:
                return None
        return cls(
            id=card['id'],
            holder=card['holder'],
            number=card['number'],
            cvv=card['cvv'],
            brand=card['brand'],
            exp=card['exp'],
            blocked=card['blocked'],
            balance=card['balance'],
            owner_id=card['owner']
        )

    @staticmethod
    def list_user_cards(user: User) -> list[dict] | None:
        with db() as (_, cur):
            cards = cur.execute('SELECT * FROM cards WHERE owner=?;', (user.id,)).fetchall()
            if not cards:
                return None

        return [dict(card) for card in cards]


    @staticmethod
    def create_card(user: User, name: str) -> bool:
        card_num: str = gerar_cartao("5", 16)
        with db() as (conn, cur):
            cur.execute(
                'INSERT OR IGNORE INTO cards(holder, number, cvv, brand, exp, blocked, balance, owner) VALUES(?, ?, ?, ?, ?, ?, ?, ?)', 
                (name, card_num, "".join([str(random.randint(0, 9)) for _ in range(3)]), 'CryptaB', '04/30', 0, 0, user.id)
            )

            try:
                conn.commit()
            except sqlite3.IntegrityError:
                return False
        return True

    @staticmethod
    def delete_card(card_id: str) -> None:
        with db() as (conn, cur):
            cur.execute('DELETE FROM cards WHERE id=?;', (card_id,))
            conn.commit()
       

