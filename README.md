# Insecure Notes Web Application (Insecure Version)


## IMPORTANT – PURPOSE OF THIS VERSION

This branch contains the **intentionally insecure version** of the Notes Web Application.  
It was created for the assignment requirement to **introduce vulnerabilities**, demonstrate exploitation, and then show the secure mitigations in the `secure` branch.

This version *must not* be used in production.  
It exists **only for educational and testing purposes**.

---

## Included Vulnerabilities (Required by Assignment)

This insecure version intentionally includes vulnerabilities from **OWASP Top 10**, specifically:

###  1. SQL Injection (A03: Injection)
Examples:
- Login form vulnerable to `' OR '1'='1`  
- Registration vulnerable to SQL tampering  
- Note search uses unsafe string concatenation  

###  2. XSS – Stored, Reflected, DOM-Based (A07: XSS)
Examples:
- Notes allow `<script>` to be stored and executed  
- Reflected XSS on search page  
- DOM-based XSS in JavaScript (if included)

###  3. Sensitive Data Exposure (A02: Cryptographic Failures)
Examples:
- Plain-text passwords stored in SQLite  
- Session not secured properly  
- Error messages reveal stack traces  
- No output encoding  

###  Additional Weaknesses
- No escaping or sanitisation  
- No validation  
- No password hashing  
- No authorization checks  
- No CSRF protection  
- Minimal logging or none at all  

These vulnerabilities are required for demonstrating exploitation and then showing mitigations.


## How to Run the Insecure Application
- cd insecure
- venv\Scripts\activate
- python app.py 

opens link to open 

### Install Dependencies
```bash
pip install flask
