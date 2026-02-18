import geo_2026 as geo

# 1. Callback function

def print_digit_coordinates(event):
    print(screen._digits.coordinates)

# 2. Screen instance

screen = geo.Screen()

# 3. Bindings

screen.keyboard_bind('1', print_digit_coordinates)

# 4. Loop

screen.loop()