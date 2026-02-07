from __future__ import annotations

from typing import Any


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def build_shape_proxy(preprocess: dict[str, Any], segment: dict[str, Any]) -> dict[str, Any]:
    width_px = int(preprocess.get('width') or 0)
    height_px = int(preprocess.get('height') or 0)
    mask_width = int(segment.get('mask_width') or 0)
    mask_height = int(segment.get('mask_height') or 0)
    fg_ratio = float(segment.get('foreground_ratio') or 0.0)

    if width_px <= 0 or height_px <= 0:
        aspect_ratio = 1.0
    else:
        aspect_ratio = round(width_px / height_px, 4)

    fill_ratio = round(_clamp(fg_ratio, 0.0, 1.0), 4)

    if 0.9 <= aspect_ratio <= 1.1:
        shape_family = 'cylindrical-like'
    elif aspect_ratio > 1.1:
        shape_family = 'horizontal-prismatic-like'
    else:
        shape_family = 'vertical-prismatic-like'

    if fill_ratio < 0.35:
        compactness = 'low'
    elif fill_ratio < 0.7:
        compactness = 'medium'
    else:
        compactness = 'high'

    return {
        'shape_family': shape_family,
        'compactness': compactness,
        'aspect_ratio': aspect_ratio,
        'fill_ratio': fill_ratio,
        'mask_resolution': {
            'width': mask_width,
            'height': mask_height,
        },
    }


def compute_dimensions(preprocess: dict[str, Any], segment: dict[str, Any]) -> dict[str, float]:
    # MVP assumption: fixed calibration factor (mm per pixel).
    mm_per_px = 0.2

    width_px = float(preprocess.get('width') or 0)
    height_px = float(preprocess.get('height') or 0)
    fg_ratio = _clamp(float(segment.get('foreground_ratio') or 0.0), 0.0, 1.0)

    width_mm = round(max(width_px * mm_per_px, 0.0), 2)
    height_mm = round(max(height_px * mm_per_px, 0.0), 2)
    # depth proxy from foreground density and smaller axis
    depth_mm = round(max(min(width_mm, height_mm) * (0.35 + 0.65 * fg_ratio), 0.0), 2)

    return {
        'width': width_mm,
        'height': height_mm,
        'depth': depth_mm,
    }


def compute_quality_metrics(preprocess: dict[str, Any], segment: dict[str, Any]) -> dict[str, Any]:
    width = preprocess.get('width')
    height = preprocess.get('height')
    has_geometry = bool(width and height and width > 0 and height > 0)

    fg_ratio = _clamp(float(segment.get('foreground_ratio') or 0.0), 0.0, 1.0)
    seg_confidence = _clamp(float(segment.get('confidence') or 0.0), 0.0, 1.0)

    calibration_reliability = 0.7 if has_geometry else 0.2
    edge_stability = round(1.0 - abs(fg_ratio - 0.5) * 1.4, 4)
    edge_stability = _clamp(edge_stability, 0.0, 1.0)

    overall = round((seg_confidence * 0.5) + (edge_stability * 0.3) + (calibration_reliability * 0.2), 4)

    return {
        'segmentation_confidence': round(seg_confidence, 4),
        'calibration_reliability': round(calibration_reliability, 4),
        'edge_stability': round(edge_stability, 4),
        'overall_score': round(overall, 4),
    }
