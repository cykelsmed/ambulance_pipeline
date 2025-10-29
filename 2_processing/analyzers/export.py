"""Export utilities for saving analysis results."""
import pandas as pd
from pathlib import Path
import logging
from datetime import datetime
from typing import Dict, Any
import json

logger = logging.getLogger(__name__)


def save_to_excel(df: pd.DataFrame, output_path: Path, sheet_name: str = 'Data'):
    """Save DataFrame to Excel file.

    Args:
        df: DataFrame to save
        output_path: Path to output file
        sheet_name: Name of Excel sheet
    """
    df.to_excel(output_path, sheet_name=sheet_name, index=False, engine='openpyxl')
    logger.info(f"Saved {len(df)} rows to {output_path}")


def save_to_csv(df: pd.DataFrame, output_path: Path):
    """Save DataFrame to CSV file.

    Args:
        df: DataFrame to save
        output_path: Path to output file
    """
    df.to_csv(output_path, index=False, encoding='utf-8')
    logger.info(f"Saved {len(df)} rows to {output_path}")


def save_metadata(output_dir: Path, config: Dict[str, Any], stats: Dict[str, Any]):
    """Save pipeline run metadata.

    Args:
        output_dir: Output directory
        config: Pipeline configuration
        stats: Statistics about the run
    """
    metadata = {
        'timestamp': datetime.now().isoformat(),
        'version': config.get('version', '1.0'),
        'regions_processed': stats.get('regions', []),
        'total_postnumre': stats.get('total_postnumre', 0),
        'total_ture': stats.get('total_ture', 0),
        'analyses_generated': stats.get('analyses', [])
    }

    metadata_path = output_dir / 'pipeline_run_metadata.json'
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved metadata to {metadata_path}")


def export_all_analyses(analyses: Dict[str, pd.DataFrame], config: Dict[str, Any]) -> Dict[str, Path]:
    """Export all analyses to files.

    Args:
        analyses: Dictionary mapping analysis name to DataFrame
        config: Pipeline configuration

    Returns:
        Dictionary mapping analysis name to output file path
    """
    output_dir = Path(config['output']['directory'])
    output_dir.mkdir(parents=True, exist_ok=True)

    output_files = {}

    # File naming map
    file_names = {
        'alle_postnumre': '01_alle_postnumre.xlsx',
        'top_10_værste': '02_top_10_værste_VALIDERET.xlsx',
        'top_10_bedste': '03_top_10_bedste.xlsx',
        'regional_sammenligning': '04_regional_sammenligning.xlsx',
        'datawrapper_csv': 'DATAWRAPPER_alle_postnumre.csv'
    }

    for analysis_name, df in analyses.items():
        if df is None or len(df) == 0:
            logger.warning(f"Skipping empty analysis: {analysis_name}")
            continue

        file_name = file_names.get(analysis_name, f'{analysis_name}.xlsx')
        output_path = output_dir / file_name

        # Save as CSV if it's the datawrapper file
        if file_name.endswith('.csv'):
            save_to_csv(df, output_path)
        else:
            save_to_excel(df, output_path)

        output_files[analysis_name] = output_path

    logger.info(f"Exported {len(output_files)} analyses to {output_dir}")

    return output_files
