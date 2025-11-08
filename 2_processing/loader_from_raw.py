#!/usr/bin/env python3
"""
Raw Data Loader - Calculate Postal Code Aggregations Directly From Raw Data

This module replaces Nils' pre-aggregated "Postnummer" sheets with calculations
directly from raw A-priority data. This ensures 100% accuracy and consistency
with Phase 3 (yearly analysis).

Key differences from loader.py:
- Reads raw data sheets instead of "Postnummer" aggregations
- Filters to A-priority cases
- Groups by postal code and calculates statistics
- Returns same format as original loader
"""

import logging
import pandas as pd
import yaml
from pathlib import Path
from typing import Dict, Any
from postal_code_names import get_postal_code_name

logger = logging.getLogger(__name__)


def load_regional_config():
    """Load regional configuration."""
    config_path = Path(__file__).parent / 'regional_config.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_all_regions_from_raw(config: Dict[str, Any], regional_data_cache: Dict = None) -> pd.DataFrame:
    """Load postal code aggregations calculated from raw data.

    This replaces load_all_regions() from loader.py. Instead of reading
    pre-aggregated "Postnummer" sheets, it:
    1. Loads raw data from each region (or uses cache)
    2. Filters to A-priority cases
    3. Groups by postal code
    4. Calculates statistics (mean, max, count)

    Args:
        config: Pipeline configuration
        regional_data_cache: Pre-loaded regional data dictionary (optional)

    Returns:
        DataFrame with columns: Postnummer, Antal_ture, Region,
                               Gennemsnit_minutter, Max_minutter
    """
    logger.info("Loading postal code aggregations from raw data...")

    # Load regional configuration
    regional_config = load_regional_config()

    all_regions = []

    for region_name, region_config in regional_config['regions'].items():
        logger.info(f"Processing {region_name}...")

        try:
            # Use cached data if available
            if regional_data_cache and region_name in regional_data_cache:
                df = regional_data_cache[region_name].copy()
                logger.info(f"  Using cached data for {region_name}")
            else:
                # Fallback: Load raw data
                file_path = Path(region_config['file'])
                sheet_name = region_config['sheet']

                logger.info(f"  Loading raw data from {file_path.name}...")
                df = pd.read_excel(file_path, sheet_name=sheet_name)

            # Get column mappings
            cols = region_config['columns']
            priority_col = cols['priority']
            response_col = cols['response_time']

            # Find postal code column (handle variations: Postnummer, Post, Postdistrikt)
            # Priority order: "Post" (numeric) > "Postnummer" > "Postdistrikt" (text)
            postal_col = None

            # Check for exact match "Post" first (Nordjylland uses this)
            if 'Post' in df.columns:
                postal_col = 'Post'
            # Then check for Postnummer
            elif any('postnummer' in col.lower() for col in df.columns):
                postal_col = [col for col in df.columns if 'postnummer' in col.lower()][0]
            # Finally check for Postdistrikt (but only if nothing else found)
            elif any('postdistrikt' in col.lower() for col in df.columns):
                postal_col = [col for col in df.columns if 'postdistrikt' in col.lower()][0]

            if not postal_col:
                logger.warning(f"  No postal code column found in {region_name} - skipping")
                logger.warning(f"  Available columns: {list(df.columns)}")
                continue

            logger.info(f"  Using postal code column: {postal_col}")

            # Handle column name variations for response time
            if response_col not in df.columns:
                response_candidates = [col for col in df.columns
                                      if 'respons' in col.lower() and 'minut' in col.lower()]
                if response_candidates:
                    response_col = response_candidates[0]
                    logger.info(f"  Using alternative response column: {response_col}")
                else:
                    logger.error(f"  Could not find response time column in {region_name}")
                    continue

            # Filter to A-priority
            df_a = df[df[priority_col] == 'A'].copy()
            logger.info(f"  Filtered to {len(df_a):,} A-priority cases")

            # Convert response time to numeric
            df_a[response_col] = pd.to_numeric(df_a[response_col], errors='coerce')
            df_a = df_a[df_a[response_col].notna()]
            logger.info(f"  {len(df_a):,} cases with valid response times")

            # Convert postal code to numeric
            df_a[postal_col] = pd.to_numeric(df_a[postal_col], errors='coerce')
            df_a = df_a[df_a[postal_col].notna()]

            # Group by postal code and calculate statistics
            postal_stats = df_a.groupby(postal_col)[response_col].agg([
                ('Antal_ture', 'count'),
                ('Gennemsnit_minutter', 'mean'),
                ('Max_minutter', 'max')
            ]).reset_index()

            # Rename postal code column
            postal_stats = postal_stats.rename(columns={postal_col: 'Postnummer'})

            # Add region
            postal_stats['Region'] = region_name

            # Convert postal code to int
            postal_stats['Postnummer'] = postal_stats['Postnummer'].astype(int)

            # Add postal code names
            postal_stats['Postnummer_Navn'] = postal_stats['Postnummer'].apply(get_postal_code_name)

            logger.info(f"  ✓ Calculated statistics for {len(postal_stats)} postal codes")

            all_regions.append(postal_stats)

        except Exception as e:
            logger.error(f"  ✗ Failed to process {region_name}: {e}", exc_info=True)
            continue

    if not all_regions:
        raise ValueError("No regional data could be loaded from raw data")

    # Combine all regions
    combined = pd.concat(all_regions, ignore_index=True)

    logger.info(f"✓ Loaded {len(combined)} postal codes from {len(all_regions)} regions (raw data)")
    logger.info(f"  Total A-priority cases: {combined['Antal_ture'].sum():,}")

    return combined


if __name__ == '__main__':
    """Test the raw data loader."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))

    from config import load_config

    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

    print("Testing raw data loader...")
    print()

    config = load_config()
    df = load_all_regions_from_raw(config)

    print()
    print(f"Loaded {len(df)} postal codes")
    print(f"Total trips: {df['Antal_ture'].sum():,}")
    print()

    print("Regional breakdown:")
    regional_summary = df.groupby('Region').agg({
        'Postnummer': 'count',
        'Antal_ture': 'sum',
        'Gennemsnit_minutter': lambda x: (x * df.loc[x.index, 'Antal_ture']).sum() / df.loc[x.index, 'Antal_ture'].sum()
    })
    regional_summary.columns = ['Postnumre', 'Total_ture', 'Weighted_avg']
    print(regional_summary)
