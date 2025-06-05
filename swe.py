import xarray as xr
import numpy as np
import pandas as pd
from pyproj import Transformer
from A_funcstat import get_values

def measurements(name, ds, scen):
    """ Returns max SWE values for each year for a given municipality. """


    # Define UTM Zone 33N
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:32633", always_xy=True)
    to_latlon = Transformer.from_crs("EPSG:32633", "EPSG:4326", always_xy=True)

    # Get coordinates from stored file
    coordinates = get_values("C:/Users/hakon/SnowAnalysis_HU/stored_data/points.csv", name, "points")
    latitude, longitude = coordinates[0]

    # Convert to UTM
    x_, y_ = transformer.transform(longitude, latitude)

    # Initialize SWE and time lists
    swe_values = []
    time_values = []

    

    for i, dataset in enumerate(ds):
        
        if scen == None:
            snow_water_equivalent = dataset['snow_water_equivalent']
            swe_at_point = snow_water_equivalent.sel(y=y_, x=x_, method='nearest')
        else:
            snow_water_equivalent = dataset[f'snow_water_equivalent__map_{scen}_daily']
            swe_at_point = snow_water_equivalent.sel(Yc=y_, Xc=x_, method='nearest')

        

        
        swe_array = swe_at_point.values

        # Append data
        swe_values.append(swe_array)
        time_values.append(swe_at_point['time'].values)

    # Flatten and process results
    swe_values = np.concatenate(swe_values)
    time_values = pd.to_datetime(np.concatenate(time_values))

    df = pd.DataFrame({'time': time_values, 'swe': swe_values})
    df['year'] = df['time'].dt.year

    o=0
    if o == 1: 
        max_swe_per_year = df.groupby('year', as_index=False).apply(
            lambda x: x.loc[x['swe'].idxmax()], include_groups=False
        )

        return max_swe_per_year['swe'].values

    else:
        grouped = df.groupby('year')

        swe_max_list = []
        for _, group in grouped:
            if group['swe'].isna().all():
                swe_max_list.append(np.nan)
            else:
                max_swe = group.loc[group['swe'].idxmax(), 'swe']
                swe_max_list.append(max_swe)

        return np.array(swe_max_list, dtype='float64')




# Test
run=0
if run==1:
    ds_ = []
    for year in range(2024, 2074):
        
        #opendap_url = f'https://thredds.met.no/thredds/dodsC/senorge/seNorge_snow/swe/swe_{year}.nc'
        opendap_url = f'https://thredds.met.no/thredds/dodsC/KSS/Klima_i_Norge_2100/utgave2015/SWE/MPI_RCA/rcp45/rcp45_MPI_RCA_SWE_daily_{year}_v4.nc'
        try:
            ds_.append(xr.open_dataset(opendap_url, chunks=None))
        except Exception as e:
            print(f"Could not process: {e}")

    list=["Fjord", "Nesna", "Gamvik", "Hammerfest", "Loppa", "Nesseby"]
    for mun in list:
        swe = measurements(mun, ds_, "rcp45")
        print(mun, repr(swe.tolist()))
