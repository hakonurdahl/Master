#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 09:03:35 2024

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

# Filter for Norway
norway = norway[norway['ADMIN'] == "Norway"]



### Zoomed Map (40km around Trondheim) ###
fig2, ax2 = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.UTM(33)})

# Add features to the zoomed map
ax2.add_feature(cfeature.LAND)
ax2.add_feature(cfeature.OCEAN)
ax2.add_feature(cfeature.BORDERS, linestyle=':')
ax2.add_feature(cfeature.COASTLINE)
ax2.add_feature(cfeature.LAKES)
ax2.add_feature(cfeature.RIVERS)

# Plot Norway boundary in the zoomed map (for context)
norway.boundary.plot(ax=ax2, color='blue', linewidth=1)
norway.plot(ax=ax2, color='lightgreen')

# Define zoom level (limit to avoid large sizes)
zoom_distance = 20000  # 20 km in each direction (total 20 km)
# Calculate new bounding box around Trondheim
x_min = x_trondheim - zoom_distance
x_max = x_trondheim + zoom_distance
y_min = y_trondheim - zoom_distance
y_max = y_trondheim + zoom_distance

# Set the extent for zooming around Trondheim
ax2.set_extent([x_min, x_max, y_min, y_max], crs=ccrs.UTM(33))

# Set gridlines for the zoomed map
ax2.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)

# Mark Trondheim in the zoomed map
ax2.plot(x_trondheim, y_trondheim, marker='o', color='red', markersize=10, label='Trondheim')
ax2.text(x_trondheim, y_trondheim, '  Trondheim', fontsize=12, verticalalignment='bottom')

# Set aspect ratio to be equal for the zoomed map
ax2.set_aspect('equal')

# Set title for the zoomed map
ax2.set_title('Zoomed Map of Trondheim (40 km radius)')
ax2.legend()

# Adjust layout for better spacing
plt.tight_layout()

# Save the zoomed map
output_path_zoomed = '/Users/kohlerm2/Downloads/norway_map_zoomed_trondheim.png'
plt.savefig(output_path_zoomed, dpi=300, bbox_inches='tight')
plt.close(fig2)  # Close the figure to free memory
