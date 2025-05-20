import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import csv
import os
from pyproj import Transformer
from matplotlib.colors import Normalize
import matplotlib.patches as mpatches  # Import for custom legend patches
import ast

input_data = {

    #Period

    "tot": {"period": (1960, 2024), "scenario": None},
    "new": {"period": (1991, 2024),"scenario": None},
    "old": {"period": (1960, 1990),"scenario": None},
    "future_rcp45": {"period": (2024, 2074),"scenario": "rcp45"},
    "future_rcp85": {"period": (2024, 2074),"scenario": "rcp85"},

    #Variable

    "beta": {"limits": (2.5,6),"label": "Reliability Index ($\\beta$)", "title": "Municipalities Colored by Reliability Index ($\\beta$)"},
    "opt_beta": {"limits": (2.5,6),"label": "Reliability Index ($\\beta$)", "title": "Municipalities Colored by Reliability Index ($\\beta$)"},
    "char": {"limits": (0, 10),"label": "Characteristic Value", "title": "Municipalities Colored by Characteristic Value"},
    "cov": {"limits": (0.3,0.8),"label": "Coefficient of Variance", "title": "Municipalities Colored by Coefficient of Variance"},
    "opt_char": {"limits": (0,10),"label": "Optimal Characteristic Value", "title": "Municipalities Colored by Optimal Characteristic Value"},
    "diff_beta_new_beta": {"limits": (-2,2),"label": "$\\Delta$Reliability Index ($\\beta$)", "title": "Municipalities Colored by Change in Reliability Index"}
}


def map(period, variable):
    # === Font size control for both title and legend ===
    map_fontsize = 10

    limits = input_data[variable]["limits"]
    label_ = input_data[variable]["label"]
    title_ = input_data[variable]["title"]

    # File paths
    geojson_path = "C:/Users/hakon/SnowAnalysis_HU/DataSources/Basisdata_0000_Norge_25833_Kommuner_GeoJSON/Basisdata_0000_Norge_25833_Kommuner_GeoJSON.geojson"
    output_map_path_1 = f"C:/Users/hakon/SnowAnalysis_HU/Output/main_output/{variable}_{period}.pdf"
    output_map_path_2 = f"C:/Users/hakon/SnowAnalysis_HU/Output/main_output/{variable}_{period}.png"
    var_csv_path = f"C:/Users/hakon/SnowAnalysis_HU/stored_data/{variable}_{period}.csv"
    points_csv_path = f"C:/Users/hakon/SnowAnalysis_HU/stored_data/points.csv"

    # Load data
    var_df = pd.read_csv(var_csv_path)
    points_df = pd.read_csv(points_csv_path)

    # Parse the string representation of tuples in 'points' column
    def extract_lat_lon(point_str):
        try:
            coords = ast.literal_eval(point_str)
            if coords and isinstance(coords[0], tuple):
                lat, lon = coords[0]
                return pd.Series([lat, lon])
            else:
                return pd.Series([None, None])
        except Exception:
            return pd.Series([None, None])

    points_df[["latitude", "longitude"]] = points_df["points"].apply(extract_lat_lon)

    # Merge the variable and coordinate data
    df = pd.merge(var_df, points_df[["municipality", "latitude", "longitude"]], on="municipality", how="inner")
    df = df[["municipality", "latitude", "longitude", "var"]]

    # Convert coordinates to UTM Zone 33 (EPSG:32633)
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:32633", always_xy=True)
    df["Easting"], df["Northing"] = zip(*df.apply(lambda row: transformer.transform(row["longitude"], row["latitude"]), axis=1))

    # Load the GeoJSON file (only Kommune layer)
    gdf_kommune = gpd.read_file(geojson_path, layer="Kommune")

    # Ensure correct CRS
    if gdf_kommune.crs is None:
        gdf_kommune.set_crs(epsg=25833, inplace=True)
    elif gdf_kommune.crs.to_epsg() != 25833:
        gdf_kommune.to_crs(epsg=25833, inplace=True)

    # Find municipalities with the lowest and highest var
    min_beta_row = df.loc[df["var"].idxmin()]
    max_beta_row = df.loc[df["var"].idxmax()]

    # Define key municipalities to highlight
    highlight_municipalities = ["Oslo", "Bergen", "Trondheim"]
    highlight_rows = df[df["municipality"].isin(highlight_municipalities)]

    # Normalize beta values for colormap
    lim = 1
    if lim == 0:
        norm = Normalize(vmin=df["var"].min(), vmax=df["var"].max())
    else:
        norm = Normalize(vmin=limits[0], vmax=limits[1])

    colormap = plt.cm.RdYlGn
    df["Color"] = df["var"].apply(lambda beta: colormap(norm(beta)))

    # Geometry mapping
    df["Geometry"] = df.apply(lambda row: gpd.points_from_xy([row["Easting"]], [row["Northing"]])[0], axis=1)
    df["Municipality_GDF"] = df.apply(lambda row: gdf_kommune[gdf_kommune.intersects(row["Geometry"])], axis=1)

    municipalities_with_points = set()
    for matched in df["Municipality_GDF"]:
        municipalities_with_points.update(matched["kommunenavn"].tolist())

    all_municipalities = set(gdf_kommune["kommunenavn"])
    municipalities_without_points = all_municipalities - municipalities_with_points

    print("Municipalities without any data points:")
    for name in sorted(municipalities_without_points):
        print("-", name)

    # === Plotting ===
    fig, ax = plt.subplots(figsize=(12, 8))
    plt.title(title_, fontsize=map_fontsize)

    gdf_kommune.plot(ax=ax, color='grey', edgecolor=None, linewidth=0.0)

    for _, row in df.iterrows():
        if not row["Municipality_GDF"].empty:
            row["Municipality_GDF"].plot(ax=ax, color=row["Color"], edgecolor=None, linewidth=0.0)

    # Colorbar
    sm = plt.cm.ScalarMappable(cmap=colormap, norm=norm)
    cbar = plt.colorbar(sm, ax=ax, orientation="vertical", pad=0.05)
    cbar.set_label(label_, fontsize=map_fontsize)
    cbar.ax.tick_params(labelsize=map_fontsize)

    # Custom legend
    legend_entries = [
        (min_beta_row["municipality"], min_beta_row["var"]),
        (max_beta_row["municipality"], max_beta_row["var"])
    ] + list(zip(highlight_rows["municipality"], highlight_rows["var"]))

    legend_handles = [
        mpatches.Patch(color=colormap(norm(beta)), label=f"{mun} ({beta:.2f})")
        for mun, beta in legend_entries
    ]

    ax.legend(handles=legend_handles, loc="lower right", fontsize=map_fontsize, frameon=True)

    # === Remove grid and axis details ===
    ax.grid(False)
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_xticks([])
    ax.set_yticks([])

    # === Save ===
    os.makedirs(os.path.dirname(output_map_path_1), exist_ok=True)
    plt.savefig(output_map_path_1, dpi=300, bbox_inches="tight")
    plt.savefig(output_map_path_2, dpi=300, bbox_inches="tight")
    #plt.show()


#plot_map("tot", "beta")