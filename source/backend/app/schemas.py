from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class OCRResultItemSchema(BaseModel):
    text: str
    value: float
    unit: str | None = None
    bbox: list[int] | None = None
    confidence: float


class OCRExtractionResponse(BaseModel):
    items: list[OCRResultItemSchema]
    engine_available: bool
    message: str


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
    dimensions_mm: dict[str, float] | None = None
    volume_mm3: float | None = None
    shape_proxy: dict[str, Any] | None = None
    error_message: str | None = None
    user_corrections: list[dict[str, Any]] | None = None


class GeometryOutput(BaseModel):
    job_id: str
    status: str
    dimensions_mm: dict[str, float] | None = None
    volume_mm3: float | None = None
    shape_proxy: dict[str, Any] | None = None
    quality_metrics: dict[str, Any] | None = None
    error_message: str | None = None
    source_type: str = 'image'


class DimensionPatchRequest(BaseModel):
    width: float
    depth: float
    height: float
    max_diameter: float | None = None


class OCRItemInput(BaseModel):
    text: str = ''
    value: float | None = None
    unit: str | None = None
    confidence: float = 0.0


class DimensionMappingItem(BaseModel):
    target: str
    value_mm: float
    confidence: float
    source_text: str
    source_index: int
    reason: str


class OCRMapDimensionsResponse(BaseModel):
    mapped_dimensions_mm: dict[str, float] = Field(default_factory=dict)
    mapping_items: list[DimensionMappingItem] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
