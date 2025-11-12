const BASE = "http://127.0.0.1:5000";

const projectTableBody = document.querySelector("#projectTable tbody");
const addProjectBtn = document.getElementById("addProjectBtn");
const projectModal = document.getElementById("projectModal");
const closeProjectModal = projectModal.querySelector(".close");
const projectForm = document.getElementById("projectForm");
const modalTitle = document.getElementById("modalTitle");

// Open modal for Add
addProjectBtn.addEventListener("click", () => {
  modalTitle.textContent = "Add Project";
  projectForm.reset();
  projectForm.dataset.mode = "add";
  projectModal.style.display = "block";
});

// Close modal
closeProjectModal.addEventListener("click", () => projectModal.style.display = "none");
window.addEventListener("click", e => {
  if (e.target === projectModal) projectModal.style.display = "none";
});

// Load projects
async function loadProjects() {
  const res = await fetch(`${BASE}/projects`);
  const data = await res.json();
  projectTableBody.innerHTML = "";
  data.forEach(p => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${p.id}</td>
      <td>${p.title}</td>
      <td>${p.description}</td>
      <td>${p.start_date}</td>
      <td>${p.end_date ?? "-"}</td>
      <td>${p.project_code}</td>
      <td>
        <button class="edit" data-id="${p.id}">Edit</button>
        <button class="delete" data-id="${p.id}">Delete</button>
      </td>
    `;
    projectTableBody.appendChild(tr);
  });

  // Edit buttons
  document.querySelectorAll(".edit").forEach(btn => {
    btn.addEventListener("click", async () => {
      const id = btn.dataset.id;
      const res = await fetch(`${BASE}/projects/${id}`);
      const proj = await res.json();

      modalTitle.textContent = "Edit Project";
      projectForm.dataset.mode = "edit";
      projectForm.dataset.id = id;

      document.getElementById("projectId").value = proj.id;
      document.getElementById("title").value = proj.title;
      document.getElementById("description").value = proj.description;
      document.getElementById("start_date").value = proj.start_date;
      document.getElementById("end_date").value = proj.end_date;

      projectModal.style.display = "block";
    });
  });

  // Delete buttons
  document.querySelectorAll(".delete").forEach(btn => {
    btn.addEventListener("click", async () => {
      if (!confirm("Delete this project?")) return;
      const res = await fetch(`${BASE}/projects/${btn.dataset.id}`, { method: "DELETE" });
      alert((await res.json()).message);
      loadProjects();
    });
  });
}

// Form submit
projectForm.addEventListener("submit", async e => {
  e.preventDefault();
  const mode = projectForm.dataset.mode;
  const id = projectForm.dataset.id;
  const payload = {
    title: document.getElementById("title").value,
    description: document.getElementById("description").value,
    start_date: document.getElementById("start_date").value,
    end_date: document.getElementById("end_date").value
  };

  let url = `${BASE}/projects`;
  let method = "POST";
  if (mode === "edit") {
    url = `${BASE}/projects/${id}`;
    method = "PUT";
  }

  const res = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  const result = await res.json();
  alert(result.message || result.error);
  projectModal.style.display = "none";
  loadProjects();
});

// Initial load
loadProjects();
