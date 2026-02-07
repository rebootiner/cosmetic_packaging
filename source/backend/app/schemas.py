from datetime import datetime
from typing import Any

from pydantic import BaseModel


class JobCreateResponse(BaseModel):
    job_id: str
    status: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    filename: str
    content_type: str
    size: int
    created_at: datetime
    quality_metrics: dict[str, Any] | None = None
    error_message: str | None = None
