import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import csv
import os
from pyproj import Transformer
from matplotlib.colors import Normalize
import matplotlib.patches as mpatches  # Import for custom legend patches




# File paths
csv_path = f"C:/Users/hakon/SnowAnalysis_JK/stored_data/map_{type}.csv"
geojson_path = "C:/Users/hakon/SnowAnalysis_JK/DataSources/Basisdata_0000_Norge_25833_Kommuner_GeoJSON/Basisdata_0000_Norge_25833_Kommuner_GeoJSON.geojson"
output_map_path = f"C:/Users/hakon/SnowAnalysis_JK/Output/Maps/map_{type}_{var}.pdf"

# Load municipality data from CSV
municipality_list = []
with open(csv_path, mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        municipality_list.append((row["Municipality"], float(row["Latitude"]), float(row["Longitude"]),  float(row["Char"])))

df = pd.DataFrame(municipality_list, columns=["Municipality", "Latitude", "Longitude",  "Char"])

# Convert coordinates to UTM Zone 33 (EPSG:32633)
transformer = Transformer.from_crs("EPSG:4326", "EPSG:32633", always_xy=True)
df["Easting"], df["Northing"] = zip(*df.apply(lambda row: transformer.transform(row["Longitude"], row["Latitude"]), axis=1))

# Load the GeoJSON file (only Kommune layer)
gdf_kommune = gpd.read_file(geojson_path, layer="Kommune")

# Ensure correct CRS
if gdf_kommune.crs is None:
    gdf_kommune.set_crs(epsg=25833, inplace=True)
elif gdf_kommune.crs.to_epsg() != 25833:
    gdf_kommune.to_crs(epsg=25833, inplace=True)

# Find municipalities with the lowest and highest Beta
min_beta_row = df.loc[df[f"{var}"].idxmin()]
max_beta_row = df.loc[df[f"{var}"].idxmax()]

# Define key municipalities to highlight
highlight_municipalities = ["Oslo", "Bergen", "Trondheim - Tråante"]
highlight_rows = df[df["Municipality"].isin(highlight_municipalities)]

# Normalize Beta values for colormap

min_beta = df[f"{var}"].min()
max_beta = df[f"{var}"].max()

#norm = Normalize(vmin=2, vmax=6)                   
#norm = Normalize(vmin=min_beta, vmax=max_beta)
norm = Normalize(vmin=-5, vmax=5)        

colormap = plt.cm.RdYlGn  # Red-to-Green colormap
df["Color"] = df[f"{var}"].apply(lambda beta: colormap(norm(beta)))

# Find which municipality each point belongs to
df["Geometry"] = df.apply(lambda row: gpd.points_from_xy([row["Easting"]], [row["Northing"]])[0], axis=1)
df["Municipality_GDF"] = df.apply(lambda row: gdf_kommune[gdf_kommune.intersects(row["Geometry"])], axis=1)

# Plot the GeoJSON data
fig, ax = plt.subplots(figsize=(12, 8))
gdf_kommune.plot(ax=ax, color='white', edgecolor=None, linewidth=0.0)  

# Color the selected municipalities
for _, row in df.iterrows():
    if not row["Municipality_GDF"].empty:
        row["Municipality_GDF"].plot(ax=ax, color=row["Color"], edgecolor=None, linewidth=0.0)

# Add colorbar
sm = plt.cm.ScalarMappable(cmap=colormap, norm=norm)
cbar = plt.colorbar(sm, ax=ax, orientation="vertical", pad=0.05)
cbar.set_label("Reliability Index ($\\beta$)")

# Create custom legend handles
legend_entries = [
    (min_beta_row["Municipality"], min_beta_row[f"{var}"]),
    (max_beta_row["Municipality"], max_beta_row[f"{var}"])
] + list(zip(highlight_rows["Municipality"], highlight_rows[f"{var}"]))

legend_handles = [
    mpatches.Patch(color=colormap(norm(beta)), label=f"{mun} ({beta:.2f})")
    for mun, beta in legend_entries
]

# Add legend at bottom-right
ax.legend(handles=legend_handles, loc="lower right", fontsize=10, frameon=True)

# Customize the map
#plt.title("Municipalities Colored by Reliability Index ($\\beta$)")    
plt.title("Municipalities Colored by Change in Characteristic Value")     
plt.xlabel("Easting (meters)")
plt.ylabel("Northing (meters)")
plt.grid(True)

# Ensure output directory exists
os.makedirs(os.path.dirname(output_map_path), exist_ok=True)

# Save the figure
plt.savefig(output_map_path, dpi=300, bbox_inches="tight")
plt.show()
