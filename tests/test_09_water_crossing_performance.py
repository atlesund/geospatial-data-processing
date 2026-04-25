"""
Test suite for Phase 9: Spatial index optimization for water crossing detection.

Validates:
1. Functional equivalence: indexed version produces identical results to naive
2. Performance: indexed version completes in reasonable time
3. Backward compatibility: existing Phase 4 tests still pass
"""

import pytest
import time
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon
import numpy as np
import routing_2026 as routing


def generate_synthetic_water_data(num_lakes=10, num_rivers=5, grid_size=10):
    """
    Generate synthetic water feature dataset for testing.

    Args:
        num_lakes: Number of lakes to create per row/column
        num_rivers: Number of rivers to create
        grid_size: Spacing between water features

    Returns:
        Tuple (lakes_gdf, rivers_gdf) - GeoDataFrames with synthetic water features
    """
    lakes = []
    for i in range(num_lakes):
        for j in range(num_lakes):
            center = Point(i * grid_size, j * grid_size)
            lakes.append({
                'name': f'Lake_{i}_{j}',
                'geometry': center.buffer(grid_size / 4)  # Circle radius
            })

    rivers = []
    for i in range(num_rivers):
        # Vertical rivers
        river = LineString([(i * grid_size, -grid_size), (i * grid_size, grid_size * num_rivers)])
        rivers.append({
            'name': f'River_{i}',
            'geometry': river
        })

    lakes_gdf = gpd.GeoDataFrame(lakes)
    rivers_gdf = gpd.GeoDataFrame(rivers)

    return lakes_gdf, rivers_gdf


def detect_water_crossing_naive(edge_start, edge_end, lakes_gdf, rivers_gdf,
                                lake_penalty=10.0, river_penalty=5.0, fjord_penalty=50.0):
    """
    Naive O(n×m) implementation of water crossing detection.

    This is the original implementation (pre-Phase 9) used for
    functional equivalence testing. Do NOT use in production.
    """
    if lakes_gdf is None and rivers_gdf is None:
        return (None, 1.0)

    x1, y1 = edge_start
    x2, y2 = edge_end
    midpoint = Point(((x1 + x2) / 2, (y1 + y2) / 2))

    # Check lakes (naive iteration)
    if lakes_gdf is not None and len(lakes_gdf) > 0:
        for idx, lake_row in lakes_gdf.iterrows():
            lake_geom = lake_row.geometry
            if midpoint.within(lake_geom):
                name = lake_row.get('name', '')
                if name and 'fjord' in str(name).lower():
                    return ('fjord', fjord_penalty)
                return ('lake', lake_penalty)

    # Check rivers (naive iteration)
    if rivers_gdf is not None and len(rivers_gdf) > 0:
        edge_line = LineString([edge_start, edge_end])
        for idx, river_row in rivers_gdf.iterrows():
            river_geom = river_row.geometry
            if edge_line.intersects(river_geom):
                return ('river', river_penalty)

    return (None, 1.0)


class TestFunctionalEquivalence:
    """Tests verifying indexed version produces identical results to naive version."""

    def test_equivalence_small_dataset(self):
        """Test functional equivalence with small dataset."""
        lakes_gdf, rivers_gdf = generate_synthetic_water_data(num_lakes=5, num_rivers=3)
        lake_tree, lakes_gdf_result, river_tree, rivers_gdf_result = routing.build_spatial_indexes(lakes_gdf, rivers_gdf)

        # Generate test edges covering various scenarios
        test_edges = [
            ((2.5, 2.5), (2.6, 2.6)),  # Inside lake
            ((0, -5), (5, 15)),  # Crosses river
            ((10, 10), (11, 11)),  # Open space
            ((2.5, 2.5), (3.5, 3.5)),  # Partial lake
            ((-1, -1), (1, 1)),  # Crosses lake and river
        ]

        for edge in test_edges:
            naive_result = detect_water_crossing_naive(
                edge[0], edge[1], lakes_gdf, rivers_gdf
            )
            indexed_result = routing.detect_water_crossing(
                edge[0], edge[1], lake_tree, river_tree,
                lakes_gdf=lakes_gdf_result, rivers_gdf=rivers_gdf_result
            )
            assert naive_result == indexed_result, \
                f"Edge {edge}: naive={naive_result}, indexed={indexed_result}"

    def test_equivalence_fjord_detection(self):
        """Test fjord detection equivalence."""
        # Create fjord
        lakes = [{'name': 'Sognefjorden', 'geometry': Point(0, 0).buffer(5)}]
        lakes_gdf = gpd.GeoDataFrame(lakes)
        lake_tree, lakes_gdf_result, river_tree, rivers_gdf_result = routing.build_spatial_indexes(
            lakes_gdf, gpd.GeoDataFrame()
        )

        edge = ((0, 0), (1, 1))
        naive_result = detect_water_crossing_naive(
            edge[0], edge[1], lakes_gdf, gpd.GeoDataFrame()
        )
        indexed_result = routing.detect_water_crossing(
            edge[0], edge[1], lake_tree, None,
            lakes_gdf=lakes_gdf_result, rivers_gdf=None
        )
        assert naive_result == indexed_result == ('fjord', 50.0)

    def test_equivalence_empty_data(self):
        """Test equivalence with empty GeoDataFrames."""
        empty_lakes = gpd.GeoDataFrame({'geometry': []})
        empty_rivers = gpd.GeoDataFrame({'geometry': []})

        lake_tree, lakes_gdf_result, river_tree, rivers_gdf_result = routing.build_spatial_indexes(
            empty_lakes, empty_rivers
        )
        assert lake_tree is None and river_tree is None

        edge = ((0, 0), (1, 1))
        naive_result = detect_water_crossing_naive(edge[0], edge[1], empty_lakes, empty_rivers)
        indexed_result = routing.detect_water_crossing(edge[0], edge[1], lake_tree, river_tree)
        assert naive_result == indexed_result == (None, 1.0)

    def test_equivalence_none_inputs(self):
        """Test equivalence with None inputs."""
        edge = ((0, 0), (1, 1))
        naive_result = detect_water_crossing_naive(edge[0], edge[1], None, None)
        indexed_result = routing.detect_water_crossing(edge[0], edge[1], None, None)
        assert naive_result == indexed_result == (None, 1.0)


class TestPerformance:
    """Tests for performance validation of spatial index optimization."""

    def test_performance_small_dataset(self):
        """Test performance with small dataset (100 edges)."""
        lakes_gdf, rivers_gdf = generate_synthetic_water_data(num_lakes=10, num_rivers=5)
        lake_tree, lakes_gdf_result, river_tree, rivers_gdf_result = routing.build_spatial_indexes(
            lakes_gdf, rivers_gdf
        )

        # Generate 100 test edges
        test_edges = [
            ((np.random.uniform(0, 50), np.random.uniform(0, 50)),
             (np.random.uniform(0, 50), np.random.uniform(0, 50)))
            for _ in range(100)
        ]

        start = time.time()
        for edge in test_edges:
            _ = routing.detect_water_crossing(
                edge[0], edge[1], lake_tree, river_tree,
                lakes_gdf=lakes_gdf_result, rivers_gdf=rivers_gdf_result
            )
        elapsed = time.time() - start

        assert elapsed < 2.0, f"100 edges took {elapsed:.2f}s (expected <2s)"
        print(f"Performance: 100 edges in {elapsed:.3f}s ({elapsed*1000:.1f}ms/edge)")

    def test_performance_medium_dataset(self):
        """Test performance with medium dataset (1000 edges)."""
        lakes_gdf, rivers_gdf = generate_synthetic_water_data(num_lakes=20, num_rivers=10)
        lake_tree, lakes_gdf_result, river_tree, rivers_gdf_result = routing.build_spatial_indexes(
            lakes_gdf, rivers_gdf
        )

        # Generate 1000 test edges
        test_edges = [
            ((np.random.uniform(0, 100), np.random.uniform(0, 100)),
             (np.random.uniform(0, 100), np.random.uniform(0, 100)))
            for _ in range(1000)
        ]

        start = time.time()
        for edge in test_edges:
            _ = routing.detect_water_crossing(
                edge[0], edge[1], lake_tree, river_tree,
                lakes_gdf=lakes_gdf_result, rivers_gdf=rivers_gdf_result
            )
        elapsed = time.time() - start

        assert elapsed < 5.0, f"1000 edges took {elapsed:.2f}s (expected <5s)"
        print(f"Performance: 1000 edges in {elapsed:.3f}s ({elapsed*1000/1000:.1f}ms/edge)")

    def test_build_index_performance(self):
        """Test spatial index build performance."""
        lakes_gdf, rivers_gdf = generate_synthetic_water_data(num_lakes=100, num_rivers=50)

        start = time.time()
        lake_tree, lakes_gdf_result, river_tree, rivers_gdf_result = routing.build_spatial_indexes(
            lakes_gdf, rivers_gdf
        )
        elapsed = time.time() - start

        assert elapsed < 2.0, f"Index build took {elapsed:.2f}s (expected <2s)"
        assert lake_tree is not None and river_tree is not None
        print(f"Index build: {len(lakes_gdf)} lakes, {len(rivers_gdf)} rivers in {elapsed:.3f}s")


class TestBackwardCompatibility:
    """Tests for backward compatibility with existing Phase 4 functionality."""

    def test_mesh_generation_no_water_queries(self):
        """Test mesh generation with water queries disabled."""
        # This tests backward compatibility (enable_water_queries=False)
        # Uses synthetic raster if available, otherwise skips
        try:
            from raster_2026 import Raster
            import os
            from pathlib import Path

            # Use relative path from test file location
            test_dir = Path(__file__).parent.parent.parent
            test_tif = test_dir / 'data' / 'dtm_50_1000.tif'

            if test_tif.exists():
                test_raster = Raster()
                test_raster.read_image(str(test_tif))

                mesh_net = routing.terrain_mesh_from_raster(
                    test_raster, mesh_spacing=50, enable_water_queries=False
                )

                assert mesh_net is not None
                assert len(mesh_net.node_coords) > 0

                # Check that edges exist before accessing them
                edge_list = list(mesh_net.graph.edges(data=True))
                assert len(edge_list) > 0, "Graph should contain edges"

                # Verify edge attributes exist
                edge_data = edge_list[0]
                assert 'water_type' in edge_data[2]
                assert 'water_penalty_factor' in edge_data[2]
        except ImportError:
            pytest.skip("Raster module not available")
        except FileNotFoundError:
            pytest.skip("Test raster not found")

    def test_edge_penalty_factors(self):
        """Test that edge penalty factors are calculated correctly."""
        lakes_gdf, rivers_gdf = generate_synthetic_water_data(num_lakes=3, num_rivers=2)
        lake_tree, lakes_gdf_result, river_tree, rivers_gdf_result = routing.build_spatial_indexes(
            lakes_gdf, rivers_gdf
        )

        # Edge inside lake (10× penalty) - use edge clearly inside lake (lake center at 0,0, radius 2.5)
        result = routing.detect_water_crossing(
            (0.5, 0.5), (0.6, 0.6), lake_tree, river_tree,
            lakes_gdf=lakes_gdf_result
        )
        assert result[0] == 'lake' and result[1] == 10.0

        # Edge crossing river (5× penalty) - river at x=0 from y=-10 to y=20, our edge crosses x=0 line
        result = routing.detect_water_crossing(
            (-1, 0), (1, 0), lake_tree, river_tree,
            rivers_gdf=rivers_gdf_result
        )
        assert result[0] == 'river' and result[1] == 5.0

        # Edge in open space (1× penalty) - far from any water features
        result = routing.detect_water_crossing((20, 20), (21, 21), lake_tree, river_tree)
        assert result == (None, 1.0)


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_empty_lakes_valid_rivers(self):
        """Test with empty lakes but valid rivers."""
        empty_lakes = gpd.GeoDataFrame({'geometry': []})
        rivers = [{'name': 'River', 'geometry': LineString([(0, -5), (0, 5)])}]
        rivers_gdf = gpd.GeoDataFrame(rivers)

        lake_tree, lakes_gdf_result, river_tree, rivers_gdf_result = routing.build_spatial_indexes(
            empty_lakes, rivers_gdf
        )
        assert lake_tree is None
        assert river_tree is not None

        result = routing.detect_water_crossing(
            (-1, -1), (1, 1), lake_tree, river_tree,
            rivers_gdf=rivers_gdf_result
        )
        assert result[0] == 'river'

    def test_valid_lakes_empty_rivers(self):
        """Test with valid lakes but empty rivers."""
        lakes = [{'name': 'Lake', 'geometry': Point(0, 0).buffer(5)}]
        lakes_gdf = gpd.GeoDataFrame(lakes)
        empty_rivers = gpd.GeoDataFrame({'geometry': []})

        lake_tree, lakes_gdf_result, river_tree, rivers_gdf_result = routing.build_spatial_indexes(
            lakes_gdf, empty_rivers
        )
        assert lake_tree is not None
        assert river_tree is None

        result = routing.detect_water_crossing(
            (0, 0), (1, 1), lake_tree, river_tree,
            lakes_gdf=lakes_gdf_result
        )
        assert result[0] == 'lake'

    def test_edge_exactly_on_river_line(self):
        """Test edge that exactly coincides with river line."""
        rivers = [{'name': 'River', 'geometry': LineString([(0, 0), (10, 10)])}]
        rivers_gdf = gpd.GeoDataFrame(rivers)
        lake_tree, lakes_gdf_result, river_tree, rivers_gdf_result = routing.build_spatial_indexes(
            gpd.GeoDataFrame({'geometry': []}), rivers_gdf
        )

        # Edge exactly on river line
        result = routing.detect_water_crossing(
            (5, 5), (6, 6), lake_tree, river_tree,
            rivers_gdf=rivers_gdf_result
        )
        assert result[0] == 'river'


if __name__ == '__main__':
    # Run tests with pytest if available, otherwise skip
    try:
        pytest.main([__file__, '-v', '--tb=short'])
    except:
        print("pytest not available, skipping automated test run")