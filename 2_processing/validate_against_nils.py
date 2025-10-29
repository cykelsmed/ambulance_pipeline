"""Validation script to compare pipeline output with Nils' regional analyses.

This script compares postnummer-level calculations between:
1. Nils' regional Excel files (in /validering/)
2. Pipeline output (in /3_output/current/)

Metrics compared:
- Number of postnumre per region
- Average response time per postnummer
- Number of trips (count) per postnummer
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Color codes for terminal output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'


def load_nils_data(region_name, file_path, sheet_name, skip_rows=3):
    """Load Nils' postnummer data from Excel file.

    Args:
        region_name: Name of region
        file_path: Path to Nils' Excel file
        sheet_name: Name of postnummer sheet
        skip_rows: Number of rows to skip (header rows)

    Returns:
        DataFrame with columns: Postnummer, Antal_ture, Gennemsnit_minutter
    """
    # Read raw data
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

    # Find the header row (contains "Row Labels")
    header_row = None
    for idx, row in df.iterrows():
        if 'Row Labels' in str(row.values):
            header_row = idx
            break

    if header_row is None:
        print(f"{RED}ERROR: Could not find header row in {file_path}{RESET}")
        return None

    # Re-read with proper header
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)

    # Rename columns based on what we find
    col_mapping = {}
    for col in df.columns:
        col_str = str(col).lower()
        if 'row labels' in col_str or col_str == 'unnamed: 0':
            col_mapping[col] = 'Postnummer'
        elif 'count' in col_str:
            col_mapping[col] = 'Antal_ture'
        elif 'average' in col_str or 'gennemsnit' in col_str:
            col_mapping[col] = 'Gennemsnit_minutter'

    df = df.rename(columns=col_mapping)

    # Filter to only relevant columns and remove NaN rows
    df = df[['Postnummer', 'Antal_ture', 'Gennemsnit_minutter']].copy()
    df = df.dropna(subset=['Postnummer'])

    # Convert postnummer to int
    df['Postnummer'] = pd.to_numeric(df['Postnummer'], errors='coerce')
    df = df.dropna(subset=['Postnummer'])
    df['Postnummer'] = df['Postnummer'].astype(int)

    # Convert numeric columns
    df['Antal_ture'] = pd.to_numeric(df['Antal_ture'], errors='coerce')
    df['Gennemsnit_minutter'] = pd.to_numeric(df['Gennemsnit_minutter'], errors='coerce')

    # Remove any remaining NaN rows
    df = df.dropna()

    df['Region'] = region_name

    return df


def load_pipeline_data(file_path):
    """Load pipeline postnummer data."""
    df = pd.read_excel(file_path, sheet_name="Data")
    return df[['Postnummer', 'Antal_ture', 'Gennemsnit_minutter', 'Region']].copy()


def compare_regions(nils_df, pipeline_df, region_name):
    """Compare Nils' data vs Pipeline data for a specific region.

    Returns:
        dict with comparison statistics
    """
    nils_region = nils_df[nils_df['Region'] == region_name].copy()
    pipeline_region = pipeline_df[pipeline_df['Region'] == region_name].copy()

    # Merge on Postnummer
    merged = pd.merge(
        nils_region,
        pipeline_region,
        on='Postnummer',
        how='outer',
        suffixes=('_nils', '_pipeline')
    )

    # Calculate differences
    merged['count_diff'] = merged['Antal_ture_pipeline'] - merged['Antal_ture_nils']
    merged['avg_diff'] = merged['Gennemsnit_minutter_pipeline'] - merged['Gennemsnit_minutter_nils']
    merged['avg_diff_pct'] = (merged['avg_diff'] / merged['Gennemsnit_minutter_nils'] * 100).abs()

    # Statistics
    stats = {
        'region': region_name,
        'nils_count': len(nils_region),
        'pipeline_count': len(pipeline_region),
        'common_postnumre': len(merged.dropna()),
        'only_nils': len(merged[merged['Antal_ture_pipeline'].isna()]),
        'only_pipeline': len(merged[merged['Antal_ture_nils'].isna()]),
        'avg_diff_mean': merged['avg_diff'].mean(),
        'avg_diff_median': merged['avg_diff'].median(),
        'avg_diff_std': merged['avg_diff'].std(),
        'max_avg_diff': merged['avg_diff'].abs().max(),
        'postnumre_within_1pct': len(merged[merged['avg_diff_pct'] <= 1.0]),
        'postnumre_within_5pct': len(merged[merged['avg_diff_pct'] <= 5.0]),
        'postnumre_over_5pct': len(merged[merged['avg_diff_pct'] > 5.0]),
    }

    return stats, merged


def print_summary(stats, merged):
    """Print formatted comparison summary."""
    region = stats['region']

    print(f"\n{BOLD}{'='*80}{RESET}")
    print(f"{BOLD}{BLUE}REGION: {region}{RESET}")
    print(f"{BOLD}{'='*80}{RESET}\n")

    # Count comparison
    print(f"📊 {BOLD}POSTNUMRE COUNT:{RESET}")
    print(f"   Nils:     {stats['nils_count']:3d} postnumre")
    print(f"   Pipeline: {stats['pipeline_count']:3d} postnumre")
    print(f"   Common:   {stats['common_postnumre']:3d} postnumre")
    if stats['only_nils'] > 0:
        print(f"   {YELLOW}Only in Nils: {stats['only_nils']}{RESET}")
    if stats['only_pipeline'] > 0:
        print(f"   {YELLOW}Only in Pipeline: {stats['only_pipeline']}{RESET}")

    # Response time accuracy
    print(f"\n⏱️  {BOLD}AVERAGE RESPONSE TIME COMPARISON:{RESET}")
    print(f"   Mean difference:   {stats['avg_diff_mean']:+.2f} min")
    print(f"   Median difference: {stats['avg_diff_median']:+.2f} min")
    print(f"   Std deviation:     {stats['avg_diff_std']:.2f} min")
    print(f"   Max difference:    {stats['max_avg_diff']:.2f} min")

    print(f"\n✅ {BOLD}ACCURACY ASSESSMENT:{RESET}")
    total = stats['common_postnumre']
    within_1pct = stats['postnumre_within_1pct']
    within_5pct = stats['postnumre_within_5pct']
    over_5pct = stats['postnumre_over_5pct']

    print(f"   Within 1%:  {within_1pct:3d} / {total} ({within_1pct/total*100:.1f}%)")
    print(f"   Within 5%:  {within_5pct:3d} / {total} ({within_5pct/total*100:.1f}%)")
    if over_5pct > 0:
        print(f"   {YELLOW}Over 5%:    {over_5pct:3d} / {total} ({over_5pct/total*100:.1f}%){RESET}")

    # Show top 5 discrepancies
    top_diff = merged.nlargest(5, 'avg_diff_pct')[['Postnummer', 'Gennemsnit_minutter_nils',
                                                      'Gennemsnit_minutter_pipeline', 'avg_diff',
                                                      'avg_diff_pct']]
    if len(top_diff) > 0:
        print(f"\n⚠️  {BOLD}TOP 5 LARGEST DISCREPANCIES:{RESET}")
        for idx, row in top_diff.iterrows():
            print(f"   {row['Postnummer']:4.0f}: Nils={row['Gennemsnit_minutter_nils']:5.1f} min, "
                  f"Pipeline={row['Gennemsnit_minutter_pipeline']:5.1f} min, "
                  f"Diff={row['avg_diff']:+5.1f} min ({row['avg_diff_pct']:.1f}%)")


def main():
    """Run validation comparison."""
    print(f"\n{BOLD}{BLUE}{'='*80}{RESET}")
    print(f"{BOLD}{BLUE}VALIDATION: NILS' ANALYSER vs PIPELINE OUTPUT{RESET}")
    print(f"{BOLD}{BLUE}{'='*80}{RESET}\n")

    # Define file paths
    validering_dir = Path("/Users/adamh/Projects/ambulance_pipeline_pro/validering")
    output_dir = Path("/Users/adamh/Projects/ambulance_pipeline_pro/3_output/current")

    nils_files = [
        ("Hovedstaden", validering_dir / "Hovedstaden20251027.xlsx", "Postnumre"),
        ("Midtjylland", validering_dir / "Midtjylland20251027.xlsx", "Postnummer"),
        ("Sjælland", validering_dir / "RegionSjælland.xlsx", "postnummer"),
        ("Syddanmark", validering_dir / "Syddanmark20251025.xlsx", "Postnummer"),
    ]

    pipeline_file = output_dir / "01_alle_postnumre.xlsx"

    # Check if files exist
    if not pipeline_file.exists():
        print(f"{RED}ERROR: Pipeline output file not found: {pipeline_file}{RESET}")
        return 1

    print(f"📂 Loading pipeline data: {pipeline_file.name}")
    pipeline_df = load_pipeline_data(pipeline_file)
    print(f"   ✅ Loaded {len(pipeline_df)} postnumre\n")

    # Load Nils' data
    print(f"📂 Loading Nils' data from /validering/...")
    nils_dfs = []
    for region_name, file_path, sheet_name in nils_files:
        if not file_path.exists():
            print(f"{YELLOW}   ⚠️  Skipping {region_name} - file not found{RESET}")
            continue

        print(f"   Loading {region_name}...", end=" ")
        df = load_nils_data(region_name, file_path, sheet_name)
        if df is not None:
            nils_dfs.append(df)
            print(f"✅ {len(df)} postnumre")
        else:
            print(f"{RED}❌ Failed{RESET}")

    nils_df = pd.concat(nils_dfs, ignore_index=True)
    print(f"\n   ✅ Total from Nils: {len(nils_df)} postnumre across {len(nils_dfs)} regions\n")

    # Compare each region
    all_stats = []
    for region_name, _, _ in nils_files:
        if region_name not in nils_df['Region'].values:
            continue

        stats, merged = compare_regions(nils_df, pipeline_df, region_name)
        all_stats.append(stats)
        print_summary(stats, merged)

    # Overall summary
    print(f"\n{BOLD}{'='*80}{RESET}")
    print(f"{BOLD}{GREEN}OVERALL VALIDATION SUMMARY{RESET}")
    print(f"{BOLD}{'='*80}{RESET}\n")

    total_common = sum(s['common_postnumre'] for s in all_stats)
    total_within_1pct = sum(s['postnumre_within_1pct'] for s in all_stats)
    total_within_5pct = sum(s['postnumre_within_5pct'] for s in all_stats)
    total_over_5pct = sum(s['postnumre_over_5pct'] for s in all_stats)

    print(f"Regions compared:     {len(all_stats)}")
    print(f"Total postnumre:      {total_common}")
    print(f"\n{BOLD}ACCURACY ACROSS ALL REGIONS:{RESET}")
    print(f"   Within 1%:  {total_within_1pct:3d} / {total_common} ({total_within_1pct/total_common*100:.1f}%)")
    print(f"   Within 5%:  {total_within_5pct:3d} / {total_common} ({total_within_5pct/total_common*100:.1f}%)")
    if total_over_5pct > 0:
        print(f"   Over 5%:    {total_over_5pct:3d} / {total_common} ({total_over_5pct/total_common*100:.1f}%)")

    # Overall verdict
    accuracy_pct = total_within_5pct / total_common * 100
    print(f"\n{BOLD}VERDICT:{RESET}")
    if accuracy_pct >= 95:
        print(f"{GREEN}✅ EXCELLENT VALIDATION - {accuracy_pct:.1f}% of postnumre within 5% difference{RESET}")
    elif accuracy_pct >= 90:
        print(f"{GREEN}✅ GOOD VALIDATION - {accuracy_pct:.1f}% of postnumre within 5% difference{RESET}")
    elif accuracy_pct >= 80:
        print(f"{YELLOW}⚠️  ACCEPTABLE VALIDATION - {accuracy_pct:.1f}% of postnumre within 5% difference{RESET}")
    else:
        print(f"{RED}❌ POOR VALIDATION - Only {accuracy_pct:.1f}% of postnumre within 5% difference{RESET}")

    print(f"\n{BOLD}{'='*80}{RESET}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
