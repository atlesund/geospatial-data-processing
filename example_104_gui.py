import geo_2026 as geo

# 1. Callback function

def print_number_one(event):
    print('This is number 1')

def print_mouse_coordinates(event):
    x = event.x
    y = event.y

    print(f'{x}, {y}')

# 2. Screen instance

screen = geo.Screen()

# 3. Bindings

screen.keyboard_bind('1', print_number_one)

screen.mouse_bind('<Motion>', print_mouse_coordinates)

# 4. Loop

screen.loop()