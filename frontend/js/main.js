async function loadComponent(name) {
  const content = document.getElementById("content");

  try {
    const res = await fetch(`components/${name}.html`);
    const html = await res.text();
    content.innerHTML = html;

    // Remove old dynamic scripts
    document.querySelectorAll("script[data-dynamic]").forEach(s => s.remove());

    // Add new script
    const script = document.createElement("script");
    script.src = `js/${name}.js`;
    script.dataset.dynamic = "true";
    script.onload = () => {
      switch (name) {
        case "employees": if (typeof loadEmployees === "function") loadEmployees(); break;
        case "departments": if (typeof loadDepartments === "function") loadDepartments(); break;
        case "projects": if (typeof loadProjects === "function") loadProjects(); break;
        case "assign": if (typeof loadAssignments === "function") loadAssignments(); break;
      }
    };
    document.body.appendChild(script);
  } catch (err) {
    console.error("Error loading component:", err);
    content.innerHTML = "<p>Failed to load component.</p>";
  }
}

// Button event listeners
document.getElementById("homeBtn")?.addEventListener("click", () => loadComponent("home"));
document.getElementById("employeesBtn")?.addEventListener("click", () => loadComponent("employees"));
document.getElementById("departmentsBtn")?.addEventListener("click", () => loadComponent("departments"));
document.getElementById("projectsBtn")?.addEventListener("click", () => loadComponent("projects"));
document.getElementById("assignBtnNav")?.addEventListener("click", () => loadComponent("assign"));

// Load home on page load
loadComponent("home");
