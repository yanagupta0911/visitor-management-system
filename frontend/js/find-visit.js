function statusBadgeClass(status) {
  if (status === "Checked In") return "badge-checkedin";
  if (status === "Checked Out") return "badge-checkedout";
  return "badge-registered";
}

function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = value ?? "";
  return div.innerHTML;
}

const alertBox = document.getElementById("alert");

function showAlert(message) {
  alertBox.textContent = message;
  alertBox.className = "alert visible alert-error";
}

function hideAlert() {
  alertBox.className = "alert";
}

document.getElementById("lookup-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  hideAlert();
  const resultEl = document.getElementById("result");
  resultEl.innerHTML = "";

  const visitorId = document.getElementById("lookup-id").value.trim();
  const email = document.getElementById("lookup-email").value.trim();

  try {
    const v = await api.request(
      `/visitors/lookup?visitor_id=${encodeURIComponent(visitorId)}&email=${encodeURIComponent(email)}`
    );
    resultEl.innerHTML = `
      <div><strong>${escapeHtml(v.name)}</strong> — <span class="badge ${statusBadgeClass(v.status)}">${escapeHtml(v.status)}</span></div>
      <div class="card-subtitle" style="margin-top:6px">Host: ${escapeHtml(v.authority)}</div>
      ${v.checkin_date ? `<div class="card-subtitle">Checked in: ${escapeHtml(v.checkin_date)} ${escapeHtml(v.checkin_time)}</div>` : ""}
      ${v.checkout_date ? `<div class="card-subtitle">Checked out: ${escapeHtml(v.checkout_date)} ${escapeHtml(v.checkout_time)}</div>` : ""}
    `;
  } catch (err) {
    showAlert(err.message);
  }
});
