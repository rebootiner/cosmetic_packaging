import json

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _png_1x1_bytes() -> bytes:
    return (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0bIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    )


def test_map_dimensions_api_with_ocr_items_only():
    payload = [
        {'text': 'width 12 mm', 'confidence': 0.9},
        {'text': 'height 34 mm', 'confidence': 0.9},
        {'text': 'depth 56 mm', 'confidence': 0.9},
    ]

    res = client.post(
        '/api/v1/ocr/map-dimensions',
        data={'ocr_items': json.dumps(payload)},
    )

    assert res.status_code == 200
    assert res.json()['mapped_dimensions_mm'] == {'width': 12.0, 'height': 34.0, 'depth': 56.0}


def test_map_dimensions_api_uses_extractor_when_ocr_items_missing(monkeypatch):
    monkeypatch.setattr(
        'app.main.extract_dimension_candidates',
        lambda _: [
            {'text': 'W 1 cm', 'confidence': 0.9},
            {'text': 'H 2 cm', 'confidence': 0.9},
            {'text': 'D 3 cm', 'confidence': 0.9},
        ],
    )

    res = client.post(
        '/api/v1/ocr/map-dimensions',
        files={'file': ('sample.png', _png_1x1_bytes(), 'image/png')},
    )

    assert res.status_code == 200
    assert res.json()['mapped_dimensions_mm'] == {'width': 10.0, 'height': 20.0, 'depth': 30.0}


def test_map_dimensions_api_requires_input():
    res = client.post('/api/v1/ocr/map-dimensions')
    assert res.status_code == 400
