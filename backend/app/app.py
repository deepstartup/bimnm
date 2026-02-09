"""Vercel FastAPI entrypoint for backend-only deployment.

This file simply re-exports the FastAPI `app` from `app.main`,
so a Vercel project with Root Directory = `backend` can detect
and deploy the FastAPI application without extra config.
"""

from app.main import app  # noqa: F401

