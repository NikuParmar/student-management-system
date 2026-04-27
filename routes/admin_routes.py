"""
Admin Routes - Handle admin dashboard, access requests, feature requests, and activity logs
"""
from flask import Blueprint, render_template, request, redirect, session, flash
from models import user_model
from models import student_model
from models.activity_model import log_activity, Actions, get_all_activities, get_activities_by_user
import sqlite3

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Decorator to require admin role"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect('/')
        if session.get('role') != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect('/dashboard')
        return f(*args, **kwargs)
    return decorated_function


def update_session_activity():
    """Update the last activity timestamp"""
    from time import time
    session['last_activity'] = time()


@admin_bp.route('/admin')
@admin_bp.route('/admin/dashboard')
@admin_required
def dashboard():
    """Admin dashboard with statistics"""
    update_session_activity()
    
    # Get statistics
    total_students = student_model.get_student_count()
    total_faculty = user_model.get_faculty_count()
    pending_requests = user_model.get_pending_requests_count()
    
    # Get feature requests count
    conn = user_model.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM feature_requests WHERE status='pending'")
    feature_requests_count = cursor.fetchone()[0]
    conn.close()
    
    # Get recent activities
    recent_activities = get_all_activities(limit=10)
    
    return render_template('admin_dashboard.html',
                         total_students=total_students,
                         total_faculty=total_faculty,
                         pending_requests=pending_requests,
                         feature_requests_count=feature_requests_count,
                         recent_activities=recent_activities)


@admin_bp.route('/admin/requests')
@admin_required
def access_requests():
    """View all access requests"""
    update_session_activity()
    
    status_filter = request.args.get('status', '')
    
    # Get pending requests count for sidebar badge
    pending_requests = user_model.get_pending_requests_count()
    
    if status_filter:
        requests = user_model.get_access_requests(status=status_filter)
    else:
        requests = user_model.get_access_requests()
    
    return render_template('access_requests.html', requests=requests, status_filter=status_filter, pending_requests=pending_requests)


@admin_bp.route('/admin/approve/<int:request_id>')
@admin_required
def approve_request(request_id):
    """Approve an access request"""
    update_session_activity()
    
    # Get the request details
    request_user = user_model.get_access_request_by_id(request_id)
    
    if request_user:
        # request_user: (id, username, password, email, role, status, created_at)
        requested_role = request_user[4] if request_user[4] else 'student'
        
        # Create user in users table
        user_model.create_user(
            username=request_user[1],
            password=request_user[2],  # Will be hashed in create_user
            role=requested_role,
            email=request_user[3]
        )
        
        # Update request status
        user_model.update_access_request_status(request_id, 'approved')
        
        # Log activity
        log_activity(
            session.get('user_id'),
            session.get('user'),
            Actions.APPROVE_REQUEST,
            f"Approved access request for: {request_user[1]} (Role: {requested_role})"
        )
        
        flash(f'Access request for {request_user[1]} approved!', 'success')
    else:
        flash('Request not found.', 'danger')
    
    return redirect('/admin/requests')


@admin_bp.route('/admin/deny/<int:request_id>')
@admin_required
def deny_request(request_id):
    """Deny an access request"""
    update_session_activity()
    
    request_user = user_model.get_access_request_by_id(request_id)
    
    # Update request status
    user_model.update_access_request_status(request_id, 'denied')
    
    # Log activity
    if request_user:
        log_activity(
            session.get('user_id'),
            session.get('user'),
            Actions.DENY_REQUEST,
            f"Denied access request for: {request_user[1]}"
        )
        flash(f'Access request for {request_user[1]} denied.', 'warning')
    else:
        flash('Request not found.', 'danger')
    
    return redirect('/admin/requests')


@admin_bp.route('/admin/feature-requests')
@admin_required
def feature_requests():
    """View all feature requests"""
    update_session_activity()
    
    # Get pending requests count for sidebar badge
    pending_requests = user_model.get_pending_requests_count()
    
    conn = user_model.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM feature_requests ORDER BY created_at DESC")
    requests = cursor.fetchall()
    conn.close()
    
    return render_template('admin_feature_requests.html', requests=requests, pending_requests=pending_requests)


@admin_bp.route('/admin/feature-request/update/<int:request_id>', methods=['POST'])
@admin_required
def update_feature_request(request_id):
    """Update feature request status"""
    update_session_activity()
    
    new_status = request.form.get('status')
    
    conn = user_model.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT title FROM feature_requests WHERE id=?", (request_id,))
    result = cursor.fetchone()
    
    if result:
        cursor.execute("UPDATE feature_requests SET status=? WHERE id=?", (new_status, request_id))
        conn.commit()
        
        # Log activity
        log_activity(
            session.get('user_id'),
            session.get('user'),
            Actions.UPDATE_FEATURE_REQUEST,
            f"Updated feature request: {result[0]} - Status: {new_status}"
        )
        
        flash(f'Feature request updated to {new_status}!', 'success')
    else:
        flash('Feature request not found.', 'danger')
    
    conn.close()
    return redirect('/admin/feature-requests')


@admin_bp.route('/admin/activity-logs')
@admin_required
def activity_logs():
    """View activity logs"""
    update_session_activity()
    
    # Get pending requests count for sidebar badge
    pending_requests = user_model.get_pending_requests_count()
    
    # Get filter parameters
    username_filter = request.args.get('username', '')
    limit = int(request.args.get('limit', 100))
    
    if username_filter:
        activities = get_activities_by_user(username_filter, limit=limit)
    else:
        activities = get_all_activities(limit=limit)
    
    return render_template('activity_logs.html', activities=activities, username_filter=username_filter, pending_requests=pending_requests)


@admin_bp.route('/admin/users')
@admin_required
def manage_users():
    """Manage users"""
    update_session_activity()
    
    # Get pending requests count for sidebar badge
    pending_requests = user_model.get_pending_requests_count()
    
    role_filter = request.args.get('role', '')
    
    if role_filter:
        users = user_model.get_users_by_role(role_filter)
    else:
        users = user_model.get_all_users()
    
    return render_template('admin_users.html', users=users, role_filter=role_filter, pending_requests=pending_requests)


@admin_bp.route('/admin/user/delete/<int:user_id>')
@admin_required
def delete_user(user_id):
    """Delete a user"""
    update_session_activity()
    
    # Prevent deleting self
    if user_id == session.get('user_id'):
        flash('You cannot delete your own account.', 'danger')
        return redirect('/admin/users')
    
    user = user_model.get_user_by_id(user_id)
    if user:
        user_model.delete_user(user_id)
        
        # Log activity
        log_activity(
            session.get('user_id'),
            session.get('user'),
            "delete_user",
            f"Deleted user: {user[1]} (ID: {user_id})"
        )
        
        flash(f'User {user[1]} deleted successfully!', 'success')
    else:
        flash('User not found.', 'danger')
    
    return redirect('/admin/users')

