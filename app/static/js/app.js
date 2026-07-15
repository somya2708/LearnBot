/**
 * app.js — Global utilities (dark mode, navbar, shared helpers)
 */
"use strict";

/* ── Dark Mode ──────────────────────────────────────────────── */
const HTML      = document.documentElement;
const DARK_KEY  = "lb_dark";

function applyTheme(dark) {
  HTML.setAttribute("data-bs-theme", dark ? "dark" : "light");
  const icon = document.getElementById("darkIcon");
  if (icon) icon.className = dark ? "bi bi-sun" : "bi bi-moon-stars";
  localStorage.setItem(DARK_KEY, dark ? "1" : "0");
}

document.addEventListener("DOMContentLoaded", () => {
  // Restore saved theme
  const saved = localStorage.getItem(DARK_KEY);
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  applyTheme(saved !== null ? saved === "1" : prefersDark);

  // Toggle button
  const toggle = document.getElementById("darkToggle");
  if (toggle) toggle.addEventListener("click", () => {
    applyTheme(HTML.getAttribute("data-bs-theme") !== "dark");
  });
});

/* ── Toast helper ────────────────────────────────────────────── */
window.showToast = function(message, type = "success") {
  const wrapper = document.getElementById("toastWrapper") || (() => {
    const el = document.createElement("div");
    el.id = "toastWrapper";
    el.style.cssText = "position:fixed;bottom:1.5rem;right:1.5rem;z-index:9999;display:flex;flex-direction:column;gap:.5rem;";
    document.body.appendChild(el);
    return el;
  })();

  const toast = document.createElement("div");
  const colors = { success: "#198754", error: "#dc3545", info: "#0dcaf0", warning: "#ffc107" };
  toast.style.cssText = `
    background:${colors[type] || colors.info};color:#fff;
    padding:.65rem 1.2rem;border-radius:.75rem;
    box-shadow:0 4px 16px rgba(0,0,0,.2);
    font-size:.88rem;font-weight:500;
    animation:fadeSlideIn .3s ease;
    max-width:340px;
  `;
  toast.textContent = message;
  wrapper.appendChild(toast);
  setTimeout(() => { toast.style.opacity = "0"; toast.style.transition = "opacity .3s"; setTimeout(() => toast.remove(), 300); }, 3500);
};

/* ── Fetch wrapper ───────────────────────────────────────────── */
window.apiFetch = async function(url, options = {}) {
  try {
    const res = await fetch(url, {
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
      ...options,
    });
    return await res.json();
  } catch (err) {
    console.error("apiFetch error:", err);
    return { error: err.message };
  }
};
