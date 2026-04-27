"""
Student Model - Handles all student-related database operations
"""
import sqlite3
from datetime import datetime

DB_NAME = 'database.db'


def get_db():
    """Get database connection"""
    return sqlite3.connect(DB_NAME)


def get_all_students(search=None, course_filter=None, year_filter=None, page=1, per_page=10):
    """
    Get all students with optional search, filter, and pagination
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # Build query with filters
    query = "SELECT * FROM students WHERE 1=1"
    params = []
    
    if search:
        query += " AND (name LIKE ? OR enrollment_number LIKE ? OR email LIKE ? OR course LIKE ?)"
        search_param = f"%{search}%"
        params.extend([search_param, search_param, search_param, search_param])
    
    if course_filter:
        query += " AND course = ?"
        params.append(course_filter)
    
    if year_filter:
        query += " AND year = ?"
        params.append(year_filter)
    
    # Get total count for pagination
    count_query = query.replace("SELECT *", "SELECT COUNT(*) as count")
    cursor.execute(count_query, params)
    total_count = cursor.fetchone()[0]
    
    # Add ordering and pagination
    query += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([per_page, (page - 1) * per_page])
    
    cursor.execute(query, params)
    students = cursor.fetchall()
    conn.close()
    
    return students, total_count


def get_student_by_id(student_id):
    """Get student by ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE id=?", (student_id,))
    student = cursor.fetchone()
    conn.close()
    return student


def get_student_by_enrollment(enrollment_number):
    """Get student by enrollment number"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE enrollment_number=?", (enrollment_number,))
    student = cursor.fetchone()
    conn.close()
    return student


def get_student_by_email(email):
    """Get student by email"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE email=?", (email,))
    student = cursor.fetchone()
    conn.close()
    return student


def create_student(name, email, enrollment_number, course, year, phone=None, address=None):
    """Create a new student"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        """INSERT INTO students 
           (name, email, enrollment_number, course, year, phone, address, created_at, updated_at) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (name, email, enrollment_number, course, year, phone, address, 
         datetime.now(), datetime.now())
    )
    
    student_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return student_id


def update_student(student_id, name, email, enrollment_number, course, year, phone=None, address=None):
    """Update student information"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        """UPDATE students 
           SET name=?, email=?, enrollment_number=?, course=?, year=?, 
               phone=?, address=?, updated_at=? 
           WHERE id=?""",
        (name, email, enrollment_number, course, year, phone, address,
         datetime.now(), student_id)
    )
    
    conn.commit()
    conn.close()
    return True


def delete_student(student_id):
    """Delete a student"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id=?", (student_id,))
    conn.commit()
    conn.close()
    return True


def get_student_count():
    """Get total number of students"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM students")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_all_courses():
    """Get all unique courses"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT course FROM students ORDER BY course")
    courses = [row[0] for row in cursor.fetchall()]
    conn.close()
    return courses


def get_students_for_export(search=None, course_filter=None, year_filter=None):
    """Get all students for export (no pagination)"""
    conn = get_db()
    cursor = conn.cursor()
    
    query = "SELECT * FROM students WHERE 1=1"
    params = []
    
    if search:
        query += " AND (name LIKE ? OR enrollment_number LIKE ? OR email LIKE ? OR course LIKE ?)"
        search_param = f"%{search}%"
        params.extend([search_param, search_param, search_param, search_param])
    
    if course_filter:
        query += " AND course = ?"
        params.append(course_filter)
    
    if year_filter:
        query += " AND year = ?"
        params.append(year_filter)
    
    query += " ORDER BY id DESC"
    
    cursor.execute(query, params)
    students = cursor.fetchall()
    conn.close()
    
    return students


def search_students(query_text):
    """Quick search for students"""
    conn = get_db()
    cursor = conn.cursor()
    
    search_param = f"%{query_text}%"
    cursor.execute(
        """SELECT id, name, enrollment_number, course, email 
           FROM students 
           WHERE name LIKE ? OR enrollment_number LIKE ? OR email LIKE ? OR course LIKE ?
           LIMIT 10""",
        (search_param, search_param, search_param, search_param)
    )
    students = cursor.fetchall()
    conn.close()
    return students

