#!/usr/bin/env python3
"""Quick test script for B-priority analysis functions."""

import sys
from pathlib import Path

# Add processing directory to path
sys.path.insert(0, str(Path(__file__).parent / '2_processing'))

from analyzers.b_priority_analysis import (
    analyze_b_geographic,
    analyze_b_temporal,
    analyze_b_yearly_trends,
    analyze_b_to_a_escalations
)

def main():
    """Test B-priority analysis functions."""
    output_dir = Path('3_output/current')

    print("Testing B-priority analysis functions...")
    print("=" * 60)

    # Test 1: Geographic analysis
    print("\n[1/4] Testing geographic hotspots analysis...")
    try:
        result = analyze_b_geographic(output_dir)
        if result.get('status') == 'success':
            print(f"   ✓ Success: {result['total_postal_codes']} postal codes")
            print(f"   Worst: {result['worst_postal_code']['postnummer']} ({result['worst_postal_code']['median_minutes']} min)")
        else:
            print(f"   ⚠ Failed: {result.get('reason', 'unknown')}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Test 2: Temporal analysis
    print("\n[2/4] Testing temporal patterns analysis...")
    try:
        result = analyze_b_temporal(output_dir)
        if result.get('status') == 'success':
            print(f"   ✓ Success: {result['regions_processed']} regions")
        else:
            print(f"   ⚠ Failed: {result.get('reason', 'unknown')}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Test 3: Yearly trends
    print("\n[3/4] Testing yearly trends analysis...")
    try:
        result = analyze_b_yearly_trends(output_dir)
        if result.get('status') == 'success':
            years = result['years_analyzed']
            trend = result.get('national_trend_percent')
            print(f"   ✓ Success: {years[0]}-{years[-1]} ({trend:+.1f}% change)")
        else:
            print(f"   ⚠ Failed: {result.get('reason', 'unknown')}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Test 4: B→A escalations
    print("\n[4/4] Testing B→A escalation analysis...")
    try:
        result = analyze_b_to_a_escalations(output_dir)
        if result.get('status') == 'success':
            print(f"   ✓ Success: {result['escalation_rate']:.1f}% upgrade rate")
        elif result.get('status') == 'no_escalations':
            print("   → No escalations found (expected for some regions)")
        else:
            print(f"   ⚠ Failed: {result.get('reason', 'unknown')}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    print("\n" + "=" * 60)
    print("Test complete! Check 3_output/current/ for generated files.")

if __name__ == '__main__':
    main()
