
import xarray as xr
import matplotlib.pyplot as plt
from pyproj import Transformer
import numpy as np
import pandas as pd
from municipalities import municipalities_data
import elevation_points

# Loop through the years from 2022 to 2024 (adjust the range as needed)
def measurements(name):
    # Define UTM Zone 33N
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:32633", always_xy=True)

    # Geographical coordinates
    longitude = municipalities_data[name]['coordinates']['longitude'] 
    latitude =  municipalities_data[name]['coordinates']['latitude']

    # Convert to UTM Zone 33 (scalar inputs)
    x_, y_ = transformer.transform(longitude, latitude)


    # Initialize an empty list to store SWE values and time
    swe_values = []
    time_values = []
    for year in range(2020, 2024):
        
        opendap_url = f'https://thredds.met.no/thredds/dodsC/senorge/seNorge_snow/swe/swe_{year}.nc'
        
        try:
            # Open the dataset
            ds = xr.open_dataset(opendap_url, chunks=None)
            
            # Access the snow water equivalent variable
            snow_water_equivalent = ds['snow_water_equivalent']
            
            # Extract SWE  (nearest point)
            swe_at_point = snow_water_equivalent.sel(y=y_, x=x_, method='nearest')
            
            # Get the actual grid point used
            actual_lon = swe_at_point.lon.values
            actual_lat = swe_at_point.lat.values
            #print(actual_lat)
            #print(actual_lon)

            # Store the SWE value and corresponding time
            swe_values.append(swe_at_point.values)
            time_values.append(swe_at_point['time'].values)  # Collect all time values in the dataset



        except Exception as e:
            print(f"Could not process year {year}: {e}")

    # Flatten the lists of values (in case there are multiple time points per year)
    swe_values = np.concatenate(swe_values)
    time_values = np.concatenate(time_values)

    # Convert time values to pandas datetime objects for better plotting
    time_values = pd.to_datetime(time_values)

    # Create a DataFrame to organize the data
    df = pd.DataFrame({'time': time_values, 'swe': swe_values})
    df['year'] = df['time'].dt.year

    # Find the maximum SWE for each year and store the time and value (include_groups=False to silence the warning)
    max_swe_per_year = df.groupby('year', as_index=False, group_keys=False).apply(lambda x: x.loc[x['swe'].idxmax()])
    return max_swe_per_year

swe=measurements('Aremark')['swe'].values
print(swe)
#print(np.mean(swe))



