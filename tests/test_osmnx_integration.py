"""
Unit tests for OSM data integration.

Tests verify osmnx trail loading, node extraction, edge weights,
and EPSG projection for hiking trails.
"""

import pytest
import sys
import os

# Add project root to path for imports
_test_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_test_dir))


@pytest.mark.osmnx
def test_load_osmnx_trails():
    """Test 1: load_osmnx_trails returns RoutingNetwork instance."""
    import routing_2026

    # Small bbox near Oslo (contains hiking trails)
    bbox = (59.90, 10.70, 59.92, 10.75)  # south, west, north, east

    routing_net = routing_2026.load_osmnx_trails(bbox)

    # Verify returns RoutingNetwork instance
    assert isinstance(routing_net, routing_2026.RoutingNetwork), \
        "load_osmnx_trails should return RoutingNetwork instance"

    # Verify graph is not empty (bbox should contain trails)
    assert routing_net.graph.number_of_nodes() > 0, \
        "RoutingNetwork should have nodes after loading OSM data"


@pytest.mark.osmnx
def test_osm_node_coordinates():
    """Test 2: Loading graph adds nodes with coordinates in node_coords dict."""
    import routing_2026

    # Small bbox near Oslo
    bbox = (59.90, 10.70, 59.92, 10.75)

    routing_net = routing_2026.load_osmnx_trails(bbox)

    # Verify node_coords dict is populated
    assert len(routing_net.node_coords) > 0, \
        "node_coords should contain OSM nodes"

    # Verify each node has (x, y) tuple coordinates
    for node_id, coords in routing_net.node_coords.items():
        assert isinstance(coords, tuple), \
            f"Node {node_id} coords should be tuple, got {type(coords)}"
        assert len(coords) == 2, \
            f"Node {node_id} coords should have 2 values (x, y)"
        assert isinstance(coords[0], (int, float)), \
            f"Node {node_id} x coordinate should be numeric"
        assert isinstance(coords[1], (int, float)), \
            f"Node {node_id} y coordinate should be numeric"


@pytest.mark.osmnx
def test_osm_edge_weights():
    """Test 3: Loading graph adds edges with length weights."""
    import routing_2026

    # Small bbox near Oslo
    bbox = (59.90, 10.70, 59.92, 10.75)

    routing_net = routing_2026.load_osmnx_trails(bbox)

    # Verify edges exist in graph
    assert routing_net.graph.number_of_edges() > 0, \
        "RoutingNetwork should have edges after loading OSM data"

    # Verify edges have weight attribute (length from OSM)
    for u, v, edge_data in routing_net.graph.edges(data=True):
        assert 'weight' in edge_data, \
            f"Edge ({u}, {v}) should have 'weight' attribute"
        assert isinstance(edge_data['weight'], (int, float)), \
            f"Edge ({u}, {v}) weight should be numeric"
        assert edge_data['weight'] >= 0, \
            f"Edge ({u}, {v}) weight should be non-negative"


@pytest.mark.osmnx
def test_epsg_projection():
    """Test 4: EPSG is set to target projection value."""
    import routing_2026

    # Small bbox near Oslo
    bbox = (59.90, 10.70, 59.92, 10.75)

    # Load with default EPSG (25832 for UTM 32V)
    routing_net = routing_2026.load_osmnx_trails(bbox)

    # Verify EPSG is set
    assert routing_net.epsg == 25832, \
        f"EPSG should be 25832, got {routing_net.epsg}"

    # Load with custom EPSG
    routing_net_custom = routing_2026.load_osmnx_trails(bbox, epsg=4326)

    # Verify custom EPSG is set
    assert routing_net_custom.epsg == 4326, \
        f"EPSG should be 4326, got {routing_net_custom.epsg}"