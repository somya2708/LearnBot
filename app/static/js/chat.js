/**
 * chat.js — Chat interface logic
 * Handles: sending messages, markdown rendering, settings sync,
 *          quick actions, auto-resize textarea, pending questions from history.
 */
"use strict";

/* ── Refs ──────────────────────────────────────────────────── */
const chatMessages   = document.getElementById("chatMessages");
const chatInput      = document.getElementById("chatInput");
const sendBtn        = document.getElementById("sendBtn");
const clearChatBtn   = document.getElementById("clearChatBtn");
const typingIndicator= document.getElementById("typingIndicator");
const proficiencyBadge = document.getElementById("proficiencyBadge");
const subjectBadge   = document.getElementById("subjectBadge");
const ragIndicator   = document.getElementById("ragIndicator");

/* ── Current settings (synced with sidebar) ─────────────────── */
let currentProficiency = document.querySelector('input[name="proficiency"]:checked')?.value || "Beginner";
let currentSubject     = document.getElementById("subjectSelect")?.value || "General / Other";

/* ── Marked.js config ────────────────────────────────────────── */
if (typeof marked !== "undefined") {
  marked.setOptions({ breaks: true, gfm: true });
}

function renderMarkdown(text) {
  if (typeof marked !== "undefined") {
    return marked.parse(text);
  }
  // Fallback: basic escaping
  return text.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/\n/g,"<br/>");
}

/* ── Scroll to bottom ────────────────────────────────────────── */
function scrollBottom() {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

/* ── Append message bubble ───────────────────────────────────── */
function appendMessage(role, content, timestamp) {
  const row  = document.createElement("div");
  row.className = `msg-row ${role}`;

  const bubble = document.createElement("div");
  bubble.className = `msg-bubble ${role === "user" ? "user-bubble" : "bot-bubble"} p-3 rounded-4`;

  if (role === "assistant") {
    const md = document.createElement("div");
    md.className = "markdown-content";
    md.innerHTML = renderMarkdown(content);
    bubble.appendChild(md);
  } else {
    bubble.textContent = content;
  }

  // Timestamp
  const ts = document.createElement("div");
  ts.className = "msg-time text-end mt-1";
  ts.innerHTML = `<small class="text-muted">${timestamp || ""}</small>`;
  bubble.appendChild(ts);

  row.appendChild(bubble);
  chatMessages.appendChild(row);
  scrollBottom();
}

/* ── Send message ────────────────────────────────────────────── */
async function sendMessage() {
  const text = chatInput.value.trim();
  if (!text) return;

  chatInput.value = "";
  autoResize();

  appendMessage("user", text, new Date().toLocaleTimeString([], {hour:"2-digit",minute:"2-digit"}));
  sendBtn.disabled = true;
  chatInput.disabled = true;
  typingIndicator.style.display = "";    // show
  scrollBottom();

  const data = await apiFetch("/chat/send", {
    method: "POST",
    body: JSON.stringify({ message: text, proficiency: currentProficiency, subject: currentSubject }),
  });

  typingIndicator.style.display = "none !important";
  typingIndicator.style.setProperty("display", "none", "important");
  sendBtn.disabled = false;
  chatInput.disabled = false;
  chatInput.focus();

  if (data.error) {
    appendMessage("assistant", `⚠️ ${data.error}`, "");
  } else {
    appendMessage("assistant", data.reply || "No response received.", data.timestamp || "");
  }
  scrollBottom();
}

/* ── Auto-resize textarea ────────────────────────────────────── */
function autoResize() {
  chatInput.style.height = "auto";
  chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + "px";
}

/* ── Settings sidebar sync ───────────────────────────────────── */
function syncSettings() {
  // Proficiency (desktop)
  const checkedP = document.querySelector('input[name="proficiency"]:checked');
  if (checkedP) currentProficiency = checkedP.value;

  // Proficiency (mobile)
  const checkedPM = document.querySelector('input[name="proficiencyMobile"]:checked');
  if (checkedPM) currentProficiency = checkedPM.value;

  // Subject
  const sel = document.getElementById("subjectSelect");
  if (sel) currentSubject = sel.value;

  const selM = document.getElementById("subjectSelectMobile");
  if (selM) currentSubject = selM.value;

  // Update header badges
  if (proficiencyBadge) proficiencyBadge.textContent = currentProficiency;
  if (subjectBadge) subjectBadge.textContent = currentSubject;

  // Persist to server
  apiFetch("/chat/settings", { method: "POST", body: JSON.stringify({ proficiency: currentProficiency, subject: currentSubject }) });
}

/* ── Event listeners ─────────────────────────────────────────── */
document.addEventListener("DOMContentLoaded", () => {
  scrollBottom();

  // Send on button click
  sendBtn.addEventListener("click", sendMessage);

  // Send on Enter (not Shift+Enter)
  chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  });

  // Auto-resize
  chatInput.addEventListener("input", autoResize);

  // Clear chat
  if (clearChatBtn) clearChatBtn.addEventListener("click", async () => {
    if (!confirm("Clear this chat session?")) return;
    await apiFetch("/chat/clear", { method: "POST" });
    chatMessages.innerHTML = "";
    showToast("Chat cleared.", "info");
  });

  // Quick action buttons
  document.querySelectorAll(".quick-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      chatInput.value = btn.dataset.msg;
      autoResize();
      chatInput.focus();
    });
  });

  // Proficiency radio change
  document.querySelectorAll('input[name="proficiency"], input[name="proficiencyMobile"]')
    .forEach(el => el.addEventListener("change", syncSettings));

  // Subject select change
  ["subjectSelect", "subjectSelectMobile"].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener("change", syncSettings);
  });

  // Load pending question from history page
  const pending = sessionStorage.getItem("pendingQuestion");
  if (pending) {
    sessionStorage.removeItem("pendingQuestion");
    chatInput.value = pending;
    autoResize();
    chatInput.focus();
  }
});
