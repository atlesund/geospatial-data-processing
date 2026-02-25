import geo_2026 as geo

# 1. Callback function

def create_polyline(event):
    polyline = [
        [100,100],
        [600, 200],
        [300, 500]
    ]
    screen.draw_polyline(polyline, vertices=True)

# 2. Screen instance
screen = geo.Screen()

# 3. Bindings
screen.keyboard_bind('1', create_polyline)

# 4. Loop
screen.loop()