#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 28 19:34:24 2024

@author: kohlerm2
"""

import xarray as xr
import numpy as np
from pyproj import Proj, Transformer
import geopandas as gpd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# Define Loppa's coordinates
longitude_Loppa = 21.856517535853513
latitude_Loppa = 70.13995711333514

# Define UTM Zone 33N projection and WGS84
utm_proj = Proj(proj='utm', zone=33, datum='WGS84')
wgs84_proj = Proj(proj='longlat', datum='WGS84')

# Create transformer for coordinate transformation
transformer_to_utm = Transformer.from_proj(wgs84_proj, utm_proj)

# Convert Loppa's coordinates to UTM Zone 33
x_Loppa, y_Loppa = transformer_to_utm.transform(longitude_Loppa, latitude_Loppa)

# Load the SWE dataset
year = 2023  # specify the year
opendap_url = f'https://thredds.met.no/thredds/dodsC/senorge/seNorge_snow/swe/swe_{year}.nc'
ds = xr.open_dataset(opendap_url)

# Extract latitude and longitude arrays from the dataset
latitudes = ds['latitude'].values
longitudes = ds['longitude'].values

# Calculate the distance to Loppa for each point in the SWE dataset
distances = np.sqrt((latitudes - latitude_Loppa)**2 + (longitudes - longitude_Loppa)**2)
min_dist_index = np.unravel_index(np.argmin(distances), distances.shape)

# Get the closest point coordinates
closest_lat = latitudes[min_dist_index]
closest_lon = longitudes[min_dist_index]

# Transform the closest point to UTM Zone 33 coordinates
x_closest, y_closest = transformer_to_utm.transform(closest_lon, closest_lat)

# Load the countries shapefile (adjust path)
shapefile_path = '/Users/kohlerm2/Downloads/ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp'
norway = gpd.read_file(shapefile_path)

# Filter for Norway
norway = norway[norway['ADMIN'] == "Norway"]

# Create the figure and axes, using UTM projection
fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': ccrs.UTM(33)})

# Add land, ocean, borders, and coastline features
ax.add_feature(cfeature.LAND, facecolor='lightgreen')
ax.add_feature(cfeature.OCEAN)
ax.add_feature(cfeature.BORDERS, linestyle=':')
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.LAKES, facecolor='lightblue')
ax.add_feature(cfeature.RIVERS, edgecolor='blue')

# Plot Norway boundary
norway.boundary.plot(ax=ax, color='blue', linewidth=1)

# Set the extent of the plot in geographic coordinates (lon, lat) for a quadratic view
lon_offset, lat_offset = 1.0, 1.0  # to create a centered and quadratic view around Loppa
ax.set_extent([longitude_Loppa - lon_offset, longitude_Loppa + lon_offset, 
               latitude_Loppa - lat_offset, latitude_Loppa + lat_offset], crs=ccrs.PlateCarree())

# Mark Loppa with a red dot
ax.plot(x_Loppa, y_Loppa, marker='o', color='red', markersize=10, label='Loppa', transform=ccrs.UTM(33))

# Mark the closest SWE point with a green dot
ax.plot(x_closest, y_closest, marker='o', color='green', markersize=10, label='Closest SWE Point', transform=ccrs.UTM(33))

# Add labels for Loppa and the closest SWE point
ax.text(x_Loppa, y_Loppa, '  Loppa', fontsize=12, verticalalignment='bottom', transform=ccrs.UTM(33))
ax.text(x_closest, y_closest, '  SWE Closest', fontsize=12, verticalalignment='bottom', transform=ccrs.UTM(33))

# Enforce equal scaling in x and y directions
ax.set_aspect('equal', 'box')

# Set gridlines for reference
gl = ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
gl.top_labels = gl.right_labels = False  # Only show labels on left and bottom

# Set the title of the map
ax.set_title('Map of Mainland Norway with Loppa and Closest SWE Point Marked')

# Add a legend
ax.legend()

# Adjust layout for better spacing
plt.tight_layout()

# Save the map
output_path = '/Users/kohlerm2/Downloads/norway_map_with_Loppa_and_SWE.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')

# Show the plot
plt.show()

# Close the figure
plt.close(fig)

# Close the dataset
ds.close()
