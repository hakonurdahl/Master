#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 00:03:49 2024

@author: kohlerm2
"""

import xarray as xr
import matplotlib.pyplot as plt
from pyproj import Proj, transform
import numpy as np
import pandas as pd

# Define UTM Zone 33N
utm_proj = Proj(proj='utm', zone=33, datum='WGS84')

# Define WGS84 (geographical coordinates)
wgs84_proj = Proj(proj='longlat', datum='WGS84')

# Trondheim's geographical coordinates
longitude_trondheim = 10.313541927467728
latitude_trondheim = 63.405021176838034

# Convert to UTM Zone 33 (scalar inputs)
x_trondheim, y_trondheim = transform(wgs84_proj, utm_proj, longitude_trondheim, latitude_trondheim)

# Initialize an empty list to store SWE values and time
swe_values = []
time_values = []

# Loop through the years from 2022 to 2024 (adjust the range as needed)
for year in range(2022, 2024):
    opendap_url = f'https://thredds.met.no/thredds/dodsC/senorge/seNorge_snow/swe/swe_{year}.nc'
    
    try:
        # Open the dataset
        ds = xr.open_dataset(opendap_url, chunks=None)
        
        # Access the snow water equivalent variable
        snow_water_equivalent = ds['snow_water_equivalent']
        
        # Extract SWE at Trondheim (nearest point)
        swe_at_point = snow_water_equivalent.sel(y=y_trondheim, x=x_trondheim, method='nearest')
        
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

# Plotting the SWE over time (for all data points)
plt.figure(figsize=(12, 6))
plt.plot(df['time'], df['swe'], marker='.', color='blue', label='SWE')
plt.scatter(max_swe_per_year['time'], max_swe_per_year['swe'], color='red', zorder=5, label='Max SWE')

# Apply a logarithmic fit to the maxima (log years)
years_maxima = max_swe_per_year['time'].dt.year.values.astype(float)
log_years_maxima = np.log(years_maxima)

# Perform a polynomial fit on the logarithmic years
coeffs_log_fit = np.polyfit(log_years_maxima, max_swe_per_year['swe'], 1)
log_trendline = np.polyval(coeffs_log_fit, log_years_maxima)

# Plot the trend line for the log fit
plt.plot(max_swe_per_year['time'], log_trendline, color='green', linestyle='--', label='Log Trend (Max SWE)')

plt.title('Snow Water Equivalent at Trondheim Over Time (Log Fit for Max SWE)')
plt.xlabel('Year')
plt.ylabel('Snow Water Equivalent (mm)')
plt.xticks(rotation=45)

# Format time on x-axis to show only the year
plt.gca().xaxis.set_major_locator(plt.matplotlib.dates.YearLocator())  # Major ticks for each year
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y'))  # Display only the year

# Add legend
plt.legend()

# Save the plot to the Downloads path
output_path = '/Users/kohlerm2/Downloads/swe_trondheim_max_trend_log.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')

# Show the plot
plt.tight_layout()
plt.show()
