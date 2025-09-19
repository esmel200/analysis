#!/usr/bin/env python3

import pandas as pd
import os

def analyze_uof_demographics():
    """
    Analyze use of force rates by demographic and normalize by population.
    Lafayette Parish demographics: 57.8% white, 28.5% black, 7.61% hispanic
    """

    # Define file paths
    uof_incidents_file = '../data/uof_lafayette_so_2015_2019.csv'
    uof_citizens_file = '../data/uof_citizens_lafayette_so_2015_2019.csv'

    # Population percentages for Lafayette Parish
    population_demographics = {
        'white': 57.8,
        'black': 28.5,
        'hispanic': 7.61,
        'other': 6.09  # Remaining percentage
    }

    # Check if files exist
    if not os.path.exists(uof_incidents_file):
        print(f"UOF incidents file not found: {uof_incidents_file}")
        return

    if not os.path.exists(uof_citizens_file):
        print(f"UOF citizens file not found: {uof_citizens_file}")
        return

    # Read the files
    print("Reading UOF incident data...")
    incidents_df = pd.read_csv(uof_incidents_file)
    print(f"UOF incidents shape: {incidents_df.shape}")

    print("Reading UOF citizen demographic data...")
    citizens_df = pd.read_csv(uof_citizens_file)
    print(f"UOF citizens shape: {citizens_df.shape}")

    # Check if the files have the same number of records
    if len(incidents_df) != len(citizens_df):
        print(f"Warning: Incident count ({len(incidents_df)}) != citizen count ({len(citizens_df)})")

    # Merge the datasets (assuming they're in the same order)
    # If they have matching UIDs, we could join on that instead
    if len(incidents_df) == len(citizens_df):
        combined_df = pd.concat([incidents_df, citizens_df], axis=1)
    else:
        print("Cannot merge - different record counts. Analyzing citizens file only.")
        combined_df = citizens_df

    print(f"\nCombined dataset shape: {combined_df.shape}")
    print(f"Columns: {list(combined_df.columns)}")

    # Analyze demographics
    print("\n" + "="*60)
    print("USE OF FORCE DEMOGRAPHIC ANALYSIS")
    print("="*60)

    # Count by race
    race_counts = combined_df['citizen_race'].value_counts()
    total_incidents = len(combined_df)

    print(f"\nTotal UOF incidents: {total_incidents}")
    print(f"Time period: 2015-2019")

    print("\nRACE BREAKDOWN:")
    print("-" * 40)
    for race, count in race_counts.items():
        percentage = (count / total_incidents) * 100
        print(f"{race.title()}: {count} incidents ({percentage:.1f}%)")

    # Calculate rates normalized by population
    print("\nPOPULATION-NORMALIZED RATES:")
    print("-" * 40)
    print("(Rate = % of UOF incidents / % of population)")

    normalized_rates = {}
    for race, count in race_counts.items():
        uof_percentage = (count / total_incidents) * 100

        # Map race categories to population demographics
        if race.lower() in population_demographics:
            pop_percentage = population_demographics[race.lower()]
            normalized_rate = uof_percentage / pop_percentage
            normalized_rates[race] = normalized_rate

            print(f"{race.title()}:")
            print(f"  UOF incidents: {count} ({uof_percentage:.1f}%)")
            print(f"  Population: {pop_percentage:.1f}%")
            print(f"  Normalized rate: {normalized_rate:.2f}x")
            print()
        else:
            print(f"{race.title()}: No population data available")

    # Summary analysis
    print("SUMMARY ANALYSIS:")
    print("-" * 40)

    # Find the baseline (white rate, typically)
    if 'white' in normalized_rates:
        baseline_rate = normalized_rates['white']
        print(f"Using White rate ({baseline_rate:.2f}x) as baseline:")
        print()

        for race, rate in normalized_rates.items():
            if race.lower() != 'white':
                ratio = rate / baseline_rate
                print(f"{race.title()} residents are {ratio:.1f}x more likely to experience use of force than White residents")

    # INTERSECTIONAL ANALYSIS: Race x Sex
    print("\n" + "="*60)
    print("INTERSECTIONAL ANALYSIS: RACE x SEX")
    print("="*60)
    print("(Assuming 50% male, 50% female population for each race)")

    # Create race-sex combinations
    race_sex_counts = combined_df.groupby(['citizen_race', 'citizen_sex']).size()
    print(f"\nRace-Sex breakdown:")
    print("-" * 30)

    # Calculate expected population percentages for each race-sex combination
    intersectional_analysis = {}

    for (race, sex), count in race_sex_counts.items():
        uof_percentage = (count / total_incidents) * 100

        # Calculate expected population percentage
        if race.lower() in population_demographics:
            race_pop_pct = population_demographics[race.lower()]
            expected_pop_pct = race_pop_pct * 0.5  # Assuming 50/50 gender split

            normalized_rate = uof_percentage / expected_pop_pct if expected_pop_pct > 0 else 0
            intersectional_analysis[f"{race}_{sex}"] = {
                'count': count,
                'uof_pct': uof_percentage,
                'expected_pop_pct': expected_pop_pct,
                'normalized_rate': normalized_rate
            }

            print(f"{race.title()} {sex.title()}:")
            print(f"  UOF incidents: {count} ({uof_percentage:.1f}%)")
            print(f"  Expected population: {expected_pop_pct:.1f}%")
            print(f"  Normalized rate: {normalized_rate:.2f}x")
            print()

    # Compare to baseline (White males)
    if 'white_male' in intersectional_analysis:
        baseline_intersectional = intersectional_analysis['white_male']['normalized_rate']
        print(f"INTERSECTIONAL DISPARITIES (vs White Male baseline {baseline_intersectional:.2f}x):")
        print("-" * 55)

        for combo, data in intersectional_analysis.items():
            if combo != 'white_male':
                race, sex = combo.split('_')
                ratio = data['normalized_rate'] / baseline_intersectional if baseline_intersectional > 0 else 0
                print(f"{race.title()} {sex.title()}: {ratio:.1f}x more likely than White males")

    # Additional gender analysis within races
    print(f"\nGENDER DISPARITIES WITHIN RACES:")
    print("-" * 35)

    for race in combined_df['citizen_race'].dropna().unique():
        race_data = combined_df[combined_df['citizen_race'] == race]
        race_gender_counts = race_data['citizen_sex'].value_counts()
        race_total = len(race_data)

        print(f"\n{str(race).title()} ({race_total} total incidents):")
        for sex, count in race_gender_counts.items():
            pct = (count / race_total) * 100
            print(f"  {str(sex).title()}: {count} ({pct:.1f}%)")

    # Age and gender analysis if available
    if 'citizen_age' in combined_df.columns:
        print(f"\nAGE ANALYSIS:")
        print("-" * 20)
        age_stats = combined_df['citizen_age'].describe()
        print(f"Average age: {age_stats['mean']:.1f} years")
        print(f"Median age: {age_stats['50%']:.1f} years")
        print(f"Age range: {age_stats['min']:.0f} - {age_stats['max']:.0f} years")

    if 'citizen_sex' in combined_df.columns:
        print(f"\nGENDER BREAKDOWN:")
        print("-" * 20)
        gender_counts = combined_df['citizen_sex'].value_counts()
        for gender, count in gender_counts.items():
            percentage = (count / total_incidents) * 100
            print(f"{gender.title()}: {count} incidents ({percentage:.1f}%)")

    # Year-over-year analysis
    if 'occur_year' in combined_df.columns:
        print(f"\nYEAR-OVER-YEAR ANALYSIS:")
        print("-" * 25)
        yearly_counts = combined_df['occur_year'].value_counts().sort_index()
        for year, count in yearly_counts.items():
            print(f"{year}: {count} incidents")

if __name__ == "__main__":
    analyze_uof_demographics()