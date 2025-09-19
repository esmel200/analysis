#!/usr/bin/env python3

import pandas as pd
import re
import os

def identify_use_of_force_complaints():
    """
    Identify use of force related complaints from PIB Annual CPRR 2023 dataset
    and check consistency with NOPD merged data
    """

    # Read the PIB Annual data
    print("Loading PIB Annual CPRR 2023 data...")
    pib_file = '../data/pib_annual_cprr_2023.csv'
    merged_file = '../output/nopd_merged_2023.csv'

    for file_path in [pib_file, merged_file]:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return

    pib_df = pd.read_csv(pib_file)
    merged_df = pd.read_csv(merged_file)

    print(f"Total PIB records: {len(pib_df)}")
    print(f"Total merged records: {len(merged_df)}")

    # Define use of force related keywords and variations
    uof_keywords = [
        # Core use of force terms
        'use of force', 'excessive force', 'force', 'physical force',
        'unnecessary force', 'unreasonable force', 'brutal force',

        # Physical actions
        'punch', 'punched', 'punching', 'hit', 'hitting', 'strike', 'struck', 'striking',
        'kick', 'kicked', 'kicking', 'knee', 'kneed', 'kneeing',
        'choke', 'choked', 'choking', 'strangled', 'strangling',
        'slam', 'slammed', 'slamming', 'throw', 'threw', 'thrown', 'throwing',
        'tackle', 'tackled', 'tackling', 'wrestle', 'wrestled', 'wrestling',
        'grab', 'grabbed', 'grabbing', 'seize', 'seized', 'seizing',
        'shove', 'shoved', 'shoving', 'push', 'pushed', 'pushing',

        # Weapons and tools
        'taser', 'tased', 'stun gun', 'electroshock',
        'baton', 'nightstick', 'club', 'asp', 'expandable baton',
        'pepper spray', 'mace', 'oc spray', 'chemical spray',
        'firearm', 'gun', 'shot', 'shooting', 'fired weapon',
        'handcuffs', 'cuffs', 'restrain', 'restrained', 'restraining',

        # Injuries and medical terms
        'injury', 'injured', 'injure', 'hurt', 'harm', 'harmed',
        'bruise', 'bruised', 'bruising', 'cut', 'bleeding', 'blood',
        'broken bone', 'fracture', 'fractured', 'sprain', 'sprained',
        'concussion', 'head injury', 'trauma',

        # Resistance and control
        'resistance', 'resisting', 'resist', 'compliance', 'non-compliant',
        'control', 'controlled', 'controlling', 'subdue', 'subdued',
        'takedown', 'taken down', 'ground control',

        # Investigation terms
        'force investigation', 'force review', 'force incident',
        'use of force policy', 'force report', 'force documentation',

        # Pain and suffering
        'pain', 'painful', 'suffer', 'suffered', 'suffering',
        'rough', 'roughed up', 'manhandle', 'manhandled',
        'violent', 'violence', 'aggressive', 'aggression'
    ]

    print(f"\nSearching for {len(uof_keywords)} use of force related keywords...")

    # Create regex pattern for case-insensitive matching
    pattern = r'\b(?:' + '|'.join(re.escape(keyword) for keyword in uof_keywords) + r')\b'
    regex = re.compile(pattern, re.IGNORECASE)

    # Search in both Summary and Complaint Text columns
    uof_matches = []

    for idx, row in pib_df.iterrows():
        complaint_id = row['Complaint_ID']
        summary = str(row.get('Summary', ''))
        complaint_text = str(row.get('Complaint Text', ''))
        disposition = row.get('Disposition', '')
        received_date = row.get('Received_Date', '')

        # Combine both text fields for searching
        combined_text = f"{summary} {complaint_text}"

        # Find all matches in the text
        matches = regex.findall(combined_text)

        if matches:
            # Remove duplicates and normalize
            unique_matches = list(set([match.lower() for match in matches]))

            uof_matches.append({
                'Complaint_ID': complaint_id,
                'Received_Date': received_date,
                'Disposition': disposition,
                'Summary': summary,
                'Complaint_Text': complaint_text,
                'Keywords_Found': ', '.join(sorted(unique_matches)),
                'Keyword_Count': len(unique_matches),
                'Total_Mentions': len(matches)
            })

    print(f"\n" + "="*60)
    print("USE OF FORCE COMPLAINTS ANALYSIS")
    print("="*60)

    if not uof_matches:
        print("No use of force related complaints found.")
        return

    uof_df = pd.DataFrame(uof_matches)
    print(f"\nFound {len(uof_df)} complaints with use of force keywords")
    print(f"Out of {len(pib_df)} total complaints ({len(uof_df)/len(pib_df)*100:.1f}%)")

    # Save results
    os.makedirs('../output', exist_ok=True)
    uof_df.to_csv('../output/use_of_force_complaints_2023.csv', index=False)
    print(f"Results saved to: ../output/use_of_force_complaints_2023.csv")

    # Analysis by disposition
    print(f"\n1. DISPOSITION BREAKDOWN:")
    print("-" * 25)
    disposition_counts = uof_df['Disposition'].value_counts()
    for disposition, count in disposition_counts.items():
        percentage = (count / len(uof_df)) * 100
        print(f"{disposition}: {count} cases ({percentage:.1f}%)")

    # Most common keywords
    print(f"\n2. MOST COMMON KEYWORDS:")
    print("-" * 25)
    all_keywords = []
    for keywords_str in uof_df['Keywords_Found']:
        all_keywords.extend([kw.strip() for kw in keywords_str.split(',')])

    keyword_counts = pd.Series(all_keywords).value_counts()
    for keyword, count in keyword_counts.head(15).items():
        print(f"{keyword}: {count} mentions")

    # Timeline analysis
    print(f"\n3. TIMELINE ANALYSIS:")
    print("-" * 20)
    uof_df['Date'] = pd.to_datetime(uof_df['Received_Date'], errors='coerce')
    uof_df['Month'] = uof_df['Date'].dt.strftime('%Y-%m')

    monthly_counts = uof_df['Month'].value_counts().sort_index()
    print("Monthly distribution:")
    for month, count in monthly_counts.items():
        print(f"{month}: {count} complaints")

    # Check overlap with merged dataset
    print(f"\n4. OVERLAP WITH NOPD MERGED DATASET:")
    print("-" * 38)

    merged_complaint_ids = set(merged_df['Complaint_ID'].dropna().unique())
    uof_complaint_ids = set(uof_df['Complaint_ID'].dropna().unique())

    uof_in_merged = uof_complaint_ids.intersection(merged_complaint_ids)

    print(f"Use of force complaints in merged dataset: {len(uof_in_merged)}")
    print(f"Match rate: {len(uof_in_merged)/len(uof_complaint_ids)*100:.1f}%")

    if uof_in_merged:
        print(f"\nUse of force complaints found in merged dataset:")
        for complaint_id in sorted(uof_in_merged):
            print(f"  - {complaint_id}")

    # Detailed analysis of overlapping cases
    if uof_in_merged:
        print(f"\n5. DETAILED ANALYSIS OF OVERLAPPING CASES:")
        print("-" * 43)

        for complaint_id in sorted(uof_in_merged):
            print(f"\n--- {complaint_id} ---")

            # Get UOF data
            uof_row = uof_df[uof_df['Complaint_ID'] == complaint_id].iloc[0]
            print(f"PIB Summary: {uof_row['Summary'][:150]}...")
            print(f"UOF Keywords: {uof_row['Keywords_Found']}")
            print(f"PIB Disposition: {uof_row['Disposition']}")

            # Get NOPD data from merged dataset
            merged_rows = merged_df[merged_df['Complaint_ID'] == complaint_id]

            for idx, merged_row in merged_rows.iterrows():
                print(f"\nNOPD Data:")
                print(f"  Allegation Desc: {merged_row.get('allegation_desc', 'N/A')}")
                print(f"  Allegation: {merged_row.get('allegation', 'N/A')}")
                print(f"  NOPD Disposition: {merged_row.get('disposition', 'N/A')}")

                # Check if it's use of force related in NOPD classification
                allegation_desc = str(merged_row.get('allegation_desc', '')).lower()
                allegation = str(merged_row.get('allegation', '')).lower()

                if any(term in allegation_desc or term in allegation
                      for term in ['use of force', 'force', 'unauthorized force']):
                    print(f"  🎯 NOPD USE OF FORCE CLASSIFICATION: YES")
                else:
                    print(f"  🎯 NOPD USE OF FORCE CLASSIFICATION: NO")

    # Search for all use of force allegations in merged dataset
    print(f"\n6. ALL USE OF FORCE ALLEGATIONS IN MERGED DATASET:")
    print("-" * 50)

    uof_terms_nopd = ['use of force', 'force', 'unauthorized force', 'excessive force']

    nopd_uof_allegations = []
    for idx, row in merged_df.iterrows():
        allegation_desc = str(row.get('allegation_desc', '')).lower()
        allegation = str(row.get('allegation', '')).lower()

        if any(term in allegation_desc or term in allegation for term in uof_terms_nopd):
            nopd_uof_allegations.append(row)

    if nopd_uof_allegations:
        print(f"Found {len(nopd_uof_allegations)} records with use of force related allegations in NOPD data:")
        for allegation_row in nopd_uof_allegations:
            complaint_id = allegation_row.get('Complaint_ID', 'Unknown')
            allegation_desc = allegation_row.get('allegation_desc', 'N/A')
            allegation = allegation_row.get('allegation', 'N/A')
            disposition = allegation_row.get('disposition', 'N/A')
            print(f"  - {complaint_id}: {allegation_desc} | {allegation} (Disposition: {disposition})")
    else:
        print("No use of force related allegations found in NOPD merged dataset")

    # Cross-reference analysis
    print(f"\n7. CROSS-REFERENCE ANALYSIS:")
    print("-" * 30)

    if uof_in_merged:
        print(f"Use of force complaints found in merged data: {len(uof_in_merged)}")

        for complaint_id in sorted(uof_in_merged):
            uof_keywords = uof_df[uof_df['Complaint_ID'] == complaint_id]['Keywords_Found'].iloc[0]
            merged_rows = merged_df[merged_df['Complaint_ID'] == complaint_id]

            nopd_allegations = []
            for _, row in merged_rows.iterrows():
                allegation_desc = row.get('allegation_desc', 'N/A')
                allegation = row.get('allegation', 'N/A')
                nopd_allegations.append(f"{allegation_desc} | {allegation}")

            print(f"\n{complaint_id}:")
            print(f"  PIB Keywords: {uof_keywords}")
            print(f"  NOPD Allegations: {'; '.join(nopd_allegations)}")

            # Check consistency
            has_uof_keywords = any(term in uof_keywords.lower()
                                 for term in ['force', 'punch', 'hit', 'kick', 'taser', 'injury'])
            has_uof_allegation = any(term in str(allegation).lower()
                                   for allegation in nopd_allegations
                                   for term in ['use of force', 'force', 'unauthorized force'])

            if has_uof_keywords and has_uof_allegation:
                print(f"  Consistency: ✓ Both PIB and NOPD indicate use of force issues")
            elif has_uof_keywords and not has_uof_allegation:
                print(f"  Consistency: ⚠️  PIB has UOF keywords but NOPD allegation doesn't reflect this")
            elif not has_uof_keywords and has_uof_allegation:
                print(f"  Consistency: ⚠️  NOPD has UOF allegation but PIB keywords don't reflect this")
            else:
                print(f"  Consistency: ? Classification unclear")

    # Show top examples
    print(f"\n8. TOP USE OF FORCE EXAMPLES:")
    print("-" * 30)

    # Sort by keyword count and total mentions for most relevant examples
    uof_df_sorted = uof_df.sort_values(['Keyword_Count', 'Total_Mentions'], ascending=False)

    for i, (_, row) in enumerate(uof_df_sorted.head(5).iterrows()):
        print(f"\nExample {i+1}: {row['Complaint_ID']}")
        print(f"Date: {row['Received_Date']}")
        print(f"Disposition: {row['Disposition']}")
        print(f"Keywords Found: {row['Keywords_Found']}")
        print(f"Summary: {row['Summary'][:200]}...")

    print(f"\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)

    print(f"Total complaints analyzed: {len(pib_df)}")
    print(f"Use of force complaints found: {len(uof_df)}")
    print(f"Percentage of total: {len(uof_df)/len(pib_df)*100:.1f}%")
    print(f"Average keywords per complaint: {uof_df['Keyword_Count'].mean():.1f}")
    print(f"Average mentions per complaint: {uof_df['Total_Mentions'].mean():.1f}")
    print(f"UOF complaints in merged dataset: {len(uof_in_merged)}")
    print(f"Overlap rate: {len(uof_in_merged)/len(uof_df)*100:.1f}%")

    if len(uof_df) > 0:
        print(f"Most common disposition: {uof_df['Disposition'].mode().iloc[0]}")
        print(f"Date range: {uof_df['Received_Date'].min()} to {uof_df['Received_Date'].max()}")

if __name__ == "__main__":
    identify_use_of_force_complaints()