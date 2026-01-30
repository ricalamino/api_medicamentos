"""
Admin endpoints (require API Key). E.g. trigger CSV import via URL.
"""
import asyncio
import subprocess
import sys
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth import get_api_key

router = APIRouter(prefix="/admin", tags=["admin"])

# Project root (parent of app/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # app/routes -> app -> root
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
DEFAULT_CSV = PROJECT_ROOT / "DADOS_ABERTOS_MEDICAMENTOS.csv"


class ImportRequest(BaseModel):
    """Optional body for import endpoint."""
    csv_path: Optional[str] = None  # If omitted, use default or CSV_URL in script


@router.post("/import")
async def run_import(
    body: Optional[ImportRequest] = None,
    api_key: str = Depends(get_api_key),
):
    """
    Run the CSV import script (reimport/update data). Requires API Key.
    Uses default CSV path or CSV_URL env; optionally pass csv_path in body.
    """
    raw = (body and body.csv_path) or ""
    raw = (raw or "").strip()
    # Ignore Swagger placeholder "string" and empty; use default if path missing or not found
    if raw and raw.lower() != "string":
        candidate = Path(raw) if Path(raw).is_absolute() else (PROJECT_ROOT / raw)
        if candidate.exists():
            csv_path = str(candidate)
        else:
            csv_path = str(DEFAULT_CSV)
    else:
        csv_path = str(DEFAULT_CSV)
    script_path = SCRIPTS_DIR / "import_csv.py"
    if not script_path.exists():
        raise HTTPException(500, detail="Import script not found")

    def _run():
        result = subprocess.run(
            [sys.executable, str(script_path), csv_path],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=3600,
        )
        return result

    try:
        result = await asyncio.to_thread(_run)
    except subprocess.TimeoutExpired:
        raise HTTPException(504, detail="Import timed out (max 1h)")

    return {
        "ok": result.returncode == 0,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
