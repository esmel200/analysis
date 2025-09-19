#!/usr/bin/env python3

import sys
import os
import re

# Add the virtual environment to the path
venv_path = os.path.join(os.path.dirname(__file__), 'venv', 'lib', 'python3.13', 'site-packages')
if os.path.exists(venv_path):
    sys.path.insert(0, venv_path)

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Use non-interactive backend
plt.switch_backend('Agg')

def clean_pd_allegation_text(allegation):
    """
    Clean and standardize Lafayette PD allegation text for consistent categorization
    """
    if pd.isna(allegation) or allegation == '':
        return 'Unknown'

    # Convert to lowercase and strip whitespace
    allegation = str(allegation).lower().strip()

    # Define mapping for standardization (Lafayette PD specific)
    standard_categories = {
        # Use of Force variations (including excessive force)
        'use_of_force': [
            'excessive force', 'excessive force body worn camera', 'excessive force kh',
            'excessive force simple battery', 'excessive force; rude; unprofessional',
            'use of force', 'use of force professional conduct', 'use of force; false arrest',
            'professional conduct; excessive force', 'simple battery',
            'response to resistance; use of force (officer involved shooting)',
            'response to resistance; use of force body worn camera',
            'professional conduct response to resistance; use of force'
        ],

        # Conduct Unbecoming / CUBO variations
        'conduct_unbecoming': [
            'cubo', 'conduct unbecoming an officer', 'cubo (missing evidence)', 'cubo- failure to take report',
            'conduct unbecoming an officer; insubordination; late reports',
            'conduct unbecoming an officer; interfering with lpso investigation',
            'conduct unbecoming an officer; social media',
            'professional conduct', 'professional conduct and responsibilities',
            'professional conduct conditions of employment',
            'professional conduct; arrest',
            'professional conduct; insubordination', 'professional conduct; media relations',
            'professional conduct; operating while intoxicated', 'professional conduct; social media',
            'ppm; conditions of employment professional conduct general conduct',
            'ppm; leaves of absence professional conduct general conduct',
            'professional conduct (s) motor vehicle insurance (s) body worn camera (e)',
            'professional conduct body worn camera evidence collection; preservation', 'rude and unprofessional', 'rude and unprofessional (je|nb)',
            'rude; unprofessional', 'rude; unprofessional; insubordinate',
            'unprofessional behavior', 'unprofessional conduct'
        ],

        # Officer Involved Shooting
        'officer_involved_shooting': [
            'officer involved shooting', 'ois', 'officer involved',
            'misuse of sick leave; off duty officer involved shooting'
        ],

        # Performance/Duty related
        'performance_duty': [
            'attention to duty', 'failure to perform duties', 'failure to perform duty',
            'failure to act', 'failure to assist', 'inattention to duty',
            'failure to take action', 'failure to supervise',
            'failure to supervise professional conduct', 'poor supervisory judgment',
            'improper supervision', 'improper supervision professional conduct'
        ],

        # Report/Documentation issues
        'report_documentation': [
            'failure to complete proper investigation', 'failure to complete proper report',
            'failure to complete report', 'failure to complete reports',
            'failure to completereports', 'failure to properly investigate',
            'failure to properly investigate incident', 'complete report',
            'preparation of reports', 'reports', 'late reports',
            'accident review', 'failure to report accident',
            'failure to report an accident', 'failure to report damage (gas)',
            'failure to report damage to patrol unit',
            'failure to notify supervisor', 'failure to notify supervisor of property damage',
            'failure to update contact info', 'failure to turn in paperwork',
        ],
        
        # Falsification/Untruthfulness
        'falsification_untruthfulness': [
            'falsifying police reports', 'falsifying records', 'filing false report',
            'falsified information on an accident report', 'false statements',
        ],


        # Search and Seizure issues
        'search_seizure': [
            'improper search', 'illegal search', 'improper patdown',
            'improper vehicle stop and search', 'unauthorized search',
            'arrest', 'false arrest', 'improper arrest', 'unlawful arrest'
        ],

        # Body Worn Camera issues
        'body_camera': [
            'body worn camera', 'body worn camera policy violation',
            'body worn camera; evidence', 'body worn camera; insubordination',
            'body worn camera; pursuit policy; untruthful', 'bwc',
            'pursuit policy body worn camera', 'dash camera',
            'disconnected in car camera system',
            'departmental discipline; (insubordination) professional conduct body worn camera',
            'general conduct professional conduct body worn camera',
            'disclosure of body cam footage', 'discloses of budg camera foot'
        ],

        # Evidence handling
        'evidence_handling': [
            'failure to turn in evidence', 'handling of evidence',
            'improper handling of evidence', 'missing evidence',
            'destruction of evidence', 'not booking seized property',
            'failure to submit summons and evidence',
            'managing recovered property', 'managing recovered, found, or seized property',
            'recovered property', 'lost property', 'missing property', 'professional conduct; handling of evidence',
        ],

        # Vehicle/Pursuit related
        'vehicle_pursuit': [
            'pursuit police', 'pursuit policy', 'pursuit policy violation',
            'violation of pursuit policy', 'pursuit; taser',
            'emergency response; pursuit driving', 'vehicle pursuit',
            'improper traffic stop and pursuit', 'vehicle crashes',
            'operation of police vehicle', 'reckless driving',
            'recklessly operation of a vehicle', 'excessive speed', 'safe speed violation'
        ],

        # Attendance/Schedule issues
        'attendance_schedule': [
            'not reporting for duty', 'court attendance', 'excessive tardiness',
            'failure to honor subpoena', 'failure to honor city court subpoena',
            'failure to report for mandatory meeting', 'left shift early',
            'leaving shift without permission', 'unauthorized absence',
            'unauthorized leave', 'unexcused absence',
            'observance of work schedule', 'failed to attend inservice'
        ],

        # Criminal violations
        'criminal_conduct': [
            'criminal violation', 'theft', 'misappropriation of funds',
            'missing money', 'payroll fraud', 'perjury', 'driving while impaired',
            'operating while intoxicated; crash', 'malfeasance',
            'hit; run in lcg vehicle', 'conduct unbecoming an officer; criminal violation'
        ],

        # Harassment/Intimidation
        'harassment_intimidation': [
            'harassment', 'harrassment', 'intimidation',
            'threatened complainant', 'threats'
        ],

        'biased_policing': [
            'civil rights violation'
        ],

        # Sexual Misconduct/Harassment
        'sexual_misconduct': [
            'sexual harassment', 'sexual misconduct', 'sexual harassment professional conduct'
            'sexual harassment (ns) sexual misconduct (ns) professional conduct (s) internal investigation (s) (truthfulness)'
        ],

        # Insubordination
        'insubordination': [
            'insubordination', 'insubordination; harassment',
            'disobey direct order', 'disobeyed directive',
            'issued unlawful order', 'issuing an unlawful order'
        ],

        # Information/Media violations
        'information_media': [
            'unauthorized release of information to media',
            'unauthorized release of information',
            'release of confidential document',
            'releasing lpd video to third party',
            'clandestine recording', 'improper recording'
        ],

        # Policy violations (general)
        'policy_violations': [
            'drug policy', 'drug screening policy',
            'sick leave policy', 'sick leave violation', 'sick leave misuse',
            'substance abuse policy', 'violation of substance abuse policy',
            'social media', 'political activity',
            'engaging in prohibited political activity',
            'take vehicle policy', 'using pd vehicle for personal use',
            'taser protocol', 'improper use oc spray',
            'violation of informant policy', 'ods violation',
            'violation of ods general order', 'residency requirement'
        ],

        # Administrative/Technical
        'administrative': [
            'failure to upload in', 'fit for duty',
            'managing recovered property', 'red-flex violation',
            'tech management'
        ],

        # Investigations
        'investigation_issues': [
            'illegal investigation', 'unauthorized investigation',
            'interfering with an investigation', 'unauthorized criminal history and background checks'
        ]
    }

    # Find matching category
    for category, keywords in standard_categories.items():
        if allegation in keywords:
            return category.replace('_', ' ').title()

    # If no match found, return original (cleaned)
    return allegation.title()

def perform_regression_analysis(df, allegation_col='allegation_clean', min_cases=10):
    """
    Perform logistic regression analysis to determine relationship between
    allegation types and likelihood of sustain
    """
    print("\n" + "="*60)
    print("STATISTICAL ANALYSIS: ALLEGATION TYPE vs SUSTAIN LIKELIHOOD")
    print("="*60)

    # Filter for allegation types with sufficient cases
    allegation_counts = df[allegation_col].value_counts()
    valid_allegations = allegation_counts[allegation_counts >= min_cases].index

    analysis_df = df[df[allegation_col].isin(valid_allegations)].copy()

    print(f"Analyzing {len(valid_allegations)} allegation types with ≥{min_cases} cases each")
    print(f"Total cases in analysis: {len(analysis_df)}")

    # Create binary outcome variable (1 = sustained, 0 = not sustained)
    analysis_df['sustained_binary'] = (analysis_df['disposition_clean'] == 'sustained').astype(int)

    # Encode allegation types
    le = LabelEncoder()
    analysis_df['allegation_encoded'] = le.fit_transform(analysis_df[allegation_col])

    # Perform logistic regression
    X = analysis_df[['allegation_encoded']]
    y = analysis_df['sustained_binary']

    model = LogisticRegression(random_state=42)
    model.fit(X, y)

    # Get predictions and probabilities
    y_pred_prob = model.predict_proba(X)[:, 1]

    # Calculate odds ratios for each allegation type
    coefficients = model.coef_[0]
    odds_ratios = np.exp(coefficients)

    # Statistical significance test
    from sklearn.metrics import classification_report, roc_auc_score
    auc_score = roc_auc_score(y, y_pred_prob)

    print(f"\\nModel Performance:")
    print(f"AUC-ROC Score: {auc_score:.3f}")

    # Chi-square test for independence
    from scipy.stats import chi2_contingency

    # Create contingency table
    contingency_table = pd.crosstab(analysis_df[allegation_col],
                                  analysis_df['sustained_binary'])

    chi2, p_value, dof, expected = chi2_contingency(contingency_table)

    print(f"\\nChi-square test for independence:")
    print(f"Chi-square statistic: {chi2:.3f}")
    print(f"p-value: {p_value:.6f}")
    print(f"Degrees of freedom: {dof}")

    if p_value < 0.001:
        significance = "highly significant (p < 0.001)"
    elif p_value < 0.01:
        significance = "very significant (p < 0.01)"
    elif p_value < 0.05:
        significance = "significant (p < 0.05)"
    else:
        significance = "not significant (p ≥ 0.05)"

    print(f"Result: {significance}")

    # Calculate sustain rates by allegation type
    sustain_rates = []
    for allegation in valid_allegations:
        subset = analysis_df[analysis_df[allegation_col] == allegation]
        total = len(subset)
        sustained = subset['sustained_binary'].sum()
        rate = (sustained / total) * 100

        # Calculate 95% confidence interval
        if total > 0:
            se = np.sqrt((rate/100) * (1 - rate/100) / total)
            ci_lower = max(0, (rate/100 - 1.96*se) * 100)
            ci_upper = min(100, (rate/100 + 1.96*se) * 100)
        else:
            ci_lower = ci_upper = rate

        sustain_rates.append({
            'allegation': allegation,
            'total_cases': total,
            'sustained_cases': sustained,
            'sustain_rate': rate,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper
        })

    sustain_df = pd.DataFrame(sustain_rates).sort_values('sustain_rate', ascending=False)

    print(f"\\nSustain Rates by Allegation Type (95% Confidence Intervals):")
    print("-" * 65)
    for _, row in sustain_df.iterrows():
        print(f"{row['allegation'][:30]:30} {row['sustain_rate']:5.1f}% "
              f"({row['ci_lower']:4.1f}%-{row['ci_upper']:4.1f}%) "
              f"[{row['sustained_cases']}/{row['total_cases']}]")

    # Identify statistically different groups
    print(f"\\nStatistical Findings:")
    print("-" * 20)

    high_sustain = sustain_df[sustain_df['sustain_rate'] > sustain_df['sustain_rate'].mean() + sustain_df['sustain_rate'].std()]
    low_sustain = sustain_df[sustain_df['sustain_rate'] < sustain_df['sustain_rate'].mean() - sustain_df['sustain_rate'].std()]

    if len(high_sustain) > 0:
        print(f"HIGH SUSTAIN RATE allegations (>{sustain_df['sustain_rate'].mean():.1f}% + 1 SD):")
        for _, row in high_sustain.iterrows():
            print(f"  • {row['allegation']}: {row['sustain_rate']:.1f}%")

    if len(low_sustain) > 0:
        print(f"\\nLOW SUSTAIN RATE allegations (<{sustain_df['sustain_rate'].mean():.1f}% - 1 SD):")
        for _, row in low_sustain.iterrows():
            print(f"  • {row['allegation']}: {row['sustain_rate']:.1f}%")

    return {
        'model': model,
        'sustain_rates_df': sustain_df,
        'auc_score': auc_score,
        'chi2_stat': chi2,
        'p_value': p_value,
        'significance': significance,
        'analysis_df': analysis_df
    }

def create_regression_visualizations(regression_results, output_file):
    """
    Create visualizations for the regression analysis results
    """
    sustain_df = regression_results['sustain_rates_df']

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # 1. Sustain rates with confidence intervals
    ax1 = axes[0, 0]
    y_pos = np.arange(len(sustain_df))

    # Sort by sustain rate for better visualization
    sustain_df_sorted = sustain_df.sort_values('sustain_rate')

    bars = ax1.barh(y_pos, sustain_df_sorted['sustain_rate'],
                   color=['red' if rate > 40 else 'orange' if rate > 25 else 'green'
                          for rate in sustain_df_sorted['sustain_rate']], alpha=0.7)

    # Add confidence interval error bars
    ax1.errorbar(sustain_df_sorted['sustain_rate'], y_pos,
                xerr=[sustain_df_sorted['sustain_rate'] - sustain_df_sorted['ci_lower'],
                      sustain_df_sorted['ci_upper'] - sustain_df_sorted['sustain_rate']],
                fmt='none', color='black', capsize=2, alpha=0.6)

    ax1.set_yticks(y_pos)
    ax1.set_yticklabels([name[:20] + '...' if len(name) > 20 else name
                        for name in sustain_df_sorted['allegation']], fontsize=9)
    ax1.set_xlabel('Sustain Rate (%)')
    ax1.set_title('Sustain Rates by Allegation Type\\n(with 95% Confidence Intervals)', fontweight='bold')
    ax1.grid(True, alpha=0.3)

    # Add value labels
    for i, (bar, rate) in enumerate(zip(bars, sustain_df_sorted['sustain_rate'])):
        ax1.text(rate + 1, bar.get_y() + bar.get_height()/2, f'{rate:.1f}%',
                ha='left', va='center', fontsize=8)

    # 2. Case volume vs sustain rate scatter plot
    ax2 = axes[0, 1]
    scatter = ax2.scatter(sustain_df['total_cases'], sustain_df['sustain_rate'],
                         s=100, alpha=0.6, c=sustain_df['sustain_rate'],
                         cmap='RdYlGn_r')

    ax2.set_xlabel('Total Cases')
    ax2.set_ylabel('Sustain Rate (%)')
    ax2.set_title('Case Volume vs Sustain Rate', fontweight='bold')
    ax2.grid(True, alpha=0.3)

    # Add colorbar
    plt.colorbar(scatter, ax=ax2, label='Sustain Rate (%)')

    # Add labels for outliers
    for _, row in sustain_df.iterrows():
        if row['total_cases'] > sustain_df['total_cases'].quantile(0.75) or \
           row['sustain_rate'] > sustain_df['sustain_rate'].quantile(0.75) or \
           row['sustain_rate'] < sustain_df['sustain_rate'].quantile(0.25):
            ax2.annotate(row['allegation'][:15],
                        (row['total_cases'], row['sustain_rate']),
                        xytext=(5, 5), textcoords='offset points',
                        fontsize=8, alpha=0.8)

    # 3. Distribution of sustain rates
    ax3 = axes[1, 0]
    ax3.hist(sustain_df['sustain_rate'], bins=10, alpha=0.7, color='skyblue', edgecolor='black')
    ax3.axvline(sustain_df['sustain_rate'].mean(), color='red', linestyle='--',
               label=f'Mean: {sustain_df["sustain_rate"].mean():.1f}%')
    ax3.set_xlabel('Sustain Rate (%)')
    ax3.set_ylabel('Number of Allegation Types')
    ax3.set_title('Distribution of Sustain Rates', fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # 4. Statistical summary
    ax4 = axes[1, 1]
    ax4.axis('off')

    # Create summary text
    summary_text = f"""
STATISTICAL ANALYSIS SUMMARY
Lafayette PD (2009-2025)

Chi-square Test:
χ² = {regression_results['chi2_stat']:.2f}
p-value = {regression_results['p_value']:.6f}
Result: {regression_results['significance']}

Model Performance:
AUC-ROC = {regression_results['auc_score']:.3f}

Sustain Rate Statistics:
Mean: {sustain_df['sustain_rate'].mean():.1f}%
Std Dev: {sustain_df['sustain_rate'].std():.1f}%
Min: {sustain_df['sustain_rate'].min():.1f}%
Max: {sustain_df['sustain_rate'].max():.1f}%

Allegation Types Analyzed: {len(sustain_df)}
Total Cases: {sustain_df['total_cases'].sum():,}
Total Sustained: {sustain_df['sustained_cases'].sum():,}

INTERPRETATION:
• There {'IS' if regression_results['p_value'] < 0.05 else 'is NO'} statistically significant
  relationship between allegation type
  and sustain likelihood
• Different allegation types show
  {sustain_df['sustain_rate'].max() - sustain_df['sustain_rate'].min():.1f} percentage point range
  in sustain rates
    """

    ax4.text(0.05, 0.95, summary_text, transform=ax4.transAxes,
            verticalalignment='top', fontsize=10, fontfamily='monospace',
            bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", alpha=0.8))

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

def analyze_lafayette_pd_allegations():
    """
    Analyze allegations in Lafayette PD complaint data
    """

    # Read the data
    print("Loading Lafayette PD complaint data...")
    df = pd.read_csv('../data/cprr_lafayette_pd_2009_2025.csv')

    print(f"Total records: {len(df)}")
    print(f"Date range: 2009-2025")

    # Clean allegations
    df['allegation_clean'] = df['allegation'].apply(clean_pd_allegation_text)

    # Standardize dispositions - Lafayette PD has different disposition categories
    df['disposition_clean'] = df['disposition'].str.lower().str.strip()

    # Handle compound dispositions by taking the first part
    df.loc[df['disposition_clean'].str.contains('unfounded; not sustained', na=False), 'disposition_clean'] = 'unfounded'
    df.loc[df['disposition_clean'].str.contains('sustained; unfounded', na=False), 'disposition_clean'] = 'sustained'
    df.loc[df['disposition_clean'].str.contains('not sustained; sustained', na=False), 'disposition_clean'] = 'sustained'
    df.loc[df['disposition_clean'].str.contains('unfounded; sustained', na=False), 'disposition_clean'] = 'sustained'
    df.loc[df['disposition_clean'].str.contains('sustained; resigned', na=False), 'disposition_clean'] = 'sustained'

    # Create output directory
    os.makedirs('../visualizations', exist_ok=True)

    print("\n" + "="*60)
    print("LAFAYETTE PD COMPLAINT ANALYSIS (2009-2025)")
    print("="*60)

    # 1. ALL COMPLAINTS ANALYSIS
    print("\n1. MOST COMMON COMPLAINT TYPES (ALL CASES)")
    print("-" * 45)

    allegation_counts = df['allegation_clean'].value_counts()
    total_complaints = len(df)

    print(f"Top 15 complaint types out of {total_complaints} total complaints:")
    for i, (allegation, count) in enumerate(allegation_counts.head(15).items(), 1):
        percentage = (count / total_complaints) * 100
        print(f"{i:2}. {allegation}: {count} cases ({percentage:.1f}%)")

    # 2. SUSTAINED COMPLAINTS ANALYSIS
    print("\n2. MOST COMMON COMPLAINT TYPES (SUSTAINED ONLY)")
    print("-" * 48)

    sustained_df = df[df['disposition_clean'] == 'sustained'].copy()
    sustained_counts = sustained_df['allegation_clean'].value_counts()
    total_sustained = len(sustained_df)

    print(f"Top 15 sustained complaint types out of {total_sustained} sustained complaints:")
    for i, (allegation, count) in enumerate(sustained_counts.head(15).items(), 1):
        percentage = (count / total_sustained) * 100
        print(f"{i:2}. {allegation}: {count} cases ({percentage:.1f}%)")

    # 3. DISPOSITION BREAKDOWN
    print("\n3. DISPOSITION BREAKDOWN")
    print("-" * 25)

    disposition_counts = df['disposition_clean'].value_counts()
    for disposition, count in disposition_counts.items():
        percentage = (count / total_complaints) * 100
        print(f"{disposition.title()}: {count} cases ({percentage:.1f}%)")

    # 4. SUSTAIN RATES BY ALLEGATION TYPE
    print("\n4. SUSTAIN RATES BY ALLEGATION TYPE")
    print("-" * 35)

    sustain_rates = []
    for allegation in allegation_counts.head(10).index:
        total_of_type = len(df[df['allegation_clean'] == allegation])
        sustained_of_type = len(df[(df['allegation_clean'] == allegation) &
                                   (df['disposition_clean'] == 'sustained')])
        rate = (sustained_of_type / total_of_type) * 100 if total_of_type > 0 else 0
        sustain_rates.append((allegation, rate, sustained_of_type, total_of_type))

    sustain_rates.sort(key=lambda x: x[1], reverse=True)

    print("Top 10 allegation types by sustain rate:")
    for allegation, rate, sustained, total in sustain_rates:
        print(f"{allegation}: {rate:.1f}% ({sustained}/{total} sustained)")

    # 5. COMPARISON TO LAFAYETTE SO
    print("\n5. COMPARISON: PD vs SO KEY METRICS")
    print("-" * 35)

    pd_sustain_rate = (total_sustained / total_complaints) * 100
    print(f"Lafayette PD overall sustain rate: {pd_sustain_rate:.1f}%")
    print(f"Lafayette SO overall sustain rate: 24.7% (from previous analysis)")
    print(f"Difference: {pd_sustain_rate - 24.7:.1f} percentage points")

    # Perform regression analysis
    regression_results = perform_regression_analysis(df)

    # Create visualizations
    create_pd_allegation_visualizations(df, allegation_counts, sustained_counts,
                                      disposition_counts, sustain_rates)

    # Create regression visualizations
    create_regression_visualizations(regression_results,
                                   '../visualizations/lafayette_pd_regression_analysis.png')

    print(f"\nVisualizations saved to ../visualizations/")
    print("- lafayette_pd_allegations_analysis.png")
    print("- lafayette_pd_regression_analysis.png")

def create_pd_allegation_visualizations(df, allegation_counts, sustained_counts,
                                      disposition_counts, sustain_rates):
    """Create comprehensive visualizations for Lafayette PD allegation analysis"""

    plt.figure(figsize=(20, 12))

    # 1. Top complaint types - all cases
    plt.subplot(2, 4, 1)
    top_15 = allegation_counts.head(15)
    colors = plt.cm.Set3(np.linspace(0, 1, len(top_15)))
    bars = plt.barh(range(len(top_15)), top_15.values, color=colors)
    plt.yticks(range(len(top_15)), [name[:25] + '...' if len(name) > 25 else name
                                    for name in top_15.index], fontsize=8)
    plt.xlabel('Number of Cases')
    plt.title('Top 15 Complaint Types\n(All Cases - Lafayette PD)', fontweight='bold')
    plt.gca().invert_yaxis()

    # Add value labels
    for i, bar in enumerate(bars):
        width = bar.get_width()
        plt.text(width + 1, bar.get_y() + bar.get_height()/2, f'{int(width)}',
                ha='left', va='center', fontsize=7)

    # 2. Top sustained complaints
    plt.subplot(2, 4, 2)
    top_10_sustained = sustained_counts.head(10)
    colors_sus = plt.cm.Reds(np.linspace(0.4, 1, len(top_10_sustained)))
    bars = plt.barh(range(len(top_10_sustained)), top_10_sustained.values, color=colors_sus)
    plt.yticks(range(len(top_10_sustained)),
               [name[:20] + '...' if len(name) > 20 else name
                for name in top_10_sustained.index], fontsize=8)
    plt.xlabel('Number of Sustained Cases')
    plt.title('Top 10 Sustained\nComplaint Types (PD)', fontweight='bold')
    plt.gca().invert_yaxis()

    # Add value labels
    for i, bar in enumerate(bars):
        width = bar.get_width()
        plt.text(width + 0.5, bar.get_y() + bar.get_height()/2, f'{int(width)}',
                ha='left', va='center', fontsize=7)

    # 3. Disposition breakdown pie chart
    plt.subplot(2, 4, 3)
    colors_disp = plt.cm.Pastel1(np.linspace(0, 1, len(disposition_counts)))
    wedges, texts, autotexts = plt.pie(disposition_counts.values,
                                      labels=disposition_counts.index,
                                      autopct='%1.1f%%', startangle=90,
                                      colors=colors_disp)
    plt.title('Disposition Breakdown\n(All Cases - Lafayette PD)', fontweight='bold')

    # Make text smaller
    for text in texts:
        text.set_fontsize(8)
    for autotext in autotexts:
        autotext.set_fontsize(7)
        autotext.set_color('white')
        autotext.set_weight('bold')

    # 4. Sustain rates by allegation type
    plt.subplot(2, 4, 4)
    rates_data = sustain_rates[:10]  # Top 10 by sustain rate
    rates_names = [item[0][:15] + '...' if len(item[0]) > 15 else item[0]
                   for item in rates_data]
    rates_values = [item[1] for item in rates_data]

    colors_rates = ['red' if rate > 40 else 'orange' if rate > 20 else 'green'
                    for rate in rates_values]
    bars = plt.barh(range(len(rates_names)), rates_values, color=colors_rates, alpha=0.7)
    plt.yticks(range(len(rates_names)), rates_names, fontsize=8)
    plt.xlabel('Sustain Rate (%)')
    plt.title('Sustain Rates by\nComplaint Type (PD)', fontweight='bold')
    plt.gca().invert_yaxis()

    # Add percentage labels
    for i, bar in enumerate(bars):
        width = bar.get_width()
        plt.text(width + 1, bar.get_y() + bar.get_height()/2, f'{width:.1f}%',
                ha='left', va='center', fontsize=7)

    # 5. Year over year complaint trends
    plt.subplot(2, 4, 5)

    # Extract year from receive_year
    df['year'] = df['receive_year'].fillna(0).astype(int)

    yearly_complaints = df.groupby('year').size()
    yearly_sustained = df[df['disposition_clean'] == 'sustained'].groupby('year').size()

    valid_years = yearly_complaints.index[(yearly_complaints.index >= 2009) &
                                         (yearly_complaints.index <= 2025)]

    plt.plot(valid_years, yearly_complaints[valid_years], marker='o',
            label='All Complaints', linewidth=2)
    plt.plot(valid_years, yearly_sustained[valid_years].fillna(0), marker='s',
            label='Sustained', linewidth=2)
    plt.xlabel('Year')
    plt.ylabel('Number of Complaints')
    plt.title('PD Complaint Trends\nOver Time', fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)

    # 6. Department/Division breakdown
    plt.subplot(2, 4, 6)

    # Clean up department descriptions
    df['dept_clean'] = df['department_desc'].fillna('Unknown')
    # Simplify department names
    df['dept_clean'] = df['dept_clean'].str.replace('criminal investigations|metro', 'Criminal/Metro', regex=False)

    dept_counts = df['dept_clean'].value_counts().head(8)  # Top 8 departments
    colors_dept = plt.cm.Set2(np.linspace(0, 1, len(dept_counts)))
    bars = plt.bar(range(len(dept_counts)), dept_counts.values, color=colors_dept)
    plt.xticks(range(len(dept_counts)),
               [dept[:10] + '...' if len(dept) > 10 else dept for dept in dept_counts.index],
               rotation=45, ha='right', fontsize=8)
    plt.ylabel('Number of Complaints')
    plt.title('Complaints by\nDepartment/Division', fontweight='bold')

    # Add value labels
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 2, f'{int(height)}',
                ha='center', va='bottom', fontweight='bold', fontsize=8)

    # 7. Top allegation types comparison (all vs sustained)
    plt.subplot(2, 4, 7)
    top_5_all = allegation_counts.head(5)

    all_values = []
    sustained_values = []
    labels = []

    for allegation in top_5_all.index:
        all_count = top_5_all[allegation]
        sustained_count = sustained_counts.get(allegation, 0)

        all_values.append(all_count)
        sustained_values.append(sustained_count)
        labels.append(allegation[:15] + '...' if len(allegation) > 15 else allegation)

    x = np.arange(len(labels))
    width = 0.35

    plt.bar(x - width/2, all_values, width, label='All Cases', alpha=0.7, color='lightblue')
    plt.bar(x + width/2, sustained_values, width, label='Sustained', alpha=0.7, color='darkred')

    plt.xlabel('Complaint Type')
    plt.ylabel('Number of Cases')
    plt.title('Top 5 PD Complaints:\nAll vs Sustained', fontweight='bold')
    plt.xticks(x, labels, rotation=45, ha='right', fontsize=8)
    plt.legend()

    # 8. Summary statistics
    plt.subplot(2, 4, 8)
    plt.axis('off')

    # Calculate key statistics
    total_complaints = len(df)
    total_sustained = len(df[df['disposition_clean'] == 'sustained'])
    overall_sustain_rate = (total_sustained / total_complaints) * 100
    top_complaint = allegation_counts.index[0]
    top_sustained_complaint = sustained_counts.index[0]

    summary_text = f"""
LAFAYETTE PD COMPLAINTS
2009-2025 SUMMARY

Total Complaints: {total_complaints:,}
Total Sustained: {total_sustained:,}
Overall Sustain Rate: {overall_sustain_rate:.1f}%

TOP COMPLAINT TYPES:
1. {top_complaint}
   ({allegation_counts.iloc[0]} cases)

2. {allegation_counts.index[1]}
   ({allegation_counts.iloc[1]} cases)

TOP SUSTAINED:
1. {top_sustained_complaint}
   ({sustained_counts.iloc[0]} cases)

DISPOSITION BREAKDOWN:
• Sustained: {disposition_counts.get('sustained', 0)}
• Unfounded: {disposition_counts.get('unfounded', 0)}
• Not Sustained: {disposition_counts.get('not sustained', 0)}
• Exonerated: {disposition_counts.get('exonerated', 0)}

COMPARISON TO SO:
PD Sustain Rate: {overall_sustain_rate:.1f}%
SO Sustain Rate: 24.7%
Difference: +{overall_sustain_rate - 24.7:.1f}pp
    """

    plt.text(0.05, 0.95, summary_text, transform=plt.gca().transAxes,
            verticalalignment='top', fontsize=9, fontfamily='monospace',
            bbox=dict(boxstyle="round,pad=0.5", facecolor="lightcyan", alpha=0.8))

    plt.tight_layout()
    plt.savefig('../visualizations/lafayette_pd_allegations_analysis.png',
                dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    analyze_lafayette_pd_allegations()