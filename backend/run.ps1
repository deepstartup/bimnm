# Run backend on port 5011 (frontend .env points to 5011 to avoid port conflict with old processes)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
& .\venv\Scripts\python.exe -B -m uvicorn app.main:app --host 0.0.0.0 --port 5011
