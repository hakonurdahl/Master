import xarray as xr
import numpy as np
import pandas as pd
from pyproj import Transformer
from municipalities import municipalities_data

def measurements(name, ds):
    """ Returns max SWE values for each year for a given municipality. """
    
    # Define UTM Zone 33N
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:32633", always_xy=True)

    # Municipality coordinates
    longitude = municipalities_data[name]['coordinates']['longitude']
    latitude = municipalities_data[name]['coordinates']['latitude']

    # Convert coordinates to UTM Zone 33
    x_, y_ = transformer.transform(longitude, latitude)

    # Initialize lists for SWE values and time
    swe_values = []
    time_values = []

    for dataset in ds:
        # Access the SWE variable
        snow_water_equivalent = dataset['snow_water_equivalent__map_rcp45_daily']
        swe_at_point = snow_water_equivalent.sel(Yc=y_, Xc=x_, method='nearest')
        swe_values.append(swe_at_point.values)
        time_values.append(swe_at_point['time'].values)

        if np.isnan(swe_values[0]).all():  # Algorithm to prevent no values if the point falls in a ocean/lake

            # Get all available grid points
            latitudes = dataset['Yc'].values  # (N,)
            longitudes = dataset['Xc'].values  # (M,)

            # Convert to 2D grids
            lon_grid, lat_grid = np.meshgrid(longitudes, latitudes)  # (N, M) each

            # Compute distances from the municipality's location to all grid points
            distances = np.sqrt((lat_grid - y_)**2 + (lon_grid - x_)**2)  # (N, M)

            # Get indices of the 4 closest points
            closest_indices = np.unravel_index(np.argsort(distances, axis=None)[:4], distances.shape)

            # Iterate over the 4 closest points
            for i in range(4):
                y_nearest = lat_grid[closest_indices[0][i], closest_indices[1][i]]
                x_nearest = lon_grid[closest_indices[0][i], closest_indices[1][i]]

                # Extract SWE value at this point
                swe_at_point = snow_water_equivalent.sel(Yc=y_nearest, Xc=x_nearest, method='nearest')

                # Check if SWE contains valid values
                swe_array = swe_at_point.values
                if not np.isnan(swe_array).all():  # If there's at least one non-NaN value, use it
                    swe_values.append(swe_array)
                    time_values.append(swe_at_point['time'].values)
                    break  # Stop searching once a valid value is found

    

    # If all four points are NaN, return NaN
    if len(swe_values) == 0:
        print(f"No valid SWE data found for {name}.")
        return np.array([np.nan])

    # Flatten lists
    swe_values = np.concatenate(swe_values)
    time_values = np.concatenate(time_values)

    # Convert time values to pandas datetime objects
    time_values = pd.to_datetime(time_values)

    # Create DataFrame
    df = pd.DataFrame({'time': time_values, 'swe': swe_values})
    df['year'] = df['time'].dt.year

    # Find max SWE per year
    max_swe_per_year = df.groupby('year', as_index=False).apply(
        lambda x: x.loc[x['swe'].idxmax()], include_groups=False
    )

    return max_swe_per_year['swe'].values

# Test
#ds_ = []
#for year in range(2020, 2024):
#    opendap_url = f'https://thredds.met.no/thredds/dodsC/KSS/Klima_i_Norge_2100/utgave2015/SWE/MPI_RCA/rcp45/rcp45_MPI_RCA_SWE_daily_{year}_v4.nc'
#    try:
#        ds_.append(xr.open_dataset(opendap_url, chunks=None))
#    except Exception as e:
#        print(f"Could not process: {e}")
#

#swe = measurements('Bergen', ds_)
#print(swe)
