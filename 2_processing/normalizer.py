"""Data normalizer for ambulance data."""
import pandas as pd
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names to standard format.

    Expected columns after normalization:
    - Postnummer: Postal code
    - Antal_ture: Number of trips
    - Gennemsnit_minutter: Average response time in minutes
    - Max_minutter: Maximum response time in minutes
    - Region: Region name

    Args:
        df: DataFrame with raw column names

    Returns:
        DataFrame with normalized column names
    """
    df = df.copy()

    # Create mapping based on common patterns
    column_mapping = {}
    average_cols = []
    max_cols = []

    for col in df.columns:
        col_lower = str(col).lower()

        # Postnummer
        if 'row labels' in col_lower:
            column_mapping[col] = 'Postnummer'

        # Antal ture
        elif 'count' in col_lower:
            column_mapping[col] = 'Antal_ture'

        # Gennemsnit - collect all average columns
        elif 'average' in col_lower or 'gennemsnit' in col_lower:
            average_cols.append(col)

        # Max - collect all max columns
        elif 'max' in col_lower:
            max_cols.append(col)

        # Region (keep as is)
        elif col == 'Region':
            column_mapping[col] = 'Region'

    # Rename basic columns
    df.rename(columns=column_mapping, inplace=True)

    # Coalesce average columns: use first non-null value across all average columns
    if average_cols:
        df['Gennemsnit_minutter'] = df[average_cols].bfill(axis=1).iloc[:, 0]
        # Drop original average columns
        df.drop(columns=average_cols, inplace=True)

    # Coalesce max columns: use first non-null value across all max columns
    if max_cols:
        df['Max_minutter'] = df[max_cols].bfill(axis=1).iloc[:, 0]
        # Drop original max columns
        df.drop(columns=max_cols, inplace=True)

    logger.info(f"Normalized columns: {list(df.columns)}")

    # Verify we have required columns
    required = ['Postnummer', 'Antal_ture', 'Gennemsnit_minutter', 'Region']
    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(f"Missing required columns after normalization: {missing}")

    # Select only required columns
    available_cols = ['Postnummer', 'Antal_ture', 'Gennemsnit_minutter', 'Region']
    if 'Max_minutter' in df.columns:
        available_cols.append('Max_minutter')

    df = df[available_cols]

    return df


def normalize_postnummer(value: Any, mapping: Dict[str, int]) -> int:
    """Normalize a single postnummer value.

    Args:
        value: Raw postnummer value (can be int, str, or special case)
        mapping: Dictionary mapping special cases to numeric values

    Returns:
        Normalized postnummer as integer
    """
    # If already numeric, return as int
    if pd.isna(value):
        return None

    # If string, check mapping
    if isinstance(value, str):
        value = value.strip()
        if value in mapping:
            return mapping[value]

        # Try to convert to int
        try:
            return int(value)
        except ValueError:
            logger.warning(f"Could not convert postnummer: {value}")
            return None

    # Try to convert to int
    try:
        return int(value)
    except (ValueError, TypeError):
        logger.warning(f"Could not convert postnummer: {value}")
        return None


def normalize_postnumre(df: pd.DataFrame, mapping: Dict[str, int]) -> pd.DataFrame:
    """Normalize all postnummer values in DataFrame.

    Args:
        df: DataFrame with Postnummer column
        mapping: Dictionary mapping special cases to numeric values

    Returns:
        DataFrame with normalized postnumre
    """
    df = df.copy()

    df['Postnummer'] = df['Postnummer'].apply(lambda x: normalize_postnummer(x, mapping))

    # Remove rows with invalid postnumre
    before = len(df)
    df = df.dropna(subset=['Postnummer'])
    after = len(df)

    if before != after:
        logger.warning(f"Removed {before - after} rows with invalid postnumre")

    # Convert to int
    df['Postnummer'] = df['Postnummer'].astype(int)

    # Validate postnummer range (1000-9999)
    invalid = df[(df['Postnummer'] < 1000) | (df['Postnummer'] > 9999)]
    if len(invalid) > 0:
        logger.warning(f"Found {len(invalid)} postnumre outside valid range (1000-9999)")
        df = df[(df['Postnummer'] >= 1000) & (df['Postnummer'] <= 9999)]

    logger.info(f"Normalized {len(df)} postnumre")

    return df


def normalize_responstider(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and clean response time data.

    Args:
        df: DataFrame with Gennemsnit_minutter column

    Returns:
        DataFrame with validated response times
    """
    df = df.copy()

    # Convert to numeric if needed
    df['Gennemsnit_minutter'] = pd.to_numeric(df['Gennemsnit_minutter'], errors='coerce')

    # Remove rows with missing or invalid response times
    before = len(df)
    df = df.dropna(subset=['Gennemsnit_minutter'])
    after = len(df)

    if before != after:
        logger.warning(f"Removed {before - after} rows with invalid response times")

    # Check for negative values
    negative = df[df['Gennemsnit_minutter'] < 0]
    if len(negative) > 0:
        logger.warning(f"Found {len(negative)} negative response times - removing")
        df = df[df['Gennemsnit_minutter'] >= 0]

    # Check for extremely high values (>300 minutes = 5 hours)
    extreme = df[df['Gennemsnit_minutter'] > 300]
    if len(extreme) > 0:
        logger.warning(f"Found {len(extreme)} response times >300 minutes")
        # Keep them but log warning

    logger.info(f"Validated {len(df)} response times")

    return df


def normalize_data(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """Apply all normalization steps to raw data.

    Args:
        df: Raw DataFrame from loader
        config: Pipeline configuration

    Returns:
        Normalized and validated DataFrame
    """
    logger.info(f"Normalizing {len(df)} rows")

    # Step 1: Normalize column names
    df = normalize_column_names(df)

    # Step 2: Normalize postnumre
    postnummer_mapping = config.get('postnummer_mapping', {})
    df = normalize_postnumre(df, postnummer_mapping)

    # Step 3: Validate response times
    df = normalize_responstider(df)

    # Step 4: Ensure Antal_ture is integer
    df['Antal_ture'] = pd.to_numeric(df['Antal_ture'], errors='coerce').fillna(0).astype(int)

    logger.info(f"Normalization complete: {len(df)} rows remaining")

    return df
