#!/usr/bin/env python3
"""
Combine four BRPD CSV files from 2004-2023 into one dataset and remove duplicates.
"""

import pandas as pd
import os
from pathlib import Path

def combine_brpd_csvs():
    """Combine the four BRPD CSV files and remove duplicates."""

    # Define file paths
    base_path = Path('/Users/esmelee/analysis/Baton_Rouge_Analysis')
    files = [
        'cprr_baton_rouge_pd_2004_2009.csv',
        'cprr_baton_rouge_pd_2018.csv',
        'cprr_baton_rouge_pd_2021.csv',
        'cprr_baton_rouge_pd_2021_2023.csv'
    ]

    dataframes = []
    total_rows_before = 0

    print("Loading and examining each file...\n")

    for file in files:
        file_path = base_path / file
        if file_path.exists():
            df = pd.read_csv(file_path)
            total_rows_before += len(df)
            print(f"{file}:")
            print(f"  Rows: {len(df)}")
            print(f"  Columns: {len(df.columns)}")
            print(f"  Date range: {df.get('occur_year', pd.Series()).min()}-{df.get('occur_year', pd.Series()).max()}")
            dataframes.append(df)
        else:
            print(f"Warning: {file} not found")

    if not dataframes:
        print("Error: No CSV files found!")
        return

    print(f"\nTotal rows before combining: {total_rows_before}")

    # Get all unique columns across all files
    all_columns = set()
    for df in dataframes:
        all_columns.update(df.columns)

    print(f"Total unique columns across all files: {len(all_columns)}")

    # Standardize all dataframes to have the same columns
    standardized_dfs = []
    for i, df in enumerate(dataframes):
        # Add missing columns with NaN values
        for col in all_columns:
            if col not in df.columns:
                df[col] = pd.NA

        # Reorder columns consistently
        df = df.reindex(sorted(all_columns), axis=1)
        standardized_dfs.append(df)
        print(f"File {i+1} standardized: {len(df)} rows, {len(df.columns)} columns")

    # Combine all dataframes
    print("\nCombining all files...")
    combined_df = pd.concat(standardized_dfs, ignore_index=True)
    print(f"Combined dataset: {len(combined_df)} rows, {len(combined_df.columns)} columns")

    # Remove exact duplicates
    print("\nRemoving duplicate rows...")
    initial_count = len(combined_df)
    combined_df = combined_df.drop_duplicates()
    duplicates_removed = initial_count - len(combined_df)
    print(f"Removed {duplicates_removed} duplicate rows")
    print(f"Final dataset: {len(combined_df)} rows")

    # Check for potential duplicates based on key fields
    if 'uid' in combined_df.columns and 'allegation_uid' in combined_df.columns:
        print("\nChecking for logical duplicates (same uid + allegation_uid)...")
        logical_duplicates = combined_df[combined_df.duplicated(subset=['uid', 'allegation_uid'], keep=False)]
        if len(logical_duplicates) > 0:
            print(f"Found {len(logical_duplicates)} rows with duplicate uid+allegation_uid combinations")
            # Remove logical duplicates, keeping the first occurrence
            combined_df = combined_df.drop_duplicates(subset=['uid', 'allegation_uid'], keep='first')
            print(f"After removing logical duplicates: {len(combined_df)} rows")

    # Sort by year and date for consistency
    if 'occur_year' in combined_df.columns:
        sort_cols = ['occur_year']
        if 'occur_month' in combined_df.columns:
            sort_cols.append('occur_month')
        if 'occur_day' in combined_df.columns:
            sort_cols.append('occur_day')

        combined_df = combined_df.sort_values(sort_cols, na_position='last')
        print("Data sorted by occurrence date")

    # Save the combined dataset
    output_path = base_path / 'cprr_baton_rouge_pd_2004_2023_combined.csv'
    combined_df.to_csv(output_path, index=False)
    print(f"\nCombined dataset saved to: {output_path}")

    # Generate summary statistics
    print("\n" + "="*60)
    print("BATON ROUGE PD COMBINED DATASET SUMMARY")
    print("="*60)
    print(f"Total records: {len(combined_df)}")
    print(f"Date range: {combined_df['occur_year'].min()}-{combined_df['occur_year'].max()}")
    print(f"Total columns: {len(combined_df.columns)}")

    # Count by year
    if 'occur_year' in combined_df.columns:
        year_counts = combined_df['occur_year'].value_counts().sort_index()
        print(f"\nRecords by year:")
        for year, count in year_counts.items():
            if pd.notna(year):
                print(f"  {int(year)}: {count}")

    # Top allegations
    if 'allegation' in combined_df.columns:
        print(f"\nTop 10 allegations:")
        allegation_counts = combined_df['allegation'].value_counts().head(10)
        for allegation, count in allegation_counts.items():
            if pd.notna(allegation):
                print(f"  {allegation}: {count}")

    # Dispositions
    if 'disposition' in combined_df.columns:
        print(f"\nDispositions:")
        disposition_counts = combined_df['disposition'].value_counts()
        for disposition, count in disposition_counts.items():
            if pd.notna(disposition):
                print(f"  {disposition}: {count}")

    print(f"\nData cleaning completed successfully!")
    return output_path

if __name__ == "__main__":
    combine_brpd_csvs()