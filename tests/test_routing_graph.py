"""
Unit tests for RoutingNetwork class core structure.

Tests verify graph construction, node/edge operations, shortest path,
and nearest node finding with KDTree.
"""

import pytest


@pytest.mark.routing
def test_routing_network_init():
    """Test 1: RoutingNetwork.__init__ creates empty graph and node_coords dict."""
    import routing_2026

    routing_net = routing_2026.RoutingNetwork()

    # Verify graph is empty
    assert hasattr(routing_net, 'graph'), "RoutingNetwork should have 'graph' attribute"
    assert routing_net.graph.number_of_nodes() == 0, "Graph should have 0 nodes after init"

    # Verify node_coords is empty dict
    assert hasattr(routing_net, 'node_coords'), "RoutingNetwork should have 'node_coords' attribute"
    assert len(routing_net.node_coords) == 0, "node_coords should be empty after init"

    # Verify epsg is None (unspecified coordinate system)
    assert routing_net.epsg is None, "EPSG should be None after init"


@pytest.mark.routing
def test_add_node():
    """Test 2: add_node(node_id, x, y) adds node to graph and stores coordinates in node_coords."""
    import routing_2026

    routing_net = routing_2026.RoutingNetwork()

    # Add a node
    node_id = 0
    x, y = 450000.0, 6500000.0
    routing_net.add_node(node_id, x, y)

    # Verify node is in graph
    assert routing_net.graph.has_node(node_id), f"Node {node_id} should be in graph"

    # Verify coordinates are stored
    assert node_id in routing_net.node_coords, f"Node {node_id} should be in node_coords"
    assert routing_net.node_coords[node_id] == (x, y), f"Coordinates for node {node_id} should be ({x}, {y})"


@pytest.mark.routing
def test_add_edge():
    """Test 3: add_edge(u, v, weight, **attrs) adds bidirectional edge with weight attribute."""
    import routing_2026

    routing_net = routing_2026.RoutingNetwork()

    # Add two nodes
    routing_net.add_node(0, 450000.0, 6500000.0)
    routing_net.add_node(1, 450100.0, 6500100.0)

    # Add edge with weight and custom attributes
    weight = 100.0
    edge_attrs = {'length': 100.0, 'trail_id': 1}
    routing_net.add_edge(0, 1, weight, **edge_attrs)

    # Verify edge exists in graph
    assert routing_net.graph.has_edge(0, 1), "Edge (0, 1) should exist in graph"
    assert routing_net.graph.has_edge(1, 0), "Edge (1, 0) should exist (bidirectional in undirected graph)"

    # Verify weight attribute
    assert 'weight' in routing_net.graph[0][1], "Edge should have 'weight' attribute"
    assert routing_net.graph[0][1]['weight'] == weight, f"Edge weight should be {weight}"

    # Verify custom attributes
    assert 'length' in routing_net.graph[0][1], "Edge should have 'length' attribute"
    assert routing_net.graph[0][1]['length'] == 100.0
    assert 'trail_id' in routing_net.graph[0][1], "Edge should have 'trail_id' attribute"
    assert routing_net.graph[0][1]['trail_id'] == 1


@pytest.mark.routing
def test_shortest_path():
    """Test 4: shortest_path(source, target) returns node list using Dijkstra algorithm."""
    import routing_2026

    routing_net = routing_2026.RoutingNetwork()

    # Create 3-node graph: 0 --(100)-- 1 --(50)-- 2
    routing_net.add_node(0, 450000.0, 6500000.0)
    routing_net.add_node(1, 450100.0, 6500100.0)
    routing_net.add_node(2, 450200.0, 6500000.0)

    # Add edges with weights
    routing_net.add_edge(0, 1, 100)
    routing_net.add_edge(1, 2, 50)

    # Compute shortest path from 0 to 2
    path = routing_net.shortest_path(0, 2)

    # Verify path is list of node IDs
    assert isinstance(path, list), "Path should be a list"
    assert len(path) == 3, "Path should have 3 nodes: [0, 1, 2]"
    assert path[0] == 0, "Path should start at source node (0)"
    assert path[2] == 2, "Path should end at target node (2)"
    assert path[1] == 1, "Path should include intermediate node (1)"


@pytest.mark.routing
def test_find_nearest_node():
    """Test 5: find_nearest_node(x, y) returns nearest node_id and distance using KDTree."""
    import routing_2026

    routing_net = routing_2026.RoutingNetwork()

    # Add nodes at known coordinates
    routing_net.add_node(0, 450000.0, 6500000.0)
    routing_net.add_node(1, 450100.0, 6500100.0)
    routing_net.add_node(2, 450200.0, 6500000.0)

    # Query near point close to node 0
    query_x, query_y = 450050.0, 6500000.0
    nearest_node_id, distance = routing_net.find_nearest_node(query_x, query_y)

    # Verify nearest node is node 0 (50m away)
    assert nearest_node_id == 0, f"Nearest node should be 0, got {nearest_node_id}"
    assert abs(distance - 50.0) < 0.01, f"Distance should be ~50.0m, got {distance}"

    # Query near node 2
    query_x, query_y = 450150.0, 6500000.0
    nearest_node_id, distance = routing_net.find_nearest_node(query_x, query_y)

    # Verify nearest node is node 2 (50m away)
    assert nearest_node_id == 2, f"Nearest node should be 2, got {nearest_node_id}"
    assert abs(distance - 50.0) < 0.01, f"Distance should be ~50.0m, got {distance}"


@pytest.mark.routing
def test_epsg_property():
    """Test 6: Set EPSG to 25832, read back, verify value matches."""
    import routing_2026

    routing_net = routing_2026.RoutingNetwork()

    # Verify EPSG is None initially
    assert routing_net.epsg is None, "EPSG should be None by default"

    # Set EPSG to 25832 (UTM 32V)
    routing_net.epsg = 25832

    # Verify EPSG is set correctly
    assert routing_net.epsg == 25832, f"EPSG should be 25832, got {routing_net.epsg}"

    # Change EPSG to 4326 (WGS84)
    routing_net.epsg = 4326
    assert routing_net.epsg == 4326, f"EPSG should be 4326, got {routing_net.epsg}"

    # Set EPSG back to None
    routing_net.epsg = None
    assert routing_net.epsg is None, "EPSG should be None after setting to None"

    # Verify invalid EPSG type raises ValueError
    try:
        routing_net.epsg = "25832"
        assert False, "Setting EPSG to string should raise ValueError"
    except ValueError:
        pass  # Expected

    try:
        routing_net.epsg = 25832.0
        assert False, "Setting EPSG to float should raise ValueError"
    except ValueError:
        pass  # Expected


@pytest.mark.routing
def test_find_nearest_node_empty_graph():
    """Test 7: Query nearest on empty graph, verify returns (None, inf)."""
    import routing_2026

    routing_net = routing_2026.RoutingNetwork()

    # Query nearest node on empty graph
    query_x, query_y = 450000.0, 6500000.0
    nearest_node_id, distance = routing_net.find_nearest_node(query_x, query_y)

    # Verify returns (None, inf) for empty graph
    assert nearest_node_id is None, f"Nearest node should be None for empty graph, got {nearest_node_id}"
    assert distance == float('inf'), f"Distance should be inf for empty graph"