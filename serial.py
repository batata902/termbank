import pickle

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password


user = User('teste', '123')
open('sess.dat', 'wb').write(pickle.dumps(user))

# gASVQQAAAAAAAACMCF9fbWFpbl9flIwEVXNlcpSTlCmBlH2UKIwIdXNlcm5hbWWUjAV0ZXN0ZZSMCHBhc3N3b3JklIwDMTIzlHViLg==