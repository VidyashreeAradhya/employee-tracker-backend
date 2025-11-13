from flask import jsonify, request
from sqlalchemy.exc import IntegrityError
from extensions import db
from models import Employee, Department, Project, employee_project
from datetime import datetime
import random, string, re

def register_routes(app):

    # -------------------------------
    # Helper Functions
    # -------------------------------
    def parse_date(date_value, field_name):
        if not date_value:
            raise ValueError(f"{field_name} is required")
        try:
            return datetime.strptime(date_value, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(f"Invalid {field_name} format. Use yyyy-mm-dd")

    def generate_unique_code(model, field_name, length):
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
            if not db.session.query(model).filter(getattr(model, field_name) == code).first():
                return code

    # -------------------------------
    # Home Route
    # -------------------------------
    @app.route("/")
    def home():
        return jsonify({"message": "Employee Tracker API is running!"})

    # -------------------------------
    # EMPLOYEE CRUD ROUTES
    # -------------------------------
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

        if not name or not Employee.is_valid_name(name):
            return jsonify({"error": "Invalid name. Name should contain only alphabets"}), 400
        if not email or not Employee.is_valid_email(email):
            return jsonify({"error": "Invalid email format. Email must end with .com"}), 400

        try:
            join_date_obj = parse_date(join_date, "join_date")
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

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
            return jsonify({"error": "Email already exists"}), 400

        return jsonify({"message": "Employee created successfully", "id": new_employee.id}), 201

    @app.route('/employees', methods=['GET'])
    def get_employees():
        employees = Employee.query.all()
        result = []

        for e in employees:
            assigned_projects = db.session.execute(
                employee_project.select().where(employee_project.c.employee_id == e.id)
            ).fetchall()

            projects = [Project.query.get(row.project_id) for row in assigned_projects]

            result.append({
                "id": e.id,
                "name": e.name,
                "email": e.email,
                "salary": e.salary,
                "join_date": str(e.join_date),
                "department_id": e.department_id,
                "projects": [
                    {"id": p.id, "title": p.title, "description": p.description,
                     "start_date": str(p.start_date), "end_date": str(p.end_date),
                     "project_code": p.project_code}
                    for p in projects if p
                ]
            })

        return jsonify(result), 200


    @app.route('/employees/<int:id>', methods=['GET'])
    def get_employee(id):
        e = Employee.query.get(id)
        if not e:
            return jsonify({"error": "Employee not found"}), 404

        assigned_projects = db.session.execute(
            employee_project.select().where(employee_project.c.employee_id == e.id)
        ).fetchall()

        projects = [Project.query.get(row.project_id) for row in assigned_projects]

        return jsonify({
            "id": e.id,
            "name": e.name,
            "email": e.email,
            "salary": e.salary,
            "join_date": str(e.join_date),
            "department_id": e.department_id,
            "projects": [
                {"id": p.id, "title": p.title, "description": p.description,
                 "start_date": str(p.start_date), "end_date": str(p.end_date),
                 "project_code": p.project_code}
                for p in projects if p
           ]
        }), 200
    
    # -------------------------------
    # GET ALL PROJECTS ASSIGNED TO AN EMPLOYEE
    # -------------------------------
    @app.route('/employees/<int:emp_id>/projects', methods=['GET'])
    def get_employee_projects(emp_id):
        emp = Employee.query.get(emp_id)
        if not emp:
            return jsonify({"error": "Employee not found"}), 404

        # Get all project IDs assigned to this employee
        assigned_rows = db.session.execute(
            employee_project.select().where(employee_project.c.employee_id == emp_id)
        ).fetchall()

        projects = [Project.query.get(row.project_id) for row in assigned_rows]

        return jsonify([
            {
                "id": p.id,
                "title": p.title,
                "description": p.description,
                "start_date": str(p.start_date),
                "end_date": str(p.end_date),
                "project_code": p.project_code,
                "department": p.department.name if p.department else "-"
            } for p in projects if p
        ]), 200



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
        department_id = data.get('department_id', emp.department_id)

        if not Employee.is_valid_name(name):
            return jsonify({"error": "Invalid name. Only alphabets and spaces are allowed"}), 400

        if not Employee.is_valid_email(email):
            return jsonify({"error": "Invalid email. Must contain @ and end with .com"}), 400


        join_date_obj = emp.join_date
        if data.get('join_date'):
            try:
                join_date_obj = parse_date(data['join_date'], "join_date")
            except ValueError as e:
                return jsonify({"error": str(e)}), 400

        # Check if anything actually changed
        if (emp.name == name and emp.email == email and emp.salary == salary
            and emp.department_id == department_id and emp.join_date == join_date_obj):
            return jsonify({"message": "Same information, nothing to update"}), 200

        emp.name = name
        emp.email = email
        emp.salary = salary
        emp.join_date = join_date_obj
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

    # -------------------------------
    # DEPARTMENT CRUD ROUTES
    # -------------------------------
    @app.route('/departments', methods=['POST'])
    def create_department():
        data = request.get_json()
        name = data.get('name')
        location = data.get('location')

        if not name:
            return jsonify({"error": "Department name is required"}), 400

        dept_code = generate_unique_code(Department, 'dept_code', 4)

        new_dept = Department(name=name, location=location, dept_code=dept_code)
        db.session.add(new_dept)
        db.session.commit()

        return jsonify({
            "message": "Department created successfully",
            "id": new_dept.id,
            "dept_code": new_dept.dept_code
        }), 201

    @app.route('/departments', methods=['GET'])
    def get_departments():
        departments = Department.query.all()
        return jsonify([{
            "id": d.id,
            "name": d.name,
            "location": d.location,
            "dept_code": d.dept_code
        } for d in departments]), 200
    
    @app.route('/departments/<int:id>', methods=['GET'])
    def get_department(id):
        dept = Department.query.get(id)
        if not dept:
            return jsonify({"error": "Department not found"}), 404

        return jsonify({
            "id": dept.id,
            "name": dept.name,
            "location": dept.location,
            "dept_code": dept.dept_code
        }), 200


    @app.route('/departments/<int:id>', methods=['PUT'])
    def update_department(id):
        dept = Department.query.get(id)
        if not dept:
            return jsonify({"error": "Department not found"}), 404

        data = request.get_json()
        name = data.get('name', dept.name)
        location = data.get('location', dept.location)

        # Check if anything actually changed
        if dept.name == name and dept.location == location:
            return jsonify({"message": "Same information, nothing to update"}), 200

        dept.name = name
        dept.location = location
        db.session.commit()
        return jsonify({"message": "Department updated successfully"}), 200


    @app.route('/departments/<int:id>', methods=['DELETE'])
    def delete_department(id):
        dept = Department.query.get(id)
        if not dept:
            return jsonify({"error": "Department not found"}), 404
        db.session.delete(dept)
        db.session.commit()
        return jsonify({"message": "Department deleted successfully"}), 200

    # -------------------------------
    # PROJECT CRUD ROUTES
    # -------------------------------
    @app.route('/projects', methods=['POST'])
    def create_project():
        data = request.get_json()
        title = data.get('title')
        description = data.get('description')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if not title or not description:
            return jsonify({"error": "Title and description are required"}), 400

        try:
            start_date_obj = parse_date(start_date, "start_date")
            end_date_obj = parse_date(end_date, "end_date")
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        project_code = generate_unique_code(Project, 'project_code', 5)

        new_project = Project(
            title=title,
            description=description,
            start_date=start_date_obj,
            end_date=end_date_obj,
            project_code=project_code
        )

        db.session.add(new_project)
        db.session.commit()

        return jsonify({
            "message": "Project created successfully",
            "id": new_project.id,
            "project_code": new_project.project_code
        }), 201

    @app.route('/projects', methods=['GET'])
    def get_projects():
        projects = Project.query.all()
        result = []

        for p in projects:
            assigned_employees = db.session.execute(
                employee_project.select().where(employee_project.c.project_id == p.id)
            ).fetchall()

            employees = [Employee.query.get(row.employee_id) for row in assigned_employees]

            result.append({
                "id": p.id,
                "title": p.title,
                "description": p.description,
                "start_date": str(p.start_date),
                "end_date": str(p.end_date),
                "project_code": p.project_code,
                "employees": [
                    {"id": e.id, "name": e.name, "email": e.email, "department_id": e.department_id}
                    for e in employees if e
               ]
           })

        return jsonify(result), 200

    
    @app.route('/projects/<int:id>', methods=['GET'])
    def get_project(id):
        p = Project.query.get(id)
        if not p:
            return jsonify({"error": "Project not found"}), 404

        assigned_employees = db.session.execute(
            employee_project.select().where(employee_project.c.project_id == p.id)
        ).fetchall()

        employees = [Employee.query.get(row.employee_id) for row in assigned_employees]

        return jsonify({
            "id": p.id,
            "title": p.title,
            "description": p.description,
            "start_date": str(p.start_date),
            "end_date": str(p.end_date),
            "project_code": p.project_code,
            "employees": [
                {"id": e.id, "name": e.name, "email": e.email, "department_id": e.department_id}
                for e in employees if e
            ]
        }), 200




    @app.route('/projects/<int:id>', methods=['PUT'])
    def update_project(id):
        p = Project.query.get(id)
        if not p:
            return jsonify({"error": "Project not found"}), 404

        data = request.get_json()
        title = data.get('title', p.title)
        description = data.get('description', p.description)

        start_date_obj = p.start_date
        end_date_obj = p.end_date

        if data.get('start_date'):
            try:
                start_date_obj = parse_date(data['start_date'], "start_date")
            except ValueError as e:
                return jsonify({"error": str(e)}), 400
        if data.get('end_date'):
            try:
                end_date_obj = parse_date(data['end_date'], "end_date")
            except ValueError as e:
                return jsonify({"error": str(e)}), 400

        # Check if anything actually changed
        if (p.title == title and p.description == description
            and p.start_date == start_date_obj and p.end_date == end_date_obj):
            return jsonify({"message": "Same information, nothing to update"}), 200

        p.title = title
        p.description = description
        p.start_date = start_date_obj
        p.end_date = end_date_obj
        db.session.commit()
        return jsonify({"message": "Project updated successfully"}), 200


    @app.route('/projects/<int:id>', methods=['DELETE'])
    def delete_project(id):
        p = Project.query.get(id)
        if not p:
            return jsonify({"error": "Project not found"}), 404
        db.session.delete(p)
        db.session.commit()
        return jsonify({"message": "Project deleted successfully"}), 200

    # -------------------------------
    # ASSIGN / UNASSIGN EMPLOYEE TO PROJECT
    # -------------------------------
    @app.route('/projects/<int:project_id>/assign', methods=['POST'])
    def assign_employee_to_project(project_id):
        data = request.get_json()
        if not data or 'employee_id' not in data:
            return jsonify({"error": "employee_id is required"}), 400

        project = Project.query.get(project_id)
        employee = Employee.query.get(data['employee_id'])
        if not project or not employee:
            return jsonify({"error": "Invalid employee or project"}), 404

        existing = db.session.execute(
            employee_project.select().where(
                (employee_project.c.employee_id == employee.id) &
                (employee_project.c.project_id == project.id)
            )
        ).first()

        if existing:
            return jsonify({"message": "Employee already assigned"}), 400

        db.session.execute(
            employee_project.insert().values(employee_id=employee.id, project_id=project.id)
        )
        db.session.commit()
        return jsonify({"message": f"Employee {employee.email} assigned to {project.title}"}), 200

    @app.route('/projects/<int:project_id>/unassign', methods=['POST'])
    def unassign_employee_from_project(project_id):
        data = request.get_json()
        if not data or 'employee_id' not in data:
            return jsonify({"error": "employee_id is required"}), 400

        project = Project.query.get(project_id)
        employee = Employee.query.get(data['employee_id'])
        if not project or not employee:
            return jsonify({"error": "Invalid employee or project"}), 404

        existing = db.session.execute(
            employee_project.select().where(
                (employee_project.c.employee_id == employee.id) &
                (employee_project.c.project_id == project.id)
            )
        ).first()

        if not existing:
            return jsonify({"message": "Employee not assigned"}), 400

        db.session.execute(
            employee_project.delete().where(
                (employee_project.c.employee_id == employee.id) &
                (employee_project.c.project_id == project.id)
            )
        )
        db.session.commit()
        return jsonify({"message": f"Employee {employee.email} unassigned from {project.title}"}), 200

    # -------------------------------
    # GET ALL EMPLOYEES ASSIGNED TO A PROJECT
    # -------------------------------
    @app.route('/projects/<int:project_id>/employees', methods=['GET'])
    def get_project_employees(project_id):
        project = Project.query.get(project_id)
        if not project:
            return jsonify({"error": "Project not found"}), 404

        assigned = db.session.execute(
            employee_project.select().where(employee_project.c.project_id == project_id)
        ).fetchall()

        if not assigned:
            return jsonify([]), 200

        employees = [Employee.query.get(row.employee_id) for row in assigned]
        return jsonify([
            {
                "id": e.id,
                "name": e.name,
                "email": e.email,
                "department_id": e.department_id
            } for e in employees if e
        ]), 200
