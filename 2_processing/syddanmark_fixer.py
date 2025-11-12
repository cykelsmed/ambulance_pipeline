"""Data quality fixes for Region Syddanmark.

This module handles known data quality issues specific to Region Syddanmark:
- 41.7% of rows have empty/space characters in response time column
- Response time can be calculated from timestamps for 148,416 additional rows
- Improves data coverage from 58.3% to ~82.1%
"""
import pandas as pd
import logging
from pathlib import Path
from typing import Tuple

logger = logging.getLogger(__name__)


def calculate_response_time_from_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate missing response times from timestamps.
    
    For Syddanmark data, response times are only filled for A/B priorities.
    This function calculates response times for C/D priorities using timestamps.
    
    Args:
        df: DataFrame with Syddanmark raw data
        
    Returns:
        DataFrame with calculated response times filled in
    """
    df = df.copy()
    
    response_col = 'Responstid i minutter'
    timestamp_col = 'Hændelse oprettet i disponeringssystem'
    arrival_col = 'Ankomst første sundhedsprofessionelle enhed'
    
    # Convert response time to numeric (handles empty strings and spaces)
    df[response_col] = pd.to_numeric(df[response_col], errors='coerce')
    
    # Identify rows with missing response time but valid timestamps
    missing_mask = (
        df[response_col].isna() & 
        df[timestamp_col].notna() & 
        df[arrival_col].notna()
    )
    
    rows_to_calculate = missing_mask.sum()
    logger.info(f"Found {rows_to_calculate:,} rows with missing response time but valid timestamps")
    
    if rows_to_calculate == 0:
        return df
    
    # Convert timestamps to datetime
    df[timestamp_col] = pd.to_datetime(df[timestamp_col], errors='coerce')
    df[arrival_col] = pd.to_datetime(df[arrival_col], errors='coerce')
    
    # Calculate response time in minutes for missing rows
    calculated_response = (
        df[arrival_col] - df[timestamp_col]
    ).dt.total_seconds() / 60
    
    # Only fill where original was missing AND calculation is valid
    valid_calculation_mask = (
        missing_mask & 
        calculated_response.notna() &
        (calculated_response > 0) &
        (calculated_response < 300)  # Sanity check: < 5 hours
    )
    
    # Fill missing response times with calculated values
    df.loc[valid_calculation_mask, response_col] = calculated_response
    
    rows_filled = valid_calculation_mask.sum()
    logger.info(f"Successfully calculated and filled {rows_filled:,} response times")
    
    # Log priority distribution of filled rows
    if rows_filled > 0:
        priority_dist = df.loc[valid_calculation_mask, 'Hastegrad ved oprettelse'].value_counts()
        logger.info(f"Priority distribution of filled rows:\n{priority_dist}")
    
    return df


def load_syddanmark_with_fixes(file_path: str = None) -> Tuple[pd.DataFrame, dict]:
    """Load Syddanmark data with all fixes applied.
    
    Args:
        file_path: Path to Syddanmark Excel file (default: standard path)
        
    Returns:
        Tuple of (cleaned DataFrame, metadata dict)
    """
    if file_path is None:
        file_path = "1_input/Syddanmark20251025.xlsx"
    
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Syddanmark data file not found: {file_path}")
    
    logger.info(f"Loading Syddanmark data from {file_path}")
    df = pd.read_excel(file_path, sheet_name='Syddanmark')
    
    rows_original = len(df)
    logger.info(f"Loaded {rows_original:,} rows")
    
    # Count valid response times before fixes
    response_col = 'Responstid i minutter'
    df_temp = df.copy()
    df_temp[response_col] = pd.to_numeric(df_temp[response_col], errors='coerce')
    valid_before = df_temp[response_col].notna().sum()
    
    # Apply fixes
    df_fixed = calculate_response_time_from_timestamps(df)
    
    # Count valid response times after fixes
    valid_after = df_fixed[response_col].notna().sum()
    rows_added = valid_after - valid_before
    
    coverage_before = 100 * valid_before / rows_original
    coverage_after = 100 * valid_after / rows_original
    
    metadata = {
        'rows_original': rows_original,
        'valid_response_before': valid_before,
        'valid_response_after': valid_after,
        'rows_added': rows_added,
        'coverage_before_pct': coverage_before,
        'coverage_after_pct': coverage_after,
        'improvement_pct': coverage_after - coverage_before
    }
    
    logger.info(f"Data quality improvement:")
    logger.info(f"  Before: {valid_before:,} rows ({coverage_before:.1f}%)")
    logger.info(f"  After:  {valid_after:,} rows ({coverage_after:.1f}%)")
    logger.info(f"  Added:  {rows_added:,} rows (+{coverage_after - coverage_before:.1f}%)")
    
    return df_fixed, metadata


if __name__ == '__main__':
    # Test the fixes
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    df_fixed, metadata = load_syddanmark_with_fixes()
    
    print("\n" + "="*60)
    print("SYDDANMARK DATA QUALITY FIX RESULTS")
    print("="*60)
    print(f"Original rows:           {metadata['rows_original']:>10,}")
    print(f"Valid before fix:        {metadata['valid_response_before']:>10,} ({metadata['coverage_before_pct']:>5.1f}%)")
    print(f"Valid after fix:         {metadata['valid_response_after']:>10,} ({metadata['coverage_after_pct']:>5.1f}%)")
    print(f"Improvement:             {metadata['rows_added']:>10,} (+{metadata['improvement_pct']:>4.1f}%)")
    print("="*60)

