import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def detect_receipt_region(image_path: str | Path) -> str | Path:
    """Locate a receipt/document region.

    YOLO is optional for this prototype. If no suitable local YOLO model is
    configured, the whole image is passed to OpenCV/OCR.
    """
    try:
        from ultralytics import YOLO

        model = YOLO("yolov8n.pt")
        results = model(str(image_path), verbose=False)
        if results and len(results[0].boxes) > 0:
            logger.info("YOLO detected candidate regions; using original image for OCR prototype")
    except Exception as exc:
        logger.info("YOLO unavailable or no receipt model configured: %s", exc)
    return image_path


def image_is_readable(image_path: str | Path) -> bool:
    import cv2

    return cv2.imread(str(image_path)) is not None
