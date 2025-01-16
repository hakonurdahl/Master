import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import glob

# Function to escape LaTeX special characters
def latex_escape(s):
    special_chars = {
        '_': r'\_',
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        '\\': r'\textbackslash{}',
    }
    for char, escaped_char in special_chars.items():
        s = s.replace(char, escaped_char)
    return s



# Function to process station_name
def clean_station_name(name):
    # Remove the 'swe_' prefix if it exists
    if name.startswith('swe_'):
        name = name[4:]  # Remove the first 4 characters ('swe_')
    # Replace underscores with spaces
    name = name.replace('_', ' ')
    return name






# Define the input and output directories
input_folder = '/Users/kohlerm2/Documents/SnowAnalysis/Output/Computations/'
output_folder = '/Users/kohlerm2/Documents/SnowAnalysis/Output/Computations/Analysis/'

# Ensure the output directory exists
os.makedirs(output_folder, exist_ok=True)

# Get a list of all CSV files in the input folder
csv_files = glob.glob(os.path.join(input_folder, '*.csv'))

for csv_file in csv_files:
    # Load the data
    data = pd.read_csv(csv_file)

    # Convert 'time' column to datetime
    data['time'] = pd.to_datetime(data['time'])

    # Define water year from July to June
    data['water_year'] = data['time'].apply(lambda x: x.year + 1 if x.month >= 7 else x.year)

    # Filter out data beyond June 30, 2023 to get complete years
    data = data[data['time'] <= '2023-06-30']

    # Find the maximum SWE for each water year
    max_swe_per_year = data.groupby('water_year', as_index=False).apply(
        lambda x: x.loc[x['swe'].idxmax()]
    ).reset_index(drop=True)

    # Exclude incomplete years (e.g., if the first year doesn't start in July)
    first_year = data['water_year'].min()
    if data[data['water_year'] == first_year]['time'].min().month > 7:
        max_swe_per_year = max_swe_per_year[max_swe_per_year['water_year'] != first_year]

    # Extract the station name from the CSV filename
    station_name = os.path.splitext(os.path.basename(csv_file))[0]
    # Clean the station name
    clean_name = clean_station_name(station_name)

    # Create the overall percentile plot with correct color shading
    swe_values = max_swe_per_year['swe'].values
    years = max_swe_per_year['water_year'].values
    

    # Sort SWE values and corresponding years
    sorted_indices = np.argsort(swe_values)
    sorted_swe_values = swe_values[sorted_indices]
    sorted_years = years[sorted_indices]

    n = len(sorted_swe_values)
    percentiles = (np.arange(1, n + 1) - 0.5) / n * 100  # Midpoint method
    
    mean_swe = np.mean(swe_values)
    std_swe = np.std(swe_values)
    
    
    norm = plt.Normalize(years.min(), years.max())

    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(
        sorted_swe_values,
        percentiles,
        c=sorted_years,
        cmap='cool',
        norm=norm
    )

    # Add colorbar with year labels
    cbar = plt.colorbar(scatter, ticks=np.linspace(years.min(), years.max(), num=5).astype(int))
    cbar.ax.set_ylabel('Water Year')
    cbar.ax.set_yticklabels([str(int(year)) for year in np.linspace(years.min(), years.max(), num=5).astype(int)])

    plt.xlabel('Maximum SWE (mm)')
    plt.ylabel('Percentile (%)')
    plt.title(f'Percentile Plot of Maximum SWE per Water Year\n({station_name})')
    plt.grid(True)

    # Save the plot to the output folder with an indicative filename
    output_filename = os.path.join(output_folder, f'percentile_plot_{station_name}.png')
    plt.savefig(output_filename)
    plt.close()  # Close the figure to free memory

    # Now, create the comparison scatter plot
    num_years = len(max_swe_per_year)
    if num_years >= 66:
        # Split the data into first and second 33 years
        sorted_years_unique = np.sort(max_swe_per_year['water_year'].unique())
        first_half_years = sorted_years_unique[:33]
        second_half_years = sorted_years_unique[33:66]

        # Data for the first 33 years
        first_half = max_swe_per_year[max_swe_per_year['water_year'].isin(first_half_years)]
        swe_values_first = np.sort(first_half['swe'].values)
        n_first = len(swe_values_first)
        percentiles_first = np.arange(1, n_first + 1) / (n_first + 1) * 100
        mean_swe1 = np.mean(swe_values_first)
        std_swe1 = np.std(swe_values_first)
        

        # Data for the second 33 years
        second_half = max_swe_per_year[max_swe_per_year['water_year'].isin(second_half_years)]
        swe_values_second = np.sort(second_half['swe'].values)
        n_second = len(swe_values_second)
        percentiles_second = np.arange(1, n_second + 1) / (n_second + 1) * 100
        mean_swe2 = np.mean(swe_values_second)
        std_swe2 = np.std(swe_values_second)
        
        
        # Plot the comparison scatter plot
        plt.figure(figsize=(10, 6))
        plt.scatter(
            swe_values_first,
            percentiles_first,
            color='blue',
            label='First 33 Years',
            alpha=0.7
        )
        plt.scatter(
            swe_values_second,
            percentiles_second,
            color='red',
            label='Second 33 Years',
            alpha=0.7
        )
        plt.xlabel('Maximum SWE (mm)')
        plt.ylabel('Percentile (%)')
        plt.title(f'Comparison of Maximum SWE per Water Year\n({station_name})')
        plt.legend()
        plt.grid(True)

        # Save the comparison plot
        output_filename_comparison = os.path.join(output_folder, f'comparison_plot_{station_name}.png')
        plt.savefig(output_filename_comparison)
        plt.close()
    else:
        print(f"Not enough data to split into two 33-year periods for station {station_name}.")


    ##Create a latex output
    # Round the numbers to 1 decimal place and convert COV to percentage
    mean_swe = round(mean_swe, 1)
    std_swe = round(std_swe, 1)
    cov_swe = round(std_swe/mean_swe, 2)  # Convert to percentage
    
    mean_swe1 = round(mean_swe1, 1)
    std_swe1 = round(std_swe1, 1)
    cov_swe1 = round(std_swe1/mean_swe1, 2) # Convert to percentage
    
    mean_swe2 = round(mean_swe2, 1)
    std_swe2 = round(std_swe2, 1)
    cov_swe2 = round(std_swe2/mean_swe2, 2)  # Convert to percentage
    
    # Escape LaTeX special characters in station_name
    station_name_latex = latex_escape(station_name)
    
    # Create the LaTeX table using f-strings
    latex_table = rf'''
    \begin{{table}}[h!]
        \centering
        \caption{{Sample Statistics for {clean_name}}}
        \begin{{tabular}}{{lccc}} 
            \toprule
            \textbf{{Period}} & \textbf{{Mean SWE (mm)}} & \textbf{{Std Dev (mm)}} & \textbf{{COV (\%)}} \\
            \midrule
            Entire Period & {mean_swe:.1f} & {std_swe:.1f} & {cov_swe:.1f} \\
            First 33 Years & {mean_swe1:.1f} & {std_swe1:.1f} & {cov_swe1:.1f} \\
            Last 33 Years & {mean_swe2:.1f} & {std_swe2:.1f} & {cov_swe2:.1f} \\
            \bottomrule
        \end{{tabular}}
        \label{{tab:sample_stats_{clean_name}}}
    \end{{table}}
    '''
    
    # Define the output filename
    output_filename = os.path.join(output_folder, f'sample_statistics{station_name}.tex')
    
    # Write the LaTeX table to the file
    with open(output_filename, 'w') as f:
        f.write(latex_table)
    




