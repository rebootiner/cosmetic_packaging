from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app, job_store
from app.store import LocalFileStorage


client = TestClient(app)


def setup_function():
    job_store.clear()


def test_create_job_success(tmp_path, monkeypatch):
    monkeypatch.setattr('app.main.file_storage', LocalFileStorage(str(tmp_path)))

    # 1x1 transparent PNG
    png_bytes = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0bIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    )

    res = client.post(
        '/api/v1/jobs',
        files={'file': ('sample.png', png_bytes, 'image/png')},
    )

    assert res.status_code == 201
    data = res.json()
    assert data['status'] == 'processed'
    assert 'job_id' in data

    saved_files = list(Path(tmp_path).iterdir())
    assert len(saved_files) == 1
    assert saved_files[0].suffix == '.png'


def test_create_job_missing_file():
    res = client.post('/api/v1/jobs')
    assert res.status_code == 422


def test_create_job_non_image_rejected():
    res = client.post(
        '/api/v1/jobs',
        files={'file': ('sample.txt', b'not image', 'text/plain')},
    )

    assert res.status_code == 400
    assert res.json()['detail'] == 'Only image uploads are allowed'


def test_get_job_status_success_includes_quality_metrics(tmp_path, monkeypatch):
    monkeypatch.setattr('app.main.file_storage', LocalFileStorage(str(tmp_path)))

    png_bytes = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0bIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    )

    create_res = client.post(
        '/api/v1/jobs',
        files={'file': ('sample.png', png_bytes, 'image/png')},
    )
    job_id = create_res.json()['job_id']

    res = client.get(f'/api/v1/jobs/{job_id}')

    assert res.status_code == 200
    data = res.json()
    assert data['job_id'] == job_id
    assert data['status'] == 'processed'
    assert data['filename'] == 'sample.png'
    assert data['content_type'] == 'image/png'
    assert data['size'] == len(png_bytes)
    assert 'created_at' in data
    assert data['quality_metrics'] is not None
    assert data['quality_metrics']['preprocess']['format'] == 'png'
    assert 'foreground_ratio' in data['quality_metrics']['segmentation']
    assert data['error_message'] is None


def test_create_job_pipeline_failure_marks_failed(tmp_path, monkeypatch):
    monkeypatch.setattr('app.main.file_storage', LocalFileStorage(str(tmp_path)))
    monkeypatch.setattr('app.main.segment_image', lambda _: (_ for _ in ()).throw(RuntimeError('seg failed')))

    png_bytes = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0bIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    )

    create_res = client.post(
        '/api/v1/jobs',
        files={'file': ('sample.png', png_bytes, 'image/png')},
    )

    assert create_res.status_code == 201
    assert create_res.json()['status'] == 'failed'
    job_id = create_res.json()['job_id']

    res = client.get(f'/api/v1/jobs/{job_id}')
    assert res.status_code == 200
    data = res.json()
    assert data['status'] == 'failed'
    assert data['quality_metrics'] is None
    assert data['error_message'] == 'seg failed'


def test_get_job_status_not_found():
    res = client.get('/api/v1/jobs/not-found-id')

    assert res.status_code == 404
    assert res.json()['detail'] == 'Job not found'
