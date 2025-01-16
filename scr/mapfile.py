#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 22:57:01 2024

@author: kohlerm2
"""
from pyproj import Proj, transform
import geopandas as gpd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# Define UTM Zone 33N
utm_proj = Proj(proj='utm', zone=33, datum='WGS84')

# Define WGS84 (geographical coordinates)
wgs84_proj = Proj(proj='longlat', datum='WGS84')

# Trondheim's geographical coordinates
longitude_trondheim = 10.313541927467728
latitude_trondheim = 63.405021176838034

# Convert Trondheim coordinates to UTM Zone 33
x_trondheim, y_trondheim = transform(wgs84_proj, utm_proj, longitude_trondheim, latitude_trondheim)

# Load the countries shapefile (update this path)
shapefile_path = '/Users/kohlerm2/Downloads/ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp'  # Adjust path
norway = gpd.read_file(shapefile_path)

# Print the columns to check the names
print(norway.columns)  # Check available columns

# Filter for Norway using the correct column name
norway = norway[norway['ADMIN'] == "Norway"]  # Ensure 'ADMIN' is correct

# Create the plot
fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': ccrs.UTM(33)})

# Add features
ax.add_feature(cfeature.LAND)
ax.add_feature(cfeature.OCEAN)
ax.add_feature(cfeature.BORDERS, linestyle=':')
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.LAKES)
ax.add_feature(cfeature.RIVERS)

# Plot Norway
norway.boundary.plot(ax=ax, color='blue', linewidth=1)
norway.plot(ax=ax, color='lightgreen')

# Define zoom level (40 km)
zoom_distance = 20000  # 20 km in each direction (total 40 km)

# Calculate new bounding box around Trondheim
x_min = x_trondheim - zoom_distance
x_max = x_trondheim + zoom_distance
y_min = y_trondheim - zoom_distance
y_max = y_trondheim + zoom_distance

# Set the extent to zoom around Trondheim
ax.set_extent([x_min, x_max, y_min, y_max], crs=ccrs.UTM(33))

# Set gridlines
ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)

# Plot the specific point at (x, y)
x_coord = x_trondheim
y_coord = y_trondheim
ax.plot(x_coord, y_coord, marker='o', color='red', markersize=10, label='Trondheim')

# Add a label for the point
ax.text(x_coord, y_coord, '  Trondheim', fontsize=12, verticalalignment='bottom')

# Set aspect ratio to be equal for better representation
ax.set_aspect('equal')

# Title
plt.title("Map of Mainland Norway Zoomed 40 km Around Trondheim")

# Show the legend
plt.legend()

# Export the figure as PNG to Downloads path
output_path = '/Users/kohlerm2/Downloads/norway_map_trondheim_zoom.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')

# Show the map
plt.show()
