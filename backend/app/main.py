"""FastAPI application entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.config import settings
from app.database import init_db
from app.api import auth, reports, coe, sql_analysis, dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize DB on startup."""
    init_db()
    yield
    # Shutdown if needed


app = FastAPI(
    title=settings.app_name,
    description="AI-powered BI migration and modernization platform",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS: ensure frontend origins are always allowed (merge with env config)
_default_origins = [
    "http://localhost:8090", "http://127.0.0.1:8090",
    "http://localhost:3000", "http://127.0.0.1:3000",
]
# Allow Vercel deployments (same-origin when frontend and API are on one domain)
_cors_origins = list(dict.fromkeys(_default_origins + settings.cors_origins_list))


def _add_cors_headers(response, origin: str):
    if origin in _cors_origins or "localhost" in origin or "127.0.0.1" in origin or ".vercel.app" in (origin or ""):
        response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"


class AddCORSHeadersMiddleware(BaseHTTPMiddleware):
    """Ensure CORS headers are on every response (including errors)."""
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin") or "http://localhost:8090"
        response = await call_next(request)
        _add_cors_headers(response, origin)
        return response


app.add_middleware(AddCORSHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(coe.router, prefix="/api/coe", tags=["coe"])
app.include_router(sql_analysis.router, prefix="/api/sql", tags=["sql"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])


@app.get("/")
async def root():
    return {"message": "BI Modernization API", "docs": "/docs"}


@app.get("/health")
async def health():
    return {"status": "ok"}
