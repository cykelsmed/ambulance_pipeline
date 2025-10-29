"""Data loader for ambulance Excel files."""
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


def find_header_row(file: Path, sheet_name: str) -> int:
    """Find the row containing 'Row Labels' as first column.

    Args:
        file: Path to Excel file
        sheet_name: Name of sheet to search

    Returns:
        Row index (0-based) containing header, or None if not found
    """
    df_raw = pd.read_excel(file, sheet_name=sheet_name, header=None, nrows=10)

    for idx, row in df_raw.iterrows():
        if str(row[0]).strip() == 'Row Labels':
            return idx

    logger.warning(f"Could not find 'Row Labels' header in {file} sheet {sheet_name}")
    return None


def detect_region_files(input_dir: Path, patterns: Dict[str, str]) -> Dict[str, Path]:
    """Auto-detect regional Excel files based on patterns.

    Args:
        input_dir: Directory containing Excel files
        patterns: Dictionary mapping region names to file patterns

    Returns:
        Dictionary mapping region name to file path
    """
    found_files = {}

    for region, pattern in patterns.items():
        matching_files = list(input_dir.glob(pattern))

        if matching_files:
            # Use most recent file if multiple matches
            latest_file = max(matching_files, key=lambda p: p.stat().st_mtime)
            found_files[region] = latest_file
            logger.info(f"Found {region}: {latest_file.name}")
        else:
            logger.warning(f"No file found for {region} with pattern {pattern}")

    return found_files


def find_postnummer_sheet(excel_file: pd.ExcelFile) -> str:
    """Find the postnummer/postnumre sheet in Excel file.

    Args:
        excel_file: ExcelFile object

    Returns:
        Sheet name containing postnummer data
    """
    preferred_names = ['Postnummer', 'Postnumre', 'postnummer', 'postnumre']

    # Try exact matches first
    for name in preferred_names:
        if name in excel_file.sheet_names:
            return name

    # Try case-insensitive substring match
    for sheet in excel_file.sheet_names:
        if 'postnummer' in sheet.lower() or 'postnumre' in sheet.lower():
            return sheet

    logger.warning(f"No postnummer sheet found. Available sheets: {excel_file.sheet_names}")
    return None


def load_region_data(file: Path, region: str) -> pd.DataFrame:
    """Load data from a single region Excel file.

    Args:
        file: Path to Excel file
        region: Region name (for logging)

    Returns:
        DataFrame with postnummer data
    """
    logger.info(f"Loading {region} from {file.name}")

    # Open Excel file
    xl = pd.ExcelFile(file)

    # Find postnummer sheet
    sheet_name = find_postnummer_sheet(xl)
    if sheet_name is None:
        raise ValueError(f"No postnummer sheet found in {file}")

    # Find header row
    header_row = find_header_row(file, sheet_name)
    if header_row is None:
        raise ValueError(f"Could not find header row in {file} sheet {sheet_name}")

    # Read data
    df = pd.read_excel(file, sheet_name=sheet_name, header=header_row)

    # Add region column
    df['Region'] = region.capitalize()

    logger.info(f"Loaded {len(df)} rows from {region}")

    return df


def load_all_regions(config: Dict) -> pd.DataFrame:
    """Load data from all regional Excel files.

    Args:
        config: Pipeline configuration dictionary

    Returns:
        Combined DataFrame with all regional data
    """
    input_dir = Path(config['input']['directory'])
    patterns = config['input']['patterns']

    # Detect files
    region_files = detect_region_files(input_dir, patterns)

    if len(region_files) == 0:
        raise ValueError(f"No regional files found in {input_dir}")

    logger.info(f"Found {len(region_files)} regional files")

    # Load each region
    dataframes = []
    for region, file in region_files.items():
        try:
            df = load_region_data(file, region)
            dataframes.append(df)
        except Exception as e:
            logger.error(f"Failed to load {region}: {e}")
            # Continue with other regions (graceful degradation)

    if len(dataframes) == 0:
        raise ValueError("Failed to load any regional data")

    # Combine all regions
    combined_df = pd.concat(dataframes, ignore_index=True)
    logger.info(f"Combined data: {len(combined_df)} rows from {len(dataframes)} regions")

    return combined_df
