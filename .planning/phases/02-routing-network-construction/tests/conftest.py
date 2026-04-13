"""
Test fixtures for Phase 2: Routing Network Construction

Provides mock data and fixtures for testing routing network components including:
- networkx graph structures
- OSM-like graph data
- Trail vector polylines
"""

import sys
import os

# Add project root to path for imports
# From .planning/phases/02-routing-network-construction/tests/conftest.py
# Need to go up 5 levels to reach project root: tests -> 02-routing-network-construction -> phases -> .planning -> project root
_worktree_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, _worktree_root)

# Import dependencies
import pytest
import networkx as nx
import scipy
import osmnx as ox

# Import geo_2026 lazily in fixtures to avoid top-level import errors


def pytest_configure(config):
    """Register pytest markers for Phase 2 tests."""
    config.addinivalue_line("markers", "routing: Tests for routing network construction")
    config.addinivalue_line("markers", "osmnx: Tests for OSM data integration")
    config.addinivalue_line("markers", "trails: Tests for trail polyline conversion")
    config.addinivalue_line("markers", "terrain: Tests for terrain mesh generation")


@pytest.fixture
def mock_routing_network():
    """Creates a simple networkx.Graph for routing network testing.

    Returns:
        dict: Plain dict with graph, EPSG code, and node coordinates
        {
            'graph': networkx.Graph,
            'epsg': 25832,
            'node_coords': {node_id: (x, y), ...}
        }
    """
    G = nx.Graph()

    # Nodes with UTM 32V coordinates (southern Norway)
    nodes = {
        0: (450000.0, 6500000.0),
        1: (450100.0, 6500100.0),
        2: (450200.0, 6500000.0),
        3: (450100.0, 6500100.0)
    }

    # Add nodes with coordinate data
    for node_id, coords in nodes.items():
        G.add_node(node_id, x=coords[0], y=coords[1])

    # Add bidirectional edges with weight=100 (100m segments)
    G.add_edge(0, 1, weight=100)
    G.add_edge(1, 2, weight=100)
    G.add_edge(2, 3, weight=100)
    G.add_edge(3, 0, weight=100)

    return {
        'graph': G,
        'epsg': 25832,
        'node_coords': nodes
    }


@pytest.fixture
def mock_osm_graph():
    """Creates mock osmnx-like MultiDiGraph structure.

    Returns:
        networkx.MultiDiGraph: Mock OSM graph with ~5 nodes and ~6 edges
    """
    G = nx.MultiDiGraph()

    # Nodes with integer IDs and projected coordinates (UTM 32V)
    G.add_node(0, x=450000.0, y=6500000.0)
    G.add_node(1, x=450100.0, y=6500100.0)
    G.add_node(2, x=450200.0, y=6500000.0)
    G.add_node(3, x=450300.0, y=6500100.0)
    G.add_node(4, x=450400.0, y=6500000.0)

    # Edges with OSM-like attributes
    G.add_edge(0, 1, 0, length=100.5, highway='path')
    G.add_edge(1, 0, 0, length=100.5, highway='path')
    G.add_edge(1, 2, 0, length=100.3, highway='footway')
    G.add_edge(2, 1, 0, length=100.3, highway='footway')
    G.add_edge(2, 3, 0, length=100.7, highway='track')
    G.add_edge(3, 2, 0, length=100.7, highway='track')
    G.add_edge(3, 4, 0, length=100.2, highway='path')
    G.add_edge(4, 3, 0, length=100.2, highway='path')

    # Set graph CRS attributes (osmnx convention)
    G.graph['crs'] = 'EPSG:25832'
    G.graph['name'] = 'mock_osm_graph'

    return G


@pytest.fixture
def mock_trail_vector():
    """Creates a geo.Vector instance with trail polylines.

    Returns:
        geo.Vector: Vector instance with 2-3 trail polylines, EPSG 25832
    """
    # Import geo_2026 at fixture execution time
    import geo_2026 as geo

    # Create Vector with POLYLINE geometry type
    trail_vector = geo.Vector(geometry_type='POLYLINE')
    trail_vector._epsg = 25832

    # Define trail polylines that form a connected network (UTM 32V)
    trail1 = [
        (450000.0, 6500000.0),
        (450100.0, 6500100.0),
        (450200.0, 6500000.0)
    ]

    trail2 = [
        (450200.0, 6500000.0),
        (450300.0, 6500100.0),
        (450400.0, 6500000.0)
    ]

    trail3 = [
        (450100.0, 6500100.0),
        (450100.0, 6500200.0),
        (450200.0, 6500200.0)
    ]

    # Add polylines to the vector
    trail_vector.insert([trail1])
    trail_vector.insert([trail2])
    trail_vector.insert([trail3])

    # Add some trail attributes
    for i in range(trail_vector.record_count):
        trail_vector.update_attribute(i, 'name', f'Trail_{i+1}')
        trail_vector.update_attribute(i, 'type', 'hiking')

    return trail_vector


@pytest.fixture
def mock_world_file():
    """Provides affine transformation from world file for raster georeferencing.

    Returns:
        list: Affine transformation parameters [pixel_width, row_rotation, etc.]
    """
    return [12.0, 0.0, 0.0, -12.0, 450000.0, 6500000.0]