#!/usr/bin/env python3

import pandas as pd
import os

def check_bias_complaints_in_merged():
    """
    Check if notable bias complaints from PIB data appear in the NOPD merged dataset
    and examine their allegation_desc values for bias-free policing content
    """

    # File paths
    bias_file = '../output/bias_complaints_2023.csv'
    merged_file = '../output/nopd_merged_2023.csv'

    # Check if files exist
    for file_path in [bias_file, merged_file]:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return

    print("Loading bias complaints and NOPD merged data...")

    # Read the datasets
    bias_df = pd.read_csv(bias_file)
    merged_df = pd.read_csv(merged_file)

    print(f"Bias complaints: {len(bias_df)} records")
    print(f"NOPD merged: {len(merged_df)} records")

    # Get the notable examples mentioned in previous analysis
    notable_examples = [
        '2023-0316-P',  # Vehicle towing with alleged racial bias
        '2023-0651-P',  # Officer dismissiveness attributed to racial bias
        '2023-0604-P',  # Crash report issues involving discrimination claims
        '2023-0228-P',  # Officer was aggressive, harassment/targeted
        '2023-0392-P'   # Officer acted rudely during harassment report
    ]

    print(f"\nColumns in merged dataset: {list(merged_df.columns)}")
    print(f"Sample allegation_desc values:")
    if 'allegation_desc' in merged_df.columns:
        unique_allegations = merged_df['allegation_desc'].dropna().unique()
        for i, allegation in enumerate(unique_allegations[:10]):
            print(f"  {i+1}. {allegation}")
        print(f"  ... and {len(unique_allegations) - 10} more" if len(unique_allegations) > 10 else "")
    else:
        print("  No 'allegation_desc' column found in merged dataset")

    print("\n" + "="*60)
    print("BIAS COMPLAINTS IN MERGED DATASET ANALYSIS")
    print("="*60)

    # Check which bias complaints appear in merged dataset
    merged_complaint_ids = set()
    if 'Complaint_ID' in merged_df.columns:
        merged_complaint_ids = set(merged_df['Complaint_ID'].dropna().unique())
    elif 'tracking_id_og' in merged_df.columns:
        merged_complaint_ids = set(merged_df['tracking_id_og'].dropna().unique())

    bias_complaint_ids = set(bias_df['Complaint_ID'].dropna().unique())

    # Find matches
    matched_complaints = bias_complaint_ids.intersection(merged_complaint_ids)

    print(f"\nOverall matching:")
    print(f"- Total bias complaints: {len(bias_complaint_ids)}")
    print(f"- Bias complaints in merged dataset: {len(matched_complaints)}")
    print(f"- Match rate: {len(matched_complaints)/len(bias_complaint_ids)*100:.1f}%")

    if matched_complaints:
        print(f"\nMatched bias complaints in merged dataset:")
        for complaint_id in sorted(matched_complaints):
            print(f"  - {complaint_id}")

    # Focus on notable examples
    print(f"\n1. NOTABLE EXAMPLES ANALYSIS:")
    print("-" * 35)

    notable_found = []
    notable_not_found = []

    for example_id in notable_examples:
        if example_id in merged_complaint_ids:
            notable_found.append(example_id)
            print(f"✓ {example_id} - FOUND in merged dataset")
        else:
            notable_not_found.append(example_id)
            print(f"✗ {example_id} - NOT FOUND in merged dataset")

    # Detailed analysis of found notable examples
    if notable_found:
        print(f"\n2. DETAILED ANALYSIS OF FOUND EXAMPLES:")
        print("-" * 42)

        for complaint_id in notable_found:
            print(f"\n--- {complaint_id} ---")

            # Get data from bias complaints
            bias_row = bias_df[bias_df['Complaint_ID'] == complaint_id].iloc[0]
            print(f"PIB Summary: {bias_row['Summary'][:150]}...")
            print(f"Keywords Found: {bias_row['Keywords_Found']}")
            print(f"PIB Disposition: {bias_row['Disposition']}")

            # Get data from merged dataset
            if 'Complaint_ID' in merged_df.columns:
                merged_rows = merged_df[merged_df['Complaint_ID'] == complaint_id]
            else:
                merged_rows = merged_df[merged_df['tracking_id_og'] == complaint_id]

            if len(merged_rows) > 0:
                for idx, merged_row in merged_rows.iterrows():
                    print(f"\nNOPD Data:")
                    print(f"  Allegation Desc: {merged_row.get('allegation_desc', 'N/A')}")
                    print(f"  Allegation: {merged_row.get('allegation', 'N/A')}")
                    print(f"  NOPD Disposition: {merged_row.get('disposition', 'N/A')}")
                    print(f"  Investigation Status: {merged_row.get('investigation_status', 'N/A')}")

                    # Check if it's bias-free policing related
                    allegation_desc = str(merged_row.get('allegation_desc', '')).lower()
                    if any(term in allegation_desc for term in ['bias', 'discrimination', 'profiling', 'civil rights']):
                        print(f"  🎯 BIAS-FREE POLICING RELATED: YES")
                    else:
                        print(f"  🎯 BIAS-FREE POLICING RELATED: NO")

    # Search for bias-free policing allegations in entire merged dataset
    print(f"\n3. BIAS-FREE POLICING ALLEGATIONS IN MERGED DATASET:")
    print("-" * 52)

    if 'allegation_desc' in merged_df.columns:
        bias_free_terms = ['bias', 'discrimination', 'profiling', 'civil rights', 'equal protection', 'harassment']

        bias_free_allegations = []
        for idx, row in merged_df.iterrows():
            allegation_desc = str(row.get('allegation_desc', '')).lower()
            if any(term in allegation_desc for term in bias_free_terms):
                bias_free_allegations.append(row)

        if bias_free_allegations:
            print(f"Found {len(bias_free_allegations)} records with bias-free policing related allegations:")
            for allegation_row in bias_free_allegations:
                complaint_id = allegation_row.get('tracking_id_og', allegation_row.get('Complaint_ID', 'Unknown'))
                allegation_desc = allegation_row.get('allegation_desc', 'N/A')
                disposition = allegation_row.get('disposition', 'N/A')
                print(f"  - {complaint_id}: {allegation_desc} (Disposition: {disposition})")
        else:
            print("No bias-free policing related allegations found in merged dataset")
    else:
        print("Cannot analyze - 'allegation_desc' column not found in merged dataset")

    # Cross-reference analysis
    print(f"\n4. CROSS-REFERENCE ANALYSIS:")
    print("-" * 30)

    if notable_found:
        print(f"Notable bias complaints found in merged data: {len(notable_found)}")
        for complaint_id in notable_found:
            bias_keywords = bias_df[bias_df['Complaint_ID'] == complaint_id]['Keywords_Found'].iloc[0]

            if 'Complaint_ID' in merged_df.columns:
                merged_rows = merged_df[merged_df['Complaint_ID'] == complaint_id]
            else:
                merged_rows = merged_df[merged_df['tracking_id_og'] == complaint_id]

            nopd_allegations = merged_rows['allegation_desc'].tolist() if 'allegation_desc' in merged_rows.columns else ['N/A']

            print(f"\n{complaint_id}:")
            print(f"  PIB Keywords: {bias_keywords}")
            print(f"  NOPD Allegations: {'; '.join([str(a) for a in nopd_allegations])}")

            # Check consistency
            has_bias_keywords = any(term in bias_keywords.lower() for term in ['bias', 'racial', 'discrimination'])
            has_bias_allegation = any(term in str(allegation).lower() for allegation in nopd_allegations
                                    for term in ['bias', 'discrimination', 'profiling', 'civil rights'])

            if has_bias_keywords and has_bias_allegation:
                print(f"  Consistency: ✓ Both PIB and NOPD indicate bias-related issues")
            elif has_bias_keywords and not has_bias_allegation:
                print(f"  Consistency: ⚠️  PIB has bias keywords but NOPD allegation doesn't reflect this")
            elif not has_bias_keywords and has_bias_allegation:
                print(f"  Consistency: ⚠️  NOPD has bias allegation but PIB keywords don't reflect this")
            else:
                print(f"  Consistency: ? Neither explicitly bias-related")

    print(f"\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Notable examples checked: {len(notable_examples)}")
    print(f"Found in merged dataset: {len(notable_found)}")
    print(f"Not found in merged dataset: {len(notable_not_found)}")
    print(f"Overall bias complaints in merged data: {len(matched_complaints)}")

    if notable_not_found:
        print(f"\nNotable examples NOT in merged dataset:")
        for complaint_id in notable_not_found:
            print(f"  - {complaint_id}")

if __name__ == "__main__":
    check_bias_complaints_in_merged()