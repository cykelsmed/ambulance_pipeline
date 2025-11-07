"""Temporal analysis module for ambulance response times.

This module analyzes time-based patterns in response times:
- Rush hour analysis (hour-by-hour, 0-23)
- Seasonal analysis (month-by-month, 1-12)
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Any
import logging

logger = logging.getLogger(__name__)


def load_raw_data(file_path: str, sheet_name: str, region_name: str) -> pd.DataFrame:
    """Load raw data from Excel file.

    Args:
        file_path: Path to Excel file
        sheet_name: Name of sheet to load
        region_name: Name of region (for logging)

    Returns:
        DataFrame with raw data
    """
    logger.info(f"Loading {region_name} rådata from {file_path}, sheet '{sheet_name}'")

    df = pd.read_excel(file_path, sheet_name=sheet_name)
    logger.info(f"Loaded {len(df):,} rows from {region_name}")

    return df


def filter_a_cases(df: pd.DataFrame, hastegrad_col: str = 'Hastegrad ved oprettelse') -> pd.DataFrame:
    """Filter dataset to only A-priority cases.

    Args:
        df: Input DataFrame
        hastegrad_col: Name of priority column

    Returns:
        Filtered DataFrame with only A-cases
    """
    before_count = len(df)
    df_filtered = df[df[hastegrad_col] == 'A'].copy()
    after_count = len(df_filtered)

    logger.info(f"Filtered to A-cases: {before_count:,} → {after_count:,} rows ({after_count/before_count*100:.1f}%)")

    return df_filtered


def extract_hour(df: pd.DataFrame, timestamp_col: str = 'Alarm modtaget') -> pd.DataFrame:
    """Extract hour from timestamp column.

    Args:
        df: Input DataFrame
        timestamp_col: Name of timestamp column

    Returns:
        DataFrame with added 'Hour' column (0-23)
    """
    df = df.copy()
    df['Hour'] = pd.to_datetime(df[timestamp_col]).dt.hour

    logger.info(f"Extracted hour from '{timestamp_col}'")
    logger.info(f"  Hour range: {df['Hour'].min()}-{df['Hour'].max()}")
    logger.info(f"  Missing hours: {df['Hour'].isna().sum()}")

    return df


def calculate_hourly_stats(df: pd.DataFrame, respons_col: str = 'ResponstidMinutter') -> pd.DataFrame:
    """Calculate statistics per hour.

    Args:
        df: DataFrame with 'Hour' column and response time
        respons_col: Name of response time column

    Returns:
        DataFrame with hourly statistics
    """
    stats = df.groupby('Hour')[respons_col].agg([
        ('Antal_ture', 'count'),
        ('Gennemsnit_minutter', 'mean'),
        ('Median_minutter', 'median'),
        ('Std_minutter', 'std'),
        ('Min_minutter', 'min'),
        ('Max_minutter', 'max')
    ]).reset_index()

    # Round to 1 decimal place
    for col in ['Gennemsnit_minutter', 'Median_minutter', 'Std_minutter',
                'Min_minutter', 'Max_minutter']:
        stats[col] = stats[col].round(1)

    # Rename Hour column to Time for clarity
    stats = stats.rename(columns={'Hour': 'Time'})

    logger.info(f"Calculated statistics for {len(stats)} hours")
    logger.info(f"  Sample sizes: {stats['Antal_ture'].min():,} - {stats['Antal_ture'].max():,} per hour")

    return stats


def add_warnings(stats: pd.DataFrame, min_sample_size: int = 100) -> pd.DataFrame:
    """Add warning column for low sample sizes.

    Args:
        stats: DataFrame with hourly statistics
        min_sample_size: Minimum sample size threshold

    Returns:
        DataFrame with 'Advarsel' column
    """
    stats = stats.copy()
    stats['Advarsel'] = stats['Antal_ture'].apply(
        lambda x: '*' if x < min_sample_size else ''
    )

    low_sample_count = (stats['Antal_ture'] < min_sample_size).sum()
    logger.info(f"Hours with <{min_sample_size} incidents: {low_sample_count}")

    return stats


def create_datawrapper_csv(stats: pd.DataFrame,
                           color_green_max: float = 10.0,
                           color_yellow_max: float = 15.0) -> pd.DataFrame:
    """Create Datawrapper-compatible CSV with color categories.

    Args:
        stats: DataFrame with hourly statistics
        color_green_max: Upper threshold for green category
        color_yellow_max: Upper threshold for yellow category

    Returns:
        DataFrame formatted for Datawrapper
    """
    dw_df = pd.DataFrame({
        'Time_label': stats['Time'].apply(lambda h: f"{h:02d}:00-{(h+1) % 24:02d}:00"),
        'Median_minutter': stats['Median_minutter'],
        'Antal_ture': stats['Antal_ture'],
        'Kategori': stats['Median_minutter'].apply(
            lambda x: 'Grøn' if x < color_green_max
                     else 'Gul' if x <= color_yellow_max
                     else 'Rød'
        ),
        'Periode': stats['Time'].apply(
            lambda h: 'Nat' if h in [0, 1, 2, 3, 4]
                     else 'Morgen' if h in [5, 6, 7, 8]
                     else 'Formiddag' if h in [9, 10, 11]
                     else 'Middag' if h == 12
                     else 'Eftermiddag' if h in [13, 14, 15, 16, 17]
                     else 'Aften'
        )
    })

    logger.info("Created Datawrapper CSV with categories")
    logger.info(f"  Grøn: {(dw_df['Kategori'] == 'Grøn').sum()} hours")
    logger.info(f"  Gul: {(dw_df['Kategori'] == 'Gul').sum()} hours")
    logger.info(f"  Rød: {(dw_df['Kategori'] == 'Rød').sum()} hours")

    return dw_df


def generate_key_findings(stats: pd.DataFrame,
                         total_ture: int,
                         region_name: str = "Nordjylland",
                         period: str = "2021-2025") -> str:
    """Generate key findings text for journalists.

    Args:
        stats: DataFrame with hourly statistics
        total_ture: Total number of incidents analyzed
        region_name: Name of region
        period: Time period covered

    Returns:
        Formatted text with key findings
    """
    # Find best and worst hours
    best_hour = stats.loc[stats['Median_minutter'].idxmin()]
    worst_hour = stats.loc[stats['Median_minutter'].idxmax()]

    # Calculate rush hour effect (17:00)
    rush_hour = stats[stats['Time'] == 17].iloc[0] if 17 in stats['Time'].values else None

    # Calculate night effect (2-5am average)
    night_hours = stats[stats['Time'].isin([2, 3, 4, 5])]
    night_avg = night_hours['Median_minutter'].mean()

    # Calculate day effect (9-17 average)
    day_hours = stats[stats['Time'].isin(range(9, 18))]
    day_avg = day_hours['Median_minutter'].mean()

    # Calculate percentage difference
    pct_diff = ((worst_hour['Median_minutter'] - best_hour['Median_minutter']) /
                best_hour['Median_minutter'] * 100)

    findings = f"""TIDSMÆSSIGE ANALYSER - TID-PÅ-DØGNET (RUSH HOUR)
================================================

Datagrundlag:
- Region: {region_name}
- Periode: {period}
- Antal A-kørsler: {total_ture:,}
- Analysedato: {pd.Timestamp.now().strftime('%Y-%m-%d')}

HOVEDFUND:
----------

1. VÆRSTE RESPONSTID (kl. {worst_hour['Time']:02d}:00)
   - Median responstid: {worst_hour['Median_minutter']:.1f} minutter
   - Antal ture: {worst_hour['Antal_ture']:,}
   - {pct_diff:.1f}% langsommere end bedste time

2. BEDSTE RESPONSTID (kl. {best_hour['Time']:02d}:00)
   - Median responstid: {best_hour['Median_minutter']:.1f} minutter
   - Antal ture: {best_hour['Antal_ture']:,}
"""

    if rush_hour is not None:
        rush_pct = ((rush_hour['Median_minutter'] - best_hour['Median_minutter']) /
                   best_hour['Median_minutter'] * 100)
        findings += f"""
3. MYLDRETIDSEFFEKT (kl. 17:00)
   - Median responstid: {rush_hour['Median_minutter']:.1f} minutter
   - Antal ture: {rush_hour['Antal_ture']:,}
   - {rush_pct:.1f}% langsommere end bedste time
"""

    findings += f"""
4. MØNSTRE:
   - Dag (kl. 09-17): {day_avg:.1f} min median
   - Nat (kl. 02-05): {night_avg:.1f} min median
   - Nat vs Dag: {((night_avg - day_avg) / day_avg * 100):.1f}% langsommere om natten

ADVARSLER:
----------
- Median bruges som primært mål (mere robust end gennemsnit)
- Korrelation ≠ kausalitet (trafik kan ikke isoleres fra andre faktorer)
- Mulige forklaringer på mønstre:
  * Varierende antal ambulancer på vagt
  * Forskellige typer opkald (urbant vs landområder)
  * Trafikforhold (men ikke nødvendigvis den primære faktor)
- Kun {region_name} analyseret - ikke nødvendigvis repræsentativt for hele Danmark

METADATA:
---------
- Primær metrik: Median (ikke gennemsnit)
- Decimal places: 1
- Color coding: <10 min = Grøn, 10-15 min = Gul, >15 min = Rød
- Sample size threshold: 100 incidents per hour
"""

    # Add low sample warnings if any
    low_sample = stats[stats['Advarsel'] == '*']
    if len(low_sample) > 0:
        findings += f"\n- Timer med <100 kørsler (markeret med *): {', '.join([f'{h:02d}:00' for h in low_sample['Time']])}"

    return findings


def analyze_rush_hour(input_file: str,
                      sheet_name: str = "Nordjylland",
                      region_name: str = "Nordjylland",
                      output_dir: str = "3_output/current",
                      config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Main function to run rush hour analysis.

    Args:
        input_file: Path to input Excel file
        sheet_name: Name of sheet to load
        region_name: Name of region
        output_dir: Directory for output files
        config: Configuration dictionary (optional)

    Returns:
        Dictionary with analysis results and metadata
    """
    logger.info("="*80)
    logger.info("RUSH HOUR ANALYSIS - STARTING")
    logger.info("="*80)

    # Load config defaults if not provided
    if config is None:
        config = {
            'statistics': {
                'color_green_max': 10.0,
                'color_yellow_max': 15.0
            },
            'output': {'decimal_places': 1}
        }

    # Step 1: Load data
    df = load_raw_data(input_file, sheet_name, region_name)

    # Step 2: Filter to A-cases
    df_a = filter_a_cases(df)

    # Step 3: Extract hour
    df_a = extract_hour(df_a)

    # Step 4: Calculate statistics
    stats = calculate_hourly_stats(df_a)

    # Step 5: Add warnings
    stats = add_warnings(stats, min_sample_size=100)

    # Step 6: Create Datawrapper CSV
    dw_csv = create_datawrapper_csv(
        stats,
        color_green_max=config['statistics']['color_green_max'],
        color_yellow_max=config['statistics']['color_yellow_max']
    )

    # Step 7: Generate key findings
    key_findings = generate_key_findings(stats, len(df_a), region_name)

    # Step 8: Export files
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Export Excel
    excel_file = output_path / "05_responstid_per_time.xlsx"
    stats.to_excel(excel_file, sheet_name="Time-Analyse", index=False)
    logger.info(f"✓ Exported Excel: {excel_file}")

    # Export Datawrapper CSV
    csv_file = output_path / "DATAWRAPPER_responstid_per_time.csv"
    dw_csv.to_csv(csv_file, index=False, encoding='utf-8')
    logger.info(f"✓ Exported Datawrapper CSV: {csv_file}")

    # Export key findings
    findings_file = output_path / "05_responstid_per_time_FUND.txt"
    with open(findings_file, 'w', encoding='utf-8') as f:
        f.write(key_findings)
    logger.info(f"✓ Exported key findings: {findings_file}")

    logger.info("="*80)
    logger.info("RUSH HOUR ANALYSIS - COMPLETED")
    logger.info("="*80)

    return {
        'region': region_name,
        'ture_analyseret': len(df_a),
        'periode': f"{df_a['År'].min()}-{df_a['År'].max()}",
        'files_generated': [
            str(excel_file),
            str(csv_file),
            str(findings_file)
        ],
        'statistics': {
            'best_hour': int(stats.loc[stats['Median_minutter'].idxmin(), 'Time']),
            'worst_hour': int(stats.loc[stats['Median_minutter'].idxmax(), 'Time']),
            'best_median': float(stats['Median_minutter'].min()),
            'worst_median': float(stats['Median_minutter'].max())
        }
    }


# ============================================================================
# SEASONAL ANALYSIS FUNCTIONS
# ============================================================================


def calculate_monthly_stats(df: pd.DataFrame,
                           month_col: str = 'Måned',
                           respons_col: str = 'ResponstidMinutter') -> pd.DataFrame:
    """Calculate statistics per month.

    Args:
        df: DataFrame with month column and response time
        month_col: Name of month column (1-12)
        respons_col: Name of response time column

    Returns:
        DataFrame with monthly statistics
    """
    stats = df.groupby(month_col)[respons_col].agg([
        ('Antal_ture', 'count'),
        ('Gennemsnit_minutter', 'mean'),
        ('Median_minutter', 'median'),
        ('Std_minutter', 'std'),
        ('Min_minutter', 'min'),
        ('Max_minutter', 'max')
    ]).reset_index()

    # Round to 1 decimal place
    for col in ['Gennemsnit_minutter', 'Median_minutter', 'Std_minutter',
                'Min_minutter', 'Max_minutter']:
        stats[col] = stats[col].round(1)

    # Rename month column
    stats = stats.rename(columns={month_col: 'Maaned_nummer'})

    # Add month names (Danish)
    month_names = {
        1: 'Januar', 2: 'Februar', 3: 'Marts', 4: 'April',
        5: 'Maj', 6: 'Juni', 7: 'Juli', 8: 'August',
        9: 'September', 10: 'Oktober', 11: 'November', 12: 'December'
    }
    stats['Maaned_navn'] = stats['Maaned_nummer'].map(month_names)

    # Add season classification
    def get_season(month):
        if month in [12, 1, 2]:
            return 'Vinter'
        elif month in [3, 4, 5]:
            return 'Forår'
        elif month in [6, 7, 8]:
            return 'Sommer'
        else:
            return 'Efterår'

    stats['Sæson'] = stats['Maaned_nummer'].apply(get_season)

    # Reorder columns
    cols = ['Maaned_nummer', 'Maaned_navn', 'Antal_ture', 'Gennemsnit_minutter',
            'Median_minutter', 'Std_minutter', 'Min_minutter', 'Max_minutter', 'Sæson']
    stats = stats[cols]

    logger.info(f"Calculated statistics for {len(stats)} months")
    logger.info(f"  Sample sizes: {stats['Antal_ture'].min():,} - {stats['Antal_ture'].max():,} per month")

    return stats


def create_seasonal_datawrapper_csv(stats: pd.DataFrame,
                                   color_green_max: float = 10.0,
                                   color_yellow_max: float = 15.0) -> pd.DataFrame:
    """Create Datawrapper-compatible CSV for seasonal analysis.

    Args:
        stats: DataFrame with monthly statistics
        color_green_max: Upper threshold for green category
        color_yellow_max: Upper threshold for yellow category

    Returns:
        DataFrame formatted for Datawrapper
    """
    dw_df = pd.DataFrame({
        'Maaned_navn': stats['Maaned_navn'],
        'Median_minutter': stats['Median_minutter'],
        'Antal_ture': stats['Antal_ture'],
        'Kategori': stats['Median_minutter'].apply(
            lambda x: 'Grøn' if x < color_green_max
                     else 'Gul' if x <= color_yellow_max
                     else 'Rød'
        ),
        'Sæson': stats['Sæson']
    })

    logger.info("Created Datawrapper CSV for seasonal analysis")
    logger.info(f"  Grøn: {(dw_df['Kategori'] == 'Grøn').sum()} months")
    logger.info(f"  Gul: {(dw_df['Kategori'] == 'Gul').sum()} months")
    logger.info(f"  Rød: {(dw_df['Kategori'] == 'Rød').sum()} months")

    return dw_df


def generate_seasonal_key_findings(stats: pd.DataFrame,
                                  total_ture: int,
                                  region_name: str = "Nordjylland",
                                  period: str = "2021-2025") -> str:
    """Generate key findings for seasonal analysis.

    Args:
        stats: DataFrame with monthly statistics
        total_ture: Total number of incidents analyzed
        region_name: Name of region
        period: Time period covered

    Returns:
        Formatted text with key findings
    """
    # Find best and worst months
    best_month = stats.loc[stats['Median_minutter'].idxmin()]
    worst_month = stats.loc[stats['Median_minutter'].idxmax()]

    # Calculate seasonal averages
    winter_months = stats[stats['Sæson'] == 'Vinter']
    spring_months = stats[stats['Sæson'] == 'Forår']
    summer_months = stats[stats['Sæson'] == 'Sommer']
    autumn_months = stats[stats['Sæson'] == 'Efterår']

    winter_avg = winter_months['Median_minutter'].mean()
    spring_avg = spring_months['Median_minutter'].mean()
    summer_avg = summer_months['Median_minutter'].mean()
    autumn_avg = autumn_months['Median_minutter'].mean()

    # Calculate percentage difference
    pct_diff = ((worst_month['Median_minutter'] - best_month['Median_minutter']) /
                best_month['Median_minutter'] * 100)

    # Winter vs Spring comparison
    winter_spring_diff = ((winter_avg - spring_avg) / spring_avg * 100)

    findings = f"""TIDSMÆSSIGE ANALYSER - SÆSONVARIATION
======================================

Datagrundlag:
- Region: {region_name}
- Periode: {period}
- Antal A-kørsler: {total_ture:,}
- Analysedato: {pd.Timestamp.now().strftime('%Y-%m-%d')}

HOVEDFUND:
----------

1. VÆRSTE MÅNED ({worst_month['Maaned_navn']})
   - Median responstid: {worst_month['Median_minutter']:.1f} minutter
   - Antal ture: {int(worst_month['Antal_ture']):,}
   - {pct_diff:.1f}% langsommere end bedste måned

2. BEDSTE MÅNED ({best_month['Maaned_navn']})
   - Median responstid: {best_month['Median_minutter']:.1f} minutter
   - Antal ture: {int(best_month['Antal_ture']):,}

3. SÆSONMØNSTRE:
   - Vinter (Dec-Feb): {winter_avg:.1f} min median
   - Forår (Mar-Maj): {spring_avg:.1f} min median
   - Sommer (Jun-Aug): {summer_avg:.1f} min median
   - Efterår (Sep-Nov): {autumn_avg:.1f} min median

4. VINTER VS FORÅR:
   - Vinter er {winter_spring_diff:.1f}% langsommere end forår
   - Journalistisk vinkel: "Vinterkrise i akuthjælpen"

ADVARSLER & METODEKRITIK:
--------------------------
⚠️ KORRELATION ≠ KAUSALITET
   Mange faktorer påvirker samtidig:
   - Vejrforhold (sne, glat underlag)
   - Influenza-sæson (flere opkald)
   - Bemandingsniveau (ferieplanlægning)
   - Trafiktæthed (jule-/nytårstrafik)

⚠️ COVID-19 PERIODE INKLUDERET
   {period} data kan være påvirket af:
   - Lockdowns (mindre trafik)
   - Overbelastning af sundhedsvæsen
   - Ændret opkaldsmønster

⚠️ KUN {region_name.upper()}
   - Ikke nødvendigvis repræsentativt for hele Danmark
   - Hovedstaden kan have anden sæsonprofil

⚠️ 5-ÅRS SAMLET DATA
   - Analyse viser gennemsnit over {period}
   - Individuelle år kan afvige væsentligt

METADATA:
---------
- Primær metrik: Median (ikke gennemsnit)
- Decimal places: 1
- Sæson-definition:
  * Vinter: December, Januar, Februar
  * Forår: Marts, April, Maj
  * Sommer: Juni, Juli, August
  * Efterår: September, Oktober, November
"""

    return findings


def analyze_seasonal(input_file: str,
                    sheet_name: str = "Nordjylland",
                    region_name: str = "Nordjylland",
                    output_dir: str = "3_output/current",
                    config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Main function to run seasonal analysis.

    Args:
        input_file: Path to input Excel file
        sheet_name: Name of sheet to load
        region_name: Name of region
        output_dir: Directory for output files
        config: Configuration dictionary (optional)

    Returns:
        Dictionary with analysis results and metadata
    """
    logger.info("="*80)
    logger.info("SEASONAL ANALYSIS - STARTING")
    logger.info("="*80)

    # Load config defaults if not provided
    if config is None:
        config = {
            'statistics': {
                'color_green_max': 10.0,
                'color_yellow_max': 15.0
            },
            'output': {'decimal_places': 1}
        }

    # Step 1: Load data
    df = load_raw_data(input_file, sheet_name, region_name)

    # Step 2: Filter to A-cases
    df_a = filter_a_cases(df)

    # Step 3: Calculate monthly statistics (month column already exists!)
    stats = calculate_monthly_stats(df_a)

    # Step 4: Create Datawrapper CSV
    dw_csv = create_seasonal_datawrapper_csv(
        stats,
        color_green_max=config['statistics']['color_green_max'],
        color_yellow_max=config['statistics']['color_yellow_max']
    )

    # Step 5: Generate key findings
    key_findings = generate_seasonal_key_findings(stats, len(df_a), region_name)

    # Step 6: Export files
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Export Excel
    excel_file = output_path / "06_responstid_per_maaned.xlsx"
    stats.to_excel(excel_file, sheet_name="Måneds-Analyse", index=False)
    logger.info(f"✓ Exported Excel: {excel_file}")

    # Export Datawrapper CSV
    csv_file = output_path / "DATAWRAPPER_responstid_per_maaned.csv"
    dw_csv.to_csv(csv_file, index=False, encoding='utf-8')
    logger.info(f"✓ Exported Datawrapper CSV: {csv_file}")

    # Export key findings
    findings_file = output_path / "06_responstid_per_maaned_FUND.txt"
    with open(findings_file, 'w', encoding='utf-8') as f:
        f.write(key_findings)
    logger.info(f"✓ Exported key findings: {findings_file}")

    logger.info("="*80)
    logger.info("SEASONAL ANALYSIS - COMPLETED")
    logger.info("="*80)

    return {
        'region': region_name,
        'ture_analyseret': len(df_a),
        'periode': f"{df_a['År'].min()}-{df_a['År'].max()}",
        'files_generated': [
            str(excel_file),
            str(csv_file),
            str(findings_file)
        ],
        'statistics': {
            'best_month': int(stats.loc[stats['Median_minutter'].idxmin(), 'Maaned_nummer']),
            'worst_month': int(stats.loc[stats['Median_minutter'].idxmax(), 'Maaned_nummer']),
            'best_median': float(stats['Median_minutter'].min()),
            'worst_median': float(stats['Median_minutter'].max())
        }
    }
