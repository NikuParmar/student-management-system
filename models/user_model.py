"""
User Model - Handles all user-related database operations
"""
import sqlite3
from datetime import datetime
import bcrypt

DB_NAME = 'database.db'


def get_db():
    """Get database connection"""
    return sqlite3.connect(DB_NAME)


def create_user(username, password, role='student', email=None):
    """Create a new user with hashed password"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Hash password with bcrypt
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')
    
    cursor.execute(
        "INSERT INTO users (username, password, role, email) VALUES (?, ?, ?, ?)",
        (username, hashed_password, role, email)
    )
    conn.commit()
    conn.close()
    return True


def verify_user(username, password):
    """Verify user credentials"""
    conn = get_db()
    cursor = conn.cursor()
    
    stored_hash = cursor.execute("SELECT password FROM users WHERE username=?", (username,)).fetchone()
    if stored_hash and bcrypt.checkpw(password.encode(), stored_hash[0].encode()):
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        return cursor.fetchone()
    return None
    user = cursor.fetchone()
    conn.close()
    return user


def get_user_by_username(username):
    """Get user by username"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user


def get_user_by_id(user_id):
    """Get user by ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user


def update_user_password(user_id, new_password):
    """Update user password"""
    conn = get_db()
    cursor = conn.cursor()
    
    hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode('utf-8')
    
    cursor.execute(
        "UPDATE users SET password=? WHERE id=?",
        (hashed_password, user_id)
    )
    conn.commit()
    conn.close()
    return True


def update_user_email(user_id, email):
    """Update user email"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET email=? WHERE id=?",
        (email, user_id)
    )
    conn.commit()
    conn.close()
    return True


def get_all_users():
    """Get all users"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
    users = cursor.fetchall()
    conn.close()
    return users


def get_users_by_role(role):
    """Get users by role"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE role=?", (role,))
    users = cursor.fetchall()
    conn.close()
    return users


def get_faculty_count():
    """Get count of faculty members"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE role='faculty'")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def delete_user(user_id):
    """Delete a user"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    return True


def create_access_request(username, password, email, role):
    """Create a new access request"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')
    
    cursor.execute(
        "INSERT INTO access_requests (username, password, email, role, status) VALUES (?, ?, ?, ?, 'pending')",
        (username, hashed_password, email, role)
    )
    conn.commit()
    conn.close()
    return True


def get_access_requests(status=None):
    """Get access requests"""
    conn = get_db()
    cursor = conn.cursor()
    if status:
        cursor.execute("SELECT * FROM access_requests WHERE status=? ORDER BY created_at DESC", (status,))
    else:
        cursor.execute("SELECT * FROM access_requests ORDER BY created_at DESC")
    requests = cursor.fetchall()
    conn.close()
    return requests


def get_access_request_by_id(request_id):
    """Get access request by ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM access_requests WHERE id=?", (request_id,))
    request = cursor.fetchone()
    conn.close()
    return request


def update_access_request_status(request_id, status):
    """Update access request status"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE access_requests SET status=? WHERE id=?",
        (status, request_id)
    )
    conn.commit()
    conn.close()
    return True


def get_pending_requests_count():
    """Get count of pending requests"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM access_requests WHERE status='pending'")
    count = cursor.fetchone()[0]
    conn.close()
    return count

