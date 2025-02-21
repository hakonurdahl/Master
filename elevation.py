import requests
import pyproj

def convert_to_utm33(lat, lon):
    """Convert WGS84 (lat, lon) to UTM Zone 33 (EPSG:25833)."""
    wgs84 = pyproj.CRS("EPSG:4326")
    utm33 = pyproj.CRS("EPSG:25833")
    transformer = pyproj.Transformer.from_crs(wgs84, utm33, always_xy=True)
    easting, northing = transformer.transform(lon, lat)
    return easting, northing

def get_elevations(points):
    """Fetch elevation data for a list of (latitude, longitude) tuples."""
    elevations = []

    for lat, lon in points:
        easting, northing = convert_to_utm33(lat, lon)
        url = f"https://ws.geonorge.no/hoydedata/v1/punkt?nord={northing}&ost={easting}&koordsys=25833&geojson=false"

        try:
            response = requests.get(url)
            response.raise_for_status()
            elevation_data = response.json()

            # Extract elevation from response
            if "punkter" in elevation_data and len(elevation_data["punkter"]) > 0:
                elevation = elevation_data["punkter"][0]["z"]
                elevations.append(elevation)
            else:
                elevations.append(None)  # Append None if no elevation data found

        except requests.exceptions.RequestException as e:
            print(f"Error fetching elevation for ({lat}, {lon}): {e}")
            elevations.append(None)

    return elevations

# Example usage
#coordinates = [(59.17994847909977, 11.68597771482694), (59.17994847909977, 11.68997771482694), (59.17994847909977, 11.69397771482694)]

#elevation_results = get_elevations(coordinates)
#print(elevation_results)  # Example Output: [127.0881271362305, 109.1782302856445, 129.9084625244141]
