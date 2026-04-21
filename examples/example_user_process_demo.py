"""
Example: Complete User Process Demonstration

Demonstrates the complete end-to-end workflow from user-process.md:
1. Load GeoTIFF terrain data (auto-generates routing network)
2. User selects start/end points via Shift+F9
3. Route automatically computes and displays
4. Export route as GPX (optional)

This example follows the documented user process from:
.planning/user-process.md

Usage:
    python -m examples.example_user_process_demo

Prerequisites:
    A GeoTIFF terrain file from Kartverket (e.g., bergen_50m_33.tif)
    Download from: https://kartverket.no/download/

Workflow:
    1. Press F5 to load your GeoTIFF terrain file
       → Terrain loads and routing mesh auto-generates (Phase 7)
    2. Press Shift+F9 to start route selection mode
    3. Click to select start point (red marker)
    4. Click to select end point (blue marker)
       → Route auto-computes and displays (Phase 6)
    5. Press Shift+F10 to stop route selection mode
    6. Optional: Export route as GPX for GPS navigation

Integration Demo:
    This example demonstrates the complete integration of:
    - Phase 7: Terrain auto-mesh generation on F5 load
    - Phase 6: GUI routing with auto-compute on 2nd click
    - Phase 5: Route visualization and GPX export
    - Phase 3: Steep terrain penalty routing
    - Phase 2: Hybrid routing network construction
    - Phase 1: Map interaction and point selection

Note: Water body penalties (Phase 4) not yet implemented.
"""

import geo_2026 as geo


def main():
    """
    Demonstrate the complete user process workflow.

    This walkthrough follows .planning/user-process.md step-by-step.
    """
    print("=" * 70)
    print(" COMPLETE USER PROCESS DEMONSTRATION")
    print("=" * 70)
    print()
    print("This example demonstrates the full workflow documented in:")
    print("  .planning/user-process.md")
    print()
    print("=" * 70)
    print()

    # Create screen
    screen = geo.Screen(rows=600, columns=800, background='black')

    # ========================================================================
    # USER PROCESS WALKTHROUGH
    # ========================================================================

    print("=" * 70)
    print(" STEP 1-3: LOAD TERRAIN DATA")
    print("=" * 70)
    print()
    print("  Download terrain from Kartverket:")
    print("    • URL: https://kartverket.no/download/")
    print("    • Dataset: Digital Terrain Model (DTM50)")
    print("    • Format: GeoTIFF (.tif)")
    print()
    print("  To load terrain:")
    print("    Press F5 and select your .tif file")
    print()
    print("  System automatically (Phase 7):")
    print("    ✓ Extracts EPSG code from file metadata")
    print("    ✓ Reads bounding box coordinates")
    print("    ✓ Loads elevation data")
    print("    ✓ Generates routing mesh (200m spacing)")
    print("    ✓ Assigns network to screen")
    print()
    print("  Console output will show:")
    print("    WORLD FILE SET (F5): [affine_transform]")
    print("    Generating routing network from terrain...")
    print("    Mesh network created and assigned: X nodes, Y edges")
    print()
    print("=" * 70)
    print()

    print("=" * 70)
    print(" STEP 4: ROUTING NETWORK GENERATED")
    print("=" * 70)
    print()
    print("  After terrain load, routing network is ready:")
    print("    • Grid of mesh nodes (200m spacing)")
    print("    • Edges with terrain-aware weights")
    print("    • Slope penalties for steep terrain (>20°)")
    print("    • Ready for route computation")
    print()
    print("  Note: Phase 7 auto-generates this network!")
    print("        No manual network creation needed.")
    print()
    print("=" * 70)
    print()

    print("=" * 70)
    print(" STEP 5: SELECT ROUTE POINTS")
    print("=" * 70)
    print()
    print("  To start route selection:")
    print("    Press Shift+F9")
    print()
    print("  First click (Start Point):")
    print("    • Red marker appears on screen")
    print("    • Screen coordinates captured")
    print("    • Auto-transformed to UTM coordinates")
    print()
    print("  Second click (End Point):")
    print("    • Blue marker appears on screen")
    print("    • Coordinates captured and transformed")
    print("    → Router auto-triggers (Phase 6)")
    print()
    print("=" * 70)
    print()

    print("=" * 70)
    print(" STEP 6-8: ROUTE COMPUTATION (AUTOMATIC)")
    print("=" * 70)
    print()
    print("  After second click, system automatically:")
    print("    1. Transforms screen → world → network coordinates")
    print("    2. Snaps points to nearest graph nodes")
    print("    3. Computes shortest path using Dijkstra")
    print("    4. Considers terrain penalties (steep slopes)")
    print("    5. Generates route polyline")
    print()
    print("  Console output:")
    print("    Looking for nearest node to: [x, y]")
    print("    Found nearest node: node_X (distance: Ym)")
    print("    Route computed: Z vertices")
    print()
    print("=" * 70)
    print()

    print("=" * 70)
    print(" STEP 9-10: DISPLAY ROUTE")
    print("=" * 70)
    print()
    print("  System automatically (Phase 6):")
    print("    • Transforms route coordinates back to screen space")
    print("    • Draws orange polyline connecting points")
    print("    • Shows route on terrain background")
    print()
    print("  Visual elements:")
    print("    • Red circle: Start point")
    print("    • Blue circle: End point")
    print("    • Orange line: Optimized hiking route")
    print("    • Terrain background: GeoTIFF grayscale")
    print()
    print("=" * 70)
    print()

    print("=" * 70)
    print(" STEP 11: EXPORT GPX (OPTIONAL)")
    print("=" * 70)
    print()
    print("  To export route for GPS navigation:")
    print("    Press F5 (file dialog opens)")
    print()
    print("  GPX file contains:")
    print("    • Track with all route waypoints")
    print("    • WGS84 coordinates (GPS-compatible)")
    print("    • Ready for Garmin, Komoot, etc.")
    print()
    print("=" * 70)
    print()

    # ========================================================================
    # QUICK REFERENCE
    # ========================================================================

    print("=" * 70)
    print(" QUICK REFERENCE GUIDE")
    print("=" * 70)
    print()
    print(" ROUTE PLANNING CONTROLS:")
    print("  F5          : Load terrain file / Export GPX")
    print("  Shift+F9    : Start route selection mode")
    print("  Click 1     : Select start point")
    print("  Click 2     : Select end point (auto-compute)")
    print("  Shift+F10   : Stop route selection mode")
    print()
    print(" MAP NAVIGATION:")
    print("  Middle/Right Drag : Pan the map")
    print("  Mouse Wheel       : Zoom in/out")
    print("  +/- Keys          : Zoom in/out")
    print()
    print("=" * 70)
    print()

    # ========================================================================
    # PHASE INTEGRATION OVERVIEW
    # ========================================================================

    print("=" * 70)
    print(" PHASE INTEGRATION OVERVIEW")
    print("=" * 70)
    print()
    print(" This demo integrates the following phases:")
    print()
    print("  Phase 7 ✅ : Terrain auto-mesh generation")
    print("    • F5 load triggers automatic mesh creation")
    print("    • Fixed 200m spacing for v1")
    print("    • Progress indication (cursor watch → arrow)")
    print("    • Error handling with warning dialogs")
    print()
    print("  Phase 6 ✅ : GUI routing integration")
    print("    • Shift+F9 route selection mode")
    print("    • Auto-compute on 2nd click")
    print("    • Network coordinate transforms")
    print("    • Node snapping to graph")
    print()
    print("  Phase 5 ✅ : Route visualization & export")
    print("    • Orange polyline display")
    print("    • GPX export for GPS devices")
    print()
    print("  Phase 3 ✅ : Steep terrain penalties")
    print("    • >20° slope penalties applied")
    print("    • Realistic hiking paths")
    print()
    print("  Phase 2 ✅ : Routing network construction")
    print("    • Hybrid network (trails + OSM + terrain)")
    print("    • KDTree for efficient node lookups")
    print()
    print("  Phase 1 ✅ : Map interaction")
    print("    • Point selection with visual markers")
    print("    • Map pan and zoom")
    print()
    print("  Phase 4 ⏳ : Water body penalties (deferred)")
    print("    • Lake/river/fjord crossing penalties")
    print("    • Will be added in future update")
    print()
    print("=" * 70)
    print()

    # ========================================================================
    # START EVENT LOOP
    # ========================================================================

    print("=" * 70)
    print(" READY TO START!")
    print("=" * 70)
    print()
    print(" To begin the user process:")
    print("   1. Press F5 to load a GeoTIFF terrain file")
    print("   2. Press Shift+F9 to start route selection")
    print("   3. Click to select start and end points")
    print("   4. Watch route auto-compute and display")
    print("=" * 70)
    print()

    # Start main event loop
    print("Starting event loop...")
    screen.loop()


if __name__ == '__main__':

    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  Norveg Hiking Route Planner - User Process Demo".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    print()

    main()