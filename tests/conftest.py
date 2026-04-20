"""
Root conftest.py for test configuration.

Registers pytest markers and provides shared fixtures.
"""

import sys
import os

# Add project root to path for imports
# We need to add the parent directory (project root) to the path
# so tests can import modules like routing_2026, geo_2026, etc.
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _project_root)

import pytest
import numpy as np


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
    config.addinivalue_line("markers", "terrain: Mark test as Phase 3 terrain penalty test")

    # Phase 4 markers
    config.addinivalue_line("markers", "water: Tests for water body penalty routing")

    # Integration test markers
    config.addinivalue_line("markers", "integration: Integration tests for end-to-end workflows")


@pytest.fixture
def elevation_grid():
    """
    Mock elevation grid for terrain penalty testing.

    Returns:
        numpy.ndarray: 4x4 elevation grid in meters representing
                      simple terrain with saddle point for testing
                      slope calculations and routing decisions.
    """
    return np.array([
        [100, 100, 100, 100],  # Row 0: flat top edge
        [100, 150, 150, 100],  # Row 1: shallow climb from left
        [100, 150, 150, 100],  # Row 2: shallow climb from left
        [100, 100, 100, 100],  # Row 3: flat bottom edge
    ])


# =============================================================================
# Phase 6: GUI Routing Integration Fixtures
# =============================================================================

# Import geospatial modules (may fail in headless environments - fixtures handle this)
try:
    from screen_2026 import Screen
    from routing_2026 import RoutingNetwork
    _SCREEN_AVAILABLE = True
except Exception:
    _SCREEN_AVAILABLE = False


@pytest.fixture
def mock_screen():
    """
    Create mock screen with world file for coordinate transformations.

    World file: [a, d, b, e, c, f] where:
    - screen_to_world: x_w = a*x + b*y + c, y_w = d*x + e*y + f
    - This world file maps screen pixels to UTM 32V coordinates (Norway)

    Returns:
        Screen: Mock screen instance with world file and EPSG set
    """
    if not _SCREEN_AVAILABLE:
        pytest.skip("Screen module not available")

    from unittest.mock import patch

    with patch('screen_2026.tkinter.Tk'):
        screen = Screen()
        # World file for coordinate transforms
        screen._world_file = [10.0, 0.0, 0.0, -10.0, 600000.0, 6650000.0]
        screen._epsg = 32632  # UTM Zone 32V (Norway)

        return screen


@pytest.fixture
def routing_network():
    """
    Create a small synthetic routing network for testing.

    Creates a linear chain of 5 nodes with bidirectional edges.

    Returns:
        RoutingNetwork: Small test network with EPSG 32632
    """
    if not _SCREEN_AVAILABLE:
        pytest.skip("RoutingNetwork module not available")

    network = RoutingNetwork()

    # Add nodes in a line
    for i in range(5):
        node_id = f'test_{i}'
        x = 600000.0 + i * 100
        y = 6650000.0 + i * 50
        network.add_node(node_id, x, y)

    # Add bidirectional edges
    for i in range(4):
        source = f'test_{i}'
        target = f'test_{i+1}'
        network.add_edge(source, target, weight=100.0)
        network.add_edge(target, source, weight=100.0)

    network.epsg = 32632

    return network


@pytest.fixture
def screen_with_network(mock_screen, routing_network):
    """
    Create mock screen with attached routing network.

    Combines mock_screen and routing_network fixtures for integration tests.

    Returns:
        tuple: (screen, network) where screen._route_network is set to network
    """
    # Assign network to screen
    mock_screen.set_route_network(routing_network)

    return (mock_screen, routing_network)