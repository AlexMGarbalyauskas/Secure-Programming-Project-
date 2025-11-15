
## Project Overview

This project is a **Flask-based Notes Web Application** created for the secure programming module.  
It includes:

- Secure version (`secure` branch)  
- Insecure version (`insecure` branch)  
- Main branch (project overview, documentation, navigation)

The purpose of the project is to demonstrate:

1. Common web vulnerabilities (OWASP Top 10)  
2. Exploitation of insecure code  
3. Mitigation and secure coding practices  
4. Logging and monitoring  

---

## Technologies & Tools Used

### **Backend**
- Python 3  
- Flask  
- SQLite  

### **Frontend**
- HTML5  
- CSS  
- Jinja2 templating  

### **Security Tools**
- `markupsafe` escaping  
- Prepared statements (secure version)  
- Basic session security  
- Logging & monitoring  

### **Version Control**
- Git & GitHub  
- Branch-based workflow (insecure & secure separation)

---

## Branch Structure

The repository includes **three main branches**:

### `insecure`
Contains intentionally vulnerable code including:

- SQL Injection  
- Stored / Reflected / DOM XSS  
- Sensitive Data Exposure  
- Weak authentication  
- Little or no validation  

This branch is used to capture screenshots and demonstrate attacks.

---

### `secure`
Contains the fully secured application:

- Input validation  
- Escaping & encoding  
- Prepared SQL queries  
- Cookie/session hardening  
- Secure password hashing  
- Logging & monitoring  
- XSS & SQLi mitigation  

This version is for demonstration of secure coding practices.

---

### `main` (You are here)
Contains:

- Documentation  
- Project explanation  
- Branch navigation  
- Installation instructions  

This branch does **not** run the app — it provides the overview.

---

## How to Download & Run the Project (ZIP or Git)

### Option 1 — Download as ZIP
1. Click **Code → Download ZIP** on GitHub  
2. Extract the ZIP file  
3. Open the folder  
4. Choose either:
   - `secure` folder  
   - `insecure` folder  
5. Open a terminal inside the chosen folder  
6. Install dependencies:
   ```bash
   pip install flask
