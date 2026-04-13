"""
Tests for terrain mesh generation from raster data.

Tests COMP-05 requirement: System uses terrain-based routing where trail network incomplete.
"""

import pytest
import numpy as np


# Test 1: terrain_mesh_from_raster returns RoutingNetwork instance
def test_terrain_mesh_returns_routing_network():
    """Test that terrain_mesh_from_raster returns RoutingNetwork instance."""
    import routing_2026
    from raster_2026 import Raster

    # Create mock Raster with necessary attributes
    mock_raster = Raster()
    mock_raster._world_file = [10.0, 0.0, 0.0, -10.0, 400000.0, 7000000.0]
    mock_raster.epsg = 25832  # UTM 32V
    mock_raster._photoimage = _MockPhotoImage(10, 10)

    # Generate terrain mesh
    mesh = routing_2026.terrain_mesh_from_raster(mock_raster, mesh_spacing=10)

    # Verify result is RoutingNetwork instance
    assert isinstance(mesh, routing_2026.RoutingNetwork), \
        "terrain_mesh_from_raster should return RoutingNetwork instance"
    assert mesh.epsg == 25832, "Mesh should inherit EPSG from raster"


# Test 2: Grid of nodes created based on mesh spacing
def test_terrain_mesh_node_grid():
    """Test that terrain mesh creates a regular grid of nodes."""
    import routing_2026
    from raster_2026 import Raster

    # Create mock Raster (10x10 pixels, 10m/pixel, 10m mesh spacing = 1 node per pixel)
    mock_raster = Raster()
    mock_raster._world_file = [10.0, 0.0, 0.0, -10.0, 400000.0, 7000000.0]
    mock_raster.epsg = 25832
    mock_raster._photoimage = _MockPhotoImage(10, 10)

    # Generate mesh
    mesh = routing_2026.terrain_mesh_from_raster(mock_raster, mesh_spacing=10)

    # Should have 100 nodes (10x10 grid)
    num_nodes = mesh.graph.number_of_nodes()
    assert num_nodes == 100, f"Expected 100 nodes in 10x10 grid, got {num_nodes}"


# Test 3: Edges connect adjacent nodes
def test_terrain_mesh_edge_topology():
    """Test that terrain mesh edges connect adjacent nodes correctly."""
    import routing_2026
    from raster_2026 import Raster

    # Create small 2x2 raster for simpler verification
    mock_raster = Raster()
    mock_raster._world_file = [10.0, 0.0, 0.0, -10.0, 400000.0, 7000000.0]
    mock_raster.epsg = 25832
    mock_raster._photoimage = _MockPhotoImage(2, 2)

    # Generate mesh
    mesh = routing_2026.terrain_mesh_from_raster(mock_raster, mesh_spacing=10)

    # Check edges exist (2x2 grid: 4 nodes, 4 edges)
    num_edges = mesh.graph.number_of_edges()
    assert num_edges >= 2, f"Expected at least 2 edges for 2x2 grid, got {num_edges}"

    # Verify edge attributes
    for u, v, edge_data in mesh.graph.edges(data=True):
        assert 'weight' in edge_data, "Edges should have weight attribute"
        assert 'source' in edge_data, "Edges should have source attribute"
        assert edge_data['source'] == 'terrain', "Edge source should be 'terrain'"


# Test: Node spacing matches mesh_spacing parameter
def test_mesh_spacing():
    """Test that node spacing matches the mesh_spacing parameter."""
    import routing_2026
    from raster_2026 import Raster

    # Create mock Raster (100x100 pixels, 10m/pixel)
    mock_raster = Raster()
    mock_raster._world_file = [10.0, 0.0, 0.0, -10.0, 400000.0, 7000000.0]
    mock_raster.epsg = 25832
    mock_raster._photoimage = _MockPhotoImage(100, 100)

    # Generate mesh with 20m spacing
    mesh = routing_2026.terrain_mesh_from_raster(mock_raster, mesh_spacing=20)

    # Should have 50x50 = 2500 nodes (100 pixels * 10m/pixel = 1000m, 1000m / 20m = 50 nodes per dimension)
    num_nodes = mesh.graph.number_of_nodes()
    expected_nodes = 2500
    assert num_nodes == expected_nodes, f"Expected {expected_nodes} nodes with 20m spacing on 100x100 pixel grid, got {num_nodes}"

    # Verify that nodes at adjacent positions are spaced at ~20m
    # Node 0 is at (0,0), Node 1 is at (1,0) in the grid
    node_0 = mesh.node_coords[0]
    node_1 = mesh.node_coords[1]
    dx = node_1[0] - node_0[0]
    dy = node_1[1] - node_0[1]
    distance = (dx**2 + dy**2)**0.5
    assert abs(distance - 20.0) < 0.1, f"Expected node spacing ~20m, got {distance}"


# Test: Node coordinates projected correctly
def test_terrain_mesh_coordinate_projection():
    """Test that node coordinates are projected correctly using world file."""
    import routing_2026
    from raster_2026 import Raster

    # Create mock Raster with known world file
    mock_raster = Raster()
    mock_raster._world_file = [10.0, 0.0, 0.0, -10.0, 400000.0, 7000000.0]
    mock_raster.epsg = 25832
    mock_raster._photoimage = _MockPhotoImage(3, 3)

    # Generate mesh
    mesh = routing_2026.terrain_mesh_from_raster(mock_raster, mesh_spacing=10)

    # Check first node (0,0) coordinate
    # x = world_file[4] + 0 * pixel_width + 0 * world_file[1]
    # y = world_file[5] + 0 * pixel_height + 0 * world_file[2]
    node_0_coord = mesh.node_coords[0]
    assert node_0_coord == (400000.0, 7000000.0), \
        f"Node 0 should be at (400000.0, 7000000.0), got {node_0_coord}"

    # Check second node (col=1, row=0) coordinate
    # x = 400000.0 + 1 * 10.0 = 400010.0
    node_1_coord = mesh.node_coords[1]
    assert node_1_coord == (400010.0, 7000000.0), \
        f"Node 1 should be at (400010.0, 7000000.0), got {node_1_coord}"


# Helper class to mock tkinter.PhotoImage
class _MockPhotoImage:
    """Mock PhotoImage for testing raster shape."""
    def __init__(self, width, height):
        self._width = width
        self._height = height

    def width(self):
        return self._width

    def height(self):
        return self._height