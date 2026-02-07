from app.dimension_mapper import map_dimensions


def test_map_dimensions_normal_success():
    items = [
        {'text': 'W 10 mm', 'confidence': 0.9},
        {'text': 'H 20 mm', 'confidence': 0.92},
        {'text': 'D 5 mm', 'confidence': 0.88},
    ]

    result = map_dimensions(items)
    assert result['mapped_dimensions_mm'] == {'width': 10.0, 'height': 20.0, 'depth': 5.0}
    assert result['warnings'] == []


def test_map_dimensions_conflict_uses_higher_confidence():
    items = [
        {'text': 'width 30 mm', 'confidence': 0.5},
        {'text': 'width 25 mm', 'confidence': 0.95},
        {'text': 'height 10 mm', 'confidence': 0.9},
        {'text': 'depth 8 mm', 'confidence': 0.9},
    ]

    result = map_dimensions(items)
    assert result['mapped_dimensions_mm']['width'] == 25.0
    assert any(w.startswith('conflict:width:') for w in result['warnings'])


def test_map_dimensions_partial_success_missing_required_warning():
    items = [
        {'text': 'height 20 mm', 'confidence': 0.8},
        {'text': 'diameter 45 mm', 'confidence': 0.9},
    ]

    result = map_dimensions(items)
    assert result['mapped_dimensions_mm']['height'] == 20.0
    assert result['mapped_dimensions_mm']['max_diameter'] == 45.0
    assert any(w.startswith('missing_required:') for w in result['warnings'])


def test_map_dimensions_filters_false_positives():
    items = [
        {'text': 'v2.0', 'confidence': 0.99},
        {'text': '12.34.56', 'confidence': 0.99},
        {'text': 'W 11 mm', 'confidence': 0.7},
        {'text': 'H 22 mm', 'confidence': 0.8},
        {'text': 'D 33 mm', 'confidence': 0.85},
    ]

    result = map_dimensions(items)
    assert result['mapped_dimensions_mm'] == {'width': 11.0, 'height': 22.0, 'depth': 33.0}
    assert 'v2.0' not in str(result['mapping_items'])
    assert '12.34.56' not in str(result['mapping_items'])
