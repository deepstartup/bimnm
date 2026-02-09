"""FastAPI entrypoint for Vercel backend project.

Vercel's FastAPI support looks for an `app` instance in one of:
- main.py / index.py / server.py at the project root
- or app/app.py, etc.

With `Root Directory = backend`, this file makes the FastAPI
application discoverable as `backend/main.py -> app`.
"""

from app.main import app  # noqa: F401

