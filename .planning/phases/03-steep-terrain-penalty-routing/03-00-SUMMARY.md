---
phase: 03-steep-terrain-penalty-routing
plan: 00
subsystem: testing
tags: [test-scaffold, pytest, terrain]
dependency_graph:
  requires: []
  provides: [test_terrain_penalties.py, conftest elevation_grid]
  affects: []
tech_stack:
  added: []
  patterns: ["pytest fixtures", "TDD red-green-refactor"]
key_files:
  created: [tests/test_terrain_penalties.py]
  modified: [tests/conftest.py]
metrics:
  duration: 9 minutes
  completed_date: 2026-04-13
---

# Phase 03-00: Test Scaffold for Terrain Penalty Functionality

**One-liner:** Test infrastructure with 9 test stubs covering all locked decisions (D-01 through D-06) and pytest fixtures for terrain testing.

## Summary

Created test scaffold for Phase 3 terrain penalty functionality following TDD methodology. Generated tests/test_terrain_penalties.py with 9 test stubs that validate all locked decisions from CONTEXT.md and COMP-02 requirements. Updated tests/conftest.py with pytest.mark.terrain marker and elevation_grid fixture for test data.

## Tasks Completed

### Task 1: Create test_terrain_penalties.py with test stubs
- Created tests/test_terrain_penalties.py with 9 test functions
- All tests marked with @pytest.mark.terrain decorator
- Test stubs cover D-01/D-02 (slope calculation), D-03/D-04 (20° threshold), D-05 (linear scaling), D-06 (multiplicative weight)
- Additional tests for validation scenarios: edge_length, elevation values, penalty clamping
- Integration test stub for realistic routing (COMP-02)
- **Commit:** 3071cd0 (in worktree), 35f0ca1 (merged to development)

### Task 2: Update conftest.py with terrain marker and elevation_grid fixture
- Added pytest_configure() extension to register "terrain: Mark test as Phase 3 terrain penalty test" marker
- Added elevation_grid() fixture returning 4x4 numpy array with saddle point pattern
- Fixture provides mock elevation data: 100m edges, 150m center point for slope testing
- **Commit:** 5ef881c

## Deviations from Plan

### Auto-fixed Issues

Agent completed with API error but work was successfully committed. Manually verified file contents match plan specification exactly.

## Authentication Gates

None encountered.

## Known Stubs

All 9 tests are intentionally stubbed with pytest.skip() following TDD RED phase:
- test_slope_calculation: Will calculate slope = atan(elevation_diff / edge_length)
- test_penalty_threshold: Will validate 20° penalty threshold behavior
- test_linear_scaling: Will validate k=0.2 linear scaling formula
- test_multiplicative_weight: Will validate weight = edge_length × penalty_factor
- test_edge_length_validation: Will validate edge_length guard clauses
- test_elevation_validation: Will validate math.isfinite() checks
- test_penalty_clamp: Will validate max 100 penalty factor clamp
- test_realistic_routing: Will validate COMP-02 requirement after terrain weighting integration

## Threat Flags

No threat surfaces. Plan 0 creates test infrastructure only, no production code.

## Technical Details

**Test Design:**
Following TDD methodology from Phase 1-2 patterns:
- Tests written before implementation (RED phase)
- Pytest markers for categorization (@pytest.mark.terrain)
- Fixtures for shared test data (elevation_grid)
- Skip messages provide clear guidance for implementation order

**Fixture Data:**
The elevation_grid fixture provides a 4x4 numpy array with intentional terrain pattern:
```
[[100, 100, 100, 100],  # Row 0: flat top edge
 [100, 150, 150, 100],  # Row 1: shallow climb from left
 [100, 150, 150, 100],  # Row 2: shallow climb from left
 [100, 100, 100, 100]]  # Row 3: flat bottom edge
```
This pattern creates measurable slopes for testing calculations.

## Files Modified

1. **tests/test_terrain_penalties.py** - Created new test file with 9 stubbed test functions
2. **tests/conftest.py** - Added terrain marker and elevation_grid fixture

## Integration Points

These test stubs will be greened by subsequent phase plans:
- Plan 03-02: Implement calculate_terrain_weight() -> greens slope/threshold/scaling/weight tests
- Plan 03-04: Integration with terrain_mesh_from_raster() -> greens realistic_routing test

## Self-Check: PASSED

- [x] tests/test_terrain_penalties.py file created
- [x] File contains 9 test stubs with @pytest.mark.terrain decorator
- [x] test_slope_calculation stub present (validates D-01/D-02)
- [x] test_penalty_threshold stub present (validates D-03/D-04)
- [x] test_linear_scaling stub present (validates D-05)
- [x] test_multiplicative_weight stub present (validates D-06)
- [x] test_edge_length_validation stub present (validates T-3-05/T-3-08)
- [x] test_elevation_validation stub present (validates T-3-06)
- [x] test_penalty_clamp stub present (validates T-3-07)
- [x] test_realistic_routing stub present (validates COMP-02 integration)
- [x] All stubs use pytest.skip() with descriptive messages
- [x] tests/conftest.py has pytest_configure with terrain marker
- [x] tests/conftest.py has elevation_grid fixture returning 4x4 numpy array
- [x] Pytest collection succeeds for all 9 tests
- [x] Pytest marker can be used with -m terrain flag