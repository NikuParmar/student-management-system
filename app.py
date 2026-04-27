"""
Student Management System - Main Application
A comprehensive full-stack Student Management System with Flask and SQLite.

Features:
- User Authentication with password hashing
- Role-based access control (Admin, Faculty, Student)
- CRUD operations for students
- Search, filter, and pagination
- Export to CSV, Excel, PDF
- Activity logging
- Modern Bootstrap 5 UI
"""
from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import os
from datetime import datetime

# Import blueprints from routes
from routes.auth_routes import auth_bp
from routes.student_routes import student_bp
from routes.admin_routes import admin_bp
from routes.feature_routes import feature_bp

app = Flask(__name__)
import secrets
app.secret_key = secrets.token_bytes(32)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(student_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(feature_bp)

DB_NAME = 'database.db'


def get_db():
    """Get database connection"""
    return sqlite3.connect(DB_NAME)


def init_db():
    """Initialize database with all required tables"""
    conn = get_db()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT,
        email TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Students table - Enhanced with more fields
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        enrollment_number TEXT UNIQUE,
        course TEXT,
        year INTEGER,
        phone TEXT,
        address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Access requests table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS access_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        email TEXT,
        role TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Feature requests table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feature_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        request_type TEXT,
        user_role TEXT,
        status TEXT DEFAULT 'pending',
        created_by TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Activity logs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        action TEXT,
        details TEXT,
        ip_address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Add columns if they don't exist (for existing databases)
    try:
        cursor.execute("SELECT role FROM access_requests LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE access_requests ADD COLUMN role TEXT")

    try:
        cursor.execute("SELECT user_role FROM feature_requests LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE feature_requests ADD COLUMN user_role TEXT")

    try:
        cursor.execute("SELECT email FROM users LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
    
    try:
        cursor.execute("SELECT created_at FROM users LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP")
        cursor.execute("UPDATE users SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")

    try:
        cursor.execute("SELECT enrollment_number FROM students LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE students ADD COLUMN enrollment_number TEXT")
        cursor.execute("ALTER TABLE students ADD COLUMN phone TEXT")
        cursor.execute("ALTER TABLE students ADD COLUMN address TEXT")

    # Insert default admin if not exists (using bcrypt)
    import bcrypt
    admin_password_bytes = bcrypt.hashpw('admin123'.encode(), bcrypt.gensalt()).decode('utf-8')
    
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if cursor.fetchone() is None:
        cursor.execute(
            "INSERT INTO users (username, password, role, email) VALUES (?, ?, ?, ?)",
            ('admin', admin_password_bytes, 'admin', 'admin@school.edu')
        )

    conn.commit()
    conn.close()


@app.route('/')
def index():
    """Root route - redirect to login"""
    if 'user' in session:
        if session.get('role') == 'admin':
            return redirect('/admin')
        else:
            return redirect('/dashboard')
    return redirect('/login')


# Error handlers
@app.errorhandler(404)
def not_found(e):
    """404 error handler"""
    return render_template('error.html', error_code=404, message='Page not found'), 404


@app.errorhandler(500)
def server_error(e):
    """500 error handler"""
    return render_template('error.html', error_code=500, message='Internal server error'), 500


if __name__ == '__main__':
    # Initialize database
    init_db()
    
    print("=" * 50)
    print("Student Management System")
    print("=" * 50)
    print("Server running at http://127.0.0.1:5000")
    print("Default admin credentials:")
    print("  Username: admin")
    print("  Password: admin123")
    print("=" * 50)
    
    app.run(debug=True)

