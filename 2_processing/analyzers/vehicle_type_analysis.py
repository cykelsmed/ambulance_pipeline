"""
Vehicle Type Analysis - Ambulance vs. Lægebil vs. Andre

Analyserer køretøjstyper (ambulance, lægebil, paramediciner, helikopter, mv.)
på tværs af alle 5 danske regioner.

Analyser:
1. National fordeling af køretøjstyper
2. Regional variation i køretøjsbrug
3. Responstidsforskelle per køretøjstype
4. Prioritetsforskelle (A vs B per køretøjstype)
5. Tidsmæssige mønstre (time-of-day per køretøjstype)

Author: Claude Code
Created: 2025-11-12
"""

import pandas as pd
import logging
import yaml
from pathlib import Path
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


# Value normalization mapping (based on actual regional values)
VEHICLE_TYPE_MAPPING = {
    # Ambulance variants
    'AMB': 'Ambulance',
    'Ambulance': 'Ambulance',

    # Lægebil/Akutbil variants
    'AKUTB': 'Lægebil',
    'Akutbil': 'Lægebil',
    'Akutlægebil': 'Lægebil',
    'ALB': 'Lægebil',

    # Paramediciner variants
    'Paramedicinerbil': 'Paramediciner',
    'Paramedicinerambulance': 'Paramediciner',
    'PMB': 'Paramediciner',

    # Sygetransport
    'ST': 'Sygetransport',

    # Helikopter variants
    'Helikopter': 'Helikopter',
    'HEMS': 'Helikopter',
    'Akutlægehelikopter': 'Helikopter',

    # Special units
    'Sociolance': 'Andre',
    'PVE': 'Andre',
}


def load_regional_config():
    """Load regional configuration."""
    config_path = Path(__file__).parent.parent / 'regional_config.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def normalize_vehicle_type(value: str) -> str:
    """Normalize vehicle type name to standard categories."""
    if pd.isna(value):
        return 'Ukendt'

    # Check exact match first
    if value in VEHICLE_TYPE_MAPPING:
        return VEHICLE_TYPE_MAPPING[value]

    # Otherwise return as-is (for unknown types)
    return value


def analyze_national_distribution(regional_data_cache: Dict) -> pd.DataFrame:
    """
    Analyze national distribution of vehicle types.

    Returns DataFrame with columns:
    - Vehicle_Type_Normalized
    - Total_Cases
    - Percentage
    - Median_Response_Time
    """
    logger.info("Analyzing national vehicle type distribution...")

    regional_config = load_regional_config()
    all_data = []

    for region_name, config in regional_config['regions'].items():
        if region_name not in regional_data_cache:
            logger.warning(f"  {region_name} not in cache, skipping")
            continue

        df = regional_data_cache[region_name].copy()

        # Get column mappings
        cols = config['columns']
        if 'vehicle_type' not in cols:
            logger.warning(f"  {region_name} has no vehicle_type column, skipping")
            continue

        vehicle_col = cols['vehicle_type']
        response_col = cols['response_time']
        priority_col = cols['priority']

        # Filter to A+B priority
        df_filtered = df[df[priority_col].isin(['A', 'B'])].copy()

        # Normalize vehicle type
        df_filtered['Vehicle_Type_Normalized'] = df_filtered[vehicle_col].apply(normalize_vehicle_type)

        # Convert response time to numeric
        df_filtered[response_col] = pd.to_numeric(df_filtered[response_col], errors='coerce')
        df_filtered = df_filtered[df_filtered[response_col].notna()]

        # Add to collection
        all_data.append(df_filtered[['Vehicle_Type_Normalized', response_col]])

        logger.info(f"  {region_name}: {len(df_filtered):,} cases")

    if not all_data:
        raise ValueError("No vehicle type data found in any region")

    # Combine all regions
    combined = pd.concat(all_data, ignore_index=True)
    combined = combined.rename(columns={combined.columns[1]: 'response_time'})

    # Calculate statistics
    stats = combined.groupby('Vehicle_Type_Normalized').agg(
        Total_Cases=('response_time', 'count'),
        Median_Response_Time=('response_time', 'median'),
        Mean_Response_Time=('response_time', 'mean')
    ).reset_index()

    # Calculate percentage
    total_cases = stats['Total_Cases'].sum()
    stats['Percentage'] = (stats['Total_Cases'] / total_cases * 100).round(1)

    # Round response times
    stats['Median_Response_Time'] = stats['Median_Response_Time'].round(1)
    stats['Mean_Response_Time'] = stats['Mean_Response_Time'].round(1)

    # Sort by total cases
    stats = stats.sort_values('Total_Cases', ascending=False)

    logger.info(f"✓ National distribution: {len(stats)} vehicle types, {total_cases:,} total cases")

    return stats


def analyze_regional_variation(regional_data_cache: Dict) -> pd.DataFrame:
    """
    Analyze regional variation in vehicle type usage.

    Returns DataFrame with columns:
    - Region
    - Vehicle_Type_Normalized
    - Total_Cases
    - Percentage
    - Median_Response_Time
    """
    logger.info("Analyzing regional vehicle type variation...")

    regional_config = load_regional_config()
    all_results = []

    for region_name, config in regional_config['regions'].items():
        if region_name not in regional_data_cache:
            continue

        df = regional_data_cache[region_name].copy()

        # Get column mappings
        cols = config['columns']
        if 'vehicle_type' not in cols:
            continue

        vehicle_col = cols['vehicle_type']
        response_col = cols['response_time']
        priority_col = cols['priority']

        # Filter to A+B priority
        df_filtered = df[df[priority_col].isin(['A', 'B'])].copy()

        # Normalize vehicle type
        df_filtered['Vehicle_Type_Normalized'] = df_filtered[vehicle_col].apply(normalize_vehicle_type)

        # Convert response time to numeric
        df_filtered[response_col] = pd.to_numeric(df_filtered[response_col], errors='coerce')
        df_filtered = df_filtered[df_filtered[response_col].notna()]

        # Calculate statistics per vehicle type
        stats = df_filtered.groupby('Vehicle_Type_Normalized')[response_col].agg([
            ('Total_Cases', 'count'),
            ('Median_Response_Time', 'median')
        ]).reset_index()

        # Calculate percentage within region
        total_cases = stats['Total_Cases'].sum()
        stats['Percentage'] = (stats['Total_Cases'] / total_cases * 100).round(1)
        stats['Median_Response_Time'] = stats['Median_Response_Time'].round(1)

        # Add region
        stats['Region'] = region_name

        all_results.append(stats)

        logger.info(f"  {region_name}: {len(stats)} vehicle types, {total_cases:,} cases")

    # Combine all regions
    combined = pd.concat(all_results, ignore_index=True)

    # Reorder columns
    combined = combined[['Region', 'Vehicle_Type_Normalized', 'Total_Cases', 'Percentage', 'Median_Response_Time']]

    # Sort by region and total cases
    combined = combined.sort_values(['Region', 'Total_Cases'], ascending=[True, False])

    logger.info(f"✓ Regional variation: {len(combined)} entries across 5 regions")

    return combined


def analyze_priority_differences(regional_data_cache: Dict) -> pd.DataFrame:
    """
    Analyze vehicle type usage differences between A and B priority.

    Returns DataFrame with columns:
    - Vehicle_Type_Normalized
    - Priority
    - Total_Cases
    - Percentage
    - Median_Response_Time
    """
    logger.info("Analyzing priority differences per vehicle type...")

    regional_config = load_regional_config()
    all_data = []

    for region_name, config in regional_config['regions'].items():
        if region_name not in regional_data_cache:
            continue

        df = regional_data_cache[region_name].copy()

        # Get column mappings
        cols = config['columns']
        if 'vehicle_type' not in cols:
            continue

        vehicle_col = cols['vehicle_type']
        response_col = cols['response_time']
        priority_col = cols['priority']

        # Filter to A+B priority
        df_filtered = df[df[priority_col].isin(['A', 'B'])].copy()

        # Normalize vehicle type
        df_filtered['Vehicle_Type_Normalized'] = df_filtered[vehicle_col].apply(normalize_vehicle_type)

        # Convert response time to numeric
        df_filtered[response_col] = pd.to_numeric(df_filtered[response_col], errors='coerce')
        df_filtered = df_filtered[df_filtered[response_col].notna()]

        # Add to collection
        all_data.append(df_filtered[[priority_col, 'Vehicle_Type_Normalized', response_col]])

    if not all_data:
        raise ValueError("No vehicle type data found")

    # Combine all regions
    combined = pd.concat(all_data, ignore_index=True)
    combined = combined.rename(columns={combined.columns[0]: 'Priority', combined.columns[2]: 'response_time'})

    # Calculate statistics per priority
    stats = combined.groupby(['Vehicle_Type_Normalized', 'Priority']).agg(
        Total_Cases=('response_time', 'count'),
        Median_Response_Time=('response_time', 'median')
    ).reset_index()

    # Calculate percentage within each priority group
    for priority in ['A', 'B']:
        priority_mask = stats['Priority'] == priority
        total_cases = stats.loc[priority_mask, 'Total_Cases'].sum()
        stats.loc[priority_mask, 'Percentage'] = (stats.loc[priority_mask, 'Total_Cases'] / total_cases * 100).round(1)

    stats['Median_Response_Time'] = stats['Median_Response_Time'].round(1)

    # Sort by priority and total cases
    stats = stats.sort_values(['Priority', 'Total_Cases'], ascending=[True, False])

    logger.info(f"✓ Priority differences: {len(stats)} entries")

    return stats


def analyze_temporal_patterns(regional_data_cache: Dict) -> pd.DataFrame:
    """
    Analyze time-of-day patterns per vehicle type (hourly).

    Returns DataFrame with columns:
    - Vehicle_Type_Normalized
    - Hour
    - Total_Cases
    - Median_Response_Time
    """
    logger.info("Analyzing temporal patterns per vehicle type...")

    regional_config = load_regional_config()
    all_data = []

    for region_name, config in regional_config['regions'].items():
        if region_name not in regional_data_cache:
            continue

        df = regional_data_cache[region_name].copy()

        # Get column mappings
        cols = config['columns']
        if 'vehicle_type' not in cols:
            continue

        vehicle_col = cols['vehicle_type']
        response_col = cols['response_time']
        priority_col = cols['priority']
        timestamp_col = cols['timestamp']

        # Filter to A+B priority
        df_filtered = df[df[priority_col].isin(['A', 'B'])].copy()

        # Normalize vehicle type
        df_filtered['Vehicle_Type_Normalized'] = df_filtered[vehicle_col].apply(normalize_vehicle_type)

        # Convert response time to numeric
        df_filtered[response_col] = pd.to_numeric(df_filtered[response_col], errors='coerce')
        df_filtered = df_filtered[df_filtered[response_col].notna()]

        # Extract hour from timestamp
        df_filtered['timestamp_dt'] = pd.to_datetime(df_filtered[timestamp_col], errors='coerce')
        df_filtered = df_filtered[df_filtered['timestamp_dt'].notna()]
        df_filtered['Hour'] = df_filtered['timestamp_dt'].dt.hour

        # Add to collection
        all_data.append(df_filtered[['Vehicle_Type_Normalized', 'Hour', response_col]])

    if not all_data:
        raise ValueError("No temporal data found")

    # Combine all regions
    combined = pd.concat(all_data, ignore_index=True)
    combined = combined.rename(columns={combined.columns[2]: 'response_time'})

    # Calculate statistics per hour
    stats = combined.groupby(['Vehicle_Type_Normalized', 'Hour']).agg(
        Total_Cases=('response_time', 'count'),
        Median_Response_Time=('response_time', 'median')
    ).reset_index()

    stats['Median_Response_Time'] = stats['Median_Response_Time'].round(1)

    # Sort by vehicle type and hour
    stats = stats.sort_values(['Vehicle_Type_Normalized', 'Hour'])

    logger.info(f"✓ Temporal patterns: {len(stats)} entries")

    return stats


def generate_summary_report(df_national: pd.DataFrame,
                            df_regional: pd.DataFrame,
                            df_priority: pd.DataFrame) -> str:
    """Generate human-readable summary report."""

    lines = []
    lines.append("KØRETØJSTYPE ANALYSE")
    lines.append("=" * 80)
    lines.append("")
    lines.append("LANDSDÆKKENDE FORDELING AF KØRETØJSTYPER")
    lines.append("Baseret på A+B prioritet kørsler fra alle 5 regioner (2021-2025)")
    lines.append("")
    lines.append("=" * 80)
    lines.append("")

    # National distribution
    lines.append("NATIONAL FORDELING:")
    lines.append("-" * 80)
    total_cases = df_national['Total_Cases'].sum()
    lines.append(f"Total analyserede kørsler: {total_cases:,}")
    lines.append("")

    for _, row in df_national.iterrows():
        vehicle = row['Vehicle_Type_Normalized']
        cases = int(row['Total_Cases'])
        pct = row['Percentage']
        median_time = row['Median_Response_Time']

        lines.append(f"{vehicle}:")
        lines.append(f"  Antal: {cases:,} kørsler ({pct:.1f}%)")
        lines.append(f"  Median responstid: {median_time:.1f} minutter")
        lines.append("")

    # Regional variation highlights
    lines.append("=" * 80)
    lines.append("")
    lines.append("REGIONAL VARIATION:")
    lines.append("-" * 80)
    lines.append("")

    # Find top vehicle type per region
    for region in df_regional['Region'].unique():
        region_data = df_regional[df_regional['Region'] == region]
        top_vehicle = region_data.iloc[0]

        lines.append(f"{region}:")
        lines.append(f"  Mest brugt: {top_vehicle['Vehicle_Type_Normalized']} ({top_vehicle['Percentage']:.1f}%)")
        lines.append(f"  Median responstid: {top_vehicle['Median_Response_Time']:.1f} min")
        lines.append("")

    # Priority differences
    lines.append("=" * 80)
    lines.append("")
    lines.append("PRIORITETSFORSKELLE (A vs B):")
    lines.append("-" * 80)
    lines.append("")

    # Group by priority
    for priority in ['A', 'B']:
        priority_data = df_priority[df_priority['Priority'] == priority]
        top_vehicle = priority_data.iloc[0]

        lines.append(f"{priority}-prioritet:")
        lines.append(f"  Mest brugt: {top_vehicle['Vehicle_Type_Normalized']} ({top_vehicle['Percentage']:.1f}%)")
        lines.append(f"  Median responstid: {top_vehicle['Median_Response_Time']:.1f} min")
        lines.append("")

    lines.append("=" * 80)
    lines.append("")
    lines.append("KONKLUSION:")
    lines.append("")

    # Find ambulance vs lægebil
    ambulance = df_national[df_national['Vehicle_Type_Normalized'] == 'Ambulance']
    laegebil = df_national[df_national['Vehicle_Type_Normalized'] == 'Lægebil']

    if len(ambulance) > 0:
        amb_pct = ambulance.iloc[0]['Percentage']
        amb_time = ambulance.iloc[0]['Median_Response_Time']
        lines.append(f"• Ambulance står for {amb_pct:.1f}% af alle kørsler")
        lines.append(f"  (median responstid: {amb_time:.1f} min)")

    if len(laegebil) > 0:
        lb_pct = laegebil.iloc[0]['Percentage']
        lb_time = laegebil.iloc[0]['Median_Response_Time']
        lines.append(f"• Lægebil/akutbil står for {lb_pct:.1f}% af alle kørsler")
        lines.append(f"  (median responstid: {lb_time:.1f} min)")

    lines.append("")
    lines.append("Dette viser køretøjstype-fordelingen på tværs af Danmark.")
    lines.append("")

    return "\n".join(lines)


def run_vehicle_type_analysis(output_dir: str = '3_output/current',
                               regional_data_cache: Dict = None) -> Tuple[Dict[str, pd.DataFrame], str]:
    """
    Run vehicle type analysis for all regions.

    Args:
        output_dir: Directory to save output files
        regional_data_cache: Pre-loaded regional data dictionary (required)

    Returns:
        - Dict of DataFrames with analysis results
        - Text summary report
    """
    logger.info("Starting vehicle type analysis...")

    if not regional_data_cache:
        raise ValueError("regional_data_cache is required for vehicle type analysis")

    logger.info(f"Analyzing data from {len(regional_data_cache)} regions")

    # Run analyses
    df_national = analyze_national_distribution(regional_data_cache)
    df_regional = analyze_regional_variation(regional_data_cache)
    df_priority = analyze_priority_differences(regional_data_cache)
    df_temporal = analyze_temporal_patterns(regional_data_cache)

    # Generate summary
    summary = generate_summary_report(df_national, df_regional, df_priority)

    # Export to Excel
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Save each analysis to separate Excel file
    excel_files = [
        ('21_vehicle_type_national.xlsx', df_national, 'National_Distribution'),
        ('22_vehicle_type_regional.xlsx', df_regional, 'Regional_Variation'),
        ('23_vehicle_type_priority.xlsx', df_priority, 'Priority_Differences'),
        ('24_vehicle_type_temporal.xlsx', df_temporal, 'Temporal_Patterns'),
    ]

    for filename, df, sheet_name in excel_files:
        excel_file = output_path / filename
        df.to_excel(excel_file, index=False, sheet_name=sheet_name)
        logger.info(f"Exported {filename}")

    # Export text summary
    summary_file = output_path / '21_VEHICLE_TYPE_FUND.txt'
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    logger.info(f"Exported summary to {summary_file}")

    # Export Datawrapper CSV (national distribution)
    datawrapper_file = output_path / 'DATAWRAPPER_vehicle_types.csv'
    df_national[['Vehicle_Type_Normalized', 'Total_Cases', 'Percentage']].to_csv(
        datawrapper_file, index=False, encoding='utf-8'
    )
    logger.info(f"Exported Datawrapper CSV to {datawrapper_file}")

    results = {
        'national': df_national,
        'regional': df_regional,
        'priority': df_priority,
        'temporal': df_temporal
    }

    return results, summary


if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Load data cache
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from data_cache import load_all_regional_data_once

    print("Loading regional data cache...")
    cache = load_all_regional_data_once()

    print("\nRunning vehicle type analysis...")
    results, summary = run_vehicle_type_analysis(regional_data_cache=cache)

    print("\n" + summary)
    print(f"\nAnalyzed {len(results)} result sets")
