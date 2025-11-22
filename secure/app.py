from flask import Flask, render_template, request, redirect, session, flash
from markupsafe import escape
import secrets
from db import create_user, verify_user, get_notes, create_note, get_note_by_id, update_note, delete_note

app = Flask(__name__)
app.secret_key = secrets.token_hex(24)  # secure session key

# -----------------------------
# ROUTES
# -----------------------------

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/notes')
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        try:
            create_user(username, password)
            flash("User created successfully. Please login.")
            return redirect('/login')
        except ValueError as ve:
            flash(str(ve))
            return redirect('/register')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        user_id = verify_user(username, password)
        if user_id:
            session['user_id'] = user_id
            flash(f"Welcome, {username}!")
            return redirect('/notes')
        flash("Invalid login.")
        return redirect('/login')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully")
    return redirect('/login')


@app.route('/notes')
def notes():
    if 'user_id' not in session:
        return redirect('/login')
    notes_list = get_notes(session['user_id'])
    return render_template('notes.html', notes=notes_list)


@app.route('/new_note', methods=['GET', 'POST'])
def new_note():
    if 'user_id' not in session:
        return redirect('/login')
    if request.method == 'POST':
        title = escape(request.form['title'].strip())
        content = escape(request.form['content'].strip())
        if not title:
            flash("Title cannot be empty")
            return redirect('/new_note')
        try:
            create_note(session['user_id'], title, content)
            flash("Note created successfully")
            return redirect('/notes')
        except ValueError as ve:
            flash(str(ve))
            return redirect('/new_note')
    return render_template('new_note.html')


@app.route('/edit_note/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    if 'user_id' not in session:
        return redirect('/login')
    note = get_note_by_id(note_id)
    if not note or note['user_id'] != session['user_id']:
        flash("Unauthorized access")
        return redirect('/notes')
    if request.method == 'POST':
        title = escape(request.form['title'].strip())
        content = escape(request.form['content'].strip())
        if not title:
            flash("Title cannot be empty")
            return redirect(f'/edit_note/{note_id}')
        update_note(note_id, title, content)
        flash("Note updated successfully")
        return redirect('/notes')
    return render_template('edit_note.html', note=note)


@app.route('/view_note/<int:note_id>')
def view_note(note_id):
    if 'user_id' not in session:
        return redirect('/login')
    note = get_note_by_id(note_id)
    if not note or note['user_id'] != session['user_id']:
        flash("Unauthorized or note not found")
        return redirect('/notes')
    return render_template('view_note.html', title=note['title'], content=note['content'])


@app.route('/delete_note/<int:note_id>', methods=['POST'])
def delete(note_id):
    if 'user_id' not in session:
        return redirect('/login')
    note = get_note_by_id(note_id)
    if not note or note['user_id'] != session['user_id']:
        flash("Unauthorized access")
        return redirect('/notes')
    delete_note(note_id)
    flash("Note deleted")
    return redirect('/notes')


# -----------------------------
# RUN SERVER
# -----------------------------
if __name__ == "__main__":
    url = "http://127.0.0.1:5002/"
    print(f"Flask app running! Open in browser: {url}")
    app.run(debug=True, host="0.0.0.0", port=5002)

