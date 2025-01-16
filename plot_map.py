import numpy as np
import scipy as sp
from SnowAnalysis_HU import MAIN
import matplotlib.pyplot as plt
from pyproj import Proj, transform
import geopandas as gpd
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib import cm  # For colormap
from matplotlib.colors import Normalize  # For normalizing values

### INPUT ####
#ChatGPT was used to transform Multiplelocationsmap.py to make a color coding of the locations based of the reliability index 

h_Trd_gl = 0.1254
cov_Trd_gl = 0.7
sk_Trd_gl = 3.5

h_Trd_li = 0.2645
cov_Trd_li = 0.6
sk_Trd_li = 4.5  # Different from JK_DRAFT?

h_lys = 0.0551
cov_lys = 0.7
sk_lys = 3.5

h_lop = 0.8158
cov_lop = 0.4
sk_lop = 5

h_lom = 0.1491
cov_lom = 0.5
sk_lom = 3.5

### Use FORM to Calculate reliability indices. MC for control ###
Bf_lys, Bmc_lys = MAIN(h_lys, cov_lys, sk_lys)
Bf_trd_gl, Bmc_trd_gl = MAIN(h_Trd_gl, cov_Trd_gl, sk_Trd_gl)
Bf_trd_li, Bmc_trd_li = MAIN(h_Trd_li, cov_Trd_li, sk_Trd_li)
Bf_lop, Bmc_lop = MAIN(h_lop, cov_lop, sk_lop)
Bf_lom, Bmc_lom = MAIN(h_lom, cov_lom, sk_lom)



#For very high reliability indices the FORM malfunctions and returns 1. This is handled by setting b=5 when no failures accure in the Monte Carlo simulation

reliability_indices = {
    "Trondheim 1 (Gløshaugen)": 5 if Bmc_trd_gl == float('inf') else Bf_trd_gl,
    "Trondheim 2 (Lianvegen)": 5 if Bmc_trd_li == float('inf') else Bf_trd_li,
    "Lysaker (Standard Norge)": 5 if Bmc_lys == float('inf') else Bf_lys,
    "Loppa Kommune (Langfjordhamn)": 5 if Bmc_lop == float('inf') else Bf_lop,
    "Lom (Innlandet)": 5 if Bmc_lom == float('inf') else Bf_lom
}




# Normalize reliability indices to [0, 1] for the colormap
norm = Normalize(vmin=min(reliability_indices.values()), vmax=max(reliability_indices.values()))
colormap = cm.get_cmap("RdYlGn")  # Red-to-Green colormap

# Assign a color to each location based on reliability index
location_colors = {name: colormap(norm(Bf)) for name, Bf in reliability_indices.items()}

### Plot ####
# Define UTM Zone 33N projection and WGS84
utm_proj = Proj(proj="utm", zone=33, datum="WGS84")
wgs84_proj = Proj(proj="longlat", datum="WGS84")

# Define the geographic bounding box of mainland Norway (WGS84)
min_lon, max_lon = 4.5, 31.0  # Longitude extent
min_lat, max_lat = 57.5, 71.2  # Latitude extent

# Convert bounding box to UTM Zone 33 coordinates
min_x, min_y = transform(wgs84_proj, utm_proj, min_lon, min_lat)
max_x, max_y = transform(wgs84_proj, utm_proj, max_lon, max_lat)

# Load the countries shapefile
shapefile_path = '/Users/hakon/SnowAnalysis_JK/DataSources/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp'
norway = gpd.read_file(shapefile_path)

# Filter for Norway
norway = norway[norway["ADMIN"] == "Norway"]

# Define the locations and names with latitude and longitude
locations = [
    ("Trondheim 1 (Gløshaugen)", 63.41597611839954, 10.408475429413997),
    ("Trondheim 2 (Lianvegen)", 63.405030783022426, 10.313520469174751),
    ("Lysaker (Standard Norge)", 59.91520899674151, 10.638403997785314),
    ("Loppa Kommune (Langfjordhamn)", 70.13995711333514, 21.856517535853513),
    ("Lom (Innlandet)", 61.83933422146636, 8.567791464666023),
]

# Convert each location to UTM coordinates
utm_locations = [(name, transform(wgs84_proj, utm_proj, lon, lat)) for name, lat, lon in locations]

# Create the figure and axes, using UTM projection
fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={"projection": ccrs.UTM(33)})

# Add land, ocean, borders, and coastline features
#ax.add_feature(cfeature.LAND, facecolor="lightgreen")
#ax.add_feature(cfeature.OCEAN)
ax.add_feature(cfeature.BORDERS, linestyle=":")
ax.add_feature(cfeature.COASTLINE)
#ax.add_feature(cfeature.LAKES, facecolor="lightblue")
#ax.add_feature(cfeature.RIVERS, edgecolor="blue")

# Plot Norway boundary
norway.boundary.plot(ax=ax, color="blue", linewidth=1)

# Set the extent of the plot using the UTM coordinates
ax.set_extent([min_x, max_x, min_y, max_y], crs=ccrs.UTM(33))

# Plot each location with the reliability index in the label
for name, (x, y) in utm_locations:
    if name in reliability_indices:
        bf_label = f"{reliability_indices[name]:.2f}" if reliability_indices[name] != 5 else ">5"
        ax.plot(x, y, marker="o", color=location_colors[name], markersize=10, label=f"{name}: $\\beta = {bf_label}$")


# Add a colorbar to represent the reliability indices
sm = plt.cm.ScalarMappable(cmap=colormap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, orientation="vertical", pad=0.05)
cbar.set_label("Reliability Index ($\\beta $)")

# Set the title of the map
ax.set_title("Map of Norway with Locations Colored by Reliability Index")

# Add a legend
ax.legend()

# Adjust layout for better spacing
plt.tight_layout()

# Save the map (using user's path)
output_path = "/Users/hakon/SnowAnalysis_JK/Output/Maps/norway_map_colored_by_Bf.png"
plt.savefig(output_path, dpi=300, bbox_inches="tight")

# Show the plot
plt.show()
