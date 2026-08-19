function parseDateTime(dateStr, timeStr) {
  if (!dateStr) return null;
  const [day, month, year] = dateStr.split("-").map(Number);
  const [h, m, s] = (timeStr || "00:00:00").split(":").map(Number);
  return new Date(year, month - 1, day, h, m, s || 0);
}

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

function renderStats(visitors) {
  const total = visitors.length;
  const checkedIn = visitors.filter((v) => v.status === "Checked In").length;
  const checkedOut = visitors.filter((v) => v.status === "Checked Out").length;
  const registered = visitors.filter((v) => v.status === "Registered").length;

  const tiles = [
    ["Total Visitors", total],
    ["Checked In", checkedIn],
    ["Checked Out", checkedOut],
    ["Awaiting Check-In", registered],
  ];

  document.getElementById("stats").innerHTML = tiles
    .map(
      ([label, value]) => `
      <div class="stat-tile">
        <div class="stat-value">${value}</div>
        <div class="stat-label">${label}</div>
      </div>`
    )
    .join("");
}

function renderActivity(visitors) {
  const events = [];

  visitors.forEach((v) => {
    if (v.registered_date) {
      events.push({ visitor: v, type: "registered", at: parseDateTime(v.registered_date, v.registered_time), date: v.registered_date, time: v.registered_time });
    }
    if (v.checkin_date) {
      events.push({ visitor: v, type: "checked in", at: parseDateTime(v.checkin_date, v.checkin_time), date: v.checkin_date, time: v.checkin_time });
    }
    if (v.checkout_date) {
      events.push({ visitor: v, type: "checked out", at: parseDateTime(v.checkout_date, v.checkout_time), date: v.checkout_date, time: v.checkout_time });
    }
  });

  events.sort((a, b) => (b.at?.getTime() || 0) - (a.at?.getTime() || 0));

  const recent = events.slice(0, 8);
  const container = document.getElementById("activity");
  const emptyState = document.getElementById("activity-empty");

  if (recent.length === 0) {
    container.innerHTML = "";
    emptyState.style.display = "block";
    return;
  }
  emptyState.style.display = "none";

  container.innerHTML = recent
    .map(
      (e) => `
      <div class="timeline-item">
        <div class="timeline-dot"></div>
        <div class="timeline-body">
          <strong>${escapeHtml(e.visitor.name)} <span class="badge ${statusBadgeClass(e.visitor.status)}" style="margin-left:6px">${escapeHtml(e.type)}</span></strong>
          <span>${escapeHtml(e.visitor.visitor_id)} · ${escapeHtml(e.date)} at ${escapeHtml(e.time)}</span>
        </div>
      </div>`
    )
    .join("");
}

(async function init() {
  try {
    const visitors = await api.request("/visitors", { auth: true });
    renderStats(visitors);
    renderActivity(visitors);
  } catch (err) {
    document.getElementById("stats").innerHTML = `<div class="alert visible alert-error">${err.message}</div>`;
  }
})();
