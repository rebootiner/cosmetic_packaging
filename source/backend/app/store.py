from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
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
