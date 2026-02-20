import geo_2026 as geo 

# 1. Callbacks

def run_exercise(event):

    rectangle = [200, 100, 600, 500]
    
    screen._points.random_points(100,0, 0, 800, 600)
    # Adding geometric fields so that we can use select()
    screen._points.add_geometric_fields()
    screen._points.select_by_rectangle(rectangle)

    #print(screen._points.attributes)

    print(screen._points)

# 2. Screen instance

screen = geo.Screen()


# 3. Bindings

screen.keyboard_bind('R', run_exercise)

# 4. Loop

screen.loop()
