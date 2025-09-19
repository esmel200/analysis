#!/usr/bin/env python3
"""
Analyze the most common complaints against BRPD officers from 2004-2023.
"""

import pandas as pd
from pathlib import Path

def analyze_brpd_complaints():
    """Analyze BRPD complaint patterns and generate visualizations."""

    # Load the combined dataset
    data_path = Path('/Users/esmelee/analysis/Baton_Rouge_Analysis/cprr_baton_rouge_pd_2004_2023_combined.csv')

    if not data_path.exists():
        print("Error: Combined dataset not found!")
        return

    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} complaints from 2004-2023\n")

    # Clean and standardize allegation data
    df['allegation_clean'] = df['allegation'].fillna('Unknown')

    # Remove very generic or unclear categories for better analysis
    exclude_terms = ['unknown', 'nan', '', ' ']
    df_filtered = df[~df['allegation_clean'].str.lower().isin(exclude_terms)]

    print("="*70)
    print("MOST COMMON COMPLAINTS AGAINST BATON ROUGE PD OFFICERS (2004-2023)")
    print("="*70)

    # Get complaint counts
    complaint_counts = df_filtered['allegation_clean'].value_counts()

    print(f"\nTop 20 Most Common Complaint Types:")
    print("-" * 50)
    for i, (complaint, count) in enumerate(complaint_counts.head(20).items(), 1):
        percentage = (count / len(df_filtered)) * 100
        print(f"{i:2d}. {complaint}: {count} cases ({percentage:.1f}%)")

    # Analyze by disposition
    print(f"\n\nCOMPLAINT OUTCOMES:")
    print("-" * 30)
    disposition_counts = df['disposition'].value_counts()
    for disposition, count in disposition_counts.items():
        if pd.notna(disposition) and disposition.strip():
            percentage = (count / len(df)) * 100
            print(f"{disposition}: {count} cases ({percentage:.1f}%)")

    # Sustained rate analysis
    sustained_cases = df[df['disposition'] == 'sustained']
    total_with_disposition = df[df['disposition'].notna() & (df['disposition'] != '')]
    sustained_rate = (len(sustained_cases) / len(total_with_disposition)) * 100
    print(f"\nOverall Sustain Rate: {sustained_rate:.1f}% ({len(sustained_cases)}/{len(total_with_disposition)} cases)")

    # Top sustained complaint types
    print(f"\n\nTOP SUSTAINED COMPLAINT TYPES:")
    print("-" * 40)
    sustained_complaints = sustained_cases['allegation_clean'].value_counts().head(10)
    for i, (complaint, count) in enumerate(sustained_complaints.items(), 1):
        # Calculate sustain rate for this complaint type
        total_of_type = len(df_filtered[df_filtered['allegation_clean'] == complaint])
        sustain_rate_type = (count / total_of_type) * 100
        print(f"{i:2d}. {complaint}: {count} sustained ({sustain_rate_type:.1f}% of {total_of_type} total)")

    # Year-over-year analysis
    print(f"\n\nCOMPLAINTS BY YEAR:")
    print("-" * 20)
    year_counts = df['occur_year'].value_counts().sort_index()
    for year, count in year_counts.items():
        if pd.notna(year):
            print(f"{int(year)}: {count} complaints")

    # Top complaint categories (grouped)
    print(f"\n\nMAJOR COMPLAINT CATEGORIES:")
    print("-" * 35)

    # Group similar complaints
    use_of_force = df_filtered[df_filtered['allegation_clean'].str.contains('use of force|force', case=False, na=False)]
    conduct_unbecoming = df_filtered[df_filtered['allegation_clean'].str.contains('conduct unbecoming|unbecoming', case=False, na=False)]
    equipment_damage = df_filtered[df_filtered['allegation_clean'].str.contains('damaging|damage.*equipment', case=False, na=False)]
    orders = df_filtered[df_filtered['allegation_clean'].str.contains('carrying out orders|orders', case=False, na=False)]
    duties = df_filtered[df_filtered['allegation_clean'].str.contains('shirking duties|duties', case=False, na=False)]
    property_evidence = df_filtered[df_filtered['allegation_clean'].str.contains('property.*evidence|evidence|secure property', case=False, na=False)]

    categories = {
        'Use of Force': len(use_of_force),
        'Conduct Unbecoming': len(conduct_unbecoming),
        'Equipment Damage': len(equipment_damage),
        'Following Orders': len(orders),
        'Shirking Duties': len(duties),
        'Property/Evidence': len(property_evidence)
    }

    for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(df_filtered)) * 100
        print(f"{category}: {count} cases ({percentage:.1f}%)")

    print(f"\n\nAnalysis completed!")

if __name__ == "__main__":
    analyze_brpd_complaints()