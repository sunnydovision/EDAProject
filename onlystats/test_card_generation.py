#!/usr/bin/env python3
"""
Test script for ONLYSTATS card generation (without ISGEN).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from onlystats.run_onlystats import generate_cards_from_profile
from quis.shared.data_loader import load_data

def main():
    csv_path = "data/adidas_cleaned.csv"
    profile_path = "baseline/auto_eda_agent/output_adidas/step1_profiling/profile.json"
    
    print("Testing ONLYSTATS card generation...")
    print(f"CSV: {csv_path}")
    print(f"Profile: {profile_path}")
    print()
    
    df = load_data(csv_path)
    cards = generate_cards_from_profile(df, profile_path, top_k=20)
    
    print(f"\n{'='*70}")
    print(f"Successfully generated {len(cards)} cards")
    print(f"{'='*70}")

if __name__ == "__main__":
    main()
