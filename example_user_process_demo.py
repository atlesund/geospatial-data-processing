"""
Example: Complete User Process Demonstration

NB! If epsg is missing use 25833 for Norwegian .tif files

Demonstrates the complete end-to-end workflow from user-process.md:
1. Load GeoTIFF terrain data (auto-generates routing network)
2. User selects start/end points via Shift+F9
3. Route automatically computes and displays
4. Export route as GPX (optional)

Usage:
    python -m example_user_process_demo

Prerequisites:
    A GeoTIFF terrain file from Kartverket (.tif)
    Download from: https://kartkatalog.geonorge.no/metadata/dtm-50/e25d0104-0858-4d06-bba8-d154514c11d2

Workflow:
    1. Press F5 to load your GeoTIFF terrain file
       → Terrain loads and routing mesh auto-generates
    2. Press Shift+F9 to start route selection mode
    3. Click to select start point (red marker)
    4. Click to select end point (blue marker)
       → Route auto-computes and displays
    5. Press Shift+F10 to stop route selection mode
    6. Optional: Export route as GPX for GPS navigation

"""

import geo_2026 as geo


def main():
    """
    Demonstrate the complete user process workflow.

    This walkthrough follows .planning/user-process.md step-by-step.
    """
    
    # Create screen
    screen = geo.Screen(rows=600, columns=800, background='black')

    # ========================================================================
    # USER PROCESS WALKTHROUGH
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
    
    print("=" * 70)
    print()

    # =============

    # Start main event loop
    print("Starting event loop...")
    screen.loop()


if __name__ == '__main__':
    main()