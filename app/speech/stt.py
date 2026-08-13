import logging
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)


def transcribe_audio(audio_path: str | Path) -> str:
    """Transcribe an audio file with pretrained Whisper."""
    try:
        import whisper

        model = whisper.load_model("base")
        audio = _load_audio_without_ffmpeg(audio_path)
        result = model.transcribe(audio if audio is not None else str(audio_path))
        text = str(result.get("text", "")).strip()
        if not text:
            raise ValueError("Whisper returned empty transcription.")
        logger.info("STT transcription completed")
        return text
    except Exception as exc:
        logger.exception("STT failed: %s", exc)
        raise RuntimeError(f"Could not transcribe audio: {exc}") from exc


def _load_audio_without_ffmpeg(audio_path: str | Path) -> np.ndarray | None:
    """Load browser WAV audio directly so Whisper does not need ffmpeg for mic input."""
    try:
        import soundfile as sf

        samples, sample_rate = sf.read(str(audio_path), dtype="float32")
        if samples.ndim > 1:
            samples = samples.mean(axis=1)
        if sample_rate != 16000:
            samples = _resample_linear(samples, sample_rate, 16000)
        return np.asarray(samples, dtype=np.float32)
    except Exception as exc:
        logger.info("Direct audio decode failed, falling back to Whisper path loading: %s", exc)
        return None


def _resample_linear(samples: np.ndarray, source_rate: int, target_rate: int) -> np.ndarray:
    if source_rate == target_rate or len(samples) == 0:
        return samples
    duration = len(samples) / source_rate
    old_positions = np.linspace(0, duration, num=len(samples), endpoint=False)
    new_length = max(1, int(duration * target_rate))
    new_positions = np.linspace(0, duration, num=new_length, endpoint=False)
    return np.interp(new_positions, old_positions, samples).astype(np.float32)
