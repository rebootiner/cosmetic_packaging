import re
from typing import Any, TypedDict


class OCRResultItem(TypedDict):
    text: str
    value: float
    unit: str | None
    bbox: list[int] | None
    confidence: float


# Stage1 lightweight / no DB persistence

_DIMENSION_PATTERN = re.compile(r'(?<!\d)(\d+(?:\.\d+)?)(?:\s*(mm))?(?!\d)', re.IGNORECASE)
_VERSION_PATTERN = re.compile(r'\bv\s*\d+(?:\.\d+)+\b', re.IGNORECASE)
_MULTI_DOT_PATTERN = re.compile(r'\b\d+\.\d+\.\d+\b')
_CONTEXT_TOKENS = ('w', 'h', 'd', 'width', 'height', 'depth', 'dia', 'diameter', 'size', 'mm', 'x', '×')


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


def _normalize_text(text: str) -> str:
    # Stage1 lightweight / no DB persistence
    # 10,5 -> 10.5 (locale decimal normalization)
    normalized = re.sub(r'(?<=\d),(?=\d)', '.', text)
    return normalized


def _is_dimension_context(text: str, start: int, end: int, unit: str | None) -> bool:
    if unit and unit.lower() == 'mm':
        return True

    left = text[max(0, start - 12):start].lower()
    right = text[end:min(len(text), end + 12)].lower()
    context = f'{left} {right}'
    return any(token in context for token in _CONTEXT_TOKENS)


def _is_excluded_by_patterns(text: str, start: int, end: int) -> bool:
    window = text[max(0, start - 4):min(len(text), end + 4)]

    # version string rejection: v2.0, v1.2.3
    if _VERSION_PATTERN.search(window):
        return True

    # multi-dot malformed numeric rejection: 12.34.56
    if _MULTI_DOT_PATTERN.search(window):
        return True

    return False


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

    extracted_text = _normalize_text(extracted_text)

    items: list[OCRResultItem] = []
    for match in _DIMENSION_PATTERN.finditer(extracted_text):
        raw = match.group(0).strip()
        value = float(match.group(1))
        unit = match.group(2)
        start, end = match.span()

        if _is_excluded_by_patterns(extracted_text, start, end):
            continue
        if not _is_dimension_context(extracted_text, start, end, unit):
            continue

        confidence = 0.9 if unit else 0.6
        items.append(build_ocr_result_item(text=raw, value=value, unit=unit, bbox=None, confidence=confidence))

    return {
        'items': items,
        'engine_available': engine_available,
        'message': message,
    }
