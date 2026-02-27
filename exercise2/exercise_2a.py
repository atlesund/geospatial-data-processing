import geo_2026 as geo 

# 1. Callbacks
def run_exercise(event):
    # Constants
    rectangle = [200, 100, 600, 500]
    
    screen._points.random_points(1000, 0, 0, 800, 600)
    # Adding geometric fields so that we can use select()
    screen._points.add_field('colour', 'yellow')
    screen._points.add_geometric_fields()
    screen._points.select_by_rectangle(rectangle)

    print(screen._points.attributes)
    print(screen._points)

    # screen.selection => gives the selection

    screen._points.calculate('colour', '"red"') # calculate does operation on selection (if exists)
    for count, point in enumerate(screen._points.coordinates):
        screen.draw_point(point, colour=screen._points._attributes[count]['colour'], tag='highlight')

# 2. Screen instance
screen = geo.Screen()

# 3. Bindings
screen.keyboard_bind('R', run_exercise)

# 4. Loop
screen.loop()