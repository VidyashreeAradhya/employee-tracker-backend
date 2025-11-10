from flask import Flask, request, jsonify
from sqlalchemy.exc import IntegrityError
from app import app, db
from models import db, Employee, Department, Project, employee_project
from datetime import datetime
import re

# -----------------------------
# Helper Function for Date Parsing
# -----------------------------
def parse_date(date_value, field_name):
    """Parses date in yyyy-mm-dd format only."""
    if not date_value:
        raise ValueError(f"{field_name} is required")
    try:
        return datetime.strptime(date_value, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"Invalid {field_name} format. Use yyyy-mm-dd")

# -----------------------------
# Helper Validation Functions
# -----------------------------
def is_valid_dept_code(code):
    """Validate dept_code: exactly 4 alphanumeric characters"""
    return bool(re.fullmatch(r"[A-Za-z0-9]{4}", code))

def is_valid_project_code(code):
    """Validate project_code: exactly 5 alphanumeric characters"""
    return bool(re.fullmatch(r"[A-Za-z0-9]{5}", code))

# -----------------------------
# EMPLOYEE CRUD ROUTES
# -----------------------------
@app.route('/employees', methods=['POST'])
def create_employee():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    name = data.get('name')
    email = data.get('email')
    salary = data.get('salary')
    join_date = data.get('join_date')
    department_id = data.get('department_id')

    # Validations
    if not name or not Employee.is_valid_name(name):
        return jsonify({"error": "Name must contain only alphabets"}), 400
    if not email or not Employee.is_valid_email(email):
        return jsonify({"error": "Invalid email. Must end with .com"}), 400

    try:
        join_date_obj = parse_date(join_date, "join_date")
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if department_id:
        dept = Department.query.get(department_id)
        if not dept:
            return jsonify({"error": "Department not found"}), 404

    new_employee = Employee(
        name=name,
        email=email,
        salary=salary,
        join_date=join_date_obj,
        department_id=department_id
    )
    try:
        db.session.add(new_employee)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email already exists. Please use a unique email."}), 400

    return jsonify({
        "message": "Employee created successfully",
        "employee": {
            "id": new_employee.id,
            "name": new_employee.name,
            "email": new_employee.email,
            "salary": new_employee.salary,
            "join_date": str(new_employee.join_date),
            "department_id": new_employee.department_id
        }
    }), 201


@app.route('/employees/<int:id>', methods=['PUT'])
def update_employee(id):
    emp = Employee.query.get(id)
    if not emp:
        return jsonify({"error": "Employee not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    name = data.get('name', emp.name)
    email = data.get('email', emp.email)
    salary = data.get('salary', emp.salary)
    join_date = data.get('join_date')
    department_id = data.get('department_id', emp.department_id)

    if not Employee.is_valid_name(name):
        return jsonify({"error": "Name must contain only alphabets"}), 400
    if not Employee.is_valid_email(email):
        return jsonify({"error": "Invalid email. Must end with .com"}), 400

    join_date_obj = emp.join_date
    if join_date:
        try:
            join_date_obj = parse_date(join_date, "join_date")
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    if department_id:
        dept = Department.query.get(department_id)
        if not dept:
            return jsonify({"error": "Department not found"}), 404

    if (name == emp.name and email == emp.email and salary == emp.salary and
        join_date_obj == emp.join_date and department_id == emp.department_id):
        return jsonify({"message": "Same information, nothing to update"}), 400

    emp.name = name
    emp.email = email
    emp.salary = salary
    emp.join_date = join_date_obj
    emp.department_id = department_id

    db.session.commit()
    return jsonify({"message": "Employee updated successfully"}), 200


# -----------------------------
# DEPARTMENT CRUD ROUTES
# -----------------------------
@app.route('/departments', methods=['POST'])
def create_department():
    data = request.get_json()
    name = data.get('name')
    location = data.get('location')
    dept_code = data.get('dept_code')

    if not name:
        return jsonify({"error": "Department name is required"}), 400
    if not dept_code or not is_valid_dept_code(dept_code):
        return jsonify({"error": "Invalid dept_code. Must be 4 alphanumeric characters"}), 400

    new_dept = Department(name=name, location=location, dept_code=dept_code)
    try:
        db.session.add(new_dept)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "dept_code must be unique"}), 400

    return jsonify({"message": "Department created", "id": new_dept.id}), 201


@app.route('/departments/<int:id>', methods=['PUT'])
def update_department(id):
    dept = Department.query.get(id)
    if not dept:
        return jsonify({"error": "Department not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    name = data.get('name', dept.name)
    location = data.get('location', dept.location)
    dept_code = data.get('dept_code', dept.dept_code)

    if not is_valid_dept_code(dept_code):
        return jsonify({"error": "Invalid dept_code. Must be 4 alphanumeric characters"}), 400

    if name == dept.name and location == dept.location and dept_code == dept.dept_code:
        return jsonify({"message": "Same information, nothing to update"}), 400

    dept.name = name
    dept.location = location
    dept.dept_code = dept_code

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "dept_code must be unique"}), 400

    return jsonify({"message": "Department updated"}), 200


# -----------------------------
# PROJECT CRUD ROUTES
# -----------------------------
@app.route('/projects', methods=['POST'])
def create_project():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    department_id = data.get('department_id')
    project_code = data.get('project_code')

    if not title or not title.strip():
        return jsonify({"error": "Project title is required"}), 400
    if not description:
        return jsonify({"error": "Project description is required"}), 400
    if not project_code or not is_valid_project_code(project_code):
        return jsonify({"error": "Invalid project_code. Must be 5 alphanumeric characters"}), 400

    try:
        start_date_obj = parse_date(start_date, "start_date")
        end_date_obj = parse_date(end_date, "end_date")
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if department_id:
        dept = Department.query.get(department_id)
        if not dept:
            return jsonify({"error": "Department not found"}), 404

    new_project = Project(
        title=title,
        description=description,
        start_date=start_date_obj,
        end_date=end_date_obj,
        department_id=department_id,
        project_code=project_code
    )

    try:
        db.session.add(new_project)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "project_code must be unique"}), 400

    return jsonify({
        "message": "Project created successfully",
        "project": {
            "id": new_project.id,
            "title": new_project.title,
            "description": new_project.description,
            "start_date": str(new_project.start_date),
            "end_date": str(new_project.end_date),
            "project_code": new_project.project_code
        }
    }), 201


@app.route('/projects/<int:id>', methods=['PUT'])
def update_project(id):
    p = Project.query.get(id)
    if not p:
        return jsonify({"error": "Project not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    title = data.get('title', p.title)
    description = data.get('description', p.description)
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    project_code = data.get('project_code', p.project_code)

    if not is_valid_project_code(project_code):
        return jsonify({"error": "Invalid project_code. Must be 5 alphanumeric characters"}), 400

    start_date_obj = p.start_date
    end_date_obj = p.end_date

    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "Invalid start_date format. Use yyyy-mm-dd"}), 400
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "Invalid end_date format. Use yyyy-mm-dd"}), 400

    if (title == p.title and description == p.description and
        start_date_obj == p.start_date and end_date_obj == p.end_date and
        project_code == p.project_code):
        return jsonify({"message": "Same information, nothing to update"}), 400

    p.title = title
    p.description = description
    p.start_date = start_date_obj
    p.end_date = end_date_obj
    p.project_code = project_code

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "project_code must be unique"}), 400

    return jsonify({"message": "Project updated successfully"}), 200
