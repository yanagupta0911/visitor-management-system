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

ui.wirePasswordChecklist(
  document.getElementById("new-password"),
  document.getElementById("password-checklist")
);

(async function loadMe() {
  try {
    const me = await api.request("/auth/me", { auth: true });
    document.getElementById("me-name").textContent = me.name;
    document.getElementById("me-email").textContent = me.email;
  } catch (err) {
    setAlert("password-alert", err.message);
  }
})();

document.getElementById("password-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  clearAlert("password-alert");

  const newPassword = document.getElementById("new-password").value;
  const confirmPassword = document.getElementById("confirm-password").value;

  if (newPassword !== confirmPassword) {
    setAlert("password-alert", "New password and confirmation do not match.");
    return;
  }

  const form = new FormData();
  form.append("current_password", document.getElementById("current-password").value);
  form.append("new_password", newPassword);

  const btn = e.target.querySelector('button[type="submit"]');
  try {
    await ui.withLoading(btn, "Updating…", () =>
      api.request("/auth/password", { method: "PUT", form, auth: true })
    );
    ui.toast("Password updated successfully.");
    e.target.reset();
  } catch (err) {
    setAlert("password-alert", err.message);
  }
});
