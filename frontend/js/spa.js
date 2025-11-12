// assets/js/spa.js

document.addEventListener("DOMContentLoaded", () => {
  const sections = {
    employeesBtn: document.getElementById("employeesSection"),
    departmentsBtn: document.getElementById("departmentsSection"),
    projectsBtn: document.getElementById("projectsSection"),
    assignBtnNav: document.getElementById("assignSection"),
  };

  // Helper: Hide all sections and show one
  function showSection(sectionId) {
    // Hide all
    Object.values(sections).forEach(sec => {
      if (sec) sec.classList.remove("active");
    });

    // Show target section
    const activeSec = sections[sectionId];
    if (activeSec) activeSec.classList.add("active");

    // Trigger data load for visible section
    switch (sectionId) {
      case "employeesBtn":
        if (typeof loadEmployees === "function") loadEmployees();
        break;
      case "departmentsBtn":
        if (typeof loadDepartments === "function") loadDepartments();
        break;
      case "projectsBtn":
        if (typeof loadProjects === "function") loadProjects();
        break;
      case "assignBtnNav":
        if (typeof loadAssignments === "function") loadAssignments();
        break;
    }
  }

  // Navigation button listeners
  document.getElementById("employeesBtn")?.addEventListener("click", () => showSection("employeesBtn"));
  document.getElementById("departmentsBtn")?.addEventListener("click", () => showSection("departmentsBtn"));
  document.getElementById("projectsBtn")?.addEventListener("click", () => showSection("projectsBtn"));
  document.getElementById("assignBtnNav")?.addEventListener("click", () => showSection("assignBtnNav"));

  // Load employees by default when app starts
  showSection("employeesBtn");
});