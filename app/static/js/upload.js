/**
 * upload.js — Document upload and paste-text logic
 * Handles: drag-and-drop, file selection, file upload API,
 *          paste text API, character count, document list refresh.
 */
"use strict";

/* ── Refs ──────────────────────────────────────────────────── */
const dropZone      = document.getElementById("dropZone");
const fileInput     = document.getElementById("fileInput");
const filePreview   = document.getElementById("filePreview");
const fileNameEl    = document.getElementById("fileName");
const fileSizeEl    = document.getElementById("fileSize");
const removeFileBtn = document.getElementById("removeFileBtn");
const uploadBtn     = document.getElementById("uploadBtn");
const uploadProgress= document.getElementById("uploadProgress");
const uploadStatus  = document.getElementById("uploadStatus");
const pasteText     = document.getElementById("pasteText");
const charCount     = document.getElementById("charCount");
const pasteBtn      = document.getElementById("pasteBtn");
const clearPasteBtn = document.getElementById("clearPasteBtn");
const documentsList = document.getElementById("documentsList");
const docCountBadge = document.getElementById("docCountBadge");
const emptyDocsMsg  = document.getElementById("emptyDocsMsg");
const clearDocsBtn  = document.getElementById("clearDocsBtn");

let selectedFile = null;

/* ── File size formatter ─────────────────────────────────────── */
function fmtSize(bytes) {
  if (bytes < 1024)       return `${bytes} B`;
  if (bytes < 1048576)    return `${(bytes/1024).toFixed(1)} KB`;
  return `${(bytes/1048576).toFixed(1)} MB`;
}

/* ── File icon ───────────────────────────────────────────────── */
function fileIcon(name) {
  if (name.endsWith(".pdf"))  return "bi-file-earmark-pdf";
  if (name.endsWith(".docx")) return "bi-file-earmark-word";
  return "bi-file-earmark-text";
}

/* ── Select file ─────────────────────────────────────────────── */
function selectFile(file) {
  selectedFile = file;
  fileNameEl.textContent = file.name;
  fileSizeEl.textContent = fmtSize(file.size);
  filePreview.classList.remove("d-none");
  uploadBtn.disabled = false;
}

/* ── Clear file selection ────────────────────────────────────── */
function clearFile() {
  selectedFile = null;
  fileInput.value = "";
  filePreview.classList.add("d-none");
  uploadBtn.disabled = true;
}

/* ── Show status message ─────────────────────────────────────── */
function showStatus(message, type = "success") {
  uploadStatus.innerHTML = `
    <div class="alert alert-${type} rounded-4 d-flex align-items-center gap-2" role="alert">
      <i class="bi ${type === "success" ? "bi-check-circle-fill" : "bi-exclamation-triangle-fill"}"></i>
      <span>${message}</span>
    </div>`;
  uploadStatus.classList.remove("d-none");
  setTimeout(() => uploadStatus.classList.add("d-none"), 6000);
}

/* ── Add document card to list ───────────────────────────────── */
function addDocCard(doc) {
  // Remove empty message if present
  if (emptyDocsMsg) emptyDocsMsg.remove();
  if (clearDocsBtn) clearDocsBtn.classList.remove("d-none");

  const card = document.createElement("div");
  card.className = "doc-card glass-card rounded-4 p-3 mb-3 d-flex align-items-start gap-3 animate-fadein";
  card.dataset.docId = doc.id;
  card.innerHTML = `
    <div class="doc-icon bg-primary-subtle text-primary rounded-3 p-2 flex-shrink-0">
      <i class="bi ${fileIcon(doc.filename)} fs-4"></i>
    </div>
    <div class="flex-grow-1 overflow-hidden">
      <p class="fw-semibold mb-1 text-truncate">${doc.filename}</p>
      <div class="d-flex flex-wrap gap-2 mb-2">
        <span class="badge bg-body-tertiary text-muted border small"><i class="bi bi-file-word me-1"></i>${doc.word_count} words</span>
        <span class="badge bg-body-tertiary text-muted border small"><i class="bi bi-puzzle me-1"></i>${doc.chunk_count} chunks</span>
        <span class="badge bg-body-tertiary text-muted border small"><i class="bi bi-bar-chart me-1"></i>${doc.difficulty}</span>
        <span class="badge bg-body-tertiary text-muted border small"><i class="bi bi-clock me-1"></i>${doc.uploaded_at}</span>
      </div>
      <p class="text-muted small mb-0 text-truncate">${doc.preview}</p>
    </div>
    <a href="/chat/" class="btn btn-sm btn-primary rounded-pill flex-shrink-0">
      <i class="bi bi-chat-dots me-1"></i>Chat
    </a>`;
  documentsList.insertBefore(card, documentsList.firstChild);

  // Update badge
  const current = parseInt(docCountBadge?.textContent || "0");
  if (docCountBadge) docCountBadge.textContent = current + 1;
}

/* ── Upload file ─────────────────────────────────────────────── */
async function uploadFile() {
  if (!selectedFile) return;

  const spinner  = uploadBtn.querySelector(".upload-spinner");
  const iconEl   = uploadBtn.querySelector(".upload-icon");
  uploadBtn.disabled = true;
  spinner.classList.remove("d-none");
  iconEl.classList.add("d-none");
  uploadProgress.classList.remove("d-none");

  // Animate progress (fake progress while uploading)
  let prog = 0;
  const bar = uploadProgress.querySelector(".progress-bar");
  const interval = setInterval(() => {
    prog = Math.min(prog + 5, 85);
    bar.style.width = prog + "%";
  }, 150);

  const formData = new FormData();
  formData.append("document", selectedFile);

  try {
    const res  = await fetch("/upload/file", { method: "POST", body: formData });
    const data = await res.json();
    clearInterval(interval);
    bar.style.width = "100%";

    if (data.success) {
      showStatus(data.message, "success");
      addDocCard(data.document);
      clearFile();
    } else {
      showStatus(data.error || "Upload failed.", "danger");
    }
  } catch (err) {
    clearInterval(interval);
    showStatus("Network error: " + err.message, "danger");
  } finally {
    uploadBtn.disabled = false;
    spinner.classList.add("d-none");
    iconEl.classList.remove("d-none");
    setTimeout(() => { uploadProgress.classList.add("d-none"); bar.style.width = "0%"; }, 800);
  }
}

/* ── Process pasted text ─────────────────────────────────────── */
async function processPaste() {
  const text = pasteText.value.trim();
  if (!text) { showStatus("Please paste some text first.", "warning"); return; }

  const spinner = pasteBtn.querySelector(".paste-spinner");
  const iconEl  = pasteBtn.querySelector(".paste-icon");
  pasteBtn.disabled = true;
  spinner.classList.remove("d-none");
  iconEl.classList.add("d-none");

  const data = await apiFetch("/upload/paste", { method: "POST", body: JSON.stringify({ text }) });

  pasteBtn.disabled = false;
  spinner.classList.add("d-none");
  iconEl.classList.remove("d-none");

  if (data.success) {
    showStatus(data.message, "success");
    addDocCard(data.document);
    pasteText.value = "";
    charCount.textContent = "0";
  } else {
    showStatus(data.error || "Processing failed.", "danger");
  }
}

/* ── Event listeners ─────────────────────────────────────────── */
document.addEventListener("DOMContentLoaded", () => {
  // File input change
  fileInput.addEventListener("change", () => {
    if (fileInput.files[0]) selectFile(fileInput.files[0]);
  });

  // Remove file
  if (removeFileBtn) removeFileBtn.addEventListener("click", clearFile);

  // Upload button
  uploadBtn.addEventListener("click", uploadFile);

  // Paste button
  pasteBtn.addEventListener("click", processPaste);

  // Clear paste
  if (clearPasteBtn) clearPasteBtn.addEventListener("click", () => {
    pasteText.value = "";
    charCount.textContent = "0";
  });

  // Char count
  pasteText.addEventListener("input", () => {
    charCount.textContent = pasteText.value.length.toLocaleString();
  });

  // Clear all docs
  if (clearDocsBtn) clearDocsBtn.addEventListener("click", async () => {
    if (!confirm("Clear all indexed documents?")) return;
    await apiFetch("/upload/clear", { method: "POST" });
    documentsList.innerHTML = '<div class="text-center py-5 text-muted" id="emptyDocsMsg"><i class="bi bi-folder2-open fs-1 mb-3 d-block"></i><p>No documents indexed yet.</p></div>';
    if (docCountBadge) docCountBadge.textContent = "0";
    showToast("All documents cleared.", "info");
  });

  /* ── Drag & Drop ── */
  ["dragenter","dragover"].forEach(e => {
    dropZone.addEventListener(e, (ev) => { ev.preventDefault(); dropZone.classList.add("drag-over"); });
  });
  ["dragleave","drop"].forEach(e => {
    dropZone.addEventListener(e, (ev) => { ev.preventDefault(); dropZone.classList.remove("drag-over"); });
  });
  dropZone.addEventListener("drop", (ev) => {
    const files = ev.dataTransfer.files;
    if (files[0]) selectFile(files[0]);
  });
  dropZone.addEventListener("click", (e) => {
    if (e.target.tagName !== "BUTTON") fileInput.click();
  });
});
