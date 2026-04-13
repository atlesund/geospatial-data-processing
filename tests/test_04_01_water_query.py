"""
Tests for water feature query functionality.

Tests the load_water_features() function which queries OSM water features
and projects them to target CRS for penalty routing.
"""

import pytest

# Mock imports for headless testing environment
try:
    from routing_2026 import load_water_features
    IMPORT_AVAILABLE = True
except ImportError:
    IMPORT_AVAILABLE = False


@pytest.mark.water
def test_load_water_features_bbox_validation():
    """
    Validate bbox assertion (west < east and south < north).

    Tests that assertion prevents invalid bbox format, protecting against
    malformed input that would corrupt osmnx queries.
    """
    if not IMPORT_AVAILABLE:
        pytest.skip("routing_2026 import not available in headless environment")

    # Invalid bbox: west > east
    bbox_invalid = (10.0, 60.0, 5.0, 61.0)

    with pytest.raises(AssertionError) as exc_info:
        load_water_features(bbox_invalid, 25832)

    assert "west" in str(exc_info.value).lower()
    assert "east" in str(exc_info.value).lower()


@pytest.mark.water
def test_load_water_features_bbox_validation_reversed():
    """
    Validate bbox assertion (south > north is also invalid).
    """
    if not IMPORT_AVAILABLE:
        pytest.skip("routing_2026 import not available in headless environment")

    # Invalid bbox: south > north
    bbox_invalid = (10.0, 61.0, 11.0, 60.0)

    with pytest.raises(AssertionError) as exc_info:
        load_water_features(bbox_invalid, 25832)

    assert "south" in str(exc_info.value).lower()
    assert "north" in str(exc_info.value).lower()


@pytest.mark.water
@pytest.mark.skip(reason="Requires live OSM API - add pytest.mock for offline testing")
def test_crs_projection():
    """
    Validate that returned GeoDataFrames have correct CRS.

    Asserts that loaded water features are projected from EPSG:4326
    to the target EPSG coordinate system.
    """
    if not IMPORT_AVAILABLE:
        pytest.skip("routing_2026 import not available in headless environment")

    # Valid bbox for Norway area (small for testing)
    bbox = (10.0, 60.0, 10.5, 60.5)
    target_epsg = 25832

    lakes_gdf, rivers_gdf = load_water_features(bbox, target_epsg)

    if lakes_gdf is not None:
        assert lakes_gdf.crs.to_epsg() == target_epsg

    if rivers_gdf is not None:
        assert rivers_gdf.crs.to_epsg() == target_epsg


@pytest.mark.water
@pytest.mark.skip(reason="Requires mocking - TODO: add pytest-mock to requirements")
def test_query_fallback():
    """
    Validate graceful fallback on network failure.

    Confirms that function returns (None, None) when osmnx query fails,
    allowing routing to continue without water penalties.
    """
    if not IMPORT_AVAILABLE:
        pytest.skip("routing_2026 import not available in headless environment")