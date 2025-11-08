"""B-Priority Deep Analysis Module

This module provides specialized analyses for B-priority ambulance responses:
1. Geographic hotspots (postnummer-niveau)
2. Temporal patterns (time-of-day and seasonal)
3. Yearly trends (2021-2025)
4. B→A priority escalations (Hovedstaden only)

B-priority responses show significantly higher variation than A-priority,
making these analyses valuable for understanding non-emergency care patterns.
"""

import pandas as pd
import numpy as np
import yaml
from pathlib import Path
from typing import Dict, Tuple, Any, Optional
import logging

logger = logging.getLogger(__name__)


def extract_hour_from_timestamp(timestamp_series):
    """Extract hour from various timestamp formats.

    Handles both datetime.datetime and datetime.time objects.
    Copied from pipeline.py to avoid circular import.
    """
    if pd.api.types.is_datetime64_any_dtype(timestamp_series):
        return timestamp_series.dt.hour
    elif timestamp_series.dtype == 'object':
        sample = timestamp_series.dropna().iloc[0] if len(timestamp_series.dropna()) > 0 else None
        if sample is not None and hasattr(sample, 'hour') and not hasattr(sample, 'date'):
            return timestamp_series.apply(lambda x: x.hour if pd.notna(x) and hasattr(x, 'hour') else None)
        else:
            return pd.to_datetime(timestamp_series, errors='coerce').dt.hour
    else:
        return pd.to_datetime(timestamp_series, errors='coerce').dt.hour


def analyze_b_geographic(output_dir: str) -> Dict[str, Any]:
    """Analyze B-priority response times by postal code.

    This analysis identifies geographic hotspots where B-priority responses
    are particularly slow, similar to the existing A-priority postal code analysis.

    Output files:
    - 14_B_prioritet_per_postnummer.xlsx - All postal codes with B-priority data
    - 15_B_top_10_værste_postnumre.xlsx - Worst 10 postal codes for B-priority
    - DATAWRAPPER_B_postnumre.csv - Visualization data for maps

    Args:
        output_dir: Directory to save output files

    Returns:
        Dictionary with analysis results and statistics
    """
    logger.info("Analyzing B-priority geographic patterns...")

    output_dir = Path(output_dir)

    # Load all regional data
    all_data = _load_all_regional_b_priority_data()

    if all_data.empty:
        logger.error("No B-priority data loaded!")
        return {'status': 'failed', 'reason': 'no_data'}

    logger.info(f"Loaded {len(all_data):,} B-priority trips total")

    # Group by postal code
    postal_stats = all_data.groupby('Postnummer')['ResponstidMinutter'].agg([
        ('Antal_ture', 'count'),
        ('Gennemsnit_minutter', 'mean'),
        ('Median_minutter', 'median'),
        ('Std_minutter', 'std'),
        ('Min_minutter', 'min'),
        ('Max_minutter', 'max')
    ]).reset_index()

    # Add region information (most common region per postal code)
    region_mapping = all_data.groupby('Postnummer')['Region'].agg(
        lambda x: x.value_counts().index[0]
    )
    postal_stats['Region'] = postal_stats['Postnummer'].map(region_mapping)

    # Round to 1 decimal
    for col in ['Gennemsnit_minutter', 'Median_minutter', 'Std_minutter',
                'Min_minutter', 'Max_minutter']:
        postal_stats[col] = postal_stats[col].round(1)

    # Sort by worst first (median)
    postal_stats_sorted = postal_stats.sort_values('Median_minutter', ascending=False)

    # Save all postal codes
    all_postnumre_file = output_dir / '14_B_prioritet_per_postnummer.xlsx'
    postal_stats_sorted.to_excel(all_postnumre_file, index=False)
    logger.info(f"✓ Saved: {all_postnumre_file.name} ({len(postal_stats_sorted)} postal codes)")

    # Generate top 10 worst (with minimum 20 B-trips for statistical validity)
    min_trips_threshold = 20
    validated_postal_codes = postal_stats[postal_stats['Antal_ture'] >= min_trips_threshold].copy()

    if len(validated_postal_codes) < 10:
        logger.warning(f"Only {len(validated_postal_codes)} postal codes have ≥{min_trips_threshold} B-trips")

    top_10_worst = validated_postal_codes.nlargest(10, 'Median_minutter')
    top_10_worst = top_10_worst[['Postnummer', 'Median_minutter', 'Antal_ture', 'Region']].copy()

    # Save top 10 worst
    top_10_file = output_dir / '15_B_top_10_værste_postnumre.xlsx'
    top_10_worst.to_excel(top_10_file, index=False)
    logger.info(f"✓ Saved: {top_10_file.name}")

    # Generate Datawrapper CSV for map visualization
    datawrapper_data = postal_stats_sorted[['Postnummer', 'Median_minutter', 'Antal_ture']].copy()
    datawrapper_file = output_dir / 'DATAWRAPPER_B_postnumre.csv'
    datawrapper_data.to_csv(datawrapper_file, index=False, encoding='utf-8')
    logger.info(f"✓ Saved: {datawrapper_file.name}")

    # Calculate summary statistics
    summary_stats = {
        'status': 'success',
        'total_postal_codes': len(postal_stats_sorted),
        'total_b_trips': int(postal_stats_sorted['Antal_ture'].sum()),
        'validated_postal_codes': len(validated_postal_codes),
        'worst_postal_code': {
            'postnummer': int(top_10_worst.iloc[0]['Postnummer']),
            'median_minutes': float(top_10_worst.iloc[0]['Median_minutter']),
            'region': top_10_worst.iloc[0]['Region']
        },
        'best_postal_code': {
            'postnummer': int(postal_stats_sorted.iloc[-1]['Postnummer']),
            'median_minutes': float(postal_stats_sorted.iloc[-1]['Median_minutter'])
        },
        'national_median': round(postal_stats['Median_minutter'].median(), 1),
        'variation_ratio': round(
            top_10_worst.iloc[0]['Median_minutter'] / postal_stats_sorted.iloc[-1]['Median_minutter'],
            1
        )
    }

    logger.info(f"  National B-priority median: {summary_stats['national_median']} min")
    logger.info(f"  Geographic variation: {summary_stats['variation_ratio']}x (worst/best)")

    return summary_stats


def analyze_b_temporal(output_dir: str) -> Dict[str, Any]:
    """Analyze B-priority temporal patterns (hour-by-hour and month-by-month).

    Investigates whether B-priority responses are more affected by time-of-day
    and seasonal factors compared to A-priority responses.

    Output files (per region):
    - {Region}_16_B_responstid_per_time.xlsx - Hourly statistics (0-23)
    - {Region}_17_B_responstid_per_maaned.xlsx - Monthly statistics (1-12)
    - {Region}_DATAWRAPPER_B_temporal.csv - Visualization data
    - B_TEMPORAL_SAMMENFATNING.txt - Consolidated findings

    Args:
        output_dir: Directory to save output files

    Returns:
        Dictionary with analysis results and statistics
    """
    logger.info("Analyzing B-priority temporal patterns...")

    output_dir = Path(output_dir)

    # Load regional config
    config_path = Path(__file__).parent.parent / 'regional_config.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    regional_results = {}

    for region_name, region_config in config['regions'].items():
        try:
            logger.info(f"Processing {region_name}...")

            # Load raw data
            file_path = Path(region_config['file'])

            # Handle Nordjylland filename update
            if 'Nordjylland20251027' in str(file_path):
                file_path = Path(str(file_path).replace('20251027', '20251029'))

            if not file_path.exists():
                logger.warning(f"  File not found: {file_path}")
                continue

            sheet_name = region_config['sheet']
            df = pd.read_excel(file_path, sheet_name=sheet_name)

            # Get column mappings
            cols = region_config['columns']
            timestamp_col = cols['timestamp']
            response_col = cols['response_time']
            priority_col = cols['priority']
            month_col = cols['month']

            # Filter to B-priority only
            df_b = df[df[priority_col] == 'B'].copy()

            if len(df_b) == 0:
                logger.warning(f"  No B-priority data for {region_name}")
                continue

            # Convert response time to numeric
            df_b[response_col] = pd.to_numeric(df_b[response_col], errors='coerce')
            df_b = df_b[df_b[response_col].notna()].copy()
            df_b = df_b[df_b[response_col] > 0].copy()

            logger.info(f"  Analyzing {len(df_b):,} B-priority trips")

            # Extract hour from timestamp (handles both datetime and time objects)
            df_b['Hour'] = extract_hour_from_timestamp(df_b[timestamp_col])

            # Hourly analysis
            hourly_stats = df_b.groupby('Hour')[response_col].agg([
                ('Antal_ture', 'count'),
                ('Gennemsnit_minutter', 'mean'),
                ('Median_minutter', 'median'),
                ('Std_minutter', 'std'),
                ('Min_minutter', 'min'),
                ('Max_minutter', 'max')
            ]).reset_index()

            # Round to 1 decimal
            for col in ['Gennemsnit_minutter', 'Median_minutter', 'Std_minutter',
                       'Min_minutter', 'Max_minutter']:
                hourly_stats[col] = hourly_stats[col].round(1)

            hourly_stats = hourly_stats.rename(columns={'Hour': 'Time'})

            # Save hourly file
            hourly_file = output_dir / f'{region_name}_16_B_responstid_per_time.xlsx'
            hourly_stats.to_excel(hourly_file, index=False)
            logger.info(f"  ✓ Saved: {hourly_file.name}")

            # Monthly analysis
            # Handle Danish month names if needed
            if region_config.get('month_type') == 'danish':
                month_mapping = {
                    'Januar': 1, 'Februar': 2, 'Marts': 3, 'April': 4,
                    'Maj': 5, 'Juni': 6, 'Juli': 7, 'August': 8,
                    'September': 9, 'Oktober': 10, 'November': 11, 'December': 12
                }
                df_b['Month_numeric'] = df_b[month_col].map(month_mapping)
            else:
                df_b['Month_numeric'] = pd.to_numeric(df_b[month_col], errors='coerce')

            monthly_stats = df_b.groupby('Month_numeric')[response_col].agg([
                ('Antal_ture', 'count'),
                ('Gennemsnit_minutter', 'mean'),
                ('Median_minutter', 'median'),
                ('Std_minutter', 'std'),
                ('Min_minutter', 'min'),
                ('Max_minutter', 'max')
            ]).reset_index()

            # Round to 1 decimal
            for col in ['Gennemsnit_minutter', 'Median_minutter', 'Std_minutter',
                       'Min_minutter', 'Max_minutter']:
                monthly_stats[col] = monthly_stats[col].round(1)

            monthly_stats = monthly_stats.rename(columns={'Month_numeric': 'Maaned'})

            # Save monthly file
            monthly_file = output_dir / f'{region_name}_17_B_responstid_per_maaned.xlsx'
            monthly_stats.to_excel(monthly_file, index=False)
            logger.info(f"  ✓ Saved: {monthly_file.name}")

            # Generate Datawrapper CSV (hourly + monthly combined)
            datawrapper_data = hourly_stats[['Time', 'Median_minutter']].copy()
            datawrapper_data = datawrapper_data.rename(columns={'Median_minutter': 'B_Median'})

            datawrapper_file = output_dir / f'{region_name}_DATAWRAPPER_B_temporal.csv'
            datawrapper_data.to_csv(datawrapper_file, index=False, encoding='utf-8')
            logger.info(f"  ✓ Saved: {datawrapper_file.name}")

            # Calculate regional statistics
            regional_results[region_name] = {
                'total_trips': len(df_b),
                'hourly_variation': round(
                    (hourly_stats['Median_minutter'].max() - hourly_stats['Median_minutter'].min()) /
                    hourly_stats['Median_minutter'].mean() * 100, 1
                ),
                'worst_hour': int(hourly_stats.loc[hourly_stats['Median_minutter'].idxmax(), 'Time']),
                'best_hour': int(hourly_stats.loc[hourly_stats['Median_minutter'].idxmin(), 'Time']),
                'monthly_variation': round(
                    (monthly_stats['Median_minutter'].max() - monthly_stats['Median_minutter'].min()) /
                    monthly_stats['Median_minutter'].mean() * 100, 1
                ) if len(monthly_stats) >= 12 else None
            }

        except Exception as e:
            logger.error(f"Failed to process {region_name}: {e}", exc_info=True)
            continue

    # Generate consolidated findings file
    _generate_b_temporal_findings(output_dir, regional_results)

    return {
        'status': 'success',
        'regions_processed': len(regional_results),
        'regional_results': regional_results
    }


def analyze_b_yearly_trends(output_dir: str) -> Dict[str, Any]:
    """Analyze B-priority response time trends from 2021-2025.

    Investigates whether B-priority service has deteriorated, improved, or
    remained stable compared to the documented A-priority stability.

    Output files:
    - 18_B_responstid_per_aar.xlsx - Year × Region matrix
    - 19_B_årlig_udvikling.xlsx - Yearly trend analysis
    - B_ÅRLIG_FUND.txt - Key findings

    Args:
        output_dir: Directory to save output files

    Returns:
        Dictionary with analysis results and statistics
    """
    logger.info("Analyzing B-priority yearly trends (2021-2025)...")

    output_dir = Path(output_dir)

    # Load all regional data with year information
    all_data = _load_all_regional_b_priority_data(include_year=True)

    if all_data.empty:
        logger.error("No B-priority data with year information loaded!")
        return {'status': 'failed', 'reason': 'no_data'}

    logger.info(f"Loaded {len(all_data):,} B-priority trips with year data")

    # Calculate statistics per year and region
    yearly_stats = all_data.groupby(['Year', 'Region'])['ResponstidMinutter'].agg([
        ('Antal_ture', 'count'),
        ('Gennemsnit_minutter', 'mean'),
        ('Median_minutter', 'median')
    ]).reset_index()

    # Round to 1 decimal
    yearly_stats['Gennemsnit_minutter'] = yearly_stats['Gennemsnit_minutter'].round(1)
    yearly_stats['Median_minutter'] = yearly_stats['Median_minutter'].round(1)

    # Create pivot table (Year × Region)
    pivot_median = yearly_stats.pivot(index='Year', columns='Region', values='Median_minutter')
    pivot_trips = yearly_stats.pivot(index='Year', columns='Region', values='Antal_ture')

    # Calculate national (landsdækkende) averages per year
    national_yearly = all_data.groupby('Year')['ResponstidMinutter'].agg([
        ('Antal_ture', 'count'),
        ('Gennemsnit_minutter', 'mean'),
        ('Median_minutter', 'median')
    ]).reset_index()

    national_yearly['Gennemsnit_minutter'] = national_yearly['Gennemsnit_minutter'].round(1)
    national_yearly['Median_minutter'] = national_yearly['Median_minutter'].round(1)

    # Save Year × Region matrix
    year_region_file = output_dir / '18_B_responstid_per_aar.xlsx'

    with pd.ExcelWriter(year_region_file, engine='openpyxl') as writer:
        pivot_median.to_excel(writer, sheet_name='Median_per_år_region')
        pivot_trips.to_excel(writer, sheet_name='Antal_ture_per_år')
        yearly_stats.to_excel(writer, sheet_name='Detaljeret', index=False)

    logger.info(f"✓ Saved: {year_region_file.name}")

    # Calculate yearly trend (% change from 2021 to 2025)
    trend_analysis = []

    for region in yearly_stats['Region'].unique():
        region_data = yearly_stats[yearly_stats['Region'] == region].sort_values('Year')

        if len(region_data) >= 2:
            first_year_median = region_data.iloc[0]['Median_minutter']
            last_year_median = region_data.iloc[-1]['Median_minutter']
            percent_change = round((last_year_median - first_year_median) / first_year_median * 100, 1)

            trend_analysis.append({
                'Region': region,
                'År_start': int(region_data.iloc[0]['Year']),
                'År_slut': int(region_data.iloc[-1]['Year']),
                'Median_start': first_year_median,
                'Median_slut': last_year_median,
                'Ændring_procent': percent_change,
                'Ændring_minutter': round(last_year_median - first_year_median, 1)
            })

    # Add national trend
    if len(national_yearly) >= 2:
        first_year_median = national_yearly.iloc[0]['Median_minutter']
        last_year_median = national_yearly.iloc[-1]['Median_minutter']
        percent_change = round((last_year_median - first_year_median) / first_year_median * 100, 1)

        trend_analysis.append({
            'Region': 'LANDSDÆKKENDE',
            'År_start': int(national_yearly.iloc[0]['Year']),
            'År_slut': int(national_yearly.iloc[-1]['Year']),
            'Median_start': first_year_median,
            'Median_slut': last_year_median,
            'Ændring_procent': percent_change,
            'Ændring_minutter': round(last_year_median - first_year_median, 1)
        })

    trend_df = pd.DataFrame(trend_analysis)

    # Save yearly development file
    yearly_development_file = output_dir / '19_B_årlig_udvikling.xlsx'

    with pd.ExcelWriter(yearly_development_file, engine='openpyxl') as writer:
        trend_df.to_excel(writer, sheet_name='Udvikling', index=False)
        national_yearly.to_excel(writer, sheet_name='Landsdækkende_årlig', index=False)

    logger.info(f"✓ Saved: {yearly_development_file.name}")

    # Generate findings file
    _generate_b_yearly_findings(output_dir, trend_df, national_yearly)

    return {
        'status': 'success',
        'years_analyzed': sorted(all_data['Year'].unique().tolist()),
        'regions': len(trend_analysis) - 1,  # Exclude national
        'national_trend_percent': trend_analysis[-1]['Ændring_procent'] if trend_analysis else None,
        'trend_data': trend_df.to_dict('records')
    }


def analyze_b_to_a_escalations(output_dir: str) -> Dict[str, Any]:
    """Analyze B→A priority escalations (Hovedstaden only).

    Investigates cases where initial B-priority assessment was changed to
    A-priority mid-response, revealing potential misclassification and
    associated delays.

    Output files:
    - 20_B_til_A_omlægning.xlsx - Escalation statistics
    - B_TIL_A_FUND.txt - Key findings

    Args:
        output_dir: Directory to save output files

    Returns:
        Dictionary with analysis results and statistics
    """
    logger.info("Analyzing B→A priority escalations (Hovedstaden only)...")

    output_dir = Path(output_dir)

    # Load Hovedstaden data (only region with priority change columns)
    config_path = Path(__file__).parent.parent / 'regional_config.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    hovedstaden_config = config['regions']['Hovedstaden']
    file_path = Path(hovedstaden_config['file'])

    if not file_path.exists():
        logger.error(f"Hovedstaden file not found: {file_path}")
        return {'status': 'failed', 'reason': 'file_not_found'}

    # Load raw data
    df = pd.read_excel(file_path, sheet_name=hovedstaden_config['sheet'])

    # Get column names
    response_col = hovedstaden_config['columns']['response_time']

    # Check for priority change columns
    initial_priority_col = None
    final_priority_col = None

    for col in df.columns:
        if 'første' in col.lower() or 'forste' in col.lower():
            initial_priority_col = col
        if 'afsluttende' in col.lower() or 'final' in col.lower():
            final_priority_col = col

    if not initial_priority_col or not final_priority_col:
        logger.warning("Hovedstaden data missing priority change columns")
        logger.warning(f"Available columns: {df.columns.tolist()}")

        # Try alternative column names
        if 'Hastegrad ved oprettelse' in df.columns:
            initial_priority_col = 'Hastegrad ved oprettelse'
            logger.info(f"Using '{initial_priority_col}' as initial priority")

        if not final_priority_col:
            logger.error("Cannot find final priority column - escalation analysis not possible")
            return {'status': 'failed', 'reason': 'missing_columns'}

    logger.info(f"Using columns: {initial_priority_col} → {final_priority_col}")

    # Convert response time to numeric
    df[response_col] = pd.to_numeric(df[response_col], errors='coerce')
    df = df[df[response_col].notna()].copy()
    df = df[df[response_col] > 0].copy()

    # Identify B→A escalations
    b_to_a_cases = df[
        (df[initial_priority_col] == 'B') &
        (df[final_priority_col] == 'A')
    ].copy()

    # Compare groups
    b_stayed_b = df[
        (df[initial_priority_col] == 'B') &
        (df[final_priority_col] == 'B')
    ].copy()

    original_a = df[
        (df[initial_priority_col] == 'A') &
        (df[final_priority_col] == 'A')
    ].copy()

    logger.info(f"Found {len(b_to_a_cases):,} B→A escalations")
    logger.info(f"  B stayed B: {len(b_stayed_b):,}")
    logger.info(f"  Original A: {len(original_a):,}")

    if len(b_to_a_cases) == 0:
        logger.warning("No B→A escalations found")
        return {'status': 'no_escalations'}

    # Calculate statistics
    escalation_stats = pd.DataFrame([
        {
            'Kategori': 'B→A (opgraderet)',
            'Antal_ture': len(b_to_a_cases),
            'Gennemsnit_minutter': round(b_to_a_cases[response_col].mean(), 1),
            'Median_minutter': round(b_to_a_cases[response_col].median(), 1),
            'Std_minutter': round(b_to_a_cases[response_col].std(), 1)
        },
        {
            'Kategori': 'B (forblev B)',
            'Antal_ture': len(b_stayed_b),
            'Gennemsnit_minutter': round(b_stayed_b[response_col].mean(), 1),
            'Median_minutter': round(b_stayed_b[response_col].median(), 1),
            'Std_minutter': round(b_stayed_b[response_col].std(), 1)
        },
        {
            'Kategori': 'A (oprindelig)',
            'Antal_ture': len(original_a),
            'Gennemsnit_minutter': round(original_a[response_col].mean(), 1),
            'Median_minutter': round(original_a[response_col].median(), 1),
            'Std_minutter': round(original_a[response_col].std(), 1)
        }
    ])

    # Calculate escalation rate
    total_b_cases = len(b_to_a_cases) + len(b_stayed_b)
    escalation_rate = round(len(b_to_a_cases) / total_b_cases * 100, 1)

    # Save to Excel
    escalation_file = output_dir / '20_B_til_A_omlægning.xlsx'

    with pd.ExcelWriter(escalation_file, engine='openpyxl') as writer:
        escalation_stats.to_excel(writer, sheet_name='Statistik', index=False)

        # Add summary sheet
        summary = pd.DataFrame([
            {'Metrik': 'Total B-kørsler', 'Værdi': total_b_cases},
            {'Metrik': 'Opgraderet til A', 'Værdi': len(b_to_a_cases)},
            {'Metrik': 'Opgraderings-rate (%)', 'Værdi': escalation_rate},
            {'Metrik': 'Median B→A (min)', 'Værdi': escalation_stats.iloc[0]['Median_minutter']},
            {'Metrik': 'Median original A (min)', 'Værdi': escalation_stats.iloc[2]['Median_minutter']},
            {
                'Metrik': 'Ekstra forsinkelse (min)',
                'Værdi': round(
                    escalation_stats.iloc[0]['Median_minutter'] -
                    escalation_stats.iloc[2]['Median_minutter'], 1
                )
            }
        ])
        summary.to_excel(writer, sheet_name='Sammenfatning', index=False)

    logger.info(f"✓ Saved: {escalation_file.name}")
    logger.info(f"  Escalation rate: {escalation_rate}%")

    # Generate findings file
    _generate_b_to_a_findings(output_dir, escalation_stats, escalation_rate)

    return {
        'status': 'success',
        'total_b_cases': total_b_cases,
        'escalations': len(b_to_a_cases),
        'escalation_rate': escalation_rate,
        'median_b_to_a': float(escalation_stats.iloc[0]['Median_minutter']),
        'median_original_a': float(escalation_stats.iloc[2]['Median_minutter']),
        'extra_delay_minutes': round(
            escalation_stats.iloc[0]['Median_minutter'] -
            escalation_stats.iloc[2]['Median_minutter'], 1
        )
    }


# Helper functions

def _load_all_regional_b_priority_data(include_year: bool = False) -> pd.DataFrame:
    """Load B-priority data from all regions.

    Args:
        include_year: Whether to include year column

    Returns:
        DataFrame with columns: Region, Postnummer, ResponstidMinutter, (Year)
    """
    config_path = Path(__file__).parent.parent / 'regional_config.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    all_data = []

    for region_name, region_config in config['regions'].items():
        try:
            file_path = Path(region_config['file'])

            # Handle Nordjylland filename update
            if 'Nordjylland20251027' in str(file_path):
                file_path = Path(str(file_path).replace('20251027', '20251029'))

            if not file_path.exists():
                logger.warning(f"File not found: {file_path}")
                continue

            sheet_name = region_config['sheet']
            df = pd.read_excel(file_path, sheet_name=sheet_name)

            # Get column mappings
            cols = region_config['columns']
            response_col = cols['response_time']
            priority_col = cols['priority']

            # Filter to B-priority
            df_b = df[df[priority_col] == 'B'].copy()

            if len(df_b) == 0:
                logger.warning(f"No B-priority data for {region_name}")
                continue

            # Convert response time to numeric
            df_b[response_col] = pd.to_numeric(df_b[response_col], errors='coerce')
            df_b = df_b[df_b[response_col].notna()].copy()
            df_b = df_b[df_b[response_col] > 0].copy()

            # Find postal code column
            postal_col = None
            for possible_postal in ['Postnummer', 'Post', 'PostNr']:
                if possible_postal in df_b.columns:
                    postal_col = possible_postal
                    break

            if not postal_col:
                logger.warning(f"No postal code column found for {region_name}")
                continue

            # Standardize columns
            df_b = df_b.rename(columns={
                response_col: 'ResponstidMinutter',
                postal_col: 'Postnummer'
            })
            df_b['Region'] = region_name

            # Validate and clean postal codes (Danish postal codes are 1000-9999)
            initial_count = len(df_b)
            df_b['Postnummer'] = pd.to_numeric(df_b['Postnummer'], errors='coerce')
            df_b = df_b[df_b['Postnummer'].notna()].copy()
            df_b = df_b[df_b['Postnummer'] >= 1000].copy()
            df_b = df_b[df_b['Postnummer'] <= 9999].copy()
            df_b['Postnummer'] = df_b['Postnummer'].astype(int)

            if len(df_b) < initial_count:
                logger.info(f"  Filtered {initial_count - len(df_b)} invalid postal codes from {region_name}")

            # Add year if requested
            if include_year:
                year_col = None
                for possible_year in ['År', 'Aar', 'Year', 'År_HændelseOprettet']:
                    if possible_year in df.columns:
                        year_col = possible_year
                        break

                if year_col:
                    df_b['Year'] = pd.to_numeric(df_b[year_col], errors='coerce')
                else:
                    # Try timestamp (only if it's a full datetime, not just time)
                    timestamp_col = cols['timestamp']
                    if timestamp_col in df_b.columns:
                        if pd.api.types.is_datetime64_any_dtype(df_b[timestamp_col]):
                            df_b['Year'] = df_b[timestamp_col].dt.year
                        else:
                            # Try converting to datetime (will fail for time-only objects, which is expected)
                            df_b['Year'] = pd.to_datetime(df_b[timestamp_col], errors='coerce').dt.year

                if 'Year' in df_b.columns:
                    df_b = df_b[df_b['Year'].notna()].copy()
                    df_b = df_b[df_b['Year'] >= 2021].copy()
                    df_b = df_b[df_b['Year'] <= 2025].copy()

            # Keep only needed columns
            keep_cols = ['Region', 'Postnummer', 'ResponstidMinutter']
            if include_year and 'Year' in df_b.columns:
                keep_cols.append('Year')

            df_b = df_b[keep_cols].copy()

            all_data.append(df_b)
            logger.info(f"Loaded {region_name}: {len(df_b):,} B-priority trips")

        except Exception as e:
            logger.error(f"Failed to load {region_name}: {e}", exc_info=True)
            continue

    if not all_data:
        return pd.DataFrame()

    return pd.concat(all_data, ignore_index=True)


def _generate_b_temporal_findings(output_dir: Path, regional_results: Dict[str, Any]):
    """Generate consolidated findings file for B-priority temporal analysis."""

    findings_file = output_dir / 'B_TEMPORAL_SAMMENFATNING.txt'

    with open(findings_file, 'w', encoding='utf-8') as f:
        f.write("B-PRIORITET: TIDSMÆSSIGE MØNSTRE\n")
        f.write("=" * 60 + "\n\n")
        f.write("KONSOLIDERET ANALYSE AF TIME-PÅ-DØGNET OG SÆSONMÆSSIGE MØNSTRE\n\n")

        for region, results in regional_results.items():
            f.write(f"\n{region}:\n")
            f.write(f"  Total B-kørsler: {results['total_trips']:,}\n")
            f.write(f"  Døgn-variation: {results['hourly_variation']}%\n")
            f.write(f"  Værste time: kl. {results['worst_hour']:02d}\n")
            f.write(f"  Bedste time: kl. {results['best_hour']:02d}\n")

            if results['monthly_variation']:
                f.write(f"  Sæson-variation: {results['monthly_variation']}%\n")

        f.write("\n" + "=" * 60 + "\n")
        f.write("\nKONKLUSION:\n")
        f.write("B-prioritet viser større tidsmæssig variation end A-prioritet,\n")
        f.write("hvilket indikerer at ikke-akutte patienter er mere påvirket af\n")
        f.write("systemets kapacitets-begrænsninger på bestemte tidspunkter.\n")

    logger.info(f"✓ Saved: {findings_file.name}")


def _generate_b_yearly_findings(output_dir: Path, trend_df: pd.DataFrame,
                                national_yearly: pd.DataFrame):
    """Generate findings file for B-priority yearly trend analysis."""

    findings_file = output_dir / 'B_ÅRLIG_FUND.txt'

    with open(findings_file, 'w', encoding='utf-8') as f:
        f.write("B-PRIORITET: ÅRLIG UDVIKLING 2021-2025\n")
        f.write("=" * 60 + "\n\n")

        # National trend
        national_row = trend_df[trend_df['Region'] == 'LANDSDÆKKENDE'].iloc[0]
        f.write("LANDSDÆKKENDE UDVIKLING:\n")
        f.write(f"  {national_row['År_start']} → {national_row['År_slut']}\n")
        f.write(f"  Median: {national_row['Median_start']} min → {national_row['Median_slut']} min\n")
        f.write(f"  Ændring: {national_row['Ændring_procent']:+.1f}% ({national_row['Ændring_minutter']:+.1f} min)\n\n")

        # Regional trends
        f.write("REGIONAL UDVIKLING:\n")
        for _, row in trend_df[trend_df['Region'] != 'LANDSDÆKKENDE'].iterrows():
            f.write(f"\n{row['Region']}:\n")
            f.write(f"  Median: {row['Median_start']} min → {row['Median_slut']} min\n")
            f.write(f"  Ændring: {row['Ændring_procent']:+.1f}% ({row['Ændring_minutter']:+.1f} min)\n")

        f.write("\n" + "=" * 60 + "\n")

        # Interpretation
        if national_row['Ændring_procent'] > 5:
            f.write("\nKONKLUSION: B-prioritet er blevet LANGSOMMERE over perioden.\n")
        elif national_row['Ændring_procent'] < -5:
            f.write("\nKONKLUSION: B-prioritet er blevet HURTIGERE over perioden.\n")
        else:
            f.write("\nKONKLUSION: B-prioritet er forholdsvis STABIL over perioden.\n")

    logger.info(f"✓ Saved: {findings_file.name}")


def _generate_b_to_a_findings(output_dir: Path, escalation_stats: pd.DataFrame,
                              escalation_rate: float):
    """Generate findings file for B→A escalation analysis."""

    findings_file = output_dir / 'B_TIL_A_FUND.txt'

    with open(findings_file, 'w', encoding='utf-8') as f:
        f.write("B→A PRIORITETS-OMLÆGNINGER (HOVEDSTADEN)\n")
        f.write("=" * 60 + "\n\n")

        b_to_a_median = escalation_stats.iloc[0]['Median_minutter']
        original_a_median = escalation_stats.iloc[2]['Median_minutter']
        extra_delay = b_to_a_median - original_a_median

        f.write(f"OPGRADERINGS-RATE: {escalation_rate}% af alle B-kørsler\n\n")

        f.write("RESPONSTIDER:\n")
        for _, row in escalation_stats.iterrows():
            f.write(f"  {row['Kategori']}: {row['Median_minutter']} min (median)\n")

        f.write(f"\nEKSTRA FORSINKELSE: {extra_delay:+.1f} min\n")
        f.write(f"(B→A vs. original A)\n\n")

        f.write("=" * 60 + "\n")
        f.write("\nKONKLUSION:\n")
        f.write(f"Ca. {escalation_rate}% af B-vurderinger bliver opgraderet til A.\n")
        f.write(f"Disse patienter oplever {extra_delay:.1f} min ekstra forsinkelse\n")
        f.write("sammenlignet med korrekt A-vurdering fra start.\n")

    logger.info(f"✓ Saved: {findings_file.name}")
