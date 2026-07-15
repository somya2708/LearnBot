/**
 * settings.js — Settings page logic
 * Handles: save preferences, test connection, danger zone actions.
 */
"use strict";

document.addEventListener("DOMContentLoaded", () => {

  /* ── Save Settings ─────────────────────────────────────────── */
  const saveBtn = document.getElementById("saveSettingsBtn");
  if (saveBtn) saveBtn.addEventListener("click", async () => {
    const proficiency = document.querySelector('input[name="settingsProficiency"]:checked')?.value;
    const subject     = document.getElementById("settingsSubject")?.value;

    const data = await apiFetch("/settings/save", {
      method: "POST",
      body: JSON.stringify({ proficiency, subject }),
    });

    if (data.ok) {
      showToast("✅ Preferences saved!", "success");
    } else {
      showToast("❌ " + (data.message || "Failed to save."), "error");
    }
  });

  /* ── Test Connection ───────────────────────────────────────── */
  const testBtn   = document.getElementById("testConnectionBtn");
  const spinner   = document.getElementById("connSpinner");
  const icon      = testBtn?.querySelector(".conn-icon");
  const resultDiv = document.getElementById("connectionResult");

  if (testBtn) testBtn.addEventListener("click", async () => {
    testBtn.disabled = true;
    spinner.classList.remove("d-none");
    if (icon) icon.classList.add("d-none");
    resultDiv.classList.add("d-none");

    const data = await apiFetch("/settings/test-connection");

    testBtn.disabled = false;
    spinner.classList.add("d-none");
    if (icon) icon.classList.remove("d-none");

    resultDiv.classList.remove("d-none");
    resultDiv.innerHTML = `
      <div class="alert alert-${data.ok ? "success" : "danger"} rounded-3 d-flex align-items-center gap-2 small">
        <i class="bi ${data.ok ? "bi-check-circle-fill" : "bi-exclamation-triangle-fill"}"></i>
        <span>${data.message}</span>
      </div>`;
  });

  /* ── Danger Zone ───────────────────────────────────────────── */
  document.getElementById("clearHistoryDangerBtn")?.addEventListener("click", async () => {
    if (!confirm("Clear all learning history? This cannot be undone.")) return;
    await apiFetch("/history/clear", { method: "POST" });
    showToast("Learning history cleared.", "info");
  });

  document.getElementById("clearDocsDangerBtn")?.addEventListener("click", async () => {
    if (!confirm("Clear all indexed documents? This cannot be undone.")) return;
    await apiFetch("/upload/clear", { method: "POST" });
    showToast("All documents cleared.", "info");
  });
});
