"""routes/chat.py — Chat interface and message handling."""

import uuid
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, session

from app.core.watsonx_client  import generate_response, check_credentials
from app.core.rag_engine      import retrieve
from app.core.agent_instructions import SUPPORTED_SUBJECTS, AGENT_NAME

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/")
def chat_page():
    """Render the chat interface."""
    session.setdefault("proficiency",  "Beginner")
    session.setdefault("subject",      "General / Other")
    session.setdefault("chat_history", [])
    return render_template(
        "chat.html",
        agent_name=AGENT_NAME,
        subjects=SUPPORTED_SUBJECTS,
        proficiency=session["proficiency"],
        subject=session["subject"],
        chat_history=session["chat_history"],
        documents=session.get("documents", []),
    )


@chat_bp.route("/send", methods=["POST"])
def send_message():
    """
    POST /chat/send
    Body (JSON): { message, proficiency, subject }
    Returns JSON: { reply, timestamp }
    """
    data        = request.get_json(force=True)
    user_msg    = (data.get("message") or "").strip()
    proficiency = data.get("proficiency", session.get("proficiency", "Beginner"))
    subject     = data.get("subject",     session.get("subject",     "General / Other"))

    if not user_msg:
        return jsonify({"error": "Empty message."}), 400

    # Persist settings to session
    session["proficiency"] = proficiency
    session["subject"]     = subject
    session.modified       = True

    # ── RAG: retrieve relevant chunks ─────────────────────────────
    session_id  = session.get("session_id", str(uuid.uuid4()))
    session["session_id"] = session_id
    rag_context = retrieve(session_id, user_msg) or None

    # ── Generate response ─────────────────────────────────────────
    chat_history = session.get("chat_history", [])
    reply = generate_response(
        user_message=user_msg,
        proficiency=proficiency,
        subject=subject,
        rag_context=rag_context,
        conversation_history=chat_history,
    )

    # ── Store turn in session history ─────────────────────────────
    timestamp = datetime.now().strftime("%H:%M")
    chat_history.append({"role": "user",      "content": user_msg,  "time": timestamp})
    chat_history.append({"role": "assistant", "content": reply,     "time": timestamp})
    session["chat_history"] = chat_history[-40:]   # keep last 40 messages

    # ── Append to learning history ────────────────────────────────
    learn_history = session.get("learn_history", [])
    learn_history.append({
        "id":          str(uuid.uuid4()),
        "date":        datetime.now().strftime("%Y-%m-%d %H:%M"),
        "topic":       user_msg[:80],
        "proficiency": proficiency,
        "subject":     subject,
        "response":    reply[:300] + ("…" if len(reply) > 300 else ""),
    })
    session["learn_history"] = learn_history[-50:]
    session.modified = True

    return jsonify({"reply": reply, "timestamp": timestamp})


@chat_bp.route("/clear", methods=["POST"])
def clear_chat():
    """Clear the current chat history."""
    session["chat_history"] = []
    session.modified = True
    return jsonify({"ok": True})


@chat_bp.route("/settings", methods=["POST"])
def update_settings():
    """Update proficiency and subject from the chat sidebar."""
    data = request.get_json(force=True)
    if "proficiency" in data:
        session["proficiency"] = data["proficiency"]
    if "subject" in data:
        session["subject"] = data["subject"]
    session.modified = True
    return jsonify({"ok": True})


@chat_bp.route("/health")
def health():
    """Quick credential health-check endpoint."""
    result = check_credentials()
    return jsonify(result)
