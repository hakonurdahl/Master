from pyproj import Proj, Transformer
import geopandas as gpd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import xarray as xr
import numpy as np

opendap_url = f'https://thredds.met.no/thredds/dodsC/senorge/seNorge_snow/swe/swe_2024.nc'

try:
    # Open the dataset
    
    
    ds = xr.open_dataset(opendap_url, chunks=None)
        

except Exception as e:
    print(f"Could not process year 2024: {e}")

def closest(lat, lon):# Calculate the distance to  for each point in the SWE dataset
        
    latitudes = ds['lat'].values
    longitudes = ds['lon'].values
    distances = np.sqrt((latitudes - lat)**2 + (longitudes - lon)**2)
    min_dist_index = np.unravel_index(np.argmin(distances), distances.shape)

    # Get the closest point coordinates
    closest_lat = latitudes[min_dist_index]
    closest_lon = longitudes[min_dist_index]
    return closest_lat, closest_lon

# Define UTM Zone 33N projection and WGS84
utm_proj = Proj(proj='utm', zone=33, datum='WGS84')
wgs84_proj = Proj(proj='longlat', datum='WGS84')

# Create transformer for coordinate transformation
transformer_to_utm = Transformer.from_proj(wgs84_proj, utm_proj)

# municipality's coordinates in WGS84



latitude_municipality = 59.2675
longitude_municipality = 10.4076


lat_close, lon_close=closest(59.2675, 10.4076)

# Convert municipality's coordinates to UTM Zone 33
x_municipality_close, y_municipality_close = transformer_to_utm.transform(lon_close, lat_close)
x_municipality, y_municipality = transformer_to_utm.transform(longitude_municipality, latitude_municipality)



# List of additional points
additional_points = [(59.26354351775349, 10.393496677073257), (59.26354351775349, 10.395496677073258), (59.26354351775349, 10.397496677073258), (59.26454351775349, 10.393496677073257), (59.26454351775349, 10.395496677073258), (59.26454351775349, 10.397496677073258), (59.26454351775349, 10.399496677073259), (59.26454351775349, 10.40149667707326), (59.26454351775349, 10.40349667707326), (59.26454351775349, 10.40549667707326), (59.265543517753486, 10.393496677073257), (59.265543517753486, 10.395496677073258), (59.265543517753486, 10.397496677073258), (59.265543517753486, 10.399496677073259), (59.265543517753486, 10.40149667707326), (59.265543517753486, 10.40349667707326), (59.265543517753486, 10.40549667707326), (59.265543517753486, 10.407496677073262), (59.265543517753486, 10.409496677073262), (59.26654351775348, 10.393496677073257), (59.26654351775348, 10.395496677073258), (59.26654351775348, 10.397496677073258), (59.26654351775348, 10.399496677073259), (59.26654351775348, 10.40149667707326), (59.26654351775348, 10.40349667707326), (59.26654351775348, 10.40549667707326), (59.26654351775348, 10.407496677073262), (59.26654351775348, 10.409496677073262), (59.26754351775348, 10.393496677073257), (59.26754351775348, 10.395496677073258), (59.26754351775348, 10.397496677073258), (59.26754351775348, 10.399496677073259), (59.26754351775348, 10.40149667707326), (59.26754351775348, 10.40349667707326), (59.26754351775348, 10.40549667707326), (59.26754351775348, 10.407496677073262), (59.26754351775348, 10.409496677073262), (59.26854351775348, 10.393496677073257), (59.26854351775348, 10.395496677073258), (59.26854351775348, 10.397496677073258), (59.26854351775348, 10.399496677073259), (59.26854351775348, 10.40149667707326), (59.26854351775348, 10.40349667707326), (59.26854351775348, 10.40549667707326), (59.26854351775348, 10.407496677073262), (59.26854351775348, 10.409496677073262), (59.269543517753476, 10.393496677073257), (59.269543517753476, 10.395496677073258), (59.269543517753476, 10.397496677073258), (59.269543517753476, 10.399496677073259), (59.269543517753476, 10.40149667707326), (59.269543517753476, 10.40349667707326), (59.269543517753476, 10.40549667707326), (59.269543517753476, 10.407496677073262), (59.269543517753476, 10.409496677073262), (59.270543517753474, 10.393496677073257), (59.270543517753474, 10.395496677073258), (59.270543517753474, 10.397496677073258), (59.270543517753474, 10.399496677073259), (59.270543517753474, 10.40149667707326), (59.270543517753474, 10.40349667707326), (59.270543517753474, 10.40549667707326), (59.270543517753474, 10.407496677073262), (59.270543517753474, 10.409496677073262), (59.27154351775347, 10.393496677073257), (59.27154351775347, 10.395496677073258), (59.27154351775347, 10.397496677073258), (59.27154351775347, 10.399496677073259), (59.27154351775347, 10.40149667707326), (59.27154351775347, 10.40349667707326), (59.27154351775347, 10.40549667707326), (59.27154351775347, 10.407496677073262), (59.27154351775347, 10.409496677073262), (59.27254351775347, 10.397496677073258), (59.27254351775347, 10.399496677073259), (59.27254351775347, 10.40149667707326), (59.27254351775347, 10.40349667707326), (59.27254351775347, 10.40549667707326), (59.27254351775347, 10.407496677073262), (59.27254351775347, 10.409496677073262), (59.27354351775347, 10.40549667707326), (59.27354351775347, 10.407496677073262), (59.27354351775347, 10.409496677073262)]
# Convert additional points to UTM
utm_points = [transformer_to_utm.transform(lon, lat) for lat, lon in additional_points]

# Define bounds for a square aspect around municipality
lon_offset, lat_offset = 0.05, 0.025
min_lon, max_lon = longitude_municipality - lon_offset, longitude_municipality + lon_offset
min_lat, max_lat = latitude_municipality - lat_offset, latitude_municipality + lat_offset

# Load the countries shapefile (adjust path)
shapefile_path = '/Users/hakon/SnowAnalysis_JK/DataSources/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp'
norway = gpd.read_file(shapefile_path)


norway = norway.to_crs(epsg=32633)  # EPSG code for UTM Zone 33N


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

# Set the extent of the plot
#ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())


min_x, min_y = transformer_to_utm.transform(min_lon, min_lat)
max_x, max_y = transformer_to_utm.transform(max_lon, max_lat)


ax.set_extent([min_x, max_x, min_y, max_y], crs=ccrs.UTM(33))



# Plot additional points with blue dots
for x, y in utm_points:
    ax.plot(x, y, marker='o', color='blue', markersize=2, transform=ccrs.UTM(33))

# Plot municipality with a red dot
ax.plot(x_municipality, y_municipality, marker='o', color='red', markersize=10, label='Chosen by ChatGPT', transform=ccrs.UTM(33))
#ax.text(x_municipality, y_municipality, 'Chosen by ChatGPT', fontsize=12, verticalalignment='bottom', transform=ccrs.UTM(33))

# Plot closest point with a green dot
ax.plot(x_municipality_close, y_municipality_close, marker='o', color='green', markersize=10, label='In SeNorge database', transform=ccrs.UTM(33))
#ax.text(x_municipality_close, y_municipality_close, 'In SeNorge database', fontsize=12, verticalalignment='bottom', transform=ccrs.UTM(33))





# Enforce equal scaling
ax.set_aspect('equal', 'box')

# Set gridlines

gl = ax.gridlines(draw_labels=False, dms=True, x_inline=False, y_inline=False)

gl.top_labels = gl.right_labels = False

# Set title
ax.set_title('Map of Tønsberg')

# Add legend
ax.legend()

# Adjust layout
plt.tight_layout()

# Save the map
output_path = '/Users/hakon/SnowAnalysis_JK/Output/Maps/norway_map_with_points.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight') 



# Show the plot
plt.show()

# Close the figure
plt.close(fig)
