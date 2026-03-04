import geo_2026 as geo

# 1. Callback function

def create_polyline(event):
    polyline = [
        [100,100],
        [600, 200],
        [300, 500]
    ]
    screen.draw_polyline(polyline, vertices=True)

def create_polygon(event):
    outer = [
        [100, 100], [600,100],[600,400], [100,400], [100,100]
    ]

    inner = [
        [200,200],[300,200],[300,300],[200,300],[200,200]
    ]
    polygon = [outer, inner]
    screen.draw_polygon(
        polygon, colour='green', stipple=True,
        boundary=True, vertices=True)


# 2. Screen instance
screen = geo.Screen()
# 3. Bindings
screen.keyboard_bind('1', create_polyline)
screen.keyboard_bind('2', create_polygon)

# 4. Loop
screen.loop()