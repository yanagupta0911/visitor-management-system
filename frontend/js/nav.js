api.requireAuth();

(function renderNav() {
  const NAV_LINKS = [
    { href: "dashboard.html", label: "Dashboard" },
    { href: "register.html", label: "Register" },
    { href: "checkin.html", label: "Check In / Out" },
    { href: "visitors.html", label: "Visitors" },
    { href: "settings.html", label: "Settings" },
  ];

  const current = window.location.pathname.split("/").pop() || "dashboard.html";
  const container = document.getElementById("app-topbar");
  if (!container) return;

  container.innerHTML = `
    <div class="topbar-inner">
      <a href="dashboard.html" class="brand">
        <div class="brand-mark">VM</div>
        <div class="brand-name">Visitor Management</div>
      </a>
      <nav class="topnav">
        ${NAV_LINKS.map(
          (link) =>
            `<a href="${link.href}" class="${link.href === current ? "active" : ""}">${link.label}</a>`
        ).join("")}
      </nav>
      <div class="topbar-user">
        <span class="user-chip" id="user-chip"></span>
        <button id="logout-btn" class="btn btn-outline btn-sm">Log Out</button>
      </div>
    </div>
  `;

  document.getElementById("user-chip").textContent = api.getName() || "";
  document.getElementById("logout-btn").addEventListener("click", () => {
    api.clearSession();
    window.location.href = "index.html";
  });
})();
