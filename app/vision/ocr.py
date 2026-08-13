import logging

logger = logging.getLogger(__name__)


def run_ocr(processed_image) -> str:
    """Convert preprocessed receipt pixels into machine-readable text."""
    import pytesseract

    text = pytesseract.image_to_string(processed_image)
    if not text.strip():
        raise RuntimeError("OCR returned no text.")
    logger.info("OCR completed")
    return text
