const BASE = "http://127.0.0.1:5000";

const employeeTableBody = document.getElementById("employeeTableBody");
const addEmployeeBtn = document.getElementById("addEmployeeBtn");
const employeeModal = document.getElementById("employeeModal");
const closeModal = document.querySelector(".modal .close");
const employeeForm = document.getElementById("employeeForm");
const modalTitle = document.getElementById("modalTitle");
const departmentSelect = document.getElementById("departmentSelect");
const searchBtn = document.getElementById("searchBtn");
const searchInput = document.getElementById("searchInput");

let employees = [];
let departments = [];

// ✅ Load Departments for dropdown
async function loadDepartments() {
  const res = await fetch(`${BASE}/departments`);
  departments = await res.json();

  departmentSelect.innerHTML = `<option value="">-- Select Department --</option>`;
  departments.forEach(dep => {
    const opt = document.createElement("option");
    opt.value = dep.id;
    opt.textContent = dep.name;
    departmentSelect.appendChild(opt);
  });
}

// ✅ Open Modal
addEmployeeBtn.addEventListener("click", () => {
  modalTitle.textContent = "Add Employee";
  employeeForm.reset();
  employeeForm.dataset.mode = "add";
  employeeModal.style.display = "block";
});

// ✅ Close Modal
closeModal.addEventListener("click", () => {
  employeeModal.style.display = "none";
});
window.addEventListener("click", e => {
  if (e.target == employeeModal) employeeModal.style.display = "none";
});

// ✅ Load Employees
async function loadEmployees(query = "") {
  const res = await fetch(`${BASE}/employees`);
  employees = await res.json();

  // Filter for search
  if (query) {
    employees = employees.filter(e =>
      e.name.toLowerCase().includes(query.toLowerCase()) ||
      e.email.toLowerCase().includes(query.toLowerCase())
    );
  }

  employeeTableBody.innerHTML = "";
  employees.forEach((e, index) => {
    const departmentName = departments.find(d => d.id === e.department_id)?.name || "-";
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${index + 1}</td>
      <td>${e.name}</td>
      <td>${e.email}</td>
      <td>${e.salary}</td>
      <td>${e.join_date}</td>
      <td>${departmentName}</td>
      <td>
        <button class="edit" data-id="${e.id}">Edit</button>
        <button class="delete" data-id="${e.id}">Delete</button>
      </td>
    `;
    employeeTableBody.appendChild(tr);
  });

  attachEventListeners();
}

// ✅ Attach events for edit & delete
function attachEventListeners() {
  document.querySelectorAll(".edit").forEach(btn => {
    btn.addEventListener("click", async () => {
      const id = btn.dataset.id;
      const res = await fetch(`${BASE}/employees/${id}`);
      const emp = await res.json();

      modalTitle.textContent = "Edit Employee";
      employeeForm.dataset.mode = "edit";
      employeeForm.dataset.id = id;

      document.getElementById("id").value = emp.id;
      document.getElementById("name").value = emp.name;
      document.getElementById("email").value = emp.email;
      document.getElementById("salary").value = emp.salary;
      document.getElementById("join_date").value = emp.join_date;
      departmentSelect.value = emp.department_id;

      // Store original data to compare
      employeeForm.dataset.original = JSON.stringify(emp);

      employeeModal.style.display = "block";
    });
  });

  document.querySelectorAll(".delete").forEach(btn => {
    btn.addEventListener("click", async () => {
      if (!confirm("Delete this employee?")) return;
      const res = await fetch(`${BASE}/employees/${btn.dataset.id}`, { method: "DELETE" });
      alert((await res.json()).message);
      loadEmployees();
    });
  });
}

// ✅ Search Function
searchBtn.addEventListener("click", () => {
  const query = searchInput.value.trim();
  loadEmployees(query);
});

// ✅ Add / Edit Employee
employeeForm.addEventListener("submit", async e => {
  e.preventDefault();
  const mode = employeeForm.dataset.mode;
  const id = employeeForm.dataset.id;

  const payload = {
    name: document.getElementById("name").value.trim(),
    email: document.getElementById("email").value.trim(),
    salary: document.getElementById("salary").value,
    join_date: document.getElementById("join_date").value,
    department_id: parseInt(departmentSelect.value)
  };

  // ✅ Compare for same info when updating
  if (mode === "edit") {
    const original = JSON.parse(employeeForm.dataset.original || "{}");
    const isSame = Object.keys(payload).every(k => String(payload[k]) === String(original[k]));
    if (isSame) {
      alert("Same information, nothing to update");
      employeeModal.style.display = "none";
      return;
    }
  }

  let url = `${BASE}/employees`;
  let method = "POST";
  if (mode === "edit") {
    url = `${BASE}/employees/${id}`;
    method = "PUT";
  }

  const res = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  const result = await res.json();
  alert(result.message || result.error);
  employeeModal.style.display = "none";
  loadEmployees();
});

// ✅ Initial Load
(async function init() {
  await loadDepartments();
  await loadEmployees();
})();
