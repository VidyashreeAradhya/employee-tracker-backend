from extensions import db
from datetime import datetime, date
import re
import random, string

# -------------------------------
# Department Model
# -------------------------------
class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=True)
    dept_code = db.Column(
        db.String(4),
        unique=True,
        nullable=False,
        default=lambda: ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    )

    employees = db.relationship('Employee', backref='department', lazy=True)

    @staticmethod
    def is_valid_dept_code(code):
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
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))

    @staticmethod
    def is_valid_name(name):
        return bool(re.fullmatch(r"[A-Za-z ]+", name))

    @staticmethod
    def is_valid_email(email):
        return email.endswith(".com") and re.match(r"^[\w\.-]+@[\w\.-]+$", email)

    @staticmethod
    def parse_join_date(date_str):
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
# Association Table
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
    project_code = db.Column(
        db.String(5),
        unique=True,
        nullable=False,
        default=lambda: ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    )

    employees = db.relationship('Employee', secondary=employee_project, backref='projects', lazy='dynamic')

    @staticmethod
    def is_valid_project_code(code):
        return bool(re.fullmatch(r'[A-Za-z0-9]{5}', code))

    @staticmethod
    def parse_project_date(date_str):
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return None

    def __repr__(self):
        return f"<Project {self.title} ({self.project_code})>"
