#DB using sqlite3


#1
#imports for encryption with becrypt, data and time, db and search
import sqlite3
import bcrypt
import logging
import os
from datetime import datetime
import re
#1 end



#2
# Database path
DB = os.path.join(os.path.dirname(__file__), 'secure.db')
#2 end





#3
# Logging setup
logging.basicConfig(
    filename='secure_app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
#3end 





#4
# DataBase Connection
def get_db_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
#4 end





#5 
# Initializes Database via SQLLite DB
#  tables for users and notes 
#opens connection 
def init_db():
    conn = get_db_connection()

    #user table 
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL)''')
    
    #notes table 
    conn.execute('''CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE )''')
    
    conn.commit()
    conn.close()
    logging.info("Database initialized successfully.")

init_db()
#5 end 





#6
# Input Validation
def valid_username(username):
    return re.fullmatch(r"[A-Za-z0-9_]{3,30}", username) is not None

#password
def valid_password(password):
    return len(password) >= 6

#title
def valid_note_title(title):
    return re.fullmatch(r"[\w\s.,!?'-]{1,100}", title) is not None
#6 end 





#7
# User Management

#7.1 
#responsible for registering new users in SQLLite database
#validates input and hashes password
def create_user(username, password):
    #validate username 
    if not valid_username(username):
        logging.warning(f"Invalid username attempted: {username}")
        raise ValueError("Invalid username. Use 3-30 letters, numbers, or underscores.")
    
    #validate password 
    if not valid_password(password):
        logging.warning(f"Password too short for username: {username}")
        raise ValueError("Password too short. Minimum 6 characters required.")

    #hash encrypt password using bcrypt.gensalt() and hashpw()
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    #Db connection opens SQLite 
    conn = get_db_connection()

    #insert new user into the users table 
    #stores hashed password 
    try:
        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_pw.decode('utf-8'))
        )
        conn.commit()
        logging.info(f"User created successfully: {username}")
    
    except sqlite3.IntegrityError as e:
        logging.warning(f"Failed to create user {username}: {e}")
        
        raise ValueError("Username already exists. Choose another.")
    
    except Exception as e:
        logging.error(f"Unexpected error creating user {username}: {e}")
        
        raise ValueError("Unexpected error. Contact admin.")
    
    finally:
        conn.close()
#7.1 end 



#7.2 
#verifies user details 
def verify_user(username, password):
    conn = get_db_connection()

    try:
        # Log login attempt
        logging.info(f"Login attempt received with username: '{username}'")

        #check inputs 
        if not valid_username(username):
            logging.warning(f"Rejected login - invalid username format: '{username}'")
            return None
        
        #check password 
        if not valid_password(password):
            logging.warning(f"Rejected login - password too short for username: '{username}'")
            return None

        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        
        #missing user than fail 
        if not user:
            logging.warning(f"Login failed - user does not exist: '{username}'")
            return None
        
        #password verify 
        if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            logging.info(f"User logged in successfully: '{username}'")
            return user['id']

        logging.warning(f"Login failed - incorrect password for user: '{username}'")
        return None
    
    #error handling 
    except Exception as e:
        logging.error(f"Unexpected error during login attempt for '{username}': {e}")
        return None
    
    #clean ensures db is closed 
    finally:
        conn.close()
#7.2 end

#7 end 







#8
# Notes Management

#8.1
#new note into the notes table for a given user with validation
def create_note(user_id, title, content):

    #validates 
    if not valid_note_title(title):
        logging.warning(f"Invalid note title by user {user_id}: {title}")
        raise ValueError("Invalid note title. Only letters, numbers, punctuation allowed (max 100 chars).")
    
    #db connection 
    conn = get_db_connection()


    try:
        #insert the note into table 
        conn.execute(
            "INSERT INTO notes (user_id, title, content, created_at) VALUES (?, ?, ?, ?)",
            (user_id, title, content, datetime.utcnow().isoformat()))
        
        conn.commit()
        logging.info(f"Note created for user {user_id}: {title}")
    
    #error handling 
    except Exception as e:
        logging.error(f"Error creating note for user {user_id}: {e}")
        raise ValueError("Unable to create note. Contact admin.")
    
    #clean connection closed 
    finally:
        conn.close()
#8.1 end 






#8.2
def get_notes(user_id):

    #connection 
    conn = get_db_connection()
    
    try:
        notes = conn.execute(
            "SELECT id, title, created_at FROM notes WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        ).fetchall()
        
        return notes
    
    #error catches 
    except Exception as e:
        logging.error(f"Error fetching notes for user {user_id}: {e}")
        
        raise ValueError("Unable to fetch notes. Contact admin.")
    
    #close connection 
    finally:
        conn.close()
#8.2 end




#8.3
#retrieves a single note from the DB by ID 
def get_note_by_id(note_id):

    #connection 
    conn = get_db_connection()
    
    try:
        #gets id , title etc 
        note = conn.execute(
            "SELECT id, user_id, title, content FROM notes WHERE id = ?",
            (note_id,)
        ).fetchone()
        
        if not note:
            logging.warning(f"Note not found: {note_id}")
        
        return note
    
    #error catches 
    except Exception as e:
        logging.error(f"Error fetching note {note_id}: {e}")
        
        raise ValueError("Unable to fetch note. Contact admin.")
    
    #close connection 
    finally:
        conn.close()
#8.3 end 




#8.4 
#updates the existing note in the database with new title
#and content while alos recording the update timestamp
def update_note(note_id, title, content):
    
    #calls helper to check title 
    if not valid_note_title(title):
        logging.warning(f"Invalid note title for update {note_id}: {title}")
        
        raise ValueError("Invalid note title. Only letters, numbers, punctuation allowed (max 100 chars).")
    
    #connection to SQlite DB
    conn = get_db_connection()
    
    try:
        #executes update query for title etc 
        conn.execute(
            "UPDATE notes SET title = ?, content = ?, updated_at = ? WHERE id = ?",
            (title, content, datetime.utcnow().isoformat(), note_id)
        )
        conn.commit()
        logging.info(f"Note updated: {note_id}")

     #error catches 
    except Exception as e:
        logging.error(f"Error updating note {note_id}: {e}")
        
        raise ValueError("Unable to update note. Contact admin.")
    
    #close connection
    finally:
        conn.close()
#8.4 end 


#8.5 
def delete_note(note_id): 

    #connection DB  
    conn = get_db_connection()
    
    #delete from query table 
    try:
        conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()
        logging.info(f"Note deleted: {note_id}")
    
    #error handling 
    except Exception as e:
        logging.error(f"Error deleting note {note_id}: {e}")
        
        raise ValueError("Unable to delete note. Contact admin.")
    
    #close connection 
    finally:
        conn.close()
#8.5 end 


#8 end 
