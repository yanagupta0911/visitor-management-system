function setAlert(elId, message, type = "error") {
  const el = document.getElementById(elId);
  el.textContent = message;
  el.className = `alert visible alert-${type}`;
}

function clearAlert(elId) {
  document.getElementById(elId).className = "alert";
}

document.getElementById("reset-btn").addEventListener("click", () => {
  document.getElementById("register-form").reset();
  clearAlert("register-alert");
});

document.getElementById("register-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  clearAlert("register-alert");

  const form = new FormData();
  form.append("name", document.getElementById("reg-name").value.trim());
  form.append("email", document.getElementById("reg-email").value.trim());
  form.append("phone", document.getElementById("reg-phone").value.trim());
  form.append("address", document.getElementById("reg-address").value.trim());
  form.append("authority", document.getElementById("reg-authority").value.trim());
  form.append("id_name", document.getElementById("reg-idname").value.trim());
  form.append("id_no", document.getElementById("reg-idno").value.trim());

  const btn = e.target.querySelector('button[type="submit"]');
  try {
    const data = await ui.withLoading(btn, "Registering…", () =>
      api.request("/visitors", { method: "POST", form, auth: true })
    );
    e.target.reset();
    document.getElementById("success-card").style.display = "block";
    document.getElementById("new-visitor-id").textContent = data.visitor_id;
    document.getElementById("success-card").scrollIntoView({ behavior: "smooth" });
    ui.toast("Visitor registered successfully.");
  } catch (err) {
    setAlert("register-alert", err.message);
  }
});
