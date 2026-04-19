# Phase 3: Steep Terrain Penalty Routing - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-13
**Phase:** 3-steep-terrain-penalty-routing
**Areas discussed:** Slope calculation, steep terrain threshold, penalty function design (updated), weight integration (reconsidered)

---

## Slope Calculation

| Option | Description | Selected |
|--------|-------------|----------|
| Gradient from adjacent pixels | Calculate slope from elevation differences between neighboring cells (3x3 window). Standard approach in terrain analysis. Computes slope per pixel, then averages along mesh edges. | |
| Use raster resolution directly | Simplify: slope = elevation_diff / raster_pixel_spacing. Simpler computation, assumes uniform terrain between pixels. | ✓ |
| You decide | Choose the most appropriate method based on performance vs. accuracy tradeoffs for Norway terrain data. | |

**User's choice:** Use raster resolution directly

**Notes:** Simplified slope calculation using elevation difference between mesh nodes divided by raster pixel spacing.

---

## Steep Terrain Threshold

| Option | Description | Selected |
|--------|-------------|----------|
| 10 degrees | Gentle limit: routes avoid terrain steeper than 10 degrees. More conservative, longer paths but easier hiking. | |
| 15 degrees (recommended) | Balanced choice: 15 degrees is a common steepness threshold for hiking. Reasonable avoiding of unrealistic climbs. | |
| 20 degrees | Aggressive threshold: 20 degrees. Routes may still use moderately steep terrain where beneficial. | ✓ |

**User's choice:** 20 degrees

**Notes:** Aggressive threshold chosen. Allows moderately steep terrain where beneficial while avoiding unrealistic climbs.

---

## Penalty Function Design

### Initial Discussion (Session 1)

| Option | Description | Selected |
|--------|-------------|----------|
| Step function | Below threshold: no penalty. Above threshold: fixed penalty added. Simple, predictable. Routes either avoid steep terrain or not. | ✓ (initial) |
| Linear scaling | Penalty increases linearly with steepness. Smooth transitions, more gradual avoidance. Example: penalty = (slope - threshold) × multiplier. | ✓ (updated) |
| Exponential | Penalty increases exponentially with steepness. Strongly discourages steep climbs. Example: penalty = base × slope^exponent. | |
| You decide | Use the best approach based on realistic hiking behavior research and Norway terrain characteristics. | |

**User's choice (Session 1):** Step function

**User's choice (Session 2):** Linear scaling

**User's clarification (Session 2):** "Make the penalty function a continuous function instead of step function"

**Notes:**

**Session 1:** Simple and predictable—routes either avoid steep terrain or not. Fixed penalty above threshold.

**Session 2:** User requested continuous function to replace step function. Chose linear scaling with penalty_factor = 1.0 for slope ≤ 20°, then linear growth above threshold.

---

### Linear Scaling Parameters (Session 2)

| Option | Description | Selected |
|--------|-------------|----------|
| 0.1 (gradual) | k = 0.1 — penalty_factor grows slowly: 1.0 at 20°, 1.5 at 25°, 2.0 at 30°, 3.0 at 40°. Modest increase, routes may still use moderately steep terrain. | |
| 0.2 (recommended) | k = 0.2 — penalty_factor grows moderately: 1.0 at 20°, 2.0 at 25°, 3.0 at 30°, 5.0 at 40°. Balanced increase that discourages steep sections significantly. | ✓ |
| 0.3 (strong) | k = 0.3 — penalty_factor grows quickly: 1.0 at 20°, 2.5 at 25°, 4.0 at 30°, 7.0 at 40°. Strong avoidance of steep climbs, longer detours expected. | |

**User's choice:** 0.2 (recommended)

**Notes:** Linear scaling with k = 0.2 provides balanced increase:
- 25° slope: penalty_factor = 2.0 (2× harder)
- 35° slope: penalty_factor = 4.0 (4× harder)
- 45° slope: penalty_factor = 6.0 (6× harder)

---

## Weight Integration

### Initial Discussion (Session 1)

| Option | Description | Selected |
|--------|-------------|----------|
| Additive (distance + penalty) | Final weight = distance + terrain_penalty. Simple and intuitive. Penalty adds to the cost of traversing steep terrain. | |
| Multiplicative (distance × factor) | Final weight = distance × penalty_factor. Penalty multiplies the distance. Makes steep terrain proportionally more costly. | |
| Weighted sum with coefficients | Final weight = w1 × distance + w2 × terrain_penalty. Allows tuning relative importance of distance vs. terrain. | |
| You decide | Choose the most appropriate approach based on the selected step function and threshold. | ✓ |

**User's choice (Session 1):** You decide

**Claude's decision (Session 1):** Multiplicative with 5.0 factor

**Claude's rationale (Session 1):** A step function penalty pairs well with multiplicative integration. When terrain is ≤20°, factor = 1.0 (no penalty). When terrain >20°, factor = 5.0 (5x cost). This is more intuitive than additive because factors represent multipliers like "this terrain is 5 times harder to hike," which aligns with realistic hiking behavior.

---

### Reconsideration (Session 2)

**Clarification requested by user:** "When you say multiplicative, does it mean for the whole route or per step?"

**Claude's explanation:** Weight integration applies per edge (per step), not per whole route. Dijkstra sums edge weights along a path, and the path with lowest total sum is chosen. The weight integration decision is about how to compute each individual edge's weight based on terrain steepness.

**User's understanding confirmed:** "Yes, go ahead with the multiplicative then."

**User's choice (Session 2):** Multiplicative

**Notes:**

- **Per edge, not per route**: Each edge's weight = edge_length × penalty_factor
- **Multiplicative pairs well with linear scaling**: penalty_factor represents "times harder to hike"
- **Flat terrain (≤20°)**: weight = distance × 1.0 = distance
- **Steep terrain (>20°)**: weight = distance × (1.0 + 0.2 × (slope - 20°))
- **Example (Session 2)**: 100m steep terrain at 35° → penalty_factor = 4.0 → weight = 400m (4× cost)

---

## Claude's Discretion

**Weight integration (Session 1):** Chose multiplicative with 5.0 factor to pair with initial step function. Factor represents "5 times harder to hike" on steep terrain.

**Weight integration (Session 2):** Multiplicative confirmed as correct choice after user clarification. Pairs well with continuous linear scaling—represents "times harder to hike" which is intuitive.

## Deferred Ideas

None — discussion stayed within phase scope