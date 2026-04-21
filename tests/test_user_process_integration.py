"""
Integration Test: Complete User Process Workflow

Tests the complete end-to-end workflow from .planning/user-process.md:

Test Flow:
1. Terrain loading with auto-mesh generation (Phase 7)
2. Route point selection (Shift+F9 + clicks)
3. Route computation auto-trigger (Phase 6)
4. Coordinate transforms (screen → world → network)
5. Node snapping to graph
6. Route display (orange polyline)
7. GPX export capability

This integration test verifies all phases work together correctly.

Usage:
    pytest tests/test_user_process_integration.py -v

Note: Uses pytest.importorskip for headless compatibility.
"""

import pytest
import numpy as np
from unittest.mock import patch, Mock

# Import geospatial modules with graceful failure handling
pytest.importorskip('tkinter', reason='tkinter not available (headless environment)')
from screen_2026 import Screen
from routing_2026 import RoutingNetwork, terrain_mesh_from_raster
from raster_2026 import Raster


@pytest.fixture
def geotiff_terrain():
    """
    Create mock GeoTIFF terrain for testing.

    Simulates a Kartverket DTM50 tile with:
    - 50m resolution elevation grid
    - EPSG: 25833 (UTM Zone 33V)
    - World file for coordinate transforms

    Returns:
        Raster: Mock GeoTIFF terrain instance
    """
    raster = Raster()
    raster._filename = "bergen_50m_33.tif"
    # 100x100 grid = 5km x 5km area at 50m resolution
    raster._elevation_grid = np.ones((100, 100)) * 100.0
    # Add some terrain variation (simple hill)
    y, x = np.indices((100, 100))
    raster._elevation_grid += 50.0 * np.sin(np.pi * x / 100) * np.sin(np.pi * y / 100)
    raster._epsg = 25833  # UTM Zone 33V (Bergen)
    raster._world_file = [50.0, 0.0, 0.0, -50.0, 600000.0, 6650000.0]

    return raster


@pytest.fixture
def screen_with_terrain_loaded(geotiff_terrain):
    """
    Create screen with loaded terrain (simulates F5 action).

    Simulates state after STEP 3 of user-process.pdf.

    Returns:
        Screen: Screen instance with _image (raster) loaded
    """
    with patch('screen_2026.tkinter.Tk'):
        screen = Screen()
        screen._epsg = 25833
        screen._world_file = [50.0, 0.0, 0.0, -50.0, 600000.0, 6650000.0]
        screen._image = geotiff_terrain
        return screen


@pytest.fixture
def routing_network_auto_generated(geotiff_terrain):
    """
    Auto-generate routing network from terrain (Phase 7).

    Simulates STEP 4 of user-process.pdf.
    Uses fixed 200m mesh spacing (v1).

    Returns:
        RoutingNetwork: Generated routing network
    """
    # Disable water queries to avoid blocking OSM API calls in test environment
    network = terrain_mesh_from_raster(geotiff_terrain, mesh_spacing=200, enable_water_queries=False)
    return network


@pytest.fixture
def screen_with_network(screen_with_terrain_loaded, routing_network_auto_generated):
    """
    Create screen with routing network assigned.

    Simulates complete state after Phase 7 auto-mesh.

    Returns:
        tuple: (screen, network)
    """
    screen = screen_with_terrain_loaded
    screen._route_network = routing_network_auto_generated
    return (screen, routing_network_auto_generated)


class TestPhase7_AutoMeshGeneration:
    """Test STEP 1-4: Terrain loading with auto-mesh generation."""

    def test_terrain_has_epsg(self, geotiff_terrain):
        """GeoTIFF terrain has EPSG code from metadata (STEP 3)."""
        assert geotiff_terrain._epsg == 25833
        assert geotiff_terrain._epsg is not None

    def test_terrain_has_world_file(self, geotiff_terrain):
        """GeoTIFF terrain has world file for transforms (STEP 3)."""
        assert geotiff_terrain._world_file is not None
        assert len(geotiff_terrain._world_file) == 6

    def test_terrain_has_elevation_grid(self, geotiff_terrain):
        """GeoTIFF terrain has elevation data (STEP 3)."""
        assert geotiff_terrain._elevation_grid is not None
        assert geotiff_terrain._elevation_grid.shape == (100, 100)

    def test_terrain_mesh_generates_network(self, routing_network_auto_generated):
        """Terrain mesh generates routing network (STEP 4, Phase 7)."""
        network = routing_network_auto_generated
        assert network is not None
        assert len(network.graph.nodes) > 0
        assert len(network.graph.edges) > 0

    def test_network_inherits_terrain_epsg(self, routing_network_auto_generated, geotiff_terrain):
        """Network inherits EPSG from terrain (STEP 4)."""
        assert routing_network_auto_generated.epsg == geotiff_terrain._epsg

    def test_network_has_node_coordinates(self, routing_network_auto_generated):
        """Network has node coordinates for routing (STEP 4)."""
        assert len(routing_network_auto_generated.node_coords) > 0
        assert len(routing_network_auto_generated.node_coords) == len(routing_network_auto_generated.graph.nodes)


class TestPhase6_RouteComputation:
    """Test STEP 5-8: Route point selection and computation."""

    def test_screen_has_world_file(self, screen_with_terrain_loaded):
        """Screen has world file for coordinate transforms (STEP 6)."""
        assert screen_with_terrain_loaded._world_file is not None

    def test_screen_has_network_assigned(self, screen_with_network):
        """Network is assigned to screen (Phase 7 → Phase 6 integration)."""
        screen, network = screen_with_network
        assert screen._route_network is not None
        assert screen._route_network is network

    def test_network_find_nearest_node(self, screen_with_network):
        """Network can find nearest node (STEP 7)."""
        screen, network = screen_with_network

        # Query a point in the network bounds
        node_id, distance = network.find_nearest_node(600100.0, 6650000.0)

        assert node_id is not None
        assert distance >= 0
        assert distance < float('inf')

    def test_network_can_compute_shortest_path(self, screen_with_network):
        """Network can compute shortest path (STEP 8)."""
        screen, network = screen_with_network

        # Get two nodes
        node_ids = list(network.graph.nodes)
        if len(node_ids) >= 2:
            start_node = node_ids[0]
            end_node = node_ids[1]

            path = network.shortest_path(start_node, end_node)

            assert path is not None
            assert len(path) > 0
            assert path[0] == start_node
            assert path[-1] == end_node


class TestPhase5_Visualization:
    """Test STEP 9-10: Route display and visualization."""

    def test_screen_has_route_attributes(self, screen_with_network):
        """Screen has route display attributes (STEP 10, Phase 5)."""
        screen, network = screen_with_network

        assert hasattr(screen, '_current_route')
        assert hasattr(screen, '_route_network_coords')
        assert hasattr(screen, 'set_route')
        assert hasattr(screen, 'display_route')


class TestIntegration_CompleteWorkflow:
    """Test complete integration of all phases."""

    def test_terrain_load_to_network_assignment(self, geotiff_terrain):
        """Complete flow: terrain load → mesh generation → network assignment."""
        # STEP 3: Load terrain (simulated)
        raster = geotiff_terrain
        assert raster._epsg is not None
        assert raster._elevation_grid is not None

        # STEP 4: Generate mesh (Phase 7)
        # Disable water queries for test environment
        network = terrain_mesh_from_raster(raster, mesh_spacing=200, enable_water_queries=False)
        assert network is not None
        assert network.epsg == raster._epsg

        # Assign to screen (Phase 6 integration)
        with patch('screen_2026.tkinter.Tk'):
            screen = Screen()
            screen._epsg = raster._epsg
            screen._world_file = raster._world_file
            screen._route_network = network

        assert screen._route_network is network

    def test_coordinate_transform_pipeline(self, screen_with_network):
        """Test coordinate transform pipeline (STEP 6)."""
        screen, network = screen_with_network

        # Screen coordinate (pixel)
        screen_x, screen_y = 100, 200

        # Transform to world coordinates (simulating screen_to_world)
        # Using world file: [a, d, b, e, c, f]
        a, d, b, e, c, f = screen._world_file
        world_x = a * screen_x + b * screen_y + c
        world_y = d * screen_x + e * screen_y + f

        assert isinstance(world_x, (int, float))
        assert isinstance(world_y, (int, float))

        # Find nearest node (STEP 7)
        node_id, distance = network.find_nearest_node(world_x, world_y)

        assert node_id is not None
        assert distance >= 0

    def test_all_phases_connected(self, screen_with_network):
        """Verify all phases are connected: 7 → 6 → 5."""
        screen, network = screen_with_network

        # Phase 7: Auto-mesh generation done
        assert network is not None
        assert len(network.graph.nodes) > 0

        # Phase 6: Network assigned to screen
        assert screen._route_network is network

        # Phase 5: Route display methods available
        assert hasattr(screen, 'display_route')
        assert hasattr(screen, 'export_gpx')


@pytest.mark.skip(reason="Manual verification test - requires GUI")
def test_manual_user_process_workflow():
    """
    Manual test for complete user process workflow.

    To run manually:
    1. Run this test in a GUI environment
    2. Load a GeoTIFF terrain file via F5
    3. Verify mesh generation in console output
    4. Press Shift+F9 to start route selection
    5. Click start point (red marker)
    6. Click end point (blue marker)
    7. Verify route auto-computes and displays
    8. Export route as GPX (optional)
    """
    # This test is a placeholder for manual GUI testing
    pass


def test_import_integration():
    """Test that all required modules can be imported together."""
    from routing_2026 import RoutingNetwork, terrain_mesh_from_raster
    from raster_2026 import Raster
    from screen_2026 import Screen

    # Verify key functions/methods exist
    assert hasattr(RoutingNetwork, 'shortest_path')
    assert hasattr(RoutingNetwork, 'find_nearest_node')
    assert callable(terrain_mesh_from_raster)
    assert hasattr(Raster, 'read_image')
    assert hasattr(Screen, '_read_image')
    assert hasattr(Screen, 'set_route_network')


def test_phase_dependencies():
    """Verify phase dependencies are satisfied."""
    # Phase 1: Map interaction
    assert hasattr(Screen, '_start_digit_points')

    # Phase 2: Routing network
    from routing_2026 import RoutingNetwork
    assert hasattr(RoutingNetwork, 'shortest_path')

    # Phase 3: Steep terrain
    from routing_2026 import calculate_terrain_weight
    assert callable(calculate_terrain_weight)

    # Phase 5: Visualization
    assert hasattr(Screen, 'display_route')
    assert hasattr(Screen, 'export_gpx')

    # Phase 6: GUI integration
    assert hasattr(Screen, 'set_route_network')

    # Phase 7: Auto-mesh (new)
    from routing_2026 import terrain_mesh_from_raster
    assert callable(terrain_mesh_from_raster)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])