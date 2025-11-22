# ============================================
# SECURE DB MODULE
# ============================================

import sqlite3
import bcrypt
import logging
from datetime import datetime
import re

# Database file
DB_FILE = "secure.db"

# Logging
logging.basicConfig(
    filename='secure_app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Singleton DB Manager
class DatabaseManager:
    _instance = None
    _connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_connection(self):
        if self._connection is None:
            self._connection = sqlite3.connect(DB_FILE, check_same_thread=False)
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA foreign_keys = ON")
        return self._connection

    def close(self):
        if self._connection:
            self._connection.close()
            self._connection = None

def get_db_connection():
    return DatabaseManager().get_connection()

# Initialize DB
def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        content TEXT,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )''')
    conn.commit()
    logging.info("Database initialized successfully.")

init_db()

# Validation helpers
def valid_username(username):
    return re.fullmatch(r"[A-Za-z0-9_]{3,30}", username) is not None

def valid_password(password):
    return len(password) >= 6

def valid_note_title(title):
    return re.fullmatch(r"[\w\s.,!?'-]{1,100}", title) is not None

# User management
def create_user(username, password):
    if not valid_username(username):
        raise ValueError("Invalid username. Use 3-30 letters, numbers, or underscores.")
    if not valid_password(password):
        raise ValueError("Password too short. Minimum 6 characters required.")
    
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                     (username, hashed_pw.decode('utf-8')))
        conn.commit()
        logging.info(f"User created: {username}")
    except sqlite3.IntegrityError:
        raise ValueError("Username already exists.")

def verify_user(username, password):
    conn = get_db_connection()
    if not valid_username(username) or not valid_password(password):
        return None
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if not user:
        return None
    if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return user['id']
    return None

# Notes management
def create_note(user_id, title, content):
    if not valid_note_title(title):
        raise ValueError("Invalid note title.")
    conn = get_db_connection()
    conn.execute("INSERT INTO notes (user_id, title, content, created_at) VALUES (?, ?, ?, ?)",
                 (user_id, title, content, datetime.utcnow().isoformat()))
    conn.commit()

def get_notes(user_id):
    conn = get_db_connection()
    return conn.execute("SELECT id, title, created_at FROM notes WHERE user_id = ? ORDER BY created_at DESC",
                        (user_id,)).fetchall()

def get_note_by_id(note_id):
    conn = get_db_connection()
    return conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()

def update_note(note_id, title, content):
    if not valid_note_title(title):
        raise ValueError("Invalid note title.")
    conn = get_db_connection()
    conn.execute("UPDATE notes SET title = ?, content = ?, updated_at = ? WHERE id = ?",
                 (title, content, datetime.utcnow().isoformat(), note_id))
    conn.commit()

def delete_note(note_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
