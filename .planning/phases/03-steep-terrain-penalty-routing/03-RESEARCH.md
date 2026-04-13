# Phase 3: Steep Terrain Penalty Routing - Research

**Researched:** 2026-04-13
**Domain:** Terrain-based routing with elevation penalties
**Confidence:** MEDIUM (with critical blocker on elevation data access)

## Summary

Phase 3 integrates Digital Terrain Model (DTM) elevation data into the routing network's edge weights, enabling pathfinding that considers slope and steepness. The phase builds on the existing `terrain_mesh_from_raster()` function from Phase 2, replacing uniform edge weights with terrain-aware penalties based on elevation differences between mesh nodes.

**Primary blocker identified**: The current `Raster` class wraps `tkinter.PhotoImage` which has no documented API for reading pixel values. This prevents access to elevation data needed for slope calculation. Before implementation can proceed, the project must decide on an approach: (1) add Pillow/PIL dependency for raster reading, (2) use PPM format dump workaround, or (3) store elevation data in numpy array format (NPZ) instead of raster images.

With the elevation data access solution in place, implementation follows the locked decisions from CONTEXT.md: calculate slope per mesh edge using `atan(elevation_diff / horizontal_distance)`, apply linear penalty scaling when slope > 20°, and integrate multiplicatively with existing Dijkstra pathfinding.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Slope = elevation_diff / raster_pixel_spacing. Compute slope directly from elevation differences between mesh nodes.
- **D-02:** Slope calculation applies per mesh edge. For each edge, compute elevation difference between two endpoint nodes, divide by edge length (mesh_spacing), convert to degrees: slope_angle = atan(elevation_diff / horizontal_distance).
- **D-03:** Penalty applies when slope > 20 degrees. Below or equal to 20°, no penalty.
- **D-04:** 20° chosen as aggressive threshold for Norway mountainous terrain.
- **D-05:** Linear scaling. Penalty_factor = 1.0 for slope ≤ 20°. For slope > 20°, penalty_factor = 1.0 + 0.2 × (slope - 20°).
- **D-06:** Multiplicative integration. Final weight = distance × penalty_factor.
- **D-07:** Continue with Dijkstra on updated weights. No change to existing `shortest_path()` implementation.

### Claude's Discretion
None — all technical decisions locked in CONTEXT.md.

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| COMP-02 | System applies fixed penalties for steep terrain to ensure realistic hiking routes | Locked decisions D-01 through D-07 provide complete implementation approach; math/numpy functions verified; existing Dijkstra in RoutingNetwork requires only edge weight updates |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| math (stdlib) | [VERIFIED] Python 3.14 | Trigonometric calculations (atan, degrees) | Built-in, no dependency, all required functions available |
| numpy | [VERIFIED] 2.4.4 | Array operations, elevation grid handling | Verified available via pip list; provides gradient, sqrt, array operations |
| networkx | [VERIFIED] 3.6.1 | Graph operations, Dijkstra pathfinding | Already used in Phase 2; Dijkstra with edge weights already implemented |
| scipy | [VERIFIED] 1.17.1 | KDTree for spatial queries | Already used in Phase 2 for neighbor search |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pyproj | [VERIFIED] In requirements.txt | Coordinate system handling | Already in use for EPSG transformations |
| [TBD] Pillow/PIL | - | PNG pixel reading (IF decision to add) | See "Critical Blocker" section below |
| [TBD] zlib (stdlib) | - | PNG decompression (IF no Pillow) | See alternative approaches below |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Edge-based slope (D-02) | 3x3 gradient window | CONTEXT.md chose edge-based for simplicity and direct mesh integration |
| Linear scaling (D-05) | Exponential/step function | Linear provides smooth gradients; locks decision in D-05 |
| Multiplicative (D-06) | Additive | Multiplicative represents "times harder" intuitively; locks decision in D-06 |

**Installation:**
```bash
# Core stack already installed (verified)
python3 -m pip install numpy networkx scipy pyproj

# IF choosing Pillow for raster reading:
python3 -m pip install Pillow
```

**Version verification:**
```bash
python3 -m pip list | grep -E "(numpy|networkx|scipy)"
# Output verified:
# networkx 3.6.1
# numpy 2.4.4
# scipy 1.17.1
```
[VERIFIED: pip list command execution on 2026-04-13]

## Architecture Patterns

### Recommended Project Structure
```
routing_2026.py          # Extend terrain_mesh_from_raster() with slope calc
tests/test_terrain_penalties.py  # New test file for slope/penalty tests
```

### Pattern 1: Terrain-Aware Edge Weight Calculation
**What:** Replace uniform edge weights in `terrain_mesh_from_raster()` with slope-based penalties.
**When to use:** Whenever generating terrain mesh edges from raster data.
**Example:**
```python
# Source: CONTEXT.md locked decisions D-01 through D-06

def calculate_terrain_weight(elev1, elev2, edge_length,
                             threshold_degrees=20.0, slope_multiplier=0.2):
    """
    Calculate edge weight with steep terrain penalty.
    
    Per CONTEXT.md D-02/D-03/D-05/D-06:
    - Slope calculated per mesh edge
    - 20° threshold for penalty
    - Linear scaling with k=0.2
    - Multiplicative integration
    """
    if edge_length == 0:
        return 0.0
    
    # D-02: Slope angle from elevation difference
    elevation_diff = elev2 - elev1
    slope_radians = math.atan(elevation_diff / edge_length)
    slope_degrees = math.degrees(slope_radians)
    
    # D-03/D-05: Linear penalty scaling
    if slope_degrees <= threshold_degrees:
        penalty_factor = 1.0
    else:
        penalty_factor = 1.0 + slope_multiplier * (slope_degrees - threshold_degrees)
    
    # D-06: Multiplicative weight
    return edge_length * penalty_factor, slope_degrees, penalty_factor
```
[VERIFIED: math module has atan, degrees functions - verified via Python execution]

### Pattern 2: Elevation Data Access
**What:** Extract elevation values from raster at mesh node coordinates.
**When to use:** In `terrain_mesh_from_raster()` when generating mesh nodes.
**Example (CONCEPTUAL - requires decision on raster reading approach):**
```python
# Source: Research - requires elevation data access solution
# BLOCKER: tkinter.PhotoImage has no pixel reading API

# Approach A (IF Pillow added):
from PIL import Image
elevation_grid = np.array(Image.open(raster._filename))

# Approach B (IF using PPM dump workaround):
import io
import base64
# tk.PhotoImage.dump() to PPM, parse PPM header + binary data

# Approach C (IF NPZ format):
elevation_grid = np.load('elevation.npz')['elevation']

# Then use world coordinates to map to grid indices:
col = int((x - world_x) / pixel_width)
row = int((y - world_y) / pixel_height)
elevation = elevation_grid[row, col]
```
[ASSUMED] - Raster elevation access requires technical decision (see Open Questions)

### Anti-Patterns to Avoid
- **Unary atan vs atan2 terrain slopes**: Using `atan(rise/run)` works for positive slopes, but `atan2(rise, run)` handles sign correctly. CONTEXT.md D-02 uses `atan(elevation_diff / edge_length)` which works for magnitude but consider `atan2` if directional slope matters.
- **Penalty on entire route**: Penalty applies per edge, not cumulatively on entire route. Each edge's weight = edge_length × penalty_factor.
- **Redundant slope calculation**: Cache slope per edge, don't recalculate for each shortest_path query.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Dijkstra pathfinding | Manual A*/Dijkstra implementation | `networkx.dijkstra_path` (already in use) | Dijkstra with edge weights already implemented in `RoutingNetwork.shortest_path()` per D-07; Dijkstra provides correct shortest path on weighted graphs |
| Trigonometric calculations | Manual sin/cos/tan implementations | `math.atan()`, `math.degrees()` (stdlib) | Standard library is battle-tested, performant, and readable |
| Edge weight lookup | Manual dictionary traversal | NetworkX edge attributes `G[u][v]['weight']` | NetworkX provides efficient adjacency access with metadata |

**Key insight:** The routing infrastructure (graph, Dijkstra) is complete from Phase 2. Phase 3 only modifies edge weight computation, not pathfinding algorithm.

## Runtime State Inventory

> Not applicable — this is a greenfield feature phase, not a rename/refactor/migration phase. No runtime state migration required.

## Common Pitfalls

### Pitfall 1: Elevation Data Access Blocker
**What goes wrong:** `tkinter.PhotoImage` used by current `Raster` class has no documented method to read pixel values in Python. Cannot access elevation data needed for slope calculation.
**Why it happens:** tkinter.PhotoImage is designed for display, not data extraction. The `data` attribute and `dump()` methods save image data externally, not return pixel array.
**How to avoid:** This is a known blocker requiring architectural decision before implementation. See Open Questions section for three approaches: (1) add Pillow dependency, (2) PPM dump workaround, (3) switch to NPZ format.
**Warning signs:** If trying to access `raster._photoimage.getpixel()` or similar API calls, this method doesn't exist.

### Pitfall 2: Division by Zero in Slope Calculation
**What goes wrong:** `math.atan(elevation_diff / edge_length)` raises ZeroDivisionError if edge_length is 0.
**Why it happens:** Mesh nodes can coincidentally have identical coordinates if raster spacing is small or world file has issues.
**How to avoid:** Add guard clause: `if edge_length == 0: return 0.0` before slope calculation.
**Warning signs:** ZeroDivisionError during terrain mesh generation.

### Pitfall 3: Penalty Factor Misinterpretation
**What goes wrong:** Applying penalty_factor additive rather than multiplicative.
**Why it happens:** Misreading D-06 decision. Some might implement `weight = distance + penalty` instead.
**How to avoid:** Follow D-06 exactly: `weight = distance × penalty_factor`. The penalty represents "times harder to hike", not additional cost.
**Warning signs:** Routes with unrealistic vertical climbs despite penalty function. Test: 100m edge at 45° should have weight = 600m (100m × 6.0), not 100m + 6.0 = 106m.

### Pitfall 4: Edge Direction Consideration
**What goes wrong:** Calculating slope using `elev2 - elev1` ignores that edges are bidirectional.
**Why it happens:** NetworkX Graph is undirected, so edge (u,v) = edge (v,u). Slope magnitude is same regardless of direction, but sign differs.
**How to avoid:** Use absolute elevation difference `abs(elev2 - elev1)` for slope magnitude, or implement bidirectional slopes if downhill/effort costs differ. CONTEXT.md D-02 uses absolute slope for "steepness" penalty.
**Warning signs:** Inconsistent weights when reversing start/end points in pathfinding test.

### Pitfall 5: Coordinate-to-Pixel Index Mapping Errors
**What goes wrong:** Incorrectly mapping world coordinates (x, y) to raster pixel indices (col, row), reading wrong elevation values.
**Why it happens:** Mixing up row/col vs x/y order, or not handling negative pixel_height in world file correctly.
**How to avoid:** Follow Phase 2 coordinate projection logic from `terrain_mesh_from_raster()` exactly:
```python
# From routing_2026.py:250-251 (Phase 2 implementation)
x = world_file[4] + col * pixel_width + row * world_file[1]
y = world_file[5] + row * pixel_height + col * world_file[2]

# Inverse for pixel lookup:
col = int((y - world_file[5] - row * world_file[2]) / pixel_height)
row = int((x - world_file[4] - col * pixel_width) / world_file[1])
```
**Warning signs:** Elevation values don't correlate with expected topography (e.g., flat mountains).

## Code Examples

Verified patterns from official sources:

### Slope Calculation with Penalty
```python
# Source: CONTEXT.md locked decisions + math module verification
# Verified functions: math.atan, math.degrees (Python 3.14)

import math

def calculate_terrain_penalty(elev1, elev2, edge_length,
                               threshold_degrees=20.0, slope_multiplier=0.2):
    """
    Calculate terrain penalty for edge between two nodes.
    
    Returns: (penalty_factor, slope_angle_degrees)
    """
    if edge_length == 0:
        return 1.0, 0.0
    
    elevation_diff = abs(elev2 - elev1)
    slope_radians = math.atan(elevation_diff / edge_length)
    slope_degrees = math.degrees(slope_radians)
    
    # D-03/D-05: Linear penalty scaling
    if slope_degrees <= threshold_degrees:
        penalty_factor = 1.0
    else:
        penalty_factor = 1.0 + slope_multiplier * (slope_degrees - threshold_degrees)
    
    return penalty_factor, slope_degrees

# Test with known values
edge_length = 100.0  # meters
elevations = [
    (100, 100),  # flat: 0° slope, 1.0x penalty
    (100, 136),  # 20° threshold: 1.0x penalty
    (100, 150),  # 26.6° slope: ~2.3x penalty
    (100, 200),  # 45° extreme: 6.0x penalty
]

print("Slope: Penalty Factor")
for e1, e2 in elevations:
    penalty, slope = calculate_terrain_penalty(e1, e2, edge_length)
    weight = edge_length * penalty
    print(f"{slope:5.1f}°: {penalty:4.1f}x = {weight:6.1f}m weight")
```
[VERIFIED: math.atan, math.degrees confirmed available - Python execution 2026-04-13]

### NetworkX Dijkstra with Custom Weights
```python
# Source: routing_2026.py:74-90 (existing implementation)
# Verified: networkx.dijkstra_path accepts 'weight' parameter

import networkx as nx

# Graph with terrain-weighted edges
G = nx.Graph()
G.add_edge(0, 1, weight=100.0)           # Flat terrain
G.add_edge(1, 2, weight=231.3, slope=26.6, penalty=2.3)  # Steep
G.add_edge(0, 2, weight=150.0)           # Alternative route

# Dijkstra finds minimal weighted path
path = nx.dijkstra_path(G, source=0, target=2, weight='weight')
# Returns path with minimal combined weight, considering terrain penalties
```
[VERIFIED: NetworkX 3.6.1 installed and used in Phase 2 - pip list 2026-04-13]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual A* implementation | networkx.dijkstra_path (Phase 2) | 2026-04-13 | Leverages optimized C backend, handles edge weights |
| Placeholder uniform weights | Terrain-aware weights (Phase 3) | 2026-04-13 (planned) | Routes avoid unrealistic vertical climbs |

**Deprecated/outdated:**
- Custom Dijkstra implementations: Use networkx instead (already adopted in Phase 2)
- Hand-rolled trigonometry: Python math module provides all needed functions

## Assumptions Log

> List all claims tagged `[ASSUMED]` in this research. The planner and discuss-phase use this section to identify decisions that need user confirmation before execution.

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Elevation data can be extracted from Raster class via one of three approaches: (1) Pillow/PIL dependency, (2) PPM dump workaround, or (3) NPZ format conversion | Elevation Data Access | HIGH - blocks entire Phase 3; tkinter.PhotoImage lacks pixel reading API |
| A2 | DTM50 data will be provided in NPZ or PNG format compatible with chosen elevation access approach | Elevation Data Access | MEDIUM - if format incompatible, conversion step needed |
| A3 | Mesh spacing parameter (default 100m in Phase 2) is appropriate for terrain slope accuracy | Architecture Patterns | LOW - can adjust mesh_spacing parameter if coarse resolution causes issues |
| A4 | Elevation grid coordinates align perfectly with world file affine transformation | Common Pitfalls | MEDIUM - coordinate rounding errors could read wrong pixels |

**If this table is empty:** All claims in this research were verified or cited — no user confirmation needed. *(Note: Table not empty - 4 assumptions require confirmation)*

## Open Questions

### Critical Blocker: Elevation Data Access

1. **How should we access elevation values from raster data?**
   - What we know: Current `Raster` class wraps `tkinter.PhotoImage` which has no documented pixel reading API. We verified that `getpixel()`, `load()`, `data()` methods don't exist or don't return numpy arrays.
   - What's unclear: Which approach should be adopted?
   - Recommendation: Choose one of three approaches:

   **Approach A: Add Pillow/PIL dependency**
   - Add `Pillow` to requirements.txt
   - Modify `Raster.read_image()` to also load elevation grid: `elevation_grid = np.array(Image.open(filename))`
   - Use `elevation_grid[row, col]` for elevation lookup
   - Pros: Standard library for image manipulation, widely used, well-documented
   - Cons: Adds dependency, increases project size

   **Approach B: PPM dump workaround (no new dependency)**
   - Use `tkinter.PhotoImage.dump()` to save as PPM format to temporary in-memory file
   - Parse PPM header and binary data manually using `struct` module
   - Pros: No new dependencies, uses standard library only
   - Cons: Complex parsing logic, relies on tkinter internal formats, potentially fragile

   **Approach C: Switch to NPZ format (numpy arrays)**
   - Convert DTMs from PNG to NPZ format (`np.savez('elevation.npz', elevation=elevation_grid)`)
   - Modify `Raster` class to load NPZ files instead of PNG
   - Pros: Direct numpy array access, no image decoding complexity, fast
   - Cons: Requires conversion step for existing raster data, not standard GIS format

2. **How should elevation data be stored in RoutingNetwork nodes for slope calculation?**
   - What we know: `terrain_mesh_from_raster()` creates nodes with (x, y) coordinates only
   - What's unclear: Should we add `elevation` attribute to each node during mesh generation?
   - Recommendation: Yes, add `elevation` attribute to nodes for easier slope calculation, or cache mesh grid indices to look up elevations from grid during edge weight calculation.

3. **Should penalty function parameters (threshold, multiplier) be configurable?**
   - What we know: CONTEXT.md D-03/D-04/D-05 lock values at 20° threshold and k=0.2 multiplier
   - What's unclear: Should these be function parameters with defaults or hardcoded constants?
   - Recommendation: Use function parameters with locked defaults (per CONTEXT.md decisions) to allow future v2 configuration without breaking v1.

**If no elevation data access solution is chosen:** Phase 3 implementation blocked. Planner must first resolve Q1 before creating tasks.

## Environment Availability

> Dependency check for Phase 3 (steep terrain penalty routing)

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| numpy | Slope calculations, elevation grid handling | ✓ | 2.4.4 | — |
| scipy | KDTree for spatial queries | ✓ | 1.17.1 | — |
| networkx | Dijkstra pathfinding | ✓ | 3.6.1 | — |
| math (stdlib) | Trigonometric functions | ✓ | Built-in | — |
| Pillow/PIL | PNG pixel reading (OPTIONAL) | ✗ | — | Use Approach B or C (see Open Questions) |
| pytest | Test framework | ✓ | 9.0.3 | — |

**Missing dependencies with no fallback:**
- None (if Pillow not chosen as elevation access approach)

**Missing dependencies with fallback:**
- Pillow/PIL (image pixel reading): If not installed, use Approach B (PPM dump with struct parsing) or Approach C (NPZ format with numpy arrays). See Open Question Q1.

**Environment audit date:** 2026-04-13

## Validation Architecture

> Per .planning/config.json: `workflow.nyquist_validation` is enabled (absent = true). Include validation architecture.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.3 |
| Config file | `pytest.ini` with `pythonpath = .` (verified in .planning/phases/02-routing-network-construction/tests/) |
| Quick run command | `python3 -m pytest tests/test_terrain_penalties.py -x -v` |
| Full suite command | `python3 -m pytest tests/ -v` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| COMP-02 | Slope calculation from elevation differences per edge | unit | `python3 -m pytest tests/test_terrain_penalties.py::test_slope_calculation -x` | ❌ Wave 0 |
| COMP-02 | 20° threshold penalty application | unit | `python3 -m pytest tests/test_terrain_penalties.py::test_penalty_threshold -x` | ❌ Wave 0 |
| COMP-02 | Linear scaling with k=0.2 multiplier | unit | `python3 -m pytest tests/test_terrain_penalties.py::test_linear_scaling -x` | ❌ Wave 0 |
| COMP-02 | Multiplicative weight integration | unit | `python3 -m pytest tests/test_terrain_penalties.py::test_multiplicative_weight -x` | ❌ Wave 0 |
| COMP-02 | Dijkstra routes avoid unrealistic climbs | integration | `python3 -m pytest tests/test_terrain_penalties.py::test_realistic_routing -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `python3 -m pytest tests/test_terrain_penalties.py -x`
- **Per wave merge:** `python3 -m pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/test_terrain_penalties.py` — covers COMP-02 (new test file)
- [ ] Elevation raster fixture or mock for testing slope calculations ( MOCK support depends on elevation data access decision)
- [ ] Framework install: pytest 9.0.3 — already verified available
- [ ] conftest.py updates: Add marker for Phase 3 terrain penalty tests

*(Note: Existing test infrastructure from Phase 2 suffices. New test file andMocks needed for elevation data.)*

## Security Domain

> Required when `security_enforcement` is enabled (absent = enabled). Security domain analysis for Phase 3.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | N/A (no auth in routing module) |
| V3 Session Management | no | N/A (no sessions) |
| V4 Access Control | no | N/A (no permission checks) |
| V5 Input Validation | yes | [math] - Validate edge_length > 0 before division; validate elevation values are numeric; validate slope_multiplier and threshold are reasonable numeric ranges |
| V6 Cryptography | no | N/A (no sensitive encryption) |

### Known Threat Patterns for Terrain-Based Routing Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|-----|
| Division by zero (slope calculation) | Denial of Service | Guard clause: `if edge_length == 0: return 0.0` before `math.atan(elevation_diff / edge_length)` |
| Invalid elevation values | Tampering (data poisoning) | Validate elevation ranges (e.g., -500m to 9000m for Norway) after reading from raster; reject NaN/infinite values |
| Extreme penalty factors DoS | Denial of Service | Clamp penalty_factor to maximum reasonable value (e.g., penalty_factor ≤ 100) to prevent astronomical edge weights |
| Coordinate rounding errors | Information Disclosure (wrong routes) | Use floor/round consistently when mapping world coordinates to pixel indices; test with known coordinates |

**Security implementation notes:**
- Terrain data (elevation, slope) is public geographic information per Phase 2 threat T-5-02 acceptance
- No new network endpoints or authentication paths introduced
- Input validation needed for elevation data reading (bounds checking, NaN validation)
- Division operations require zero-guard to prevent runtime errors

## Sources

### Primary (HIGH confidence)
- [CONTEXT.md] - Locked decisions D-01 through D-07 for slope calculation, penalty function, and weight integration [VERIFIED: Read 2026-04-13]
- [Python math module] - `math.atan()`, `math.degrees()` trigonometric functions availability [VERIFIED: Python execution 2026-04-13 confirmed all functions exist]
- [pip list] - numpy 2.4.4, networkx 3.6.1, scipy 1.17.1, pytest 9.0.3 installed [VERIFIED: Command execution 2026-04-13]
- [routing_2026.py] - Existing Dijkstra implementation at lines 74-90, graph structure, terrain_mesh_from_raster() function [VERIFIED: Read 2026-04-13]
- [tests/test_terrain_mesh.py] - TDD pattern, mock PhotoImage class for testing [VERIFIED: Read 2026-04-13]

### Secondary (MEDIUM confidence)
- [numpy.gradient documentation] - Gradient computation for elevation arrays (WebFetch verified) [CITED: numpy.org docs 2026-04-13]
- [networkx.dijkstra_path documentation] - Edge weight handling in pathfinding [CITED: CONTEXT.md references routing_2026.py implementation]
- [Slope calculation mathematics] - Formula `m = Δy/Δx`, `θ = arctan(m)` from engineering standards [CITED: Wikipedia/Slope via WebFetch 2026-04-13]

### Tertiary (LOW confidence)
- [WebSearch results] - tkinter PhotoImage pixel reading limitations (search returned no usable methods) [LOW: Could not verify official documentation; empirically confirmed no getpixel() method exists]
- [WebSearch results] - PNG reading without Pillow (complex binary parsing approaches) [LOW: Search results indicate PNG requires zlib/deflate decompression; verified via Python that zlib is available in stdlib but PNG chunk parsing is complex]

## Metadata

**Confidence breakdown:**
- Standard stack: [MEDIUM] - Verified numpy, networkx, scipy, pytest versions via pip list; math functions verified; Pillow availability unknown (not installed)
- Architecture: [MEDIUM] - Phase 2 patterns well-documented; slope calculation math verified via Python execution; elevation data access remains blocked
- Pitfalls: [HIGH] - Found critical blocker (PhotoImage pixel access); documentedZeroDivisionError, penalty misinterpretation, coordinate mapping risks
- Overall: [MEDIUM] - Clear path forward once elevation data access decision is made; all other components verified and available

**Research date:** 2026-04-13
**Valid until:** 30 days for stable stack (numpy, networkx, scipy versions change rarely); 7 days for web search accuracy (Pillow workaround approaches may have better solutions)

**Critical blocker resolution required before planning:**
- Elevation data access approach must be chosen (Open Question Q1)
- Elevation data format must be confirmed (NPZ vs PNG)
- Mock/test fixture strategy depends on elevation access approach