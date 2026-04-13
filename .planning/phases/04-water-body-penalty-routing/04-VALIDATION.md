---
phase: 04
slug: water-body-penalty-routing
status: draft
nyquist_compliant: false
wave_0_complete: false
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
| **Quick run command** | `python -m pytest tests/ -v -k "test_04" --tb=short` |
| **Full suite command** | `python -m pytest tests/ -v` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/ -v -k "test_04" --tb=short`
- **After every plan wave:** Run `python -m pytest tests/ -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 04-01 | 01 | 1 | COMP-01 | — | Water data queried safely without code injection | unit | `python -m pytest tests/test_04_01.py::test_query_water_features -v` | ❌ W0 | ⬜ pending |
| 04-02 | 02 | 1 | COMP-01 | — | Penalty calculations use defined factors only | unit | `python -m pytest tests/test_04_02.py::test_water_penalty_factors -v` | ❌ W0 | ⬜ pending |
| 04-03 | 03 | 2 | COMP-01 | — | Combined cost function bounded and deterministic | unit | `python -m pytest tests/test_04_03.py::test_combined_cost_function -v` | ❌ W0 | ⬜ pending |
| 04-04 | 04 | 3 | COMP-01 | — | Pathfinding terminates and respects all weights | integration | `python -m pytest tests/test_04_04.py::test_water_aware_routing -v` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_04_01.py` — stubs for water data query tests
- [ ] `tests/test_04_02.py` — stubs for penalty factor tests
- [ ] `tests/test_04_03.py` — stubs for combined cost function tests
- [ ] `tests/test_04_04.py` — stubs for integration tests
- [ ] `tests/conftest.py` — shared fixtures for routing network

Existing infrastructure: pytest framework, `tests/world.mqoı` fixture file, Phase 1-3 test patterns
Infra Check: ❌ — Wave 0 must create test stubs for Phase 4

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Route visualization on map showing water-aware paths | COMP-01 | Requires visual inspection of map display with actual water features | 1. Generate route in area with lakes/rivers. 2. Verify visually that route hugs coastlines/bridges. 3. Verify no straight-line crossings of large water bodies. |
| GPX export compatibility on water-avoiding routes | COMP-01 | Requires external GPS device loading verification | 1. Export route GPX for water-heavy area. 2. Load into GPS device or GPX viewer. 3. Verify track follows expected path around water. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending