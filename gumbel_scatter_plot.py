import pandas as pd
import ast
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

# File paths
beta_file = r"stored_data/municipalities_data_map.csv"  
swe_file = r"stored_data/municipalities_data_swe.csv"  
output_folder = r"/Users/hakon/SnowAnalysis_JK/Output/ForMaster/"  
output_mean_file = output_folder + "reliability_vs_gumbel_mean.pdf"
output_cov_file = output_folder + "reliability_vs_gumbel_cov.pdf"

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
    c=merged_df["Beta"],  # Color by Beta
    cmap="RdYlGn", 
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

### PLOT 2: CoV of Gumbel Distribution ###
plt.figure(figsize=(8, 6))
scatter_cov = plt.scatter(
    merged_df["SWE_Gumbel_CoV"], 
    merged_df["Beta"], 
    c=merged_df["Beta"],  
    cmap="RdYlGn",  
    #edgecolors="black", 
    s=20,  
    alpha=1
)
#plt.colorbar(scatter_cov)
plt.axhline(y=3.8, color='red', linestyle='dashed', linewidth=1.5, label="Reliability target = 3.8")
plt.xlabel("Gumbel Coefficient of Variation (CoV)", fontsize=15)
plt.ylabel("Reliability Index", fontsize=15)
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
plt.title("Reliability Index vs. Gumbel CoV of SWE", fontsize=20)
plt.grid(True)
plt.legend(fontsize=15)
plt.savefig(output_cov_file, format="pdf", bbox_inches="tight")
plt.show()
print(f"CoV plot saved successfully at: {output_cov_file}")
