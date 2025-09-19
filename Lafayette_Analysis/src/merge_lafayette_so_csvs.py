#!/usr/bin/env python3

import pandas as pd
import os

def merge_lafayette_so_csvs():
    """
    Merge the three Lafayette SO CSV files into one, preserving all columns and data.
    """

    # Define the input files
    input_files = [
        'cprr_lafayette_so_2006_2008.csv',
        'cprr_lafayette_so_2009_2014.csv',
        'cprr_lafayette_so_2015_2020.csv'
    ]

    # List to store dataframes
    dataframes = []

    # Read each CSV file
    for file in input_files:
        if os.path.exists(file):
            print(f"Reading {file}...")
            df = pd.read_csv(file)
            print(f"  - Shape: {df.shape}")
            print(f"  - Columns: {list(df.columns)}")
            dataframes.append(df)
        else:
            print(f"Warning: {file} not found!")

    if not dataframes:
        print("No CSV files found to merge!")
        return

    # Concatenate all dataframes, filling missing columns with NaN
    print("\nMerging dataframes...")
    merged_df = pd.concat(dataframes, ignore_index=True, sort=False)

    print(f"Merged dataframe shape: {merged_df.shape}")
    print(f"Total columns in merged data: {len(merged_df.columns)}")
    print(f"Columns: {list(merged_df.columns)}")

    # Save the merged dataframe
    output_file = 'cprr_lafayette_so_2006_2020.csv'
    merged_df.to_csv(output_file, index=False)
    print(f"\nMerged data saved to: {output_file}")

    # Print summary statistics
    print(f"\nSummary:")
    print(f"- Total rows: {len(merged_df)}")
    print(f"- Total columns: {len(merged_df.columns)}")
    print(f"- Files merged: {len(dataframes)}")

if __name__ == "__main__":
    merge_lafayette_so_csvs()