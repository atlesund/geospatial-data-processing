"""
Pytest configuration and fixtures for Phase 1 map interaction and user selection tests.
"""

import sys
import os

# Add project root to path for imports
# We're in a worktree, so need to go up multiple levels to find the project root
_worktree_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, _worktree_root)

import pytest


# Import geo_2026 for Screen class access
import geo_2026 as geo


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers for Phase 1 tests."""
    config.addinivalue_line("markers", "screen: Tests related to Screen class functionality")
    config.addinivalue_line("markers", "navigation: Tests for pan/zoom navigation operations")
    config.addinivalue_line("markers", "coord_display: Tests for coordinate display functionality")
    config.addinivalue_line("markers", "route_selection: Tests for route point selection on map")


@pytest.fixture
def mock_world_file():
    """
    Mock world file with UTM 32V affine transformation values.

    Returns:
        list: Affine transformation tuple [pixel_width, rotation_x, rotation_y, pixel_height, top_left_x, top_left_y]
    """
    return [12.0, 0.0, 0.0, -12.0, 450000.0, 6500000.0]


@pytest.fixture
def mock_epsg():
    """
    Mock EPSG code for decimal degree testing.

    Returns:
        int: EPSG code 4326 (WGS84 decimal degrees)
    """
    return 4326


@pytest.fixture
def screen():
    """
    Create a Screen instance with default dimensions (800x600).

    Returns:
        geo.Screen: Screen instance with default configuration
    """
    # Create Screen with default columns=800, rows=600
    screen_instance = geo.Screen(rows=600, columns=800)
    yield screen_instance

    # Cleanup: destroy tkinter window
    try:
        screen_instance._root.destroy()
    except:
        pass


@pytest.fixture
def screen_with_world_file(mock_world_file, mock_epsg):
    """
    Create a Screen instance with mock world file and EPSG set.

    Args:
        mock_world_file: Affine transformation tuple from fixture
        mock_epsg: EPSG code from fixture

    Returns:
        geo.Screen: Screen instance with world file metadata
    """
    # Create Screen instance
    screen_instance = geo.Screen(rows=600, columns=800)

    # Set world file and EPSG
    screen_instance._world_file = mock_world_file
    screen_instance._epsg = mock_epsg

    yield screen_instance

    # Cleanup: destroy tkinter window
    try:
        screen_instance._root.destroy()
    except:
        pass