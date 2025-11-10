from flask import Flask, request, jsonify
from sqlalchemy.exc import IntegrityError
from app import app, db
from models import db, Employee, Department, Project, employee_project
from datetime import datetime

# Helper function to accept both yy-mm-dd and yyyy-mm-dd formats
def parse_date(date_value, field_name):
    """Parses both yy-mm-dd and yyyy-mm-dd date formats."""
    if not date_value:
        raise ValueError(f"{field_name} is required")

    for fmt in ("%Y-%m-%d", "%y-%m-%d"):
        try:
            return datetime.strptime(date_value, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Invalid {field_name} format. Use yy-mm-dd or yyyy-mm-dd")

# -----------------------------
# Employee CRUD Routes
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
        join_date=join_date_obj,  # FIXED: should use parsed date
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


@app.route('/employees', methods=['GET'])
def get_employees():
    employees = Employee.query.all()
    result = []
    for emp in employees:
        result.append({
            "id": emp.id,
            "name": emp.name,
            "email": emp.email,
            "salary": emp.salary,
            "join_date": str(emp.join_date),
            "department_id": emp.department_id
        })
    return jsonify(result), 200


@app.route('/employees/<int:id>', methods=['GET'])
def get_employee(id):
    emp = Employee.query.get(id)
    if not emp:
        return jsonify({"error": "Employee not found"}), 404
    return jsonify({
        "id": emp.id,
        "name": emp.name,
        "email": emp.email,
        "salary": emp.salary,
        "join_date": str(emp.join_date),
        "department_id": emp.department_id
    }), 200


@app.route('/employees/<int:id>', methods=['PUT'])
def update_employee(id):
    emp = Employee.query.get(id)
    if not emp:
        return jsonify({"error": "Employee not found"}), 404

    data = request.get_json()
    name = data.get('name', emp.name)
    email = data.get('email', emp.email)
    salary = data.get('salary', emp.salary)
    join_date = data.get('join_date')
    department_id = data.get('department_id', emp.department_id)

    # Validations
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

    emp.name = name
    emp.email = email
    emp.salary = salary
    emp.join_date = join_date_obj  #  FIXED: should store parsed date
    emp.department_id = department_id

    db.session.commit()
    return jsonify({"message": "Employee updated successfully"}), 200


@app.route('/employees/<int:id>', methods=['DELETE'])
def delete_employee(id):
    emp = Employee.query.get(id)
    if not emp:
        return jsonify({"error": "Employee not found"}), 404

    db.session.delete(emp)
    db.session.commit()
    return jsonify({"message": "Employee deleted successfully"}), 200


# -----------------------------
# Department CRUD Routes
# -----------------------------

@app.route('/departments', methods=['POST'])
def create_department():
    data = request.get_json()
    name = data.get('name')
    location = data.get('location')

    if not name:
        return jsonify({"error": "Department name is required"}), 400

    dept = Department(name=name, location=location)
    db.session.add(dept)
    db.session.commit()
    return jsonify({"message": "Department created", "id": dept.id}), 201


@app.route('/departments', methods=['GET'])
def get_departments():
    depts = Department.query.all()
    result = [{"id": d.id, "name": d.name, "location": d.location} for d in depts]
    return jsonify({"departments": result}), 200


@app.route('/departments/<int:id>', methods=['GET'])
def get_department(id):
    dept = Department.query.get(id)
    if not dept:
        return jsonify({"error": "Department not found"}), 404
    employees = [{"id": e.id, "name": e.name} for e in dept.employees]
    return jsonify({"id": dept.id, "name": dept.name, "location": dept.location, "employees": employees}), 200


@app.route('/departments/<int:id>', methods=['PUT'])
def update_department(id):
    dept = Department.query.get(id)
    if not dept:
        return jsonify({"error": "Department not found"}), 404

    data = request.get_json()
    dept.name = data.get('name', dept.name)
    dept.location = data.get('location', dept.location)
    db.session.commit()
    return jsonify({"message": "Department updated"}), 200


@app.route('/departments/<int:id>', methods=['DELETE'])
def delete_department(id):
    dept = Department.query.get(id)
    if not dept:
        return jsonify({"error": "Department not found"}), 404

    db.session.delete(dept)
    db.session.commit()
    return jsonify({"message": "Department deleted"}), 200


# -----------------------------
# Project CRUD Routes
# -----------------------------

@app.route('/projects', methods=['POST'])
def create_project():
    data = request.get_json()
    title = data.get('title')
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    if not title or not title.strip():
        return jsonify({"error": "Project title is required"}), 400

    try:
        start_date_obj = parse_date(start_date, "start_date")
        end_date_obj = parse_date(end_date, "end_date")
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    new_project = Project(
        title=title,
        start_date=start_date_obj,
        end_date=end_date_obj
    )

    db.session.add(new_project)
    db.session.commit()

    return jsonify({
        "message": "Project created successfully",
        "project": {
            "id": new_project.id,
            "title": new_project.title,
            "start_date": str(new_project.start_date),
            "end_date": str(new_project.end_date)
        }
    }), 201



@app.route('/projects', methods=['GET'])
def get_projects():
    projects = Project.query.all()
    result = []
    for p in projects:
        emp_list = [{"id": e.id, "name": e.name} for e in p.employees]
        result.append({
            "id": p.id,
            "title": p.title,
            "description": p.description,
            "start_date": str(p.start_date),
            "end_date": str(p.end_date),
            "employees": emp_list
        })
    return jsonify(result), 200


@app.route('/projects/<int:id>', methods=['GET'])
def get_project(id):
    p = Project.query.get(id)
    if not p:
        return jsonify({"error": "Project not found"}), 404
    emp_list = [{"id": e.id, "name": e.name} for e in p.employees]
    return jsonify({
        "id": p.id,
        "title": p.title,
        "description": p.description,
        "start_date": str(p.start_date),
        "end_date": str(p.end_date),
        "employees": emp_list
    }), 200


@app.route('/projects/<int:id>', methods=['PUT'])
def update_project(id):
    p = Project.query.get(id)
    if not p:
        return jsonify({"error": "Project not found"}), 404

    data = request.get_json()
    p.title = data.get('title', p.title)
    p.description = data.get('description', p.description)
    p.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date() if data.get('start_date') else p.start_date
    p.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else p.end_date

    db.session.commit()
    return jsonify({"message": "Project updated"}), 200


@app.route('/projects/<int:id>', methods=['DELETE'])
def delete_project(id):
    p = Project.query.get(id)
    if not p:
        return jsonify({"error": "Project not found"}), 404
    db.session.delete(p)
    db.session.commit()
    return jsonify({"message": "Project deleted"}), 200


# -----------------------------
# Assign Employee to Project
# -----------------------------
@app.route('/projects/<int:project_id>/assign', methods=['POST'])
def assign_employees_to_project(project_id):
    data = request.get_json()

    # Validate JSON body
    if not data or 'employee_id' not in data:
        return jsonify({'error': 'employee_id is required'}), 400

    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404

    # Handle both single ID and list of IDs
    employee_ids = data['employee_id']
    if isinstance(employee_ids, int):
        employee_ids = [employee_ids]  # convert to list for consistency

    elif not isinstance(employee_ids, list):
        return jsonify({'error': 'employee_id must be an integer or a list of integers'}), 400

    # Fetch all employees by IDs
    employees = Employee.query.filter(Employee.id.in_(employee_ids)).all()
    if not employees:
        return jsonify({'error': 'No valid employees found'}), 400

    # Assign employees to the project
    for emp in employees:
        if emp not in project.employees:
            project.employees.append(emp)

    db.session.commit()

    return jsonify({
        'message': 'Employee(s) assigned successfully',
        'assigned_employee_ids': [e.id for e in employees],
        'project_id': project_id
    }), 200