import os
import sqlite3
import mysql.connector

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_PATH = os.path.join(BASE_DIR, "company.db")

mysql_db = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST", "localhost"),
    user=os.getenv("MYSQL_USER", "root"),
    password=os.getenv("MYSQL_PASSWORD", "root"),
    database=os.getenv("MYSQL_DATABASE", "company"),
)
sqlite_db = sqlite3.connect(SQLITE_PATH)

try:
    sqlite_db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(50) NOT NULL,
            email VARCHAR(50) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(30) NOT NULL
        );
        CREATE TABLE IF NOT EXISTS employee (
            eid INTEGER PRIMARY KEY AUTOINCREMENT,
            ename VARCHAR(50),
            edept VARCHAR(50),
            esalary INTEGER,
            ephone VARCHAR(15),
            Manager_id INTEGER,
            FOREIGN KEY (Manager_id) REFERENCES users(id)
        );
    """)
    source = mysql_db.cursor()
    target = sqlite_db.cursor()
    # Avoid silently replacing data if this SQLite database already contains rows.
    for table in ("users", "employee"):
        target.execute(f"SELECT COUNT(*) FROM {table}")
        if target.fetchone()[0] > 0:
            raise RuntimeError(
                f"SQLite table '{table}' is not empty. Back up company.db and "
                "use an empty SQLite database before running migration again."
            )
    for table, columns in [
        ("users", "id, name, email, password, role"),
        ("employee", "eid, ename, edept, esalary, ephone, Manager_id"),
    ]:
        source.execute(f"SELECT {columns} FROM {table}")
        rows = source.fetchall()
        marks = ", ".join(["?"] * len(columns.split(",")))
        target.executemany(
            f"INSERT OR REPLACE INTO {table} ({columns}) VALUES ({marks})", rows
        )
        print(f"Copied {len(rows)} rows from {table}.")
    sqlite_db.commit()
    source.close()
    target.close()
    print(f"Migration complete: {SQLITE_PATH}")
finally:
    mysql_db.close()
    sqlite_db.close()
