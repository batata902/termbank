CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    currency INTEGER NOT NULL,
    key TEXT UNIQUE NOT NULL
);

INSERT OR IGNORE INTO users(username, password, currency, key) VALUES('guest', 'bfbdb10e7244d30e9225a2bc22658556a50ffc79f032704bcbb96d89469a14b8', 1000, 'guest');
-- guest:senhadaora