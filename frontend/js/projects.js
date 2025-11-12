const BASE = "http://127.0.0.1:5000";

const projectTableBody = document.querySelector("#projectTable tbody");
const addProjectBtn = document.getElementById("addProjectBtn");
const projectModal = document.getElementById("projectModal");
const closeProjectModal = projectModal.querySelector(".close");
const projectForm = document.getElementById("projectForm");
const modalTitle = document.getElementById("modalTitle");
const messageBox = document.getElementById("messageBox");
const searchInput = document.getElementById("searchInput");
const searchBtn = document.getElementById("searchBtn");

// Popup message
function showMessage(text, type = "success") {
  const msg = document.createElement("div");
  msg.className = `popup-message ${type}`;
  msg.textContent = text;
  document.body.appendChild(msg);

  setTimeout(() => {
    msg.classList.add("show");
  }, 100);

  setTimeout(() => {
    msg.classList.remove("show");
    setTimeout(() => msg.remove(), 400);
  }, 2000);
}

// Open modal
addProjectBtn.addEventListener("click", () => {
  modalTitle.textContent = "Add Project";
  projectForm.reset();
  projectForm.dataset.mode = "add";
  projectModal.style.display = "block";
});

// Close modal
closeProjectModal.addEventListener("click", () => (projectModal.style.display = "none"));
window.addEventListener("click", e => {
  if (e.target === projectModal) projectModal.style.display = "none";
});

// Load Projects
async function loadProjects(query = "") {
  try {
    const res = await fetch(`${BASE}/projects`);
    if (!res.ok) throw new Error("Failed to fetch projects");
    const data = await res.json();

    const filtered = data.filter(p =>
      p.title.toLowerCase().includes(query.toLowerCase()) ||
      p.description.toLowerCase().includes(query.toLowerCase())
    );

    projectTableBody.innerHTML = "";
    filtered.forEach((p, index) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${index + 1}</td>
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

    attachProjectEvents();
  } catch (err) {
    showMessage("Error fetching projects", "error");
    console.error(err);
  }
}

// Edit / Delete button events
function attachProjectEvents() {
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

  document.querySelectorAll(".delete").forEach(btn => {
    btn.addEventListener("click", async () => {
      if (!confirm("Delete this project?")) return;
      const res = await fetch(`${BASE}/projects/${btn.dataset.id}`, { method: "DELETE" });
      const result = await res.json();
      showMessage(result.message || "Project deleted successfully", "success");
      loadProjects();
    });
  });
}

// Form Submit
projectForm.addEventListener("submit", async e => {
  e.preventDefault();
  const mode = projectForm.dataset.mode;
  const id = projectForm.dataset.id;

  const startDate = document.getElementById("start_date").value;
  const endDate = document.getElementById("end_date").value;

  if (endDate && endDate < startDate) {
    showMessage("End date cannot be earlier than start date!", "error");
    return;
  }

  const payload = {
    title: document.getElementById("title").value,
    description: document.getElementById("description").value,
    start_date: startDate,
    end_date: endDate
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

  showMessage(result.message || result.error, result.error ? "error" : "success");
  projectModal.style.display = "none";
  loadProjects();
});

// Search button
searchBtn.addEventListener("click", () => {
  const query = searchInput.value.trim();
  loadProjects(query);
});

// Initial load
loadProjects();


const style = document.createElement("style");
style.textContent = `
.popup-message {
  position: fixed;
  top: 20px;
  right: -300px;
  background: #222;
  color: white;
  padding: 10px 18px;
  border-radius: 8px;
  box-shadow: 0 3px 10px rgba(0,0,0,0.3);
  font-size: 15px;
  opacity: 0;
  transition: all 0.4s ease;
  z-index: 9999;
}
.popup-message.show {
  right: 20px;
  opacity: 1;
}
.popup-message.success { background: #28a745; }
.popup-message.error { background: #dc3545; }
.popup-message.info { background: #007bff; }
`;
document.head.appendChild(style);
