#!/usr/bin/env python3
"""Run temporal analyses on ambulance data.

This script runs time-based analyses on raw ambulance data:
- Rush hour analysis (hour-by-hour patterns)
- Seasonal analysis (month-by-month patterns)
"""
import sys
import logging
from pathlib import Path
import yaml
from datetime import datetime

# Add processing modules to path
sys.path.insert(0, str(Path(__file__).parent / '2_processing'))

from analyzers.temporal_analysis import analyze_rush_hour, analyze_seasonal
from config import load_config


def setup_logging():
    """Configure logging for the script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('temporal_analysis.log'),
            logging.StreamHandler()
        ]
    )


def main():
    """Main execution function."""
    print("="*80)
    print("AMBULANCE TEMPORAL ANALYSIS")
    print("="*80)
    print()

    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)

    # Load configuration
    try:
        config = load_config('config.yaml')
        logger.info("✓ Configuration loaded")
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        sys.exit(1)

    # Define input file
    input_file = "1_input/Nordjylland20251027.xlsx"

    if not Path(input_file).exists():
        logger.error(f"Input file not found: {input_file}")
        sys.exit(1)

    logger.info(f"✓ Input file found: {input_file}")

    # Run Rush Hour Analysis
    print("\n" + "="*80)
    print("RUNNING: Rush Hour Analysis")
    print("="*80 + "\n")

    try:
        results = analyze_rush_hour(
            input_file=input_file,
            sheet_name="Nordjylland",
            region_name="Nordjylland",
            output_dir=config['output']['directory'],
            config=config
        )

        print("\n" + "="*80)
        print("RUSH HOUR ANALYSIS - SUCCESS")
        print("="*80)
        print(f"\nRegion: {results['region']}")
        print(f"Ture analyseret: {results['ture_analyseret']:,}")
        print(f"Periode: {results['periode']}")
        print(f"\nBedste time: kl. {results['statistics']['best_hour']:02d}:00 ({results['statistics']['best_median']:.1f} min)")
        print(f"Værste time: kl. {results['statistics']['worst_hour']:02d}:00 ({results['statistics']['worst_median']:.1f} min)")
        print(f"\nFiler genereret:")
        for file in results['files_generated']:
            print(f"  - {file}")

    except Exception as e:
        logger.error(f"Rush Hour analysis failed: {e}", exc_info=True)
        sys.exit(1)

    # Run Seasonal Analysis
    print("\n" + "="*80)
    print("RUNNING: Seasonal Analysis")
    print("="*80 + "\n")

    try:
        results_seasonal = analyze_seasonal(
            input_file=input_file,
            sheet_name="Nordjylland",
            region_name="Nordjylland",
            output_dir=config['output']['directory'],
            config=config
        )

        print("\n" + "="*80)
        print("SEASONAL ANALYSIS - SUCCESS")
        print("="*80)
        print(f"\nRegion: {results_seasonal['region']}")
        print(f"Ture analyseret: {results_seasonal['ture_analyseret']:,}")
        print(f"Periode: {results_seasonal['periode']}")

        # Get month names
        month_names = {
            1: 'Januar', 2: 'Februar', 3: 'Marts', 4: 'April',
            5: 'Maj', 6: 'Juni', 7: 'Juli', 8: 'August',
            9: 'September', 10: 'Oktober', 11: 'November', 12: 'December'
        }

        best_month_name = month_names[results_seasonal['statistics']['best_month']]
        worst_month_name = month_names[results_seasonal['statistics']['worst_month']]

        print(f"\nBedste måned: {best_month_name} ({results_seasonal['statistics']['best_median']:.1f} min)")
        print(f"Værste måned: {worst_month_name} ({results_seasonal['statistics']['worst_median']:.1f} min)")
        print(f"\nFiler genereret:")
        for file in results_seasonal['files_generated']:
            print(f"  - {file}")

    except Exception as e:
        logger.error(f"Seasonal analysis failed: {e}", exc_info=True)
        sys.exit(1)

    print("\n" + "="*80)
    print("ALL ANALYSES COMPLETED SUCCESSFULLY")
    print("="*80)


if __name__ == "__main__":
    main()
