import logging
from pathlib import Path

from app.agents.tools import parse_receipt_fields
from app.vision.detector import detect_receipt_region, image_is_readable
from app.vision.ocr import run_ocr
from app.vision.preprocessing import preprocess_receipt_image

logger = logging.getLogger(__name__)


def analyze_receipt(image_path: str | Path) -> dict:
    """YOLO/localization -> OpenCV preprocessing -> OCR -> structured expense."""
    if not image_is_readable(image_path):
        raise ValueError("Unsupported image file.")
    receipt_region = detect_receipt_region(image_path)
    processed = preprocess_receipt_image(receipt_region)
    text = run_ocr(processed)
    fields = parse_receipt_fields(text)
    logger.info("Receipt analysis completed")
    return {"raw_text": text, "expense": fields}
