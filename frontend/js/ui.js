const ui = {
  toast(message, type = "success") {
    let container = document.getElementById("toast-container");
    if (!container) {
      container = document.createElement("div");
      container.id = "toast-container";
      container.className = "toast-container";
      document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    requestAnimationFrame(() => toast.classList.add("visible"));

    setTimeout(() => {
      toast.classList.remove("visible");
      setTimeout(() => toast.remove(), 250);
    }, 3500);
  },

  confirmDialog(message, { confirmLabel = "Confirm", tone = "danger" } = {}) {
    return new Promise((resolve) => {
      const overlay = document.createElement("div");
      overlay.className = "modal-overlay";
      overlay.innerHTML = `
        <div class="modal-box">
          <div class="modal-message"></div>
          <div class="modal-actions">
            <button class="btn btn-outline" data-action="cancel">Cancel</button>
            <button class="btn ${tone === "danger" ? "btn-danger" : "btn-primary"}" data-action="confirm"></button>
          </div>
        </div>
      `;
      // Set via textContent (not template interpolation) so untrusted data
      // like a visitor's name can never be parsed as markup.
      overlay.querySelector(".modal-message").textContent = message;
      overlay.querySelector('[data-action="confirm"]').textContent = confirmLabel;

      document.body.appendChild(overlay);
      requestAnimationFrame(() => overlay.classList.add("visible"));

      function close(result) {
        overlay.classList.remove("visible");
        setTimeout(() => overlay.remove(), 200);
        resolve(result);
      }

      overlay.addEventListener("click", (e) => {
        if (e.target === overlay) close(false);
      });
      overlay.querySelector('[data-action="cancel"]').addEventListener("click", () => close(false));
      overlay.querySelector('[data-action="confirm"]').addEventListener("click", () => close(true));
    });
  },

  wirePasswordChecklist(inputEl, checklistEl) {
    if (!inputEl || !checklistEl) return;
    const rules = {
      length: (v) => v.length >= 8,
      lower: (v) => /[a-z]/.test(v),
      upper: (v) => /[A-Z]/.test(v),
      number: (v) => /\d/.test(v),
      special: (v) => /[@$!%*?&]/.test(v),
    };
    inputEl.addEventListener("input", () => {
      const value = inputEl.value;
      checklistEl.querySelectorAll("li[data-rule]").forEach((li) => {
        const rule = rules[li.dataset.rule];
        li.classList.toggle("met", !!rule && rule(value));
      });
    });
  },

  async withLoading(button, loadingLabel, fn) {
    const originalText = button.textContent;
    const originalDisabled = button.disabled;
    button.disabled = true;
    button.textContent = loadingLabel;
    try {
      return await fn();
    } finally {
      button.disabled = originalDisabled;
      button.textContent = originalText;
    }
  },
};
