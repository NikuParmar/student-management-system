"""
Authentication Routes - Handle login, register, logout, and session management
"""
from flask import Blueprint, render_template, request, redirect, session, flash
from models import user_model
from models.activity_model import log_activity, Actions

auth_bp = Blueprint('auth', __name__)

# Session timeout in seconds (30 minutes)
SESSION_TIMEOUT = 30 * 60


def is_session_valid():
    """Check if session is still valid based on timeout"""
    if 'last_activity' in session:
        from time import time
        elapsed = time() - session['last_activity']
        return elapsed < SESSION_TIMEOUT
    return False


def update_session_activity():
    """Update the last activity timestamp"""
    from time import time
    session['last_activity'] = time()


def login_required(role=None):
    """Decorator to require login and optionally check role"""
    from functools import wraps
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session:
                return redirect('/')
            
            if not is_session_valid():
                session.clear()
                flash('Session expired. Please login again.', 'warning')
                return redirect('/')
            
            if role and session.get('role') != role:
                flash('You do not have permission to access this page.', 'danger')
                return redirect('/admin')
            
            update_session_activity()
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@auth_bp.route('/', methods=['GET', 'POST'])
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            return render_template('login.html', error='Please enter username and password')

        # Try to verify user
        user = user_model.verify_user(username, password)
        
        if user:
            # user: (id, username, password, role, email, created_at)
            session['user'] = user[1]
            session['role'] = user[3]
            session['user_id'] = user[0]
            session['email'] = user[4] if len(user) > 4 else None
            update_session_activity()
            
            # Log the login activity
            log_activity(user[0], user[1], Actions.LOGIN, f"User logged in")
            
            # Redirect based on role
            if user[3] == 'admin':
                return redirect('/admin')
            else:
                return redirect('/dashboard')
        else:
            # Check if user has a pending/denied request
            conn = user_model.get_db()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM access_requests WHERE username=?",
                (username,)
            )
            request_user = cursor.fetchone()
            conn.close()
            
            if request_user:
                status = request_user[4]
                if status == 'pending':
                    return render_template('login.html', 
                        error='Your access request is still pending. Please wait for admin approval.')
                elif status == 'denied':
                    return render_template('login.html', 
                        error='Your access request has been denied. Please contact the admin.')
            
            return render_template('login.html', error='Invalid credentials or user does not exist.')

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration / access request"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        email = request.form.get('email', '').strip()
        role = request.form.get('role', 'student')

        if not username or not password or not email:
            return render_template('register.html', error='Please fill in all fields')

        # Check if username already exists in users
        existing_user = user_model.get_user_by_username(username)
        if existing_user:
            return render_template('register.html', error='Username already exists')

        # Check if username already has a request
        conn = user_model.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM access_requests WHERE username=?", (username,))
        if cursor.fetchone():
            conn.close()
            return render_template('register.html', 
                error='You already have a pending request. Please wait for approval.')

        # Create new access request
        user_model.create_access_request(username, password, email, role)
        
        # Log the registration
        log_activity(None, username, Actions.REGISTER, f"New user registered with role: {role}")
        
        return render_template('register.html', 
            success='Access request submitted successfully! Please wait for admin approval.')

    return render_template('register.html')


@auth_bp.route('/logout')
def logout():
    """User logout"""
    username = session.get('user', 'Unknown')
    user_id = session.get('user_id')
    
    # Log the logout activity
    log_activity(user_id, username, Actions.LOGOUT, f"User logged out")
    
    session.clear()
    return redirect('/')


@auth_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    """User profile page"""
    if 'user' not in session:
        return redirect('/')
    
    update_session_activity()
    user_id = session.get('user_id')
    
    if request.method == 'POST':
        # Update password
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if current_password and new_password:
            # Verify current password
            user = user_model.get_user_by_id(user_id)
            if not bcrypt.checkpw(current_password.encode(), user[2].encode()):
                return render_template('profile.html', error='Current password is incorrect')
            
            if new_password != confirm_password:
                return render_template('profile.html', error='New passwords do not match')
            
            # Update password
            user_model.update_user_password(user_id, new_password)
            log_activity(user_id, session['user'], Actions.CHANGE_PASSWORD, "Password changed")
            
            return render_template('profile.html', success='Password updated successfully')
    
    user = user_model.get_user_by_id(user_id)
    return render_template('profile.html', user=user)


@auth_bp.route('/dashboard')
def dashboard():
    """User dashboard (non-admin)"""
    if 'user' not in session:
        return redirect('/')
    
    if not is_session_valid():
        session.clear()
        return redirect('/')
    
    update_session_activity()
    
    # Redirect admin to admin dashboard
    if session.get('role') == 'admin':
        return redirect('/admin')
    
    return render_template('user_dashboard.html')

