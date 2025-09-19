#!/usr/bin/env python3
"""
Script to separate NOPD Stop and Search data by year and type (stops vs searches)
"""

import pandas as pd
import os
from datetime import datetime
import argparse

def main():
    # File paths
    input_file = "Stop_and_Search_(Field_Interviews)_20250918.csv"

    print(f"Loading data from {input_file}...")

    # Read the CSV file
    df = pd.read_csv(input_file)
    print(f"Total records loaded: {len(df):,}")

    # Convert EventDate to datetime
    df['EventDate'] = pd.to_datetime(df['EventDate'])
    df['Year'] = df['EventDate'].dt.year

    # Show year distribution
    year_counts = df['Year'].value_counts().sort_index()
    print(f"\nYear distribution:")
    for year, count in year_counts.items():
        print(f"  {year}: {count:,} records")

    # Create separate dataframes for stops and searches
    # Search records: those with "Search Occurred: Yes"
    search_df = df[df['ActionsTaken'].str.contains('Search Occurred: Yes', na=False)].copy()
    # Stop records: all others (includes "Search Occurred: No" and any others)
    stop_df = df[~df['ActionsTaken'].str.contains('Search Occurred: Yes', na=False)].copy()

    print(f"\nRecord type distribution:")
    print(f"  Stop records: {len(stop_df):,}")
    print(f"  Search records: {len(search_df):,}")

    # Create output directories
    stop_dir = "stops_by_year"
    search_dir = "searches_by_year"
    os.makedirs(stop_dir, exist_ok=True)
    os.makedirs(search_dir, exist_ok=True)

    # Process each year
    years = sorted(df['Year'].unique())

    for year in years:
        if pd.isna(year):
            continue

        year = int(year)
        print(f"\nProcessing year {year}...")

        # Filter data for this year
        year_stop_df = stop_df[stop_df['Year'] == year]
        year_search_df = search_df[search_df['Year'] == year]

        # Save stop data for this year
        if not year_stop_df.empty:
            stop_filename = f"{stop_dir}/nopd_stops_{year}.csv"
            year_stop_df.to_csv(stop_filename, index=False)
            print(f"  Saved {len(year_stop_df):,} stop records to {stop_filename}")

        # Save search data for this year
        if not year_search_df.empty:
            search_filename = f"{search_dir}/nopd_searches_{year}.csv"
            year_search_df.to_csv(search_filename, index=False)
            print(f"  Saved {len(year_search_df):,} search records to {search_filename}")

    # Create summary report
    summary_filename = "nopd_data_separation_summary.txt"
    with open(summary_filename, 'w') as f:
        f.write(f"NOPD Stop and Search Data Separation Summary\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Source file: {input_file}\n\n")

        f.write(f"Total records processed: {len(df):,}\n")
        f.write(f"Stop records: {len(stop_df):,}\n")
        f.write(f"Search records: {len(search_df):,}\n\n")

        f.write("Year-by-year breakdown:\n")
        for year in years:
            if pd.isna(year):
                continue
            year = int(year)
            year_stops = len(stop_df[stop_df['Year'] == year])
            year_searches = len(search_df[search_df['Year'] == year])
            f.write(f"  {year}: {year_stops:,} stops, {year_searches:,} searches\n")

    print(f"\nSummary report saved to {summary_filename}")
    print(f"\nData separation complete!")
    print(f"Stop files saved in: {stop_dir}/")
    print(f"Search files saved in: {search_dir}/")

if __name__ == "__main__":
    main()