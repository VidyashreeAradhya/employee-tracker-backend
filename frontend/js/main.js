async function loadComponent(name) {
  const content = document.getElementById("content");
  const res = await fetch(`components/${name}.html`);
  content.innerHTML = await res.text();

  // Load the corresponding JS file dynamically
  const script = document.createElement("script");
  script.src = `js/${name}.js`;
  document.body.appendChild(script);
}

document.getElementById("homeBtn").addEventListener("click", () => {
  loadComponent("home"); // assuming your home page file is `home.html`
});
