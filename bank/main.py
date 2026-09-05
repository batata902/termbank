from src import bank, seed_database

if __name__ == '__main__':
    seed_database()

    try:
        bank.start_server()
    except KeyboardInterrupt:
        print('Serviço encerrado')