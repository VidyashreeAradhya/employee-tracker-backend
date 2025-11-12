const BASE_URL = "http://127.0.0.1:5000";

async function apiGet(endpoint) {
  const res = await fetch(`${BASE_URL}${endpoint}`);
  return res.json();
}

async function apiPost(endpoint, data) {
  const res = await fetch(`${BASE_URL}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

async function apiPut(endpoint, data) {
  const res = await fetch(`${BASE_URL}${endpoint}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

async function apiDelete(endpoint) {
  const res = await fetch(`${BASE_URL}${endpoint}`, { method: "DELETE" });
  return res.json();
}
