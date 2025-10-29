"""Core analyses: Top 10, regional comparison, all postnumre."""
import pandas as pd
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)


def analyze_alle_postnumre(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """Generate master file with all postnumre.

    Output: 01_alle_postnumre.xlsx

    Columns:
    - Postnummer
    - Antal_ture
    - Gennemsnit_minutter
    - Max_minutter
    - Region

    Args:
        df: Normalized DataFrame
        config: Pipeline configuration

    Returns:
        DataFrame sorted by Gennemsnit_minutter (descending)
    """
    logger.info("Generating analysis: Alle postnumre")

    result = df[['Postnummer', 'Antal_ture', 'Gennemsnit_minutter', 'Max_minutter', 'Region']].copy()

    # Round to 1 decimal
    decimal_places = config['output']['decimal_places']
    result['Gennemsnit_minutter'] = result['Gennemsnit_minutter'].round(decimal_places)
    result['Max_minutter'] = result['Max_minutter'].round(decimal_places)

    # Sort by worst first
    result = result.sort_values('Gennemsnit_minutter', ascending=False)

    logger.info(f"Generated alle postnumre: {len(result)} rows")

    return result


def analyze_top_10_værste(df: pd.DataFrame, config: Dict[str, Any]) -> Tuple[pd.DataFrame, int]:
    """Generate Top 10 worst postnumre (statistically validated).

    Output: 02_top_10_værste_VALIDERET.xlsx

    Filter: Only postnumre with ≥50 ture
    Sort: Descending by Gennemsnit_minutter
    Take: Top 10

    Args:
        df: Normalized DataFrame
        config: Pipeline configuration

    Returns:
        Tuple of (DataFrame with top 10, total count meeting threshold)
    """
    logger.info("Generating analysis: Top 10 værste")

    min_ture = config['statistics']['top_10_min_ture']

    # Filter by minimum ture
    validated = df[df['Antal_ture'] >= min_ture].copy()

    logger.info(f"Postnumre with ≥{min_ture} ture: {len(validated)}")

    if len(validated) == 0:
        logger.error(f"No postnumre meet the {min_ture} ture threshold!")
        raise ValueError(f"Cannot generate Top 10: No postnumre with ≥{min_ture} ture")

    if len(validated) < 10:
        logger.warning(f"Only {len(validated)} postnumre meet threshold (expected ≥10)")

    # Sort and take top 10
    top_10 = validated.nlargest(10, 'Gennemsnit_minutter')

    # Select and order columns
    result = top_10[['Postnummer', 'Gennemsnit_minutter', 'Antal_ture', 'Region']].copy()

    # Round to 1 decimal
    decimal_places = config['output']['decimal_places']
    result['Gennemsnit_minutter'] = result['Gennemsnit_minutter'].round(decimal_places)

    logger.info(f"Generated top 10 værste: {len(result)} rows")

    return result, len(validated)


def analyze_top_10_bedste(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """Generate Top 10 best postnumre (statistically validated).

    Output: 03_top_10_bedste.xlsx

    Filter: Only postnumre with ≥50 ture
    Sort: Ascending by Gennemsnit_minutter
    Take: Top 10

    Args:
        df: Normalized DataFrame
        config: Pipeline configuration

    Returns:
        DataFrame with top 10 best
    """
    logger.info("Generating analysis: Top 10 bedste")

    min_ture = config['statistics']['top_10_min_ture']

    # Filter by minimum ture
    validated = df[df['Antal_ture'] >= min_ture].copy()

    logger.info(f"Postnumre with ≥{min_ture} ture: {len(validated)}")

    # Sort and take top 10 (smallest values)
    top_10 = validated.nsmallest(10, 'Gennemsnit_minutter')

    # Select and order columns
    result = top_10[['Postnummer', 'Gennemsnit_minutter', 'Antal_ture', 'Region']].copy()

    # Round to 1 decimal
    decimal_places = config['output']['decimal_places']
    result['Gennemsnit_minutter'] = result['Gennemsnit_minutter'].round(decimal_places)

    logger.info(f"Generated top 10 bedste: {len(result)} rows")

    return result


def analyze_regional_sammenligning(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """Generate regional comparison.

    Output: 04_regional_sammenligning.xlsx

    Group by: Region
    Aggregate: mean, median, sum(ture), count(postnumre)
    Sort: Descending by Gennemsnit_minutter (worst first)

    Derived fields:
    - Forskel_til_bedste: Difference from best region
    - Procent_over_bedste: % difference from best region

    Args:
        df: Normalized DataFrame
        config: Pipeline configuration

    Returns:
        DataFrame with regional statistics
    """
    logger.info("Generating analysis: Regional sammenligning")

    # Aggregate by region
    regional_stats = df.groupby('Region').agg({
        'Gennemsnit_minutter': ['mean', 'median'],
        'Antal_ture': 'sum',
        'Postnummer': 'count'
    }).reset_index()

    # Flatten column names
    regional_stats.columns = [
        'Region',
        'Gennemsnit_minutter',
        'Median_minutter',
        'Total_ture',
        'Antal_postnumre'
    ]

    # Round to 1 decimal
    decimal_places = config['output']['decimal_places']
    regional_stats['Gennemsnit_minutter'] = regional_stats['Gennemsnit_minutter'].round(decimal_places)
    regional_stats['Median_minutter'] = regional_stats['Median_minutter'].round(decimal_places)

    # Sort by worst first
    regional_stats = regional_stats.sort_values('Gennemsnit_minutter', ascending=False)

    # Calculate derived fields
    best_time = regional_stats['Gennemsnit_minutter'].min()

    regional_stats['Forskel_til_bedste'] = (
        regional_stats['Gennemsnit_minutter'] - best_time
    ).round(decimal_places)

    regional_stats['Procent_over_bedste'] = (
        (regional_stats['Gennemsnit_minutter'] / best_time - 1) * 100
    ).round(1)

    logger.info(f"Generated regional sammenligning: {len(regional_stats)} regions")

    return regional_stats


def analyze_datawrapper_csv(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """Generate Datawrapper-ready CSV for map visualization.

    Output: DATAWRAPPER_alle_postnumre.csv

    Include: All postnumre (no filter)
    Add: Kategori (Grøn/Gul/Rød based on response time)

    Color mapping:
    - Grøn: <10 min
    - Gul: 10-15 min
    - Rød: >15 min

    Args:
        df: Normalized DataFrame
        config: Pipeline configuration

    Returns:
        DataFrame ready for Datawrapper
    """
    logger.info("Generating analysis: Datawrapper CSV")

    result = df[['Postnummer', 'Gennemsnit_minutter', 'Antal_ture', 'Region']].copy()

    # Round to 1 decimal
    decimal_places = config['output']['decimal_places']
    result['Gennemsnit_minutter'] = result['Gennemsnit_minutter'].round(decimal_places)

    # Add color category
    green_max = config['statistics']['color_green_max']
    yellow_max = config['statistics']['color_yellow_max']

    def categorize(minutes):
        if minutes < green_max:
            return 'Grøn'
        elif minutes < yellow_max:
            return 'Gul'
        else:
            return 'Rød'

    result['Kategori'] = result['Gennemsnit_minutter'].apply(categorize)

    # Add note for statistically uncertain (<50 ture)
    min_ture = config['statistics']['top_10_min_ture']
    result['Note'] = result['Antal_ture'].apply(lambda x: '*' if x < min_ture else '')

    logger.info(f"Generated Datawrapper CSV: {len(result)} rows")

    # Count by category
    category_counts = result['Kategori'].value_counts()
    logger.info(f"Categories: {category_counts.to_dict()}")

    return result
