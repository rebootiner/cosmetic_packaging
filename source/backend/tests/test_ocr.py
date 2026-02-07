from fastapi.testclient import TestClient

from app.main import app
from app.ocr_engine import extract_dimension_candidates


client = TestClient(app)


def _png_1x1_bytes() -> bytes:
    return (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0bIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    )


def test_ocr_extract_success_with_mock(monkeypatch):
    monkeypatch.setattr(
        'app.main.extract_dimension_candidates',
        lambda _: {
            'items': [
                {'text': '27.9mm', 'value': 27.9, 'unit': 'mm', 'bbox': None, 'confidence': 0.9},
                {'text': '48.8', 'value': 48.8, 'unit': None, 'bbox': None, 'confidence': 0.8},
            ],
            'engine_available': False,
            'message': 'mocked',
        },
    )

    res = client.post(
        '/api/v1/ocr/extract',
        files={'file': ('sample.png', _png_1x1_bytes(), 'image/png')},
    )

    assert res.status_code == 200
    data = res.json()
    assert data['engine_available'] is False
    assert data['message'] == 'mocked'
    assert len(data['items']) == 2
    assert data['items'][0]['text'] == '27.9mm'
    assert data['items'][1]['value'] == 48.8


def test_ocr_extract_missing_file():
    res = client.post('/api/v1/ocr/extract')
    assert res.status_code == 422


def test_ocr_extract_non_image_rejected():
    res = client.post(
        '/api/v1/ocr/extract',
        files={'file': ('sample.txt', b'not image', 'text/plain')},
    )

    assert res.status_code == 400
    assert res.json()['detail'] == 'Only image uploads are allowed'


def test_parse_dimension_candidates_from_text_bytes():
    raw = b'W: 48.8 H: 27.9mm D: 13 mm'
    result = extract_dimension_candidates(raw)

    parsed = [(item['text'], item['value'], item['unit']) for item in result['items']]
    assert ('48.8', 48.8, None) in parsed
    assert ('27.9mm', 27.9, 'mm') in parsed
    assert ('13 mm', 13.0, 'mm') in parsed


def test_parse_excludes_version_and_multi_dot_patterns():
    raw = b'v2.0 size 13mm bad 12.34.56mm good 7mm'
    result = extract_dimension_candidates(raw)

    parsed_text = [item['text'] for item in result['items']]
    assert '2.0' not in parsed_text
    assert '12.34' not in parsed_text
    assert '56mm' not in parsed_text
    assert '13mm' in parsed_text
    assert '7mm' in parsed_text


def test_parse_normalizes_comma_decimal():
    raw = b'D: 10,5mm'
    result = extract_dimension_candidates(raw)

    parsed = [(item['text'], item['value'], item['unit']) for item in result['items']]
    assert ('10.5mm', 10.5, 'mm') in parsed
