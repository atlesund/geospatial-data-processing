import geo_2026 as geo

# 1. Callbacks

def create_points(event):
    screen._points.random_points(1000, 50, 50, 750, 550)
    screen._points.add_geometric_fields()

    for point in screen._points.coordinates:
        screen.draw_point(point, colour='yellow')

    print(screen._points)

def select_and_remove_points(event):
    screen._points.select('x < 300 or y > 200')
    print(len(screen._points.selection))
    screen._points.remove()
    print(screen._points)

    screen.delete('point')

    for point in screen._points.coordinates:
        screen.draw_point(point, size=5, colour='violet')

# 2. Screen instance
screen = geo.Screen()

# 3. Bindings
screen.keyboard_bind('C', create_points)
screen.keyboard_bind('R', select_and_remove_points)

# 4. Loop
screen.loop()