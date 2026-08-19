const TOKEN_KEY = "vms_token";
const NAME_KEY = "vms_name";

const api = {
  saveSession(token, name) {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(NAME_KEY, name || "");
  },

  clearSession() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(NAME_KEY);
  },

  getToken() {
    return localStorage.getItem(TOKEN_KEY);
  },

  getName() {
    return localStorage.getItem(NAME_KEY);
  },

  requireAuth() {
    if (!this.getToken()) {
      window.location.href = "index.html";
    }
  },

  authHeaders() {
    const token = this.getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  },

  async request(path, { method = "GET", form, auth = false } = {}) {
    const headers = auth ? this.authHeaders() : {};
    const response = await fetch(path, { method, headers, body: form });
    let data = null;
    try {
      data = await response.json();
    } catch (err) {
      data = null;
    }

    if (!response.ok) {
      const message = (data && data.detail) || `Request failed (${response.status})`;
      if (response.status === 401 && auth) {
        this.clearSession();
        window.location.href = "index.html";
      }
      throw new Error(typeof message === "string" ? message : JSON.stringify(message));
    }

    return data;
  },

  async fetchPhoto(url) {
    const response = await fetch(url, { headers: this.authHeaders() });
    if (!response.ok) return null;
    const blob = await response.blob();
    return URL.createObjectURL(blob);
  },
};
