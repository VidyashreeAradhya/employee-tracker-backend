from app import db
from datetime import datetime, date
import re

# -------------------------------
# Department Model
# -------------------------------
class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=True)  # New column

    # One-to-Many relationship
    employees = db.relationship('Employee', backref='department', lazy=True)

    def __repr__(self):
        return f"<Department {self.name}>"


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
        return bool(re.fullmatch(r"[A-Za-z ]+", name))

    @staticmethod
    def is_valid_email(email):
        return email.endswith(".com") and re.match(r"^[\w\.-]+@[\w\.-]+$", email)

    @staticmethod
    def parse_join_date(date_str):
        """
        Convert string in 'yy-mm-dd' format to datetime.date
        """
        try:
            # Convert yy-mm-dd → full year if needed
            dt = datetime.strptime(date_str, "%y-%m-%d").date()
            if dt > date.today():
                return None  # join_date cannot be in the future
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

    # Foreign key: each project belongs to one department
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)

    # Relationship with Department (One Department → Many Projects)
    department = db.relationship('Department', backref='projects', lazy=True)

    # Many-to-Many relationship with Employees
    employees = db.relationship('Employee', secondary=employee_project, backref='projects', lazy='dynamic')

    def __repr__(self):
        return f"<Project {self.title}>"
