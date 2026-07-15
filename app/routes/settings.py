"""routes/settings.py — Application settings."""

from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for
from app.core.agent_instructions import (
    SUPPORTED_SUBJECTS, AGENT_NAME, AGENT_TONE, TEACHING_STYLE,
    TONE_INSTRUCTIONS, TEACHING_STYLE_INSTRUCTIONS,
)
from app.core.watsonx_client import check_credentials

settings_bp = Blueprint("settings", __name__)


@settings_bp.route("/")
def settings_page():
    return render_template(
        "settings.html",
        agent_name=AGENT_NAME,
        subjects=SUPPORTED_SUBJECTS,
        tones=list(TONE_INSTRUCTIONS.keys()),
        styles=list(TEACHING_STYLE_INSTRUCTIONS.keys()),
        current_proficiency=session.get("proficiency", "Beginner"),
        current_subject=session.get("subject", "General / Other"),
        current_tone=AGENT_TONE,
        current_style=TEACHING_STYLE,
    )


@settings_bp.route("/save", methods=["POST"])
def save_settings():
    data = request.get_json(force=True)
    if "proficiency" in data:
        session["proficiency"] = data["proficiency"]
    if "subject" in data:
        session["subject"] = data["subject"]
    session.modified = True
    return jsonify({"ok": True, "message": "Settings saved."})


@settings_bp.route("/test-connection")
def test_connection():
    result = check_credentials()
    return jsonify(result)
