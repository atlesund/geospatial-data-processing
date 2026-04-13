"""
Root conftest.py for test configuration.

Registers pytest markers and provides shared fixtures.
"""

import pytest


def pytest_configure(config):
    """Register pytest markers for testing."""
    # Phase 1 markers
    config.addinivalue_line("markers", "navigation: Tests for map navigation and zoom")
    config.addinivalue_line("markers", "selection: Tests for feature selection")
    config.addinivalue_line("markers", "digitizing: Tests for digitizing tools")

    # Phase 2 markers
    config.addinivalue_line("markers", "routing: Tests for routing network construction")
    config.addinivalue_line("markers", "osmnx: Tests for OSM data integration")
    config.addinivalue_line("markers", "trails: Tests for trail polyline conversion")
    config.addinivalue_line("markers", "terrain: Tests for terrain mesh generation")