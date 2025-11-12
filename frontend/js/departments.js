const BASE = "http://127.0.0.1:5000";

const deptTableBody = document.querySelector("#departmentTable tbody");
const addDeptBtn = document.getElementById("addDepartmentBtn");
const deptModal = document.getElementById("departmentModal");
const closeDeptModal = deptModal.querySelector(".close");
const deptForm = document.getElementById("departmentForm");
const modalTitle = document.getElementById("modalTitle");

// Open modal for Add
addDeptBtn.addEventListener("click", () => {
  modalTitle.textContent = "Add Department";
  deptForm.reset();
  deptForm.dataset.mode = "add";
  deptModal.style.display = "block";
});

// Close modal
closeDeptModal.addEventListener("click", () => deptModal.style.display = "none");
window.addEventListener("click", e => {
  if (e.target === deptModal) deptModal.style.display = "none";
});

// Load departments
async function loadDepartments() {
  const res = await fetch(`${BASE}/departments`);
  const data = await res.json();
  deptTableBody.innerHTML = "";
  data.forEach(d => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${d.id}</td>
      <td>${d.name}</td>
      <td>${d.location ?? "-"}</td>
      <td>${d.dept_code}</td>
      <td>
        <button class="edit" data-id="${d.id}">Edit</button>
        <button class="delete" data-id="${d.id}">Delete</button>
      </td>
    `;
    deptTableBody.appendChild(tr);
  });

  // Edit buttons
  document.querySelectorAll(".edit").forEach(btn => {
    btn.addEventListener("click", async () => {
      const id = btn.dataset.id;
      const res = await fetch(`${BASE}/departments/${id}`);
      const dept = await res.json();

      modalTitle.textContent = "Edit Department";
      deptForm.dataset.mode = "edit";
      deptForm.dataset.id = id;

      document.getElementById("departmentId").value = dept.id;
      document.getElementById("deptName").value = dept.name;
      document.getElementById("deptLocation").value = dept.location;

      deptModal.style.display = "block";
    });
  });

  // Delete buttons
  document.querySelectorAll(".delete").forEach(btn => {
    btn.addEventListener("click", async () => {
      if (!confirm("Delete this department?")) return;
      const res = await fetch(`${BASE}/departments/${btn.dataset.id}`, { method: "DELETE" });
      alert((await res.json()).message);
      loadDepartments();
    });
  });
}

// Form submit
deptForm.addEventListener("submit", async e => {
  e.preventDefault();
  const mode = deptForm.dataset.mode;
  const id = deptForm.dataset.id;
  const payload = {
    name: document.getElementById("deptName").value,
    location: document.getElementById("deptLocation").value
  };

  let url = `${BASE}/departments`;
  let method = "POST";
  if (mode === "edit") {
    url = `${BASE}/departments/${id}`;
    method = "PUT";
  }

  const res = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  const result = await res.json();
  alert(result.message || result.error);
  deptModal.style.display = "none";
  loadDepartments();
});

// Initial load
loadDepartments();
