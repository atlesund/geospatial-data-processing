"""
Example: Phase 07 - Terrain Auto-Mesh Generation

Demonstrates Phase 7 automatic terrain mesh generation:
- F5: Load GeoTIFF terrain file and auto-generate routing mesh
- Automatic mesh generation with 200m spacing (v1 fixed)
- Progress indication during mesh generation (cursor watch → arrow)
- Error handling with warning dialogs on failures
- Hot reload: Re-load terrain to regenerate mesh
- Routing immediately available after mesh generation

Usage:
    python -m examples.example_phase07_terrain_auto_mesh

Controls:
    F5: Load GeoTIFF terrain file (auto-generates routing mesh)
    Shift+F9: Start route selection mode (requires mesh to be loaded)
    Shift+F10: Stop route selection mode
    Left Click: Select start/end points (auto-computes route after 2nd click)
    Middle/Right Drag: Pan the map
    Mouse Wheel: Zoom in/out
    +/- Keys: Zoom in/out

Per D-01: Mesh generation auto-triggers after terrain load.
Per D-02: Fixed 200m mesh spacing for v1 (no UI control).
Per D-03: Cursor shows watch during generation, arrow after.
Per D-04: All errors show warning dialogs.
Per D-05: Network validated non-empty before assignment.
Per D-06: Network replacement on re-load (hot reload support).

Note: Requires a GeoTIFF terrain file (e.g., from Kartverket DTM50).
Norwegian terrain data: https://kartverket.no/download/
"""

import geo_2026 as geo


def main():
    """
    Demonstrate automatic terrain mesh generation (Phase 7).
    """
    print("=" * 60)
    print("Phase 07: Terrain Auto-Mesh Generation Demo")
    print("=" * 60)
    print()

    # Create screen
    screen = geo.Screen(rows=600, columns=800, background='black')

    print("=" * 60)
    print(" Auto-Mesh Generation Workflow")
    print("=" * 60)
    print()

    print(" 1. Load Terrain with Auto-Mesh Generation:")
    print("    F5          -> Load GeoTIFF + auto-generate routing network")
    print()

    print(" 2. Route Selection (Phase 6 - requires mesh):")
    print("    Shift+F9    : Start route selection mode")
    print("    Click 1     : Select start point (red marker)")
    print("    Click 2     : Select end point (blue marker) -> AUTO-COMPUTE")
    print("    Shift+F10   : Stop route selection mode")
    print()

    print(" 3. Route Display:")
    print("    Auto-display: Orange polyline after 2nd click")
    print("    F5          : Export route as GPX (optional)")
    print()

    print(" 4. Map Navigation:")
    print("    Middle/Right Drag : Pan the map")
    print("    Mouse Wheel       : Zoom in/out")
    print("    +/- Keys          : Zoom in/out")
    print()

    print("=" * 60)
    print()
    print("Behavior Notes:")
    print()
    print("  - Mesh generation uses 200m spacing (v1 fixed, not configurable)")
    print("  - Cursor changes to 'watch' during generation (30-60s for DTM50 tiles)")
    print("  - All errors show warning dialogs (no silent failures)")
    print("  - Hot reload: Re-open same .tif file to regenerate mesh")
    print("  - Empty terrain or invalid files show error dialogs")
    print()

    print("=" * 60)
    print(" Ready to start!")
    print()
    print("To begin: Press F5 to load a GeoTIFF terrain file.")
    print(" Sample terrain files available from Kartverket:")
    print(" https://kartverket.no/download/")
    print()
    print("=" * 60)

    # Start main loop
    screen.loop()


if __name__ == '__main__':
    main()