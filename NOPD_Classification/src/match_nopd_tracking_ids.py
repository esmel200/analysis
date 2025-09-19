#!/usr/bin/env python3

import pandas as pd
import os

def match_nopd_tracking_ids():
    """
    Match tracking_id_og from nopd_cprr_23.csv with:
    - Complaint_ID from pib_annual_cprr_2023.csv
    - tracking_id from skip_gist_2023.csv
    """

    # Define file paths
    nopd_file = '../data/nopd_cprr_23.csv'
    pib_file = '../data/pib_annual_cprr_2023.csv'
    skip_file = '../data/skip_gist_2023.csv'

    # Check if files exist
    for file_path in [nopd_file, pib_file, skip_file]:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return

    print("Loading NOPD data files...")

    # Read the files
    nopd_df = pd.read_csv(nopd_file)
    pib_df = pd.read_csv(pib_file)
    skip_df = pd.read_csv(skip_file)

    print(f"NOPD CPRR 2023: {len(nopd_df)} records")
    print(f"PIB Annual 2023: {len(pib_df)} records")
    print(f"Skip Gist 2023: {len(skip_df)} records")

    print("\nColumns in each file:")
    print(f"NOPD CPRR: {list(nopd_df.columns)}")
    print(f"PIB Annual: {list(pib_df.columns)}")
    print(f"Skip Gist: {list(skip_df.columns)}")

    # Get unique tracking IDs from base file (case-insensitive)
    nopd_tracking_ids = set(str(id).upper() for id in nopd_df['tracking_id_og'].dropna().unique())
    pib_complaint_ids = set(str(id).upper() for id in pib_df['Complaint_ID'].dropna().unique())
    skip_tracking_ids = set(str(id).upper() for id in skip_df['tracking_id'].dropna().unique())

    # Keep original case versions for merging
    nopd_tracking_ids_orig = set(nopd_df['tracking_id_og'].dropna().unique())
    pib_complaint_ids_orig = set(pib_df['Complaint_ID'].dropna().unique())
    skip_tracking_ids_orig = set(skip_df['tracking_id'].dropna().unique())

    print(f"\nUnique IDs in each dataset:")
    print(f"NOPD tracking_id_og: {len(nopd_tracking_ids)} unique")
    print(f"PIB Complaint_ID: {len(pib_complaint_ids)} unique")
    print(f"Skip tracking_id: {len(skip_tracking_ids)} unique")

    # Find matches
    print("\n" + "="*60)
    print("MATCHING ANALYSIS")
    print("="*60)

    # 1. NOPD vs PIB matches
    nopd_pib_matches = nopd_tracking_ids.intersection(pib_complaint_ids)
    print(f"\n1. NOPD tracking_id_og matches with PIB Complaint_ID:")
    print(f"   Matches found: {len(nopd_pib_matches)}")
    print(f"   Match rate: {len(nopd_pib_matches)/len(nopd_tracking_ids)*100:.1f}% of NOPD records")

    # 2. NOPD vs Skip matches
    nopd_skip_matches = nopd_tracking_ids.intersection(skip_tracking_ids)
    print(f"\n2. NOPD tracking_id_og matches with Skip tracking_id:")
    print(f"   Matches found: {len(nopd_skip_matches)}")
    print(f"   Match rate: {len(nopd_skip_matches)/len(nopd_tracking_ids)*100:.1f}% of NOPD records")

    # 3. Three-way matches (all files)
    three_way_matches = nopd_tracking_ids.intersection(pib_complaint_ids).intersection(skip_tracking_ids)
    print(f"\n3. Three-way matches (all files):")
    print(f"   Matches found: {len(three_way_matches)}")
    print(f"   Match rate: {len(three_way_matches)/len(nopd_tracking_ids)*100:.1f}% of NOPD records")

    # Show some example matches
    if nopd_pib_matches:
        print(f"\nExample NOPD-PIB matches:")
        for i, match_id in enumerate(sorted(list(nopd_pib_matches))[:5]):
            print(f"  {i+1}. {match_id}")

    if nopd_skip_matches:
        print(f"\nExample NOPD-Skip matches:")
        for i, match_id in enumerate(sorted(list(nopd_skip_matches))[:5]):
            print(f"  {i+1}. {match_id}")

    if three_way_matches:
        print(f"\nThree-way matches:")
        for i, match_id in enumerate(sorted(list(three_way_matches))[:10]):
            print(f"  {i+1}. {match_id}")

    # Detailed analysis of non-matches
    print(f"\n" + "="*60)
    print("NON-MATCHING ANALYSIS")
    print("="*60)

    # IDs only in NOPD
    nopd_only = nopd_tracking_ids - pib_complaint_ids - skip_tracking_ids
    print(f"\nIDs only in NOPD (not in PIB or Skip): {len(nopd_only)}")
    if nopd_only:
        print("Examples:")
        for i, id_val in enumerate(sorted(list(nopd_only))[:5]):
            print(f"  {i+1}. {id_val}")

    # IDs only in PIB
    pib_only = pib_complaint_ids - nopd_tracking_ids - skip_tracking_ids
    print(f"\nIDs only in PIB (not in NOPD or Skip): {len(pib_only)}")
    if pib_only:
        print("Examples:")
        for i, id_val in enumerate(sorted(list(pib_only))[:5]):
            print(f"  {i+1}. {id_val}")

    # IDs only in Skip
    skip_only = skip_tracking_ids - nopd_tracking_ids - pib_complaint_ids
    print(f"\nIDs only in Skip (not in NOPD or PIB): {len(skip_only)}")
    if skip_only:
        print("Examples:")
        for i, id_val in enumerate(sorted(list(skip_only))[:5]):
            print(f"  {i+1}. {id_val}")

    # Create merged dataset for matches
    if three_way_matches:
        print(f"\n" + "="*60)
        print("CREATING MERGED DATASET")
        print("="*60)

        # Create mapping dictionaries for case-insensitive matching
        nopd_id_map = {str(id).upper(): id for id in nopd_df['tracking_id_og'].dropna()}
        pib_id_map = {str(id).upper(): id for id in pib_df['Complaint_ID'].dropna()}
        skip_id_map = {str(id).upper(): id for id in skip_df['tracking_id'].dropna()}

        # Get original case versions of matching IDs
        three_way_matches_list = list(three_way_matches)

        # Filter to only matching records using original case
        nopd_orig_matches = [nopd_id_map[match_id] for match_id in three_way_matches_list if match_id in nopd_id_map]
        pib_orig_matches = [pib_id_map[match_id] for match_id in three_way_matches_list if match_id in pib_id_map]
        skip_orig_matches = [skip_id_map[match_id] for match_id in three_way_matches_list if match_id in skip_id_map]

        nopd_matched = nopd_df[nopd_df['tracking_id_og'].isin(nopd_orig_matches)].copy()
        pib_matched = pib_df[pib_df['Complaint_ID'].isin(pib_orig_matches)].copy()
        skip_matched = skip_df[skip_df['tracking_id'].isin(skip_orig_matches)].copy()

        # Add normalized ID column for merging
        nopd_matched['tracking_id_normalized'] = nopd_matched['tracking_id_og'].str.upper()
        pib_matched['tracking_id_normalized'] = pib_matched['Complaint_ID'].str.upper()
        skip_matched['tracking_id_normalized'] = skip_matched['tracking_id'].str.upper()

        # Merge on normalized tracking_id
        merged_df = nopd_matched.merge(pib_matched, on='tracking_id_normalized', how='inner', suffixes=('_nopd', '_pib'))
        merged_df = merged_df.merge(skip_matched, on='tracking_id_normalized', how='inner', suffixes=('', '_skip'))

        print(f"Merged dataset created with {len(merged_df)} records")
        print(f"Columns in merged dataset: {len(merged_df.columns)}")

        # Save merged dataset
        os.makedirs('../output', exist_ok=True)
        merged_df.to_csv('../output/nopd_merged_2023.csv', index=False)
        print(f"Merged dataset saved to: ../output/nopd_merged_2023.csv")

        # Show summary of merged data
        print(f"\nMerged dataset summary:")
        print(f"- Total records: {len(merged_df)}")
        print(f"- Unique tracking IDs: {merged_df['tracking_id_normalized'].nunique()}")
        print(f"- Date range: {merged_df.get('Received_Date', 'N/A').min() if 'Received_Date' in merged_df.columns else 'N/A'} to {merged_df.get('Received_Date', 'N/A').max() if 'Received_Date' in merged_df.columns else 'N/A'}")

        # Show some example merged records
        print(f"\nExample merged records:")
        for i, (_, row) in enumerate(merged_df.head(3).iterrows()):
            print(f"  {i+1}. {row['tracking_id_og']} -> {row['Complaint_ID']} -> {row.get('tracking_id', 'N/A')}")
            print(f"     NOPD: {row.get('allegation', 'N/A')}")
            print(f"     PIB: {row.get('Summary', 'N/A')[:100]}...")
            print(f"     Skip: {row.get('gist', 'N/A')[:100]}...")
            print()

    # Summary statistics
    print(f"\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)

    total_unique_ids = len(nopd_tracking_ids.union(pib_complaint_ids).union(skip_tracking_ids))

    print(f"Total unique tracking IDs across all files: {total_unique_ids}")
    print(f"Coverage by file:")
    print(f"  NOPD: {len(nopd_tracking_ids)/total_unique_ids*100:.1f}%")
    print(f"  PIB: {len(pib_complaint_ids)/total_unique_ids*100:.1f}%")
    print(f"  Skip: {len(skip_tracking_ids)/total_unique_ids*100:.1f}%")

    print(f"\nOverlap analysis:")
    print(f"  NOPD-PIB overlap: {len(nopd_pib_matches)/min(len(nopd_tracking_ids), len(pib_complaint_ids))*100:.1f}%")
    print(f"  NOPD-Skip overlap: {len(nopd_skip_matches)/min(len(nopd_tracking_ids), len(skip_tracking_ids))*100:.1f}%")
    print(f"  PIB-Skip overlap: {len(pib_complaint_ids.intersection(skip_tracking_ids))/min(len(pib_complaint_ids), len(skip_tracking_ids))*100:.1f}%")

    # Pattern analysis
    print(f"\n" + "="*60)
    print("ID PATTERN ANALYSIS")
    print("="*60)

    # Analyze ID formats
    nopd_sample = list(nopd_tracking_ids)[:5]
    pib_sample = list(pib_complaint_ids)[:5]
    skip_sample = list(skip_tracking_ids)[:5]

    print(f"Sample ID formats:")
    print(f"  NOPD: {nopd_sample}")
    print(f"  PIB:  {pib_sample}")
    print(f"  Skip: {skip_sample}")

    # Check for common patterns
    if nopd_tracking_ids:
        nopd_pattern = list(nopd_tracking_ids)[0]
        print(f"\nCommon patterns:")
        print(f"  NOPD format appears to be: YYYY-NNNN-X (e.g., {nopd_pattern})")

        # Count by suffix type in NOPD
        suffixes = {}
        for track_id in nopd_tracking_ids:
            if isinstance(track_id, str) and len(track_id) > 0:
                suffix = track_id.split('-')[-1] if '-' in track_id else 'Unknown'
                suffixes[suffix] = suffixes.get(suffix, 0) + 1

        print(f"  NOPD suffix distribution:")
        for suffix, count in sorted(suffixes.items()):
            print(f"    -{suffix}: {count} cases")

if __name__ == "__main__":
    match_nopd_tracking_ids()