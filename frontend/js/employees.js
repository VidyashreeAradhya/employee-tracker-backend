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

// Toast container
let toastContainer = document.querySelector(".toast-container");
if (!toastContainer) {
  toastContainer = document.createElement("div");
  toastContainer.className = "toast-container";
  document.body.appendChild(toastContainer);
}

let employees = [];
let departments = [];

// Toast message
function showMessage(message, type = "success") {
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <span class="toast-icon">${
      type === "success" ? "✅" : type === "error" ? "❌" : "ℹ️"
    }</span>
    <span class="toast-text">${message}</span>
  `;
  toastContainer.appendChild(toast);

  // animate in
  setTimeout(() => toast.classList.add("show"), 100);

  // remove after 3s
  setTimeout(() => {
    toast.classList.remove("show");
    setTimeout(() => toast.remove(), 400);
  }, 3000);
}

/* Load Departments */
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

/* Open Modal */
addEmployeeBtn.addEventListener("click", () => {
  modalTitle.textContent = "Add Employee";
  employeeForm.reset();
  employeeForm.dataset.mode = "add";
  employeeModal.style.display = "block";
});

/* Close Modal */
closeModal.addEventListener("click", () => {
  employeeModal.style.display = "none";
});
window.addEventListener("click", e => {
  if (e.target == employeeModal) employeeModal.style.display = "none";
});

/* Load Employees */
async function loadEmployees(query = "") {
  const res = await fetch(`${BASE}/employees`);
  employees = await res.json();

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

/* Attach events for edit & delete */
function attachEventListeners() {
  document.querySelectorAll(".edit").forEach(btn => {
    btn.addEventListener("click", async () => {
      const id = btn.dataset.id;
      const res = await fetch(`${BASE}/employees/${id}`);
      const emp = await res.json();

      modalTitle.textContent = "Edit Employee";
      employeeForm.dataset.mode = "edit";
      employeeForm.dataset.id = id;
      employeeForm.dataset.original = JSON.stringify(emp);

      document.getElementById("id").value = emp.id;
      document.getElementById("name").value = emp.name;
      document.getElementById("email").value = emp.email;
      document.getElementById("salary").value = emp.salary;
      document.getElementById("join_date").value = emp.join_date;
      departmentSelect.value = emp.department_id;

      employeeModal.style.display = "block";
    });
  });

  document.querySelectorAll(".delete").forEach(btn => {
    btn.addEventListener("click", async () => {
      if (!confirm("Delete this employee?")) return;
      const res = await fetch(`${BASE}/employees/${btn.dataset.id}`, { method: "DELETE" });
      const data = await res.json();
      showMessage(data.message || "Employee deleted successfully", "success");
      loadEmployees();
    });
  });
}

/* Search */
searchBtn.addEventListener("click", () => {
  const query = searchInput.value.trim();
  loadEmployees(query);
});

/* Add/Edit Employee */
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

  if (mode === "edit") {
    const original = JSON.parse(employeeForm.dataset.original || "{}");
    const isSame = Object.keys(payload).every(k => String(payload[k]) === String(original[k]));
    if (isSame) {
      showMessage("Same information, nothing to update", "info");
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
  showMessage(result.message || result.error, result.error ? "error" : "success");
  employeeModal.style.display = "none";
  loadEmployees();
});

/* Init */
(async function init() {
  await loadDepartments();
  await loadEmployees();
})();
