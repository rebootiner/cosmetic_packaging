from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import threading


@dataclass
class JobMeta:
    job_id: str
    status: str
    filename: str
    content_type: str
    size: int
    file_path: str
    created_at: datetime
    quality_metrics: dict[str, Any] | None = None
    error_message: str | None = None


class InMemoryJobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, JobMeta] = {}
        self._lock = threading.Lock()

    def create(self, meta: JobMeta) -> None:
        with self._lock:
            self._jobs[meta.job_id] = meta

    def get(self, job_id: str) -> JobMeta | None:
        with self._lock:
            return self._jobs.get(job_id)

    def update(self, job_id: str, **fields: Any) -> JobMeta | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return None
            for key, value in fields.items():
                if hasattr(job, key):
                    setattr(job, key, value)
            return job

    def clear(self) -> None:
        with self._lock:
            self._jobs.clear()


class LocalFileStorage:
    def __init__(self, base_dir: str) -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, job_id: str, filename: str, content: bytes) -> str:
        suffix = Path(filename).suffix
        destination = self.base_dir / f"{job_id}{suffix}"
        destination.write_bytes(content)
        return str(destination)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)
