"""
Feature Request Routes - Handle feature requests from users
"""
from flask import Blueprint, render_template, request, redirect, session, flash
from models.activity_model import log_activity, Actions
import sqlite3

feature_bp = Blueprint('features', __name__)

DB_NAME = 'database.db'


def get_db():
    """Get database connection"""
    return sqlite3.connect(DB_NAME)


def login_required(f):
    """Decorator to require login"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function


def update_session_activity():
    """Update the last activity timestamp"""
    from time import time
    session['last_activity'] = time()


@feature_bp.route('/feature-request', methods=['GET', 'POST'])
@login_required
def submit_feature_request():
    """Submit a feature request"""
    update_session_activity()
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        request_type = request.form.get('request_type', '').strip()
        
        if not title or not description or not request_type:
            return render_template('feature_request.html', 
                error='Please fill in all fields', 
                form_data=request.form)
        
        # Get user's role
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE username=?", (session['user'],))
        user_result = cursor.fetchone()
        user_role = user_result[0] if user_result else 'unknown'
        
        # Insert feature request
        cursor.execute(
            """INSERT INTO feature_requests 
               (title, description, request_type, user_role, status, created_by) 
               VALUES (?, ?, ?, ?, 'pending', ?)""",
            (title, description, request_type, user_role, session['user'])
        )
        conn.commit()
        conn.close()
        
        flash('Feature request submitted successfully!', 'success')
        return redirect('/feature-request')
    
    return render_template('feature_request.html')


@feature_bp.route('/my-feature-requests')
@login_required
def my_feature_requests():
    """View user's own feature requests"""
    update_session_activity()
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM feature_requests WHERE created_by=? ORDER BY created_at DESC",
        (session['user'],)
    )
    requests = cursor.fetchall()
    conn.close()
    
    return render_template('my_feature_requests.html', requests=requests)


@feature_bp.route('/feature-request/delete/<int:request_id>')
@login_required
def delete_feature_request(request_id):
    """Delete a feature request (only by owner or admin)"""
    update_session_activity()
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if request exists and user is owner or admin
    cursor.execute("SELECT created_by FROM feature_requests WHERE id=?", (request_id,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        flash('Feature request not found.', 'danger')
        return redirect('/my-feature-requests')
    
    if result[0] != session['user'] and session.get('role') != 'admin':
        conn.close()
        flash('You do not have permission to delete this request.', 'danger')
        return redirect('/my-feature-requests')
    
    # Delete the request
    cursor.execute("DELETE FROM feature_requests WHERE id=?", (request_id,))
    conn.commit()
    conn.close()
    
    flash('Feature request deleted successfully!', 'success')
    return redirect('/my-feature-requests')

