
#1
#imports 
import os
import secrets
from datetime import timedelta
from flask import Flask, render_template, request, redirect, session, flash
from flask_wtf import CSRFProtect
from db import create_user, verify_user, get_notes, create_note, get_note_by_id, update_note, delete_note
#1 end 




# flask app
app = Flask(__name__)

# Secret key is critical for signing session cookies and CSRF tokens.
# In production, we load it from environment variables for stability and security.
# Fallback: generate a random secret for local dev.
app.secret_key = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(24))




#2
# Session and CSRF configuration
app.config.update({

    # Prevent JavaScript from accessing session cookies (mitigates XSS attacks).
    "SESSION_COOKIE_HTTPONLY": True,

    # Ensure cookies are only sent over HTTPS in production.
    # For local dev, you can set this to False, but in real deployments it MUST be True.
    "SESSION_COOKIE_SECURE": True,

    # Restrict cookies to same-site requests, reducing CSRF risk.
    "SESSION_COOKIE_SAMESITE": "Lax",

    # Limit session lifetime to 30 minutes of inactivity.
    # This reduces exposure if a session token is stolen.
    "PERMANENT_SESSION_LIFETIME": timedelta(minutes=30),

    # Disable CSRF token expiration (tokens remain valid until session ends).
    "WTF_CSRF_TIME_LIMIT": None
})
#2 end 



# Enable CSRF protection for all forms.
# This prevents attackers from forging requests on behalf of logged-in users.
csrf = CSRFProtect(app)



#3
# Security headers applied to all responses.
@app.after_request
def set_security_headers(response):
    # Prevent clickjacking by disallowing the app to be embedded in iframes.
    response.headers["X-Frame-Options"] = "DENY"

    # Stop browsers from MIME-sniffing responses (prevents content-type confusion attacks).
    response.headers["X-Content-Type-Options"] = "nosniff"

    # Enforce HTTPS with HSTS (HTTP Strict Transport Security).
    # Once enabled, browsers will only connect via HTTPS for 1 year.
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    # Prevent referrer leakage (no sensitive URLs passed to external sites).
    response.headers["Referrer-Policy"] = "no-referrer"

    # Lock down browser features (Permissions Policy).
    # Explicitly deny access to sensors, camera, mic, geolocation, etc.
    # This reduces attack surface if malicious scripts run.
    response.headers["Permissions-Policy"] = (
        "geolocation=(), microphone=(), camera=(), accelerometer=(), gyroscope=(), "
        "magnetometer=(), usb=(), payment=(), interest-cohort=()"
    )

    # Content Security Policy (CSP).
    # Restricts what resources can load:
    # Only allow scripts, styles, images, fonts from self
    # Block inline scripts/styles unless explicitly allowed
    # Prevent embedding external frames
    # Force upgrade of insecure requests
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "base-uri 'self'; "
        "object-src 'none'; "
        "script-src 'self'; "
        "style-src 'self'; "
        "img-src 'self'; "
        "font-src 'self'; "
        "frame-ancestors 'none'; "
        "form-action 'self'; "
        "upgrade-insecure-requests"
    )

    # Remove or neutralize server banner (e.g., Werkzeug/Flask version).
    # This prevents attackers from fingerprinting your stack.
    if "Server" in response.headers:

        del response.headers["Server"]

        # Alternatively, you can set it to a generic value:
    response.headers["Server"] = " "

    return response
#3 end







#4 
# Routes
@app.route("/")

# index route 
def index():

    # Redirect logged-in users directly to notes.
    if "user_id" in session:

        return redirect("/notes")
    
    return render_template("index.html")







# register route
@app.route("/register", methods=["GET", "POST"])

#  register function to handle user registration
def register():

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        try:
            # Create user securely (db.py should hash passwords with bcrypt).
            create_user(username, password)
            flash("User created successfully. Please login.")

            return redirect("/login")
        
        except ValueError as ve:
            # Handle duplicate usernames or validation errors.
            flash(str(ve))

            return redirect("/register")
        
    return render_template("register.html")







# login route
@app.route("/login", methods=["GET", "POST"])

# login function to handle user login
def login():

# Check if form submitted 
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        # Verify credentials securely (db.py should check bcrypt hash).
        user_id = verify_user(username, password)

# If valid, set session cookie with hardened settings.
        if user_id:
            # Store user_id in session (cookie is hardened above).
            session["user_id"] = user_id
            flash(f"Welcome, {username}!")

            return redirect("/notes")
        
        # Invalid credentials
        flash("Invalid login.")
        
        return redirect("/login")
    
    return render_template("login.html")




# logout route
@app.route("/logout")
def logout():
    # Clear session on logout to prevent reuse of stolen cookies.
    session.clear()
    flash("Logged out successfully")

# Redirect to home page after logout
    return redirect("/login")




# notes route
@app.route("/notes")
def notes():

    if "user_id" not in session:

        return redirect("/login")
    
    # Fetch notes belonging only to the logged-in user.
    notes_list = get_notes(session["user_id"])

    return render_template("notes.html", notes=notes_list)





# new note route
@app.route("/new_note", methods=["GET", "POST"])
def new_note():

    # Create new note
    if "user_id" not in session:

        return redirect("/login")
    
    if request.method == "POST":
        title = request.form["title"].strip()
        content = request.form["content"].strip()

        if not title:
            flash("Title cannot be empty")
            return redirect("/new_note")
        
        try:
            create_note(session["user_id"], title, content)
            flash("Note created successfully")

            return redirect("/notes")
        
        except ValueError as ve:

            flash(str(ve))

            return redirect("/new_note")
        
    return render_template("new_note.html")





# edit note route
@app.route("/edit_note/<int:note_id>", methods=["GET", "POST"])

# def edit note to handle editing notes
def edit_note(note_id):

    if "user_id" not in session:

        return redirect("/login")
    note = get_note_by_id(note_id)

    # Authorization check: ensure user owns the note.
    if not note or note["user_id"] != session["user_id"]:
        flash("Unauthorized access")

        return redirect("/notes")
    
    if request.method == "POST":
        title = request.form["title"].strip()
        content = request.form["content"].strip()

        if not title:
            flash("Title cannot be empty")

            return redirect(f"/edit_note/{note_id}")
        update_note(note_id, title, content)
        flash("Note updated successfully")

        return redirect("/notes")
    
    return render_template("edit_note.html", note=note)



# view note route
@app.route("/view_note/<int:note_id>")
def view_note(note_id):

    if "user_id" not in session:

        return redirect("/login")
    note = get_note_by_id(note_id)

    # Authorization check again.
    if not note or note["user_id"] != session["user_id"]:
        flash("Unauthorized or note not found")

        return redirect("/notes")
    
    return render_template("view_note.html", title=note["title"], content=note["content"])




# delete note route
@app.route("/delete_note/<int:note_id>", methods=["POST"])
def delete(note_id):

    if "user_id" not in session:

        return redirect("/login")
    note = get_note_by_id(note_id)

    # Prevent deletion of notes not owned by the user.
    if not note or note["user_id"] != session["user_id"]:
        flash("Unauthorized access")

        return redirect("/notes")
    
    delete_note(note_id)
    flash("Note deleted")

    return redirect("/notes")




#   search route
@app.route("/search", methods=["GET"])
def search():

    if "user_id" not in session:

        return redirect("/login")
    query = request.args.get("q", "").strip()
    results = []

    if query:
        # Simple search: only within user's own notes.
        all_notes = get_notes(session["user_id"])
        results = [note for note in all_notes if query.lower() in note["title"].lower()]

    return render_template("search.html", results=results, query=query)

# 4 end 






# Run the app
if __name__ == "__main__":
    # Opens terminal URL for local testing
    # app.config["SESSION_COOKIE_SECURE"] = False
    url = "http://127.0.0.1:5002/"
    print(f"Flask app running! Open in browser: {url}")
    app.run(debug=True, host="0.0.0.0", port=5002)
