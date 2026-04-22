import json
import math
from pyproj import CRS, Transformer


def read_geojson(filepath):
    """Read a GeoJSON file and return the features."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data['features']


def calculate_rms_utm(control_points, field_points):
    """
    Calculate RMS error in UTM coordinates.

    RMS = sqrt(sum((x_field - x_control)^2 + (y_field - y_control)^2) / n)
    """
    # Set up transformer from WGS84 (EPSG:4326) to UTM zone 30N (EPSG:32630)
    crs_wgs84 = CRS.from_epsg(4326)
    crs_utm = CRS.from_epsg(32630)
    transformer = Transformer.from_crs(crs_wgs84, crs_utm)

    # Create dictionary of control points keyed by ID for quick lookup
    control_dict = {
        f['id']: f for f in control_points
    }

    # Store squared differences for RMS calculation
    squared_distance_sum = 0
    matches = []

    # Match field points to control points by ID
    for field_point in field_points:
        point_id = field_point['id']
        control_point = control_dict.get(point_id)

        if control_point:
            # Transform field point from lat/lon to UTM
            field_lon, field_lat = field_point['geometry']['coordinates']
            x_field, y_field = transformer.transform(field_lat, field_lon)

            # Get control point UTM coordinates
            x_control = control_point['properties']['x_utm']
            y_control = control_point['properties']['y_utm']

            # Calculate squared distance
            dx = x_field - x_control
            dy = y_field - y_control
            squared_distance = dx**2 + dy**2
            squared_distance_sum += squared_distance

            matches.append({
                'id': point_id,
                'x_field': x_field,
                'y_field': y_field,
                'x_control': x_control,
                'y_control': y_control
            })
        else:
            print(f"Warning: No matching control point found for ID {point_id}")

    # Calculate RMS error
    n = len(matches)
    if n == 0:
        return None, matches

    rmse = math.sqrt(squared_distance_sum / n)

    return rmse, matches


def main():
    # File paths 
    control_file = 'data/geojson/control_points.geojson'
    field_file = 'data/geojson/field_data.geojson'

    # Read data
    control_points = read_geojson(control_file)
    field_points = read_geojson(field_file)

    # Calculate RMS error in UTM
    rmse, matches = calculate_rms_utm(control_points, field_points)

    if rmse is None:
        print("No matching points found!")
        return

    # Print point-by-point data
    print(f"{'PID':>5} {'X(FIELD)':>15} {'Y(FIELD)':>15} {'X(CONTROL)':>15} {'Y(CONTROL)':>15}")
    print("-" * 70)

    for m in matches:
        print(f"{m['id']:>5} {m['x_field']:>15.6f} {m['y_field']:>15.6f} {m['x_control']:>15.6f} {m['y_control']:>15.6f}")

    # Print RMSE
    print()
    print(f"RMSE: {rmse:.6f}")


if __name__ == '__main__':
    main()