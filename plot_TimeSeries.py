import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import glob
from datetime import datetime
import scipy.stats as stats

# Define the input and output directories
input_folder = '/Users/hakon/SnowAnalysis_JK/Output/Computations/'
output_folder = '/Users/hakon/SnowAnalysis_JK/Output/ForMaster/'

# Ensure the output directory exists
os.makedirs(output_folder, exist_ok=True)

# Get a list of all CSV files in the input folder
csv_files = glob.glob(os.path.join(input_folder, '*.csv'))
print(csv_files)
# Define the fixed SWE scale (adjust as needed)
fixed_swe_scale = [0, 2000]  # SWE in mm

csv_file='/Users/hakon/SnowAnalysis_JK/Output/Computations\\swe_Trondheim_1_Gloshaugen.csv'
# Load the data
data = pd.read_csv(csv_file)

# Convert 'time' column to datetime
data['time'] = pd.to_datetime(data['time'])

# Define water year from July to June
data['water_year'] = data['time'].apply(lambda x: x.year + 1 if x.month >= 7 else x.year)

# Filter data from July 1, 1958 to June 30, 2023
start_date = pd.to_datetime('1958-07-01')
end_date = pd.to_datetime('2023-06-30')
data = data[(data['time'] >= start_date) & (data['time'] <= end_date)]

# Find the maximum SWE for each water year
max_swe_per_year = data.groupby('water_year', as_index=False).apply(
    lambda x: x.loc[x['swe'].idxmax()]
).reset_index(drop=True)

loc, scale = stats.gumbel_r.fit(max_swe_per_year['swe'])


gamma = 0.57722



# Extract the station name from the CSV filename
station_name = os.path.splitext(os.path.basename(csv_file))[0]

# Plot time series of SWE with yearly maxima marked
# First figure with fixed SWE scale
plt.figure(figsize=(12, 6))
plt.plot(data['time'], data['swe'], label='Daily SWE', color='skyblue')
plt.scatter(max_swe_per_year['time'], max_swe_per_year['swe'], color='red', label='Yearly Maxima')
plt.xlabel('Date')
plt.ylabel('SWE (mm)')
plt.title(f'SWE Time Series (1958-2023) - {station_name}')
plt.ylim(fixed_swe_scale)
plt.legend()
plt.grid(True)

# Save the figure
output_filename_fixed = os.path.join(output_folder, f'swe_timeseries_fixed_{station_name}.png')
plt.savefig(output_filename_fixed)
plt.close()

# Second figure with tailored SWE scale
plt.figure(figsize=(12, 6))
plt.plot(data['time'], data['swe'], label='Daily SWE', color='skyblue')
plt.scatter(max_swe_per_year['time'], max_swe_per_year['swe'], color='red', label='Yearly Maxima')
plt.xlabel('Date')
plt.ylabel('SWE (mm)')
plt.title(f'SWE Time Series (1958-2023) - Trondheim')
plt.legend()
plt.grid(True)

# Save the figure
output_filename_scaled = os.path.join(output_folder, f'swe_timeseries_scaled_{station_name}.png')
plt.savefig(output_filename_scaled)
plt.close()

# Indicate some trend of the maxima (e.g., linear regression)
# Prepare data for trend analysis
max_swe_per_year = max_swe_per_year.sort_values('time')
years = max_swe_per_year['water_year'].values
swe_maxima = max_swe_per_year['swe'].values

# Perform linear regression on the maxima
from scipy.stats import linregress

slope, intercept, r_value, p_value, std_err = linregress(years, swe_maxima)
trend_line = intercept + slope * years

# Plot the maxima with trend line (fixed SWE scale)
plt.figure(figsize=(12, 6))
plt.scatter(years, swe_maxima, color='red', label='Yearly Maxima')
plt.plot(years, trend_line, color='green', linestyle='--', label='Trend Line')
plt.xlabel('Water Year')
plt.ylabel('Maximum SWE (mm)')
plt.title(f'Yearly Maximum SWE with Trend - {station_name}')
plt.ylim(fixed_swe_scale)
plt.legend()
plt.grid(True)

# Save the figure
output_filename_maxima_fixed = os.path.join(output_folder, f'swe_maxima_fixed_{station_name}.png')
plt.savefig(output_filename_maxima_fixed)
plt.close()

# Plot the maxima with trend line (tailored SWE scale)
plt.figure(figsize=(12, 6))
plt.scatter(years, swe_maxima, color='red', label='Yearly Maxima')
plt.plot(years, trend_line, color='green', linestyle='--', label='Trend Line')
plt.xlabel('Water Year')
plt.ylabel('Maximum SWE (mm)')
plt.title(f'Yearly Maximum SWE with Trend - {station_name}')
plt.legend()
plt.grid(True)

# Save the figure
output_filename_maxima_scaled = os.path.join(output_folder, f'swe_maxima_scaled_{station_name}.png')
plt.savefig(output_filename_maxima_scaled)
plt.close()

# Optionally, print the trend information
print(f"Station: {station_name}")
print(f"Trend slope: {slope:.2f} mm per year")
print(f"p-value: {p_value:.4f}")
print("-" * 40)
