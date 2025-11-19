from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "insecurekey"  # Hardcoded and weak (Sensitive Data Exposure)

# Database connection
def get_db():
    conn = sqlite3.connect("insecure.db")
    conn.row_factory = sqlite3.Row
    return conn


# Home route
@app.route("/")
def index():
    return render_template("index.html")


# Register (insecure: plaintext passwords)
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]  # stored in plain-text

        conn = get_db()
        # SQL Injection vulnerability
        conn.execute(f"INSERT INTO users(username, password) VALUES('{username}', '{password}')")
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")


# Login (SQL injection vulnerable)
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        # SQL Injection vulnerability
        user = conn.execute(
            f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        ).fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            return redirect("/notes")

        return "Invalid credentials"

    return render_template("login.html")


# Notes page SQL injection vulnerable
@app.route("/notes")
def notes():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    # SQL Injection vulnerable
    user_notes = conn.execute(
        f"SELECT * FROM notes WHERE user_id={session['user_id']}"
    ).fetchall()
    conn.close()

    return render_template("user_notes.html", notes=user_notes)


# Create note (XSS vulnerable)
@app.route("/new_note", methods=["GET", "POST"])
def new_note():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        # Prevent SQL syntax errors but keep SQL Injection + XSS
        title = title.replace("'", "''")      # still insecure
        content = content.replace("'", "''")  # still insecure

        conn = get_db()
        conn.execute(
            f"INSERT INTO notes(title, content, user_id) VALUES('{title}', '{content}', {session['user_id']})"
        )
        conn.commit()
        conn.close()

        return redirect("/notes")

    return render_template("new_note.html")


# View note (XSS executed via |safe)
@app.route("/note/<int:note_id>")
def note(note_id):
    conn = get_db()
    note = conn.execute(f"SELECT * FROM notes WHERE id={note_id}").fetchone()
    conn.close()

    return render_template("view_note.html", note=note)


# Edit note (SQL injection)
@app.route("/edit_note/<int:note_id>", methods=["GET", "POST"])
def edit_note(note_id):
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        # Prevent SQL break but keep vulnerabilities alive
        title = title.replace("'", "''")
        content = content.replace("'", "''")

        conn.execute(
            f"UPDATE notes SET title='{title}', content='{content}' WHERE id={note_id}"
        )
        conn.commit()
        conn.close()

        return redirect("/notes")

    note = conn.execute(f"SELECT * FROM notes WHERE id={note_id}").fetchone()
    conn.close()

    return render_template("edit_note.html", note=note)


# Delete (no authorization check)
@app.route("/delete_note/<int:note_id>")
def delete_note(note_id):
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    # SQL injection vulnerability + user can delete ANY note
    conn.execute(f"DELETE FROM notes WHERE id={note_id}")
    conn.commit()
    conn.close()

    return redirect("/notes")


# Search (SQL injection + reflected XSS)
@app.route("/search", methods=["GET", "POST"])
def search():
    results = []
    if request.method == "POST":
        term = request.form["term"]

        conn = get_db()
        # SQL Injection and unsafe output
        results = conn.execute(
            f"SELECT * FROM notes WHERE title LIKE '%{term}%'"
        ).fetchall()
        conn.close()

    return render_template("search.html", results=results)


# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
