from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app, job_store
from app.store import LocalFileStorage


client = TestClient(app)


def _png_1x1_bytes() -> bytes:
    return (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0bIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    )


def _create_sample_job(tmp_path, monkeypatch) -> str:
    monkeypatch.setattr('app.main.file_storage', LocalFileStorage(str(tmp_path)))
    create_res = client.post(
        '/api/v1/jobs',
        files={'file': ('sample.png', _png_1x1_bytes(), 'image/png')},
    )
    assert create_res.status_code == 201
    return create_res.json()['job_id']


def setup_function():
    job_store.clear()


def test_create_job_success(tmp_path, monkeypatch):
    monkeypatch.setattr('app.main.file_storage', LocalFileStorage(str(tmp_path)))

    res = client.post(
        '/api/v1/jobs',
        files={'file': ('sample.png', _png_1x1_bytes(), 'image/png')},
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
    job_id = _create_sample_job(tmp_path, monkeypatch)

    res = client.get(f'/api/v1/jobs/{job_id}')

    assert res.status_code == 200
    data = res.json()
    assert data['job_id'] == job_id
    assert data['status'] == 'processed'
    assert data['filename'] == 'sample.png'
    assert data['content_type'] == 'image/png'
    assert data['size'] == len(_png_1x1_bytes())
    assert 'created_at' in data

    assert data['quality_metrics'] is not None
    assert data['quality_metrics']['preprocess']['format'] == 'png'
    assert 'foreground_ratio' in data['quality_metrics']['segmentation']
    assert 'overall_score' in data['quality_metrics']['shape_engine']

    assert data['dimensions_mm'] is not None
    assert set(data['dimensions_mm'].keys()) == {'width', 'height', 'depth'}
    assert data['dimensions_mm']['width'] > 0
    assert data['dimensions_mm']['height'] > 0
    assert data['dimensions_mm']['depth'] > 0

    assert data['volume_mm3'] is not None
    assert data['volume_mm3'] > 0

    assert data['shape_proxy'] is not None
    assert 'shape_family' in data['shape_proxy']
    assert 'aspect_ratio' in data['shape_proxy']

    assert data['error_message'] is None


def test_get_job_result_success_and_shape_proxy_schema_keys(tmp_path, monkeypatch):
    job_id = _create_sample_job(tmp_path, monkeypatch)

    res = client.get(f'/api/v1/jobs/{job_id}/result')

    assert res.status_code == 200
    data = res.json()
    assert data['job_id'] == job_id
    assert data['status'] == 'processed'
    assert data['source_type'] == 'image'
    assert data['dimensions_mm'] is not None
    assert data['quality_metrics'] is not None
    assert data['shape_proxy'] is not None
    assert 'compactness' in data['shape_proxy']
    assert 'fill_ratio' in data['shape_proxy']
    assert 'mask_resolution' in data['shape_proxy']


def test_get_job_result_not_found():
    res = client.get('/api/v1/jobs/not-found-id/result')

    assert res.status_code == 404
    assert res.json()['detail'] == 'Job not found'


def test_patch_dimensions_updates_volume_and_user_corrections(tmp_path, monkeypatch):
    job_id = _create_sample_job(tmp_path, monkeypatch)

    patch_res = client.patch(
        f'/api/v1/jobs/{job_id}/dimensions',
        json={'width': 12.3, 'depth': 4.5, 'height': 6.7, 'max_diameter': 10.0},
    )

    assert patch_res.status_code == 200
    patched = patch_res.json()
    dims = patched['dimensions_mm']
    assert dims['width'] == 12.3
    assert dims['depth'] == 4.5
    assert dims['height'] == 6.7
    assert dims['max_diameter'] == 10.0
    assert round(dims['width'] * dims['height'] * dims['depth'], 3) == patched['volume_mm3']
    assert patched['status'] == 'processed'

    status_res = client.get(f'/api/v1/jobs/{job_id}')
    assert status_res.status_code == 200
    status_data = status_res.json()
    assert status_data['user_corrections'] is not None
    assert status_data['user_corrections'][-1]['fields'] == ['width', 'depth', 'height', 'max_diameter']


def test_patch_dimensions_clamp_boundaries(tmp_path, monkeypatch):
    job_id = _create_sample_job(tmp_path, monkeypatch)

    patch_res = client.patch(
        f'/api/v1/jobs/{job_id}/dimensions',
        json={'width': -1, 'depth': 10001, 'height': 3.3339, 'max_diameter': -99},
    )

    assert patch_res.status_code == 200
    data = patch_res.json()
    assert data['dimensions_mm']['width'] == 0.0
    assert data['dimensions_mm']['depth'] == 10000.0
    assert data['dimensions_mm']['height'] == 3.334
    assert data['dimensions_mm']['max_diameter'] == 0.0


def test_create_job_pipeline_failure_marks_failed(tmp_path, monkeypatch):
    monkeypatch.setattr('app.main.file_storage', LocalFileStorage(str(tmp_path)))
    monkeypatch.setattr('app.main.segment_image', lambda _: (_ for _ in ()).throw(RuntimeError('seg failed')))

    create_res = client.post(
        '/api/v1/jobs',
        files={'file': ('sample.png', _png_1x1_bytes(), 'image/png')},
    )

    assert create_res.status_code == 201
    assert create_res.json()['status'] == 'failed'
    job_id = create_res.json()['job_id']

    res = client.get(f'/api/v1/jobs/{job_id}')
    assert res.status_code == 200
    data = res.json()
    assert data['status'] == 'failed'
    assert data['quality_metrics'] is None
    assert data['dimensions_mm'] is None
    assert data['volume_mm3'] is None
    assert data['shape_proxy'] is None
    assert data['error_message'] == 'seg failed'


def test_shape_proxy_fill_ratio_clamp_boundary(tmp_path, monkeypatch):
    monkeypatch.setattr('app.main.file_storage', LocalFileStorage(str(tmp_path)))
    monkeypatch.setattr(
        'app.main.segment_image',
        lambda _: {
            'mask_width': 64,
            'mask_height': 64,
            'foreground_ratio': 9.9,
            'background_ratio': -8.9,
            'confidence': 0.5,
            'algorithm': 'mock',
        },
    )

    create_res = client.post(
        '/api/v1/jobs',
        files={'file': ('sample.png', _png_1x1_bytes(), 'image/png')},
    )
    job_id = create_res.json()['job_id']

    res = client.get(f'/api/v1/jobs/{job_id}/result')
    assert res.status_code == 200
    assert res.json()['shape_proxy']['fill_ratio'] == 1.0


def test_get_job_status_not_found():
    res = client.get('/api/v1/jobs/not-found-id')

    assert res.status_code == 404
    assert res.json()['detail'] == 'Job not found'
