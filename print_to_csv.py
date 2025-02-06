import csv
import os
from municipalities import municipalities_data
#from FORM import form

#Write all information to csv file that is to be used in plot_map.py

# Define the folder path (modify this to match your folder structure)
folder_path = "C:/Users/hakon/OneDrive/Dokumenter/Skole/Master/Code_updated/Haakon"



os.makedirs(folder_path, exist_ok=True)  # Ensure the directory exists

# Define the CSV file path
csv_file_path = os.path.join(folder_path, "municipalities_data.csv")


# Open CSV file for writing
with open(csv_file_path, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    
    # Write header row
    writer.writerow(["Municipality", "sk_0", "hg", "dsk", "sk_maks", "Latitude", "Longitude", "Beta"])
    
    # Loop through municipalities and write data
    for municipality, data in municipalities_data.items():
        #beta = form(municipality)

        beta=4  #tentative

        writer.writerow([
            municipality,
            data["sk_0"],
            data["hg"],
            data["dsk"],
            data["sk_maks"],
            data["coordinates"]["latitude"],
            data["coordinates"]["longitude"],
            beta
        ])

print(f"CSV file successfully saved to: {csv_file_path}")


