# Phase 01 Validation Strategy

**Phase:** 1 - Map Interaction & User Selection
**Created:** 2026-04-12
**Validation Framework:** pytest

## Validation Goals

Ensure users can:
1. Select route endpoints through interactive map interface
2. Navigate maps with pan/zoom controls
3. View selected coordinates in decimal degrees format

## Test Requirements

### Test Files to Create
| File | Purpose | Tests |
|------|---------|-------|
| `tests/test_route_selector.py` | Screen integration tests for route selection | MAP-01, MAP-02, MAP-03, MAP-04 |
| `tests/test_coordinate_transform.py` | Coordinate transformation unit tests | MAP-05 |
| `tests/conftest.py` | Shared fixtures for pytest | All |

### Test Fixtures Needed
```python
# Standard Screen fixture with world file
@pytest.fixture
def screen_with_world():
    """Screen instance with attached georeferenced image"""
    # Requires: valid PNG+PGW test data files
    pass

# Mock tkinter event fixture
@pytest.fixture
def mock_mouse_event():
    """Simulate mouse click/drag/wheel events"""
    pass
```

## Success Criteria

All automated tests must pass before phase completion:

```bash
# Full suite
pytest tests/ -v

# Individual tests (per plan verification)
pytest tests/test_route_selector.py::test_select_start_point -x
pytest tests/test_route_selector.py::test_select_end_point -x
pytest tests/test_route_selector.py::test_pan_functionality -x
pytest tests/test_route_selector.py::test_zoom_functionality -x
pytest tests/test_coordinate_transform.py::test_screen_to_decimal_degrees -x
```

## Coverage Requirements

| Requirement | Test Type | Command |
|-------------|-----------|---------|
| MAP-01 (start point selection) | integration | `pytest tests/test_route_selector.py::test_select_start_point -x` |
| MAP-02 (end point selection) | integration | `pytest tests/test_route_selector.py::test_select_end_point -x` |
| MAP-03 (map pan) | integration | `pytest tests/test_route_selector.py::test_pan_functionality -x` |
| MAP-04 (map zoom) | integration | `pytest tests/test_route_selector.py::test_zoom_functionality -x` |
| MAP-05 (decimal degree display) | unit | `pytest tests/test_coordinate_transform.py::test_screen_to_decimal_degrees -x` |

---

*Phase: 01-map-interaction-user-selection*
*Validation strategy: 2026-04-12*