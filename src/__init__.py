from src.models import User, Transfers
from src.core import Bank
import sqlite3

def seed_database():
    conn = sqlite3.connect('src/database/database.db')
    conn.executescript(open('schema.sql', 'r').read())

    conn.close()