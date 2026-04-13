"""
Example: Phase 01 Route Selection and Map Navigation

Demonstrates interactive map features from Phase 01:
- Route selection (start/end points via mouse clicks)
- Map navigation (pan via mouse drag, zoom via mouse wheel/keyboard)
- Coordinate display in WGS84 decimal degrees

Usage:
    python -m examples.example_phase01_route_selection

Controls:
    Shift+F9: Start route selection mode
    Shift+F10: Stop route selection mode
    Left click: Select route points (when in route selection mode)
    Middle/Right drag: Pan the map
    Mouse wheel: Zoom in/out
    +/- keys: Zoom in/out
    F5: Load an image (optional - requires image file)
    F6 (Shift+F5): Display loaded image
"""

import geo_2026 as geo


def main():
    """
    Main function demonstrating Phase 01 features.
    """
    print("=" * 60)
    print("Phase 01: Route Selection and Map Navigation Demo")
    print("=" * 60)
    print()
    print("Interactive Map Controls:")
    print("  Shift+F9  : Start route selection mode")
    print("  Shift+F10 : Stop route selection mode")
    print("  Left Click : Select start/end points (in route mode)")
    print("  Middle/Right Drag : Pan the map")
    print("  Mouse Wheel : Zoom in/out")
    print("  +/- Keys : Zoom in/out")
    print()
    print("Optional Image Loading:")
    print("  F5 : Load an image (you'll need a test image file)")
    print("  F6 (Shift+F5) : Display the loaded image")
    print()
    print("=" * 60)
    print()

    # Create a Screen instance with default size (800x600)
    screen = geo.Screen(rows=600, columns=800, background='black')

    print("Screen created. Ready for interaction.")
    print("Press Shift+F9 to start selecting route points.")
    print()

    # Optional: You can load an image and world file if you have test data
    # Uncomment the following line to test with an image:
    # print("Tip: Load a test image with F5, then display it with Shift+F5")
    # print("      This enables coordinate transformation to decimal degrees.")

    # Start the main event loop
    screen.loop()


if __name__ == '__main__':
    main()