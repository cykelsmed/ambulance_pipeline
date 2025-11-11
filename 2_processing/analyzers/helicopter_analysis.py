"""Helicopter Analysis Module

This module analyzes national helicopter (HEMS) data:
1. National overview statistics
2. Regional breakdown
3. Base performance
4. Temporal patterns (monthly/yearly)
5. Postal code coverage
6. Dispatch delay vs flight time
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


def parse_month_year(month_str: str) -> str:
    """Convert Danish month-year string to YYYY-MM format.

    Args:
        month_str: Danish format like "juli 2021"

    Returns:
        ISO format like "2021-07"
    """
    months = {
        'januar': 1, 'februar': 2, 'marts': 3, 'april': 4,
        'maj': 5, 'juni': 6, 'juli': 7, 'august': 8,
        'september': 9, 'oktober': 10, 'november': 11, 'december': 12
    }
    parts = month_str.lower().split()
    month_name = parts[0]
    year = int(parts[1])
    month = months[month_name]
    return f'{year}-{month:02d}'


def time_to_minutes(time_str: str) -> float:
    """Convert HH:MM time string to minutes since midnight.

    Args:
        time_str: Time in "HH:MM" format

    Returns:
        Minutes since midnight (0-1439)
    """
    if pd.isna(time_str):
        return np.nan
    try:
        parts = time_str.split(':')
        return int(parts[0]) * 60 + int(parts[1])
    except:
        return np.nan


def calculate_duration(start_min: float, end_min: float, max_minutes: int = 180) -> float:
    """Calculate duration handling midnight crossings and outliers.

    Args:
        start_min: Start time in minutes since midnight
        end_min: End time in minutes since midnight
        max_minutes: Maximum reasonable duration (default 180 min = 3 hours)

    Returns:
        Duration in minutes, or NaN if invalid/outlier
    """
    if pd.isna(start_min) or pd.isna(end_min):
        return np.nan

    diff = end_min - start_min

    # Handle midnight crossing (e.g., 23:55 -> 00:05 = -1430 min -> +10 min)
    if diff < 0:
        diff += 1440  # Add 24 hours

    # Remove outliers (likely data errors)
    if diff > max_minutes:
        return np.nan

    return diff


def load_and_clean_helicopter_data(file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Load helicopter data and perform cleaning/calculations.

    Args:
        file_path: Path to helicopter Excel file

    Returns:
        Tuple of (cleaned DataFrame, metadata dict)
    """
    logger.info(f"Loading helicopter data from {file_path}")

    # Load data
    df = pd.read_excel(file_path, sheet_name='Ark1')
    original_count = len(df)

    logger.info(f"  Loaded {original_count:,} helicopter cases")

    # Parse dates
    df['year_month'] = df['Måned og år'].apply(parse_month_year)
    df['year'] = df['year_month'].str[:4].astype(int)

    # Convert times to minutes
    df['alarm_min'] = df['Tid alarm'].apply(time_to_minutes)
    df['airborne_min'] = df['Tid airborne'].apply(time_to_minutes)
    df['ankomst_min'] = df['Tid ankomst skadested'].apply(time_to_minutes)

    # Calculate durations
    df['dispatch_delay'] = df.apply(
        lambda row: calculate_duration(row['alarm_min'], row['airborne_min']),
        axis=1
    )
    df['flight_time'] = df.apply(
        lambda row: calculate_duration(row['airborne_min'], row['ankomst_min']),
        axis=1
    )
    df['total_response'] = df.apply(
        lambda row: calculate_duration(row['alarm_min'], row['ankomst_min']),
        axis=1
    )

    # Remove invalid cases (outliers)
    valid_mask = (df['total_response'] <= 180) & (df['total_response'].notna())
    df_clean = df[valid_mask].copy()

    removed_count = original_count - len(df_clean)
    logger.info(f"  Removed {removed_count:,} outliers/errors ({removed_count/original_count*100:.1f}%)")
    logger.info(f"  Valid cases: {len(df_clean):,} ({len(df_clean)/original_count*100:.1f}%)")

    # Metadata
    metadata = {
        'original_count': original_count,
        'valid_count': len(df_clean),
        'removed_count': removed_count,
        'removal_pct': round(removed_count / original_count * 100, 1),
        'date_range_start': df_clean['year_month'].min(),
        'date_range_end': df_clean['year_month'].max(),
        'regions': df_clean['Disponerende region'].nunique(),
        'bases': df_clean['Helikopterbase'].nunique(),
        'postal_codes': df_clean['Skadested Postnummer'].nunique()
    }

    return df_clean, metadata


def analyze_national_overview(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate national overview statistics.

    Args:
        df: Cleaned helicopter DataFrame

    Returns:
        DataFrame with national statistics
    """
    logger.info("Calculating national helicopter overview...")

    stats = []

    for metric in ['dispatch_delay', 'flight_time', 'total_response']:
        stats.append({
            'Metric': metric.replace('_', ' ').title(),
            'Gennemsnit_min': round(df[metric].mean(), 1),
            'Median_min': round(df[metric].median(), 1),
            'Percentil_90': round(df[metric].quantile(0.9), 1),
            'Min': round(df[metric].min(), 1),
            'Max': round(df[metric].max(), 1),
            'Std': round(df[metric].std(), 1)
        })

    return pd.DataFrame(stats)


def analyze_regional_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze response times by region.

    Args:
        df: Cleaned helicopter DataFrame

    Returns:
        DataFrame with regional statistics
    """
    logger.info("Analyzing regional helicopter breakdown...")

    regional = df.groupby('Disponerende region').agg({
        'total_response': ['mean', 'median', 'count'],
        'dispatch_delay': 'mean',
        'flight_time': 'mean'
    }).round(1)

    # Flatten columns
    regional.columns = ['_'.join(col).strip() for col in regional.columns.values]
    regional = regional.reset_index()

    # Rename for clarity
    regional.columns = [
        'Region',
        'Total_Response_Gennemsnit',
        'Total_Response_Median',
        'Antal_Cases',
        'Dispatch_Delay_Gennemsnit',
        'Flight_Time_Gennemsnit'
    ]

    # Add percentage of total
    regional['Procent_af_Total'] = (regional['Antal_Cases'] / regional['Antal_Cases'].sum() * 100).round(1)

    # Sort by response time
    regional = regional.sort_values('Total_Response_Gennemsnit')

    logger.info(f"  Analyzed {len(regional)} regions")

    return regional


def analyze_base_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze response times by helicopter base.

    Args:
        df: Cleaned helicopter DataFrame

    Returns:
        DataFrame with base statistics
    """
    logger.info("Analyzing helicopter base performance...")

    base = df.groupby('Helikopterbase').agg({
        'total_response': ['mean', 'median', 'count'],
        'dispatch_delay': 'mean',
        'flight_time': 'mean'
    }).round(1)

    # Flatten columns
    base.columns = ['_'.join(col).strip() for col in base.columns.values]
    base = base.reset_index()

    # Rename for clarity
    base.columns = [
        'Base',
        'Total_Response_Gennemsnit',
        'Total_Response_Median',
        'Antal_Cases',
        'Dispatch_Delay_Gennemsnit',
        'Flight_Time_Gennemsnit'
    ]

    # Add percentage of total
    base['Procent_af_Total'] = (base['Antal_Cases'] / base['Antal_Cases'].sum() * 100).round(1)

    # Sort by response time
    base = base.sort_values('Total_Response_Gennemsnit')

    logger.info(f"  Analyzed {len(base)} helicopter bases")

    return base


def analyze_yearly_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze yearly trends.

    Args:
        df: Cleaned helicopter DataFrame

    Returns:
        DataFrame with yearly statistics
    """
    logger.info("Analyzing yearly helicopter trends...")

    yearly = df.groupby('year').agg({
        'total_response': ['mean', 'median', 'count'],
        'dispatch_delay': 'mean',
        'flight_time': 'mean',
        'Disponerende region': 'nunique'
    }).round(1)

    # Flatten columns
    yearly.columns = ['_'.join(col).strip() for col in yearly.columns.values]
    yearly = yearly.reset_index()

    # Rename for clarity
    yearly.columns = [
        'År',
        'Total_Response_Gennemsnit',
        'Total_Response_Median',
        'Antal_Cases',
        'Dispatch_Delay_Gennemsnit',
        'Flight_Time_Gennemsnit',
        'Antal_Regioner'
    ]

    # Add percentage of total
    yearly['Procent_af_Total'] = (yearly['Antal_Cases'] / yearly['Antal_Cases'].sum() * 100).round(1)

    logger.info(f"  Analyzed {len(yearly)} years")

    return yearly


def analyze_monthly_seasonality(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze monthly seasonal patterns.

    Args:
        df: Cleaned helicopter DataFrame

    Returns:
        DataFrame with monthly statistics
    """
    logger.info("Analyzing monthly seasonality...")

    monthly = df.groupby('year_month').agg({
        'total_response': ['mean', 'count']
    }).round(1)

    # Flatten columns
    monthly.columns = ['_'.join(col).strip() for col in monthly.columns.values]
    monthly = monthly.reset_index()

    # Rename
    monthly.columns = ['Måned', 'Gennemsnit_Responstid', 'Antal_Cases']

    # Sort by count to find busiest months
    monthly_sorted = monthly.sort_values('Antal_Cases', ascending=False)

    logger.info(f"  Analyzed {len(monthly)} months")
    logger.info(f"  Busiest month: {monthly_sorted.iloc[0]['Måned']} ({monthly_sorted.iloc[0]['Antal_Cases']:.0f} cases)")

    return monthly_sorted


def analyze_postal_coverage(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze postal code coverage.

    Args:
        df: Cleaned helicopter DataFrame

    Returns:
        DataFrame with postal code statistics
    """
    logger.info("Analyzing postal code coverage...")

    postal = df.groupby('Skadested Postnummer').agg({
        'total_response': ['mean', 'median', 'count']
    }).round(1)

    # Flatten columns
    postal.columns = ['_'.join(col).strip() for col in postal.columns.values]
    postal = postal.reset_index()

    # Rename
    postal.columns = ['Postnummer', 'Gennemsnit_min', 'Median_min', 'Antal_Cases']

    # Sort by cases (most common postal codes)
    postal = postal.sort_values('Antal_Cases', ascending=False)

    logger.info(f"  Analyzed {len(postal)} unique postal codes")
    logger.info(f"  Most common: {postal.iloc[0]['Postnummer']} ({postal.iloc[0]['Antal_Cases']:.0f} cases)")

    return postal


def generate_findings_text(df: pd.DataFrame,
                          regional: pd.DataFrame,
                          base: pd.DataFrame,
                          yearly: pd.DataFrame,
                          monthly: pd.DataFrame,
                          metadata: Dict[str, Any]) -> str:
    """Generate text findings summary.

    Args:
        df: Cleaned helicopter DataFrame
        regional: Regional analysis
        base: Base analysis
        yearly: Yearly analysis
        monthly: Monthly analysis
        metadata: Data metadata

    Returns:
        Formatted findings text
    """
    logger.info("Generating helicopter findings text...")

    # National stats
    avg_total = df['total_response'].mean()
    median_total = df['total_response'].median()
    avg_dispatch = df['dispatch_delay'].mean()
    avg_flight = df['flight_time'].mean()

    # Regional extremes
    fastest_region = regional.iloc[0]
    slowest_region = regional.iloc[-1]

    # Base extremes
    fastest_base = base.iloc[0]
    slowest_base = base.iloc[-1]

    # Monthly extremes
    busiest_month = monthly.iloc[0]
    quietest_month = monthly.iloc[-1]

    # Yearly
    yearly_sorted = yearly.sort_values('Antal_Cases', ascending=False)
    busiest_year = yearly_sorted.iloc[0]

    findings = f"""HELIKOPTER (HEMS) ANALYSE - KEY FINDINGS

=== DATAGRUNDLAG ===
Periode: {metadata['date_range_start']} til {metadata['date_range_end']}
Total cases: {metadata['valid_count']:,} (efter rensning)
Fjernet som fejl: {metadata['removed_count']:,} ({metadata['removal_pct']}%)
Regioner: {metadata['regions']}
Helikopterbaser: {metadata['bases']}
Postnumre dækket: {metadata['postal_codes']}

=== NATIONAL OVERSIGT ===
Total responstid (alarm → arrival):
  - Gennemsnit: {avg_total:.1f} min
  - Median: {median_total:.1f} min

Komponentopdeling:
  - Dispatch delay (alarm → airborne): {avg_dispatch:.1f} min ({avg_dispatch/avg_total*100:.0f}% af total)
  - Flight time (airborne → arrival): {avg_flight:.1f} min ({avg_flight/avg_total*100:.0f}% af total)

=== FUND 1: DISPATCH DELAY ===
Helikoptere bruger {avg_dispatch:.1f} minutter fra alarm til de letter.
Dette er betydeligt længere end ambulancer (~2 min).

Journalistisk vinkel:
"Når du får helikopter venter du {avg_dispatch:.1f} minutter før den overhovedet letter - {avg_dispatch/2:.1f}x længere end ambulance"

=== FUND 2: REGIONAL VARIATION ===
Hurtigste region: {fastest_region['Region']} ({fastest_region['Total_Response_Gennemsnit']:.1f} min)
Langsomste region: {slowest_region['Region']} ({slowest_region['Total_Response_Gennemsnit']:.1f} min)
Forskel: {slowest_region['Total_Response_Gennemsnit'] - fastest_region['Total_Response_Gennemsnit']:.1f} min ({(slowest_region['Total_Response_Gennemsnit']/fastest_region['Total_Response_Gennemsnit']-1)*100:.0f}% langsommere)

VIGTIGT FUND: {slowest_region['Region']} har kun {slowest_region['Antal_Cases']:.0f} cases ({slowest_region['Procent_af_Total']:.1f}%)
Dette tyder på at helikopter bruges meget sjældent i denne region.

Regional fordeling (antal cases):
"""

    for _, row in regional.iterrows():
        findings += f"  - {row['Region']}: {row['Antal_Cases']:.0f} cases ({row['Procent_af_Total']:.1f}%)\n"

    findings += f"""
=== FUND 3: HELIKOPTERBASE PERFORMANCE ===
Hurtigste base: {fastest_base['Base']} ({fastest_base['Total_Response_Gennemsnit']:.1f} min, {fastest_base['Antal_Cases']:.0f} cases)
Langsomste base: {slowest_base['Base']} ({slowest_base['Total_Response_Gennemsnit']:.1f} min, {slowest_base['Antal_Cases']:.0f} cases)

=== FUND 4: SÆSONMÆSSIGHED ===
Travleste måned: {busiest_month['Måned']} ({busiest_month['Antal_Cases']:.0f} cases)
Roligste måned: {quietest_month['Måned']} ({quietest_month['Antal_Cases']:.0f} cases)
Forskel: {(busiest_month['Antal_Cases'] / quietest_month['Antal_Cases'] - 1) * 100:.0f}% flere cases i travleste måned

Journalistisk vinkel:
"Helikopteren presser om sommeren - {(busiest_month['Antal_Cases'] / quietest_month['Antal_Cases'] - 1) * 100:.0f}% flere udrykninger i {busiest_month['Måned'].split('-')[1]} sammenlignet med roligste måned"

=== FUND 5: ÅRLIG UDVIKLING ===
Travleste år: {busiest_year['År']:.0f} ({busiest_year['Antal_Cases']:.0f} cases)
Gennemsnitlig responstid per år:
"""

    for _, row in yearly.sort_values('År').iterrows():
        findings += f"  - {row['År']:.0f}: {row['Total_Response_Gennemsnit']:.1f} min ({row['Antal_Cases']:.0f} cases)\n"

    findings += f"""
=== ANBEFALING TIL JOURNALISTIK ===

1. BRUG helikopterdata til at:
   ✓ Validere "værste postnumre" (er det helikopter eller ambulance?)
   ✓ Udvide alarmtid-analyse (dispatch delay {avg_dispatch:.1f} min vs. ~2 min ambulance)
   ✓ Forklare regional variation (nogle regioner bruger helikopter 5x mere end andre)
   ✓ Sæsonmønstre (sommeren presser helikopteren)

2. UNDGÅ at:
   ✗ Sammenligne direkte med ambulance-responstider (forskellig use case)
   ✗ Inkludere i national ambulance-gennemsnit (for lille volumen, ~1%)

3. VIGTIG ADVARSEL:
   Helikoptere bruges til høj-kompleksitet cases (traumer, hjertestop).
   De supplerer - ikke erstatter - ambulancer.
   Direkte sammenligning kan være misvisende uden kontekst.

=== NÆSTE SKRIDT ===
- Cross-reference helikopter postnumre med "værste postnumre" i ambulance-analyse
- Undersøg {slowest_region['Region']} anomali (hvorfor {slowest_region['Total_Response_Gennemsnit']:.1f} min vs. {fastest_region['Total_Response_Gennemsnit']:.1f} min?)
- Spørg Nils om ABC-prioritet data for helikoptere
"""

    return findings


def run_helicopter_analysis(file_path: str, output_dir: str) -> Dict[str, Any]:
    """Run complete helicopter analysis pipeline.

    Args:
        file_path: Path to helicopter Excel file
        output_dir: Directory for output files

    Returns:
        Dictionary with analysis results
    """
    logger.info("="*80)
    logger.info("STARTING HELICOPTER ANALYSIS")
    logger.info("="*80)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Load and clean data
    df, metadata = load_and_clean_helicopter_data(file_path)

    # Run analyses
    national = analyze_national_overview(df)
    regional = analyze_regional_breakdown(df)
    base = analyze_base_performance(df)
    yearly = analyze_yearly_trends(df)
    monthly = analyze_monthly_seasonality(df)
    postal = analyze_postal_coverage(df)

    # Generate findings text
    findings = generate_findings_text(df, regional, base, yearly, monthly, metadata)

    # Save outputs
    logger.info("Saving helicopter analysis outputs...")

    # Excel outputs
    with pd.ExcelWriter(output_path / 'helikopter_national_oversigt.xlsx', engine='openpyxl') as writer:
        national.to_excel(writer, sheet_name='National Stats', index=False)
        metadata_df = pd.DataFrame([metadata])
        metadata_df.to_excel(writer, sheet_name='Metadata', index=False)

    regional.to_excel(output_path / 'helikopter_regional_sammenligning.xlsx', index=False)
    base.to_excel(output_path / 'helikopter_base_performance.xlsx', index=False)
    yearly.to_excel(output_path / 'helikopter_årlig_udvikling.xlsx', index=False)
    monthly.to_excel(output_path / 'helikopter_månedlig_sæsonmønstre.xlsx', index=False)
    postal.to_excel(output_path / 'helikopter_postnummer_dækning.xlsx', index=False)

    # Text findings
    with open(output_path / 'HELIKOPTER_FUND.txt', 'w', encoding='utf-8') as f:
        f.write(findings)

    logger.info(f"  Saved 6 Excel files to {output_dir}/")
    logger.info(f"  Saved findings to {output_dir}/HELIKOPTER_FUND.txt")

    logger.info("="*80)
    logger.info("HELICOPTER ANALYSIS COMPLETE")
    logger.info("="*80)

    return {
        'national': national,
        'regional': regional,
        'base': base,
        'yearly': yearly,
        'monthly': monthly,
        'postal': postal,
        'findings': findings,
        'metadata': metadata
    }
