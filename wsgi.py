"""
wsgi.py — WSGI entry point for production (gunicorn).
Usage: gunicorn -w 4 wsgi:app
"""

from app import create_app
app = create_app()
