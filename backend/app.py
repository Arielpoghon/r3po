"""Single-origin API and built frontend server."""

from __future__ import annotations

import threading
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from backend.models import ScanRequest, ScanResponse
from core.scanner import scan

app = FastAPI(title="r3po")
scan_lock = threading.Lock()
static_dir = Path(__file__).resolve().parent.parent / "frontend" / "dist"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/scan", response_model=ScanResponse)
def run_scan(request: ScanRequest) -> ScanResponse:
    if not scan_lock.acquire(blocking=False):
        raise HTTPException(status_code=429, detail="A scan is already running, please try again shortly")
    try:
        return ScanResponse(**scan(request.repo_url).model_dump())
    finally:
        scan_lock.release()


# This is mounted last so API routes take precedence. Docker supplies this directory.
app.mount("/", StaticFiles(directory=static_dir, html=True, check_dir=False), name="frontend")
