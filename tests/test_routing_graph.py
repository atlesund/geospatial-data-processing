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


@pytest.mark.routing
def test_polylines_to_graph_returns_routing_network():
    """Test 8: polylines_to_graph returns RoutingNetwork instance."""
    import routing_2026
    import vector_2026

    # Create mock Vector with POLYLINE geometry
    trails = vector_2026.Vector(geometry='POLYLINE')

    # Manually set coordinates (simulating loaded trail data)
    trails._coordinates = [
        [(450000.0, 6500000.0), (450100.0, 6500100.0)],  # Trail 0
        [(450200.0, 6500000.0), (450300.0, 6500100.0)],  # Trail 1
    ]
    trails._epsg = 25832

    # Convert polylines to graph
    routing_net = routing_2026.polylines_to_graph(trails)

    # Verify returns RoutingNetwork instance
    assert isinstance(routing_net, routing_2026.RoutingNetwork), "Should return RoutingNetwork instance"

    # Verify EPSG is set
    assert routing_net.epsg == 25832, f"EPSG should be 25832, got {routing_net.epsg}"


@pytest.mark.routing
def test_line_endpoints_converted_to_nodes():
    """Test 9: Line endpoints converted to nodes."""
    import routing_2026
    import vector_2026

    # Create mock Vector with 2 polylines (4 endpoints, 4 nodes)
    trails = vector_2026.Vector(geometry='POLYLINE')
    trails._coordinates = [
        [(450000.0, 6500000.0), (450100.0, 6500000.0)],
        [(450200.0, 6500000.0), (450300.0, 6500000.0)],
    ]
    trails._epsg = 25832

    # Convert to graph
    routing_net = routing_2026.polylines_to_graph(trails)

    # Verify 4 nodes created (2 trails × 2 endpoints)
    assert routing_net.graph.number_of_nodes() == 4, f"Should have 4 nodes, got {routing_net.graph.number_of_nodes()}"
    assert len(routing_net.node_coords) == 4, f"node_coords should have 4 entries, got {len(routing_net.node_coords)}"

    # Verify 2 edges created
    assert routing_net.graph.number_of_edges() == 2, f"Should have 2 edges, got {routing_net.graph.number_of_edges()}"


@pytest.mark.routing
def test_endpoint_snapping_within_distance():
    """Test 10: Nearby endpoints snap to same node."""
    import routing_2026
    import vector_2026

    # Create mock Vector with 2 polylines sharing nearby endpoint
    # Trail 0 endpoints: (0,0) and (100,0)
    # Trail 1 endpoints: (90,0) and (200,0)
    # With snap_distance=20, points (100,0) and (90,0) should snap to same node
    trails = vector_2026.Vector(geometry='POLYLINE')
    trails._coordinates = [
        [(0.0, 0.0), (100.0, 0.0)],    # Trail 0
        [(90.0, 0.0), (200.0, 0.0)],   # Trail 1 (start near Trail 0's end)
    ]
    trails._epsg = 25832

    # Convert with snap_distance=20
    snap_distance = 20.0
    routing_net = routing_2026.polylines_to_graph(trails, snap_distance=snap_distance)

    # Verify only 3 nodes (one shared node due to snapping)
    # Expected nodes: (0,0), snapped shared near (100,0)/(90,0), (200,0)
    assert routing_net.graph.number_of_nodes() == 3, f"Should have 3 nodes after snapping, got {routing_net.graph.number_of_nodes()}"

    # Coordinates should contain values within expected bounds
    coords_list = list(routing_net.node_coords.values())
    assert len(coords_list) == 3, f"Should have 3 coordinate entries, got {len(coords_list)}"


@pytest.mark.routing
def test_edges_created_with_euclidean_weight():
    """Test 11: Edges created with Euclidean distance weights."""
    import routing_2026
    import vector_2026
    import math

    # Create mock Vector with 1 polyline (horizontal line)
    trails = vector_2026.Vector(geometry='POLYLINE')
    trails._coordinates = [
        [(0.0, 0.0), (100.0, 0.0), (200.0, 0.0)]  # Two segments, each 100m
    ]
    trails._epsg = 25832

    # Convert to graph
    routing_net = routing_2026.polylines_to_graph(trails)

    # Verify 1 edge exists (between start and end of polyline)
    assert routing_net.graph.number_of_edges() == 1, f"Should have 1 edge, got {routing_net.graph.number_of_edges()}"

    # Get edge data
    edges = list(routing_net.graph.edges(data=True))
    assert len(edges) == 1, "Should have exactly one edge"

    u, v, edge_data = edges[0]

    # Verify weight attribute exists
    assert 'weight' in edge_data, "Edge should have 'weight' attribute"

    # Verify weight equals polyline length (200m)
    expected_length = 200.0
    assert abs(edge_data['weight'] - expected_length) < 0.01, f"Weight should be {expected_length}m, got {edge_data['weight']}"

    # Verify length attribute also set
    assert 'length' in edge_data, "Edge should have 'length' attribute"
    assert abs(edge_data['length'] - expected_length) < 0.01, f"Length should be {expected_length}m, got {edge_data['length']}"

    # Verify trail_id attribute set
    assert 'trail_id' in edge_data, "Edge should have 'trail_id' attribute"
    assert edge_data['trail_id'] == 0, "trail_id should be 0 for first polyline"


@pytest.mark.routing
def test_connected_components():
    """Test 12: Verify resulting graph has connected components."""
    import routing_2026
    import vector_2026
    import networkx as nx

    # Create mock Vector with 3 disconnected polylines
    # Component 1: Trail A and Trail B are connected
    # Component 2: Trail C is isolated (far away)
    trails = vector_2026.Vector(geometry='POLYLINE')
    trails._coordinates = [
        # Component 1: Connected trails
        [(0.0, 0.0), (100.0, 0.0)],    # Trail A
        [(100.0, 0.0), (200.0, 0.0)],   # Trail B (continues from Trail A's end)
        # Component 2: Isolated trail (far away)
        [(10000.0, 10000.0), (10200.0, 10000.0)],  # Trail C
    ]
    trails._epsg = 25832

    # Convert to graph with small snap distance (no snapping across distance)
    snap_distance = 10.0
    routing_net = routing_2026.polylines_to_graph(trails, snap_distance=snap_distance)

    # Verify node count
    # Component 1: 3 nodes (Trail A start, shared junction, Trail B end)
    # Component 2: 2 nodes
    # Total: 5 nodes
    assert routing_net.graph.number_of_nodes() == 5, f"Should have 5 nodes, got {routing_net.graph.number_of_nodes()}"

    # Verify edge count
    assert routing_net.graph.number_of_edges() == 3, f"Should have 3 edges, got {routing_net.graph.number_of_edges()}"

    # Verify graph has exactly 2 connected components
    # Using NetworkX's connected_components
    components = list(nx.connected_components(routing_net.graph))
    assert len(components) == 2, f"Should have 2 connected components, got {len(components)}"

    # Verify component sizes
    component_sizes = [len(comp) for comp in components]
    component_sizes.sort(reverse=True)
    assert component_sizes[0] == 3, f"Largest component should have 3 nodes, got {component_sizes[0]}"
    assert component_sizes[1] == 2, f"Smallest component should have 2 nodes, got {component_sizes[1]}"


@pytest.mark.routing
def test_merge_networks():
    """Test: Create multiple RoutingNetwork instances, verify merge."""
    import routing_2026

    # Create three networks
    net1 = routing_2026.RoutingNetwork()
    net1.add_node(0, 450000.0, 6500000.0)
    net1.add_node(1, 450100.0, 6500100.0)
    net1.add_edge(0, 1, 100.0)
    net1.epsg = 25832

    net2 = routing_2026.RoutingNetwork()
    net2.add_node(0, 450200.0, 6500000.0)
    net2.add_node(1, 450300.0, 6500100.0)
    net2.add_edge(0, 1, 150.0)
    net2.epsg = 25832

    net3 = routing_2026.RoutingNetwork()
    net3.add_node(0, 450400.0, 6500000.0)
    net3.add_node(1, 450500.0, 6500100.0)
    net3.add_edge(0, 1, 200.0)
    net3.epsg = 25832

    # Merge networks with custom prefixes
    merged = routing_2026.merge_networks([net1, net2, net3], prefix_mapping=['trail_', 'osm_', 'mesh_'])

    # Verify merge successful
    assert isinstance(merged, routing_2026.RoutingNetwork), "Should return RoutingNetwork instance"
    assert merged.graph.number_of_nodes() == 6, f"Should have 6 nodes, got {merged.graph.number_of_nodes()}"
    assert merged.graph.number_of_edges() == 3, f"Should have 3 edges, got {merged.graph.number_of_edges()}"
    assert merged.epsg == 25832, f"EPSG should be 25832, got {merged.epsg}"

    # Verify all prefixed nodes exist
    node_ids = list(merged.graph.nodes())
    assert 'trail_0' in node_ids, "trail_0 should exist"
    assert 'trail_1' in node_ids, "trail_1 should exist"
    assert 'osm_0' in node_ids, "osm_0 should exist"
    assert 'osm_1' in node_ids, "osm_1 should exist"
    assert 'mesh_0' in node_ids, "mesh_0 should exist"
    assert 'mesh_1' in node_ids, "mesh_1 should exist"


@pytest.mark.routing
def test_node_prefix_collision():
    """Test: Verify prefixed IDs don't collide."""
    import routing_2026

    # Create two networks with identical node IDs
    net1 = routing_2026.RoutingNetwork()
    net1.add_node(0, 450000.0, 6500000.0)
    net1.add_node(1, 450100.0, 6500100.0)
    net1.add_edge(0, 1, 100.0)
    net1.epsg = 25832

    net2 = routing_2026.RoutingNetwork()
    net2.add_node(0, 450200.0, 6500000.0)
    net2.add_node(1, 450300.0, 6500100.0)
    net2.add_edge(0, 1, 100.0)
    net2.epsg = 25832

    # Merge with prefixes
    merged = routing_2026.merge_networks([net1, net2], prefix_mapping=['trail_', 'osm_'])

    # Verify no collisions - should have 4 distinct nodes
    assert merged.graph.number_of_nodes() == 4, f"Should have 4 nodes without collision, got {merged.graph.number_of_nodes()}"

    # Verify each original node exists with correct prefix
    node_ids = list(merged.graph.nodes())
    assert 'trail_0' in node_ids, "trail_0 should exist"
    assert 'trail_1' in node_ids, "trail_1 should exist"
    assert 'osm_0' in node_ids, "osm_0 should exist"
    assert 'osm_1' in node_ids, "osm_1 should exist"

    # Verify no unprefixed nodes remain (no collision)
    unprefixed_nodes = [node_id for node_id in node_ids if isinstance(node_id, int)]
    assert len(unprefixed_nodes) == 0, f"No unprefixed nodes should remain, got {unprefixed_nodes}"

    # Verify edges use prefixed nodes
    edges = list(merged.graph.edges())
    trail_edge = ('trail_0', 'trail_1')
    osm_edge = ('osm_0', 'osm_1')
    assert trail_edge in edges, "Trail edge should use prefixed nodes"
    assert osm_edge in edges, "OSM edge should use prefixed nodes"


@pytest.mark.routing
def test_epsg_validation():
    """Test: Verify ValueError raised for mismatched EPSG."""
    import routing_2026

    # Create two networks with different EPSG codes
    net1 = routing_2026.RoutingNetwork()
    net1.add_node(0, 450000.0, 6500000.0)
    net1.add_node(1, 450100.0, 6500100.0)
    net1.add_edge(0, 1, 100.0)
    net1.epsg = 25832  # UTM 32V

    net2 = routing_2026.RoutingNetwork()
    net2.add_node(0, 450200.0, 6500000.0)
    net2.add_node(1, 450300.0, 6500100.0)
    net2.add_edge(0, 1, 100.0)
    net2.epsg = 4326  # WGS84

    # Verify ValueError raised for mismatched EPSG
    try:
        merged = routing_2026.merge_networks([net1, net2], prefix_mapping=['trail_', 'osm_'])
        assert False, "Should raise ValueError for mismatched EPSG codes"
    except ValueError as e:
        error_msg = str(e)
        assert "EPSG codes" in error_msg, f"Error message should mention EPSG codes, got: {error_msg}"
        assert "25832" in error_msg, f"Error should mention EPSG 25832, got: {error_msg}"
        assert "4326" in error_msg, f"Error should mention EPSG 4326, got: {error_msg}"

    # Verify merge succeeds with matching EPSG codes
    net2.epsg = 25832  # Change to match net1
    merged = routing_2026.merge_networks([net1, net2], prefix_mapping=['trail_', 'osm_'])
    assert merged.graph.number_of_nodes() == 4, f"Should merge successfully with matching EPSG, got {merged.graph.number_of_nodes()} nodes"

    # Verify merge succeeds when all EPSG codes are None
    net1.epsg = None
    net2.epsg = None
    merged = routing_2026.merge_networks([net1, net2], prefix_mapping=['trail_', 'osm_'])
    assert merged.graph.number_of_nodes() == 4, f"Should merge successfully with None EPSG, got {merged.graph.number_of_nodes()} nodes"