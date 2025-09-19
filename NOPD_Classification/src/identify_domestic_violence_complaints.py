#!/usr/bin/env python3

import pandas as pd
import re
import os

def identify_domestic_violence_complaints():
    """
    Identify domestic violence related complaints from PIB Annual CPRR 2023 dataset
    and check consistency with NOPD merged data (Chapter 42.4)
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

    # Define domestic violence related keywords and variations
    dv_keywords = [
        # Core domestic violence terms
        'domestic violence', 'domestic abuse', 'domestic assault',
        'domestic disturbance', 'domestic dispute', 'domestic incident',
        'domestic call', 'domestic battery', 'domestic situation',

        # Family violence
        'family violence', 'family abuse', 'intimate partner violence',
        'spousal abuse', 'spousal assault', 'spousal battery',
        'partner violence', 'partner abuse',

        # Relationship terms
        'boyfriend', 'girlfriend', 'spouse', 'husband', 'wife',
        'ex-boyfriend', 'ex-girlfriend', 'ex-husband', 'ex-wife',
        'intimate partner', 'romantic partner', 'dating violence',

        # Protection orders
        'protective order', 'restraining order', 'order of protection',
        'protection from abuse', 'pfa', 'tpo', 'temporary protective order',
        'no contact order', 'stay away order',

        # Violations
        'violation of protective order', 'violating protective order',
        'breach of protective order', 'violation of restraining order',

        # Related terms
        'harassment by ex', 'stalking by ex', 'threatened by ex',
        'abuse by partner', 'assault by partner', 'battery by partner',
        'cohabitation', 'cohabitant', 'live-in partner',

        # Specific contexts
        'home invasion by ex', 'breaking and entering by ex',
        'property damage by ex', 'threatening calls from ex',
        'unwanted contact', 'repeated contact',

        # Legal terms
        'domestic relations', 'family court', 'custody dispute',
        'child custody', 'visitation dispute',

        # NOPD specific policy terms
        'chapter 42.4', 'nopd policy 42.4', 'domestic policy',
        'domestic violence policy', 'domestic procedures'
    ]

    print(f"\nSearching for {len(dv_keywords)} domestic violence related keywords...")

    # Create regex pattern for case-insensitive matching
    pattern = r'\b(?:' + '|'.join(re.escape(keyword) for keyword in dv_keywords) + r')\b'
    regex = re.compile(pattern, re.IGNORECASE)

    # Search in both Summary and Complaint Text columns
    dv_matches = []

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

            dv_matches.append({
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
    print("DOMESTIC VIOLENCE COMPLAINTS ANALYSIS")
    print("="*60)

    if not dv_matches:
        print("No domestic violence related complaints found.")
        return

    dv_df = pd.DataFrame(dv_matches)
    print(f"\nFound {len(dv_df)} complaints with domestic violence keywords")
    print(f"Out of {len(pib_df)} total complaints ({len(dv_df)/len(pib_df)*100:.1f}%)")

    # Save results
    os.makedirs('../output', exist_ok=True)
    dv_df.to_csv('../output/domestic_violence_complaints_2023.csv', index=False)
    print(f"Results saved to: ../output/domestic_violence_complaints_2023.csv")

    # Analysis by disposition
    print(f"\n1. DISPOSITION BREAKDOWN:")
    print("-" * 25)
    disposition_counts = dv_df['Disposition'].value_counts()
    for disposition, count in disposition_counts.items():
        percentage = (count / len(dv_df)) * 100
        print(f"{disposition}: {count} cases ({percentage:.1f}%)")

    # Most common keywords
    print(f"\n2. MOST COMMON KEYWORDS:")
    print("-" * 25)
    all_keywords = []
    for keywords_str in dv_df['Keywords_Found']:
        all_keywords.extend([kw.strip() for kw in keywords_str.split(',')])

    keyword_counts = pd.Series(all_keywords).value_counts()
    for keyword, count in keyword_counts.head(15).items():
        print(f"{keyword}: {count} mentions")

    # Timeline analysis
    print(f"\n3. TIMELINE ANALYSIS:")
    print("-" * 20)
    dv_df['Date'] = pd.to_datetime(dv_df['Received_Date'], errors='coerce')
    dv_df['Month'] = dv_df['Date'].dt.strftime('%Y-%m')

    monthly_counts = dv_df['Month'].value_counts().sort_index()
    print("Monthly distribution:")
    for month, count in monthly_counts.items():
        print(f"{month}: {count} complaints")

    # Check overlap with merged dataset
    print(f"\n4. OVERLAP WITH NOPD MERGED DATASET:")
    print("-" * 38)

    merged_complaint_ids = set(merged_df['Complaint_ID'].dropna().unique())
    dv_complaint_ids = set(dv_df['Complaint_ID'].dropna().unique())

    dv_in_merged = dv_complaint_ids.intersection(merged_complaint_ids)

    print(f"Domestic violence complaints in merged dataset: {len(dv_in_merged)}")
    print(f"Match rate: {len(dv_in_merged)/len(dv_complaint_ids)*100:.1f}%")

    if dv_in_merged:
        print(f"\nDomestic violence complaints found in merged dataset:")
        for complaint_id in sorted(dv_in_merged):
            print(f"  - {complaint_id}")

    # Search for Chapter 42.4 allegations in merged dataset
    print(f"\n5. CHAPTER 42.4 (DOMESTIC VIOLENCE) ALLEGATIONS IN MERGED DATASET:")
    print("-" * 63)

    chapter_42_4_terms = ['chapter 42.4', '42.4', 'domestic violence', 'domestic disturbance']

    nopd_dv_allegations = []
    for idx, row in merged_df.iterrows():
        allegation_desc = str(row.get('allegation_desc', '')).lower()
        allegation = str(row.get('allegation', '')).lower()

        if any(term in allegation_desc for term in chapter_42_4_terms):
            nopd_dv_allegations.append(row)

    if nopd_dv_allegations:
        print(f"Found {len(nopd_dv_allegations)} records with Chapter 42.4 (domestic violence) allegations:")
        for allegation_row in nopd_dv_allegations:
            complaint_id = allegation_row.get('Complaint_ID', 'Unknown')
            allegation_desc = allegation_row.get('allegation_desc', 'N/A')
            allegation = allegation_row.get('allegation', 'N/A')
            disposition = allegation_row.get('disposition', 'N/A')
            print(f"  - {complaint_id}: {allegation_desc} | {allegation} (Disposition: {disposition})")
    else:
        print("No Chapter 42.4 (domestic violence) related allegations found in NOPD merged dataset")

    # Detailed analysis of overlapping cases
    if dv_in_merged:
        print(f"\n6. DETAILED ANALYSIS OF OVERLAPPING CASES:")
        print("-" * 43)

        for complaint_id in sorted(dv_in_merged):
            print(f"\n--- {complaint_id} ---")

            # Get DV data
            dv_row = dv_df[dv_df['Complaint_ID'] == complaint_id].iloc[0]
            print(f"PIB Summary: {dv_row['Summary'][:150]}...")
            print(f"DV Keywords: {dv_row['Keywords_Found']}")
            print(f"PIB Disposition: {dv_row['Disposition']}")

            # Get NOPD data from merged dataset
            merged_rows = merged_df[merged_df['Complaint_ID'] == complaint_id]

            for idx, merged_row in merged_rows.iterrows():
                print(f"\nNOPD Data:")
                print(f"  Allegation Desc: {merged_row.get('allegation_desc', 'N/A')}")
                print(f"  Allegation: {merged_row.get('allegation', 'N/A')}")
                print(f"  NOPD Disposition: {merged_row.get('disposition', 'N/A')}")

                # Check if it's Chapter 42.4 related in NOPD classification
                allegation_desc = str(merged_row.get('allegation_desc', '')).lower()
                allegation = str(merged_row.get('allegation', '')).lower()

                if any(term in allegation_desc for term in ['42.4', 'domestic violence', 'domestic disturbance']):
                    print(f"  🎯 NOPD CHAPTER 42.4 CLASSIFICATION: YES")
                else:
                    print(f"  🎯 NOPD CHAPTER 42.4 CLASSIFICATION: NO")

    # Cross-reference analysis
    print(f"\n7. CROSS-REFERENCE ANALYSIS:")
    print("-" * 30)

    if dv_in_merged:
        print(f"Domestic violence complaints found in merged data: {len(dv_in_merged)}")

        for complaint_id in sorted(dv_in_merged):
            dv_keywords = dv_df[dv_df['Complaint_ID'] == complaint_id]['Keywords_Found'].iloc[0]
            merged_rows = merged_df[merged_df['Complaint_ID'] == complaint_id]

            nopd_allegations = []
            for _, row in merged_rows.iterrows():
                allegation_desc = row.get('allegation_desc', 'N/A')
                allegation = row.get('allegation', 'N/A')
                nopd_allegations.append(f"{allegation_desc} | {allegation}")

            print(f"\n{complaint_id}:")
            print(f"  PIB Keywords: {dv_keywords}")
            print(f"  NOPD Allegations: {'; '.join(nopd_allegations)}")

            # Check consistency
            has_dv_keywords = any(term in dv_keywords.lower()
                                for term in ['domestic', 'protective order', 'restraining', 'partner', 'spouse'])
            has_dv_allegation = any(term in str(allegation).lower()
                                  for allegation in nopd_allegations
                                  for term in ['42.4', 'domestic', 'family'])

            if has_dv_keywords and has_dv_allegation:
                print(f"  Consistency: ✓ Both PIB and NOPD indicate domestic violence issues")
            elif has_dv_keywords and not has_dv_allegation:
                print(f"  Consistency: ⚠️  PIB has DV keywords but NOPD allegation doesn't reflect this")
            elif not has_dv_keywords and has_dv_allegation:
                print(f"  Consistency: ⚠️  NOPD has DV allegation but PIB keywords don't reflect this")
            else:
                print(f"  Consistency: ? Classification unclear")

    # Show top examples
    print(f"\n8. TOP DOMESTIC VIOLENCE EXAMPLES:")
    print("-" * 35)

    # Sort by keyword count and total mentions for most relevant examples
    dv_df_sorted = dv_df.sort_values(['Keyword_Count', 'Total_Mentions'], ascending=False)

    for i, (_, row) in enumerate(dv_df_sorted.head(5).iterrows()):
        print(f"\nExample {i+1}: {row['Complaint_ID']}")
        print(f"Date: {row['Received_Date']}")
        print(f"Disposition: {row['Disposition']}")
        print(f"Keywords Found: {row['Keywords_Found']}")
        print(f"Summary: {row['Summary'][:200]}...")

    print(f"\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)

    print(f"Total complaints analyzed: {len(pib_df)}")
    print(f"Domestic violence complaints found: {len(dv_df)}")
    print(f"Percentage of total: {len(dv_df)/len(pib_df)*100:.1f}%")
    print(f"Average keywords per complaint: {dv_df['Keyword_Count'].mean():.1f}")
    print(f"Average mentions per complaint: {dv_df['Total_Mentions'].mean():.1f}")
    print(f"DV complaints in merged dataset: {len(dv_in_merged)}")
    print(f"Overlap rate: {len(dv_in_merged)/len(dv_df)*100:.1f}%" if len(dv_df) > 0 else "N/A")

    if len(dv_df) > 0:
        print(f"Most common disposition: {dv_df['Disposition'].mode().iloc[0]}")
        print(f"Date range: {dv_df['Received_Date'].min()} to {dv_df['Received_Date'].max()}")

    # Classification accuracy analysis
    if dv_in_merged:
        print(f"\nCLASSIFICATION ACCURACY:")
        print(f"PIB DV complaints correctly classified by NOPD as Chapter 42.4:")

        correct_classifications = 0
        for complaint_id in dv_in_merged:
            merged_rows = merged_df[merged_df['Complaint_ID'] == complaint_id]
            for _, row in merged_rows.iterrows():
                allegation_desc = str(row.get('allegation_desc', '')).lower()
                if '42.4' in allegation_desc or 'domestic' in allegation_desc:
                    correct_classifications += 1
                    break

        accuracy_rate = (correct_classifications / len(dv_in_merged)) * 100
        print(f"Accuracy rate: {correct_classifications}/{len(dv_in_merged)} ({accuracy_rate:.1f}%)")

if __name__ == "__main__":
    identify_domestic_violence_complaints()