"""routes/dashboard.py — Learner dashboard."""

from flask import Blueprint, render_template, session
from app.core.agent_instructions import AGENT_NAME, SUPPORTED_SUBJECTS

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def dashboard():
    """Render the learner dashboard with aggregated session statistics."""
    chat_history  = session.get("chat_history",  [])
    learn_history = session.get("learn_history", [])
    documents     = session.get("documents",     [])

    # ── Stats ──────────────────────────────────────────────────────
    total_messages  = len([m for m in chat_history if m["role"] == "user"])
    total_sessions  = len(learn_history)
    topics_explored = list({h["topic"][:40] for h in learn_history})
    subjects_used   = list({h["subject"]   for h in learn_history})

    # Subject frequency for mini chart
    subject_counts = {}
    for h in learn_history:
        s = h.get("subject", "General / Other")
        subject_counts[s] = subject_counts.get(s, 0) + 1

    proficiency_counts = {}
    for h in learn_history:
        p = h.get("proficiency", "Beginner")
        proficiency_counts[p] = proficiency_counts.get(p, 0) + 1

    # Estimated reading time (avg 200 wpm)
    total_words    = sum(d.get("word_count", 0) for d in documents)
    reading_mins   = round(total_words / 200)

    return render_template(
        "dashboard.html",
        agent_name=AGENT_NAME,
        proficiency=session.get("proficiency", "Beginner"),
        subject=session.get("subject", "General / Other"),
        total_messages=total_messages,
        total_sessions=total_sessions,
        topics_explored=topics_explored[:10],
        subjects_used=subjects_used,
        subject_counts=subject_counts,
        proficiency_counts=proficiency_counts,
        documents=documents,
        total_words=total_words,
        reading_mins=reading_mins,
        recent_history=learn_history[-5:][::-1],
        all_subjects=SUPPORTED_SUBJECTS,
    )
