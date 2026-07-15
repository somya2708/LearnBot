"""routes/upload.py — Document upload and text paste handling."""

import os
import uuid
import logging
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, session, current_app

from app.core.rag_engine      import process_document, process_pasted_text, estimate_difficulty
from app.core.agent_instructions import AGENT_NAME

logger = logging.getLogger(__name__)

upload_bp = Blueprint("upload", __name__)

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}


def _allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route("/")
def upload_page():
    return render_template(
        "upload.html",
        agent_name=AGENT_NAME,
        documents=session.get("documents", []),
    )


@upload_bp.route("/file", methods=["POST"])
def upload_file():
    """
    POST /upload/file  (multipart/form-data, field: 'document')
    Returns JSON with document metadata.
    """
    if "document" not in request.files:
        return jsonify({"success": False, "error": "No file provided."}), 400

    file = request.files["document"]
    if file.filename == "":
        return jsonify({"success": False, "error": "Empty filename."}), 400
    if not _allowed(file.filename):
        return jsonify({"success": False, "error": "Unsupported file type. Use PDF, DOCX, or TXT."}), 400

    file_bytes = file.read()
    if len(file_bytes) > current_app.config["MAX_CONTENT_LENGTH"]:
        return jsonify({"success": False, "error": "File exceeds 16 MB limit."}), 400

    session_id = session.get("session_id", str(uuid.uuid4()))
    session["session_id"] = session_id

    result = process_document(session_id, file_bytes, file.filename)
    if not result["success"]:
        logger.error("process_document failed for '%s': %s", file.filename, result.get("error"))
        return jsonify(result), 422

    # Estimate difficulty
    difficulty = estimate_difficulty(result["raw_text"])
    result.pop("raw_text", None)          # don't store full text in session

    # Save document metadata to session
    doc_entry = {
        "id":          str(uuid.uuid4()),
        "filename":    result["filename"],
        "word_count":  result["word_count"],
        "chunk_count": result["chunk_count"],
        "preview":     result["preview"],
        "difficulty":  difficulty,
        "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    documents = session.get("documents", [])
    documents.append(doc_entry)
    session["documents"] = documents[-10:]   # keep last 10
    session.modified = True

    return jsonify({
        "success":    True,
        "document":   doc_entry,
        "difficulty": difficulty,
        "message":    f"✅ '{file.filename}' processed successfully ({result['word_count']} words, {result['chunk_count']} chunks).",
    })


@upload_bp.route("/paste", methods=["POST"])
def paste_text():
    """
    POST /upload/paste  (JSON: { text })
    Process pasted text for RAG.
    """
    data = request.get_json(force=True)
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"success": False, "error": "No text provided."}), 400

    session_id = session.get("session_id", str(uuid.uuid4()))
    session["session_id"] = session_id

    result = process_pasted_text(session_id, text)
    if not result["success"]:
        return jsonify(result), 422

    difficulty = estimate_difficulty(result["raw_text"])
    result.pop("raw_text", None)

    doc_entry = {
        "id":          str(uuid.uuid4()),
        "filename":    "Pasted Text",
        "word_count":  result["word_count"],
        "chunk_count": result["chunk_count"],
        "preview":     result["preview"],
        "difficulty":  difficulty,
        "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    documents = session.get("documents", [])
    documents.append(doc_entry)
    session["documents"] = documents[-10:]
    session.modified = True

    return jsonify({
        "success":  True,
        "document": doc_entry,
        "message":  f"✅ Text processed successfully ({result['word_count']} words, {result['chunk_count']} chunks).",
    })


@upload_bp.route("/clear", methods=["POST"])
def clear_documents():
    """Remove all uploaded documents and clear the RAG index."""
    from app.core.rag_engine import clear_session
    session_id = session.get("session_id")
    if session_id:
        clear_session(session_id)
    session["documents"] = []
    session.modified = True
    return jsonify({"ok": True})
