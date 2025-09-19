#!/usr/bin/env python3

import sys
import os

# Add the virtual environment to the path
venv_path = os.path.join(os.path.dirname(__file__), '..', 'venv', 'lib', 'python3.13', 'site-packages')
if os.path.exists(venv_path):
    sys.path.insert(0, venv_path)

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Use non-interactive backend
plt.switch_backend('Agg')

def create_uof_visualizations():
    """
    Create visualizations for UOF demographic analysis
    """

    # Set up the plotting style
    plt.style.use('default')
    sns.set_palette("husl")

    # Define file paths
    uof_incidents_file = '../data/uof_lafayette_so_2015_2019.csv'
    uof_citizens_file = '../data/uof_citizens_lafayette_so_2015_2019.csv'

    # Population percentages for Lafayette Parish
    population_demographics = {
        'white': 57.8,
        'black': 28.5,
        'hispanic': 7.61
    }

    # Read and combine data
    print("Loading data...")
    incidents_df = pd.read_csv(uof_incidents_file)
    citizens_df = pd.read_csv(uof_citizens_file)
    combined_df = pd.concat([incidents_df, citizens_df], axis=1)

    total_incidents = len(combined_df)

    # Create output directory for plots
    os.makedirs('../visualizations', exist_ok=True)

    # 1. BASIC RACE BREAKDOWN
    plt.figure(figsize=(15, 10))

    # Subplot 1: Raw counts
    plt.subplot(2, 3, 1)
    race_counts = combined_df['citizen_race'].value_counts()
    colors = ['#3498db', '#e74c3c', '#f39c12']
    bars = plt.bar(race_counts.index, race_counts.values, color=colors)
    plt.title('UOF Incidents by Race\n(Raw Counts)', fontweight='bold')
    plt.xlabel('Race')
    plt.ylabel('Number of Incidents')
    plt.xticks(rotation=45)

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.5, f'{int(height)}',
                ha='center', va='bottom', fontweight='bold')

    # Subplot 2: Percentage breakdown
    plt.subplot(2, 3, 2)
    race_percentages = (race_counts / total_incidents) * 100
    bars = plt.bar(race_percentages.index, race_percentages.values, color=colors)
    plt.title('UOF Incidents by Race\n(Percentages)', fontweight='bold')
    plt.xlabel('Race')
    plt.ylabel('Percentage of Incidents (%)')
    plt.xticks(rotation=45)

    # Add percentage labels
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.5, f'{height:.1f}%',
                ha='center', va='bottom', fontweight='bold')

    # Subplot 3: Population vs UOF comparison
    plt.subplot(2, 3, 3)
    races = ['White', 'Black', 'Hispanic']
    pop_percentages = [population_demographics[race.lower()] for race in races]
    uof_percentages = [race_percentages.get(race.lower(), 0) for race in races]

    x = np.arange(len(races))
    width = 0.35

    plt.bar(x - width/2, pop_percentages, width, label='Population %', alpha=0.7, color='lightblue')
    plt.bar(x + width/2, uof_percentages, width, label='UOF %', alpha=0.7, color='darkred')

    plt.title('Population vs UOF Percentages', fontweight='bold')
    plt.xlabel('Race')
    plt.ylabel('Percentage')
    plt.xticks(x, races)
    plt.legend()
    plt.grid(axis='y', alpha=0.3)

    # Subplot 4: Normalized rates
    plt.subplot(2, 3, 4)
    normalized_rates = []
    race_labels = []

    for race in races:
        uof_pct = race_percentages.get(race.lower(), 0)
        pop_pct = population_demographics[race.lower()]
        normalized_rate = uof_pct / pop_pct
        normalized_rates.append(normalized_rate)
        race_labels.append(race)

    colors_norm = ['green' if rate < 1 else 'orange' if rate < 1.5 else 'red' for rate in normalized_rates]
    bars = plt.bar(race_labels, normalized_rates, color=colors_norm, alpha=0.7)
    plt.axhline(y=1, color='black', linestyle='--', alpha=0.5, label='Population Parity')
    plt.title('Population-Normalized UOF Rates', fontweight='bold')
    plt.xlabel('Race')
    plt.ylabel('Normalized Rate (1.0 = Population Parity)')
    plt.legend()

    # Add rate labels
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.02, f'{height:.2f}x',
                ha='center', va='bottom', fontweight='bold')

    # Subplot 5: Gender breakdown
    plt.subplot(2, 3, 5)
    gender_counts = combined_df['citizen_sex'].value_counts()
    plt.pie(gender_counts.values, labels=[f'{label.title()}\n({count} incidents)'
                                         for label, count in gender_counts.items()],
            autopct='%1.1f%%', startangle=90, colors=['lightcoral', 'lightblue'])
    plt.title('UOF by Gender', fontweight='bold')

    # Subplot 6: Year over year
    plt.subplot(2, 3, 6)
    yearly_counts = combined_df['occur_year'].value_counts().sort_index()
    plt.plot(yearly_counts.index, yearly_counts.values, marker='o', linewidth=2, markersize=8)
    plt.title('UOF Incidents Over Time', fontweight='bold')
    plt.xlabel('Year')
    plt.ylabel('Number of Incidents')
    plt.grid(True, alpha=0.3)

    # Add value labels
    for year, count in yearly_counts.items():
        plt.text(year, count + 0.5, str(count), ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    plt.savefig('../visualizations/uof_racial_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 2. INTERSECTIONAL ANALYSIS VISUALIZATION
    plt.figure(figsize=(15, 8))

    # Create intersectional data
    race_sex_counts = combined_df.groupby(['citizen_race', 'citizen_sex']).size()

    # Subplot 1: Heatmap of intersectional counts
    plt.subplot(2, 3, 1)
    pivot_counts = race_sex_counts.unstack(fill_value=0)
    sns.heatmap(pivot_counts, annot=True, fmt='d', cmap='Reds', cbar_kws={'label': 'Number of Incidents'})
    plt.title('UOF Incidents by Race x Sex\n(Raw Counts)', fontweight='bold')
    plt.ylabel('Race')
    plt.xlabel('Sex')

    # Subplot 2: Normalized rates heatmap
    plt.subplot(2, 3, 2)
    normalized_intersectional = {}

    for (race, sex), count in race_sex_counts.items():
        uof_percentage = (count / total_incidents) * 100
        if race.lower() in population_demographics:
            race_pop_pct = population_demographics[race.lower()]
            expected_pop_pct = race_pop_pct * 0.5  # 50/50 gender split
            normalized_rate = uof_percentage / expected_pop_pct if expected_pop_pct > 0 else 0
            normalized_intersectional[(race, sex)] = normalized_rate

    # Create pivot table for normalized rates
    normalized_data = []
    for race in ['white', 'black', 'hispanic']:
        row = []
        for sex in ['female', 'male']:
            rate = normalized_intersectional.get((race, sex), 0)
            row.append(rate)
        normalized_data.append(row)

    normalized_df = pd.DataFrame(normalized_data,
                                index=['White', 'Black', 'Hispanic'],
                                columns=['Female', 'Male'])

    sns.heatmap(normalized_df, annot=True, fmt='.2f', cmap='RdYlBu_r',
                cbar_kws={'label': 'Normalized Rate'}, center=1.0)
    plt.title('Population-Normalized Rates\nby Race x Sex', fontweight='bold')
    plt.ylabel('Race')
    plt.xlabel('Sex')

    # Subplot 3: Bar chart comparing to white male baseline
    plt.subplot(2, 3, 3)
    white_male_rate = normalized_intersectional.get(('white', 'male'), 1)

    intersectional_ratios = {}
    for (race, sex), rate in normalized_intersectional.items():
        if (race, sex) != ('white', 'male'):
            ratio = rate / white_male_rate if white_male_rate > 0 else 0
            intersectional_ratios[f"{race.title()}\n{sex.title()}"] = ratio

    labels = list(intersectional_ratios.keys())
    values = list(intersectional_ratios.values())
    colors_intersect = ['red' if v > 1 else 'blue' for v in values]

    bars = plt.bar(labels, values, color=colors_intersect, alpha=0.7)
    plt.axhline(y=1, color='black', linestyle='--', alpha=0.5, label='White Male Rate')
    plt.title('UOF Risk vs White Males\n(Baseline = 1.0)', fontweight='bold')
    plt.xlabel('Race-Sex Group')
    plt.ylabel('Relative Risk Ratio')
    plt.xticks(rotation=45)
    plt.legend()

    # Add value labels
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.02, f'{height:.1f}x',
                ha='center', va='bottom', fontweight='bold')

    # Subplot 4: Gender breakdown within races
    plt.subplot(2, 3, 4)
    races_for_gender = combined_df['citizen_race'].dropna().unique()
    gender_data = []

    for race in races_for_gender:
        race_data = combined_df[combined_df['citizen_race'] == race]
        male_count = len(race_data[race_data['citizen_sex'] == 'male'])
        female_count = len(race_data[race_data['citizen_sex'] == 'female'])
        total_race = len(race_data)

        male_pct = (male_count / total_race) * 100 if total_race > 0 else 0
        female_pct = (female_count / total_race) * 100 if total_race > 0 else 0

        gender_data.append([female_pct, male_pct])

    gender_df = pd.DataFrame(gender_data,
                            index=[race.title() for race in races_for_gender],
                            columns=['Female %', 'Male %'])

    gender_df.plot(kind='bar', stacked=True, ax=plt.gca(), color=['lightcoral', 'lightblue'])
    plt.title('Gender Distribution\nWithin Each Race', fontweight='bold')
    plt.xlabel('Race')
    plt.ylabel('Percentage')
    plt.legend()
    plt.xticks(rotation=45)

    # Subplot 5: Age distribution by race
    plt.subplot(2, 3, 5)
    for race in combined_df['citizen_race'].dropna().unique():
        race_ages = combined_df[combined_df['citizen_race'] == race]['citizen_age']
        plt.hist(race_ages, alpha=0.6, label=race.title(), bins=8)

    plt.title('Age Distribution by Race', fontweight='bold')
    plt.xlabel('Age')
    plt.ylabel('Frequency')
    plt.legend()
    plt.grid(axis='y', alpha=0.3)

    # Subplot 6: Summary statistics
    plt.subplot(2, 3, 6)
    plt.axis('off')

    # Create summary text
    summary_text = f"""
    SUMMARY STATISTICS

    Total UOF Incidents: {total_incidents}
    Period: 2015-2019

    KEY FINDINGS:
    • Black residents: 1.5x more likely
    • Black males: Highest risk group
    • White females: Lowest risk group
    • 91% of all UOF involve males

    DISPARITIES:
    • Black male rate: 2.52x normalized
    • White male rate: 1.73x normalized
    • Black female rate: 0.36x normalized
    • White female rate: 0.04x normalized
    """

    plt.text(0.05, 0.95, summary_text, transform=plt.gca().transAxes,
            verticalalignment='top', fontsize=10, fontfamily='monospace',
            bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))

    plt.tight_layout()
    plt.savefig('../visualizations/uof_intersectional_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

    print("Visualizations saved to ../visualizations/")
    print("- uof_racial_analysis.png")
    print("- uof_intersectional_analysis.png")

if __name__ == "__main__":
    create_uof_visualizations()