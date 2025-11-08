"""Central Data Cache - Load Regional Data Once

This module provides efficient data loading by reading all regional Excel files
once and caching them in memory for reuse across multiple analyses.

Performance: Reduces Excel I/O from ~30-40 reads to just 5 reads.
"""

import logging
import pandas as pd
import yaml
from pathlib import Path
from typing import Dict
from datetime import datetime

logger = logging.getLogger(__name__)


def load_all_regional_data_once() -> Dict[str, pd.DataFrame]:
    """Load all regional Excel data once and return as dictionary.
    
    This function reads each regional Excel file once and caches the raw
    DataFrames in memory. All subsequent analyses can reuse this cache
    instead of re-reading from disk.
    
    Returns:
        Dictionary mapping region name to raw DataFrame:
        {
            'Hovedstaden': pd.DataFrame,
            'Midtjylland': pd.DataFrame,
            'Nordjylland': pd.DataFrame,
            'Sjælland': pd.DataFrame,
            'Syddanmark': pd.DataFrame
        }
    
    Performance:
        - First call: ~10-20 seconds (reads 5 Excel files)
        - Memory usage: <1 GB for all 5 regions
        - Subsequent analyses: instant (in-memory cache)
    """
    start_time = datetime.now()
    logger.info("="*80)
    logger.info("LOADING ALL REGIONAL DATA (ONE-TIME CACHE)")
    logger.info("="*80)
    
    # Load regional configuration
    config_path = Path(__file__).parent / 'regional_config.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    regional_data_cache = {}
    total_rows = 0
    
    for region_name, region_config in config['regions'].items():
        try:
            logger.info(f"Loading {region_name}...")
            
            # Get file path
            file_path = Path(region_config['file'])
            
            # Handle Nordjylland filename update (if needed)
            if 'Nordjylland20251027' in str(file_path):
                file_path = Path(str(file_path).replace('20251027', '20251029'))
            
            if not file_path.exists():
                logger.warning(f"  File not found: {file_path}")
                continue
            
            sheet_name = region_config['sheet']
            
            # Load raw data
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # Store in cache with region name as key
            regional_data_cache[region_name] = df
            
            total_rows += len(df)
            memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
            
            logger.info(f"  ✓ {region_name}: {len(df):,} rows, {memory_mb:.1f} MB")
            
        except Exception as e:
            logger.error(f"  ✗ Failed to load {region_name}: {e}", exc_info=True)
            continue
    
    elapsed = (datetime.now() - start_time).total_seconds()
    total_memory_mb = sum(df.memory_usage(deep=True).sum() for df in regional_data_cache.values()) / 1024 / 1024
    
    logger.info("="*80)
    logger.info(f"CACHE LOADED: {len(regional_data_cache)} regions, {total_rows:,} total rows")
    logger.info(f"Memory usage: {total_memory_mb:.1f} MB")
    logger.info(f"Load time: {elapsed:.1f} seconds")
    logger.info("="*80)
    
    if len(regional_data_cache) == 0:
        raise ValueError("No regional data could be loaded - cache is empty")
    
    return regional_data_cache


def get_region_config() -> Dict:
    """Load and return regional configuration.
    
    Returns:
        Regional configuration dictionary from regional_config.yaml
    """
    config_path = Path(__file__).parent / 'regional_config.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

