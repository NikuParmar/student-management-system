"""
Activity Model - Handles all activity logging database operations
"""
import sqlite3
from datetime import datetime

DB_NAME = 'database.db'


def get_db():
    """Get database connection"""
    return sqlite3.connect(DB_NAME)


def init_activity_log():
    """Initialize activity log table"""
    conn = get_db()
    cursor = conn.cursor()
    
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
    
    conn.commit()
    conn.close()


def log_activity(user_id, username, action, details=None, ip_address=None):
    """Log an activity"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        """INSERT INTO activity_logs (user_id, username, action, details, ip_address) 
           VALUES (?, ?, ?, ?, ?)""",
        (user_id, username, action, details, ip_address)
    )
    
    conn.commit()
    conn.close()
    return True


def get_all_activities(limit=100):
    """Get all activities"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM activity_logs ORDER BY created_at DESC LIMIT ?", (limit,))
    activities = cursor.fetchall()
    conn.close()
    return activities


def get_activities_by_user(username, limit=50):
    """Get activities by username"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM activity_logs WHERE username=? ORDER BY created_at DESC LIMIT ?",
        (username, limit)
    )
    activities = cursor.fetchall()
    conn.close()
    return activities


def get_recent_activities(days=7, limit=50):
    """Get recent activities"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Calculate date from days ago
    from datetime import timedelta
    date_from = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    cursor.execute(
        "SELECT * FROM activity_logs WHERE created_at >= ? ORDER BY created_at DESC LIMIT ?",
        (date_from, limit)
    )
    activities = cursor.fetchall()
    conn.close()
    return activities


def get_activity_count_today():
    """Get count of activities today"""
    conn = get_db()
    cursor = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute(
        "SELECT COUNT(*) FROM activity_logs WHERE created_at LIKE ?",
        (f"{today}%",)
    )
    count = cursor.fetchone()[0]
    conn.close()
    return count


def clear_old_logs(days=90):
    """Clear logs older than specified days"""
    conn = get_db()
    cursor = conn.cursor()
    
    from datetime import timedelta
    date_from = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    cursor.execute("DELETE FROM activity_logs WHERE created_at < ?", (date_from,))
    
    conn.commit()
    conn.close()
    return True


# Predefined action types
class Actions:
    LOGIN = "login"
    LOGOUT = "logout"
    REGISTER = "register"
    ADD_STUDENT = "add_student"
    EDIT_STUDENT = "edit_student"
    DELETE_STUDENT = "delete_student"
    VIEW_STUDENT = "view_student"
    SEARCH_STUDENT = "search_student"
    EXPORT_DATA = "export_data"
    APPROVE_REQUEST = "approve_request"
    DENY_REQUEST = "deny_request"
    UPDATE_FEATURE_REQUEST = "update_feature_request"
    CHANGE_PASSWORD = "change_password"
    UPDATE_PROFILE = "update_profile"

