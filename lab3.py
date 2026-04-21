import geo_2026 as geo

"""
Expected output:

150 300 False
250 300 True
350 300 False
450 300 True
550 300 False
650 300 False
750 300 False
"""

polygon = [
    [
        [200, 100], [200, 400], [300, 500], [600, 500], [600, 400],
        [500, 400], [500, 200], [700, 200], [700, 100], [200, 100]
    ],
    [
        [300, 200], [400, 200], [400, 400], [300, 400], [300, 200]
    ]
]

POINT_TAG = 'pinp_point'
TEXT_TAG = 'pinp_text'
FILL_TAG = 'polygon_fill'
BOUNDARY_TAG = 'polygon_boundary'

polygon_drawn = False


# 1. Callback functions

def help_message(event=None):

    print("\n--- LAB 3: Point In Polygon ---")
    print("This program tests whether a point is inside or outside")
    print("a polygon with one hole.")
    print("")
    print("1 : Draw polygon with hole")
    print("2 : Start point-in-polygon test with mouse motion")
    print("3 : Delete the red/green point and stop drawing")
    print("h : Show this help")
    print("--------------------------------\n")


def draw_polygon(event=None):
    global polygon_drawn

    screen.delete(FILL_TAG)
    screen.delete(BOUNDARY_TAG)

    screen.draw_polygon(polygon, colour='lightgrey', tag=FILL_TAG)

    for part in polygon:
        screen.draw_polyline(part, width=2, colour='white', tag=BOUNDARY_TAG)

    polygon_drawn = True


def draw_point(event):

    point = [event.x, event.y]
    inside = geo.utilities.point_in_polygon(point, polygon)

    if inside:
        colour = 'green'
        location = 'inside'
    else:
        colour = 'red'
        location = 'outside'

    screen.delete(POINT_TAG)
    screen.delete(TEXT_TAG)

    screen.draw_point(point, size=5, colour=colour, tag=POINT_TAG)
    screen.draw_text(
        [170, 20],
        f'Point: {point} -> {location}',
        colour='white',
        tag=TEXT_TAG
    )


def start_point_test(event=None):

    if polygon_drawn is False:
        draw_polygon()

    screen.mouse_bind('<Motion>', draw_point)
    screen.cursor('none')


def stop_point_test(event=None):

    screen.mouse_unbind('<Motion>')
    screen.cursor('')
    screen.delete(POINT_TAG)
    screen.delete(TEXT_TAG)


def run_pinp_test():

    print('Expected output:\n')

    x = 50
    y = 300

    for count in range(7):

        x += 100

        inside = geo.utilities.point_in_polygon([x, y], polygon)

        print(x, y, inside)

    print()


# 2. Screen instance

screen = geo.Screen()

run_pinp_test()


# 3. Bindings

screen.keyboard_bind('1', draw_polygon)
screen.keyboard_bind('2', start_point_test)
screen.keyboard_bind('3', stop_point_test)
screen.keyboard_bind('h', help_message)

print("Press 'h' for help")
print("Press '1' to draw the polygon")
print("Press '2' to test the point with the mouse")
print("Press '3' to stop and delete the point")


# 4. Loop

screen.loop()

