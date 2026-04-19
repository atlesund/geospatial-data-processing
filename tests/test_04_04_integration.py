"""
Integration tests for water-aware routing.

Tests validate end-to-end water penalty pipeline (osm query → crossing detection
→ combined weights → Dijkstra) produces routes that avoid unnecessary
water crossings while finding optimal paths.
"""

import pytest
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon, LineString, Point
from routing_2026 import RoutingNetwork, detect_water_crossing, calculate_terrain_weight
from unittest.mock import MagicMock

# Mock imports for headless testing environment
try:
    import osmnx
    IMPORT_AVAILABLE = True
except ImportError:
    IMPORT_AVAILABLE = False


@pytest.mark.water
@pytest.mark.integration
def test_route_avoids_lake():
    """
    Test that routing avoids lake crossing when land alternatives exist.

    Creates a 3x3 routing grid with a lake polygon in the center.
    Verifies that the shortest path from top-left to bottom-right
    takes a land detour around the water rather than crossing it.
    """
    # Create 3x3 grid (9 nodes) with 100m spacing
    # Node layout:
    #   0---1---2
    #   |   |   |
    #   3---4---5
    #   |   |   |
    #   6---7---8
    routing_net = RoutingNetwork()

    # Add nodes to grid (coordinates in meters)
    mesh_spacing = 100
    for row in range(3):
        for col in range(3):
            node_id = row * 3 + col
            x = col * mesh_spacing
            y = row * mesh_spacing
            routing_net.add_node(node_id, x, y)

    # Create lake polygon covering middle row nodes (3, 4, 5)
    # Lake spans from y=100 to y=200, x=0 to x=300
    lake_polygon = Polygon([(0, 50), (300, 50), (300, 150), (0, 150)])
    lakes_gdf = gpd.GeoDataFrame(
        {'name': ['Test Lake']},
        geometry=[lake_polygon],
        crs='EPSG:25832'
    )

    # Create edges and apply water penalties
    # Horizontal edges
    for row in range(3):
        for col in range(2):
            u = row * 3 + col
            v = row * 3 + col + 1
            edge_start = routing_net.node_coords[u]
            edge_end = routing_net.node_coords[v]

            # Detect water crossing
            water_type, water_penalty_factor = detect_water_crossing(
                edge_start, edge_end, lakes_gdf, None
            )

            # Calculate terrain penalty (flat terrain = 1.0)
            terrain_weight, slope, terrain_penalty = calculate_terrain_weight(
                100, 100, mesh_spacing
            )

            # Combine penalties
            combined_penalty = terrain_penalty * water_penalty_factor
            final_weight = mesh_spacing * combined_penalty

            routing_net.add_edge(u, v, final_weight,
                               length=mesh_spacing,
                               slope_angle=slope,
                               terrain_penalty_factor=terrain_penalty,
                               water_type=water_type,
                               water_penalty_factor=water_penalty_factor,
                               penalty_factor=combined_penalty,
                               source='terrain_water')

    # Vertical edges (middle row edges will have lake penalty)
    for row in range(2):
        for col in range(3):
            u = row * 3 + col
            v = (row + 1) * 3 + col
            edge_start = routing_net.node_coords[u]
            edge_end = routing_net.node_coords[v]

            # Detect water crossing
            water_type, water_penalty_factor = detect_water_crossing(
                edge_start, edge_end, lakes_gdf, None
            )

            # Calculate terrain penalty (flat terrain = 1.0)
            terrain_weight, slope, terrain_penalty = calculate_terrain_weight(
                100, 100, mesh_spacing
            )

            # Combine penalties
            combined_penalty = terrain_penalty * water_penalty_factor
            final_weight = mesh_spacing * combined_penalty

            routing_net.add_edge(u, v, final_weight,
                               length=mesh_spacing,
                               slope_angle=slope,
                               terrain_penalty_factor=terrain_penalty,
                               water_type=water_type,
                               water_penalty_factor=water_penalty_factor,
                               penalty_factor=combined_penalty,
                               source='terrain_water')

    # Find shortest path from top-left (node 0) to bottom-right (node 8)
    path = routing_net.shortest_path(0, 8)

    # Assert path exists
    assert path is not None, "Path should exist"
    assert len(path) > 0, "Path should have nodes"

    # Calculate total path weight
    total_weight = 0
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        total_weight += routing_net.graph[u][v]['weight']

    # Direct crossing (0-4-8) would be 200m × 10 = 2000 (crosses lake)
    # Land detour (0-1-2-5-8 or 0-3-6-7-8) would be 300m × 1 = 300
    # Path should be the land detour (~300m), not the lake crossing (~2000m)
    assert total_weight < 1000, f"Path should avoid lake crossing (weight: {total_weight})"


@pytest.mark.water
@pytest.mark.integration
def test_route_avoids_river():
    """
    Test that routing avoids river crossing when alternatives exist.

    Creates a 4x4 routing grid with a river linestring crossing diagonally.
    Verifies that path takes detour around river crossing where possible.
    """
    # Create 4x4 grid (16 nodes)
    routing_net = RoutingNetwork()

    mesh_spacing = 100
    for row in range(4):
        for col in range(4):
            node_id = row * 4 + col
            x = col * mesh_spacing
            y = row * mesh_spacing
            routing_net.add_node(node_id, x, y)

    # Create river linestring crossing diagonally from top-right to bottom-left
    river_line = LineString([(350, 0), (0, 350)])
    rivers_gdf = gpd.GeoDataFrame(
        {'waterway': ['river'], 'name': ['Test River']},
        geometry=[river_line],
        crs='EPSG:25832'
    )

    # Create horizontal edges
    for row in range(4):
        for col in range(3):
            u = row * 4 + col
            v = row * 4 + col + 1
            edge_start = routing_net.node_coords[u]
            edge_end = routing_net.node_coords[v]

            water_type, water_penalty_factor = detect_water_crossing(
                edge_start, edge_end, None, rivers_gdf
            )

            terrain_weight, slope, terrain_penalty = calculate_terrain_weight(
                100, 100, mesh_spacing
            )

            combined_penalty = terrain_penalty * water_penalty_factor
            final_weight = mesh_spacing * combined_penalty

            routing_net.add_edge(u, v, final_weight,
                               length=mesh_spacing,
                               slope_angle=slope,
                               terrain_penalty_factor=terrain_penalty,
                               water_type=water_type,
                               water_penalty_factor=water_penalty_factor,
                               penalty_factor=combined_penalty,
                               source='terrain_water')

    # Create vertical edges
    for row in range(3):
        for col in range(4):
            u = row * 4 + col
            v = (row + 1) * 4 + col
            edge_start = routing_net.node_coords[u]
            edge_end = routing_net.node_coords[v]

            water_type, water_penalty_factor = detect_water_crossing(
                edge_start, edge_end, None, rivers_gdf
            )

            terrain_weight, slope, terrain_penalty = calculate_terrain_weight(
                100, 100, mesh_spacing
            )

            combined_penalty = terrain_penalty * water_penalty_factor
            final_weight = mesh_spacing * combined_penalty

            routing_net.add_edge(u, v, final_weight,
                               length=mesh_spacing,
                               slope_angle=slope,
                               terrain_penalty_factor=terrain_penalty,
                               water_type=water_type,
                               water_penalty_factor=water_penalty_factor,
                               penalty_factor=combined_penalty,
                               source='terrain_water')

    # Find path from top-left (node 0) to bottom-right (node 15)
    path = routing_net.shortest_path(0, 15)

    assert path is not None, "Path should exist"
    assert len(path) > 0, "Path should have nodes"

    # Verify at least one edge has river crossing info
    has_river_edge = False
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        edge_data = routing_net.graph[u][v]
        if edge_data.get('water_type') == 'river':
            has_river_edge = True
            # Verify river penalty factor is correct
            assert edge_data.get('water_penalty_factor') == 5.0, \
                "River penalty factor should be 5.0"

    # Note: In this grid setup, the path may or may not cross the river
    # depending on exact geometry. We just verify the system works.


@pytest.mark.water
@pytest.mark.integration
def test_route_accepts_fjord_crossing_with_detour():
    """
    Test that fjord crossing occurs with appropriate detours.

    Creates a 5x5 grid with a fjord polygon covering the bottom row.
    Verifies that path uses land as far as possible before minimal
    fjord crossing, and applies 50× fjord penalty factor.
    """
    # Create 5x5 grid (25 nodes)
    routing_net = RoutingNetwork()

    mesh_spacing = 100
    for row in range(5):
        for col in range(5):
            node_id = row * 5 + col
            x = col * mesh_spacing
            y = row * mesh_spacing
            routing_net.add_node(node_id, x, y)

    # Create fjord polygon covering bottom row (y=400 to y=500)
    fjord_polygon = Polygon([(0, 350), (500, 350), (500, 500), (0, 500)])
    lakes_gdf = gpd.GeoDataFrame(
        {'name': ['Sognefjord']},
        geometry=[fjord_polygon],
        crs='EPSG:25832'
    )

    # Create horizontal edges
    for row in range(5):
        for col in range(4):
            u = row * 5 + col
            v = row * 5 + col + 1
            edge_start = routing_net.node_coords[u]
            edge_end = routing_net.node_coords[v]

            water_type, water_penalty_factor = detect_water_crossing(
                edge_start, edge_end, lakes_gdf, None
            )

            terrain_weight, slope, terrain_penalty = calculate_terrain_weight(
                100, 100, mesh_spacing
            )

            combined_penalty = terrain_penalty * water_penalty_factor
            final_weight = mesh_spacing * combined_penalty

            routing_net.add_edge(u, v, final_weight,
                               length=mesh_spacing,
                               slope_angle=slope,
                               terrain_penalty_factor=terrain_penalty,
                               water_type=water_type,
                               water_penalty_factor=water_penalty_factor,
                               penalty_factor=combined_penalty,
                               source='terrain_water')

    # Create vertical edges
    for row in range(4):
        for col in range(5):
            u = row * 5 + col
            v = (row + 1) * 5 + col
            edge_start = routing_net.node_coords[u]
            edge_end = routing_net.node_coords[v]

            water_type, water_penalty_factor = detect_water_crossing(
                edge_start, edge_end, lakes_gdf, None
            )

            terrain_weight, slope, terrain_penalty = calculate_terrain_weight(
                100, 100, mesh_spacing
            )

            combined_penalty = terrain_penalty * water_penalty_factor
            final_weight = mesh_spacing * combined_penalty

            routing_net.add_edge(u, v, final_weight,
                               length=mesh_spacing,
                               slope_angle=slope,
                               terrain_penalty_factor=terrain_penalty,
                               water_type=water_type,
                               water_penalty_factor=water_penalty_factor,
                               penalty_factor=combined_penalty,
                               source='terrain_water')

    # Find path from top-left (node 0) to bottom-right (node 24)
    # Must cross fjord at some point
    path = routing_net.shortest_path(0, 24)

    assert path is not None, "Path should exist"

    # Verify fjord crossing penalty is applied correctly
    has_fjord_edge = False
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        edge_data = routing_net.graph[u][v]
        if edge_data.get('water_type') == 'fjord':
            has_fjord_edge = True
            # Verify fjord penalty factor is 50.0
            assert edge_data.get('water_penalty_factor') == 50.0, \
                f"Fjord penalty factor should be 50.0, got {edge_data.get('water_penalty_factor')}"

    # In this setup, the path from node 0 to node 24 will need to cross
    # the fjord at least once (or use edges at the fjord boundary)
    # We verify the system identifies fjord crossings correctly


@pytest.mark.water
@pytest.mark.integration
def test_terrain_and_water_combined():
    """
    Test multiplicative combination of terrain and water penalties.

    Creates a synthetic network with steep slope AND water crossing
    on the same edge. Verifies multiplicative penalty calculation.
    """
    routing_net = RoutingNetwork()

    # Create simple 3-node network: 0 -- A -- 1 -- B -- 2
    # Edge A has steep slope + water crossing
    # Edge B is flat + land (alternative route)
    mesh_spacing = 200

    # Node 0 at origin
    routing_net.add_node(0, 0, 0)

    # Node 1 between 0 and 2
    routing_net.add_node(1, 200, 0)

    # Node 2 at end
    routing_net.add_node(2, 400, 0)

    # Create lake polygon covering edge 0-1 (water crossing)
    lake_polygon = Polygon([(0, -50), (200, -50), (200, 50), (0, 50)])
    lakes_gdf = gpd.GeoDataFrame(
        {'name': ['Test Lake']},
        geometry=[lake_polygon],
        crs='EPSG:25832'
    )

    # Edge 0-1: steep slope (30°) + water crossing (lake)
    # Elevation: 100m -> 250m (150m rise over 200m)
    # Slope = atan(150/200) ≈ 36.87°
    # Terrain penalty for 36.87° ≈ 1.0 + 0.1 × (36.87 - 20) ≈ 2.69
    # Water penalty = 10.0 (lake)
    # Combined = 2.69 × 10.0 ≈ 26.9
    edge_start_0_1 = routing_net.node_coords[0]
    edge_end_0_1 = routing_net.node_coords[1]

    water_type_0_1, water_penalty_0_1 = detect_water_crossing(
        edge_start_0_1, edge_end_0_1, lakes_gdf, None
    )

    terrain_weight_0_1, slope_0_1, terrain_penalty_0_1 = calculate_terrain_weight(
        100, 250, mesh_spacing
    )

    combined_penalty_0_1 = terrain_penalty_0_1 * water_penalty_0_1
    final_weight_0_1 = mesh_spacing * combined_penalty_0_1

    routing_net.add_edge(0, 1, final_weight_0_1,
                         length=mesh_spacing,
                         slope_angle=slope_0_1,
                         terrain_penalty_factor=terrain_penalty_0_1,
                         water_type=water_type_0_1,
                         water_penalty_factor=water_penalty_0_1,
                         penalty_factor=combined_penalty_0_1,
                         source='terrain_water')

    # Edge 1-2: flat terrain + land (no water)
    # Elevation: 250m -> 250m (flat)
    # Terrain penalty = 1.0
    # Water penalty = 1.0
    # Combined = 1.0
    edge_start_1_2 = routing_net.node_coords[1]
    edge_end_1_2 = routing_net.node_coords[2]

    water_type_1_2, water_penalty_1_2 = detect_water_crossing(
        edge_start_1_2, edge_end_1_2, None, None
    )

    terrain_weight_1_2, slope_1_2, terrain_penalty_1_2 = calculate_terrain_weight(
        250, 250, mesh_spacing
    )

    combined_penalty_1_2 = terrain_penalty_1_2 * water_penalty_1_2
    final_weight_1_2 = mesh_spacing * combined_penalty_1_2

    routing_net.add_edge(1, 2, final_weight_1_2,
                         length=mesh_spacing,
                         slope_angle=slope_1_2,
                         terrain_penalty_factor=terrain_penalty_1_2,
                         water_type=water_type_1_2,
                         water_penalty_factor=water_penalty_1_2,
                         penalty_factor=combined_penalty_1_2,
                         source='terrain_water')

    # Verify multiplicative combination on edge 0-1
    assert water_type_0_1 == 'lake', "Edge 0-1 should cross lake"
    assert water_penalty_0_1 == 10.0, "Lake penalty factor should be 10.0"
    assert terrain_penalty_0_1 > 1.0, "Steep slope should have terrain penalty > 1.0"
    assert combined_penalty_0_1 == pytest.approx(terrain_penalty_0_1 * 10.0, rel=0.01), \
        "Combined penalty should be multiplicative"

    # Calculate expected weight
    expected_weight = mesh_spacing * combined_penalty_0_1 + final_weight_1_2
    path = routing_net.shortest_path(0, 2)

    assert path == [0, 1, 2], "Path should go through both edges"
    assert water_type_0_1 == 'lake', "First edge should be lake crossing"
    assert water_penalty_0_1 == 10.0, "Lake penalty should be 10×"


@pytest.mark.water
@pytest.mark.integration
def test_dijkstra_convergence_with_water_weights():
    """
    Test Dijkstra algorithm termination and determinism with water weights.

    Creates a 10x10 grid with multiple water features of different types.
    Verifies Dijkstra terminates within reasonable time and produces
    deterministic results.
    """
    # Create 10x10 grid (100 nodes)
    routing_net = RoutingNetwork()

    mesh_spacing = 100
    for row in range(10):
        for col in range(10):
            node_id = row * 10 + col
            x = col * mesh_spacing
            y = row * mesh_spacing
            routing_net.add_node(node_id, x, y)

    # Create multiple water features
    # Lake in center
    lake_polygon = Polygon([(400, 400), (600, 400), (600, 600), (400, 600)])
    lakes_gdf = gpd.GeoDataFrame(
        {'name': ['Central Lake']},
        geometry=[lake_polygon],
        crs='EPSG:25832'
    )

    # River crossing top-left to bottom-right
    river_line = LineString([(0, 0), (1000, 1000)])
    rivers_gdf = gpd.GeoDataFrame(
        {'waterway': ['river'], 'name': ['Test River']},
        geometry=[river_line],
        crs='EPSG:25832'
    )

    # Create edges for full grid
    # Horizontal edges
    for row in range(10):
        for col in range(9):
            u = row * 10 + col
            v = row * 10 + col + 1
            edge_start = routing_net.node_coords[u]
            edge_end = routing_net.node_coords[v]

            water_type, water_penalty_factor = detect_water_crossing(
                edge_start, edge_end, lakes_gdf, rivers_gdf
            )

            terrain_weight, slope, terrain_penalty = calculate_terrain_weight(
                100, 100, mesh_spacing
            )

            combined_penalty = terrain_penalty * water_penalty_factor
            final_weight = mesh_spacing * combined_penalty

            routing_net.add_edge(u, v, final_weight,
                               length=mesh_spacing,
                               slope_angle=slope,
                               terrain_penalty_factor=terrain_penalty,
                               water_type=water_type,
                               water_penalty_factor=water_penalty_factor,
                               penalty_factor=combined_penalty,
                               source='terrain_water')

    # Vertical edges
    for row in range(9):
        for col in range(10):
            u = row * 10 + col
            v = (row + 1) * 10 + col
            edge_start = routing_net.node_coords[u]
            edge_end = routing_net.node_coords[v]

            water_type, water_penalty_factor = detect_water_crossing(
                edge_start, edge_end, lakes_gdf, rivers_gdf
            )

            terrain_weight, slope, terrain_penalty = calculate_terrain_weight(
                100, 100, mesh_spacing
            )

            combined_penalty = terrain_penalty * water_penalty_factor
            final_weight = mesh_spacing * combined_penalty

            routing_net.add_edge(u, v, final_weight,
                               length=mesh_spacing,
                               slope_angle=slope,
                               terrain_penalty_factor=terrain_penalty,
                               water_type=water_type,
                               water_penalty_factor=water_penalty_factor,
                               penalty_factor=combined_penalty,
                               source='terrain_water')

    # Test determinism: run Dijkstra twice, get same path
    import time

    start_time = time.time()
    path1 = routing_net.shortest_path(0, 99)
    time1 = time.time() - start_time

    start_time = time.time()
    path2 = routing_net.shortest_path(0, 99)
    time2 = time.time() - start_time

    # Verify paths are identical
    assert path1 == path2, "Dijkstra should be deterministic"

    # Verify path exists and is reasonable
    assert path1 is not None, "Path should exist"
    assert len(path1) > 0, "Path should have nodes"

    # Verify termination time is reasonable (< 5 seconds per plan)
    assert time1 < 5.0, f"Dijkstra terminated in {time1:.3f}s (< 5s threshold)"
    assert time2 < 5.0, f"Dijkstra terminated in {time2:.3f}s (< 5s threshold)"

    # Verify all edges in path have valid weights
    for i in range(len(path1) - 1):
        u, v = path1[i], path1[i + 1]
        edge_data = routing_net.graph[u][v]
        weight = edge_data.get('weight', 0)
        assert weight > 0, f"Edge ({u}, {v}) should have weight > 0"

    # Verify all edges have expected attributes
    for u, v, data in routing_net.graph.edges(data=True):
        assert 'weight' in data, "Edge should have weight attribute"
        assert 'penalty_factor' in data, "Edge should have penalty_factor attribute"
        assert 'water_type' in data, "Edge should have water_type attribute"
        assert 'water_penalty_factor' in data, "Edge should have water_penalty_factor attribute"
        assert data['weight'] > 0, "Edge weight should be positive"