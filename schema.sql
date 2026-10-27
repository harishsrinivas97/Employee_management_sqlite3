-- SQLite schema for Employee Management System
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
