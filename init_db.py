import sqlite3
import os

# Database and schema files are located in the same folder as this script.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "company.db")
SCHEMA_FILE = os.path.join(BASE_DIR, "schema.sql")

def initialize_database():
    """Create the SQLite database and tables using schema.sql."""
    if not os.path.exists(SCHEMA_FILE):
        raise FileNotFoundError(f"Schema file not found: {SCHEMA_FILE}")

    with open(SCHEMA_FILE, "r", encoding="utf-8") as file:
        schema = file.read()

    with sqlite3.connect(DATABASE) as connection:
        connection.executescript(schema)

    print(f"Database initialized successfully: {DATABASE}")

if __name__ == "__main__":
    initialize_database()
