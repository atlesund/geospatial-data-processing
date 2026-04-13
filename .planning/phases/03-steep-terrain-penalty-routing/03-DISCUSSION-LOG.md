# Phase 3: Steep Terrain Penalty Routing - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-13
**Phase:** 3-steep-terrain-penalty-routing
**Areas discussed:** Slope calculation, steep terrain threshold, penalty function design, weight integration

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

| Option | Description | Selected |
|--------|-------------|----------|
| Step function | Below threshold: no penalty. Above threshold: fixed penalty added. Simple, predictable. Routes either avoid steep terrain or not. | ✓ |
| Linear scaling | Penalty increases linearly with steepness. Smooth transitions, more gradual avoidance. Example: penalty = (slope - threshold) × multiplier. | |
| Exponential | Penalty increases exponentially with steepness. Strongly discourages steep climbs. Example: penalty = base × slope^exponent. | |
| You decide | Use the best approach based on realistic hiking behavior research and Norway terrain characteristics. | |

**User's choice:** Step function

**Notes:** Simple and predictable—routes either avoid steep terrain or not. Fixed penalty above threshold.

---

## Weight Integration

| Option | Description | Selected |
|--------|-------------|----------|
| Additive (distance + penalty) | Final weight = distance + terrain_penalty. Simple and intuitive. Penalty adds to the cost of traversing steep terrain. | |
| Multiplicative (distance × factor) | Final weight = distance × penalty_factor. Penalty multiplies the distance. Makes steep terrain proportionally more costly. | |
| Weighted sum with coefficients | Final weight = w1 × distance + w2 × terrain_penalty. Allows tuning relative importance of distance vs. terrain. | |
| You decide | Choose the most appropriate approach based on the selected step function and threshold. | ✓ |

**User's choice:** You decide

**Claude's decision:** Multiplicative with 5.0 factor

**Claude's rationale:** A step function penalty pairs well with multiplicative integration. When terrain is ≤20°, factor = 1.0 (no penalty). When terrain >20°, factor = 5.0 (5x cost). This is more intuitive than additive because factors represent multipliers like "this terrain is 5 times harder to hike," which aligns with realistic hiking behavior. Additive would require defining arbitrary penalty values in distance units.

---

## Claude's Discretion

- Weight integration: Chose multiplicative with 5.0 factor to pair with the step function penalty. Factor represents "5 times harder to hike" on steep terrain, which aligns with realistic hiking behavior more intuitively than additive penalties.

## Deferred Ideas

None — discussion stayed within phase scope