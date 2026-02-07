from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile

from .config import settings
from .db import check_db_connection
from .image_pipeline import preprocess_image, segment_image
from .schemas import JobCreateResponse, JobStatusResponse
from .store import InMemoryJobStore, JobMeta, LocalFileStorage, utcnow

app = FastAPI(title=settings.app_name)

job_store = InMemoryJobStore()
file_storage = LocalFileStorage(settings.upload_dir)


@app.get('/health')
def health() -> dict:
    return {'status': 'ok', 'service': settings.app_name}


@app.get('/health/db')
def health_db() -> dict:
    ok = check_db_connection()
    return {'status': 'ok' if ok else 'error', 'database': ok}


@app.post('/api/v1/jobs', response_model=JobCreateResponse, status_code=201)
async def create_job(file: UploadFile = File(...)) -> JobCreateResponse:
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail='Only image uploads are allowed')

    content = await file.read()
    job_id = str(uuid4())
    file_path = file_storage.save(job_id=job_id, filename=file.filename or 'upload.bin', content=content)

    meta = JobMeta(
        job_id=job_id,
        status='processing',
        filename=file.filename or 'upload.bin',
        content_type=file.content_type,
        size=len(content),
        file_path=file_path,
        created_at=utcnow(),
    )
    job_store.create(meta)

    try:
        preprocess_meta = preprocess_image(content)
        segment_meta = segment_image(content)
        quality_metrics = {
            'preprocess': preprocess_meta,
            'segmentation': segment_meta,
        }
        job_store.update(job_id, status='processed', quality_metrics=quality_metrics, error_message=None)
    except Exception as exc:
        job_store.update(job_id, status='failed', error_message=str(exc), quality_metrics=None)

    latest = job_store.get(job_id) or meta
    return JobCreateResponse(job_id=job_id, status=latest.status)


@app.get('/api/v1/jobs/{job_id}', response_model=JobStatusResponse)
def get_job(job_id: str) -> JobStatusResponse:
    meta = job_store.get(job_id)
    if meta is None:
        raise HTTPException(status_code=404, detail='Job not found')

    return JobStatusResponse(
        job_id=meta.job_id,
        status=meta.status,
        filename=meta.filename,
        content_type=meta.content_type,
        size=meta.size,
        created_at=meta.created_at,
        quality_metrics=meta.quality_metrics,
        error_message=meta.error_message,
    )
