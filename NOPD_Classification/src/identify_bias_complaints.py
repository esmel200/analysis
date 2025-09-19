#!/usr/bin/env python3

import pandas as pd
import re
import os

def identify_bias_complaints():
    """
    Identify complaints related to bias, discrimination, or profiling
    from the PIB Annual CPRR 2023 dataset
    """

    # Read the PIB Annual data
    print("Loading PIB Annual CPRR 2023 data...")
    pib_file = '../data/pib_annual_cprr_2023.csv'

    if not os.path.exists(pib_file):
        print(f"File not found: {pib_file}")
        return

    pib_df = pd.read_csv(pib_file)
    print(f"Total PIB records: {len(pib_df)}")
    print(f"Columns: {list(pib_df.columns)}")

    # Define bias-related keywords and variations
    bias_keywords = [
        # Bias variations
        'bias', 'biased', 'biases', 'biasing',

        # Discrimination variations
        'discriminat', 'discriminate', 'discriminated', 'discriminates', 'discriminating',
        'discrimination', 'discriminatory',

        # Profiling variations
        'profil', 'profile', 'profiled', 'profiles', 'profiling',
        'racial profiling', 'ethnic profiling', 'religious profiling',

        # Related terms
        'prejudice', 'prejudiced', 'prejudicial',
        'stereotype', 'stereotyped', 'stereotyping', 'stereotypes',
        'harassment', 'harass', 'harassed', 'harassing',
        'civil rights', 'equal protection',
        'selective enforcement',
        'unfair treatment', 'unequal treatment',
        'targeting', 'targeted',

        # Specific protected classes
        'race', 'racial', 'racism', 'racist',
        'color', 'ethnicity', 'ethnic', 'nationality', 'national origin',
        'religion', 'religious', 'faith',
        'gender', 'sex', 'sexual orientation', 'lgbtq', 'transgender',
        'age', 'disability', 'disabled',
        'homeless', 'homelessness',

        # Bias-free policing specific terms
        'bias-free', 'bias free', 'biased policing', 'discriminatory policing',
        'equal enforcement', 'fair policing', 'impartial policing'
    ]

    print(f"\nSearching for {len(bias_keywords)} bias-related keywords...")

    # Create regex pattern for case-insensitive matching
    # Use word boundaries to avoid partial matches
    pattern = r'\b(?:' + '|'.join(re.escape(keyword) for keyword in bias_keywords) + r')\b'
    regex = re.compile(pattern, re.IGNORECASE)

    # Search in both Summary and Complaint Text columns
    bias_matches = []

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

            bias_matches.append({
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
    print("BIAS-RELATED COMPLAINTS ANALYSIS")
    print("="*60)

    if not bias_matches:
        print("No bias-related complaints found.")
        return

    bias_df = pd.DataFrame(bias_matches)
    print(f"\nFound {len(bias_df)} complaints with bias-related keywords")
    print(f"Out of {len(pib_df)} total complaints ({len(bias_df)/len(pib_df)*100:.1f}%)")

    # Save results
    os.makedirs('../output', exist_ok=True)
    bias_df.to_csv('../output/bias_complaints_2023.csv', index=False)
    print(f"Results saved to: ../output/bias_complaints_2023.csv")

    # Analysis by disposition
    print(f"\n1. DISPOSITION BREAKDOWN:")
    print("-" * 25)
    disposition_counts = bias_df['Disposition'].value_counts()
    for disposition, count in disposition_counts.items():
        percentage = (count / len(bias_df)) * 100
        print(f"{disposition}: {count} cases ({percentage:.1f}%)")

    # Most common keywords
    print(f"\n2. MOST COMMON KEYWORDS:")
    print("-" * 25)
    all_keywords = []
    for keywords_str in bias_df['Keywords_Found']:
        all_keywords.extend([kw.strip() for kw in keywords_str.split(',')])

    keyword_counts = pd.Series(all_keywords).value_counts()
    for keyword, count in keyword_counts.head(10).items():
        print(f"{keyword}: {count} mentions")

    # Timeline analysis
    print(f"\n3. TIMELINE ANALYSIS:")
    print("-" * 20)
    if 'Received_Date' in bias_df.columns:
        # Convert dates and extract month
        bias_df['Date'] = pd.to_datetime(bias_df['Received_Date'], errors='coerce')
        bias_df['Month'] = bias_df['Date'].dt.strftime('%Y-%m')

        monthly_counts = bias_df['Month'].value_counts().sort_index()
        print("Monthly distribution:")
        for month, count in monthly_counts.items():
            print(f"{month}: {count} complaints")

    # Show detailed examples
    print(f"\n4. DETAILED EXAMPLES:")
    print("-" * 20)

    # Sort by keyword count and total mentions for most relevant examples
    bias_df_sorted = bias_df.sort_values(['Keyword_Count', 'Total_Mentions'], ascending=False)

    for i, (_, row) in enumerate(bias_df_sorted.head(5).iterrows()):
        print(f"\nExample {i+1}: {row['Complaint_ID']}")
        print(f"Date: {row['Received_Date']}")
        print(f"Disposition: {row['Disposition']}")
        print(f"Keywords Found: {row['Keywords_Found']}")
        print(f"Summary: {row['Summary'][:200]}...")

        # Highlight keywords in the complaint text
        complaint_excerpt = row['Complaint_Text'][:300]
        print(f"Complaint Text (excerpt): {complaint_excerpt}...")
        print("-" * 40)

    # Specific bias-free policing analysis
    print(f"\n5. BIAS-FREE POLICING SPECIFIC ANALYSIS:")
    print("-" * 40)

    bias_free_keywords = ['bias-free', 'bias free', 'biased policing', 'discriminatory policing',
                         'racial profiling', 'ethnic profiling', 'profiling']

    bias_free_pattern = r'\b(?:' + '|'.join(re.escape(kw) for kw in bias_free_keywords) + r')\b'
    bias_free_regex = re.compile(bias_free_pattern, re.IGNORECASE)

    bias_free_complaints = []
    for _, row in bias_df.iterrows():
        combined_text = f"{row['Summary']} {row['Complaint_Text']}"
        if bias_free_regex.search(combined_text):
            bias_free_complaints.append(row)

    if bias_free_complaints:
        print(f"Found {len(bias_free_complaints)} complaints specifically related to bias-free policing:")
        for complaint in bias_free_complaints:
            print(f"- {complaint['Complaint_ID']}: {complaint['Disposition']}")
    else:
        print("No complaints specifically mentioning bias-free policing terms found.")

    # Summary statistics
    print(f"\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)

    print(f"Total complaints analyzed: {len(pib_df)}")
    print(f"Bias-related complaints found: {len(bias_df)}")
    print(f"Percentage of total: {len(bias_df)/len(pib_df)*100:.1f}%")
    print(f"Average keywords per complaint: {bias_df['Keyword_Count'].mean():.1f}")
    print(f"Average mentions per complaint: {bias_df['Total_Mentions'].mean():.1f}")

    if len(bias_df) > 0:
        print(f"Most common disposition: {bias_df['Disposition'].mode().iloc[0]}")
        print(f"Date range: {bias_df['Received_Date'].min()} to {bias_df['Received_Date'].max()}")

if __name__ == "__main__":
    identify_bias_complaints()