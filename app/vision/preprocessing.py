from pathlib import Path


def preprocess_receipt_image(image_path: str | Path):
    """Read, grayscale, denoise, and threshold a receipt image before OCR."""
    import cv2

    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError("Unsupported or unreadable image.")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray)
    return cv2.adaptiveThreshold(
        denoised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11,
    )
