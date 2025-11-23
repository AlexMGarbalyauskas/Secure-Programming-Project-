#1
#imports
import sqlite3
import bcrypt
import logging
from datetime import datetime
import re
#1 end 



# Database file for SQLite
DB_FILE = "secure.db"



#2 
# Logging configuration
logging.basicConfig(
    filename="secure_app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
#2 end




#3 
# Singleton DB Manager
class DatabaseManager:
    _instance = None
    _connection = None
# 3 end 




#4
# Singleton pattern to ensure one DB connection
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
#4 end






#5
# Get or create DB connection
    def get_connection(self):
        if self._connection is None:
            self._connection = sqlite3.connect(DB_FILE, check_same_thread=False)
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA foreign_keys = ON")
        return self._connection
#5 end 





#6
# Close DB connection
    def close(self):
        if self._connection:
            self._connection.close()
            self._connection = None
# 6 end 






#7
# Helper to get DB connection
def get_db_connection():
    # DatabaseManager singleton
    return DatabaseManager().get_connection()
#7 end







#8
# Initialize DB by creating necessary tables for users and notes
def init_db():
    conn = get_db_connection()

    # create users table
    conn.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )""")

    # create notes table
    conn.execute("""CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        content TEXT,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )""")
    # commit changes
    conn.commit()
    # log success
    logging.info("Database initialized successfully.")

# Call to initialize DB on module load
init_db()
#8 end 








# 9 
# Validation helpers
def valid_username(username):
    # Alphanumeric and underscores, 3-30 chars
    return re.fullmatch(r"[A-Za-z0-9_]{3,30}", username) is not None

def valid_password(password):
    # Strengthen as needed (length/complexity)
    return len(password) >= 6

def valid_note_title(title):
    # Allow letters, numbers, spaces, and basic punctuation, max 100 chars
    return re.fullmatch(r"[\w\s.,!?'-]{1,100}", title) is not None
# 9 end 






#10 
# User management
def create_user(username, password):
    
    # Validate inputs
    if not valid_username(username):
        raise ValueError("Invalid username. Use 3-30 letters, numbers, or underscores.")
    
    # Validate password
    if not valid_password(password):
        raise ValueError("Password too short. Minimum 6 characters required.")

    # Hash password using bcrypt
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    # connect to DB and insert user
    conn = get_db_connection()

    try:
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                     (username, hashed_pw.decode("utf-8")))
        conn.commit()
        # log user creation
        logging.info(f"User created: {username}")

    except sqlite3.IntegrityError:
        raise ValueError("Username already exists.")
# 10 end 






#11 
# Verify user credentials
def verify_user(username, password):

    # connect to DB
    conn = get_db_connection()

    # Validate inputs
    if not valid_username(username) or not valid_password(password):
        return None
    
    # Fetch user by username
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if not user:
        return None
    
    # Check password using bcrypt
    if bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
        return user["id"]
    return None
# 11 end





# 12 
# Notes management
def create_note(user_id, title, content):
    if not valid_note_title(title):
        # Validate note title
        raise ValueError("Invalid note title.")
    
    # connect to DB and insert note
    conn = get_db_connection()

    # Insert note with timestamp
    conn.execute("INSERT INTO notes (user_id, title, content, created_at) VALUES (?, ?, ?, ?)",
                 (user_id, title, content, datetime.utcnow().isoformat()))
    conn.commit()



# Fetch notes for a user
def get_notes(user_id):
    conn = get_db_connection()
    return conn.execute(
        "SELECT id, title, created_at FROM notes WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    ).fetchall()




# Fetch a single note by ID
def get_note_by_id(note_id):
    conn = get_db_connection()
    return conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()



#   Update a note
def update_note(note_id, title, content):

    # Validate note title
    if not valid_note_title(title):
        raise ValueError("Invalid note title.")
    conn = get_db_connection()

    # update note by ID
    conn.execute(
        "UPDATE notes SET title = ?, content = ?, updated_at = ? WHERE id = ?",
        (title, content, datetime.utcnow().isoformat(), note_id)
    )
    conn.commit()



#   Delete a note
def delete_note(note_id):
    conn = get_db_connection()

    # delete note by ID
    conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()


# 12 end