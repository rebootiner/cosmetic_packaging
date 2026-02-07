from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app, file_storage, job_store
from app.store import LocalFileStorage


client = TestClient(app)


def setup_function():
    job_store.clear()


def test_create_job_success(tmp_path, monkeypatch):
    monkeypatch.setattr('app.main.file_storage', LocalFileStorage(str(tmp_path)))

    res = client.post(
        '/api/v1/jobs',
        files={'file': ('sample.png', b'fake image bytes', 'image/png')},
    )

    assert res.status_code == 201
    data = res.json()
    assert data['status'] == 'uploaded'
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


def test_get_job_status_success(tmp_path, monkeypatch):
    monkeypatch.setattr('app.main.file_storage', LocalFileStorage(str(tmp_path)))
    create_res = client.post(
        '/api/v1/jobs',
        files={'file': ('sample.jpg', b'image bytes', 'image/jpeg')},
    )
    job_id = create_res.json()['job_id']

    res = client.get(f'/api/v1/jobs/{job_id}')

    assert res.status_code == 200
    data = res.json()
    assert data['job_id'] == job_id
    assert data['status'] == 'uploaded'
    assert data['filename'] == 'sample.jpg'
    assert data['content_type'] == 'image/jpeg'
    assert data['size'] == len(b'image bytes')
    assert 'created_at' in data


def test_get_job_status_not_found():
    res = client.get('/api/v1/jobs/not-found-id')

    assert res.status_code == 404
    assert res.json()['detail'] == 'Job not found'
