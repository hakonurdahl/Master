
import xarray as xr
import matplotlib.pyplot as plt
from pyproj import Transformer
import numpy as np
import pandas as pd
from municipalities import municipalities_data
from A_funcstat import closest
import requests



# The measurements from SeNorge is done over a square kilometer, which means the area can have large differences in elevation.
# Snow is very dependent on elevation. There is more snow on higher altitudes. 
# Since the reliaiblity analysis is reliant on a characteristic value for snow load the elevation plays a major role.
# To deal with this, elevation_points.py locates a grid of points that is within this square kilometer.
# The elevation can then be found for each of these points in elevation.py. Then the characteristic load calculation can
# for example use the average value for elevation. The method for finding these points is to first find the center of the square.
# The center of all squares is the point listed in the data set. So when a point is found in this data set it is the center.
# Then a grid of points around the center is generated and if the generated point is closest to the center in question it is 
# appended to the list of coordinates. This list will then contain all the points included in the measurement of snow.
# The function that finds the point closest to a coordinate uses a "brute force" method, because the more efficient "nearest" method 
# gave wrong results. 

# A function that find the coordinates of a place from https://nominatim.openstreetmap.org
def get_coordinates(building_name):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': building_name,
        'format': 'json',
        'limit': 1
    }
    headers = {
        'User-Agent': 'reliability_analysis/1.0 (hakon.urdahl@outlook.com)'  # Nominatim requires identifying info
    }

    response = requests.get(url, params=params, headers=headers)
    data = response.json()

    if data:
        lat = data[0]['lat']
        lon = data[0]['lon']
        return float(lat), float(lon)
    else:
        print("Didn't find coordinates for", building_name)
        return None


def coordinates(name, ds):

    transformer = Transformer.from_crs("EPSG:4326", "EPSG:32633", always_xy=True)
    to_latlon = Transformer.from_crs("EPSG:32633", "EPSG:4326", always_xy=True)

    # Geographical coordinates from keyword
    # The name of the municipality + one of the key words below are meant to represent a part of the
    # municipality that is relatively populated. 

    keywords = [" rådhus", " barneskole", " skule", " kirke", " skole"]
    
    
    # Special-case municipalities with manually specified coordinates
    special_coordinates = {
        "Ål": (60.63024, 8.56121),       
        "Meland": (60.51757, 5.23958),
        "Nesset": (62.77575, 8.06621), 
        "Båtsfjord": (70.63459, 29.71046),  
        "Austrheim": (60.76380, 4.91567),
        "Birkenes": (58.33485,8.23298),
        "Dovre": (61.98560, 9.24943),
        "Gjerstad": (58.88114, 9.01837),
        "Hol": (60.61607,8.30206),
        "Lillestrøm": (59.96151, 11.05753),
        "Røyrvik": (64.88776, 13.55853),
        "Valle": (59.21175, 7.5334),
        "Vang": (61.12518, 8.57213),
        "Vik": (61.08815, 6.58583),
        "Vinje": (59.5689, 7.98935),
        "Norddal": (62.29811193390707, 7.245234119948996),
        "Fjord": (62.29811193390707, 7.245234119948996),
        "Nesna": (66.19917491265197, 13.034484695551873),
        "Gamvik": (71.04147355360465, 27.8681967921552),
        "Hammerfest": (70.6601431489694, 23.697329832073535),
        "Loppa": (70.2325140824077, 22.340843599656),
        "Nesseby": (70.16691702484962, 28.55303337930349)
        }

    # Determine coordinates
    if name in special_coordinates:
        data = special_coordinates[name]
    else:
        for keyword in keywords:
            data = get_coordinates(name + keyword)
            if data is not None:
                break


    latitude, longitude = data

   
    x_, y_ = transformer.transform(longitude, latitude)

    #Algorithm to make sure the point contain SWE values
    
    #snow_water_equivalent = ds['snow_water_equivalent']
    snow_water_equivalent = ds['snow_water_equivalent__map_rcp45_daily']

    #latitudes = ds['y'].values
    #longitudes = ds['x'].values
    latitudes = ds['Yc'].values
    longitudes = ds['Xc'].values
    lon_grid, lat_grid = np.meshgrid(longitudes, latitudes)
    distances = np.sqrt((lat_grid - y_)**2 + (lon_grid - x_)**2)
    closest_indices = np.unravel_index(np.argsort(distances, axis=None)[:21], distances.shape)

    for j in range(21):
        y_nearest = lat_grid[closest_indices[0][j], closest_indices[1][j]]
        x_nearest = lon_grid[closest_indices[0][j], closest_indices[1][j]]
        #swe_at_point = snow_water_equivalent.sel(y=y_nearest, x=x_nearest, method='nearest')
        swe_at_point = snow_water_equivalent.sel(Yc=y_nearest, Xc=x_nearest, method='nearest')
        swe_array = swe_at_point.values

        if not np.isnan(swe_array).all():
            actual_lon, actual_lat = to_latlon.transform(x_nearest, y_nearest)      
            #print("j=",j)      
            #print(f"{name} has updated coordinates: lat= {actual_lat}, lon= {actual_lon}")
            break

    coordinate_samples=[]
    coordinate_samples.append((float(actual_lat), float(actual_lon)))

    #Function to retrievy a evenly spread out grip of points within the square kilometer. 
    # Currently not in use.
    grid=0
    if grid ==1:
        coordinate_samples=[]
        test_lat=actual_lat-0.01
        for i in range(20):
            
            test_lon = actual_lon - 0.01        

            for k in range(10):
                
                
                lat, lon = closest(test_lat, test_lon)

                if lon==actual_lon and lat==actual_lat:
                    coordinate_samples.append((float(test_lat), float(test_lon)))

                test_lon+=0.002
            
            test_lat+=0.001


        

    return coordinate_samples


#Test
test_run = 0

if test_run==1:
    #opendap_url = f'https://thredds.met.no/thredds/dodsC/senorge/seNorge_snow/swe/swe_2024.nc'
    opendap_url = f'https://thredds.met.no/thredds/dodsC/KSS/Klima_i_Norge_2100/utgave2015/SWE/MPI_RCA/rcp45/rcp45_MPI_RCA_SWE_daily_2025_v4.nc'


    try:
        # Open the dataset    
        ds_ = xr.open_dataset(opendap_url, chunks=None)
        

    except Exception as e:
        print(f"Could not process year 2024: {e}")



    test_mun = "Nesseby"

    print(test_mun + ',' + '"' + str(coordinates(test_mun, ds_)) + '"')


