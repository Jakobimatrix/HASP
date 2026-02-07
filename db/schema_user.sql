CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    salt TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    user_groups TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_users_username
ON users(username);