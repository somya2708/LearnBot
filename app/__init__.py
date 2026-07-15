"""
app/__init__.py
───────────────
Flask application factory.
"""

import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # ── Core config ───────────────────────────────────────────────
    app.secret_key               = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")
    app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))  # 16 MB
    app.config["UPLOAD_FOLDER"]      = os.getenv("UPLOAD_FOLDER", "app/static/uploads")
    app.config["ALLOWED_EXTENSIONS"] = {"pdf", "docx", "txt"}
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    # ── Register blueprints ───────────────────────────────────────
    from app.routes.main     import main_bp
    from app.routes.chat     import chat_bp
    from app.routes.upload   import upload_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.history  import history_bp
    from app.routes.settings import settings_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(chat_bp,      url_prefix="/chat")
    app.register_blueprint(upload_bp,    url_prefix="/upload")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(history_bp,   url_prefix="/history")
    app.register_blueprint(settings_bp,  url_prefix="/settings")

    # ── Ensure upload directory exists ───────────────────────────
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    return app
