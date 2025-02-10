import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pyproj import Transformer
import geopandas as gpd
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.colors import Normalize

# Load Data
csv_path = "C:/Users/hakon/SnowAnalysis_JK/stored_data/municipalities_data_map.csv"
municipalities_df = pd.read_csv(csv_path)

# Extract reliability indices and coordinates
reliability_indices = municipalities_df.set_index("Municipality")[["Beta"]].to_dict()["Beta"]
locations = municipalities_df[["Municipality", "Latitude", "Longitude"]].values


# Filter out NaN values
reliability_indices = {k: v for k, v in reliability_indices.items() if not np.isnan(v)}
locations = [loc for loc in locations if loc[0] in reliability_indices]


# Normalize reliability indices for colormap
norm = Normalize(vmin=min(reliability_indices.values()), vmax=max(reliability_indices.values()))
colormap = plt.cm.RdYlGn  # Red-to-Green colormap

# Assign colors based on reliability index
location_colors = {name: colormap(norm(beta)) for name, beta in reliability_indices.items()}

# Convert coordinates to UTM
transformer = Transformer.from_crs("EPSG:4326", "EPSG:32633", always_xy=True)
utm_locations = [(name, *transformer.transform(lon, lat)) for name, lat, lon in locations]

# Load Norway shapefile
gdf = gpd.read_file("/Users/hakon/SnowAnalysis_JK/DataSources/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp")
norway = gdf[gdf["ADMIN"] == "Norway"]

# Create figure and axes
fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={"projection": ccrs.UTM(33)})
ax.set_extent([4.5, 31.0, 57.5, 71.2], crs=ccrs.PlateCarree())

# Add map features
ax.add_feature(cfeature.BORDERS, linestyle=":")
ax.add_feature(cfeature.COASTLINE)
norway.boundary.plot(ax=ax, color="blue", linewidth=1)

# Plot municipalities

for name, x, y in utm_locations:
    if name in reliability_indices:  # Double-check to avoid errors
        beta_label = f"{reliability_indices[name]:.2f}" if reliability_indices[name] != 5 else ">5"
        ax.plot(x, y, marker="o", color=location_colors[name], markersize=5, label=f"{name}: $\\beta$ = {beta_label}")


# Add colorbar
sm = plt.cm.ScalarMappable(cmap=colormap, norm=norm)
cbar = plt.colorbar(sm, ax=ax, orientation="vertical", pad=0.05)
cbar.set_label("Reliability Index ($\\beta$)")

# Set title
ax.set_title("Map of Norway with Locations Colored by Reliability Index")

# Save and show plot
output_path = "/Users/hakon/SnowAnalysis_JK/Output/Maps/norway_map_colored_by_Bf.png"
plt.savefig(output_path, dpi=300, bbox_inches="tight")
plt.show()
