#!/usr/bin/env python3

import pandas as pd
import os

def find_award_complaint_overlap():
    """
    Find officers who appear in both the award file and complaint file for Lafayette SO.
    """

    # Define file paths
    award_file = '../data/award_lafayette_so_2017_2021.csv'
    complaint_file = '../data/cprr_lafayette_so_2006_2020.csv'

    # Check if files exist
    if not os.path.exists(award_file):
        print(f"Award file not found: {award_file}")
        return

    if not os.path.exists(complaint_file):
        print(f"Complaint file not found: {complaint_file}")
        return

    # Read the files
    print("Reading award file...")
    award_df = pd.read_csv(award_file)
    print(f"Award file shape: {award_df.shape}")
    print(f"Award columns: {list(award_df.columns)}")

    print("\nReading complaint file...")
    complaint_df = pd.read_csv(complaint_file)
    print(f"Complaint file shape: {complaint_df.shape}")
    print(f"Complaint columns: {list(complaint_df.columns)}")

    # Create officer identifiers for comparison
    # Award file: combine first_name + last_name
    award_df['officer_name'] = (award_df['first_name'].str.strip().str.lower() + '_' +
                               award_df['last_name'].str.strip().str.lower())

    # Complaint file: combine first_name + last_name
    complaint_df['officer_name'] = (complaint_df['first_name'].str.strip().str.lower() + '_' +
                                   complaint_df['last_name'].str.strip().str.lower())

    # Get unique officers from each dataset
    award_officers = set(award_df['officer_name'].dropna().unique())
    complaint_officers = set(complaint_df['officer_name'].dropna().unique())

    print(f"\nUnique officers in awards: {len(award_officers)}")
    print(f"Unique officers in complaints: {len(complaint_officers)}")

    # Find overlap
    overlap_officers = award_officers.intersection(complaint_officers)

    print(f"\nOfficers appearing in BOTH awards and complaints: {len(overlap_officers)}")

    if overlap_officers:
        print("\nOfficers with both awards and complaints:")
        print("=" * 50)

        for officer in sorted(overlap_officers):
            # Get details from both datasets
            award_info = award_df[award_df['officer_name'] == officer]
            complaint_info = complaint_df[complaint_df['officer_name'] == officer]

            first_name = award_info['first_name'].iloc[0]
            last_name = award_info['last_name'].iloc[0]

            print(f"\n{first_name.title()} {last_name.title()}:")
            print(f"  Awards: {len(award_info)}")
            print(f"  Complaints: {len(complaint_info)}")

            # Show award details
            for _, award in award_info.iterrows():
                dept = str(award['department_desc']).strip() if pd.notna(award['department_desc']) else 'Unknown'
                print(f"    Award ({award['receive_year']}): {dept}")

            # Show complaint details
            for _, complaint in complaint_info.iterrows():
                year = complaint['receive_year'] if pd.notna(complaint['receive_year']) else 'Unknown'
                disposition = complaint['disposition'] if pd.notna(complaint['disposition']) else 'Unknown'
                allegation = complaint['allegation'] if pd.notna(complaint['allegation']) else 'Unknown'
                print(f"    Complaint ({year}): {disposition} - {allegation}")

    # Summary statistics
    print(f"\n" + "=" * 60)
    print("SUMMARY:")
    print(f"Total officers with awards: {len(award_officers)}")
    print(f"Total officers with complaints: {len(complaint_officers)}")
    print(f"Officers with both: {len(overlap_officers)}")
    print(f"Overlap percentage (of award recipients): {len(overlap_officers)/len(award_officers)*100:.1f}%")
    print(f"Overlap percentage (of complaint subjects): {len(overlap_officers)/len(complaint_officers)*100:.1f}%")

if __name__ == "__main__":
    find_award_complaint_overlap()