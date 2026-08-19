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

function setAlert(elId, message, type = "error") {
  const el = document.getElementById(elId);
  el.textContent = message;
  el.className = `alert visible alert-${type}`;
  if (type === "success") {
    setTimeout(() => (el.className = "alert"), 4000);
  }
}

function clearAlert(elId) {
  document.getElementById(elId).className = "alert";
}

const visitorId = new URLSearchParams(window.location.search).get("id");

if (!visitorId) {
  setAlert("load-alert", "No visitor ID given.");
} else {
  loadVisitor();
}

async function renderPhotos(v) {
  const gallery = document.getElementById("photo-gallery");
  document.getElementById("photos-card").style.display = "block";

  const stages = [
    { key: "checkin", label: "Check-in photo", path: v.checkin_photo, by: v.checkin_by },
    { key: "checkout", label: "Check-out photo", path: v.checkout_photo, by: v.checkout_by },
  ];

  gallery.innerHTML = stages
    .map(
      (s) => `
      <div class="photo-frame">
        ${s.path ? `<img id="photo-${s.key}" alt="${escapeHtml(s.label)}" />` : `<div class="empty-state" style="padding:40px 12px">No ${s.label.toLowerCase()} yet</div>`}
        <div class="photo-caption">${escapeHtml(s.label)}${s.by ? ` · by ${escapeHtml(s.by)}` : ""}</div>
      </div>`
    )
    .join("");

  for (const s of stages) {
    if (!s.path) continue;
    const url = await api.fetchPhoto(`/visitors/${encodeURIComponent(v.visitor_id)}/photo/${s.key}`);
    const img = document.getElementById(`photo-${s.key}`);
    if (url && img) img.src = url;
  }
}

function fillEditForm(v) {
  document.getElementById("e-name").value = v.name;
  document.getElementById("e-email").value = v.email;
  document.getElementById("e-phone").value = v.phone;
  document.getElementById("e-authority").value = v.authority;
  document.getElementById("e-idname").value = v.id_name;
  document.getElementById("e-idno").value = v.id_no;
  document.getElementById("e-address").value = v.address;
}

async function loadVisitor() {
  try {
    const v = await api.request(`/visitors/${encodeURIComponent(visitorId)}`, { auth: true });

    document.getElementById("profile-card").style.display = "block";
    document.getElementById("edit-card").style.display = "block";
    document.getElementById("danger-card").style.display = "block";

    document.getElementById("avatar").textContent = initials(v.name);
    document.getElementById("profile-name").textContent = v.name;
    document.getElementById("profile-id").textContent = v.visitor_id;
    document.getElementById("profile-status").textContent = v.status;
    document.getElementById("profile-status").className = `badge ${statusBadgeClass(v.status)}`;

    document.getElementById("d-registered").textContent = v.registered_date
      ? `${v.registered_date} ${v.registered_time}${v.registered_by ? ` by ${v.registered_by}` : ""}`
      : "Not recorded";
    document.getElementById("d-email").textContent = v.email;
    document.getElementById("d-phone").textContent = v.phone;
    document.getElementById("d-authority").textContent = v.authority;
    document.getElementById("d-address").textContent = v.address;
    document.getElementById("d-idname").textContent = v.id_name;
    document.getElementById("d-idno").textContent = v.id_no;

    fillEditForm(v);
    await renderPhotos(v);
  } catch (err) {
    setAlert("load-alert", err.message);
  }
}

document.getElementById("edit-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  clearAlert("edit-alert");

  const form = new FormData();
  form.append("name", document.getElementById("e-name").value.trim());
  form.append("email", document.getElementById("e-email").value.trim());
  form.append("phone", document.getElementById("e-phone").value.trim());
  form.append("address", document.getElementById("e-address").value.trim());
  form.append("authority", document.getElementById("e-authority").value.trim());
  form.append("id_name", document.getElementById("e-idname").value.trim());
  form.append("id_no", document.getElementById("e-idno").value.trim());

  const btn = e.target.querySelector('button[type="submit"]');
  try {
    await ui.withLoading(btn, "Saving…", () =>
      api.request(`/visitors/${encodeURIComponent(visitorId)}`, { method: "PUT", form, auth: true })
    );
    ui.toast("Changes saved.");
    await loadVisitor();
  } catch (err) {
    setAlert("edit-alert", err.message);
  }
});

document.getElementById("print-btn").addEventListener("click", () => window.print());

document.getElementById("delete-btn").addEventListener("click", async () => {
  const ok = await ui.confirmDialog(`Delete visitor ${visitorId}? This cannot be undone.`, {
    confirmLabel: "Delete",
    tone: "danger",
  });
  if (!ok) return;

  const btn = document.getElementById("delete-btn");
  try {
    await ui.withLoading(btn, "Deleting…", () =>
      api.request(`/visitors/${encodeURIComponent(visitorId)}`, { method: "DELETE", auth: true })
    );
    ui.toast("Visitor deleted.");
    window.location.href = "visitors.html";
  } catch (err) {
    ui.toast(err.message, "error");
  }
});
