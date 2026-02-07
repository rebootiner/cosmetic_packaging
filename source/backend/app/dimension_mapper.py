import re
from typing import Any

_DIM_TOKENS = {
    'width': ('w', 'width', '가로'),
    'height': ('h', 'height', '세로'),
    'depth': ('d', 'depth', '길이'),
    'max_diameter': ('dia', 'diameter', 'ø', 'φ'),
}


def _to_mm(value: float, unit: str | None) -> tuple[float, str]:
    unit_norm = (unit or 'mm').strip().lower()
    if unit_norm in {'mm', 'millimeter', 'millimeters'}:
        return float(value), 'mm'
    if unit_norm in {'cm', 'centimeter', 'centimeters'}:
        return float(value) * 10.0, 'cm'
    if unit_norm in {'m', 'meter', 'meters'}:
        return float(value) * 1000.0, 'm'
    if unit_norm in {'in', 'inch', 'inches'}:
        return float(value) * 25.4, 'in'
    return float(value), unit_norm


def _is_false_positive(text: str) -> bool:
    lowered = text.strip().lower()
    if re.search(r'\bv\d+(?:\.\d+)+\b', lowered):
        return True
    if re.search(r'\b\d+\.\d+\.\d+\b', lowered):
        return True
    return False


def _extract_values(text: str) -> list[tuple[float, str | None]]:
    values: list[tuple[float, str | None]] = []
    for m in re.finditer(r'(?<![\w.])(\d+(?:\.\d+)?)(?:\s*)(mm|cm|m|in)?\b', text, re.IGNORECASE):
        values.append((float(m.group(1)), m.group(2)))
    return values


def _detect_target(text: str) -> str | None:
    lowered = text.lower()
    for target, tokens in _DIM_TOKENS.items():
        if any(re.search(rf'\b{re.escape(token)}\b', lowered) for token in tokens if token.isascii() and token.isalnum()):
            return target
        if any(token in lowered for token in tokens if not (token.isascii() and token.isalnum())):
            return target
    return None


def map_dimensions(ocr_items: list[dict[str, Any]]) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    warnings: list[str] = []

    for idx, item in enumerate(ocr_items):
        text = str(item.get('text') or '')
        if _is_false_positive(text):
            continue

        confidence = float(item.get('confidence', 0.0) or 0.0)

        if item.get('value') is not None:
            try:
                value = float(item['value'])
            except (TypeError, ValueError):
                value = None
            if value is not None:
                values = [(value, item.get('unit'))]
            else:
                values = _extract_values(text)
        else:
            values = _extract_values(text)

        if not values:
            continue

        target = _detect_target(text)

        # size / x / × formatted strings
        lowered = text.lower()
        if target is None and (' x ' in lowered or '×' in lowered or 'size' in lowered):
            values_for_size = values[:3]
            ordered_targets = ['width', 'height', 'depth']
            for i, (raw_value, raw_unit) in enumerate(values_for_size):
                mm_value, normalized_unit = _to_mm(raw_value, raw_unit)
                score = confidence + (0.3 if normalized_unit == 'mm' else 0.1)
                candidates.append(
                    {
                        'target': ordered_targets[i],
                        'value_mm': round(mm_value, 3),
                        'confidence': confidence,
                        'score': score,
                        'source_text': text,
                        'source_index': idx,
                        'reason': 'size-sequence',
                    }
                )
            continue

        chosen_target = target
        if chosen_target is None:
            # generic candidate is ignored to reduce over-mapping
            continue

        mm_value, normalized_unit = _to_mm(values[0][0], values[0][1])
        score = confidence + (0.3 if normalized_unit == 'mm' else 0.1) + 0.2
        candidates.append(
            {
                'target': chosen_target,
                'value_mm': round(mm_value, 3),
                'confidence': confidence,
                'score': score,
                'source_text': text,
                'source_index': idx,
                'reason': 'token-match',
            }
        )

    best: dict[str, dict[str, Any]] = {}
    for cand in candidates:
        target = cand['target']
        previous = best.get(target)
        if previous is None or cand['score'] > previous['score']:
            if previous is not None:
                warnings.append(f"conflict:{target}:replaced lower-confidence candidate")
            best[target] = cand
        elif cand['score'] == previous['score'] and cand['value_mm'] != previous['value_mm']:
            warnings.append(f"conflict:{target}:same-score different value")

    mapped_dimensions: dict[str, float] = {
        key: value['value_mm']
        for key, value in best.items()
        if key in {'width', 'height', 'depth', 'max_diameter'}
    }

    mapping_items = [
        {
            'target': item['target'],
            'value_mm': item['value_mm'],
            'confidence': item['confidence'],
            'source_text': item['source_text'],
            'source_index': item['source_index'],
            'reason': item['reason'],
        }
        for item in best.values()
    ]

    required = {'width', 'height', 'depth'}
    missing = sorted(required - mapped_dimensions.keys())
    if missing:
        warnings.append(f"missing_required:{','.join(missing)}")

    return {
        'mapped_dimensions_mm': mapped_dimensions,
        'mapping_items': sorted(mapping_items, key=lambda x: x['source_index']),
        'warnings': warnings,
    }
