import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.config import get_settings
from app.speech.stt import transcribe_audio
from app.speech.tts import synthesize_speech

router = APIRouter()


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=4000)


@router.post("/transcribe")
def transcribe(file: UploadFile = File(...)) -> dict[str, str]:
    settings = get_settings()
    if file.content_type and not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Upload an audio file.")
    suffix = Path(file.filename or "audio.wav").suffix or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)
    if tmp_path.stat().st_size > settings.upload_max_mb * 1024 * 1024:
        tmp_path.unlink(missing_ok=True)
        raise HTTPException(status_code=413, detail="File too large.")
    try:
        text = transcribe_audio(tmp_path).strip()
        if not text:
            raise HTTPException(status_code=422, detail="I couldn't understand the speech. Please try again.")
        return {"text": text}
    except RuntimeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    finally:
        tmp_path.unlink(missing_ok=True)


@router.post("/tts")
def tts(request: TTSRequest) -> FileResponse:
    try:
        audio_path = synthesize_speech(request.text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unable to generate answer audio.") from exc
    return FileResponse(audio_path, media_type="audio/wav", filename="answer.wav")
