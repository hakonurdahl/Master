# Because of the many computational expensive operations, the data is stored in csv files

import csv
import os
import csv
import xarray as xr
import numpy as np
import ast

from municipalities import municipalities_data
from coordinates import coordinates
from elevation import get_elevations
from swe import measurements
from FORM import calibration
from FORM import municipality_form
from FORM import char
from FORM import char_actual
from FORM import prop
from A_funcstat import get_values


input_data = {

    #Period

    "tot": {"period": (1960, 2024), "scenario": None},
    "new": {"period": (1991, 2024),"scenario": None},
    "old": {"period": (1960, 1990),"scenario": None},
    "future_rcp45": {"period": (2024, 2074),"scenario": "rcp45"},
    "future_rcp85": {"period": (2024, 2074),"scenario": "rcp85"},

    #Variable

    "beta": {"limits": (3,6),"label": "Reliability Index ($\\beta$)", "title": "Municipalities Colored by Reliability Index ($\\beta$)"},
    "char": {"limits": (0, 10),"label": "Characteristic Value", "title": "Municipalities Colored by Characteristic Value"},
    "CoV": {"limits": (0,1),"label": "Coefficient of Variance", "title": "Municipalities Colored by Coefficient of Variance"},

}

# Define the folder path
folder_path = "C:/Users/hakon/SnowAnalysis_HU/stored_data"

os.makedirs(folder_path, exist_ok=True)  # Ensure the directory exists

#Writes a csv file with a list of yearly maximum SWE values for a given period for all municipalities 
def print_to_csv_swe(time, start_municipality=None):

    #INPUT

    #if future projection, define scenario
    scen=input_data[time]["scenario"]

    #Define time period
    years=input_data[time]["period"]
    
    #Naming
    csv_file_path = os.path.join(folder_path, f"swe_{time}.csv")

    # Determine whether to overwrite or append
    overwrite = start_municipality is None  # If no start point, overwrite
    mode = "w" if overwrite else "a"  # "w" for overwrite, "a" for append
    file_exists = os.path.exists(csv_file_path)

    with open(csv_file_path, mode=mode, newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # Write header only if overwriting or if the file is new
        if overwrite or not file_exists:
            writer.writerow(["municipality", "swe"])

        # Load datasets for future SWE projections
        ds_list = []
        for year in range(years[0], years[1]):
            if scen==None:
                opendap_url = f'https://thredds.met.no/thredds/dodsC/senorge/seNorge_snow/swe/swe_{year}.nc'      #Past
            else:
                opendap_url = f'https://thredds.met.no/thredds/dodsC/KSS/Klima_i_Norge_2100/utgave2015/SWE/MPI_RCA/{scen}/{scen}_MPI_RCA_SWE_daily_{year}_v4.nc'      #Future
                
            try:
                ds_list.append(xr.open_dataset(opendap_url, chunks=None))
            except Exception as e:
                print(f"Could not process year {year}: {e}")

        start_writing = overwrite  # Start from beginning if overwriting

        # Loop through municipalities and write data
        for municipality in municipalities_data.keys():
            if not start_writing:
                if municipality == start_municipality:
                    start_writing = True  # Found the start point, begin writing

            if start_writing:
                swe = measurements(municipality, ds_list, scen)
                
                # Convert NaN values to a standardized string representation
                swe_str = "[nan]" if np.isnan(swe).all() else repr(swe.tolist())
                
                writer.writerow([municipality, swe_str])
                file.flush()  # Flush after every write
                print(f'SWE for {municipality} successfully added')  # Debugging

    print(f"CSV file successfully {'overwritten' if overwrite else 'updated'} at: {csv_file_path}")


#This is a csv file storing all the points that falls within the square kilometer of the measurement
def print_to_csv_points(start_municipality=None):
    
    #Random year and dataset chosen
    opendap_url = f'https://thredds.met.no/thredds/dodsC/senorge/seNorge_snow/swe/swe_2024.nc'

    try:
        # Open the dataset
        ds = xr.open_dataset(opendap_url, chunks=None)
            
    except Exception as e:
        print(f"Could not process year 2024: {e}")
    
    csv_file_path = os.path.join(folder_path, "points.csv")

    # Determine whether to overwrite or append
    overwrite = start_municipality is None  # If no start point, overwrite

    mode = "w" if overwrite else "a"  # "w" for overwrite, "a" for append
    file_exists = os.path.exists(csv_file_path)

    with open(csv_file_path, mode=mode, newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # Write header only if overwriting or if the file is new
        if overwrite or not file_exists:
            writer.writerow(["municipality", "points"])

        start_writing = overwrite  # Start from beginning if overwriting

        # Loop through municipalities and write data
        for municipality, data in municipalities_data.items():
            if not start_writing:
                if municipality == start_municipality:
                    start_writing = True  # Found the start point, begin writing

            if start_writing:
                points = coordinates(municipality, ds)
                writer.writerow([municipality, points])
                file.flush()  # Flush after every write
                print(f'Points for {municipality} successfully added')  # Debugging

    print(f"CSV file successfully {'overwritten' if overwrite else 'updated'} at: {csv_file_path}")


#
def print_to_csv_elevation(start_municipality=None):
    """
    Writes elevation data to a CSV file for all municipalities,
    starting from a specific municipality if provided.
    """

    # Define CSV path
    csv_file_path = os.path.join(folder_path, "elevation.csv")

    # Determine whether to overwrite or append
    overwrite = start_municipality is None
    mode = "w" if overwrite else "a"
    file_exists = os.path.exists(csv_file_path)

    with open(csv_file_path, mode=mode, newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # Write header only if overwriting or file does not exist
        if overwrite or not file_exists:
            writer.writerow(["municipality", "elevation"])

        start_writing = overwrite  # Start writing immediately if overwriting

        # Loop through municipalities
        for municipality, data in municipalities_data.items():
            if not start_writing:
                if municipality == start_municipality:
                    start_writing = True

            if start_writing:
                coordinates = get_values(
                    "C:/Users/hakon/SnowAnalysis_HU/stored_data/points.csv",
                    municipality,
                    "points"
                )
                elevation = get_elevations(coordinates)
                writer.writerow([municipality, elevation])
                file.flush()

                print(f"Elevation for {municipality} successfully added")

    print(f"CSV file successfully {'overwritten' if overwrite else 'updated'} at: {csv_file_path}")


#
def print_to_csv_beta(time, start_municipality=None):
    # Define the CSV file path

    years=input_data[time]["period"]
    csv_file_path = os.path.join(folder_path, f"beta_{time}.csv")
    
    # Determine whether to overwrite or append
    overwrite = start_municipality is None  # If no start point, overwrite
    mode = "w" if overwrite else "a"  # "w" for overwrite, "a" for append
    file_exists = os.path.exists(csv_file_path)
    
    with open(csv_file_path, mode=mode, newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        
        # Write header only if overwriting or if the file is new
        if overwrite or not file_exists:
            writer.writerow(["municipality", "var"])
        
        start_writing = overwrite  # Start from beginning if overwriting
        
        # Loop through municipalities and write data
        for municipality, data in municipalities_data.items():
            if not start_writing:
                if municipality == start_municipality:
                    start_writing = True  # Found the start point, begin writing
            
            if start_writing:
                beta, alpha = municipality_form(municipality, time, None)
                writer.writerow([
                    municipality,
                    beta
                ])
                file.flush()  # Flush after every write
                print(f'Beta for {municipality} and period {time} successfully added')  # Debugging
    
    print(f"CSV file successfully {'overwritten' if overwrite else 'updated'} at: {csv_file_path}")


#
def print_to_csv_char(start_municipality=None):
    # Define the CSV file path

    csv_file_path = os.path.join(folder_path, f"char_ec.csv")

    file_exists = os.path.exists(csv_file_path)
    
    with open(csv_file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        
        writer.writerow(["municipality", "var"])
                
        # Loop through municipalities and write data
        for municipality, data in municipalities_data.items():
            char_= char(municipality)
            writer.writerow([
                municipality,
                char_
            ])
            file.flush()  # Flush after every write
            print(f'Char for {municipality} successfully added')  # Debugging
    
    print(f"CSV file successfully overwritten at: {csv_file_path}")


def print_to_csv_char_actual(start_municipality=None):
    # Define the CSV file paths
    csv_file_path_1 = os.path.join(folder_path, "char_actual_tot.csv")
    csv_file_path_2 = os.path.join(folder_path, "beta_actual_tot.csv")

    # Determine file mode
    overwrite = start_municipality is None
    mode = "w" if overwrite else "a"
    file1_exists = os.path.exists(csv_file_path_1)
    file2_exists = os.path.exists(csv_file_path_2)

    # Open both files simultaneously
    with open(csv_file_path_1, mode=mode, newline="", encoding="utf-8") as file1, \
         open(csv_file_path_2, mode=mode, newline="", encoding="utf-8") as file2:

        writer1 = csv.writer(file1)
        writer2 = csv.writer(file2)

        # Write headers only if overwriting or if files are new
        if overwrite or not file1_exists:
            writer1.writerow(["municipality", "var"])
        if overwrite or not file2_exists:
            writer2.writerow(["municipality", "var"])

        start_writing = overwrite

        # Loop through municipalities and write data
        for municipality, data in municipalities_data.items():
            if not start_writing:
                if municipality == start_municipality:
                    start_writing = True  # Found the start point, begin writing

            if start_writing:
                char_ = char_actual(municipality)
                beta, _ = municipality_form(municipality, "tot", char_)

                writer1.writerow([municipality, char_])
                writer2.writerow([municipality, beta])

                file1.flush()
                file2.flush()

                print(f"Characteristic value and beta for {municipality} successfully added")

    print(f"CSV files successfully {'overwritten' if overwrite else 'updated'} at: {csv_file_path_1} and {csv_file_path_2}")

#
def print_to_csv_cov(time, start_municipality=None):
    # Define the CSV file path

    years=input_data[time]["period"]
    csv_file_path = os.path.join(folder_path, f"cov_{time}.csv")
    
    # Determine whether to overwrite or append
    overwrite = start_municipality is None  # If no start point, overwrite
    mode = "w" if overwrite else "a"  # "w" for overwrite, "a" for append
    file_exists = os.path.exists(csv_file_path)
    
    with open(csv_file_path, mode=mode, newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        
        # Write header only if overwriting or if the file is new
        if overwrite or not file_exists:
            writer.writerow(["municipality", "var"])
        
        start_writing = overwrite  # Start from beginning if overwriting
        
        # Loop through municipalities and write data
        for municipality, data in municipalities_data.items():
            if not start_writing:
                if municipality == start_municipality:
                    start_writing = True  # Found the start point, begin writing
            
            if start_writing:
                mean_, cov_= prop(municipality, time)
                writer.writerow([
                    municipality,
                    cov_
                ])
                file.flush()  # Flush after every write
                print(f'CoV for {municipality} successfully added')  # Debugging
    
    print(f"CSV file successfully {'overwritten' if overwrite else 'updated'} at: {csv_file_path}")


#
def print_to_csv_diff(time_1, var_1, time_2, var_2):

    """Computes the difference in values between two CSV files and writes to a new CSV file."""
    values = {}
    
    # Read the first file and store values
    csv_file_path_1 = f"C:/Users/hakon/SnowAnalysis_HU/stored_data/{var_1}_{time_1}.csv"
    with open(csv_file_path_1, mode='r', encoding='utf-8') as f1:
        reader1 = csv.DictReader(f1)
        for row in reader1:
            values[row["municipality"]] = float(row[f"var"])
    
    # Read the second file and calculate the difference
    results = []
    csv_file_path_2 = f"C:/Users/hakon/SnowAnalysis_HU/stored_data/{var_2}_{time_2}.csv"
    with open(csv_file_path_2, mode='r', encoding='utf-8') as f2:
        reader2 = csv.DictReader(f2)
        for row in reader2:
            municipality = row["municipality"]
            if municipality in values:
                diff =  values[municipality] - float(row[f"var"])
                results.append([municipality, diff])
            else:
                print(f"Municipality {municipality} not found in first file.")
    
    # Write results to the output CSV file
    csv_file_path = f"C:/Users/hakon/SnowAnalysis_HU/stored_data/diff_{var_1}_{time_1}_{time_2}.csv"
    with open(csv_file_path, mode='w', encoding='utf-8', newline='') as f_out:
        writer = csv.writer(f_out)
        writer.writerow(["municipality", "var"])
        writer.writerows(results)
    
    print(f"CSV file successfully overwritten at: {csv_file_path}")


def print_to_csv_char_opt(time, start_municipality=None):
    # Define the CSV file paths
    csv_file_path_1 = os.path.join(folder_path, f"opt_char_{time}.csv")
    csv_file_path_2 = os.path.join(folder_path, f"opt_beta_{time}.csv")

    # Determine file mode
    overwrite = start_municipality is None
    mode = "w" if overwrite else "a"
    file1_exists = os.path.exists(csv_file_path_1)
    file2_exists = os.path.exists(csv_file_path_2)

    # Open both files simultaneously
    with open(csv_file_path_1, mode=mode, newline="", encoding="utf-8") as file1, \
         open(csv_file_path_2, mode=mode, newline="", encoding="utf-8") as file2:

        writer1 = csv.writer(file1)
        writer2 = csv.writer(file2)

        # Write headers only if overwriting or if files are new
        if overwrite or not file1_exists:
            writer1.writerow(["municipality", "var"])
        if overwrite or not file2_exists:
            writer2.writerow(["municipality", "var"])

        start_writing = overwrite

        # Loop through municipalities and write data
        for municipality, data in municipalities_data.items():
            if not start_writing:
                if municipality == start_municipality:
                    start_writing = True  # Found the start point, begin writing

            if start_writing:
                char_opt, beta = calibration(municipality, time, 3.8)
                writer1.writerow([municipality, char_opt])
                writer2.writerow([municipality, beta])
                file1.flush()
                file2.flush()
                print(f"Optimal characteristic value and beta for {municipality} successfully added")

    print(f"CSV files successfully {'overwritten' if overwrite else 'updated'} at: {csv_file_path_1} and {csv_file_path_2}")



#print_to_csv_points()  #Run to update sample points

#print_to_csv_elevation()  #Run to update elevation

#print_to_csv_swe()  #Run to update swe

#print_to_csv_beta("tot")  #Run to update map csv file

#print_to_csv_char()

#print_to_csv_map_diff()

#print_to_csv_map_cov()

#print_to_csv_char_opt("tot")

#print_to_csv_diff("tot", "opt_char", "ec", "char")

#print_to_csv_char_actual()