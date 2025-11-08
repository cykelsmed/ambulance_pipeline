"""Yearly analysis module for ambulance response times.

This module analyzes response times broken down by:
- Year (2021-2025)
- Region (all 5 regions)
- Combined statistics
"""
import pandas as pd
import numpy as np
import yaml
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def load_all_regional_raw_data(regional_data_cache=None):
    """Load raw data from all 5 regions with standardized columns.

    Args:
        regional_data_cache: Pre-loaded regional data dictionary (optional)

    Returns:
        DataFrame with columns: Region, Year, ResponstidMinutter, Priority
    """
    # Load regional config
    config_path = Path(__file__).parent.parent / 'regional_config.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    all_data = []

    for region_name, region_config in config['regions'].items():
        try:
            logger.info(f"Loading {region_name}...")

            # Use cached data if available
            if regional_data_cache and region_name in regional_data_cache:
                df = regional_data_cache[region_name].copy()
                logger.info(f"  Using cached data for {region_name}")
            else:
                # Fallback: Load data from Excel
                # Fix file path for Nordjylland (updated filename)
                file_path = region_config['file']
                if 'Nordjylland20251027' in file_path:
                    file_path = file_path.replace('20251027', '20251029')

                file_path = Path(file_path)
                if not file_path.exists():
                    logger.warning(f"File not found: {file_path}")
                    continue

                sheet_name = region_config['sheet']

                # Load data
                df = pd.read_excel(file_path, sheet_name=sheet_name)

            # Get column mappings
            cols = region_config['columns']
            response_col = cols['response_time']
            priority_col = cols['priority']

            # Check if response column exists, otherwise find it
            if response_col not in df.columns:
                possible_cols = [c for c in df.columns
                               if 'minut' in c.lower() and 'respons' in c.lower()]
                if possible_cols:
                    response_col = possible_cols[0]
                    logger.info(f"  Using alternative response column: {response_col}")

            # Convert response time to numeric
            df[response_col] = pd.to_numeric(df[response_col], errors='coerce')

            # Remove invalid response times
            df = df[df[response_col].notna()].copy()
            df = df[df[response_col] > 0].copy()

            # Find year column
            year_col = None
            for possible_year in ['År', 'Aar', 'Year', 'aar', 'År_HændelseOprettet']:
                if possible_year in df.columns:
                    year_col = possible_year
                    break

            if year_col:
                df['Year'] = pd.to_numeric(df[year_col], errors='coerce')
            else:
                # Try to extract year from timestamp
                timestamp_col = cols['timestamp']
                if timestamp_col in df.columns:
                    df['Year'] = pd.to_datetime(df[timestamp_col], errors='coerce').dt.year
                else:
                    logger.warning(f"  No year column found for {region_name}")
                    continue

            # Standardize column names
            df = df.rename(columns={
                response_col: 'ResponstidMinutter',
                priority_col: 'Priority'
            })
            df['Region'] = region_name

            # Keep only needed columns
            df = df[['Region', 'Year', 'ResponstidMinutter', 'Priority']].copy()

            # Remove rows with missing year
            df = df[df['Year'].notna()].copy()
            df = df[df['Year'] >= 2021].copy()
            df = df[df['Year'] <= 2025].copy()

            all_data.append(df)

            logger.info(f"  ✓ Loaded {len(df):,} rows from {region_name}")

        except Exception as e:
            logger.error(f"  ✗ Failed to load {region_name}: {e}")
            continue

    if not all_data:
        raise ValueError("No data could be loaded from any region")

    # Combine all data
    combined_df = pd.concat(all_data, ignore_index=True)
    logger.info(f"Total combined: {len(combined_df):,} rows from {len(all_data)} regions")

    return combined_df


def analyze_yearly_by_region(df, priority='A'):
    """Analyze response times by year and region.

    Args:
        df: DataFrame with Region, Year, ResponstidMinutter, Priority columns
        priority: Priority level to filter ('A', 'B', or 'all')

    Returns:
        tuple: (yearly_by_region_df, yearly_summary_df, regional_summary_df)
    """
    logger.info(f"Analyzing yearly data for priority={priority}...")

    # Filter by priority if specified
    if priority != 'all':
        df_filtered = df[df['Priority'] == priority].copy()
        logger.info(f"  Filtered to {len(df_filtered):,} {priority}-priority cases")
    else:
        df_filtered = df.copy()
        logger.info(f"  Using all priorities: {len(df_filtered):,} cases")

    # 1. Year-by-region matrix
    yearly_by_region = df_filtered.groupby(['Year', 'Region'])['ResponstidMinutter'].agg([
        ('Antal_kørsler', 'count'),
        ('Gennemsnit_minutter', 'mean'),
        ('Median_minutter', 'median'),
        ('Std_minutter', 'std'),
        ('Min_minutter', 'min'),
        ('Max_minutter', 'max')
    ]).reset_index()

    # Round to 1 decimal
    for col in ['Gennemsnit_minutter', 'Median_minutter', 'Std_minutter',
                'Min_minutter', 'Max_minutter']:
        yearly_by_region[col] = yearly_by_region[col].round(1)

    yearly_by_region['Year'] = yearly_by_region['Year'].astype(int)

    # 2. Yearly summary (landsdækkende)
    yearly_summary = df_filtered.groupby('Year')['ResponstidMinutter'].agg([
        ('Antal_kørsler', 'count'),
        ('Gennemsnit_minutter', 'mean'),
        ('Median_minutter', 'median'),
        ('Std_minutter', 'std'),
        ('Min_minutter', 'min'),
        ('Max_minutter', 'max')
    ]).reset_index()

    # Round to 1 decimal
    for col in ['Gennemsnit_minutter', 'Median_minutter', 'Std_minutter',
                'Min_minutter', 'Max_minutter']:
        yearly_summary[col] = yearly_summary[col].round(1)

    yearly_summary['Year'] = yearly_summary['Year'].astype(int)

    # 3. Regional summary (alle år samlet)
    regional_summary = df_filtered.groupby('Region')['ResponstidMinutter'].agg([
        ('Antal_kørsler', 'count'),
        ('Gennemsnit_minutter', 'mean'),
        ('Median_minutter', 'median'),
        ('Std_minutter', 'std'),
        ('Min_minutter', 'min'),
        ('Max_minutter', 'max')
    ]).reset_index()

    # Round to 1 decimal
    for col in ['Gennemsnit_minutter', 'Median_minutter', 'Std_minutter',
                'Min_minutter', 'Max_minutter']:
        regional_summary[col] = regional_summary[col].round(1)

    # Sort by average response time (worst first)
    regional_summary = regional_summary.sort_values('Gennemsnit_minutter', ascending=False)

    logger.info(f"  Generated yearly analysis:")
    logger.info(f"    - Year-by-region: {len(yearly_by_region)} entries")
    logger.info(f"    - Yearly summary: {len(yearly_summary)} years")
    logger.info(f"    - Regional summary: {len(regional_summary)} regions")

    return yearly_by_region, yearly_summary, regional_summary


def export_yearly_analysis(yearly_by_region, yearly_summary, regional_summary,
                           output_dir, priority='A'):
    """Export yearly analysis results to Excel files.

    Args:
        yearly_by_region: DataFrame with year x region data
        yearly_summary: DataFrame with yearly totals
        regional_summary: DataFrame with regional totals
        output_dir: Path to output directory
        priority: Priority level analyzed
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    priority_label = f"_{priority}" if priority != 'all' else "_ALLE"

    # Export 1: Year by region matrix
    file1 = output_dir / f"10_responstid_per_aar_og_region{priority_label}.xlsx"
    yearly_by_region.to_excel(file1, index=False, engine='openpyxl')
    logger.info(f"  ✓ Saved: {file1.name}")

    # Export 2: Yearly summary (landsdækkende)
    file2 = output_dir / f"11_responstid_per_aar_landsdækkende{priority_label}.xlsx"
    yearly_summary.to_excel(file2, index=False, engine='openpyxl')
    logger.info(f"  ✓ Saved: {file2.name}")

    # Export 3: Regional summary (alle år)
    file3 = output_dir / f"12_responstid_per_region_samlet{priority_label}.xlsx"
    regional_summary.to_excel(file3, index=False, engine='openpyxl')
    logger.info(f"  ✓ Saved: {file3.name}")

    # Export 4: Pivot table (år som rækker, regioner som kolonner)
    pivot = yearly_by_region.pivot(
        index='Year',
        columns='Region',
        values='Gennemsnit_minutter'
    ).round(1)

    file4 = output_dir / f"13_responstid_pivot_aar_x_region{priority_label}.xlsx"
    pivot.to_excel(file4, engine='openpyxl')
    logger.info(f"  ✓ Saved: {file4.name}")

    # Export 5: Summary text file with key findings
    file5 = output_dir / f"ÅRLIG_ANALYSE_FUND{priority_label}.txt"
    with open(file5, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write(f"ÅRLIG ANALYSE - {priority}-PRIORITET\n")
        f.write("="*80 + "\n\n")

        f.write(f"Total kørsler analyseret: {yearly_summary['Antal_kørsler'].sum():,}\n")
        f.write(f"Periode: {yearly_summary['Year'].min()}-{yearly_summary['Year'].max()}\n")
        f.write(f"Regioner: {len(regional_summary)}\n\n")

        f.write("LANDSDÆKKENDE UDVIKLING:\n")
        f.write("-" * 80 + "\n")
        for _, row in yearly_summary.iterrows():
            f.write(f"{int(row['Year'])}: {row['Gennemsnit_minutter']:.1f} min gennemsnit ")
            f.write(f"(median: {row['Median_minutter']:.1f}, n={row['Antal_kørsler']:,})\n")

        # Year-over-year changes
        f.write("\nÅR-TIL-ÅR ÆNDRINGER:\n")
        f.write("-" * 80 + "\n")
        for i in range(1, len(yearly_summary)):
            year = int(yearly_summary.iloc[i]['Year'])
            prev_year = int(yearly_summary.iloc[i-1]['Year'])
            current = yearly_summary.iloc[i]['Gennemsnit_minutter']
            previous = yearly_summary.iloc[i-1]['Gennemsnit_minutter']
            change = current - previous
            pct_change = (change / previous) * 100

            symbol = "↑" if change > 0 else "↓" if change < 0 else "→"
            f.write(f"{prev_year} → {year}: {change:+.1f} min ({pct_change:+.1f}%) {symbol}\n")

        f.write("\nREGIONAL SAMMENLIGNING (ALLE ÅR):\n")
        f.write("-" * 80 + "\n")
        for i, row in regional_summary.iterrows():
            rank = i + 1
            f.write(f"{rank}. {row['Region']:15s}: {row['Gennemsnit_minutter']:.1f} min ")
            f.write(f"(median: {row['Median_minutter']:.1f}, n={row['Antal_kørsler']:,})\n")

        # Regional variation
        best = regional_summary.iloc[-1]['Gennemsnit_minutter']
        worst = regional_summary.iloc[0]['Gennemsnit_minutter']
        diff = worst - best
        pct_diff = (diff / best) * 100

        f.write(f"\nREGIONAL VARIATION:\n")
        f.write("-" * 80 + "\n")
        f.write(f"Bedste region: {regional_summary.iloc[-1]['Region']} ({best:.1f} min)\n")
        f.write(f"Værste region: {regional_summary.iloc[0]['Region']} ({worst:.1f} min)\n")
        f.write(f"Forskel: {diff:.1f} min ({pct_diff:.1f}% langsommere)\n")

        f.write("\n" + "="*80 + "\n")
        f.write("Analyse genereret af Ambulance Pipeline\n")
        f.write("="*80 + "\n")

    logger.info(f"  ✓ Saved: {file5.name}")

    return [file1, file2, file3, file4, file5]


def run_yearly_analysis(output_dir, priority='A', regional_data_cache=None):
    """Run complete yearly analysis pipeline.

    Args:
        output_dir: Path to output directory
        priority: Priority level to analyze ('A', 'B', or 'all')
        regional_data_cache: Pre-loaded regional data dictionary (optional)

    Returns:
        list: Paths to generated files
    """
    logger.info("="*80)
    logger.info(f"Starting yearly analysis for priority={priority}")
    logger.info("="*80)

    # Load data (use cache if available)
    df = load_all_regional_raw_data(regional_data_cache=regional_data_cache)

    # Analyze
    yearly_by_region, yearly_summary, regional_summary = analyze_yearly_by_region(df, priority)

    # Export
    files = export_yearly_analysis(
        yearly_by_region,
        yearly_summary,
        regional_summary,
        output_dir,
        priority
    )

    logger.info(f"Yearly analysis complete - {len(files)} files generated")

    return files
