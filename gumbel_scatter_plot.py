import pandas as pd
import ast
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

# File paths
beta_file = r"stored_data/municipalities_data_map_new.csv"  
swe_file = r"stored_data/municipalities_data_swe_new.csv"  
output_folder = r"/Users/hakon/SnowAnalysis_JK/Output/ForMaster/"  
output_mean_file = output_folder + "reliability_vs_gumbel_mean_new.pdf"
output_cov_file = output_folder + "reliability_vs_gumbel_cov_new.pdf"

# Load data
beta_df = pd.read_csv(beta_file)
swe_df = pd.read_csv(swe_file)

# Set Municipality as index
beta_df.set_index("Municipality", inplace=True)
swe_df.set_index("Municipality", inplace=True)

# Convert SWE column (from string representation of a list to an actual list)
def parse_swe(value):
    try:
        return ast.literal_eval(value) if isinstance(value, str) else value
    except (SyntaxError, ValueError):
        return []  # Return empty list if parsing fails

swe_df["SWE"] = swe_df["SWE"].apply(parse_swe)

# Constants
GAMMA = 0.57722  # Euler-Mascheroni constant

# Compute Gumbel mean and CoV
def compute_gumbel_params(swe_list):
    if not swe_list or len(swe_list) < 2:  # Need at least 2 points to fit a distribution
        return None, None
    loc, scale = stats.gumbel_r.fit(swe_list)  # Fit Gumbel distribution
    mean_gumbel = loc + GAMMA * scale  # Compute mean
    std_gumbel = np.pi * scale / np.sqrt(6)  # Standard deviation formula for Gumbel
    cov_snow = std_gumbel / mean_gumbel if mean_gumbel != 0 else None  # Compute CoV
    return mean_gumbel, cov_snow

# Apply function to compute mean and CoV
swe_df[["SWE_Gumbel_Mean", "SWE_Gumbel_CoV"]] = swe_df["SWE"].apply(lambda x: pd.Series(compute_gumbel_params(x)))

# Merge datasets
merged_df = swe_df.join(beta_df, how="inner").dropna(subset=["SWE_Gumbel_Mean", "SWE_Gumbel_CoV", "Beta"])

### PLOT 1: Mean of Gumbel Distribution ###
plt.figure(figsize=(8, 6))
scatter_mean = plt.scatter(
    merged_df["SWE_Gumbel_Mean"], 
    merged_df["Beta"], 
    #c=merged_df["Beta"],  # Color by Beta
    #cmap="RdYlGn", 
    #edgecolors="black", 
    s=20,  # Smaller point size
    alpha=1
)
#plt.colorbar(scatter_mean)
plt.axhline(y=3.8, color='red', linestyle='dashed', linewidth=1.5, label="Reliability target = 3.8")
plt.xlabel("Gumbel Mean of SWE", fontsize=15)
plt.ylabel("Reliability Index", fontsize=15)
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
plt.title("Reliability Index vs. Gumbel Mean of SWE", fontsize=20)
plt.grid(True)
plt.legend(fontsize=15)
plt.savefig(output_mean_file, format="pdf", bbox_inches="tight")
#plt.show()
print(f"Mean plot saved successfully at: {output_mean_file}")

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# --- Assuming merged_df is already created as per your existing pipeline ---

# Categorize 'SWE_Gumbel_Mean' into 3 bins
# Categorize 'SWE_Gumbel_Mean' into new bins: 0-200, 201-700, >700
# --- CATEGORIZATION OF GUMBEL MEANS INTO SPECIFIED GROUPS (0-100, 101-350, >350) ---

# --- CATEGORIZATION OF GUMBEL MEANS INTO SPECIFIED GROUPS (0-100, 101-350, >350) ---

# Define the mean groups
def mean_category(mean_value):
    if mean_value <= 100:
        return "0-100"
    elif 100 < mean_value <= 350:
        return "101-350"
    else:
        return ">350"

# Apply categorization to create a new column
merged_df["Mean_Group"] = merged_df["SWE_Gumbel_Mean"].apply(mean_category)

# Define color mapping for groups (with ">350" as black)
color_map = {
    "0-100": "blue",
    "101-350": "green",
    ">350": "black"  # Changed from red to black
}

# Map colors to groups
colors = merged_df["Mean_Group"].map(color_map)

### --- PLOT: CoV of Gumbel Distribution with color by Mean Groups and Solid Trendlines --- ###
plt.figure(figsize=(10, 7))

# Scatter plot colored by groups
scatter_cov = plt.scatter(
    merged_df["SWE_Gumbel_CoV"], 
    merged_df["Beta"], 
    c=colors,
    s=50,  # Size of points
    alpha=0.8,
    edgecolors='black'
)

# Add reference line for Reliability target (keep dashed line)
plt.axhline(y=3.8, color='red', linestyle='dashed', linewidth=1.5, label="Reliability target = 3.8")

# --- ADD SOLID TRENDLINES FOR EACH GROUP WITHOUT ADDING TO LEGEND ---
for group, color in color_map.items():
    group_df = merged_df[merged_df["Mean_Group"] == group]
    if not group_df.empty:
        # Linear regression
        slope, intercept = np.polyfit(group_df["SWE_Gumbel_CoV"], group_df["Beta"], 1)
        x_vals = np.array([group_df["SWE_Gumbel_CoV"].min(), group_df["SWE_Gumbel_CoV"].max()])
        y_vals = intercept + slope * x_vals
        plt.plot(x_vals, y_vals, color=color, linewidth=2)  # Solid line, no label to avoid adding to legend

# Labels and title
plt.xlabel("Gumbel Coefficient of Variation (CoV)", fontsize=15)
plt.ylabel("Reliability Index", fontsize=15)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.title("Reliability Index vs. Gumbel CoV of SWE\nColored by Gumbel Mean Groups", fontsize=18)
plt.grid(True)

# --- CUSTOM LEGEND (ONLY POINT GROUPS AND RELIABILITY LINE) ---
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='o', color='w', label='Mean: 0-100', markerfacecolor='blue', markersize=10, markeredgecolor='black'),
    Line2D([0], [0], marker='o', color='w', label='Mean: 101-350', markerfacecolor='green', markersize=10, markeredgecolor='black'),
    Line2D([0], [0], marker='o', color='w', label='Mean: >350', markerfacecolor='black', markersize=10, markeredgecolor='black'),
    Line2D([0], [0], color='red', lw=2, linestyle='--', label='Reliability target = 3.8')
]

plt.legend(handles=legend_elements, fontsize=12, loc='best')

# Save figure
plt.savefig(output_cov_file, format="pdf", bbox_inches="tight")
plt.show()

print(f"CoV plot saved successfully at: {output_cov_file}")
