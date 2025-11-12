const BASE = "http://127.0.0.1:5000";

const assignmentTableBody = document.querySelector("#assignmentTable tbody");
const assignBtn = document.getElementById("assignBtn");
const assignModal = document.getElementById("assignModal");
const closeAssignModal = assignModal.querySelector(".close");
const assignForm = document.getElementById("assignForm");
const employeeSelect = document.getElementById("employeeSelect");
const projectSelect = document.getElementById("projectSelect");

// Message box for success/info/error
function showMessage(message, type = "success") {
  const msgBox = document.createElement("div");
  msgBox.textContent = message;
  msgBox.className = `msg-box ${type}`;
  document.body.appendChild(msgBox);
  setTimeout(() => msgBox.remove(), 2500);
}

// Open modal
assignBtn.addEventListener("click", async () => {
  // Load employees
  const empRes = await fetch(`${BASE}/employees`);
  const employees = await empRes.json();
  employeeSelect.innerHTML = '<option value="">Select Employee</option>';
  employees.forEach(e => {
    const option = document.createElement("option");
    option.value = e.id;
    option.textContent = `${e.name} (${e.email})`;
    employeeSelect.appendChild(option);
  });

  // Load projects
  const projRes = await fetch(`${BASE}/projects`);
  const projects = await projRes.json();
  projectSelect.innerHTML = '<option value="">Select Project</option>';
  projects.forEach(p => {
    const option = document.createElement("option");
    option.value = p.id;
    option.textContent = `${p.title}`;
    projectSelect.appendChild(option);
  });

  assignModal.style.display = "block";
});

// Close modal
closeAssignModal.addEventListener("click", () => assignModal.style.display = "none");
window.addEventListener("click", e => {
  if (e.target === assignModal) assignModal.style.display = "none";
});

// Load current assignments
async function loadAssignments() {
  const empRes = await fetch(`${BASE}/employees`);
  const employees = await empRes.json();
  assignmentTableBody.innerHTML = "";

  for (let e of employees) {
    for (let p of e.projects) {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${e.name}</td>
        <td>${p.title}</td>
        <td>
          <button class="unassign" data-employee="${e.id}" data-project="${p.id}">Unassign</button>
        </td>
      `;
      assignmentTableBody.appendChild(tr);
    }
  }

  // Unassign buttons
  document.querySelectorAll(".unassign").forEach(btn => {
    btn.addEventListener("click", async () => {
      const empId = btn.dataset.employee;
      const projId = btn.dataset.project;

      const res = await fetch(`${BASE}/projects/${projId}/unassign`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ employee_id: empId })
      });

      const result = await res.json();
      showMessage(result.message || result.error, result.error ? "error" : "success");
      loadAssignments();
    });
  });
}

// Form submit - assign
assignForm.addEventListener("submit", async e => {
  e.preventDefault();
  const employee_id = employeeSelect.value;
  const project_id = projectSelect.value;

  if (!employee_id || !project_id) {
    showMessage("Please select both employee and project", "error");
    return;
  }

  const res = await fetch(`${BASE}/projects/${project_id}/assign`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ employee_id })
  });

  const result = await res.json();
  showMessage(result.message || result.error, result.error ? "error" : "success");
  assignModal.style.display = "none";
  loadAssignments();
});

// Initial load
loadAssignments();
