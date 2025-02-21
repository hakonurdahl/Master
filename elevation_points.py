
import xarray as xr
import matplotlib.pyplot as plt
from pyproj import Transformer
import numpy as np
import pandas as pd
from municipalities import municipalities_data


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


def samples(name, ds):



    # Geographical coordinates
    longitude = municipalities_data[name]['coordinates']['longitude'] 
    latitude =  municipalities_data[name]['coordinates']['latitude'] 

    

    def closest(lat, lon):# Calculate the distance to  for each point in the SWE dataset
        


        

        latitudes = ds['lat'].values
        longitudes = ds['lon'].values
        distances = np.sqrt((latitudes - lat)**2 + (longitudes - lon)**2)
        min_dist_index = np.unravel_index(np.argmin(distances), distances.shape)

        # Get the closest point coordinates
        closest_lat = latitudes[min_dist_index]
        closest_lon = longitudes[min_dist_index]
        return closest_lat, closest_lon


    #Find a center point that is close to the requested point
    actual_lat, actual_lon = closest(latitude, longitude) 

    coordinate_samples=[]


    run=0   #The algorythm that finds the relevant points takes a lot of time, so to just find the elevation at one point set run to 1
    
    if run==0:
        test_lat=actual_lat-0.01
        for i in range(20):
            
            test_lon = actual_lon - 0.01        

            for k in range(10):
                
                
                lat, lon = closest(test_lat, test_lon)

                if lon==actual_lon and lat==actual_lat:
                    coordinate_samples.append((float(test_lat), float(test_lon)))

                test_lon+=0.002
            
            test_lat+=0.001
    else:
        coordinate_samples.append((float(actual_lat), float(actual_lon)))    
        
        

    return coordinate_samples


#Test

#opendap_url = f'https://thredds.met.no/thredds/dodsC/senorge/seNorge_snow/swe/swe_2024.nc'

#try:
#    # Open the dataset    
#    ds_ = xr.open_dataset(opendap_url, chunks=None)
        

#except Exception as e:
#    print(f"Could not process year 2024: {e}")



#print(samples('Tønsberg', ds_))

