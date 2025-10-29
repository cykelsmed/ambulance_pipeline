"""Kommune Mapper - Maps postal codes to municipality names using DAWA API.

This module provides functionality to map Danish postal codes (postnumre) to
their corresponding municipality (kommune) and city names (bynavn) using the
Danmarks Adresser Web API (DAWA).

The module implements a hybrid caching approach:
1. First checks for existing CSV cache
2. If not found, queries DAWA API for all postal codes
3. Saves results to CSV for future use (fast lookup)
"""

import pandas as pd
import requests
from pathlib import Path
from typing import Dict, Optional
import logging
import time

logger = logging.getLogger(__name__)

# DAWA API endpoint
DAWA_BASE_URL = "https://api.dataforsyningen.dk"
CACHE_FILE = Path("data/postnr_kommune_mapping.csv")


def get_kommune_from_dawa(postnr: int) -> Optional[Dict[str, str]]:
    """Query DAWA API for postal code information.

    Args:
        postnr: Danish postal code (4 digits)

    Returns:
        Dictionary with keys: postnummer, bynavn, kommune
        Returns None if API call fails
    """
    try:
        url = f"{DAWA_BASE_URL}/postnumre/{postnr:04d}"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            data = response.json()
            return {
                'Postnummer': postnr,
                'Bynavn': data.get('navn', ''),
                'Kommune': data['kommuner'][0]['navn'] if data.get('kommuner') else ''
            }
        else:
            logger.warning(f"DAWA API returned {response.status_code} for postnr {postnr}")
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to query DAWA for postnr {postnr}: {e}")
        return None
    except (KeyError, IndexError) as e:
        logger.error(f"Unexpected DAWA response format for postnr {postnr}: {e}")
        return None


def create_kommune_mapping_csv(postnumre: list, output_file: Path = CACHE_FILE) -> pd.DataFrame:
    """Create CSV mapping file by querying DAWA for all postal codes.

    Args:
        postnumre: List of postal codes to map
        output_file: Path to save CSV cache

    Returns:
        DataFrame with columns: Postnummer, Bynavn, Kommune
    """
    output_file.parent.mkdir(parents=True, exist_ok=True)

    results = []
    total = len(postnumre)

    logger.info(f"Querying DAWA API for {total} postal codes...")

    for i, postnr in enumerate(postnumre, 1):
        if i % 50 == 0:
            logger.info(f"  Progress: {i}/{total} ({i/total*100:.1f}%)")

        result = get_kommune_from_dawa(postnr)
        if result:
            results.append(result)

        # Rate limiting: small delay between requests
        time.sleep(0.05)

    df = pd.DataFrame(results)

    # Save to CSV
    df.to_csv(output_file, index=False, encoding='utf-8')
    logger.info(f"✓ Saved {len(df)} postal code mappings to {output_file}")

    return df


def load_kommune_mapping(postnumre: Optional[list] = None, force_refresh: bool = False) -> pd.DataFrame:
    """Load kommune mapping from cache or create new via DAWA.

    Args:
        postnumre: Optional list of postal codes to ensure are in mapping
        force_refresh: If True, ignore cache and query DAWA

    Returns:
        DataFrame with columns: Postnummer, Bynavn, Kommune
    """
    # Check if cache exists and we're not forcing refresh
    if CACHE_FILE.exists() and not force_refresh:
        logger.info(f"Loading kommune mapping from cache: {CACHE_FILE}")
        df = pd.read_csv(CACHE_FILE, dtype={'Postnummer': int})

        # If specific postal codes requested, check if any are missing
        if postnumre:
            existing = set(df['Postnummer'])
            missing = [p for p in postnumre if p not in existing]

            if missing:
                logger.info(f"Found {len(missing)} new postal codes, updating cache...")
                new_data = create_kommune_mapping_csv(missing, CACHE_FILE)
                df = pd.concat([df, new_data], ignore_index=True)
                df = df.drop_duplicates(subset=['Postnummer'])
                df.to_csv(CACHE_FILE, index=False, encoding='utf-8')

        return df
    else:
        # No cache or force refresh - need postal codes to create mapping
        if not postnumre:
            raise ValueError("No cache found and no postal codes provided. Cannot create mapping.")

        logger.info("Creating new kommune mapping from DAWA...")
        return create_kommune_mapping_csv(postnumre, CACHE_FILE)


def add_kommune_to_dataframe(df: pd.DataFrame, postnummer_col: str = 'Postnummer') -> pd.DataFrame:
    """Add Bynavn and Kommune columns to a DataFrame with postal codes.

    Args:
        df: DataFrame containing a postal code column
        postnummer_col: Name of the postal code column

    Returns:
        DataFrame with added Bynavn and Kommune columns
    """
    # Get unique postal codes
    unique_postnr = df[postnummer_col].dropna().unique().tolist()

    # Load or create mapping
    mapping = load_kommune_mapping(postnumre=unique_postnr)

    # Merge with original DataFrame
    df_with_kommune = df.merge(
        mapping,
        left_on=postnummer_col,
        right_on='Postnummer',
        how='left'
    )

    return df_with_kommune


if __name__ == "__main__":
    # Standalone test
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Test with a few postal codes
    test_postnumre = [5935, 6560, 8210, 1000, 9000]

    print(f"\nTesting kommune mapper with {len(test_postnumre)} postal codes...")
    print(f"Postal codes: {test_postnumre}\n")

    mapping = load_kommune_mapping(postnumre=test_postnumre, force_refresh=True)

    print("\nResults:")
    print(mapping.to_string(index=False))
    print(f"\nCache saved to: {CACHE_FILE.absolute()}")
