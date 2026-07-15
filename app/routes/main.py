"""routes/main.py — Home, About pages."""

from flask import Blueprint, render_template, session
from app.core.agent_instructions import SUPPORTED_SUBJECTS, AGENT_NAME

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Landing / Home page."""
    session.setdefault("proficiency",   "Beginner")
    session.setdefault("subject",       "General / Other")
    session.setdefault("chat_history",  [])
    session.setdefault("documents",     [])
    session.setdefault("learn_history", [])
    return render_template(
        "home.html",
        agent_name=AGENT_NAME,
        subjects=SUPPORTED_SUBJECTS,
    )


@main_bp.route("/about")
def about():
    """About page."""
    return render_template("about.html", agent_name=AGENT_NAME)
