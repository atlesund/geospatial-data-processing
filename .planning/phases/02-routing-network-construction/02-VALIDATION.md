---
phase: 2
slug: routing-network-construction
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-12
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x (Python) |
| **Config file** | `tests/conftest.py` or none — Wave 0 installs |
| **Quick run command** | `pytest tests/ -v -k "test_routing" --tb=short` |
| **Full suite command** | `pytest tests/ -v --tb=short` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_routing_*.py -v --tb=short`
- **After every plan wave:** Run `pytest tests/ -v --tb=short`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 1 | COMP-03 | T-2-01 / — | Input validated, no RCE | unit | `pytest tests/test_routing.py::test_osm_extraction -v` | ❌ W0 | ⬜ pending |
| 02-01-02 | 01 | 1 | COMP-03 | T-2-01 / — | Safe OSM API usage | unit | `pytest tests/test_routing.py::test_highway_filter -v` | ❌ W0 | ⬜ pending |
| 02-02-01 | 02 | 1 | COMP-04 | T-2-02 / — | Graph structure validated | unit | `pytest tests/test_routing.py::test_trail_graph -v` | ❌ W0 | ⬜ pending |
| 02-02-02 | 02 | 1 | COMP-04 | T-2-02 / — | No infinite loops in traversal | unit | `pytest tests/test_routing.py::test_graph_connectivity -v` | ❌ W0 | ⬜ pending |
| 02-03-01 | 03 | 2 | COMP-05 | T-2-03 / — | Terrain calculations bounded | unit | `pytest tests/test_routing.py::test_terrain_mesh -v` | ❌ W0 | ⬜ pending |
| 02-04-01 | 04 | 2 | All | T-2-04 / — | Multi-source data integrity | integration | `pytest tests/test_routing.py::test_complete_network -v` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_routing.py` — stubs for COMP-03, COMP-04, COMP-05
- [ ] `tests/conftest.py` — shared fixtures for mock trail data, OSM responses, terrain rasters
- [ ] `pytest` installation — verify existing or add to requirements

*If none: "Existing infrastructure covers all phase requirements."*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Network visualization (GUI) | COMP-04 | Visual verification requires human judgment | 1. Load trail data, 2. Trigger network visualization, 3. Verify trails appear correctly on map |
| OSM trail density verification | COMP-03 | Qualitative assessment of data quality | 1. Query Norwegian region, 2. Inspect returned trails, 3. Confirm sufficient coverage |

*If none: "All phase behaviors have automated verification."*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending