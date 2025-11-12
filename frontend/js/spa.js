// spa.js
document.addEventListener("DOMContentLoaded", () => {
  const sections = {
    employeesBtn: document.getElementById("employeesSection"),
    departmentsBtn: document.getElementById("departmentsSection"),
    projectsBtn: document.getElementById("projectsSection"),
    assignBtnNav: document.getElementById("assignSection"),
  };

  // Helper: hide all and show one
  function showSection(sectionId) {
    Object.values(sections).forEach(sec => sec.classList.remove("active"));
    sections[sectionId].classList.add("active");

    // load data for each section
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

  // Button event listeners
  document.getElementById("employeesBtn").addEventListener("click", () => showSection("employeesBtn"));
  document.getElementById("departmentsBtn").addEventListener("click", () => showSection("departmentsBtn"));
  document.getElementById("projectsBtn").addEventListener("click", () => showSection("projectsBtn"));
  document.getElementById("assignBtnNav").addEventListener("click", () => showSection("assignBtnNav"));

  // Load employees by default on first page load
  showSection("employeesBtn");
});
