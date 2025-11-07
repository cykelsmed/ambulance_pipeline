#!/usr/bin/env python3
"""
Multi-Region Temporal Analysis Runner
Runs temporal analyses (time-of-day and seasonal) for all 5 Danish regions
"""

import sys
import yaml
import pandas as pd
from pathlib import Path
from datetime import datetime

# Add processing modules to path
sys.path.insert(0, str(Path(__file__).parent / '2_processing'))

from analyzers.temporal_analysis import analyze_rush_hour, analyze_seasonal

def load_regional_config():
    """Load regional configuration from YAML"""
    config_path = Path(__file__).parent / '2_processing' / 'regional_config.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def convert_danish_months_to_numeric(df, month_col, danish_months_map):
    """Convert Danish month names to numeric (1-12)"""
    df = df.copy()
    df[month_col] = df[month_col].map(danish_months_map)
    return df

def run_region_temporal_analysis(region_name, region_config, global_config):
    """Run temporal analyses for a single region"""

    print(f"\n{'='*80}")
    print(f"PROCESSING REGION: {region_name}")
    print(f"{'='*80}\n")

    # Load data
    file_path = Path(region_config['file'])
    sheet_name = region_config['sheet']

    print(f"Loading data from: {file_path}")
    print(f"Sheet: {sheet_name}")

    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        print(f"Loaded {len(df):,} rows")

        # Get column mappings
        cols = region_config['columns']
        timestamp_col = cols['timestamp']
        response_col = cols['response_time']
        priority_col = cols['priority']
        month_col = cols['month']

        # Handle Danish month names if needed
        if region_config.get('month_type') == 'danish':
            print(f"Converting Danish month names to numeric...")
            df = convert_danish_months_to_numeric(
                df, month_col, global_config['danish_months']
            )

        # Filter for A-priority cases
        print(f"Filtering for A-priority cases...")
        df_a = df[df[priority_col] == 'A'].copy()
        print(f"  A-cases: {len(df_a):,} ({100*len(df_a)/len(df):.1f}%)")

        # Convert response time to numeric (handles Syddanmark's empty strings)
        print(f"Converting response times to numeric...")
        df_a[response_col] = pd.to_numeric(df_a[response_col], errors='coerce')
        valid_response = df_a[response_col].notna().sum()
        print(f"  Valid response times: {valid_response:,} ({100*valid_response/len(df_a):.1f}%)")

        # Drop rows with invalid response times
        df_a = df_a[df_a[response_col].notna()].copy()

        # Extract hour from timestamp
        print(f"Extracting hour from timestamp...")
        # Handle different timestamp formats
        if pd.api.types.is_datetime64_any_dtype(df_a[timestamp_col]):
            # Already datetime - extract hour directly
            df_a['Hour'] = df_a[timestamp_col].dt.hour
        elif df_a[timestamp_col].dtype == 'object':
            # Check if values are datetime.time objects
            sample = df_a[timestamp_col].dropna().iloc[0] if len(df_a[timestamp_col].dropna()) > 0 else None
            if sample is not None and hasattr(sample, 'hour') and not hasattr(sample, 'date'):
                # It's a time object (has hour but not date) - extract directly
                df_a['Hour'] = df_a[timestamp_col].apply(lambda x: x.hour if pd.notna(x) and hasattr(x, 'hour') else None)
            else:
                # Try converting to datetime
                df_a['Hour'] = pd.to_datetime(df_a[timestamp_col], errors='coerce').dt.hour
        else:
            # Try converting to datetime
            df_a['Hour'] = pd.to_datetime(df_a[timestamp_col], errors='coerce').dt.hour

        # Filter out rows where hour extraction failed
        before_hour_filter = len(df_a)
        df_a = df_a[df_a['Hour'].notna()].copy()
        if len(df_a) < before_hour_filter:
            print(f"  Removed {before_hour_filter - len(df_a):,} rows with invalid hour ({100*len(df_a)/before_hour_filter:.1f}% remaining)")

        # Prepare for analysis - rename columns to match existing analyze functions
        df_a = df_a.rename(columns={
            response_col: 'ResponstidMinutter',
            month_col: 'Måned' if region_config['month_type'] != 'danish' else month_col
        })

        # If we renamed month column for Hovedstaden, rename it to standard name
        if 'Maaned' in df_a.columns:
            df_a = df_a.rename(columns={'Maaned': 'Måned'})

        # Run Rush Hour Analysis
        print(f"\nRunning time-of-day analysis...")
        output_dir = Path(global_config['output']['directory'])

        # Create temporary CSV for analysis
        temp_file = output_dir / f'temp_{region_name}_data.csv'
        df_a.to_csv(temp_file, index=False)

        # Run analyses with region-specific output prefix
        from analyzers.temporal_analysis import (
            calculate_hourly_stats,
            calculate_monthly_stats
        )

        # Helper function for categorization
        def categorize_response_time(df, col_name='Median_minutter'):
            """Categorize response times into green/yellow/red"""
            df = df.copy()
            def categorize(val):
                if val < 10:
                    return 'Grøn'
                elif val <= 15:
                    return 'Gul'
                else:
                    return 'Rød'
            df['Kategori'] = df[col_name].apply(categorize)
            return df

        # Time-of-day analysis
        hourly_stats = calculate_hourly_stats(df_a)
        hourly_stats = categorize_response_time(hourly_stats)

        # Add time period labels
        def get_period(hour):
            if 2 <= hour <= 5:
                return 'Nat'
            elif 6 <= hour <= 8:
                return 'Morgen'
            elif 9 <= hour <= 11:
                return 'Formiddag'
            elif hour == 12:
                return 'Middag'
            elif 13 <= hour <= 17:
                return 'Eftermiddag'
            elif 18 <= hour <= 23:
                return 'Aften'
            else:
                return 'Nat'

        # Note: calculate_hourly_stats returns 'Time' not 'Hour'
        hourly_stats['Periode'] = hourly_stats['Time'].apply(get_period)
        # Convert Time to int before formatting (handles float types from NaN values)
        hourly_stats['Time_label'] = hourly_stats['Time'].apply(lambda h: f"{int(h):02d}:00-{(int(h)+1)%24:02d}:00")

        # Export time-of-day results
        output_prefix = f"{region_name}_"
        excel_file = output_dir / f"{output_prefix}05_responstid_per_time.xlsx"
        hourly_stats.to_excel(excel_file, index=False, engine='openpyxl')
        print(f"  ✓ Saved: {excel_file}")

        fund_file = output_dir / f"{output_prefix}05_responstid_per_time_FUND.txt"
        # Simple fund text
        with open(fund_file, 'w', encoding='utf-8') as f:
            f.write(f"TIDSMÆSSIGE ANALYSER - TID-PÅ-DØGNET\n")
            f.write(f"Region: {region_name}\n")
            f.write(f"A-kørsler analyseret: {len(df_a):,}\n\n")

            best_hour = hourly_stats.loc[hourly_stats['Median_minutter'].idxmin()]
            worst_hour = hourly_stats.loc[hourly_stats['Median_minutter'].idxmax()]

            f.write(f"Bedste time: kl. {int(best_hour['Time']):02d}:00 ({best_hour['Median_minutter']:.1f} min)\n")
            f.write(f"Værste time: kl. {int(worst_hour['Time']):02d}:00 ({worst_hour['Median_minutter']:.1f} min)\n")
            f.write(f"Variation: {100*(worst_hour['Median_minutter']-best_hour['Median_minutter'])/best_hour['Median_minutter']:.1f}%\n")
        print(f"  ✓ Saved: {fund_file}")

        dw_file = output_dir / f"{output_prefix}DATAWRAPPER_responstid_per_time.csv"
        dw_data = hourly_stats[['Time_label', 'Median_minutter', 'Antal_ture', 'Kategori', 'Periode']].copy()
        dw_data.to_csv(dw_file, index=False)
        print(f"  ✓ Saved: {dw_file}")

        # Seasonal analysis
        print(f"\nRunning seasonal analysis...")
        monthly_stats = calculate_monthly_stats(df_a, month_col='Måned')
        monthly_stats = categorize_response_time(monthly_stats, col_name='Median_minutter')

        # Export seasonal results
        excel_file = output_dir / f"{output_prefix}06_responstid_per_maaned.xlsx"
        monthly_stats.to_excel(excel_file, index=False, engine='openpyxl')
        print(f"  ✓ Saved: {excel_file}")

        fund_file = output_dir / f"{output_prefix}06_responstid_per_maaned_FUND.txt"
        with open(fund_file, 'w', encoding='utf-8') as f:
            f.write(f"TIDSMÆSSIGE ANALYSER - SÆSONVARIATION\n")
            f.write(f"Region: {region_name}\n")
            f.write(f"A-kørsler analyseret: {len(df_a):,}\n\n")

            best_month = monthly_stats.loc[monthly_stats['Median_minutter'].idxmin()]
            worst_month = monthly_stats.loc[monthly_stats['Median_minutter'].idxmax()]

            f.write(f"Bedste måned: {best_month['Maaned_navn']} ({best_month['Median_minutter']:.1f} min)\n")
            f.write(f"Værste måned: {worst_month['Maaned_navn']} ({worst_month['Median_minutter']:.1f} min)\n")
            f.write(f"Variation: {100*(worst_month['Median_minutter']-best_month['Median_minutter'])/best_month['Median_minutter']:.1f}%\n")
        print(f"  ✓ Saved: {fund_file}")

        dw_file = output_dir / f"{output_prefix}DATAWRAPPER_responstid_per_maaned.csv"
        dw_data = monthly_stats[['Maaned_navn', 'Median_minutter', 'Antal_ture', 'Kategori', 'Sæson']].copy()
        dw_data.to_csv(dw_file, index=False)
        print(f"  ✓ Saved: {dw_file}")

        # Clean up temp file
        if temp_file.exists():
            temp_file.unlink()

        print(f"\n✅ {region_name} temporal analyses completed successfully!")
        return True

    except Exception as e:
        print(f"\n❌ ERROR processing {region_name}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main execution"""
    print("="*80)
    print("MULTI-REGION TEMPORAL ANALYSIS")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Load configurations
    config = load_regional_config()

    # Load main config for output directory
    from config import load_config
    main_config = load_config()
    config['output'] = main_config['output']

    # Process each region
    regions = config['regions']
    results = {}

    for region_name, region_config in regions.items():
        success = run_region_temporal_analysis(region_name, region_config, config)
        results[region_name] = success

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    successful = sum(results.values())
    total = len(results)

    for region, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{region:<15}: {status}")

    print(f"\nCompleted: {successful}/{total} regions")
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return 0 if successful == total else 1

if __name__ == '__main__':
    sys.exit(main())
