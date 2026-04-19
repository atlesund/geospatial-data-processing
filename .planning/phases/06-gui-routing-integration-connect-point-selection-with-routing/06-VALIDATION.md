---
phase: 6
slug: gui-routing-integration-connect-point-selection-with-routing
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-16
---

# Phase 6 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x+ |
| **Config file** | No explicit pytest.ini found |
| **Quick run command** | `pytest tests/test_06_gui_routing.py -x -v` |
| **Full suite command** | `pytest tests/ -v` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_06_gui_routing.py -x -v`
- **After every plan wave:** Run `pytest tests/ -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 06-01-01 | 01 | 1 | D-01 (Auto-trigger) | — | Routing starts on end point click | integration | `pytest tests/test_06_gui_routing.py::TestGuiRouting::test_auto_trigger -x -v` | ❌ W0 | ⬜ pending |
| 06-02-01 | 02 | 1 | D-02 (Coordinate mapping) | — | Screen→World→Network transform | unit | `pytest tests/test_06_gui_routing.py::TestCoordinateTransforms::test_screen_to_network -x -v` | ❌ W0 | ⬜ pending |
| 06-02-02 | 02 | 1 | D-03 (Node snapping) | — | find_nearest_node() called | unit | `pytest tests/test_06_gui_routing.py::TestNodeSnapping::test_snap_to_existing_node -x -v` | ❌ W0 | ⬜ pending |
| 06-03-01 | 03 | 1 | Path computation | — | shortest_path() returns valid path | integration | `pytest tests/test_06_gui_routing.py::TestPathComputation::test_shortest_path_after_snapping -x -v` | ❌ W0 | ⬜ pending |
| 06-04-01 | 04 | 1 | Route display | — | draw_polyline() called with route | integration | `pytest tests/test_06_gui_routing.py::TestRouteDisplay::test_route_polyline_rendered -x -v` | ❌ W0 | ⬜ pending |
| 06-05-01 | 05 | 1 | D-04 (Error handling) | — | utilities.warning() on all errors | unit | `pytest tests/test_06_gui_routing.py::TestErrorHandling::test_no_network_warning -x -v` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_06_gui_routing.py` — Integration test suite for GUI routing (auto-trigger, transforms, snapping, path computation, display, errors)
- [ ] `tests/conftest.py` — Shared pytest fixtures (routing network, screen with world file, sample coordinates)
- [ ] Test fixtures for mocking tkinter events (mouse clicks, key presses)
- [ ] Test fixtures for synthetic routing networks (small: 10 nodes, medium: 100 nodes)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| User experience with route auto-trigger | D-01 | GUI interaction requires visual confirmation | 1. Run example_phase06_gui_routing.py<br>2. Press Shift+F9<br>3. Click two points<br>4. Verify route appears immediately<br>5. Verify orange polyline is visible |
| Error dialog visibility | D-04 | Modal dialogs require user interaction | 1. Run example without loading routing network<br>2. Attempt route selection<br>3. Verify warning dialog appears and blocks UI |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending 2026-04-16