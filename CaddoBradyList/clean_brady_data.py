#!/usr/bin/env python3
"""
Clean and extract Brady list data from OCRed document into standardized CSV format.
"""

import pandas as pd
import re
import uuid
from typing import Dict, List, Optional

def parse_brady_entry(name: str, context_lines: List[str]) -> Dict:
    """Parse a single Brady entry from name and context."""
    entry = {
        'brady_uid': str(uuid.uuid4()),
        'uid': None,
        'name': name.strip(),
        'allegation': None,
        'initial_allegation': None,
        'initial_disposition': None,
        'disposition': None,
        'action': None,
        'allegation_desc': None,
        'court_location': None,
        'charge_location': None,
        'indicted_by': None,
        'tracking_id': None,
        'tracking_id_og': None,
        'source_agency': 'Caddo Parish DA',
        'charging_agency': None,
        'agency': None
    }

    # Combine context lines for analysis
    full_text = ' '.join(context_lines)

    # Extract docket numbers
    docket_patterns = [
        r'(?:DOCKET|#|Docket)\s*#?\s*(\d+)',
        r'(\d{6})',  # 6-digit numbers often dockets
        r'(\d{3,6})'  # 3-6 digit numbers
    ]

    for pattern in docket_patterns:
        matches = re.findall(pattern, full_text, re.IGNORECASE)
        if matches:
            entry['tracking_id'] = matches[0]
            entry['tracking_id_og'] = matches[0]
            break

    # Extract court information
    if 'CADDO DISTRICT COURT' in full_text:
        entry['court_location'] = 'CADDO DISTRICT COURT'
        entry['charge_location'] = 'Caddo Parish'
        entry['charging_agency'] = 'Caddo Parish'
    elif 'BOSSIER' in full_text:
        entry['court_location'] = 'BOSSIER DISTRICT COURT'
        entry['charge_location'] = 'Bossier Parish'
        entry['charging_agency'] = 'Bossier Parish'
    elif 'City Court' in full_text or 'CITY COURT' in full_text:
        entry['court_location'] = 'Shreveport City Court'
        entry['charge_location'] = 'Shreveport'
        entry['charging_agency'] = 'Shreveport'

    # Extract charges/allegations with broader patterns
    charge_patterns = [
        r'(MALFEASANCE IN OFFICE)',
        r'(DOMESTIC ABUSE BATTERY|DAB)',
        r'(DWI|DRIVING WHILE INTOXICATED)',
        r'(SEXUAL BATTERY)',
        r'(SIMPLE BATTERY)',
        r'(THEFT|STOLEN)',
        r'(CRIMINAL MISCHIEF)',
        r'(OBSTRUCTION OF JUSTICE)',
        r'(POSSESSION[^.]*CDS|POSSESSION[^.]*MARIJUANA)',
        r'(FORGERY)',
        r'(ACCESSORY AFTER THE FACT)',
        r'(RAPE)',
        r'(MURDER|HOMICIDE)',
        r'(WIRE FRAUD)',
        r'(CONSPIRACY)',
        r'(CHILD ENDANGERMENT)',
        r'(UNAUTHORIZED ENTRY)',
        r'(FALSE IMPRISONMENT)',
        r'(USE OF FORCE)',
        r'(EXCESSIVE FORCE)',
        r'(POLICY VIOLATION)',
        r'(TERMINATED|FIRED)',
        r'(ADMINISTRATIVE LEAVE)'
    ]

    for pattern in charge_patterns:
        matches = re.findall(pattern, full_text, re.IGNORECASE)
        if matches:
            entry['allegation'] = matches[0]
            entry['initial_allegation'] = matches[0]
            break

    # Extract disposition with broader patterns
    disposition_patterns = [
        r'(PLED GUILTY|Pled guilty|Pled Guilty|GUILTY)',
        r'(FOUND NOT GUILTY|Found not guilty|NOT GUILTY)',
        r'(DISMISSED|Dismissed)',
        r'(NOLLE PROS|Nolle Pro|NOLL)',
        r'(CONVICTED|convicted)',
        r'(ACQUITTED|Acquitted)',
        r'(PENDING|Pending)',
        r'(REJECTED|Rejected)',
        r'(RESIGNED|Resigned)',
        r'(TERMINATED|Terminated|FIRED|Fired)',
        r'(SUSPENDED|Suspended)',
        r'(ADMINISTRATIVE LEAVE|administrative leave)',
        r'(EXONERATED|Exonerated)',
        r'(COMPLETED|Completed)'
    ]

    for pattern in disposition_patterns:
        matches = re.findall(pattern, full_text, re.IGNORECASE)
        if matches:
            entry['disposition'] = matches[0]
            entry['initial_disposition'] = matches[0]
            break

    # Determine agency from context
    if 'SPD' in full_text or 'Shreveport Police' in full_text or 'Officer' in full_text:
        entry['agency'] = 'Shreveport Police Department'
    elif 'CPSO' in full_text or 'Caddo Parish Sheriff' in full_text or 'Caddo SO' in full_text or 'Deputy' in full_text:
        entry['agency'] = 'Caddo Parish Sheriff\'s Office'
    elif 'LSP' in full_text or 'Louisiana State Police' in full_text:
        entry['agency'] = 'Louisiana State Police'
    elif 'Vivian' in full_text:
        entry['agency'] = 'Vivian Police Department'
    elif 'Oil City' in full_text:
        entry['agency'] = 'Oil City Police Department'
    elif 'DeSoto' in full_text or 'Desoto' in full_text:
        entry['agency'] = 'DeSoto Parish Sheriff\'s Office'
    elif 'Jailer' in full_text:
        entry['agency'] = 'Shreveport City Jail'
    elif 'Probation' in full_text:
        entry['agency'] = 'Probation and Parole'

    # Create allegation description
    entry['allegation_desc'] = full_text[:200] + '...' if len(full_text) > 200 else full_text

    return entry

def extract_brady_data():
    """Extract Brady data from OCRed CSV and create cleaned dataset."""

    # Read the OCRed data
    df = pd.read_csv('/Users/esmelee/analysis/CaddoBradyList/rawText.csv')

    # Clean column names by removing quotes
    df.columns = df.columns.str.strip("'")

    # Get text lines and clean them
    text_lines = []
    for text in df['Text'].tolist():
        if isinstance(text, str):
            # Clean up OCR artifacts
            cleaned = text.strip().strip("'\"")
            if cleaned and len(cleaned) > 2:
                text_lines.append(cleaned)

    # Common names that appear in the Brady list
    known_names = [
        'Officer Marcellas Anderson', 'LeRoy Bates', 'Parrish Bernard', 'Jason Brooks',
        'Treveion Brooks', 'Maverick Caldwell', 'Lashell L Crawford', 'Chandler Cisco',
        'Peter Marcus Darcy', 'Nathaniel Davis', 'Ronald Debello', 'Hunter Deloach',
        'Peggy Elzie', 'David Francis', 'Roland Gardner Jr', 'Arthur Green',
        'Breanna Harris', 'Dylan Hudson', 'William Isenhour', "D'Andre Jackson",
        'Montrel Jackson', 'QUALESHA JACKSON', 'Aaron Jaudon', "D'Marea Johnson",
        'Joshunna Jones', 'Mike Jones', 'Rodney Keaton', 'James LeClare',
        'Alfredo Lofton', 'LaBrian Marsden', 'Symphany Mays', 'Treona McCarter',
        'Christopher McConnell', 'William McIntire', 'Steve McKenna', 'Logan McDonald',
        'ZJAYBRYUN MCNEIL', 'Daniel Meyers', 'Marcus Mitchell', 'Twanna Moore',
        'Darius Morris', 'Sheena Morris', 'Cinterrica Mosby', 'Kristen Moses',
        'Mark Ordoyne', 'Orlando Peyton', 'Stephanie Perez', 'Jeffery Peters',
        'Peter Pollitt', 'Daniel Robalo', 'Rosendo Rodriguez', 'Brian Ross',
        'Joshua Allen Sass', 'Dirmarcus Scott', 'Derek Snyder', 'Brian Skinner',
        'Darrielle Stephens', 'Austin Terry', 'James Tipton', 'Kenneth Thompson',
        'Jaquerus Turner', 'Dadrien Updite', 'Brandon Walker', 'David Ware',
        'Delandro Washington', 'Michael Welch', 'Torrance Wesley', 'John C. Kelly',
        'Jacob Brown', 'Randall Dickerson', 'Dakota DeMoss', 'George Harper',
        'James Vernon McDaniel', 'Marilyn Roberson', 'Ashton Brown', 'Justin Harvey',
        'Kevina Maxie', 'Dvarciea Small', 'Decarlos Washington', 'BENJAMIN BRANTLEY SPEER',
        'Jason Allgrunn', 'William Fitzpatrick', 'Kenny Thompson'
    ]

    entries = []

    # Process text to find entries
    full_text = ' '.join(text_lines)

    # Find each known name and extract surrounding context
    for name in known_names:
        # Look for the name in various forms
        name_patterns = [
            name,
            name.upper(),
            name.lower(),
            name.replace(' Jr', ''),
            name.replace(' SR', ''),
            name.replace(' III', '')
        ]

        for pattern in name_patterns:
            if pattern in full_text:
                # Find the index of this name in the text
                start_idx = full_text.find(pattern)
                if start_idx >= 0:
                    # Extract context around the name (500 chars before and after)
                    context_start = max(0, start_idx - 500)
                    context_end = min(len(full_text), start_idx + 1000)
                    context = full_text[context_start:context_end]

                    # Split context into lines for processing
                    context_lines = [line.strip() for line in context.split() if line.strip()]

                    entry = parse_brady_entry(name, context_lines)
                    entries.append(entry)
                    break  # Found this name, move to next

    # Also look for pattern-based name extraction as backup
    for i, line in enumerate(text_lines):
        # Look for name patterns at start of lines
        name_match = re.match(r'^([A-Z][a-zA-Z]+ [A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)', line)
        if name_match:
            name = name_match.group(1)

            # Skip obvious non-names
            if any(skip in name for skip in ['PDF', 'Click', 'See', 'Update', 'Summary', 'DOCKET', 'CHARGE']):
                continue

            # Skip if we already processed this name
            if any(entry['name'] == name for entry in entries):
                continue

            # Get context lines
            context_lines = text_lines[i:min(i + 5, len(text_lines))]

            entry = parse_brady_entry(name, context_lines)
            entries.append(entry)

    return entries

def main():
    """Main function to clean Brady data."""
    print("Extracting Brady list data from OCRed document...")

    entries = extract_brady_data()

    # Create DataFrame
    df = pd.DataFrame(entries)

    # Save to CSV
    output_path = '/Users/esmelee/analysis/CaddoBradyList/cleaned_brady_list.csv'
    df.to_csv(output_path, index=False)

    print(f"Extracted {len(entries)} Brady entries")
    print(f"Saved cleaned data to: {output_path}")

    # Print summary statistics
    print("\n=== BRADY LIST SUMMARY ===")
    print(f"Total entries: {len(entries)}")

    if len(entries) > 0:
        print(f"\nAgencies represented:")
        agency_counts = df['agency'].value_counts()
        for agency, count in agency_counts.items():
            print(f"  {agency}: {count}")

        print(f"\nTop allegations:")
        allegation_counts = df['allegation'].value_counts().head(10)
        for allegation, count in allegation_counts.items():
            if allegation:
                print(f"  {allegation}: {count}")

        print(f"\nDispositions:")
        disposition_counts = df['disposition'].value_counts()
        for disposition, count in disposition_counts.items():
            if disposition:
                print(f"  {disposition}: {count}")

if __name__ == "__main__":
    main()