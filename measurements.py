import xarray as xr
import matplotlib.pyplot as plt
from pyproj import Transformer
import numpy as np
import pandas as pd
from municipalities import municipalities_data

# Based on datasets for the relevant years, this file returns the max SWE values for each year for a municipality
def measurements(name, ds):
    # Define UTM Zone 33N
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:32633", always_xy=True)

    # Geographical coordinates
    longitude = municipalities_data[name]['coordinates']['longitude']
    latitude = municipalities_data[name]['coordinates']['latitude']

    # Convert to UTM Zone 33 (scalar inputs)
    x_, y_ = transformer.transform(longitude, latitude)

    # Initialize an empty list to store SWE values and time
    swe_values = []
    time_values = []
    for dataset in ds:

        # Open the dataset

        # Access the snow water equivalent variable
        snow_water_equivalent = dataset['snow_water_equivalent']
        
        # Extract SWE  (nearest point)
        swe_at_point = snow_water_equivalent.sel(y=y_, x=x_, method='nearest')
        
        # Store the SWE value and corresponding time
        swe_values.append(swe_at_point.values)
        check_=swe_values[0][0]
        
        # If the coordinates falls within ocean or lakes all values will be NaN
        
        # Check if the first value is NaN
        if np.isnan(check_):  
            print(f"Stopping early for {name}: First value is NaN")
            return np.array([np.nan])  # Return NaN immediately
        
        time_values.append(swe_at_point['time'].values)


    # Flatten the lists of values
    
    swe_values = np.concatenate(swe_values)
    
    time_values = np.concatenate(time_values)

    # Convert time values to pandas datetime objects
    time_values = pd.to_datetime(time_values)

    # Create a DataFrame to organize the data
    df = pd.DataFrame({'time': time_values, 'swe': swe_values})
    df['year'] = df['time'].dt.year

    

    # Find the maximum SWE for each year without grouping columns (silences warning)
    max_swe_per_year = df.groupby('year', as_index=False).apply(
        lambda x: x.loc[x['swe'].idxmax()], include_groups=False
    )


    return max_swe_per_year['swe'].values

# Test



#ds_=[]
#for year in range(2020,2024):
#        opendap_url = f'https://thredds.met.no/thredds/dodsC/senorge/seNorge_snow/swe/swe_{year}.nc'
#        
#        try:
#            # Open the dataset
#            ds_.append(xr.open_dataset(opendap_url, chunks=None))
#            
#
#        except Exception as e:
#            print(f"Could not process: {e}")


#swe = measurements('Aremark', ds_)
#print(swe)
