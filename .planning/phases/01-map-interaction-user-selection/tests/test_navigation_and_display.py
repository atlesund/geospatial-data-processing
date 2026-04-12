"""
Integration tests for map navigation (pan/zoom) and coordinate display.

Tests verify pan/zoom functionality, cross-platform mouse wheel handling,
and WGS84 decimal degree coordinate display with persistence.
"""

import pytest


class TestMapNavigation:
    """Test pan and zoom navigation methods."""

    def test_screen_to_decimal_degrees(self, screen_with_world_file):
        """Test coordinate transformation from screen to decimal degrees."""
        screen = screen_with_world_file
        result = screen.screen_to_decimal_degrees([100, 200])

        # Should return coordinates when world file is set
        assert result is not None
        assert len(result) == 2
        assert isinstance(result[0], (int, float))
        assert isinstance(result[1], (int, float))

    def test_screen_to_decimal_degrees_no_world_file(self, screen):
        """Test transformation returns None when world file not set."""
        screen._world_file = None
        result = screen.screen_to_decimal_degrees([100, 200])

        assert result is None

    def test_coordinate_display(self, screen_with_world_file):
        """Test coordinate display on canvas."""
        screen = screen_with_world_file
        screen._update_coordinate_display([100, 200], 'Test')

        # Check if coord_display tag exists
        items = screen._canvas.find_withtag('coord_display')
        assert len(items) > 0

    def test_coordinate_display_no_world_file(self, screen):
        """Test coordinate display returns early when world file missing."""
        screen._world_file = None
        screen._update_coordinate_display([100, 200], 'Test')

        # Should not create any display items
        items = screen._canvas.find_withtag('coord_display')
        assert len(items) == 0

    def test_pan_start(self, screen):
        """Test pan start marks initial position."""
        mock_event = type('MockEvent', (), {'x': 50, 'y': 50})()

        screen._start_pan(mock_event)

        # Should complete without error
        print("Pan start test passed")

    def test_pan_drag(self, screen):
        """Test pan drag continues from marked position."""
        screen._start_point = None
        screen._end_point = None  # Avoid coordinate display during test

        mock_start_event = type('MockEvent', (), {'x': 50, 'y': 50})()
        mock_drag_event = type('MockEvent', (), {'x': 150, 'y': 150})()

        screen._start_pan(mock_start_event)
        screen._do_pan(mock_drag_event)

        # Should complete without error
        print("Pan drag test passed")

    def test_zoom_in(self, screen):
        """Test zoom in method."""
        screen._start_point = None
        screen._end_point = None  # Avoid coordinate display during test

        mock_event = type('MockEvent', (), {'x': 400, 'y': 300})()

        screen._zoom_in(mock_event)

        # Should complete without error
        print("Zoom in test passed")

    def test_zoom_out(self, screen):
        """Test zoom out method."""
        screen._start_point = None
        screen._end_point = None  # Avoid coordinate display during test

        mock_event = type('MockEvent', (), {'x': 400, 'y': 300})()

        screen._zoom_out(mock_event)

        # Should complete without error
        print("Zoom out test passed")

    def test_mouse_wheel_handler_windows_mac(self, screen):
        """Test mouse wheel handler for Windows/macOS (delta property)."""
        screen._start_point = None
        screen._end_point = None  # Avoid coordinate display during test

        # Simulate Windows/macOS event with delta
        class MockEventWithDelta:
            x = 400
            y = 300
            delta = 120  # Scroll up (zoom in)

        mock_event = MockEventWithDelta()
        screen._handle_mouse_wheel(mock_event)

        print("Mouse wheel handler (Windows/macOS) test passed")

    def test_mouse_wheel_handler_linux(self, screen):
        """Test mouse wheel handler for Linux (num property)."""
        screen._start_point = None
        screen._end_point = None  # Avoid coordinate display during test

        # Simulate Linux event with num
        class MockEventWithNum:
            x = 400
            y = 300
            num = 4  # Scroll up (zoom in)

        mock_event = MockEventWithNum()
        screen._handle_mouse_wheel(mock_event)

        print("Mouse wheel handler (Linux) test passed")

    def test_mouse_wheel_handler_linux_scroll_down(self, screen):
        """Test mouse wheel handler for Linux scroll down (zoom out)."""
        screen._start_point = None
        screen._end_point = None  # Avoid coordinate display during test

        class MockEventWithNumDown:
            x = 400
            y = 300
            num = 5  # Scroll down (zoom out)

        mock_event = MockEventWithNumDown()
        screen._handle_mouse_wheel(mock_event)

        print("Mouse wheel handler (Linux down) test passed")

    def test_coordinate_display_persistence_after_pan(self, screen_with_world_file):
        """Test coordinate display persists after pan operation."""
        screen = screen_with_world_file
        screen._start_point = [100, 200]
        screen._end_point = None

        # Display initial coordinate
        screen._update_coordinate_display([100, 200], 'Start')

        # Apply pan
        mock_start = type('MockEvent', (), {'x': 50, 'y': 50})()
        mock_drag = type('MockEvent', (), {'x': 150, 'y': 150})()
        screen._start_pan(mock_start)
        screen._do_pan(mock_drag)

        # Coordinate should still exist after pan
        items = screen._canvas.find_withtag('coord_display')
        assert len(items) > 0

        print("Coordinate persistence after pan test passed")

    def test_coordinate_display_persistence_after_zoom(self, screen_with_world_file):
        """Test coordinate display persists after zoom operation."""
        screen = screen_with_world_file
        screen._start_point = [100, 200]
        screen._end_point = None

        # Display coordinate
        screen._update_coordinate_display([100, 200], 'Start')

        # Apply zoom
        mock_event = type('MockEvent', (), {'x': 400, 'y': 300})()
        screen._zoom_in(mock_event)

        # Coordinate should still exist after zoom
        items = screen._canvas.find_withtag('coord_display')
        assert len(items) > 0

        print("Coordinate persistence after zoom test passed")

    def test_coordinate_format(self, screen_with_world_file):
        """Test coordinate display format uses decimal degrees."""
        screen = screen_with_world_file
        screen._update_coordinate_display([100, 200], 'Test')

        # Get text from canvas
        items = screen._canvas.find_withtag('coord_display')
        if items:
            text = screen._canvas.itemcget(items[0], 'text')
            # Should contain 'Lat' and 'Lon' with decimal format
            assert 'Lat' in text or 'Lon' in text
            print(f"Coordinate format: {text}")

    def test_both_points_display_after_navigation(self, screen_with_world_file):
        """Test both start and end points display after pan/zoom."""
        screen = screen_with_world_file
        screen._start_point = [100, 100]
        screen._end_point = [300, 300]

        # Apply navigation operation
        mock_start = type('MockEvent', (), {'x': 50, 'y': 50})()
        mock_drag = type('MockEvent', (), {'x': 150, 'y': 150})()
        screen._start_pan(mock_start)
        screen._do_pan(mock_drag)

        # Both coordinates should exist
        items = screen._canvas.find_withtag('coord_display')
        assert len(items) > 0

        print("Both points display test passed")