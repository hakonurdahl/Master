#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 13:05:07 2024

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
min_lon, max_lon = 4.5, 31.0  # Longitude extent
min_lat, max_lat = 57.5, 71.2  # Latitude extent

# Convert bounding box to UTM Zone 33 coordinates
min_x, min_y = transform(wgs84_proj, utm_proj, min_lon, min_lat)
max_x, max_y = transform(wgs84_proj, utm_proj, max_lon, max_lat)

# Load the countries shapefile (using user's path)

#shapefile_path = '/Users/jochenimac/Downloads/ne_110m_admin_0_countries.shp'
shapefile_path = '/Users/kohlerm2/Documents/SnowAnalysis/DataSources/ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp'
norway = gpd.read_file(shapefile_path)

# Filter for Norway
norway = norway[norway['ADMIN'] == "Norway"]

# Define the locations and names
locations = [
    ("Trondheim 1 (Gløshaugen)", 63.41597611839954, 10.408475429413997, 'red'),
    ("Trondheim 2 (Lianvegen)", 63.405030783022426, 10.313520469174751, 'blue'),
    ("Lysaker (Standard Norge)", 59.91520899674151, 10.638403997785314, 'green'),
    ("Loppa Kommune (Langfjordhamn)", 70.13995711333514, 21.856517535853513, 'orange'),
    ("Lom (Innlandet)", 61.83933422146636, 8.567791464666023, 'purple')
]

# Convert each location to UTM coordinates
utm_locations = [(name, transform(wgs84_proj, utm_proj, lon, lat), color) for name, lat, lon, color in locations]

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

# Mark each location with a different color and label
for name, (x, y), color in utm_locations:
    ax.plot(x, y, marker='o', color=color, markersize=10, label=name)

# Specific handling for Trondheim locations to avoid text overlap
# Add arrows for Trondheim locations
ax.annotate(
    "Trondheim 1 (Gløshaugen)", xy=(utm_locations[0][1][0], utm_locations[0][1][1]), xytext=(utm_locations[0][1][0] + 3000, utm_locations[0][1][1] + 5000),
    fontsize=10, color='red', verticalalignment='bottom'
)

ax.annotate(
    "Trondheim 2 (Lianvegen)", xy=(utm_locations[1][1][0], utm_locations[1][1][1]), xytext=(utm_locations[1][1][0] - 4000, utm_locations[1][1][1] - 4000),
    fontsize=10, color='blue', verticalalignment='top'
)

# For other locations, just text with sufficient distance
for name, (x, y), color in utm_locations[2:]:
    ax.text(x, y, f'  {name}', fontsize=10, verticalalignment='bottom', color=color)

# Enforce equal scaling in x and y directions
ax.set_aspect('equal', 'box')

# Set gridlines for reference
ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)

# Set the title of the map
ax.set_title('Map of Norway with Multiple Locations Marked')

# Add a legend
ax.legend()

# Adjust layout for better spacing
plt.tight_layout()

# Save the map (using user's path)
output_path = '/Users/kohlerm2/Documents/SnowAnalysis/Output/Maps/norway_map_multiple_locations_with_arrows.png'
#output_path = '/Users/jochenimac/Downloads/norway_map_multiple_locations_with_arrows.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')

# Show the plot
plt.show()

# Close the figure
plt.close(fig)
