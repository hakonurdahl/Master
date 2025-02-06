import numpy as np
import scipy as sp
import pandas as pd
import matplotlib.pyplot as plt
from pyproj import Transformer
import geopandas as gpd
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib import cm  # For colormap
from matplotlib.colors import Normalize  # For normalizing values

### Load Data ###
municipalities_df = pd.read_csv("municipalities_data.csv")

# Extract reliability indices and coordinates
reliability_indices = dict(zip(municipalities_df["Municipality"], municipalities_df["Beta"]))
locations = list(zip(municipalities_df["Municipality"], municipalities_df["Latitude"], municipalities_df["Longitude"]))

# Normalize reliability indices to [0, 1] for the colormap
norm = Normalize(vmin=min(reliability_indices.values()), vmax=max(reliability_indices.values()))
colormap = plt.colormaps["RdYlGn"]  # Red-to-Green colormap

# Assign a color to each location based on reliability index
location_colors = {name: colormap(norm(Bf)) for name, Bf in reliability_indices.items()}

# Define transformer for coordinate conversion
transformer = Transformer.from_crs("EPSG:4326", "EPSG:32633", always_xy=True)

# Convert locations to UTM coordinates
utm_locations = [(name, *transformer.transform(lon, lat)) for name, lat, lon in locations]

# Load the countries shapefile
shapefile_path = '/Users/hakon/SnowAnalysis_JK/DataSources/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp'
norway = gpd.read_file(shapefile_path)

# Filter for Norway
norway = norway[norway["ADMIN"] == "Norway"]

# Create the figure and axes, using UTM projection
fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={"projection": ccrs.UTM(33)})

# Set the extent to show only Norway
ax.set_extent([4.5, 31.0, 57.5, 71.2], crs=ccrs.PlateCarree())

# Add geographical features
ax.add_feature(cfeature.BORDERS, linestyle=":")
ax.add_feature(cfeature.COASTLINE)

# Plot Norway boundary
norway.boundary.plot(ax=ax, color="blue", linewidth=1)

# Plot each location with the reliability index in the label
for name, x, y in utm_locations:
    if name in reliability_indices:
        bf_label = f"{reliability_indices[name]:.2f}" if reliability_indices[name] != 5 else ">5"
        ax.plot(x, y, marker="o", color=location_colors[name], markersize=5, label=f"{name}: $\\beta = {bf_label}$")

# Add a colorbar to represent the reliability indices
sm = plt.cm.ScalarMappable(cmap=colormap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, orientation="vertical", pad=0.05)
cbar.set_label("Reliability Index ($\\beta $)")

# Set the title of the map
ax.set_title("Map of Norway with Locations Colored by Reliability Index")

# Add a legend


# Adjust layout for better spacing
plt.tight_layout()

# Save the map
output_path = "/Users/hakon/SnowAnalysis_JK/Output/Maps/norway_map_colored_by_Bf.png"
plt.savefig(output_path, dpi=300, bbox_inches="tight")

# Show the plot
plt.show()
