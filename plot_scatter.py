import pandas as pd
import ast
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression



def scatter_gumbel(time):
    # File paths
    beta_file = f"stored_data/beta_{time}.csv"
    swe_file = f"stored_data/swe_{time}.csv"

    output_folder = f"/Users/hakon/SnowAnalysis_HU/Output/main_output/"
    output_mean_file = output_folder + f"mean_scatter_{time}.png"
    output_cov_file = output_folder + f"cov_scatter_{time}.png"

    # Load data
    beta_df = pd.read_csv(beta_file)
    swe_df = pd.read_csv(swe_file)

    # Set Municipality as index
    beta_df.set_index("municipality", inplace=True)
    swe_df.set_index("municipality", inplace=True)

    # Convert SWE column from string to list
    def parse_swe(value):
        try:
            return ast.literal_eval(value) if isinstance(value, str) else value
        except (SyntaxError, ValueError):
            return []

    swe_df["swe"] = swe_df["swe"].apply(parse_swe)

    # Constants
    GAMMA = 0.57722  # Euler-Mascheroni constant

    # Compute Gumbel mean and CoV
    def compute_gumbel_params(swe_list):

        if np.sum(swe_list)<10:
            loc, scale = 0.01, 0.01
        else:
            loc, scale = stats.gumbel_r.fit(swe_list)

        gamma = 0.57722  

        # Compute mean and standard deviation
        mean_gumbel = loc + gamma * scale
        std_gumbel = (np.pi / np.sqrt(6)) * scale
        mean_snow_=mean_gumbel*9.8*2/1000 # Converting mm to kN/m

        # Compute CoV
        cov_snow = std_gumbel / mean_gumbel
        
        return mean_snow_, cov_snow


    swe_df[["SWE_Gumbel_Mean", "SWE_Gumbel_CoV"]] = swe_df["swe"].apply(lambda x: pd.Series(compute_gumbel_params(x)))

    # Merge datasets
    merged_df = swe_df.join(beta_df, how="inner").dropna(subset=["SWE_Gumbel_Mean", "SWE_Gumbel_CoV", "var"])

    # === Plot 1: Reliability vs. Gumbel Mean ===
    plt.figure(figsize=(8, 6))
    plt.scatter(
        merged_df["SWE_Gumbel_Mean"],
        merged_df["var"],
        s=20,
        alpha=1
    )
    plt.axhline(y=3.8, color='red', linestyle='dashed', linewidth=1.5, label="Reliability target = 3.8")
    plt.xlabel("Gumbel Mean of SWE", fontsize=20)
    plt.ylabel("Reliability Index", fontsize=20)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.title("Reliability Index vs. Gumbel Mean of SWE", fontsize=20)
    plt.grid(True)
    plt.legend(fontsize=20)
    plt.savefig(output_mean_file, format="png", bbox_inches="tight")
    print(f"Mean plot saved successfully at: {output_mean_file}")

    # === Remove effect of Mean ===
    X_mean = merged_df[["SWE_Gumbel_Mean"]]
    y_reliability = merged_df["var"]

    model_mean = LinearRegression()
    model_mean.fit(X_mean, y_reliability)
    merged_df["Residual_Reliability"] = y_reliability - model_mean.predict(X_mean)

    # === Plot 2: Residual Reliability vs. CoV (No Grouping, Matched Style) ===
    plt.figure(figsize=(8, 6))
    plt.scatter(
        merged_df["SWE_Gumbel_CoV"],
        merged_df["Residual_Reliability"],
        s=20,
        alpha=1
    )

    plt.xlabel("Gumbel Coefficient of Variation (CoV)", fontsize=20)
    plt.ylabel("Residual Reliability Index", fontsize=20)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.title("Residual Reliability vs. CoV of SWE", fontsize=20)
    plt.grid(True)
    plt.savefig(output_cov_file, format="png", bbox_inches="tight")
    #plt.show()

    print(f"CoV plot saved successfully at: {output_cov_file}")



import seaborn as sns

def scatter_char_box(time):
    # Load data
    ec_path = f"/Users/hakon/SnowAnalysis_HU/stored_data/char_ec.csv"
    opt_path = f"/Users/hakon/SnowAnalysis_HU/stored_data/opt_char_{time}.csv"
    output_path = f"/Users/hakon/SnowAnalysis_HU/Output/main_output/scatter_char_box_{time}.png"

    ec_df = pd.read_csv(ec_path)
    opt_df = pd.read_csv(opt_path)

    # Set Municipality as index
    ec_df.set_index("municipality", inplace=True)
    opt_df.set_index("municipality", inplace=True)

    # Merge with suffixes
    merged_df = ec_df.join(opt_df, how="inner", lsuffix="_EC", rsuffix="_opt")
    merged_df.rename(columns={"var_EC": "Char_EC", "var_opt": "Char_opt"}, inplace=True)

    # Drop missing values
    merged_df.dropna(subset=["Char_EC", "Char_opt"], inplace=True)

    # Convert Char_EC to categorical (grouping for boxplot)
    merged_df["Char_EC"] = merged_df["Char_EC"].round(2)  # optional: round to avoid tiny floating differences

    # Plot
    plt.figure(figsize=(10, 6))
    sns.boxplot(x="Char_EC", y="Char_opt", data=merged_df, palette="Set3")

    # Add 1:1 line
    unique_ec = sorted(merged_df["Char_EC"].unique())
    tick_positions = range(len(unique_ec))
    plt.plot(tick_positions, unique_ec, linestyle="--", color="gray", label="1:1 Line")
    plt.legend()


    plt.xlabel("Prescribed Characteristic Value", fontsize=14)
    plt.ylabel("Optimal Characteristic Value", fontsize=14)
    plt.title("Distribution of Optimal Values by Prescribed Characteristic Value", fontsize=16)
    plt.grid(True, axis='y')
    plt.tight_layout()
    plt.savefig(output_path, format="png", bbox_inches="tight")
    #plt.show()

    print(f"Plot saved to: {output_path}")


def scatter_char_violin(time):
    # Load data
    ec_path = f"/Users/hakon/SnowAnalysis_HU/stored_data/char_ec.csv"
    opt_path = f"/Users/hakon/SnowAnalysis_HU/stored_data/opt_char_{time}.csv"
    output_path = f"/Users/hakon/SnowAnalysis_HU/Output/main_output/scatter_char_violin_{time}.png"

    ec_df = pd.read_csv(ec_path)
    opt_df = pd.read_csv(opt_path)

    # Set Municipality as index
    ec_df.set_index("municipality", inplace=True)
    opt_df.set_index("municipality", inplace=True)

    # Merge with suffixes
    merged_df = ec_df.join(opt_df, how="inner", lsuffix="_EC", rsuffix="_opt")
    merged_df.rename(columns={"var_EC": "Char_EC", "var_opt": "Char_opt"}, inplace=True)

    # Drop missing values
    merged_df.dropna(subset=["Char_EC", "Char_opt"], inplace=True)

    # Convert Char_EC to categorical (grouping for violin plot)
    merged_df["Char_EC"] = merged_df["Char_EC"].round(2)

    # Plot
    plt.figure(figsize=(10, 6))
    sns.violinplot(x="Char_EC", y="Char_opt", data=merged_df, palette="Set3", inner="box")

    # Add 1:1 line
    unique_ec = sorted(merged_df["Char_EC"].unique())
    tick_positions = range(len(unique_ec))
    plt.plot(tick_positions, unique_ec, linestyle="--", color="gray", label="1:1 Line")
    plt.legend()

    plt.xlabel("Prescribed Characteristic Value", fontsize=14)
    plt.ylabel("Optimal Characteristic Value", fontsize=14)
    plt.title("Distribution of Optimal Values by Prescribed Characteristic Value", fontsize=16)
    plt.grid(True, axis='y')
    plt.tight_layout()
    plt.savefig(output_path, format="png", bbox_inches="tight")
    #plt.show()

    print(f"Plot saved to: {output_path}")


    


#Test
#scatter_char_box("tot")
#scatter_char_violin("tot")