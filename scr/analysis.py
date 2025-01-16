import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm

# Load the data
data = pd.read_csv('/Users/kohlerm2/Documents/SnowAnalysis/Output/Computations/swe_Trondheim_2_Lianvegen.csv')

# Convert 'time' column to datetime
data['time'] = pd.to_datetime(data['time'])

# Define water year from July to June
data['water_year'] = data['time'].apply(lambda x: x.year + 1 if x.month >= 7 else x.year)

# Filter out data beyond June 30, 2023 to get complete years
data = data[data['time'] <= '2023-06-30']

# Find the maximum SWE for each water year
max_swe_per_year = data.groupby('water_year', as_index=False).apply(lambda x: x.loc[x['swe'].idxmax()]).reset_index(drop=True)

# Exclude incomplete years (e.g., if the first year doesn't start in July)
first_year = data['water_year'].min()
if data[data['water_year'] == first_year]['time'].min().month > 7:
    max_swe_per_year = max_swe_per_year[max_swe_per_year['water_year'] != first_year]

# Compute percentiles of the maximum SWE values
swe_values = max_swe_per_year['swe'].values
percentiles = np.arange(1, len(swe_values)+1) / (len(swe_values)+1) * 100

# Sort the SWE maxima and corresponding water years
sorted_indices = np.argsort(swe_values)
sorted_swe_values = swe_values[sorted_indices]
sorted_water_years = max_swe_per_year['water_year'].values[sorted_indices]

# Ensure arrays are NumPy arrays of float type
sorted_swe_values = np.array(sorted_swe_values, dtype=float)
percentiles = np.array(percentiles, dtype=float)
years = np.array(sorted_water_years, dtype=float)

# Check for NaN or infinite values
assert not np.isnan(sorted_swe_values).any(), "NaN values in sorted_swe_values"
assert not np.isnan(percentiles).any(), "NaN values in percentiles"
assert not np.isnan(years).any(), "NaN values in years"

assert np.isfinite(sorted_swe_values).all(), "Infinite values in sorted_swe_values"
assert np.isfinite(percentiles).all(), "Infinite values in percentiles"
assert np.isfinite(years).all(), "Infinite values in years"

# Create a normalization instance
norm = plt.Normalize(years.min(), years.max())

# Plot the percentile scatter plot with norm
plt.figure(figsize=(10, 6))
scatter = plt.scatter(
    sorted_swe_values,
    percentiles,
    c=years,
    cmap='cool',
    norm=norm
)

# Add colorbar with year labels
cbar = plt.colorbar(scatter, ticks=np.linspace(years.min(), years.max(), num=5).astype(int))
cbar.ax.set_ylabel('Water Year')
cbar.ax.set_yticklabels([str(int(year)) for year in np.linspace(years.min(), years.max(), num=5).astype(int)])

plt.xlabel('Maximum SWE (mm)')
plt.ylabel('Percentile (%)')
plt.title('Percentile Plot of Maximum SWE per Water Year\n(Trondheim 2 Lianvegen)')
plt.grid(True)
plt.show()
