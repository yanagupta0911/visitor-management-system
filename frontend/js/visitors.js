const PAGE_SIZE = 8;

let visitors = [];
let currentPage = 1;
let sortKey = null;
let sortDir = 1;

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

function parseDateTime(dateStr, timeStr) {
  if (!dateStr) return null;
  const [day, month, year] = dateStr.split("-").map(Number);
  const [h, m, s] = (timeStr || "00:00:00").split(":").map(Number);
  return new Date(year, month - 1, day, h, m, s || 0);
}

function getFiltered() {
  const search = document.getElementById("search-input").value.toLowerCase();
  const status = document.getElementById("status-filter").value;

  const filtered = visitors.filter((v) => {
    const haystack = `${v.visitor_id} ${v.name} ${v.email}`.toLowerCase();
    const matchesSearch = haystack.includes(search);
    const matchesStatus = !status || v.status === status;
    return matchesSearch && matchesStatus;
  });

  if (!sortKey) return filtered;

  const isDateCol = sortKey === "checkin_date" || sortKey === "checkout_date";
  const timeKey = sortKey === "checkin_date" ? "checkin_time" : "checkout_time";

  return [...filtered].sort((a, b) => {
    let cmp;
    if (isDateCol) {
      const da = parseDateTime(a[sortKey], a[timeKey]);
      const db = parseDateTime(b[sortKey], b[timeKey]);
      cmp = (da?.getTime() || 0) - (db?.getTime() || 0);
    } else {
      cmp = String(a[sortKey] ?? "").localeCompare(String(b[sortKey] ?? ""));
    }
    return cmp * sortDir;
  });
}

function updateSortHeaders() {
  document.querySelectorAll("th.sortable").forEach((th) => {
    th.classList.remove("sort-active");
    const arrow = th.querySelector(".sort-arrow");
    if (arrow) arrow.remove();
    if (th.dataset.sort === sortKey) {
      th.classList.add("sort-active");
      const span = document.createElement("span");
      span.className = "sort-arrow";
      span.textContent = sortDir === 1 ? "▲" : "▼";
      th.appendChild(span);
    }
  });
}

document.querySelectorAll("th.sortable").forEach((th) => {
  th.addEventListener("click", () => {
    if (sortKey === th.dataset.sort) {
      sortDir *= -1;
    } else {
      sortKey = th.dataset.sort;
      sortDir = 1;
    }
    updateSortHeaders();
    render();
  });
});

function toCsvValue(value) {
  const str = String(value ?? "");
  return /[",\n]/.test(str) ? `"${str.replace(/"/g, '""')}"` : str;
}

function exportCsv() {
  const rows = getFiltered();
  const headers = [
    "visitor_id",
    "name",
    "email",
    "phone",
    "status",
    "registered_date",
    "registered_time",
    "checkin_date",
    "checkin_time",
    "checkout_date",
    "checkout_time",
  ];

  const lines = [headers.join(",")];
  rows.forEach((v) => {
    lines.push(headers.map((h) => toCsvValue(v[h])).join(","));
  });

  const blob = new Blob([lines.join("\n")], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `visitors_${new Date().toISOString().slice(0, 10)}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

function renderPagination(totalItems) {
  const totalPages = Math.max(1, Math.ceil(totalItems / PAGE_SIZE));
  currentPage = Math.min(currentPage, totalPages);

  const pagination = document.getElementById("pagination");
  if (totalPages <= 1) {
    pagination.innerHTML = "";
    return;
  }

  let buttons = `<button ${currentPage === 1 ? "disabled" : ""} data-page="${currentPage - 1}">‹</button>`;
  for (let p = 1; p <= totalPages; p++) {
    buttons += `<button class="${p === currentPage ? "active" : ""}" data-page="${p}">${p}</button>`;
  }
  buttons += `<button ${currentPage === totalPages ? "disabled" : ""} data-page="${currentPage + 1}">›</button>`;

  pagination.innerHTML = buttons;
  pagination.querySelectorAll("button[data-page]").forEach((btn) => {
    btn.addEventListener("click", () => {
      currentPage = Number(btn.dataset.page);
      render();
    });
  });
}

function render() {
  const filtered = getFiltered();
  const tbody = document.getElementById("visitors-body");
  const emptyState = document.getElementById("empty-state");

  if (filtered.length === 0) {
    tbody.innerHTML = "";
    emptyState.style.display = "block";
    document.getElementById("pagination").innerHTML = "";
    return;
  }
  emptyState.style.display = "none";

  const start = (currentPage - 1) * PAGE_SIZE;
  const pageItems = filtered.slice(start, start + PAGE_SIZE);

  tbody.innerHTML = pageItems
    .map(
      (v) => `
      <tr>
        <td><img class="thumb" data-thumb="${escapeHtml(v.visitor_id)}" alt="" /></td>
        <td class="mono">${escapeHtml(v.visitor_id)}</td>
        <td>${escapeHtml(v.name)}</td>
        <td>${escapeHtml(v.email)}<br /><span class="card-subtitle">${escapeHtml(v.phone)}</span></td>
        <td><span class="badge ${statusBadgeClass(v.status)}">${escapeHtml(v.status)}</span></td>
        <td>${v.checkin_date ? `${escapeHtml(v.checkin_date)} ${escapeHtml(v.checkin_time)}` : "—"}</td>
        <td>${v.checkout_date ? `${escapeHtml(v.checkout_date)} ${escapeHtml(v.checkout_time)}` : "—"}</td>
        <td>
          <a class="btn btn-outline btn-sm" href="visitor.html?id=${encodeURIComponent(v.visitor_id)}">View</a>
        </td>
      </tr>`
    )
    .join("");

  pageItems.forEach(async (v) => {
    const stage = v.checkout_photo ? "checkout" : v.checkin_photo ? "checkin" : null;
    if (!stage) return;
    const img = document.querySelector(`[data-thumb="${CSS.escape(v.visitor_id)}"]`);
    if (!img) return;
    const url = await api.fetchPhoto(`/visitors/${encodeURIComponent(v.visitor_id)}/photo/${stage}`);
    if (url) img.src = url;
  });

  renderPagination(filtered.length);
}

async function loadVisitors() {
  try {
    visitors = await api.request("/visitors", { auth: true });
    render();
  } catch (err) {
    document.getElementById("empty-state").textContent = err.message;
    document.getElementById("empty-state").style.display = "block";
  }
}

document.getElementById("refresh-btn").addEventListener("click", loadVisitors);
document.getElementById("export-btn").addEventListener("click", () => {
  if (getFiltered().length === 0) {
    ui.toast("Nothing to export.", "error");
    return;
  }
  exportCsv();
  ui.toast("CSV export started.");
});
document.getElementById("search-input").addEventListener("input", () => {
  currentPage = 1;
  render();
});
document.getElementById("status-filter").addEventListener("change", () => {
  currentPage = 1;
  render();
});

loadVisitors();
