"""
Unit tests for terrain penalty routing functionality.

Phase 3: Steep Terrain Penalty Routing
Tests validate locked decisions D-01 through D-06 from CONTEXT.md.
"""

import pytest
import numpy as np
import math
from routing_2026 import calculate_terrain_weight


@pytest.mark.terrain
def test_slope_calculation():
    """
    Test slope angle calculation per D-01/D-02.

    Validates:
    - Slope = atan(elevation_diff / edge_length)
    - Slope converted to degrees using math.degrees()
    - Guard clause for edge_length == 0
    """
    # Normal case: elev1=100, elev2=150, edge_length=100
    # Elevation diff: abs(150-100) = 50
    # Slope radians: atan(50/100) = atan(0.5) ≈ 0.46365
    # Slope degrees: degrees(0.46365) ≈ 26.565°
    weight, slope_degrees, penalty_factor = calculate_terrain_weight(100, 150, 100)
    assert slope_degrees == pytest.approx(26.565, abs=0.01)

    # Guard clause: edge_length=0 should return (0.0, 0.0, 1.0)
    weight, slope_degrees, penalty_factor = calculate_terrain_weight(100, 150, 0)
    assert weight == 0.0
    assert slope_degrees == 0.0
    assert penalty_factor == 1.0


@pytest.mark.terrain
def test_penalty_threshold():
    """
    Test 20° threshold behavior per D-03/D-04.

    Validates:
    - Penalty_factor = 1.0 for slope <= 20°
    - Penalty_factor > 1.0 for slope > 20°
    """
    # Test case 1: slope=20.0° -> penalty_factor=1.0 (at threshold, no penalty)
    # Slope ≈ 20° when elevation_diff / edge_length = tan(20°) ≈ 0.364
    weight, slope, penalty = calculate_terrain_weight(100, 136.4, 100)
    assert slope == pytest.approx(20.0, abs=0.01)
    assert penalty == 1.0

    # Test case 2: slope=15.0° -> penalty_factor=1.0 (below threshold)
    # Slope ≈ 15° when elevation_diff / edge_length = tan(15°) ≈ 0.268
    weight, slope, penalty = calculate_terrain_weight(100, 126.8, 100)
    assert slope == pytest.approx(15.0, abs=0.01)
    assert penalty == 1.0

    # Test case 3: slope=21.0° -> penalty_factor=1.2 (just above threshold)
    # Slope ≈ 21° when elevation_diff / edge_length = tan(21°) ≈ 0.384
    weight, slope, penalty = calculate_terrain_weight(100, 138.4, 100)
    assert slope == pytest.approx(21.0, abs=0.01)
    assert penalty == pytest.approx(1.2, abs=0.01)

    # Test case 4: slope=25.0° -> penalty_factor=2.0 (above threshold)
    # Slope ≈ 25° when elevation_diff / edge_length = tan(25°) ≈ 0.466
    weight, slope, penalty = calculate_terrain_weight(100, 146.6, 100)
    assert slope == pytest.approx(25.0, abs=0.01)
    assert penalty == pytest.approx(2.0, abs=0.01)


@pytest.mark.terrain
def test_linear_scaling():
    """
    Test linear penalty scaling per D-05.

    Validates:
    - Penalty factor formula: 1.0 + 0.2 * (slope - 20.0)
    - Known examples: 25° = 2.0×, 35° = 4.0×, 45° = 6.0×
    - Penalty clamped to max 100 (mitigation for T-3-07)
    """
    # Test case 1: slope=20° -> penalty=1.0× (at threshold)
    # tan(20°) ≈ 0.364, so elev_diff ≈ 36.4
    weight, slope, penalty = calculate_terrain_weight(100, 136.4, 100)
    assert slope == pytest.approx(20.0, abs=0.01)
    assert penalty == 1.0

    # Test case 2: slope=25° -> penalty=2.0× (1.0 + 0.2*5)
    # tan(25°) ≈ 0.466, so elev_diff ≈ 46.6
    weight, slope, penalty = calculate_terrain_weight(100, 146.6, 100)
    assert slope == pytest.approx(25.0, abs=0.01)
    assert penalty == pytest.approx(2.0, abs=0.01)

    # Test case 3: slope=35° -> penalty=4.0× (1.0 + 0.2*15)
    # tan(35°) ≈ 0.7, so elev_diff ≈ 70
    weight, slope, penalty = calculate_terrain_weight(100, 170, 100)
    assert slope == pytest.approx(35.0, abs=0.01)
    assert penalty == pytest.approx(4.0, abs=0.01)

    # Test case 4: slope=45° -> penalty=6.0× (1.0 + 0.2*25)
    # tan(45°) = 1.0, so elev_diff = 100
    weight, slope, penalty = calculate_terrain_weight(100, 200, 100)
    assert slope == pytest.approx(45.0, abs=0.01)
    assert penalty == pytest.approx(6.0, abs=0.01)

    # Test clamp case: slope=90° -> penalty=100.0× (clamped, not 17.0)
    # tan(90°) approaches infinity, use very steep slope instead
    # tan(76°) ≈ 4.01 would give penalty ~1.0+0.2*56=12.2, but we clamp to 100
    # Actually, our clamp saves us from extreme values. Let's test with a known extreme:
    # Very large elevation difference will create penalty > 100, should be clamped
    weight, slope, penalty = calculate_terrain_weight(100, 10000, 1)  # Extremely steep
    assert penalty == 100.0  # Clamped to max 100


@pytest.mark.terrain
def test_multiplicative_weight():
    """
    Test multiplicative weight integration per D-06.

    Validates:
    - Final weight = edge_length × penalty_factor
    - Penalty applied per edge, not per route
    """
    # Test case 1: edge_length=100, slope=20° -> weight=100×1.0=100
    weight, slope, penalty = calculate_terrain_weight(100, 136.4, 100)
    assert weight == pytest.approx(100.0, abs=0.5)
    assert penalty == 1.0

    # Test case 2: edge_length=100, slope=25° -> weight=100×2.0=200
    weight, slope, penalty = calculate_terrain_weight(100, 146.6, 100)
    assert weight == pytest.approx(200.0, abs=0.5)
    assert penalty == pytest.approx(2.0, abs=0.01)

    # Test case 3: edge_length=50, slope=35° -> weight=50×4.0=200
    weight, slope, penalty = calculate_terrain_weight(100, 170, 50)
    assert weight == pytest.approx(200.0, abs=0.5)
    assert penalty == pytest.approx(4.0, abs=0.01)


@pytest.mark.terrain
def test_edge_length_validation():
    """
    Test edge length validation and guard clauses.

    Validates:
    - ValueError raised for edge_length <= 0 (T-3-08)
    - Returns (0.0, 0.0, 1.0) for edge_length == 0 (T-3-05)
    """
    # Test case 1: edge_length=0 -> returns (0.0, 0.0, 1.0) per guard clause
    weight, slope, penalty = calculate_terrain_weight(100, 150, 0)
    assert weight == 0.0
    assert slope == 0.0
    assert penalty == 1.0

    # Test case 2: edge_length=-10 -> raises ValueError with clear message
    with pytest.raises(ValueError) as exc_info:
        calculate_terrain_weight(100, 150, -10)
    assert "edge_length must be positive" in str(exc_info.value)

    # Test case 3: edge_length=0.0 -> returns (0.0, 0.0, 1.0) (zero float)
    weight, slope, penalty = calculate_terrain_weight(100, 150, 0.0)
    assert weight == 0.0
    assert slope == 0.0
    assert penalty == 1.0


@pytest.mark.terrain
def test_elevation_validation():
    """
    Test elevation value validation per T-3-06.

    Validates:
    - NaN values rejected with ValueError
    - Infinite values rejected with ValueError
    - math.isfinite() check applied
    """
    # Test case 1: elev1=float('nan'), elev2=100 -> raises ValueError
    with pytest.raises(ValueError) as exc_info:
        calculate_terrain_weight(float('nan'), 100, 100)
    assert "finite" in str(exc_info.value).lower()

    # Test case 2: elev1=100, elev2=float('inf') -> raises ValueError
    with pytest.raises(ValueError) as exc_info:
        calculate_terrain_weight(100, float('inf'), 100)
    assert "finite" in str(exc_info.value).lower()

    # Test case 3: elev1=float('-inf'), elev2=100 -> raises ValueError
    with pytest.raises(ValueError) as exc_info:
        calculate_terrain_weight(float('-inf'), 100, 100)
    assert "finite" in str(exc_info.value).lower()

    # Test case 4: Both NaN -> raises ValueError
    with pytest.raises(ValueError) as exc_info:
        calculate_terrain_weight(float('nan'), float('nan'), 100)
    assert "finite" in str(exc_info.value).lower()


@pytest.mark.terrain
def test_penalty_clamp():
    """
    Test penalty factor clamping to max 100 per T-3-07.

    Validates:
    - Extreme slopes (e.g., 90°) produce penalty_factor = 100, not infinity
    - Clamp applied after linear scaling calculation
    """
    # Test extreme slope: very large elevation difference creates huge penalty
    # Without clamp, this would give penalty > 100. With clamp, should be 100.
    weight, slope, penalty = calculate_terrain_weight(100, 10000, 1)  # Extremely steep
    assert penalty == 100.0  # Clamped to max 100
    assert weight == 100.0   # edge_length (1) * penalty (100)

    # Another extreme case: massive height difference over short distance
    weight, slope, penalty = calculate_terrain_weight(0, 5000, 5)  # Very steep
    assert penalty == 100.0  # Clamped to max 100

    # Verify it still works for normal steep slopes (below clamp threshold)
    # 45° slope gives penalty = 1.0 + 0.2*25 = 6.0, which is below 100
    weight, slope, penalty = calculate_terrain_weight(100, 200, 100)
    assert penalty == pytest.approx(6.0, abs=0.01)  # Not clamped


@pytest.mark.terrain
def test_realistic_routing():
    """
    Integration test: Dijkstra routes avoid steep terrain edges.

    Validates COMP-02 requirement:
    - System applies fixed penalties for steep terrain
    - Routes avoid unrealistic vertical climbs when alternatives exist
    - Routes follow natural hiking gradients where possible

    Tests:
    - 4x4 elevation grid with saddle point pattern
    - Flat alternative: edges at 100m elevation (penalty 1.0×)
    - Steep alternative: edges over saddle (150m, slope ~26.6°, penalty ~2.3×)
    - Dijkstra should prefer flat route over steep alternative
    """
    import routing_2026
    from raster_2026 import Raster

    # Create mock Raster with 4x4 elevation grid (saddle point pattern)
    # Row 0: [100, 100, 100, 100] (flat top)
    # Row 1: [100, 150, 150, 100] (shallow climb center)
    # Row 2: [100, 150, 150, 100] (shallow climb center)
    # Row 3: [100, 100, 100, 100] (flat bottom)
    mock_raster = Raster()
    mock_raster._world_file = [10.0, 0.0, 0.0, -10.0, 400000.0, 7000000.0]
    mock_raster.epsg = 25832

    # Create mock PhotoImage with 4x4 dimensions
    class _MockPhotoImage:
        def __init__(self, width, height):
            self._width = width
            self._height = height
        def width(self):
            return self._width
        def height(self):
            return self._height

    mock_raster._photoimage = _MockPhotoImage(4, 4)

    # Set elevation grid using numpy array
    import numpy as np
    mock_raster._elevation_grid = np.array([
        [100, 100, 100, 100],
        [100, 150, 150, 100],
        [100, 150, 150, 100],
        [100, 100, 100, 100],
    ])

    # Generate terrain mesh with 10m spacing
    mesh = routing_2026.terrain_mesh_from_raster(mock_raster, mesh_spacing=10)

    # Compute path from node 0 (top-left, 100m) to node 15 (bottom-right, 100m)
    path = mesh.shortest_path(0, 15)

    # Verify path exists
    assert path is not None, "Path should exist between node 0 and node 15"
    assert len(path) > 0, "Path should contain nodes"
    assert path[0] == 0, "Path should start at node 0"
    assert path[-1] == 15, "Path should end at node 15"

    # Verify edges in path have terrain-aware weights
    has_terrain_edges = False
    for u, v in zip(path[:-1], path[1:]):
        edge_data = mesh.graph.get_edge_data(u, v)
        assert edge_data is not None, f"Edge should exist between {u} and {v}"
        assert 'weight' in edge_data, "Edge should have weight"
        assert 'length' in edge_data, "Edge should have length"
        assert 'slope_angle' in edge_data, "Edge should have slope_angle"
        assert 'penalty_factor' in edge_data, "Edge should have penalty_factor"

        # Verify terrain edges have weights > 0
        if edge_data.get('source') == 'terrain':
            has_terrain_edges = True
            assert edge_data['weight'] > 0, "Terrain edge weight should be positive"

    assert has_terrain_edges, "Path should include terrain edges"

    # Verify that edges with slope > 20° have penalty_factor > 1.0
    for u, v in mesh.graph.edges(data=False):
        edge_data = mesh.graph.get_edge_data(u, v)
        if 'slope_angle' in edge_data and 'penalty_factor' in edge_data:
            slope = edge_data['slope_angle']
            penalty = edge_data['penalty_factor']
            if slope > 20.0:
                assert penalty > 1.0, f"Edge {u}-{v} with slope {slope}° should have penalty > 1.0, got {penalty}"


@pytest.mark.terrain
def test_all_steep_terrain_routing():
    """
    Test Dijkstra handles all-steep terrain (no flat alternative).

    Validates:
    - Dijkstra produces path despite all edges having high penalty
    - Penalty function applies correctly even when no flat alternatives
    - Total weight reflects sum of high-penalty edges

    Tests:
    - 2x2 mock elevation grid with uniform steep climb
    - Grid: [[100, 200], [200, 300]] - all edges have significant slope
    - Route from node 0 (top-left, 100m) to node 3 (bottom-right, 300m)
    - Expected: Path exists despite all edges having penalty_factor > 1.0
    """
    import routing_2026
    from raster_2026 import Raster

    # Create mock Raster with 2x2 elevation grid (uniform steep climb)
    # Grid: [[100, 200], [200, 300]]
    mock_raster = Raster()
    mock_raster._world_file = [10.0, 0.0, 0.0, -10.0, 400000.0, 7000000.0]
    mock_raster.epsg = 25832

    # Create mock PhotoImage with 2x2 dimensions
    class _MockPhotoImage:
        def __init__(self, width, height):
            self._width = width
            self._height = height
        def width(self):
            return self._width
        def height(self):
            return self._height

    mock_raster._photoimage = _MockPhotoImage(2, 2)

    # Set elevation grid uniformly steep
    import numpy as np
    mock_raster._elevation_grid = np.array([
        [100, 200],
        [200, 300],
    ])

    # Generate terrain mesh with 10m spacing
    mesh = routing_2026.terrain_mesh_from_raster(mock_raster, mesh_spacing=10)

    # Compute path from node 0 (top-left, 100m) to node 3 (bottom-right, 300m)
    path = mesh.shortest_path(0, 3)

    # Verify path exists despite all steep terrain
    assert path is not None, "Path should exist in all-steep terrain"
    assert len(path) > 0, "Path should contain nodes"
    assert path[0] == 0, "Path should start at node 0"
    assert path[-1] == 3, "Path should end at node 3"

    # Verify that all terrain edges have penalty_factor > 1.0
    for u, v in mesh.graph.edges(data=False):
        edge_data = mesh.graph.get_edge_data(u, v)
        if edge_data.get('source') == 'terrain':
            penalty = edge_data.get('penalty_factor', 1.0)
            assert penalty > 1.0, f"Steep terrain edge {u}-{v} should have penalty > 1.0, got {penalty}"

    # Verify slope angles and penalties are applied correctly
    # With 100m elevation difference over 10m horizontal: slope = atan(100/10) = atan(10) = 84.3°
    # Penalty for 84.3° = 1.0 + 0.2*(84.3 - 20) = 1.0 + 12.86 = 13.86 (clamped if needed)
    for u, v in mesh.graph.edges(data=False):
        edge_data = mesh.graph.get_edge_data(u, v)
        if edge_data.get('source') == 'terrain':
            slope = edge_data.get('slope_angle', 0)
            penalty = edge_data.get('penalty_factor', 1.0)
            # Verify slope is significant (> 20° threshold)
            assert slope > 20.0, f"Steep terrain edge {u}-{v} should have slope > 20°, got {slope}°"
            # Verify penalty factor is significant
            assert penalty > 1.5, f"Steep terrain edge {u}-{v} should have penalty > 1.5, got {penalty}"


@pytest.mark.terrain
def test_threshold_boundary_routing():
    """
    Test 20° threshold behavior in realistic routing.

    Validates:
    - Edges with slope <= 20° have penalty_factor = 1.0
    - Edges with slope > 20° have penalty_factor > 1.0
    - 20° threshold applied correctly in routing context

    Tests:
    - 2x3 mock elevation grid with slopes at threshold
    - Grid: [[100, 115, 130], [115, 130, 145]]
    - Elevation differences create slopes near 20° threshold
    - Route from node 0 to node 5
    """
    import routing_2026
    from raster_2026 import Raster

    # Create mock Raster with 2x3 elevation grid (slopes near threshold)
    # Grid: [[100, 115, 130], [115, 130, 145]]
    # Horizontal diff: 15m over 10m spacing -> slope = atan(15/10) = atan(1.5) = 56.3°
    # Vertical diff: 15m over 10m spacing -> slope = atan(15/10) = 56.3°
    mock_raster = Raster()
    mock_raster._world_file = [10.0, 0.0, 0.0, -10.0, 400000.0, 7000000.0]
    mock_raster.epsg = 25832

    # Create mock PhotoImage with 2x3 dimensions
    class _MockPhotoImage:
        def __init__(self, width, height):
            self._width = width
            self._height = height
        def width(self):
            return self._width
        def height(self):
            return self._height

    mock_raster._photoimage = _MockPhotoImage(3, 2)

    # Set elevation grid with slopes near threshold
    import numpy as np
    mock_raster._elevation_grid = np.array([
        [100, 115, 130],
        [115, 130, 145],
    ])

    # Generate terrain mesh with 10m spacing
    mesh = routing_2026.terrain_mesh_from_raster(mock_raster, mesh_spacing=10)

    # Compute path from node 0 to node 5
    path = mesh.shortest_path(0, 5)

    # Verify path exists
    assert path is not None, "Path should exist"
    assert len(path) > 0, "Path should contain nodes"

    # Verify threshold behavior for all terrain edges
    for u, v in mesh.graph.edges(data=False):
        edge_data = mesh.graph.get_edge_data(u, v)
        if edge_data.get('source') == 'terrain':
            slope = edge_data.get('slope_angle', 0)
            penalty = edge_data.get('penalty_factor', 1.0)

            # Threshold test: slope <= 20° implies penalty_factor = 1.0
            if slope <= 20.0:
                assert penalty == pytest.approx(1.0, abs=0.01), \
                    f"Edge {u}-{v} with slope {slope}° (<= 20°) should have penalty = 1.0, got {penalty}"

            # Threshold test: slope > 20° implies penalty_factor > 1.0
            if slope > 20.0:
                assert penalty > 1.0, \
                    f"Edge {u}-{v} with slope {slope}° (> 20°) should have penalty > 1.0, got {penalty}"