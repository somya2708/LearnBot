"""
rag_engine.py
─────────────
Retrieval-Augmented Generation (RAG) pipeline.

Responsibilities
────────────────
1. Parse uploaded PDF / DOCX / TXT documents into plain text.
2. Split text into overlapping chunks.
3. Embed chunks with sentence-transformers.
4. Store & search a FAISS index per session.
5. Return the most relevant chunks for a given query.
"""

import os
import re
import io
import uuid
import pickle
import logging
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

# ── Optional heavy imports (graceful degradation) ─────────────────
try:
    import faiss                                   # noqa: F401
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logger.warning("faiss-cpu not installed — RAG disabled, falling back to keyword search.")

try:
    from sentence_transformers import SentenceTransformer
    _EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    ST_AVAILABLE = True
except Exception:                                  # noqa: BLE001
    ST_AVAILABLE = False
    _EMBED_MODEL = None
    logger.warning("sentence-transformers not available — RAG disabled.")

try:
    import pypdf          # modern, Python 3.14-compatible PDF library
    PDF_AVAILABLE = True
except ImportError:
    try:
        import PyPDF2 as pypdf   # fallback to legacy library
        PDF_AVAILABLE = True
    except ImportError:
        PDF_AVAILABLE = False

try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# ── Constants ─────────────────────────────────────────────────────
CHUNK_SIZE    = 400    # words per chunk
CHUNK_OVERLAP = 80     # words overlap between consecutive chunks
TOP_K         = 5      # number of chunks to retrieve


# ─────────────────────────────────────────────────────────────────
# 1. Document Parsing
# ─────────────────────────────────────────────────────────────────

def parse_pdf(file_bytes: bytes) -> str:
    """Extract all text from a PDF byte stream using pypdf (Python 3.14-safe)."""
    if not PDF_AVAILABLE:
        return ""
    try:
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        pages  = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages)
    except Exception as exc:
        logger.warning("pypdf failed to parse PDF: %s", exc)
        return ""


def parse_docx(file_bytes: bytes) -> str:
    """Extract all paragraph text from a DOCX byte stream."""
    if not DOCX_AVAILABLE:
        return ""
    doc = DocxDocument(io.BytesIO(file_bytes))
    return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())


def parse_txt(file_bytes: bytes) -> str:
    """Decode a plain-text byte stream, trying UTF-8 then latin-1."""
    try:
        return file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return file_bytes.decode("latin-1", errors="replace")


def extract_text(file_bytes: bytes, filename: str) -> str:
    """Dispatch to the correct parser based on file extension."""
    ext = os.path.splitext(filename.lower())[1]
    if ext == ".pdf":
        text = parse_pdf(file_bytes)
    elif ext in (".docx", ".doc"):
        text = parse_docx(file_bytes)
    else:
        text = parse_txt(file_bytes)
    # Normalise whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


# ─────────────────────────────────────────────────────────────────
# 2. Chunking
# ─────────────────────────────────────────────────────────────────

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split *text* into overlapping word-level chunks."""
    words  = text.split()
    chunks = []
    start  = 0
    while start < len(words):
        end   = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        if end == len(words):
            break
        start += chunk_size - overlap
    return chunks


# ─────────────────────────────────────────────────────────────────
# 3. FAISS Index (per-session, in-memory)
# ─────────────────────────────────────────────────────────────────

# Global store: session_id → {"chunks": [...], "index": faiss.Index}
_SESSION_INDEXES: dict = {}


def build_index(session_id: str, chunks: list[str]) -> None:
    """Embed *chunks* and store a FAISS index for the given session."""
    if not (FAISS_AVAILABLE and ST_AVAILABLE):
        # Fallback: just store raw chunks
        _SESSION_INDEXES[session_id] = {"chunks": chunks, "index": None}
        return

    embeddings = _EMBED_MODEL.encode(chunks, show_progress_bar=False, convert_to_numpy=True)
    dim   = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings.astype(np.float32))
    _SESSION_INDEXES[session_id] = {"chunks": chunks, "index": index}
    logger.info("Built FAISS index: %d chunks for session %s", len(chunks), session_id)


def retrieve(session_id: str, query: str, top_k: int = TOP_K) -> str:
    """
    Return the *top_k* most relevant chunks for *query*.
    Falls back to keyword overlap if FAISS/ST is unavailable.
    """
    store = _SESSION_INDEXES.get(session_id)
    if not store or not store["chunks"]:
        return ""

    chunks = store["chunks"]
    index  = store["index"]

    if index is not None and ST_AVAILABLE:
        q_emb = _EMBED_MODEL.encode([query], convert_to_numpy=True).astype(np.float32)
        k     = min(top_k, len(chunks))
        _, idxs = index.search(q_emb, k)
        selected = [chunks[i] for i in idxs[0] if 0 <= i < len(chunks)]
    else:
        # Keyword-overlap fallback
        q_words = set(query.lower().split())
        scored  = []
        for chunk in chunks:
            c_words = set(chunk.lower().split())
            score   = len(q_words & c_words)
            scored.append((score, chunk))
        scored.sort(key=lambda x: x[0], reverse=True)
        selected = [c for _, c in scored[:top_k]]

    return "\n\n---\n\n".join(selected)


def clear_session(session_id: str) -> None:
    """Remove the FAISS index for a session (e.g., on new upload)."""
    _SESSION_INDEXES.pop(session_id, None)


# ─────────────────────────────────────────────────────────────────
# 4. High-level API
# ─────────────────────────────────────────────────────────────────

def process_document(session_id: str, file_bytes: bytes, filename: str) -> dict:
    """
    Full pipeline: parse → chunk → index.
    Returns metadata dict with word/chunk counts and a short preview.
    """
    try:
        text = extract_text(file_bytes, filename)
    except Exception as exc:
        logger.error("extract_text raised for '%s': %s", filename, exc)
        return {"success": False, "error": f"Failed to parse document: {exc}"}

    if not text or not text.strip():
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "file"
        if ext == "pdf":
            msg = (
                "No text could be extracted from this PDF. "
                "It may be a scanned/image-only PDF. "
                "Please use a text-based PDF, or copy-paste the text using the 'Paste Text' option."
            )
        else:
            msg = "Could not extract any text from the document. Please check the file is not empty or corrupted."
        return {"success": False, "error": msg}

    chunks = chunk_text(text)
    build_index(session_id, chunks)

    word_count = len(text.split())
    preview    = " ".join(text.split()[:80]) + ("…" if word_count > 80 else "")

    return {
        "success":     True,
        "filename":    filename,
        "word_count":  word_count,
        "chunk_count": len(chunks),
        "preview":     preview,
        "raw_text":    text,          # returned so callers can store it in session
    }


def process_pasted_text(session_id: str, text: str) -> dict:
    """
    Index plain-text pasted by the user.
    """
    text = text.strip()
    if not text:
        return {"success": False, "error": "No text provided."}

    chunks = chunk_text(text)
    build_index(session_id, chunks)

    word_count = len(text.split())
    preview    = " ".join(text.split()[:80]) + ("…" if word_count > 80 else "")

    return {
        "success":     True,
        "filename":    "Pasted Text",
        "word_count":  word_count,
        "chunk_count": len(chunks),
        "preview":     preview,
        "raw_text":    text,
    }


def estimate_difficulty(text: str) -> str:
    """
    Simple heuristic-based readability estimate.
    Returns a difficulty label string.
    """
    words     = text.split()
    sentences = re.split(r"[.!?]+", text)
    sentences = [s for s in sentences if s.strip()]

    if not sentences:
        return "Unknown"

    avg_words_per_sentence = len(words) / len(sentences)
    long_words = sum(1 for w in words if len(w) > 8)
    long_word_ratio = long_words / max(len(words), 1)

    # Simple scoring
    score = avg_words_per_sentence * 0.4 + long_word_ratio * 60

    if score < 10:
        return "Elementary (Grades 1–6)"
    elif score < 18:
        return "Intermediate (Grades 7–10)"
    elif score < 26:
        return "Advanced (Grades 11–12 / Undergraduate)"
    else:
        return "Expert (Graduate / Professional)"
