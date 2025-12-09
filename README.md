# Secure Flask Notes Application

A secure Flask-based web application for creating, viewing, editing, and deleting personal notes. This application incorporates best practices for session management, password security, and web security headers.

---

## Table of Contents

- [Features](#features)
- [Security Mitigations](#security-mitigations)
- [Requirements](#requirements)
- [Setup Instructions](#setup-instructions)
- [Project Structure](#project-structure)


---

## Features

- User registration and login with password hashing (bcrypt)
- Session management with secure cookies
- CSRF protection on all forms
- Create, edit, delete, view, and search personal notes
- Notes are user-specific and protected by authorization checks
- Simple search functionality for user's notes
- Logging of important application events

---

## Security Mitigations

This application implements several security measures:

1. **Password Security**
   - Passwords are hashed using **bcrypt** before storing in the database.
   - Input validation ensures minimum password length and proper username format.

2. **Session Security**
   - Cookies are `HttpOnly` to prevent JavaScript access.
   - `Secure` flag ensures cookies are sent only over HTTPS.
   - `SameSite=Lax` to mitigate CSRF risks.
   - Sessions expire after 30 minutes of inactivity.

3. **CSRF Protection**
   - All forms are protected with **Flask-WTF CSRF tokens**.
   - Tokens remain valid for the session lifetime.

4. **Web Security Headers**
   - `X-Frame-Options: DENY` → Prevents clickjacking.
   - `X-Content-Type-Options: nosniff` → Prevents MIME-type confusion.
   - `Strict-Transport-Security` → Enforces HTTPS in production.
   - `Referrer-Policy: no-referrer` → No URL leakage.
   - `Permissions-Policy` → Restricts access to browser features.
   - `Content-Security-Policy` → Restricts loaded resources to self only.

5. **Database Security**
   - SQLite database uses foreign key constraints.
   - Parameterized queries prevent SQL injection.
   - Singleton pattern ensures single DB connection to avoid concurrency issues.

---

## Requirements

- Python 3.10+
- Flask
- Flask-WTF
- bcrypt
- SQLite3
- Optional: `virtualenv` for isolated environment

---

## Setup Instructions

1. **Clone the repository**

bash

- git clone <your-repo-url>
- cd <your-repo-folder>

2. **Run**
- cd secure
- venv should be auto but if not enter venv\Scripts\activate
- python ./app.py will start the url for app
- login etc

## Test setup 
- open new terminal
- enter  python -m unittest secure.tests.test_app
- Will start FireFox automatic testing 




