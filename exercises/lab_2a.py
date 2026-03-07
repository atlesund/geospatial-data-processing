import geo_2026 as geo
# EPSG = 25830

# 1. Callbacks

def delete_points(event):
    screen._digits.add_geometric_fields()
    screen._digits.select("x == x")
    screen._digits.remove()
    screen.delete('point')


# 2. Screen instance

screen = geo.Screen()


# 3. Key bindings

screen.keyboard_bind('D', delete_points)


# 4. Loop
screen.loop()