import geo_2026 as geo

# 1. Callback function

def mouse_coordinates(event):

    screen.delete('text')

    x = event.x
    y = event.y

    if x < 400:
        colour = 'green'

    else:
        colour = 'red'

    message = f'{x}, {y}'

    screen.draw_text([x,y], message, colour=colour)

# 2. Screen instance
screen = geo.Screen()
# 3. Bindings

screen.mouse_bind('<Motion>', mouse_coordinates)

# 4. Loop
screen.loop()