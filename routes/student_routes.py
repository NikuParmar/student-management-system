"""
Student Routes - Handle student CRUD, search, pagination, and export
"""
from flask import Blueprint, render_template, request, redirect, session, send_file, flash
from models import student_model
from models.activity_model import log_activity, Actions
import pandas as pd
import xlsxwriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
from datetime import datetime

student_bp = Blueprint('students', __name__)

# Pagination settings
STUDENTS_PER_PAGE = 10


def login_required(role=None):
    """Decorator to require login and optionally check role"""
    from functools import wraps
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session:
                return redirect('/')
            if role and session.get('role') != role:
                flash('You do not have permission to access this page.', 'danger')
                return redirect('/admin')
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def update_session_activity():
    """Update the last activity timestamp"""
    from time import time
    session['last_activity'] = time()


@student_bp.route('/students')
def list_students():
    """List all students with search, filter, and pagination"""
    if 'user' not in session:
        return redirect('/')
    
    update_session_activity()
    
    # Get query parameters
    search = request.args.get('search', '').strip()
    course_filter = request.args.get('course', '').strip()
    year_filter = request.args.get('year', '').strip()
    page = int(request.args.get('page', 1))
    
    # Convert year_filter to int if provided
    if year_filter:
        try:
            year_filter = int(year_filter)
        except ValueError:
            year_filter = None
    
    # Get students with pagination
    students, total_count = student_model.get_all_students(
        search=search,
        course_filter=course_filter if course_filter else None,
        year_filter=year_filter,
        page=page,
        per_page=STUDENTS_PER_PAGE
    )
    
    # Calculate pagination values
    total_pages = (total_count + STUDENTS_PER_PAGE - 1) // STUDENTS_PER_PAGE
    has_prev = page > 1
    has_next = page < total_pages
    
    # Calculate start and end for display
    start_num = (page - 1) * STUDENTS_PER_PAGE + 1
    end_num = min(page * STUDENTS_PER_PAGE, total_count)
    
    # Get all courses for filter dropdown
    all_courses = student_model.get_all_courses()
    
    # Log search activity
    if search:
        log_activity(
            session.get('user_id'), 
            session.get('user'), 
            Actions.SEARCH_STUDENT, 
            f"Searched for: {search}"
        )
    
    return render_template('students/list.html',
                         students=students,
                         search=search,
                         course_filter=course_filter,
                         year_filter=year_filter,
                         all_courses=all_courses,
                         page=page,
                         total_pages=total_pages,
                         total_count=total_count,
                         has_prev=has_prev,
                         has_next=has_next,
                         start_num=start_num,
                         end_num=end_num)


@student_bp.route('/students/add', methods=['GET', 'POST'])
def add_student():
    """Add a new student"""
    if 'user' not in session:
        return redirect('/')
    
    if session.get('role') not in ['admin', 'faculty']:
        flash('You do not have permission to add students.', 'danger')
        return redirect('/students')
    
    update_session_activity()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        enrollment_number = request.form.get('enrollment_number', '').strip()
        course = request.form.get('course', '').strip()
        year = request.form.get('year', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        
        # Validation
        errors = []
        if not name:
            errors.append('Name is required')
        if not email:
            errors.append('Email is required')
        if not enrollment_number:
            errors.append('Enrollment number is required')
        if not course:
            errors.append('Course is required')
        if not year:
            errors.append('Year is required')
        
        # Check if enrollment number already exists
        if student_model.get_student_by_enrollment(enrollment_number):
            errors.append('Enrollment number already exists')
        
        # Check if email already exists
        if student_model.get_student_by_email(email):
            errors.append('Email already exists')
        
        if errors:
            return render_template('students/add.html', errors=errors, form_data=request.form)
        
        # Create student
        student_id = student_model.create_student(
            name=name,
            email=email,
            enrollment_number=enrollment_number,
            course=course,
            year=int(year),
            phone=phone,
            address=address
        )
        
        # Log activity
        log_activity(
            session.get('user_id'),
            session.get('user'),
            Actions.ADD_STUDENT,
            f"Added student: {name} (ID: {student_id})"
        )
        
        flash('Student added successfully!', 'success')
        return redirect('/students')
    
    return render_template('students/add.html')


@student_bp.route('/students/edit/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    """Edit an existing student"""
    if 'user' not in session:
        return redirect('/')
    
    if session.get('role') not in ['admin', 'faculty']:
        flash('You do not have permission to edit students.', 'danger')
        return redirect('/students')
    
    update_session_activity()
    
    student = student_model.get_student_by_id(student_id)
    if not student:
        flash('Student not found.', 'danger')
        return redirect('/students')
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        enrollment_number = request.form.get('enrollment_number', '').strip()
        course = request.form.get('course', '').strip()
        year = request.form.get('year', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        
        # Validation
        errors = []
        if not name:
            errors.append('Name is required')
        if not email:
            errors.append('Email is required')
        if not enrollment_number:
            errors.append('Enrollment number is required')
        if not course:
            errors.append('Course is required')
        if not year:
            errors.append('Year is required')
        
        # Check if enrollment number exists for another student
        existing = student_model.get_student_by_enrollment(enrollment_number)
        if existing and existing[0] != student_id:
            errors.append('Enrollment number already exists for another student')
        
        # Check if email exists for another student
        existing = student_model.get_student_by_email(email)
        if existing and existing[0] != student_id:
            errors.append('Email already exists for another student')
        
        if errors:
            return render_template('students/edit.html', student=student, errors=errors, form_data=request.form)
        
        # Update student
        student_model.update_student(
            student_id=student_id,
            name=name,
            email=email,
            enrollment_number=enrollment_number,
            course=course,
            year=int(year),
            phone=phone,
            address=address
        )
        
        # Log activity
        log_activity(
            session.get('user_id'),
            session.get('user'),
            Actions.EDIT_STUDENT,
            f"Edited student: {name} (ID: {student_id})"
        )
        
        flash('Student updated successfully!', 'success')
        return redirect('/students')
    
    return render_template('students/edit.html', student=student)


@student_bp.route('/students/delete/<int:student_id>')
def delete_student(student_id):
    """Delete a student"""
    if 'user' not in session:
        return redirect('/')
    
    if session.get('role') != 'admin':
        flash('Only administrators can delete students.', 'danger')
        return redirect('/students')
    
    update_session_activity()
    
    student = student_model.get_student_by_id(student_id)
    if not student:
        flash('Student not found.', 'danger')
        return redirect('/students')
    
    # Get student name for logging
    student_name = student[1]
    
    # Delete student
    student_model.delete_student(student_id)
    
    # Log activity
    log_activity(
        session.get('user_id'),
        session.get('user'),
        Actions.DELETE_STUDENT,
        f"Deleted student: {student_name} (ID: {student_id})"
    )
    
    flash('Student deleted successfully!', 'success')
    return redirect('/students')


@student_bp.route('/students/<int:student_id>')
def view_student(student_id):
    """View student details"""
    if 'user' not in session:
        return redirect('/')
    
    update_session_activity()
    
    student = student_model.get_student_by_id(student_id)
    if not student:
        flash('Student not found.', 'danger')
        return redirect('/students')
    
    # Log activity
    log_activity(
        session.get('user_id'),
        session.get('user'),
        Actions.VIEW_STUDENT,
        f"Viewed student: {student[1]} (ID: {student_id})"
    )
    
    return render_template('students/view.html', student=student)


# Export Routes
@student_bp.route('/students/export/csv')
def export_csv():
    """Export students to CSV"""
    if 'user' not in session:
        return redirect('/')
    
    update_session_activity()
    
    # Get all students (without pagination)
    search = request.args.get('search', '').strip()
    course_filter = request.args.get('course', '').strip()
    year_filter = request.args.get('year', '').strip()
    
    if year_filter:
        try:
            year_filter = int(year_filter)
        except ValueError:
            year_filter = None
    
    students = student_model.get_students_for_export(
        search=search if search else None,
        course_filter=course_filter if course_filter else None,
        year_filter=year_filter
    )
    
    # Create CSV
    df = pd.DataFrame(students, columns=[
        'ID', 'Name', 'Email', 'Enrollment Number', 'Course', 'Year', 
        'Phone', 'Address', 'Created At', 'Updated At'
    ])
    
    # Log activity
    log_activity(
        session.get('user_id'),
        session.get('user'),
        Actions.EXPORT_DATA,
        f"Exported {len(students)} students to CSV"
    )
    
    # Save to buffer
    buffer = io.BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    
    return send_file(
        buffer,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'students_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )


@student_bp.route('/students/export/excel')
def export_excel():
    """Export students to Excel"""
    if 'user' not in session:
        return redirect('/')
    
    update_session_activity()
    
    # Get all students
    search = request.args.get('search', '').strip()
    course_filter = request.args.get('course', '').strip()
    year_filter = request.args.get('year', '').strip()
    
    if year_filter:
        try:
            year_filter = int(year_filter)
        except ValueError:
            year_filter = None
    
    students = student_model.get_students_for_export(
        search=search if search else None,
        course_filter=course_filter if course_filter else None,
        year_filter=year_filter
    )
    
    # Create Excel
    df = pd.DataFrame(students, columns=[
        'ID', 'Name', 'Email', 'Enrollment Number', 'Course', 'Year', 
        'Phone', 'Address', 'Created At', 'Updated At'
    ])
    
    # Log activity
    log_activity(
        session.get('user_id'),
        session.get('user'),
        Actions.EXPORT_DATA,
        f"Exported {len(students)} students to Excel"
    )
    
    # Save to buffer
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Students')
    
    buffer.seek(0)
    
    return send_file(
        buffer,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'students_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    )


@student_bp.route('/students/export/pdf')
def export_pdf():
    """Export students to PDF"""
    if 'user' not in session:
        return redirect('/')
    
    update_session_activity()
    
    # Get all students
    search = request.args.get('search', '').strip()
    course_filter = request.args.get('course', '').strip()
    year_filter = request.args.get('year', '').strip()
    
    if year_filter:
        try:
            year_filter = int(year_filter)
        except ValueError:
            year_filter = None
    
    students = student_model.get_students_for_export(
        search=search if search else None,
        course_filter=course_filter if course_filter else None,
        year_filter=year_filter
    )
    
    # Log activity
    log_activity(
        session.get('user_id'),
        session.get('user'),
        Actions.EXPORT_DATA,
        f"Exported {len(students)} students to PDF"
    )
    
    # Create PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, "Student List Export")
    
    # Date
    p.setFont("Helvetica", 10)
    p.drawString(50, height - 70, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Table header
    p.setFont("Helvetica-Bold", 8)
    y = height - 100
    headers = ['ID', 'Name', 'Enrollment', 'Course', 'Year', 'Email']
    col_widths = [30, 80, 80, 60, 30, 100]
    x = 50
    
    for header, col_width in zip(headers, col_widths):
        p.drawString(x, y, header)
        x += col_width
    
    # Table rows
    p.setFont("Helvetica", 7)
    y -= 15
    
    for student in students[:50]:  # Limit to 50 per page
        if y < 50:  # New page if needed
            p.showPage()
            p.setFont("Helvetica-Bold", 8)
            y = height - 50
            for header, col_width in zip(headers, col_widths):
                p.drawString(x, y, header)
                x += col_width
            p.setFont("Helvetica", 7)
            y -= 15
        
        x = 50
        p.drawString(x, y, str(student[0]))  # ID
        x += 30
        p.drawString(x, y, student[1][:20] if student[1] else '')  # Name
        x += 80
        p.drawString(x, y, student[3][:15] if student[3] else '')  # Enrollment
        x += 80
        p.drawString(x, y, student[4][:15] if student[4] else '')  # Course
        x += 60
        p.drawString(x, y, str(student[5]) if student[5] else '')  # Year
        x += 30
        p.drawString(x, y, student[2][:25] if student[2] else '')  # Email
        y -= 15
    
    p.save()
    buffer.seek(0)
    
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'students_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    )


@student_bp.route('/api/students/search')
def api_search_students():
    """API endpoint for quick search"""
    if 'user' not in session:
        return {'error': 'Unauthorized'}, 401
    
    query = request.args.get('q', '').strip()
    if not query:
        return {'students': []}
    
    students = student_model.search_students(query)
    
    # Format results
    results = []
    for s in students:
        results.append({
            'id': s[0],
            'name': s[1],
            'enrollment_number': s[2],
            'course': s[3],
            'email': s[4]
        })
    
    return {'students': results}

