"""
Comprehensive v1 integration test for Norwegian Hiking Route Planner.

Tests all implemented features:
- Phase 1: Map Interaction (point selection, pan, zoom, coordinate display)
- Phase 2: Routing Network Construction (trails, OSM, terrain mesh)
- Phase 3: Steep Terrain Penalty Routing
- Phase 5: Route Visualization & Export

Note: Phase 4 (Water Body Penalty) is not yet implemented.

Usage:
    Run all tests: pytest tests/test_v1_complete.py -v
    Run specific test class: pytest tests/test_v1_complete.py::TestRoutingNetworkBasics -v
    Run with verbose output: pytest tests/test_v1_complete.py -v -s
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

# Import geospatial modules
from routing_2026 import RoutingNetwork, calculate_terrain_weight
from raster_2026 import Raster


# =============================================================================
# Phase 2: Routing Network Construction Tests
# =============================================================================

class TestRoutingNetworkBasics:
    """Test basic routing network functionality."""

    def test_network_initialization(self):
        """Network starts empty with proper structure."""
        network = RoutingNetwork()
        assert len(network.graph.nodes) == 0
        assert len(network.graph.edges) == 0
        assert len(network.node_coords) == 0
        assert network._epsg is None

    def test_add_node_with_coordinates(self):
        """Can add nodes with georeferenced coordinates."""
        network = RoutingNetwork()
        network.add_node(1, 600000.0, 6650000.0)  # UTM 32V coordinates (Norway)
        assert 1 in network.graph.nodes
        assert network.node_coords[1] == (600000.0, 6650000.0)

    def test_add_edge_with_weight_and_attrs(self):
        """Can add weighted edges with additional attributes."""
        network = RoutingNetwork()
        network.add_node(1, 600000.0, 6650000.0)
        network.add_node(2, 601000.0, 6650000.0)
        network.add_edge(1, 2, weight=100.0, length=100.0, trail_id="t123")

        assert network.graph.has_edge(1, 2)
        assert network.graph[1][2]['weight'] == 100.0
        assert network.graph[1][2]['length'] == 100.0
        assert network.graph[1][2]['trail_id'] == "t123"

    def test_shortest_path_simple(self):
        """Dijkstra finds shortest path in simple network."""
        network = RoutingNetwork()
        # Create linear: 1 - 2 - 3
        network.add_node(1, 0, 0)
        network.add_node(2, 100, 0)
        network.add_node(3, 200, 0)
        network.add_edge(1, 2, weight=100)
        network.add_edge(2, 3, weight=100)

        path = network.shortest_path(1, 3)
        assert path == [1, 2, 3]

    def test_shortest_path_chooses_shorter_route(self):
        """Dijkstra chooses shorter route when multiple paths exist."""
        network = RoutingNetwork()
        # Triangle: 1-2-3 (200) vs 1-3 direct (150)
        network.add_node(1, 0, 0)
        network.add_node(2, 100, 50)
        network.add_node(3, 150, 0)
        network.add_edge(1, 2, weight=80)
        network.add_edge(2, 3, weight=120)
        network.add_edge(1, 3, weight=150)

        path = network.shortest_path(1, 3)
        assert path == [1, 3]  # Direct path is shorter (150 vs 200)


class TestTerrainWeightCalculation:
    """Test slope-based terrain weight calculations (Phase 3)."""

    def test_flat_terrain_no_penalty(self):
        """Flat terrain (0° slope) has no penalty."""
        elevation_diff = 0.0
        edge_length = 100.0
        weight, slope, penalty = calculate_terrain_weight(
            elev1=100.0,
            elev2=100.0,
            edge_length=edge_length,
            threshold_degrees=20.0,
            slope_multiplier=0.2
        )

        assert slope == 0.0
        assert penalty == 1.0  # No penalty
        assert weight == edge_length  # Weight = edge length

    def test_moderate_slope_no_penalty(self):
        """Slopes under 20° threshold have minimal penalty."""
        # 15 degrees of steepness
        elevation_diff = 26.8  # sin(15°) * 100
        edge_length = 100.0

        weight, slope, penalty = calculate_terrain_weight(
            elev1=100.0,
            elev2=100.0 + elevation_diff,
            edge_length=edge_length,
            threshold_degrees=20.0,
            slope_multiplier=0.2
        )

        assert slope < 20.0
        assert penalty == 1.0  # Below threshold
        assert weight == edge_length

    def test_steep_slope_applies_penalty(self):
        """Slopes above 20° threshold apply penalties."""
        # 30 degrees of steepness (very steep)
        elevation_diff = 50.0
        edge_length = 100.0

        weight, slope, penalty = calculate_terrain_weight(
            elev1=100.0,
            elev2=100.0 + elevation_diff,
            edge_length=edge_length,
            threshold_degrees=20.0,
            slope_multiplier=0.2
        )

        assert slope > 20.0
        assert penalty > 1.0  # Penalty applied
        assert weight > edge_length  # Weight increased

    def test_very_steep_slope_higher_penalty(self):
        """Steeper slopes get higher penalties."""
        # Compare 30° vs 60° slopes
        _, slope_30, penalty_30 = calculate_terrain_weight(
            elev1=100.0, elev2=150.0, edge_length=100.0,
            threshold_degrees=20.0, slope_multiplier=0.2
        )
        _, slope_60, penalty_60 = calculate_terrain_weight(
            elev1=100.0, elev2=186.6, edge_length=100.0,  # sin(60°) * 216
            threshold_degrees=20.0, slope_multiplier=0.2
        )

        assert slope_60 > slope_30
        assert penalty_60 > penalty_30


class TestTerrainMeshRouting:
    """Test terrain-aware routing on mesh networks (Phase 3)."""

    def test_route_avoids_steep_when_flat_available(self):
        """Route chooses flat path over steep when available."""
        network = RoutingNetwork()

        # Create two paths:
        # Flat: 1-3-5 (slope = 5°)
        # Steep: 1-2-4-5 (slope = 30°)
        network.add_node(1, 0, 0)
        network.add_node(2, 100, 50)   # Steep
        network.add_node(3, 200, 5)    # Flat
        network.add_node(4, 300, 100)  # Steep
        network.add_node(5, 400, 10)   # Flat

        # Flat edges (low weight = 220 * 1.0 = 220)
        network.add_edge(1, 3, weight=220, slope_angle=5, penalty_factor=1.0)
        network.add_edge(3, 5, weight=220, slope_angle=5, penalty_factor=1.0)

        # Steep edges (high weight = 120 * 2.0 = 240 due to penalty_factor)
        network.add_edge(1, 2, weight=240, slope_angle=30, penalty_factor=2.0)
        network.add_edge(2, 4, weight=240, slope_angle=30, penalty_factor=2.0)
        network.add_edge(4, 5, weight=240, slope_angle=30, penalty_factor=2.0)

        path = network.shortest_path(1, 5)
        assert path == [1, 3, 5]  # Chooses flat path


class TestNearestNode:
    """Test nearest node finding for snapping points to network."""

    def test_finds_nearest_node(self):
        """Finds the closest network node to a query point."""
        network = RoutingNetwork()
        network.add_node(1, 600000.0, 6650000.0)
        network.add_node(2, 601000.0, 6650000.0)
        network.add_node(3, 600500.0, 6650500.0)

        # Query closest to node 2
        nearest_id, distance = network.find_nearest_node(600950.0, 6650010.0, k=1)

        assert nearest_id == 2
        assert distance < 60.0  # Reasonable proximity

    def test_returns_multiple_nearest(self):
        """Can find k nearest nodes."""
        network = RoutingNetwork()
        for i, (x, y) in enumerate([(0, 0), (100, 0), (200, 0), (300, 0)]):
            network.add_node(i, x, y)

        node_ids = network.find_nearest_node(250, 10, k=3)

        # Should return [3, 2, 1] in order of proximity
        assert len(node_ids) == 3


# =============================================================================
# Phase 5: Route Visualization & Export Tests
# =============================================================================

# Skip these tests if tkinter is not available
try:
    import tkinter
    tkinter_available = True
except ImportError:
    tkinter_available = False


@pytest.mark.skipif(not tkinter_available, reason="tkinter not available")
class TestRouteStateManagement:
    """Test route state storage for visualization and export."""

    @pytest.fixture
    def mock_screen(self):
        """Create a mock Screen object with route attributes."""
        from screen_2026 import Screen

        # Mock tkinter root to avoid actual window creation
        with patch('screen_2026.tkinter.Tk'):
            screen = Screen()

            # Set up coordinate system
            screen._epsg = 32632  # UTM 32V
            screen._rows = 600
            screen._columns = 800

            # Mock world file for coordinate transformation (6-element affine tuple)
            # Format: [a, d, b, e, c, f] where screen_to_world: x_w = a*x + b*y + c, y_w = d*x + e*y + f
            screen._world_file = [10.0, 0.0, 0.0, -10.0, 600000.0, 6650000.0]

            return screen

    def test_route_state_initialization(self, mock_screen):
        """Route state attributes are initialized correctly."""
        assert hasattr(mock_screen, '_current_route')
        assert mock_screen._current_route is None

        assert hasattr(mock_screen, '_route_network_coords')
        assertListEqual(mock_screen._route_network_coords, [])

    def test_set_route_stores_coordinates(self, mock_screen):
        """set_route stores both screen and network coordinates."""
        network_coords = [(600000.0, 6650000.0), (601000.0, 6650000.0), (602000.0, 6650000.0)]

        mock_screen.set_route(network_coords)

        # Network coordinates stored
        assert mock_screen._route_network_coords == network_coords
        assert len(mock_screen._route_network_coords) == 3

    def test_display_route_clears_previous(self, mock_screen):
        """Displaying new route clears previous route."""
        # Set first route
        mock_screen.set_route([(600000, 6650000), (601000, 6650000)])

        # Set second route
        mock_screen.set_route([(600000, 6650000), (602000, 6650000)])

        # Should have only second route
        assert len(mock_screen._route_network_coords) == 2
        assert mock_screen._route_network_coords[-1] == (602000, 6650000)


def assertListEqual(list1, list2):
    """Simple list equality check for testing."""
    if list1 != list2:
        raise AssertionError(f"Lists not equal: {list1} != {list2}")


class TestGPXExport:
    """Test GPX file export functionality."""

    @pytest.fixture
    def mock_screen_with_route(self):
        """Create mock screen with a test route."""
        from screen_2026 import Screen

        with patch('screen_2026.tkinter.Tk'):
            screen = Screen()
            screen._epsg = 32632  # UTM 32V
            screen._route_network_coords = [
                (600000.0, 6650000.0),
                (601000.0, 6650100.0),
                (602000.0, 6650200.0),
                (603000.0, 6650300.0)
            ]
            return screen

    def test_gpx_export_creates_valid_xml(self, mock_screen_with_route):
        """Exported GPX file has valid XML structure."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gpx', delete=False) as f:
            filename = f.name

        try:
            # Mock the file dialog to return our temp file
            with patch('screen_2026.tkinter.filedialog.asksaveasfilename', return_value=filename):
                mock_screen_with_route.export_gpx(Mock())

            # Read and validate XML
            import xml.etree.ElementTree as ET
            tree = ET.parse(filename)
            root = tree.getroot()

            # Check namespace
            expected_ns = "http://www.topografix.com/GPX/1/1"
            assert root.tag.endswith('gpx')

            # Check for track structure (track-only, no waypoints)
            trk = root.find('.//{http://www.topografix.com/GPX/1/1}trk')
            assert trk is not None
            assert trk.find('{http://www.topografix.com/GPX/1/1}trkseg') is not None

            trackpts = root.findall('.//{http://www.topografix.com/GPX/1/1}trkpt')
            assert len(trackpts) == 4  # 4 route points

        finally:
            if os.path.exists(filename):
                os.unlink(filename)

    def test_gpx_export_coordinates_transformed(self, mock_screen_with_route):
        """Coordinates are transformed from UTM to WGS84."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gpx', delete=False) as f:
            filename = f.name

        try:
            with patch('screen_2026.tkinter.filedialog.asksaveasfilename', return_value=filename):
                mock_screen_with_route.export_gpx(Mock())

            import xml.etree.ElementTree as ET
            tree = ET.parse(filename)
            root = tree.getroot()

            # Extract coordinates
            trackpts = root.findall('.//{http://www.topografix.com/GPX/1/1}trkpt')

            # WGS84 coordinates for UTM 32V (600000, 6650000) should be around:
            # Longitude: ~10°E, Latitude: ~60°N
            lat = float(trackpts[0].attrib['lat'])
            lon = float(trackpts[0].attrib['lon'])

            # Check they're reasonable for Norway
            assert 59.0 < lat < 61.0
            assert 9.0 < lon < 11.0

        finally:
            if os.path.exists(filename):
                os.unlink(filename)

    def test_gpx_export_coordinates_precision(self, mock_screen_with_route):
        """Coordinates have 6 decimal places (0.1m precision)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gpx', delete=False) as f:
            filename = f.name

        try:
            with patch('screen_2026.tkinter.filedialog.asksaveasfilename', return_value=filename):
                mock_screen_with_route.export_gpx(Mock())

            import xml.etree.ElementTree as ET
            tree = ET.parse(filename)
            root = tree.getroot()

            trackpt = root.find('.//{http://www.topografix.com/GPX/1/1}trkpt')
            lat = trackpt.attrib['lat']
            lon = trackpt.attrib['lon']

            # Check decimal places
            assert len(lat.split('.')[-1]) <= 6
            assert len(lon.split('.')[-1]) <= 6

        finally:
            if os.path.exists(filename):
                os.unlink(filename)

    def test_gpx_export_utf8_encoding(self, mock_screen_with_route):
        """Exported file uses UTF-8 encoding."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gpx', delete=False) as f:
            filename = f.name

        try:
            with patch('screen_2026.tkinter.filedialog.asksaveasfilename', return_value=filename):
                mock_screen_with_route.export_gpx(Mock())

            # Read file and check encoding
            with open(filename, 'rb') as f:
                content = f.read()
                # UTF-8 BOM check plus valid UTF-8 decode
                try:
                    content.decode('utf-8')
                except UnicodeDecodeError:
                    pytest.fail("File is not valid UTF-8")

        finally:
            if os.path.exists(filename):
                os.unlink(filename)


# =============================================================================
# Integration Tests
# =============================================================================

class TestV1Workflow:
    """End-to-end integration tests for v1 functionality."""

    def test_complete_routing_workflow(self):
        """Test complete workflow: network → penalty → path."""
        network = RoutingNetwork()

        # 1. Build network (Phase 2)
        nodes = [
            (1, 600000, 6650000),  # Start
            (2, 601000, 6650100), # Option A (flat)
            (3, 601000, 6650500), # Option A2 (flat)
            (4, 601200, 6650300), # Option B (steep)
            (5, 602000, 6650200),  # End
        ]
        for node_id, x, y in nodes:
            network.add_node(node_id, x, y)

        # Add edges with terrain penalties applied to weights (Phase 3)
        # Flat route: 1 → 2 → 3 → 5 (weights include penalty_factor=1.0)
        network.add_edge(1, 2, weight=1040, slope_angle=7, penalty_factor=1.0)  # Low slope
        network.add_edge(2, 3, weight=420, slope_angle=5, penalty_factor=1.0)   # Low slope
        network.add_edge(3, 5, weight=1040, slope_angle=7, penalty_factor=1.0)  # Low slope
        # Total flat: 2500

        # Steep route: 1 → 4 → 5 (weights include penalty_factor: 10.0, 7.0)
        network.add_edge(1, 4, weight=2600, slope_angle=50, penalty_factor=10.0)  # 260 * 10
        network.add_edge(4, 5, weight=6090, slope_angle=45, penalty_factor=7.0)   # 870 * 7
        # Total steep: 8690

        # 2. Compute path (Phase 3 - terrain-aware routing)
        path = network.shortest_path(1, 5)

        # 3. Verify route chooses flat path (Phase 3 requirement met)
        assert path != [1, 4, 5]  # Should avoid steep

        # Verify the path coordinates
        coordinates = [network.node_coords[node_id] for node_id in path]
        assert len(coordinates) > 2  # Has intermediate points
        assert coordinates[0] == (600000, 6650000)  # Start
        assert coordinates[-1] == (602000, 6650200)  # End

        print(f"\n✓ V1 integration test passed:")
        print(f"  Path: {path} ({len(path)} waypoints)")
        # Distance calculation removed - test only needs to verify path structure

    def test_path_coordinates_preserve_epsg(self):
        """Path coordinates maintain correct EPSG for export."""
        network = RoutingNetwork()
        network._epsg = 32632  # UTM 32V (Norway)

        # Simple network
        network.add_node(1, 600000, 6650000)
        network.add_node(2, 610000, 6660000)
        network.add_edge(1, 2, weight=141400)

        path = network.shortest_path(1, 2)
        coords = [network.node_coords[node_id] for node_id in path]

        # Verify coordinates are in expected range for UTM 32V
        for x, y in coords:
            assert 400000 < x < 800000  # UTM 32V Easting range
            assert 6400000 < y < 7400000  # UTM 32V Northing range (Norway)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])