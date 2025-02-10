import csv
import os
from municipalities import municipalities_data
from elevation_points import samples
from elevation import get_elevations
from measurements import measurements
import ast
from FORM import municipality_form
import xarray as xr

# Write all information to csv file that is to be used in plot_map.py. Since there are many operations in this calculation that takes a lot of data power,
# the calculations are done step by step and stored in csv files. 
#First of all a grid of points within the square kilometer is stored to municipalities_data_points.csv. The elevation from each of these points 
# are stored to municipalities_data_elevation.csv. The SWE are then stored to municipalities_data_swe.csv. The beta for each munipalities are calculated
# from the swe and the elevation and stored to municipalities_data_map.csv which is used to plot the map in the file plot_map.py.   

# Define the folder path (modify this to match your folder structure)
folder_path = "C:/Users/hakon/SnowAnalysis_JK/stored_data"



os.makedirs(folder_path, exist_ok=True)  # Ensure the directory exists


# First some helper functions that reads csv files.

#This helper function reads the csv files with points
def read_coordinates_from_csv(input_csv_path):
    """Reads municipalities and their coordinates from a CSV file."""
    municipalities_coordinates = {}
    with open(input_csv_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            municipality = row["Municipality"]
            # Safely parse the string representation of the coordinates list
            coordinates_str = row["Points"]
            coordinates = ast.literal_eval(coordinates_str)  # Safe parsing
            municipalities_coordinates[municipality] = coordinates 
    return municipalities_coordinates







#This is a csv file storing all the swe data

def print_to_csv_swe():
    # Define the CSV file path
    csv_file_path = os.path.join(folder_path, "municipalities_data_swe.csv")


    # Open CSV file for writing
    with open(csv_file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        
        # Write header row
        writer.writerow(["Municipality", "SWE"])

        ds_=[]
        for year in range(2020,2024):
                opendap_url = f'https://thredds.met.no/thredds/dodsC/senorge/seNorge_snow/swe/swe_{year}.nc'
                
                try:
                    # Open the dataset
                    ds_.append(xr.open_dataset(opendap_url, chunks=None))
                    

                except Exception as e:
                    print(f"Could not process: {e}")




        # Loop through municipalities and write data
        for municipality, data in municipalities_data.items():

            swe=measurements(municipality, ds_)  

            import numpy as np
            # Convert np.nan to "[nan]"
            if np.isnan(swe).all():  # Check if all values are NaN
                swe_str = "[nan]"
            else:
                swe_str = repr(swe.tolist())  # Convert to list string format
            
            writer.writerow([municipality, swe_str])
            file.flush()

            
            print(f'SWE for {municipality} successfully added') #For debugging

    print(f"CSV file successfully saved to: {csv_file_path}")

#This is a csv file storing all the points that falls within the square kilometer of the measurement




def print_to_csv_points(start_municipality=None):
    
    opendap_url = f'https://thredds.met.no/thredds/dodsC/senorge/seNorge_snow/swe/swe_2024.nc'

    try:
        # Open the dataset
        
        
        ds = xr.open_dataset(opendap_url, chunks=None)
            

    except Exception as e:
        print(f"Could not process year 2024: {e}")
    
    
    csv_file_path = os.path.join(folder_path, "municipalities_data_points.csv")

    # Determine whether to overwrite or append
    overwrite = start_municipality is None  # If no start point, overwrite

    mode = "w" if overwrite else "a"  # "w" for overwrite, "a" for append
    file_exists = os.path.exists(csv_file_path)

    with open(csv_file_path, mode=mode, newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # Write header only if overwriting or if the file is new
        if overwrite or not file_exists:
            writer.writerow(["Municipality", "Points"])

        start_writing = overwrite  # Start from beginning if overwriting

        # Loop through municipalities and write data
        for municipality, data in municipalities_data.items():
            if not start_writing:
                if municipality == start_municipality:
                    start_writing = True  # Found the start point, begin writing

            if start_writing:
                points = samples(municipality, ds)
                writer.writerow([municipality, points])
                file.flush()  # Flush after every write
                print(f'Points for {municipality} successfully added')  # Debugging

    print(f"CSV file successfully {'overwritten' if overwrite else 'updated'} at: {csv_file_path}")



#This is the csv file storing the elevation for all sample points for each municipality


def print_to_csv_elevation():
    # Load municipality coordinates from the input CSV
    municipalities_data = read_coordinates_from_csv("C:/Users/hakon/SnowAnalysis_JK/stored_data/municipalities_data_points.csv")

    # Define the CSV file path for output
    csv_file_path = os.path.join(folder_path, "municipalities_data_elevation.csv")

    # Open CSV file for writing
    with open(csv_file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # Write header row
        writer.writerow(["Municipality", "Elevation"])

        # Loop through municipalities and write data
        for municipality, coordinates in municipalities_data.items():
            elevation = get_elevations(coordinates)
            writer.writerow([municipality, elevation])
            file.flush()

            print(f'Elevation for {municipality} successfully added') #For debugging
    print(f"CSV file successfully saved to: {csv_file_path}")


#This is the csv file used to plot the map. It contains coordinates and the reliability index

def print_to_csv_map(start_municipality=None):
    # Define the CSV file path
    csv_file_path = os.path.join(folder_path, "municipalities_data_map.csv")
    
    # Determine whether to overwrite or append
    overwrite = start_municipality is None  # If no start point, overwrite
    mode = "w" if overwrite else "a"  # "w" for overwrite, "a" for append
    file_exists = os.path.exists(csv_file_path)
    
    with open(csv_file_path, mode=mode, newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        
        # Write header only if overwriting or if the file is new
        if overwrite or not file_exists:
            writer.writerow(["Municipality", "Latitude", "Longitude", "Beta"])
        
        start_writing = overwrite  # Start from beginning if overwriting
        
        # Loop through municipalities and write data
        for municipality, data in municipalities_data.items():
            if not start_writing:
                if municipality == start_municipality:
                    start_writing = True  # Found the start point, begin writing
            
            if start_writing:
                beta, alpha = municipality_form(municipality)
                writer.writerow([
                    municipality,
                    data["coordinates"]["latitude"],
                    data["coordinates"]["longitude"],
                    beta
                ])
                file.flush()  # Flush after every write
                print(f'Beta for {municipality} successfully added')  # Debugging
    
    print(f"CSV file successfully {'overwritten' if overwrite else 'updated'} at: {csv_file_path}")



#print_to_csv_points()  #Run to update sample points

#print_to_csv_elevation()  #Run to update elevation

#print_to_csv_swe()  #Run to update swe

#print_to_csv_map()  #Run to update map csv file

