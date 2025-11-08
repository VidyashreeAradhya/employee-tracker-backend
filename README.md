# Employee Tracker Backend (Flask + MySQL)

## Project Description
The **Employee Tracker** is a backend-only REST API system designed to manage an organization’s employees, departments, and projects.

This system provides endpoints to perform CRUD operations and assign employees to multiple projects. It helps track:
- Which employees belong to which department
- Which projects employees are working on
- Employee joining dates and salary details

---

## Tech Stack
- **Python 3.9+**
- **Flask**
- **Flask-SQLAlchemy**
- **MySQL**
- **Postman (for API testing)**

---

## Database Design
### Tables:
1. **departments**
2. **employees**
3. **projects**
4. **employee_project** (many-to-many relationship table)

### Relationships:
- One Department → Many Employees  
- One Project ↔ Many Employees (Many-to-Many)

---

## API Endpoints

### Employee
| Method | Endpoint | Description |
|--------|-----------|--------------|
| POST | `/employees` | Create new employee |
| GET | `/employees` | Get all employees |
| GET | `/employees/<id>` | Get employee by ID |
| PUT | `/employees/<id>` | Update employee |
| DELETE | `/employees/<id>` | Delete employee |

### Department
| Method | Endpoint | Description |
|--------|-----------|--------------|
| POST | `/departments` | Create department |
| GET | `/departments` | Get all departments |
| GET | `/departments/<id>` | Get department by ID |
| PUT | `/departments/<id>` | Update department |
| DELETE | `/departments/<id>` | Delete department |

### Project
| Method | Endpoint | Description |
|--------|-----------|--------------|
| POST | `/projects` | Create project |
| GET | `/projects` | Get all projects |
| GET | `/projects/<id>` | Get project by ID |
| PUT | `/projects/<id>` | Update project |
| DELETE | `/projects/<id>` | Delete project |

### 🔗 Assign Employee to Project
| Method | Endpoint | Description |
|--------|-----------|--------------|
| POST | `/projects/<project_id>/assign` | Assign employee(s) to project |

---

## Validations Implemented
- `name`, `email`, `title` → cannot be blank  
- `email` → must be valid format  
- `join_date` → cannot be a future date  

---

## Testing
All APIs were tested using **Postman**.

Example JSON request to add employee:
```json
{
  "name": "Vidyashree",
  "email": "vidyashree@gmail.com",
  "salary": 40000,
  "join_date": "2025-11-01",
  "department_id": 2
}
