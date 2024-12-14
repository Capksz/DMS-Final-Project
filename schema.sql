-- Example
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
);

INSERT INTO users (name, email) VALUES ('John Doe', 'john.doe@example.com');
