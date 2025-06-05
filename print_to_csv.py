import csv
import os
import xarray as xr
import numpy as np

from coordinates import coordinates
from elevation import get_elevations
from swe import measurements
from FORM import calibration, municipality_form, char, char_actual, prop
from C_Input_AHG import input_data
from A_funcstat import get_values


# Many of the calculations in this project are computationally intensive or involve large datasets. 
# This Python file automates the extraction, computation, and storage of the necessary data.
# The results are written to CSV files for later use in analysis, visualization, and reporting.
# This script stores results in CSV files to avoid recalculating the same values repeatedly.



# Folder where all data files are stored
folder_path = "C:/Users/hakon/SnowAnalysis_HU/stored_data"
os.makedirs(folder_path, exist_ok=True)

# Load municipality properties directly from EN1991.csv
municipalities_data = {}
with open(os.path.join(folder_path, "EN1991.csv"), mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        municipalities_data[row["municipality"]] = {
            "sk_0": float(row["sk_0"]),
            "hg": float(row["hg"]),
            "dsk": float(row["dsk"]),
            "sk_maks": float(row["sk_maks"]),
        }


# Generic function to write CSV output
def write_csv(filename, header, rows, mode="w"):
    file_path = os.path.join(folder_path, filename)
    with open(file_path, mode=mode, newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if mode == "w":
            writer.writerow(header)
        writer.writerows(rows)
    print(f"CSV written: {file_path}")

# Download dataset files sequentially (one request at a time)
def load_swe_datasets(years, scenario=None):
    ds_list = []
    for year in range(years[0], years[1]):
        # The historical and future projections are from different URLs
        if scenario:
            url = f'https://thredds.met.no/thredds/dodsC/KSS/Klima_i_Norge_2100/utgave2015/SWE/MPI_RCA/{scenario}/{scenario}_MPI_RCA_SWE_daily_{year}_v4.nc'
        else:
            url = f'https://thredds.met.no/thredds/dodsC/senorge/seNorge_snow/swe/swe_{year}.nc'
        try:
            print(f"Loading dataset: {year}")
            ds_list.append(xr.open_dataset(url, chunks=None))
        except Exception as e:
            print(f"Failed to load {year}: {e}")
    return ds_list

# SWE data
def print_to_csv_swe(time, start_municipality=None):
    scen = input_data[time]["scenario"]
    years = input_data[time]["period"]
    ds_list = load_swe_datasets(years, scen)

    rows = []
    start = start_municipality is None
    for municipality in municipalities_data:
        if not start and municipality == start_municipality:
            start = True
        if start:
            swe = measurements(municipality, ds_list, scen)
            swe_str = "[nan]" if np.isnan(swe).all() else repr(swe.tolist())
            rows.append([municipality, swe_str])
            print(f"SWE added: {municipality}")
    write_csv(f"swe_{time}.csv", ["municipality", "swe"], rows)

# Points within grid cells
def print_to_csv_points(start_municipality=None):
    url =  f'https://thredds.met.no/thredds/dodsC/KSS/Klima_i_Norge_2100/utgave2015/SWE/MPI_RCA/rcp85/rcp85_MPI_RCA_SWE_daily_2025_v4.nc'

    try:
        ds = xr.open_dataset(url, chunks=None)
    except Exception as e:
        print(f"Dataset load failed: {e}")
        return

    rows = []
    start = start_municipality is None
    for municipality in municipalities_data:
        if not start and municipality == start_municipality:
            start = True
        if start:
            pts = coordinates(municipality, ds)
            rows.append([municipality, pts])
            print(f"Points added: {municipality}")
    write_csv("points.csv", ["municipality", "points"], rows)

# Elevation values
def print_to_csv_elevation(start_municipality=None):
    rows = []
    start = start_municipality is None
    for municipality in municipalities_data:
        if not start and municipality == start_municipality:
            start = True
        if start:
            coords = get_values(os.path.join(folder_path, "points.csv"), municipality, "points")
            elev = get_elevations(coords)
            rows.append([municipality, elev])
            print(f"Elevation added: {municipality}")
    write_csv("elevation.csv", ["municipality", "elevation"], rows)

# Generic template for char, beta, cov, etc.
def print_single_value_csv(task_name, header_name, compute_func, time=None, start_municipality=None):
    rows = []
    start = start_municipality is None
    for municipality in municipalities_data:
        if not start and municipality == start_municipality:
            start = True
        if start:
            result = compute_func(municipality) if not time else compute_func(municipality, time)
            rows.append([municipality, result])
            print(f"{header_name} added: {municipality}")
    write_csv(f"{task_name}.csv", ["municipality", "var"], rows)

# Specific versions using the generic writer
def print_to_csv_char(start_municipality=None):
    print_single_value_csv("char_ec", "char", char, start_municipality=start_municipality)

def print_to_csv_beta(time, start_municipality=None):
    def beta_func(m, t): return municipality_form(m, t, None)[0]
    print_single_value_csv(f"beta_{time}", "beta", beta_func, time=time, start_municipality=start_municipality)

def print_to_csv_cov(time, start_municipality=None):
    def cov_func(m, t): return prop(m, t)[1]
    print_single_value_csv(f"cov_{time}", "cov", cov_func, time=time, start_municipality=start_municipality)

# Characteristic value and beta from actual form
def print_to_csv_char_actual(start_municipality=None):
    rows_char = []
    rows_beta = []
    start = start_municipality is None
    for municipality in municipalities_data:
        if not start and municipality == start_municipality:
            start = True
        if start:
            c = char_actual(municipality)
            b, _ = municipality_form(municipality, "tot", c)
            rows_char.append([municipality, c])
            rows_beta.append([municipality, b])
            print(f"Actual char/beta added: {municipality}")
    write_csv("char_actual_tot.csv", ["municipality", "var"], rows_char)
    write_csv("beta_actual_tot.csv", ["municipality", "var"], rows_beta)

# Difference between two result CSVs
def print_to_csv_diff(time_1, var_1, time_2, var_2):
    def read_results(var, time):
        path = os.path.join(folder_path, f"{var}_{time}.csv")
        with open(path, mode='r', encoding='utf-8') as f:
            return {row["municipality"]: float(row["var"]) for row in csv.DictReader(f)}

    vals_1 = read_results(var_1, time_1)
    vals_2 = read_results(var_2, time_2)

    results = []
    for m in vals_2:
        if m in vals_1:
            results.append([m, vals_1[m] - vals_2[m]])
        else:
            print(f"Missing in first: {m}")
    write_csv(f"diff_{var_1}_{time_1}_{time_2}.csv", ["municipality", "var"], results)

# Optimized char and beta
def print_to_csv_char_opt(time, start_municipality=None):
    rows_char, rows_beta = [], []
    start = start_municipality is None
    for municipality in municipalities_data:
        if not start and municipality == start_municipality:
            start = True
        if start:
            char_opt, beta = calibration(municipality, time, 3.8)
            rows_char.append([municipality, char_opt])
            rows_beta.append([municipality, beta])
            print(f"Optimized char/beta added: {municipality}")
    write_csv(f"opt_char_{time}.csv", ["municipality", "var"], rows_char)
    write_csv(f"opt_beta_{time}.csv", ["municipality", "var"], rows_beta)

# Example usage
#print_to_csv_points()
#print_to_csv_elevation()
#print_to_csv_swe("tot")
#print_to_csv_beta("tot")
#print_to_csv_char()
#print_to_csv_cov("tot")
#print_to_csv_diff("tot", "opt_char", "ec", "char")
#print_to_csv_char_opt("tot")
#print_to_csv_char_actual()
