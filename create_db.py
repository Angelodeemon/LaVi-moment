import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE users(
    id INTEGER PRIMARY KEY,
    email TEXT,
    name TEXT,
    salt TEXT,
    password_hash TEXT,
    qr_codes VARCHAR(13),
    from_schoo21 BOOLEAN,
    session TEXT
)""")



