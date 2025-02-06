import csv
import os
from municipalities_test import municipalities_data
from elevation_points import samples
from elevation import get_elevations
from measurements import measurements
import ast
from FORM import municipality_form

# Write all information to csv file that is to be used in plot_map.py. Since there are many operations in this calculation that takes a lot of data power,
# the calculations are done step by step and stored in csv files.

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
        
        # Loop through municipalities and write data
        for municipality, data in municipalities_data.items():

            swe=measurements(municipality)  

            # Join SWE values with commas
            swe = measurements(municipality)

            writer.writerow([municipality, repr(swe.tolist())])

    print(f"CSV file successfully saved to: {csv_file_path}")

#This is a csv file storing all the points that falls within the square kilometer of the measurement


def print_to_csv_points():
    # Define the CSV file path
    csv_file_path = os.path.join(folder_path, "municipalities_data_points.csv")


    # Open CSV file for writing
    with open(csv_file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        
        # Write header row
        writer.writerow(["Municipality", "Points"])
        
        # Loop through municipalities and write data
        for municipality, data in municipalities_data.items():

            points=samples(municipality)  

            writer.writerow([
                municipality,                
                points
            ])

    print(f"CSV file successfully saved to: {csv_file_path}")


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

    print(f"CSV file successfully saved to: {csv_file_path}")


#This is the csv file used to plot the map. It contains coordinates and the reliability index

def print_to_csv_map():
    # Define the CSV file path
    csv_file_path = os.path.join(folder_path, "municipalities_data_map.csv")


    # Open CSV file for writing
    with open(csv_file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        
        # Write header row
        writer.writerow(["Municipality", "Latitude", "Longitude", "Beta"])
        
        # Loop through municipalities and write data
        for municipality, data in municipalities_data.items():
            
            beta, alpha = municipality_form(municipality)


            writer.writerow([
                municipality,
                data["coordinates"]["latitude"],
                data["coordinates"]["longitude"],
                beta
            ])

    print(f"CSV file successfully saved to: {csv_file_path}")


#print_to_csv_points()  #Run to update sample points

#print_to_csv_elevation()  #Run to update elevation

#print_to_csv_swe()  #Run to update swe

print_to_csv_map()  #Run to update map csv file

