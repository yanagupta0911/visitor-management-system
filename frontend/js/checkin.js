function setAlert(elId, message, type = "error") {
  const el = document.getElementById(elId);
  el.textContent = message;
  el.className = `alert visible alert-${type}`;
}

function clearAlert(elId) {
  document.getElementById(elId).className = "alert";
}

function statusBadgeClass(status) {
  if (status === "Checked In") return "badge-checkedin";
  if (status === "Checked Out") return "badge-checkedout";
  return "badge-registered";
}

function initials(name) {
  return (name || "?")
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((p) => p[0].toUpperCase())
    .join("");
}

function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = value ?? "";
  return div.innerHTML;
}

let currentVisitor = null;

function renderVisitor(v) {
  currentVisitor = v;
  document.getElementById("visit-card").style.display = "block";

  document.getElementById("visitor-preview").innerHTML = `
    <div class="avatar-sm">${escapeHtml(initials(v.name))}</div>
    <div>
      <div><strong>${escapeHtml(v.name)}</strong> <span class="badge ${statusBadgeClass(v.status)}">${escapeHtml(v.status)}</span></div>
      <div class="card-subtitle">${escapeHtml(v.visitor_id)} · ${escapeHtml(v.email)} · Host: ${escapeHtml(v.authority)}</div>
    </div>
  `;

  const canCheckin = v.status !== "Checked In";
  const canCheckout = v.status === "Checked In";

  const checkinBtn = document.getElementById("checkin-btn");
  const checkoutBtn = document.getElementById("checkout-btn");
  checkinBtn.disabled = !canCheckin;
  checkoutBtn.disabled = !canCheckout;
  checkinBtn.style.opacity = canCheckin ? 1 : 0.5;
  checkoutBtn.style.opacity = canCheckout ? 1 : 0.5;
}

document.getElementById("visit-photo").addEventListener("change", (e) => {
  const file = e.target.files[0];
  const frame = document.getElementById("photo-preview-frame");
  const img = document.getElementById("photo-preview");

  if (!file) {
    frame.classList.remove("visible");
    img.src = "";
    return;
  }

  img.src = URL.createObjectURL(file);
  frame.classList.add("visible");
});

document.getElementById("find-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  clearAlert("find-alert");
  document.getElementById("visit-card").style.display = "none";

  const visitorId = document.getElementById("find-id").value.trim();
  const btn = e.target.querySelector('button[type="submit"]');
  try {
    const visitor = await ui.withLoading(btn, "Finding…", () =>
      api.request(`/visitors/${encodeURIComponent(visitorId)}`, { auth: true })
    );
    renderVisitor(visitor);
  } catch (err) {
    setAlert("find-alert", err.message);
  }
});

document.getElementById("visit-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  clearAlert("visit-alert");

  if (!currentVisitor) return;

  const action = e.submitter ? e.submitter.dataset.action : "checkin";
  const photoInput = document.getElementById("visit-photo");

  if (!photoInput.files[0]) {
    setAlert("visit-alert", "Please choose a photo first.");
    return;
  }

  const form = new FormData();
  form.append("photo", photoInput.files[0]);

  const visitorId = currentVisitor.visitor_id;
  const path =
    action === "checkout"
      ? `/visitors/${encodeURIComponent(visitorId)}/checkout`
      : `/visitors/${encodeURIComponent(visitorId)}/checkin`;
  const method = action === "checkout" ? "PUT" : "POST";

  try {
    const updated = await ui.withLoading(
      e.submitter,
      action === "checkout" ? "Checking out…" : "Checking in…",
      () => api.request(path, { method, form, auth: true })
    );
    ui.toast(`${updated.name} ${action === "checkout" ? "checked out" : "checked in"} successfully.`);
    photoInput.value = "";
    document.getElementById("photo-preview-frame").classList.remove("visible");
    renderVisitor(updated);
  } catch (err) {
    setAlert("visit-alert", err.message);
  }
});
