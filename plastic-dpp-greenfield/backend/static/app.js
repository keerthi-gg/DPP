const API_BASE = "";

const roleSelect = document.getElementById("role-select");
const userIdInput = document.getElementById("user-id");
const healthBadge = document.getElementById("health-badge");
const dppOptions = document.getElementById("dpp-id-options");

function loadIdentity() {
  const role = localStorage.getItem("dpp.role") || "manufacturer";
  const userId = localStorage.getItem("dpp.userId") || "mfg-1";
  roleSelect.value = role;
  userIdInput.value = userId;
}

function saveIdentity() {
  localStorage.setItem("dpp.role", roleSelect.value);
  localStorage.setItem("dpp.userId", userIdInput.value);
}

roleSelect.addEventListener("change", saveIdentity);
userIdInput.addEventListener("change", saveIdentity);

function authHeaders() {
  return {
    "X-Role": roleSelect.value,
    "X-User-Id": userIdInput.value || "anonymous",
  };
}

async function api(path, { method = "GET", body } = {}) {
  const response = await fetch(API_BASE + path, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  const text = await response.text();
  const data = text ? JSON.parse(text) : null;
  if (!response.ok) {
    const detail = data && data.detail ? data.detail : response.statusText;
    const error = new Error(`${response.status} ${detail}`);
    error.status = response.status;
    error.data = data;
    throw error;
  }
  return data;
}

function showOutput(elementId, value, isError = false) {
  const el = document.getElementById(elementId);
  el.textContent = typeof value === "string" ? value : JSON.stringify(value, null, 2);
  el.classList.toggle("error", isError);
}

async function checkHealth() {
  try {
    await api("/health");
    healthBadge.textContent = "API online";
    healthBadge.className = "badge ok";
  } catch (err) {
    healthBadge.textContent = "API offline";
    healthBadge.className = "badge down";
  }
}

async function refreshProducts() {
  try {
    const data = await api("/products");
    const tbody = document.querySelector("#products-table tbody");
    tbody.innerHTML = "";
    dppOptions.innerHTML = "";
    data.products.forEach((p) => {
      const row = document.createElement("tr");
      row.innerHTML = `<td>${p.dpp_id}</td><td>${p.product_type}</td><td>${p.current_state}</td><td>${p.qr_code_ref}</td><td>${p.manufacturer_id}</td>`;
      tbody.appendChild(row);

      const option = document.createElement("option");
      option.value = p.dpp_id;
      dppOptions.appendChild(option);
    });
  } catch (err) {
    showOutput("lookup-output", err.message, true);
  }
}

document.getElementById("register-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = new FormData(e.target);
  try {
    const product = await api("/products", {
      method: "POST",
      body: {
        product_type: form.get("product_type"),
        material_summary: form.get("material_summary"),
        manufacture_date: form.get("manufacture_date"),
      },
    });
    showOutput("register-output", product);
    e.target.reset();
    refreshProducts();
  } catch (err) {
    showOutput("register-output", err.message, true);
  }
});

document.getElementById("refresh-products").addEventListener("click", refreshProducts);

document.getElementById("lookup-by-id").addEventListener("click", async () => {
  const dppId = document.getElementById("lookup-dpp-id").value.trim();
  if (!dppId) return;
  try {
    const product = await api(`/products/${encodeURIComponent(dppId)}`);
    showOutput("lookup-output", product);
  } catch (err) {
    showOutput("lookup-output", err.message, true);
  }
});

document.getElementById("lookup-by-qr").addEventListener("click", async () => {
  const qr = document.getElementById("lookup-qr").value.trim();
  if (!qr) return;
  try {
    const product = await api(`/products/lookup?qr_code=${encodeURIComponent(qr)}`);
    showOutput("lookup-output", product);
  } catch (err) {
    showOutput("lookup-output", err.message, true);
  }
});

document.getElementById("transaction-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = new FormData(e.target);
  const value = form.get("value");
  try {
    const txn = await api("/transactions", {
      method: "POST",
      body: { value: value ? Number(value) : null },
    });
    showOutput("transaction-output", txn);
    e.target.reset();
  } catch (err) {
    showOutput("transaction-output", err.message, true);
  }
});

document.getElementById("lifecycle-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = new FormData(e.target);
  const dppId = form.get("dpp_id").trim();
  try {
    const event = await api(`/products/${encodeURIComponent(dppId)}/lifecycle-events`, {
      method: "POST",
      body: {
        target_state: form.get("target_state"),
        transaction_id: form.get("transaction_id").trim(),
      },
    });
    showOutput("lifecycle-output", event);
    refreshProducts();
  } catch (err) {
    showOutput("lifecycle-output", err.message, true);
  }
});

document.getElementById("history-fetch").addEventListener("click", async () => {
  const dppId = document.getElementById("history-dpp-id").value.trim();
  if (!dppId) return;
  try {
    const data = await api(`/products/${encodeURIComponent(dppId)}/history`);
    const tbody = document.querySelector("#history-table tbody");
    tbody.innerHTML = "";
    data.events.forEach((ev) => {
      const row = document.createElement("tr");
      row.innerHTML = `<td>${ev.timestamp}</td><td>${ev.prior_state}</td><td>${ev.new_state}</td><td>${ev.actor_id}</td><td>${ev.actor_role}</td><td>${ev.transaction_id}</td>`;
      tbody.appendChild(row);
    });
  } catch (err) {
    alert(err.message);
  }
});

document.getElementById("report-fetch").addEventListener("click", async () => {
  try {
    const report = await api("/regulator/report");
    showOutput("report-output", report);
  } catch (err) {
    showOutput("report-output", err.message, true);
  }
});

loadIdentity();
checkHealth();
refreshProducts();
