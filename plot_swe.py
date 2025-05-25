import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from scipy.stats import gumbel_r, linregress
from matplotlib import rcParams

# LaTeX font settings
rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],
    "axes.formatter.use_mathtext": True,
    "text.latex.preamble": r"\usepackage{lmodern}",
})

fontsize_ = 22

# Define paths
csv_file = '/Users/hakon/SnowAnalysis_HU/stored_data/swe_Gloshaugen.csv'
output_folder = '/Users/hakon/SnowAnalysis_HU/Figures/main_output/'
station_name = os.path.splitext(os.path.basename(csv_file))[0]

# Load data
data = pd.read_csv(csv_file)
data['time'] = pd.to_datetime(data['time'])
data['water_year'] = data['time'].apply(lambda x: x.year + 1 if x.month >= 7 else x.year)
data = data[(data['time'] >= '1958-07-01') & (data['time'] <= '2023-06-30')]

# Annual maxima
max_swe_per_year = data.loc[data.groupby('water_year')['swe'].idxmax()].reset_index(drop=True)

# Remove first water year if not starting in July
first_year = data['water_year'].min()
if data[data['water_year'] == first_year]['time'].min().month > 7:
    max_swe_per_year = max_swe_per_year[max_swe_per_year['water_year'] != first_year]

# --- PLOT 1: Percentile plot with Gumbel fit ---

swe_values = max_swe_per_year['swe'].values
n = len(swe_values)
percentiles = np.arange(1, n + 1) / (n + 1) * 100

sorted_indices = np.argsort(swe_values)
sorted_swe_values = swe_values[sorted_indices]

loc, scale = gumbel_r.fit(swe_values)
x_fit = np.linspace(0, sorted_swe_values.max(), 500)
cdf_gumbel = gumbel_r.cdf(x_fit, loc=loc, scale=scale) * 100

plt.figure(figsize=(10, 6))
plt.scatter(sorted_swe_values, percentiles, color='blue', label='Empirical Data')
plt.plot(x_fit, cdf_gumbel, color='black', linestyle='--', label='Gumbel Fit (MLE)')

plt.xlabel('Maximum SWE (mm)', fontsize=fontsize_-3)
plt.ylabel(r'Percentile (\%)', fontsize=fontsize_-3)
plt.title(r'Percentile Plot of Maximum SWE per Water Year\\with Gumbel Fit in Trondheim, Gløshaugen',
          fontsize=fontsize_)
plt.xticks(fontsize=fontsize_-4)
plt.yticks(fontsize=fontsize_-4)
plt.legend(fontsize=fontsize_-3)
plt.grid(True)
plt.tight_layout()

output_filename_percentile = os.path.join(output_folder, 'swe_maxima.png')
plt.savefig(output_filename_percentile, dpi=300)
#plt.show()

# --- PLOT 2: SWE Time Series (Scaled) ---

plt.figure(figsize=(12, 6))
plt.plot(data['time'], data['swe'], label='Daily SWE', color='skyblue')
plt.scatter(max_swe_per_year['time'], max_swe_per_year['swe'], color='red', label='Yearly Maxima')

plt.xlabel('Date', fontsize=fontsize_-3)
plt.ylabel('SWE (mm)', fontsize=fontsize_-3)
plt.title(r'SWE Time Series (1958--2023) -- Trondheim, Gl\o shaugen', fontsize=fontsize_)
plt.xticks(fontsize=fontsize_-4)
plt.yticks(fontsize=fontsize_-4)
plt.legend(fontsize=fontsize_-3)
plt.grid(True)
plt.tight_layout()

output_filename_scaled = os.path.join(output_folder, f'swe_timeseries.png')
plt.savefig(output_filename_scaled, dpi=300)
#plt.show()
