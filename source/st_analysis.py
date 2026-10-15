"""Descriptive plots of RCSB metadata produced by source/data.py.

Usage:
    python source/st_analysis.py --excel rcsb_statistical_data_enhanced.xlsx
"""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Plot RCSB metadata distributions.")
    parser.add_argument("--excel", type=Path, default=Path("rcsb_statistical_data_enhanced.xlsx"),
                        help="Excel file written by data.py.")
    args = parser.parse_args(argv)

    df = pd.read_excel(args.excel)

    # Display basic statistical summaries of the dataset
    print(df.describe())

    # Convert the 'Release Date' column to datetime format
    df["Release Date"] = pd.to_datetime(df["Release Date"], errors="coerce")

    plt.figure(figsize=(10, 6))
    sns.histplot(df["Molecular Weight"].dropna(), bins=30, kde=True)
    plt.title("Distribution of Molecular Weights")
    plt.xlabel("Molecular Weight")
    plt.ylabel("Frequency")
    plt.show()

    plt.figure(figsize=(10, 6))
    sns.boxplot(x=df["Resolution"].dropna())
    plt.title("Boxplot of Resolution")
    plt.xlabel("Resolution")
    plt.show()

    plt.figure(figsize=(10, 6))
    sns.histplot(df["Resolution"].dropna(), bins=30, kde=True)
    plt.title("Distribution of Resolution")
    plt.xlabel("Resolution")
    plt.ylabel("Frequency")
    plt.show()

    plt.figure(figsize=(10, 6))
    sns.histplot(df["Release Date"].dropna(), bins=30, kde=False)
    plt.title("Distribution of Release Dates")
    plt.xlabel("Release Date")
    plt.ylabel("Frequency")
    plt.xticks(rotation=45)
    plt.show()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
