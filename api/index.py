# Vercel serverless entry: expose FastAPI app for all /api/* routes.
# Add backend to path so "from app.main import app" resolves.
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

# Ensure serverless-friendly DB path (writable on Vercel)
if os.environ.get("VERCEL"):
    os.environ.setdefault("DATABASE_URL", "sqlite:////tmp/app.db")

from app.main import app

# Vercel Python runtime uses the "app" export for ASGI apps.
