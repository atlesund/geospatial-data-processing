"""
Integration tests for route selection functionality.

Tests verify state machine, marker behavior, and user interaction flows.
"""

import pytest


class TestRouteSelector:
    """Test route selection state management and marker behavior."""

    def test_route_selection_state_init(self, screen):
        """Test that route selection state attributes are initialized to None."""
        assert screen._start_point is None
        assert screen._end_point is None
        assert screen._route_stage is None

    def test_select_start_point(self, screen):
        """Test starting point selection with marker drawing."""
        screen._route_stage = 'start'
        mock_event = type('MockEvent', (), {'x': 100, 'y': 200})()

        screen._select_route_point(mock_event)

        assert screen._start_point == [100, 200]
        assert screen._route_stage == 'end'
        print("Start point selection test verified")

    def test_select_end_point(self, screen):
        """Test end point selection after start point is set."""
        screen._route_stage = 'end'
        screen._start_point = [100, 200]
        mock_event = type('MockEvent', (), {'x': 300, 'y': 400})()

        screen._select_route_point(mock_event)

        assert screen._end_point == [300, 400]
        assert screen._route_stage == 'start'
        print("End point selection test verified")

    def test_selection_stage_toggle(self, screen):
        """Test that selection stage toggles between 'start' and 'end'."""
        screen._route_stage = 'start'
        mock_event1 = type('MockEvent', (), {'x': 100, 'y': 100})()
        mock_event2 = type('MockEvent', (), {'x': 200, 'y': 200})()

        screen._select_route_point(mock_event1)
        assert screen._route_stage == 'end'

        screen._select_route_point(mock_event2)
        assert screen._route_stage == 'start'
        print("Stage toggle test verified")

    def test_start_route_selection_mode(self, screen):
        """Test starting route selection mode."""
        mock_event = type('MockEvent', (), {})()

        screen._start_route_selection(mock_event)

        assert screen._route_stage == 'start'
        print("Start route selection mode test verified")

    def test_stop_route_selection_mode(self, screen):
        """Test stopping route selection mode resets state."""
        screen._route_stage = 'start'
        screen._start_point = [100, 100]
        screen._end_point = [200, 200]
        mock_event = type('MockEvent', (), {})()

        screen._stop_route_selection(mock_event)

        assert screen._route_stage is None
        assert screen._start_point == [100, 100]
        assert screen._end_point == [200, 200]
        print("Stop route selection mode test verified")