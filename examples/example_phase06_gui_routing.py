"""
Example: Phase 06 GUI Routing Integration

Demonstrates Phase 6 integrated routing features:
- Automated route computation after point selection
- Coordinate transformation (screen → world → network EPSG)
- Node snapping to graph nodes
- Shortest path pathfinding
- Route display with distinctive orange styling

Usage:
    python -m examples.example_phase06_gui_routing

Controls:
    Shift+F9: Start route selection mode
    Shift+F10: Stop route selection mode
    Left Click: Select start/end points (auto-computes route after 2nd click)
    F5: Load an image (optional - requires image file with world file)
    F6 (Shift+F5): Display loaded image

Per D-01: Route auto-triggers after end point selection.
Per D-02: Uses screen → world → network EPSG coordinate mapping.
Per D-03: Snaps to nearest graph nodes via KDTree.
Per D-04: All errors show message dialogs.

Note: This example creates a synthetic routing network.
For real routing, load OSM/terrain data using RoutingNetwork methods.
"""
import geo_2026 as geo
from routing_2026 import RoutingNetwork


def main():
    """
    Demonstrate integrated GUI routing (Phase 6).
    """
    print("=" * 60)
    print("Phase 06: GUI Routing Integration Demo")
    print("=" * 60)
    print()
    print("Creating screen and synthetic routing network...")
    print("(For real routing, load OSM/terrain data)")
    print()

    # 1. Create screen
    screen = geo.Screen(rows=600, columns=800, background='black')

    # 2. Load raster with world file (optional for routing, required for geo-referencing)
    print("Optional: Load test image with F5 for geo-referencing")
    print("  (This example works without image - uses synthetic network)")
    print()

    # 3. Create synthetic routing network
    print("Creating synthetic routing network...")
    network = RoutingNetwork()

    # Add sample nodes (linear chain for simple pathfinding)
    for i in range(10):
        x = 600000.0 + i * 100  # UTM 32V coordinates (southern Norway)
        y = 6650000.0 + i * 50
        node_id = f'n{i}'
        network.add_node(node_id, x, y)

    # Add edges with weights to create a connected graph
    for i in range(9):
        source = f'n{i}'
        target = f'n{i+1}'
        # Bidirectional edges (hiking trails are traversable both ways)
        network.add_edge(source, target, weight=100.0, length=100.0)
        network.add_edge(target, source, weight=100.0, length=100.0)

    # Add some cross connections for more interesting routes
    network.add_edge('n2', 'n5', weight=150.0, length=150.0)
    network.add_edge('n5', 'n2', weight=150.0, length=150.0)
    network.add_edge('n4', 'n7', weight=150.0, length=150.0)
    network.add_edge('n7', 'n4', weight=150.0, length=150.0)

    network.epsg = 32632  # UTM Zone 32V (Norway)

    print(f"Network created: {len(network.graph.nodes)} nodes, "
          f"{len(network.graph.edges)} edges, EPSG: {network.epsg}")
    print()

    # 4. Assign network to screen
    screen.set_route_network(network)
    print("Routing network assigned to screen.")
    print()

    # 5. Set up coordinate system (UTM 32V)
    screen._epsg = 32632

    # 6. Provide load instructions
    print("Optional: Load test image with world file for geo-referencing")
    print("  1. Press F5 to load an image (you'll need a test .png file)")
    print("  2. Press F6/Shift+F5 to display the image")
    print("  3. This enables full coordinate transformations")
    print()
    print("  Note: This example works without image - uses synthetic coordinates")
    print()

    # 7. Instructions
    print("=" * 60)
    print(" Routing Controls")
    print("=" * 60)
    print()
    print(" 1. Routing Workflow:")
    print("    Shift+F9  : Start route selection mode")
    print("    Click 1   : Select start point (red marker)")
    print("    Click 2   : Select end point (blue marker) -> AUTO-COMPUTE")
    print("    Shift+F10 : Stop route selection mode")
    print()
    print(" 2. Route Actions:")
    print("    Auto-display: Route appears in orange after 2nd click")
    print("    F5          : Export route as GPX (works without menu)")
    print()
    print(" 3. Map Navigation:")
    print("    Middle/Right Drag : Pan the map")
    print("    Mouse Wheel       : Zoom in/out")
    print("    +/- Keys          : Zoom in/out")
    print()
    print("=" * 60)
    print()
    print("Ready for route selection!")
    print("Select two points to auto-compute route")
    print("=" * 60)

    # 8. Start main loop
    screen.loop()


if __name__ == '__main__':
    main()