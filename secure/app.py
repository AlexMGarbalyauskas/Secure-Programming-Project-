# start project here python app.py on terminal 

#routes to pages 


#1 
#imports 
from flask import Flask, render_template, request, redirect, session, flash
from markupsafe import escape
import os
import webbrowser
from db import (
create_user,
verify_user,
get_notes,
create_note,
get_note_by_id,
update_note,
delete_note
)
#1 end 




app = Flask(__name__)
app.secret_key = os.urandom(24)




#2 
# Home 
#home is the index.html page 
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/notes')
    return render_template('index.html')
#2 end 




#3 
# Register new user 
#opens register page 
@app.route('/register', methods=['GET', 'POST'])
def register():

    #handling form submission , .strip removes trail spaces 
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()


        #password check length and password 
        if len(username) < 3:
            flash("Username must be at least 3 characters.")
            return redirect('/register')
        
        if len(password) < 6:
            flash("Password must be at least 6 characters.")
            return redirect('/register')

    #user creation by calling create_user() then shows success or value error 
        try:
            create_user(username, password)
            flash("User created successfully. Please login.")
            return redirect('/login')
        
        except ValueError as ve:
            flash(str(ve))
            return redirect('/register')
        
        #user exists already 
        except Exception:
            flash("Username already exists")
            return redirect('/register')

    return render_template('register.html')
#3 end 





#4
# Login the user login.html page 
@app.route('/login', methods=['GET', 'POST'])

#defines the /login route 
def login():

    #handling login submission of username and password 
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        #verification of user 
        user_id = verify_user(username, password)
        
        #success 
        if user_id:
            session['user_id'] = user_id
            flash(f"Welcome, {username}!")
            return redirect('/notes')
        
        #incorrect
        flash("Invalid login. Check username/password or input requirements.")
        return redirect('/login')

    return render_template('login.html')
#4 end 







#5 
# Logouts the user back to login page 
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully")
    return redirect('/login')
#5 end 






#6
# List of notes 
@app.route('/notes')
def notes():
    if 'user_id' not in session:
        return redirect('/login')

    notes_list = get_notes(session['user_id'])
    return render_template('notes.html', notes=notes_list)
#6 end 







#7 
# Create new Note 
#accepts the get of the page route 
@app.route('/new_note', methods=['GET', 'POST'])
def new_note():

    #if user tries to open page without access then prevent back to login 
    if 'user_id' not in session:
        return redirect('/login')

    #handling form submission extracts title and content 
    if request.method == 'POST':
        title = escape(request.form['title'].strip())
        content = escape(request.form['content'].strip())

        #validate ensure note has title 
        if len(title) == 0:
            flash("Title cannot be empty")
            return redirect('/new_note')

        #creates the note 
        try:
            create_note(session['user_id'], title, content)
            flash("Note created successfully")

        except ValueError as ve:
            flash(str(ve))
            return redirect('/new_note')

        return redirect('/notes')

    return render_template('new_note.html')
#7 end 








#8
# Edit the Note with new data 
@app.route('/edit_note/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):

    #check if user is logged in if not then back to login
    if 'user_id' not in session:
        return redirect('/login')

    #Auth check retreive ID if note does not
    #exist then flash error or redirect to notes
    #prevents editing notes they dont own 
    note = get_note_by_id(note_id)
    if not note or note['user_id'] != session['user_id']:
        flash("Unauthorized access")
        return redirect('/notes')

    #submit form takes title and content from the form 
    if request.method == 'POST':

        #escape() prevents XSS attacks malicious HTML
        #or JS injection
        title = escape(request.form['title'].strip())
        content = escape(request.form['content'].strip())

        #validate needs title 
        if len(title) == 0:
            flash("Title cannot be empty")
            return redirect(f'/edit_note/{note_id}')
        
        #update note by update_note() 
        try:
            update_note(note_id, title, content)
            flash("Note updated successfully")
        
        #error handle redirect back 
        except ValueError as ve:
            flash(str(ve))
            return redirect(f'/edit_note/{note_id}')

        return redirect('/notes')

    return render_template('edit_note.html', note=note)
#8 end 







#9
# View the note seperatley in view_note.html page 
@app.route('/view_note/<int:note_id>')
def view_note(note_id):
    if 'user_id' not in session:
        return redirect('/login')

    note = get_note_by_id(note_id)
    if not note or note['user_id'] != session['user_id']:
        flash("Unauthorized access or note not found")
        return redirect('/notes')

    return render_template(
        'view_note.html',
        title=note['title'],
        content=note['content']
    )
#9 end 







#10 
# Delete the note 
@app.route('/delete_note/<int:note_id>', methods=['POST'])
def delete(note_id):

    #if user not logged then redirect back to login page 
    #prevents unauth access 
    if 'user_id' not in session:
        return redirect('/login')

    note = get_note_by_id(note_id)
    if not note or note['user_id'] != session['user_id']:
        flash("Unauthorized access")
        return redirect('/notes')

    delete_note(note_id)
    flash("Note deleted")
    return redirect('/notes')
#10 end 






#11
# Search Notes 
@app.route('/search', methods=['GET'])
def search():

    #access control back to login if not logged in 
    if 'user_id' not in session:
        return redirect('/login')

    #gains query deafult to empty if none given 
    query = request.args.get('q', '').strip()
    results = []
    
    #fetch all notes to user 
    if query:
        all_notes = get_notes(session['user_id'])
        results = [note for note in all_notes if query.lower() in note['title'].lower()]
        if not results:
            flash(f"No notes found for '{query}'")
        else:
            flash(f"Found {len(results)} note(s) matching '{query}'")
    else:
        flash("Please enter a search query")

    return render_template('search.html', results=results, query=query)
#11 end 




#12 
# Start the server and makes it open auto on broswer 
if __name__ == '__main__':
    webbrowser.open("http://127.0.0.1:5002/")
    app.run(debug=True, host='0.0.0.0', port=5002)
#12 end 