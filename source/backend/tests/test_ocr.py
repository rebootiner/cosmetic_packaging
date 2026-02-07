from fastapi.testclient import TestClient

from app.main import app
from app.ocr_engine import extract_dimension_candidates

client = TestClient(app)


def _png_1x1_bytes() -> bytes:
    return (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0bIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    )


def test_ocr_extract_non_image_rejected():
    res = client.post('/api/v1/ocr/extract', files={'file': ('x.txt', b'abc', 'text/plain')})
    assert res.status_code == 400


def test_parse_dimension_candidates_from_text_bytes():
    raw = b'W: 48.8 H: 27.9mm D: 13 mm'
    result = extract_dimension_candidates(raw)
    parsed = [(item['text'], item['value'], item['unit']) for item in result['items']]
    assert ('48.8', 48.8, None) in parsed
    assert ('27.9mm', 27.9, 'mm') in parsed
    assert ('13 mm', 13.0, 'mm') in parsed


def test_parse_normalizes_comma_decimal():
    raw = b'D: 10,5mm'
    result = extract_dimension_candidates(raw)
    parsed = [(item['text'], item['value'], item['unit']) for item in result['items']]
    assert ('10.5mm', 10.5, 'mm') in parsed
