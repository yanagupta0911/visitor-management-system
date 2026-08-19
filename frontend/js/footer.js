(function renderFooter() {
  const el = document.getElementById("app-footer");
  if (!el) return;
  el.textContent = `© ${new Date().getFullYear()} Visitor Management System · v1.0.0`;
})();
