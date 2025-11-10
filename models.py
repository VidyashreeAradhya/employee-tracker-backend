from app import db       # import db instance from app.py
from datetime import datetime, date  # to handle date fields
import re                # to use regular expressions for validations

# -------------------------------
# Department Model
# -------------------------------
class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=True)

    # New unique department code (4 alphanumeric)
    dept_code = db.Column(db.String(4), unique=True, nullable=False)

    # One-to-Many relationship with Employees
    employees = db.relationship('Employee', backref='department', lazy=True)

    # One-to-Many relationship with Projects
    projects = db.relationship('Project', backref='department', lazy=True)

    # Validation for department code
    @staticmethod
    def is_valid_dept_code(code):
        """
        Validate dept_code is exactly 4 alphanumeric characters.
        Example: IT01, HR02, D123
        """
        return bool(re.fullmatch(r'[A-Za-z0-9]{4}', code))

    def __repr__(self):
        return f"<Department {self.name} ({self.dept_code})>"


# -------------------------------
# Employee Model
# -------------------------------
class Employee(db.Model):
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    salary = db.Column(db.Float)
    join_date = db.Column(db.Date, nullable=False, default=date.today)

    # Foreign Key to Department
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))

    # -------------------------------
    # Validations
    # -------------------------------
    @staticmethod
    def is_valid_name(name):
        """Validate name contains only alphabets and spaces."""
        return bool(re.fullmatch(r"[A-Za-z ]+", name))

    @staticmethod
    def is_valid_email(email):
        """Validate email format and must end with .com."""
        return email.endswith(".com") and re.match(r"^[\w\.-]+@[\w\.-]+$", email)

    @staticmethod
    def parse_join_date(date_str):
        """Convert 'yyyy-mm-dd' format to date and ensure not future."""
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d").date()
            if dt > date.today():
                return None
            return dt
        except ValueError:
            return None

    def __repr__(self):
        return f"<Employee {self.name}>"


# -------------------------------
# Association Table (Employee <-> Project)
# -------------------------------
employee_project = db.Table(
    'employee_project',
    db.Column('employee_id', db.Integer, db.ForeignKey('employees.id'), primary_key=True),
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True)
)


# -------------------------------
# Project Model
# -------------------------------
class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)

    # New unique project code (5 alphanumeric)
    project_code = db.Column(db.String(5), unique=True, nullable=False)

    # Foreign key: each project belongs to one department
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)

    # Many-to-Many relationship with Employees
    employees = db.relationship('Employee', secondary=employee_project, backref='projects', lazy='dynamic')

    # Validation for project code
    @staticmethod
    def is_valid_project_code(code):
        """
        Validate project_code is exactly 5 alphanumeric characters.
        Example: P1234, DEV01, A1B2C
        """
        return bool(re.fullmatch(r'[A-Za-z0-9]{5}', code))

    @staticmethod
    def parse_project_date(date_str):
        """Convert 'yyyy-mm-dd' format to datetime.date"""
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return None

    def __repr__(self):
        return f"<Project {self.title} ({self.project_code})>"
