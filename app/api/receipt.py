import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import get_settings
from app.vision.receipt import analyze_receipt

router = APIRouter()


@router.post("/analyze")
def analyze(file: UploadFile = File(...)) -> dict:
    settings = get_settings()
    allowed = {"image/jpeg", "image/png", "image/webp"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Upload a JPG, PNG, or WEBP receipt image.")
    suffix = Path(file.filename or "receipt.png").suffix or ".png"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)
    if tmp_path.stat().st_size > settings.upload_max_mb * 1024 * 1024:
        tmp_path.unlink(missing_ok=True)
        raise HTTPException(status_code=413, detail="File too large.")
    try:
        return analyze_receipt(tmp_path)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        tmp_path.unlink(missing_ok=True)
