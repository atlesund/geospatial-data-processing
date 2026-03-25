import geo_2026 as geo
import itertools

# 1. Callbacks

def read_draw_polylines(event):

    #screen._polylines.read_csv('id', 'x', 'y')
    screen._points.read_csv('id', 'x', 'y')

    print(screen._polylines.coordinates)
    print(screen._polylines.attributes)

    for polyline in screen._polylines.coordinates:
        screen.draw_polyline(polyline)

def compute_intersections(event):
    number_of_polylines = len(screen._polylines.coordinates)

    # Pairs of polylines

    pairs = itertools.combinations(range(number_of_polylines), 2)

    # Compute all intersections

    for pair in pairs:
        segments_1 = geo.utilities.get_segments(screen._polylines.coordinates[pair[0]])
        segments_2 = geo.utilities.get_segments(screen._polylines.coordinates[pair[1]])

        # Intersect all segments with all segments ~ brute force

        count = 0

        for segment_1 in segments_1:
            p_1, p_2 = segment_1

            for segment_2 in segments_2:
                p_3, p_4 = segment_2

                # Compute the intersection

                intersection = geo.utilities.intersect(p_1, p_2, p_3, p_4)

                print(intersection)

                screen.draw_point(intersection[:2])

        


# 2. Screen instance
screen = geo.Screen()
# 3. Bindings

screen.keyboard_bind('1', read_draw_polylines)
screen.keyboard_bind('2', compute_intersections)

# 4. Loop

screen.loop()