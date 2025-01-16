#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 28 19:20:31 2024

@author: kohlerm2
"""

from pyproj import Proj, Transformer
import geopandas as gpd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# Define UTM Zone 33N projection and WGS84
utm_proj = Proj(proj='utm', zone=33, datum='WGS84')
wgs84_proj = Proj(proj='longlat', datum='WGS84')

# Create transformer for coordinate transformation
transformer_to_utm = Transformer.from_proj(wgs84_proj, utm_proj)

# Loppa's coordinates in WGS84
longitude_Loppa = 21.856517535853513
latitude_Loppa = 70.13995711333514

# Convert Loppa's coordinates to UTM Zone 33
x_Loppa, y_Loppa = transformer_to_utm.transform(longitude_Loppa, latitude_Loppa)

# Define bounds for a square aspect around Loppa
# Adjusting +/- 0.5° longitude and latitude for a better centered view
lon_offset = 0.5
lat_offset = 0.3

# Calculate geographic bounds around Loppa
min_lon, max_lon = longitude_Loppa - lon_offset, longitude_Loppa + lon_offset
min_lat, max_lat = latitude_Loppa - lat_offset, latitude_Loppa + lat_offset

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
ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())

# Mark Loppa with a red dot
ax.plot(x_Loppa, y_Loppa, marker='o', color='red', markersize=10, label='Loppa', transform=ccrs.UTM(33))

# Add a label for Loppa
ax.text(x_Loppa, y_Loppa, '  Loppa', fontsize=12, verticalalignment='bottom', transform=ccrs.UTM(33))

# Enforce equal scaling in x and y directions
ax.set_aspect('equal', 'box')

# Set gridlines for reference
gl = ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
gl.top_labels = gl.right_labels = False  # Only show labels on left and bottom

# Set the title of the map
ax.set_title('Map of Mainland Norway with Loppa Centered')

# Add a legend
ax.legend()

# Adjust layout for better spacing
plt.tight_layout()

# Save the map
output_path = '/Users/kohlerm2/Downloads/norway_map_with_Loppa_centered.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')

# Show the plot
plt.show()

# Close the figure
plt.close(fig)
