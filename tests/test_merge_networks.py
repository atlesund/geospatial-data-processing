"""
Unit tests for merge_networks function.

Tests verify multi-source network integration with node prefixing,
EPSG validation, and complete preservation of nodes and edges.
"""

import pytest


@pytest.mark.routing
def test_merge_networks_returns_routing_network():
    """Test 1: merge_networks returns unified RoutingNetwork instance."""
    import routing_2026

    # Create multiple RoutingNetwork instances
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

    # Merge networks
    merged = routing_2026.merge_networks([net1, net2], prefix_mapping=['trail_', 'osm_'])

    # Verify returns RoutingNetwork instance
    assert isinstance(merged, routing_2026.RoutingNetwork), "Should return RoutingNetwork instance"


@pytest.mark.routing
def test_all_nodes_preserved_in_merged_network():
    """Test 2: All nodes from source networks present in merged network."""
    import routing_2026

    # Create first network with 2 nodes
    net1 = routing_2026.RoutingNetwork()
    net1.add_node(0, 450000.0, 6500000.0)
    net1.add_node(1, 450100.0, 6500100.0)
    net1.add_edge(0, 1, 100.0)
    net1.epsg = 25832

    # Create second network with 3 nodes
    net2 = routing_2026.RoutingNetwork()
    net2.add_node(0, 450200.0, 6500000.0)
    net2.add_node(1, 450300.0, 6500100.0)
    net2.add_node(2, 450400.0, 6500000.0)
    net2.add_edge(0, 1, 100.0)
    net2.add_edge(1, 2, 100.0)
    net2.epsg = 25832

    # Merge networks
    merged = routing_2026.merge_networks([net1, net2], prefix_mapping=['trail_', 'osm_'])

    # Verify all 5 nodes preserved (2 + 3)
    assert merged.graph.number_of_nodes() == 5, f"Should have 5 nodes, got {merged.graph.number_of_nodes()}"
    assert len(merged.node_coords) == 5, f"node_coords should have 5 entries, got {len(merged.node_coords)}"


@pytest.mark.routing
def test_all_edges_preserved_in_merged_network():
    """Test 3: All edges from source networks present in merged network."""
    import routing_2026

    # Create first network with 1 edge
    net1 = routing_2026.RoutingNetwork()
    net1.add_node(0, 450000.0, 6500000.0)
    net1.add_node(1, 450100.0, 6500100.0)
    net1.add_edge(0, 1, 100.0, trail_id=1)
    net1.epsg = 25832

    # Create second network with 2 edges
    net2 = routing_2026.RoutingNetwork()
    net2.add_node(0, 450200.0, 6500000.0)
    net2.add_node(1, 450300.0, 6500100.0)
    net2.add_node(2, 450400.0, 6500000.0)
    net2.add_edge(0, 1, 100.0, source='osm')
    net2.add_edge(1, 2, 150.0, source='osm')
    net2.epsg = 25832

    # Merge networks
    merged = routing_2026.merge_networks([net1, net2], prefix_mapping=['trail_', 'osm_'])

    # Verify all 3 edges preserved (1 + 2)
    assert merged.graph.number_of_edges() == 3, f"Should have 3 edges, got {merged.graph.number_of_edges()}"

    # Verify edge attributes preserved
    edges = list(merged.graph.edges(data=True))
    edge_attrs = [edge[2] for edge in edges]
    trail_id_found = any(edge['trail_id'] == 1 for edge in edge_attrs)
    source_osm_found = any(edge.get('source') == 'osm' for edge in edge_attrs)
    assert trail_id_found, "Should preserve trail_id attribute from net1"
    assert source_osm_found, "Should preserve source attribute from net2"


@pytest.mark.routing
def test_node_id_prefixing_prevents_collisions():
    """Test 4: Node ID prefixes prevent collisions between sources."""
    import routing_2026

    # Create first network with node ID 0
    net1 = routing_2026.RoutingNetwork()
    net1.add_node(0, 450000.0, 6500000.0)
    net1.add_node(1, 450100.0, 6500100.0)
    net1.add_edge(0, 1, 100.0)
    net1.epsg = 25832

    # Create second network with overlapping node IDs (also 0 and 1)
    net2 = routing_2026.RoutingNetwork()
    net2.add_node(0, 450200.0, 6500000.0)
    net2.add_node(1, 450300.0, 6500100.0)
    net2.add_edge(0, 1, 100.0)
    net2.epsg = 25832

    # Merge networks with prefixes
    merged = routing_2026.merge_networks([net1, net2], prefix_mapping=['trail_', 'osm_'])

    # Verify 4 distinct nodes (prefixing should prevent collisions)
    assert merged.graph.number_of_nodes() == 4, f"Should have 4 nodes, got {merged.graph.number_of_nodes()}"

    # Verify node IDs have correct prefixes
    node_ids = list(merged.graph.nodes())
    prefixed_nodes = [node_id for node_id in node_ids if isinstance(node_id, str) and (node_id.startswith('trail_') or node_id.startswith('osm_'))]
    assert len(prefixed_nodes) == 4, f"All 4 nodes should have prefixes, got {len(prefixed_nodes)}"

    # Verify specific prefixed IDs exist
    assert 'trail_0' in node_ids, "trail_0 should be in merged network"
    assert 'trail_1' in node_ids, "trail_1 should be in merged network"
    assert 'osm_0' in node_ids, "osm_0 should be in merged network"
    assert 'osm_1' in node_ids, "osm_1 should be in merged network"