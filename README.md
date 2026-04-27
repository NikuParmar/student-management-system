# Student Management System

A comprehensive full-stack Student Management System built with Flask and SQLite. This system provides complete student data management with a modern Bootstrap 5 UI.

## Features

### 1. CRUD Operations for Students
- **Add Student** - Create new student records with comprehensive details
- **View Students** - Browse all students with detailed information
- **Edit Student** - Update student information
- **Delete Student** - Remove student records (Admin only)
- Full database handling with SQLite

### 2. Search & Filter
- Search by: Name, Enrollment Number, Email, Course
- Filter by Course and Year
- Real-time search capabilities
- Backend SQL LIKE queries for efficient searching

### 3. Pagination
- 10 students per page
- Previous/Next navigation
- Page numbers: 1 | 2 | 3 | ...
- Maintains search/filter state across pages

### 4. Authentication & Security
- **Password Hashing** - SHA256 password encryption
- **Session Management** - 30-minute session timeout
- **Role-Based Access Control** ( - **Admin**RBAC):
  - Full access to all features
  - **Faculty** - Can manage students
  - **Student** - Limited access

### 5. Dashboard Statistics
- Total Students count
- Total Faculty count
- Pending Access Requests
- Feature Requests count

### 6. Export Data
- Export to **CSV**
- Export to **Excel** (.xlsx)
- Export to **PDF**
- Filtered exports supported

### 7. Activity Logging
- Track all admin actions
- Log user activities
- View activity history
- Filter by username

### 8. User Management
- Access request system
- Feature request submission
- User profile management
- Password change functionality

## Tech Stack

- **Backend**: Flask 3.0.0 (Python)
- **Database**: SQLite
- **Frontend**: Bootstrap 5, FontAwesome 6
- **Data Handling**: Pandas, XlsxWriter, ReportLab
- **Authentication**: Flask-Login

## Project Structure

```
student-management-system/
│
├── app.py                      # Main application entry point
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── PLAN.md                     # Implementation plan
├── TODO.md                     # Task tracking
│
├── models/                     # Database models
│   ├── __init__.py
│   ├── user_model.py          # User operations
│   ├── student_model.py       # Student CRUD operations
│   └── activity_model.py     # Activity logging
│
├── routes/                     # Application routes
│   ├── __init__.py
│   ├── auth_routes.py         # Login, register, logout
│   ├── student_routes.py      # Student CRUD, search, export
│   ├── admin_routes.py        # Admin dashboard, requests
│   └── feature_routes.py     # Feature requests
│
├── templates/                  # HTML templates
│   ├── base.html             # Base template with sidebar
│   ├── login.html            # Login page
│   ├── register.html         # Registration page
│   ├── admin_dashboard.html  # Admin dashboard
│   ├── profile.html          # User profile
│   ├── error.html            # Error page
│   │
│   ├── students/
│   │   ├── list.html         # Student list with pagination
│   │   ├── add.html          # Add student form
│   │   ├── edit.html         # Edit student form
│   │   └── view.html         # View student details
│   │
│   ├── access_requests.html
│   ├── admin_feature_requests.html
│   ├── admin_users.html
│   ├── activity_logs.html
│   ├── feature_request.html
│   ├── my_feature_requests.html
│   └── user_dashboard.html
│
└── static/
    └── css/
        └── style.css         # Custom styles
```

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd student-management-system
```

### 2. Create Virtual Environment (Recommended)
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python app.py
```

The server will start at `http://127.0.0.1:5000`

### 5. Login with Default Admin Credentials
- **Username**: `admin`
- **Password**: `admin123`

## Usage Guide

### Admin Features
1. **Dashboard** - View statistics and recent activities
2. **Students** - Manage student records (Add, Edit, Delete, View)
3. **Access Requests** - Approve/Deny user registrations
4. **Feature Requests** - Review and manage feature suggestions
5. **Activity Logs** - View system activity history
6. **Manage Users** - View and delete system users

### Faculty Features
1. **Dashboard** - View personal dashboard
2. **Students** - Add, Edit, View students (no delete)
3. **Feature Requests** - Submit feature suggestions
4. **Profile** - Update password

### Student Features
1. **Dashboard** - View personal dashboard
2. **Feature Requests** - Submit feature suggestions
3. **My Requests** - View own feature requests
4. **Profile** - Update password

## Screenshots

The application features:
- Modern sidebar navigation
- Responsive Bootstrap 5 design
- Dashboard with statistics cards
- Searchable and paginated tables
- Export buttons for data
- Activity logging system

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Redirect to login or dashboard |
| `/login` | GET/POST | User login |
| `/register` | GET/POST | Request access |
| `/logout` | GET | User logout |
| `/admin` | GET | Admin dashboard |
| `/students` | GET | List students |
| `/students/add` | GET/POST | Add student |
| `/students/edit/<id>` | GET/POST | Edit student |
| `/students/delete/<id>` | GET | Delete student |
| `/students/export/csv` | GET | Export to CSV |
| `/students/export/excel` | GET | Export to Excel |
| `/students/export/pdf` | GET | Export to PDF |
| `/profile` | GET/POST | User profile |
| `/activity-logs` | GET | View activity logs |

## Future Improvements

- [ ] Email notifications using Flask-Mail
- [ ] Two-factor authentication
- [ ] RESTful API for mobile apps
- [ ] Data backup/restore functionality
- [ ] Advanced reporting and analytics
- [ ] Multi-language support

## License

This project is for educational purposes.

## Author

Developed as a comprehensive Student Management System demonstration.

## Support

For issues or questions, please open an issue in the repository.

