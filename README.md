# BI Modernization Platform — FastAPI + React

AI-powered automation toolkit for migrating legacy Business Intelligence systems (e.g. SAP Business Objects) to modern platforms (Power BI, Tableau). This is the **FastAPI + React** rebuild of the original Flask/Jinja2 application.

## Stack

- **Backend:** FastAPI, SQLAlchemy 2.0, SQLite, JWT (python-jose), Uvicorn — port **5011**
- **Frontend:** React 18, React Router, Axios — port **8090**

## Quick start

### Backend

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env if needed (SECRET_KEY, etc.)
uvicorn app.main:app --reload --port 5011
```

API docs: **http://localhost:5011/docs**

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
# Edit .env if needed: REACT_APP_API_URL=http://localhost:5011, PORT=8090
npm start
```

App: **http://localhost:8090**

### Deploy full-stack on Vercel (one URL)

The repo is set up so **one Vercel project** serves both the React app and the FastAPI API from the same domain.

1. In [Vercel](https://vercel.com), import the repo and deploy **with Root Directory left at the repo root** (do not set it to `frontend`).
2. Build and API are configured in root `vercel.json`:
   - Frontend is built from `frontend/` and served as static files.
   - All `/api/*` requests are handled by the FastAPI app (serverless) in `api/`.
3. Set **Environment Variable** (optional): `REACT_APP_API_URL` = leave **empty** so the app uses the same origin (`/api`). Only set it if you host the API elsewhere.
4. **Note:** The API uses SQLite in `/tmp` on Vercel; data does not persist across serverless invocations. For persistent data, add a database (e.g. Vercel Postgres) and set `DATABASE_URL`.

### First run

1. Start backend, then frontend.
2. Open http://localhost:8090 → Register a user → Sign in.
3. Use the Dashboard and Reports (empty until you add data via API or future features).

## Project layout

```
backend/
  app/
    main.py          # FastAPI app, CORS, lifespan
    config.py        # Settings (env)
    database.py      # SQLAlchemy engine, session, get_db
    models/          # User, Report, COEAnalysis
    schemas/         # Pydantic request/response
    api/             # auth, reports, deps (get_current_user)
    core/            # security (JWT, password hashing)
    services/        # report_service
frontend/
  src/
    App.js           # Routes, protected layout
    context/         # AuthContext
    services/        # api (axios + interceptors)
    components/      # auth, common, reports
    pages/           # Dashboard
```

## Implemented

- **Phase 1–2:** FastAPI app, CORS, SQLite, SQLAlchemy 2.0, JWT auth (register, login, `/api/auth/me`), protected routes, React Login/Register/ProtectedRoute/AuthContext, Dashboard, Report CRUD.
- **Phase 3:** COE CSV processor — upload CSV, complexity scoring, duplicate detection, effort estimation; `POST /api/coe/upload`, `GET /api/coe/results/{id}`, `GET /api/coe/history`, `DELETE /api/coe/results/{id}`; COE Processor page with upload, results, and history.
- **Phase 4:** SQL complexity analyzer — `POST /api/sql/analyze`, `POST /api/sql/compare`; SQL Analysis page (analyze + compare modes) with lineage and recommendations.
- **Phase 5:** Report consolidation — `POST /api/reports/consolidate`; Consolidation page to find duplicate/near-duplicate reports and potential savings.
- **Phase 8:** Dashboard stats — `GET /api/dashboard/stats` (total reports, migrated, progress %, complexity breakdown, estimated hours, COE count); Dashboard uses it for KPI cards.

## Next steps (from handoff)

- Phase 6: AI services (NL to SQL, RAG)
- Phase 7: Screenshot column mapper
- PDF/Excel export

## Environment

- **Backend:** `.env` (see `.env.example`) — `DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS`, etc.
- **Frontend:** Copy `frontend/.env.example` to `frontend/.env`. Set `REACT_APP_API_URL=http://localhost:5011` and `PORT=8090` (or your backend port).

## License / repo

See repository and handoff document for full spec, algorithms, and timeline.
