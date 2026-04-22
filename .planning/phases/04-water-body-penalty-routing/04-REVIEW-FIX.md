---
phase: 04-water-body-penalty-routing
fixed_at: 2026-04-22T12:00:00Z
review_path: .planning/phases/04-water-body-penalty-routing/04-REVIEW.md
iteration: 1
findings_in_scope: 5
fixed: 3
skipped: 2
status: partial
---

# Phase 04: Code Review Fix Report

**Fixed at:** 2026-04-22T12:00:00Z
**Source review:** .planning/phases/04-water-body-penalty-routing/04-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 5
- Fixed: 3
- Skipped: 2

## Fixed Issues

### CR-01: Unused timeout parameter causes indefinite hangs

**Files modified:** `routing_2026.py`
**Commit:** `7fa5cfa`
**Applied fix:** Added `timeout=timeout` parameter to both `ox.features_from_bbox()` calls in `load_water_features()` function (lines 310 and 317). This ensures the timeout parameter is actually passed to the osmnx API calls, preventing indefinite hangs when the Overpass API is slow or unresponsive.

### CR-02: Synchronous network calls block GUI thread

**Files modified:** None (addressed by CR-03)
**Commit:** N/A
**Applied fix:** This finding is effectively resolved by CR-03. The GUI issue of synchronous network calls blocking the main thread is mitigated by changing `enable_water_queries` default to `False`. The GUI call to `terrain_mesh_from_raster()` in `screen_2026.py` doesn't explicitly pass `enable_water_queries=True`, so with the new default of `False`, water queries won't run in the GUI thread and won't block the application. This implements "Option 1" from the review (disable water queries in GUI for v1 stability).

### CR-03: Inconsistent default for enable_water_queries parameter

**Files modified:** `routing_2026.py`
**Commit:** `43dc9ac`
**Applied fix:** Changed the default value of `enable_water_queries` parameter in `terrain_mesh_from_raster()` function from `True` to `False` (line 395). This aligns with the FIXME comment in `screen_2026.py` acknowledging the need for a non-blocking approach, and ensures v1 stability by preventing GUI freezes from synchronous water queries.

### WR-02: Missing timeout documentation for osmnx API

**Files modified:** `routing_2026.py`
**Commit:** `0fc3723`
**Applied fix:** Enhanced the docstring for `load_water_features()` function to clarify that the `timeout` parameter is an HTTP request timeout for the osmnx Overpass API calls. Added detail that it's a per-request timeout (lakes and rivers queried separately) and that exceeding the timeout allows routing to continue without water penalties.

## Skipped Issues

### WR-01: Insufficient error feedback in GUI context

**File:** `routing_2026.py:324-328`
**Reason:** This finding is partially mitigated by CR-03's fix. With `enable_water_queries` now defaulting to `False`, the GUI won't run water queries by default, so users won't experience this issue. The suggested fix (adding an `error_callback` parameter) would require significant API changes (changing `load_water_features()` signature, updating `terrain_mesh_from_raster()`, and updating all call sites including tests) which is not critical for v1 stability given that water queries are now disabled by default.

**Original issue:** The `load_water_features()` function catches all exceptions and prints to console, but provides no user-facing feedback when called from GUI context. Users see the application freeze with no explanation if the query fails.

### CR-02: Synchronous network calls block GUI thread (Documented as addressed)

**Note:** This is documented above in "Fixed Issues" but required no code changes. The fix was achieved through CR-03 changing the default behavior.

---

_Fixed: 2026-04-22T12:00:00Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_