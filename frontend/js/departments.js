const BASE = "http://127.0.0.1:5000";

const deptTableBody = document.querySelector("#departmentTable tbody");
const addDeptBtn = document.getElementById("addDepartmentBtn");
const deptModal = document.getElementById("departmentModal");
const closeDeptModal = deptModal.querySelector(".close");
const deptForm = document.getElementById("departmentForm");
const modalTitle = document.getElementById("modalTitle");
const searchInput = document.getElementById("searchInput");
const searchBtn = document.getElementById("searchBtn");

// Toast container
let toastContainer = document.querySelector(".toast-container");
if (!toastContainer) {
  toastContainer = document.createElement("div");
  toastContainer.className = "toast-container";
  document.body.appendChild(toastContainer);
}

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

  setTimeout(() => toast.classList.add("show"), 100);
  setTimeout(() => {
    toast.classList.remove("show");
    setTimeout(() => toast.remove(), 400);
  }, 3000);
}

// Open modal for Add
addDeptBtn.addEventListener("click", () => {
  modalTitle.textContent = "Add Department";
  deptForm.reset();
  deptForm.dataset.mode = "add";
  deptModal.style.display = "block";
});

// Close modal
closeDeptModal.addEventListener("click", () => (deptModal.style.display = "none"));
window.addEventListener("click", e => {
  if (e.target === deptModal) deptModal.style.display = "none";
});

// Load departments
async function loadDepartments(query = "") {
  try {
    const res = await fetch(`${BASE}/departments`);
    if (!res.ok) throw new Error("Failed to fetch departments");
    const data = await res.json();

    // Filter if query present
    const filtered = data.filter(d =>
      d.name.toLowerCase().includes(query.toLowerCase()) ||
      (d.location ?? "").toLowerCase().includes(query.toLowerCase())
    );

    deptTableBody.innerHTML = "";
    if (filtered.length === 0) {
      deptTableBody.innerHTML = `
        <tr><td colspan="5" style="text-align:center;">No departments found</td></tr>
      `;
      return;
    }

    filtered.forEach((d, index) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${index + 1}</td>
        <td>${d.name}</td>
        <td>${d.location ?? "-"}</td>
        <td>${d.dept_code ?? "-"}</td>
        <td>
          <button class="edit" data-id="${d.id}">Edit</button>
          <button class="delete" data-id="${d.id}">Delete</button>
        </td>
      `;
      deptTableBody.appendChild(tr);
    });

    attachDeptEvents();
  } catch (err) {
    console.error("Error fetching departments:", err);
    showMessage("Error fetching departments!", "error");
  }
}

// Attach edit & delete handlers
function attachDeptEvents() {
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

  document.querySelectorAll(".delete").forEach(btn => {
    btn.addEventListener("click", async () => {
      const id = btn.dataset.id;
      if (!confirm("Delete this department?")) return;
      const res = await fetch(`${BASE}/departments/${id}`, { method: "DELETE" });
      const result = await res.json();
      showMessage(result.message || "Department deleted successfully", "success");
      loadDepartments();
    });
  });
}

// Form submit (Add/Edit)
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
  showMessage(result.message || result.error, result.error ? "error" : "success");
  deptModal.style.display = "none";
  loadDepartments();
});

// Search
searchBtn.addEventListener("click", () => {
  const query = searchInput.value.trim();
  loadDepartments(query);
});

// Initial load
loadDepartments();
