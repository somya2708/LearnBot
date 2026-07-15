"""routes/history.py — Learning history view."""

from flask import Blueprint, render_template, session, jsonify, request
from app.core.agent_instructions import AGENT_NAME

history_bp = Blueprint("history", __name__)


@history_bp.route("/")
def history_page():
    learn_history = session.get("learn_history", [])
    return render_template(
        "history.html",
        agent_name=AGENT_NAME,
        learn_history=list(reversed(learn_history)),
    )


@history_bp.route("/clear", methods=["POST"])
def clear_history():
    session["learn_history"] = []
    session["chat_history"]  = []
    session.modified = True
    return jsonify({"ok": True})


@history_bp.route("/delete/<item_id>", methods=["POST"])
def delete_item(item_id):
    learn_history = session.get("learn_history", [])
    session["learn_history"] = [h for h in learn_history if h.get("id") != item_id]
    session.modified = True
    return jsonify({"ok": True})
