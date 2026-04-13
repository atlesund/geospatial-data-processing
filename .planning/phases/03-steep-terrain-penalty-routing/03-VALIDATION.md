---
phase: 3
slug: steep-terrain-penalty-routing
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-13
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.3 |
| **Config file** | pytest.ini with `pythonpath = .` |
| **Quick run command** | `python3 -m pytest tests/test_terrain_penalties.py -x -v` |
| **Full suite command** | `python3 -m pytest tests/ -v` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python3 -m pytest tests/test_terrain_penalties.py -x`
- **After every plan wave:** Run `python3 -m pytest tests/ -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | COMP-02 | T-3-01 | Validate edge_length > 0 before division | unit | `python3 -m pytest tests/test_terrain_penalties.py::test_slope_calculation -x` | ✅ W0 | ⬜ pending |
| 03-01-02 | 01 | 1 | COMP-02 | T-3-02 | Validate elevation values are numeric, reject NaN/infinite | unit | `python3 -m pytest tests/test_terrain_penalties.py::test_penalty_threshold -x` | ✅ W0 | ⬜ pending |
| 03-02-01 | 02 | 1 | COMP-02 | T-3-03 | Clamp penalty_factor to max 100 to prevent DoS | unit | `python3 -m pytest tests/test_terrain_penalties.py::test_linear_scaling -x` | ✅ W0 | ⬜ pending |
| 03-03-01 | 03 | 2 | COMP-02 | — | Multiplicative weight integration (not additive) | unit | `python3 -m pytest tests/test_terrain_penalties.py::test_multiplicative_weight -x` | ✅ W0 | ⬜ pending |
| 03-04-01 | 04 | 2 | COMP-02 | — | Dijkstra routes avoid unrealistic climbs | integration | `python3 -m pytest tests/test_terrain_penalties.py::test_realistic_routing -x` | ✅ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `tests/test_terrain_penalties.py` — stubs for COMP-02 (new test file)
- [x] `tests/conftest.py` — update with marker for Phase 3 terrain penalty tests
- [x] Elevation grid fixture using mock GrayscaleImage class

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| None | — | All phase behaviors have automated verification. | — |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 30s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending