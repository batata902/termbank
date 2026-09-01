from src import bank, seed_database

if __name__ == '__main__':
    seed_database()

    bank.start_server()