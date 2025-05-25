from pyproj import Transformer
import geopandas as gpd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import xarray as xr
from coordinates import coordinates
import matplotlib.lines as mlines
from matplotlib import rcParams
rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],  # Matches LaTeX default
    "axes.formatter.use_mathtext": True
})

# === Config ===
municipality_name = "Farsund"
marker_size = 6
fontsize_ = 25
shapefile_path = '/Users/hakon/SnowAnalysis_HU/DataSources/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp'
output_path = '/Users/hakon/SnowAnalysis_HU/Output/main_output/farsund_coordinates.png'
dataset_url = 'https://thredds.met.no/thredds/dodsC/KSS/Klima_i_Norge_2100/utgave2015/SWE/MPI_RCA/rcp45/rcp45_MPI_RCA_SWE_daily_2025_v4.nc'

# === Load Dataset ===
try:
    ds = xr.open_dataset(dataset_url, chunks=None)
except Exception as e:
    raise RuntimeError(f"Could not open dataset: {e}")

# === Coordinate Handling ===
transformer = Transformer.from_crs("EPSG:4326", "EPSG:32633", always_xy=True)
coords_wgs84 = coordinates(municipality_name, ds, save_all_attempts=True)
coords_utm = [transformer.transform(lon, lat) for lat, lon in coords_wgs84]

# === Map Extent ===
ref_lat, ref_lon = coords_wgs84[0]
ref_x, ref_y = coords_utm[0]
offset_lon, offset_lat = 0.04, 0.02
min_x, min_y = transformer.transform(ref_lon - offset_lon, ref_lat - offset_lat)
max_x, max_y = transformer.transform(ref_lon + offset_lon, ref_lat + offset_lat)

# === Load Norway Shapefile ===
norway = gpd.read_file(shapefile_path)
norway = norway.to_crs(epsg=32633)
norway = norway[norway['ADMIN'] == "Norway"]

# === Create Map ===
fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': ccrs.UTM(33)})

# Add geographic features
ax.add_feature(cfeature.LAND, facecolor='lightgreen')
ax.add_feature(cfeature.OCEAN)
ax.add_feature(cfeature.BORDERS, linestyle=':')
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.LAKES, facecolor='lightblue')
ax.add_feature(cfeature.RIVERS, edgecolor='blue')



# Plot Norway boundary
norway.boundary.plot(ax=ax, color='blue', linewidth=1)

# Set extent
ax.set_extent([min_x, max_x, min_y, max_y], crs=ccrs.UTM(33))

# === Plot Points ===
num_points = len(coords_utm)
for idx, (x, y) in enumerate(coords_utm):
    if idx == 0:
        ax.plot(x, y, marker='o', color='red', markersize=marker_size, transform=ccrs.UTM(33))
    elif idx == num_points - 1:
        ax.plot(x, y, marker='o', color='green', markersize=marker_size, transform=ccrs.UTM(33))
    else:
        ax.plot(x, y, marker='o', color='blue', markersize=marker_size, transform=ccrs.UTM(33))

# === Add Title & Legend ===
ax.set_title(f'Coordinates around {municipality_name}', fontsize=fontsize_)
ax.set_aspect('equal', 'box')

# Legend
legend_items = [
    mlines.Line2D([], [], color='red', marker='o', markersize=10, linestyle='None', label='First Point'),
    mlines.Line2D([], [], color='green', marker='o', markersize=10, linestyle='None', label='Final Point'),
    mlines.Line2D([], [], color='blue', marker='o', markersize=10, linestyle='None', label='Intermediate Points'),
]
ax.legend(handles=legend_items, loc='best', fontsize=fontsize_-3)

# === Save Output ===
plt.tight_layout()
plt.savefig(output_path, dpi=300, format="png", bbox_inches='tight')
plt.show()
plt.close(fig)

