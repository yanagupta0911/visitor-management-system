const alertBox = document.getElementById("alert");

function showAlert(message, type = "error") {
  alertBox.textContent = message;
  alertBox.className = `alert visible alert-${type}`;
}

function hideAlert() {
  alertBox.className = "alert";
}

// Redirect straight to the dashboard if we already hold a token.
if (api.getToken()) {
  window.location.href = "dashboard.html";
}

ui.wirePasswordChecklist(
  document.getElementById("signup-password"),
  document.getElementById("password-checklist")
);

document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".auth-form").forEach((f) => f.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(`${btn.dataset.tab}-form`).classList.add("active");
    hideAlert();
  });
});

document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  hideAlert();

  const form = new FormData();
  form.append("email", document.getElementById("login-email").value.trim());
  form.append("password", document.getElementById("login-password").value);

  const btn = e.target.querySelector('button[type="submit"]');
  try {
    const data = await ui.withLoading(btn, "Logging in…", () =>
      api.request("/auth/login", { method: "POST", form })
    );
    const email = document.getElementById("login-email").value.trim();
    api.saveSession(data.access_token, email);
    window.location.href = "dashboard.html";
  } catch (err) {
    showAlert(err.message);
  }
});

document.getElementById("signup-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  hideAlert();

  const form = new FormData();
  form.append("name", document.getElementById("signup-name").value.trim());
  form.append("email", document.getElementById("signup-email").value.trim());
  form.append("password", document.getElementById("signup-password").value);

  const btn = e.target.querySelector('button[type="submit"]');
  try {
    await ui.withLoading(btn, "Creating account…", () =>
      api.request("/auth/signup", { method: "POST", form })
    );
    ui.toast("Account created — you can log in now.");
    document.querySelector('[data-tab="login"]').click();
    document.getElementById("login-email").value = document.getElementById("signup-email").value;
  } catch (err) {
    showAlert(err.message);
  }
});
