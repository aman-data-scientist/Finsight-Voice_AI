import logging
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


def synthesize_speech(text: str) -> Path:
    """Create a WAV file from text using local pyttsx3."""
    if not text.strip():
        raise ValueError("Text is required for TTS.")

    output_path = Path(tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name)
    try:
        import pyttsx3

        engine = pyttsx3.init()
        engine.save_to_file(text, str(output_path))
        engine.runAndWait()
        logger.info("TTS audio generated at %s", output_path)
        return output_path
    except Exception as exc:
        logger.exception("TTS failed: %s", exc)
        raise RuntimeError("Could not synthesize speech.") from exc
