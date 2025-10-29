#!/usr/bin/env python3
"""Ambulance Pipeline - TV2 Response Time Analysis

Dette script processerer ambulance-responstidsdata fra 5 danske regioner og
genererer TV2-klare analysefiler.

DATA KILDE:
Pipeline læser pre-aggregerede data fra "Postnummer"-ark i Excel-filerne.
Disse aggregeringer er verificeret 100% korrekte mod rå data (~2M rækker).
Se VERIFICATION.md for detaljer.

INPUT:
- 5 Excel-filer fra Nils (1_input/)
- Automatisk detektion baseret på filnavne
- Læser "Postnummer" eller "Postnumre" ark

OUTPUT:
- 5 TV2-klare analysefiler (3_output/current/)
- Metadata-fil med run-statistik
- Komplet log (pipeline.log)

PERFORMANCE:
- Processerer 861,757 ambulance-ture på ~6 sekunder
- Low memory footprint (kun aggregerede data)

Usage:
    python pipeline.py
"""
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add processing modules to path
sys.path.insert(0, str(Path(__file__).parent / '2_processing'))

from config import load_config
from loader import load_all_regions
from normalizer import normalize_data
from analyzers.core import (
    analyze_alle_postnumre,
    analyze_top_10_værste,
    analyze_top_10_bedste,
    analyze_regional_sammenligning,
    analyze_datawrapper_csv
)
from analyzers.export import export_all_analyses, save_metadata


def setup_logging(config):
    """Setup logging configuration."""
    log_level = config['logging']['level']
    log_file = config['logging']['file']
    console = config['logging']['console']

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)

    # Console handler
    handlers = [file_handler]
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        handlers.append(console_handler)

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level),
        handlers=handlers
    )

    return logging.getLogger(__name__)


def print_banner():
    """Print pipeline banner."""
    print("="*80)
    print("  AMBULANCE PIPELINE - TV2 Response Time Analysis")
    print("="*80)
    print()


def print_summary(analyses, stats):
    """Print summary of results."""
    print("\n" + "="*80)
    print("  PIPELINE SUMMARY")
    print("="*80)
    print(f"\nRegions processed: {', '.join(stats['regions'])}")
    print(f"Total postnumre: {stats['total_postnumre']}")
    print(f"Total ture: {stats['total_ture']:,}")
    print(f"\nAnalyses generated:")
    for name in analyses.keys():
        print(f"  ✓ {name}")
    print("\n" + "="*80)


def main():
    """Main pipeline execution."""
    start_time = datetime.now()

    print_banner()

    # Load configuration
    print("Loading configuration...")
    config = load_config()

    # Setup logging
    logger = setup_logging(config)
    logger.info("="*80)
    logger.info("AMBULANCE PIPELINE STARTED")
    logger.info("="*80)

    try:
        # Step 1: Load data
        print("\n[1/4] Loading regional data...")
        print("   → Auto-detecting Excel files from 1_input/")
        print("   → Reading 'Postnummer' ark (pre-aggregated by Nils)")
        df_raw = load_all_regions(config)
        logger.info(f"Loaded {len(df_raw)} rows from {df_raw['Region'].nunique()} regions")

        # Step 2: Normalize data
        print("[2/4] Normalizing data...")
        print("   → Standardizing column names")
        print("   → Coalescing multiple average/max columns")
        print("   → Validating postnumre (1000-9999)")
        df_clean = normalize_data(df_raw, config)
        logger.info(f"Normalized to {len(df_clean)} rows")

        # Step 3: Run analyses
        print("[3/4] Running analyses...")
        print("   → Generating 5 Tier 1 analyses")
        analyses = {}

        # Get enabled analyses from config
        enabled = config['output']['enabled_analyses']

        if 'alle_postnumre' in enabled:
            analyses['alle_postnumre'] = analyze_alle_postnumre(df_clean, config)

        if 'top_10_værste' in enabled:
            top_10_værste, validated_count = analyze_top_10_værste(df_clean, config)
            analyses['top_10_værste'] = top_10_værste
            logger.info(f"  → {validated_count} postnumre validated for Top 10")

        if 'top_10_bedste' in enabled:
            analyses['top_10_bedste'] = analyze_top_10_bedste(df_clean, config)

        if 'regional_sammenligning' in enabled:
            analyses['regional_sammenligning'] = analyze_regional_sammenligning(df_clean, config)

        if 'datawrapper_csv' in enabled:
            analyses['datawrapper_csv'] = analyze_datawrapper_csv(df_clean, config)

        logger.info(f"Generated {len(analyses)} analyses")

        # Step 4: Export results
        print("[4/4] Exporting results...")
        output_files = export_all_analyses(analyses, config)

        # Save metadata
        stats = {
            'regions': sorted(df_clean['Region'].unique().tolist()),
            'total_postnumre': len(df_clean),
            'total_ture': int(df_clean['Antal_ture'].sum()),
            'analyses': list(analyses.keys())
        }

        output_dir = Path(config['output']['directory'])
        save_metadata(output_dir, config, stats)

        # Print summary
        print_summary(analyses, stats)

        # Print output location
        print(f"\nOutput files saved to: {output_dir.absolute()}")
        print()

        # Execution time
        elapsed = datetime.now() - start_time
        logger.info(f"Pipeline completed in {elapsed.total_seconds():.1f} seconds")
        print(f"✓ Pipeline completed successfully in {elapsed.total_seconds():.1f} seconds")

        return 0

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        print(f"\n✗ ERROR: Pipeline failed - {e}")
        print(f"Check pipeline.log for details")
        return 1


if __name__ == '__main__':
    sys.exit(main())
