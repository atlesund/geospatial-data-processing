# Requirements: Norwegian Hiking Route Planner

**Defined:** 2026-04-12
**Core Value:** Generate safe, optimal hiking routes between any two points in Norway using terrain and hydrography data, with a simple interface for route planning and export

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Map Interaction

- [ ] **MAP-01**: User can select start point by clicking on interactive map
- [ ] **MAP-02**: User can select end point by clicking on interactive map
- [ ] **MAP-03**: User can pan the map to navigate to different areas
- [ ] **MAP-04**: User can zoom in/out to adjust map scale
- [ ] **MAP-05**: System displays selected coordinates in decimal degrees format

### Route Configuration

(None - v1 uses fixed optimization settings)

### Route Computation

- [ ] **COMP-01**: System applies penalties for water body crossings (lakes, rivers, fjords)
- [ ] **COMP-02**: System applies fixed penalties for steep terrain to ensure realistic hiking routes
- [x] **COMP-03**: System combines established hiking trails into routing network
- [x] **COMP-04**: System incorporates OpenStreetMap paths and trails where available
- [x] **COMP-05**: System uses terrain-based routing where trail network incomplete

### Route Visualization

- [ ] **VIZ-01**: System displays computed route polyline on interactive map with distinct visualization

### Export

- [ ] **EXP-01**: User can export route as GPX file for GPS navigation device use

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Route Configuration

- **CFG-02**: User can specify max acceptable total elevation gain for route
- **CFG-03**: User can enable scenic preference weighting
- **CFG-04**: User can select from route preset profiles (Easy hiker, Fast and flat, Scenic wanderer)

### Route Visualization

- **VIZ-02**: System displays elevation profile chart along route
- **VIZ-03**: System displays route statistics (total distance, elevation gain/loss, estimated time)
- **VIZ-04**: System shows multiple route alternatives with different trade-offs

### Export

- **EXP-02**: User can export route image with map overlay
- **EXP-03**: User can export route in additional formats (KML, GeoJSON)

### Offline Support

- **OFF-01**: User can download terrain data for specific regions
- **OFF-02**: User can download mapping data for specific regions
- **OFF-03**: User can view cached offline data and manage storage
- **OFF-04**: System displays offline mode status indicator
- **OFF-05**: System operates fully offline after initial data download

### Norway-Specific Features

- **NORW-01**: System integrates Kartverket DTM50 terrain data
- **NORW-02**: System accesses GEONORGE geospatial data portal
- **NORW-03**: System incorporates DNT (Norwegian Trekking Association) trails where available
- **NORW-04**: System prioritizes routes near named scenic features
- **NORW-05**: System applies scenic weighting for water proximity (lakes, fjords, rivers)

## Out of Scope

| Feature | Reason |
|---------|--------|
| UTM coordinate display (MAP-06) | v1 uses UTM 32V only, no zone conversion needed |
| User-specified optimization (CFG-01) | v1 uses fixed penalty-based optimization with steep terrain penalties |
| Elevation profile calculation | User deferred to v2, adds complexity |
| Route statistics display | User deferred to v2, not essential for core routing |
| Max elevation constraint | User deferred to v2, intricate UI required |
| Scenic preference weighting | User deferred to v2, complex weight calculation |
| Route alternatives display | User deferred to v2, multi-path algorithm complexity |
| Offline data download/management | User deferred to v2, requires cache management UX |
| User-configurable steep penalty | v1 uses fixed steep terrain penalty |
| Multi-UTM zone handling | v1 limited to UTM 32V (southern Norway) only |
| Real-time weather integration | Out of v1 scope per PROJECT.md, complex dependencies |
| Social features (sharing, reviews) | Out of v1 scope per PROJECT.md, beyond route generation |
| Mobile app | Out of v1 scope per PROJECT.md, desktop-only needed |
| Live GPS tracking | Out of v1 scope per PROJECT.md, route planning tool only |
| Route analytics/history | Out of v1 scope per PROJECT.md, single-use route generation |
| Seasonal routing (winter/snow) | Not in v1 scope, requires snow data and avalanche risk |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| MAP-01 | Phase 1 | Pending |
| MAP-02 | Phase 1 | Pending |
| MAP-03 | Phase 1 | Pending |
| MAP-04 | Phase 1 | Pending |
| MAP-05 | Phase 1 | Pending |
| COMP-01 | Phase 4 | Pending |
| COMP-02 | Phase 3 | Pending |
| COMP-03 | Phase 2 | Complete |
| COMP-04 | Phase 2 | Complete |
| COMP-05 | Phase 2 | Complete |
| VIZ-01 | Phase 5 | Pending |
| EXP-01 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 12 total
- Mapped to phases: 12
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-12*
*Last updated: 2026-04-12 after initial definition*