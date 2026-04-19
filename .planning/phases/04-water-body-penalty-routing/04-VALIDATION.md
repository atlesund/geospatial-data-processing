---
phase: 04
slug: water-body-penalty-routing
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-13
---

# Phase 04 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | Existing `tests/world.mqolı` (O) — fixture file legacy, no config needed |
| **Quick run command** | `python3 -m pytest tests/ -v -k "test_04" --tb=short` |
| **Alternative marker command** | `python3 -m pytest tests/ -v -m "water"` (after conftest.py updated with water marker) |
| **Full suite command** | `python3 -m pytest tests/ -v` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python3 -m pytest tests/ -v -k "test_04" --tb=short`
- **After every plan wave:** Run `python3 -m pytest tests/ -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 04-01 | 01 | 1 | COMP-01 | T-4-01,T-4-02 | Water data queried safely without code injection | unit | `python3 -m pytest tests/test_04_01_water_query.py::test_load_water_features_bbox_validation -v` | ✅ Plan 01 Task 2 | ⬜ pending |
| 04-02 | 02 | 1 | COMP-01 | T-4-05,T-4-07 | Penalty calculations use defined factors only | unit | `python3 -m pytest tests/test_04_02_water_detection.py::test_lake_crossing_detection -v` | ✅ Plan 02 Task 2 | ⬜ pending |
| 04-03 | 03 | 2 | COMP-01 | T-4-08 | Combined cost function bounded and deterministic | unit | `python3 -m pytest tests/test_04_03_combined_penalty.py::test_combined_penalty_multiplication -v` | ✅ Plan 03 Task 2 | ⬜ pending |
| 04-04 | 04 | 3 | COMP-01 | T-4-10 | Pathfinding terminates and respects all weights | integration | `python3 -m pytest tests/test_04_04_integration.py::test_route_avoids_lake -v` | ✅ Plan 04 Task 1 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `tests/test_04_01_water_query.py` — stubs for water data query tests
- [x] `tests/test_04_02_water_detection.py` — stubs for penalty factor tests
- [x] `tests/test_04_03_combined_penalty.py` — stubs for combined cost function tests
- [x] `tests/test_04_04_integration.py` — stubs for integration tests
- [x] `tests/conftest.py` — shared fixtures for routing network

Existing infrastructure: pytest framework, `tests/world.mqoı` fixture file, Phase 1-3 test patterns
Infra Check: ✅ — Wave 0 stubs created in Plan 01 Task 2

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Route visualization on map showing water-aware paths | COMP-01 | Requires visual inspection of map display with actual water features | 1. Generate route in area with lakes/rivers. 2. Verify visually that route hugs coastlines/bridges. 3. Verify no straight-line crossings of large water bodies. |
| GPX export compatibility on water-avoiding routes | COMP-01 | Requires external GPS device loading verification | 1. Export route GPX for water-heavy area. 2. Load into GPS device or GPX viewer. 3. Verify track follows expected path around water. |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (Plan 01 Task 2 creates stubs and markers)
- [x] No watch-mode flags
- [x] Feedback latency < 10s
- [x] `nyquist_compliant: true` set in frontmatter
- [x] `wave_0_complete: true` set in frontmatter

**Approval:** pending