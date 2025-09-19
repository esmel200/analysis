#!/usr/bin/env python3
"""
Test script to verify the enhanced regression analysis functionality
"""

import sys
import os

# Add the virtual environment to the path
venv_path = os.path.join(os.path.dirname(__file__), 'venv', 'lib', 'python3.13', 'site-packages')
if os.path.exists(venv_path):
    sys.path.insert(0, venv_path)

def test_pd_analysis():
    """Test Lafayette PD regression analysis"""
    print("Testing Lafayette PD regression analysis...")
    try:
        from analyze_pd_allegations import analyze_lafayette_pd_allegations
        analyze_lafayette_pd_allegations()
        print("✓ Lafayette PD analysis completed successfully")
    except Exception as e:
        print(f"✗ Lafayette PD analysis failed: {e}")

def test_so_analysis():
    """Test Lafayette SO regression analysis"""
    print("\nTesting Lafayette SO regression analysis...")
    try:
        from analyze_allegations import analyze_lafayette_allegations
        analyze_lafayette_allegations()
        print("✓ Lafayette SO analysis completed successfully")
    except Exception as e:
        print(f"✗ Lafayette SO analysis failed: {e}")

if __name__ == "__main__":
    print("Testing enhanced allegation analysis scripts with regression...")
    print("=" * 60)

    test_pd_analysis()
    test_so_analysis()

    print("\n" + "=" * 60)
    print("Testing complete!")
    print("\nThe enhanced scripts now include:")
    print("• Logistic regression analysis")
    print("• Chi-square tests for statistical significance")
    print("• Confidence intervals for sustain rates")
    print("• AUC-ROC model performance metrics")
    print("• Enhanced visualizations with statistical plots")