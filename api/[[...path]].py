# Vercel catch-all: all /api/* requests hit this and are handled by FastAPI.
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

if os.environ.get("VERCEL"):
    os.environ.setdefault("DATABASE_URL", "sqlite:////tmp/app.db")

from app.main import app
