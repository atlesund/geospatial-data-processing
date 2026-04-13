# Phase 2 Test Infrastructure

Test fixtures and utilities for Phase 2: Routing Network Construction.

## Purpose

Phase 2 involves building a routing network from multiple data sources:
- Established hiking trails (polylines)
- OpenStreetMap data (osmnx)
- Terrain-based mesh generation

This test infrastructure provides mock data and fixtures to support graph construction,
OSM integration, and trail conversion testing.

## Fixtures

### `mock_routing_network`

Creates a simple networkx.Graph with 4 nodes and 4 edges.

**Returns:**
- `graph`: networkx.Graph instance
- `epsg`: 25832 (UTM zone 32V)
- `node_coords`: Dictionary mapping node IDs to (x, y) coordinate tuples

**Node coordinates (UTM 32V):**
- Node 0: (450000.0, 6500000.0)
- Node 1: (450100.0, 6500100.0)
- Node 2: (450200.0, 6500000.0)
- Node 3: (450100.0, 6500200.0)

**Edge weights:** All edges have weight=100 (representing 100m segments)

### `mock_osm_graph`

Creates a mock osmnx-like MultiDiGraph structure with ~5 nodes and ~6 edges.

**Returns:** networkx.MultiDiGraph with osmnx-style attributes

**Node attributes:**
- Integer IDs (0-4)
- `x`, `y` coordinates in projected CRS (EPSG 25832)

**Edge attributes:**
- `length`: Distance in meters
- `highway`: Path type (path, footway, track)

### `mock_trail_vector`

Creates a geo.Vector instance with 2-3 trail polylines forming a connected network.

**Returns:** geo.Vector with POLYLINE geometry

**Trail polylines (UTM 32V):**
- Trail 1: (450000, 6500000) → (450100, 6500100) → (450200, 6500000)
- Trail 2: (450200, 6500000) → (450300, 6500100) → (450400, 6500000)
- Trail 3: (450100, 6500100) → (450100, 6500200) → (450200, 6500200)

**Attributes:**
- `name`: Trail_N (N is trail number)
- `type`: 'hiking'

### `mock_world_file`

Provides affine transformation from world file for raster georeferencing.

**Returns:** [12.0, 0.0, 0.0, -12.0, 450000.0, 6500000.0]

## Running Tests

Run all Phase 2 tests:
```bash
pytest .planning/phases/02-routing-network-construction/tests/
```

Run specific test subsets using markers:
```bash
pytest .planning/phases/02-routing-network-construction/tests/ -m routing
pytest .planning/phases/02-routing-network-construction/tests/ -m osmnx
pytest .planning/phases/02-routing-network-construction/tests/ -m trails
pytest .planning/phases/02-routing-network-construction/tests/ -m terrain
```

List available fixtures:
```bash
pytest .planning/phases/02-routing-network-construction/tests/ --fixtures -v
```

## Test Data

Test data files should be placed in the `data/` subdirectory.

## Dependencies

- geo_2026 (main geospatial library)
- networkx>=3.6.1
- scipy>=1.17.1
- osmnx>=2.1.0
- pytest>=8.0.0