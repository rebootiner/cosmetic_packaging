import re
from typing import Any, TypedDict


class OCRResultItem(TypedDict):
    text: str
    value: float
    unit: str | None
    bbox: list[int] | None
    confidence: float


_DIMENSION_PATTERN = re.compile(r'(?<!\d)(\d+(?:\.\d+)?)(?:\s*(mm))?(?!\d)', re.IGNORECASE)


# Stage1 lightweight / no DB persistence

def build_ocr_result_item(
    text: str,
    value: float,
    unit: str | None = None,
    bbox: list[int] | None = None,
    confidence: float = 0.0,
) -> OCRResultItem:
    return {
        'text': text,
        'value': float(value),
        'unit': unit.lower() if unit else None,
        'bbox': bbox,
        'confidence': float(confidence),
    }


# Stage1 lightweight / no DB persistence

def extract_dimension_candidates(image_bytes: bytes) -> dict[str, Any]:
    """Extract dimensional candidates from OCR text (placeholder-friendly)."""
    engine_available = False
    message = 'OCR engine unavailable in current runtime; using lightweight parser fallback.'

    extracted_text = ''
    try:
        import pytesseract  # type: ignore
        from PIL import Image  # type: ignore
        import io

        engine_available = True
        message = 'OCR engine available.'
        image = Image.open(io.BytesIO(image_bytes))
        extracted_text = pytesseract.image_to_string(image)
    except Exception:
        # Placeholder fallback: decode bytes to text when OCR runtime is not available.
        extracted_text = image_bytes.decode('utf-8', errors='ignore')

    items: list[OCRResultItem] = []
    for match in _DIMENSION_PATTERN.finditer(extracted_text):
        raw = match.group(0).strip()
        value = float(match.group(1))
        unit = match.group(2)
        items.append(build_ocr_result_item(text=raw, value=value, unit=unit, bbox=None, confidence=0.0))

    return {
        'items': items,
        'engine_available': engine_available,
        'message': message,
    }
