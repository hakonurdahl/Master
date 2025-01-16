#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 23:29:39 2024

@author: kohlerm2
"""
from pyproj import Proj, transform
import geopandas as gpd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# Define UTM Zone 33N projection and WGS84
utm_proj = Proj(proj='utm', zone=33, datum='WGS84')
wgs84_proj = Proj(proj='longlat', datum='WGS84')

# Define the geographic bounding box of mainland Norway (WGS84)
min_lon, max_lon = 21, 22  # Longitude extent
min_lat, max_lat = 70, 71  # Latitude extent

# Convert bounding box to UTM Zone 33 coordinates
min_x, min_y = transform(wgs84_proj, utm_proj, min_lon, min_lat)
max_x, max_y = transform(wgs84_proj, utm_proj, max_lon, max_lat)

# Convert Loppa's coordinates to UTM Zone 33
longitude_Loppa = 21.856517535853513
latitude_Loppa = 70.13995711333514

x_Loppa, y_Loppa = transform(wgs84_proj, utm_proj, longitude_Loppa, latitude_Loppa)

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

# Set the extent of the plot using the UTM coordinates
ax.set_extent([min_x, max_x, min_y, max_y], crs=ccrs.UTM(33))

# Mark Loppa with a red dot
ax.plot(x_Loppa, y_Loppa, marker='o', color='red', markersize=10, label='Loppa')

# Add a label for Loppa
ax.text(x_Loppa, y_Loppa, '  Loppa', fontsize=12, verticalalignment='bottom')

# Enforce equal scaling in x and y directions
ax.set_aspect('equal', 'box')

# Set gridlines for reference
ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)

# Set the title of the map
ax.set_title('Map of Mainland Norway with Loppa Marked')

# Add a legend
ax.legend()

# Adjust layout for better spacing
plt.tight_layout()

# Save the map
output_path = '/Users/kohlerm2/Downloads/norway_map_with_Loppa.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')

# Show the plot
plt.show()

# Close the figure
plt.close(fig)
