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
from analyzers.summary_generator import generate_consolidated_summary, generate_master_findings_report
from analyzers.priority_analysis import (
    analyze_abc_priority,
    calculate_priority_differences,
    analyze_rekvireringskanal,
    analyze_hastegrad_changes,
    export_priority_analyses
)


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


def run_priority_analyses(config, logger):
    """Run priority and system analyses (ABC, changes, channels).

    Args:
        config: Configuration dictionary
        logger: Logger instance

    Returns:
        bool: True if analyses succeeded
    """
    import yaml
    import pandas as pd

    # Load regional configuration
    regional_config_path = Path(__file__).parent / '2_processing' / 'regional_config.yaml'
    try:
        with open(regional_config_path, 'r', encoding='utf-8') as f:
            regional_config = yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load regional config: {e}")
        return False

    output_dir = Path(config['output']['directory'])

    # Load all regional data
    logger.info("Loading raw data for priority analyses...")
    all_dfs = []

    for region_name, region_config in regional_config['regions'].items():
        try:
            file_path = Path(region_config['file'])
            sheet_name = region_config['sheet']
            df = pd.read_excel(file_path, sheet_name=sheet_name)

            # Get column mappings
            cols = region_config['columns']

            # Standardize column names
            rename_map = {
                cols.get('priority', 'Hastegrad ved oprettelse'): 'Hastegrad ved oprettelse',
                cols['response_time']: 'ResponstidMinutter',
                cols.get('channel', 'Rekvireringskanal'): 'Rekvireringskanal'
            }

            df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
            df['Region'] = region_name

            # Convert response time to numeric
            if 'ResponstidMinutter' in df.columns:
                df['ResponstidMinutter'] = pd.to_numeric(df['ResponstidMinutter'], errors='coerce')

            all_dfs.append(df)
            logger.info(f"  Loaded {len(df):,} rows from {region_name}")

        except Exception as e:
            logger.error(f"Failed to load {region_name}: {e}")

    if not all_dfs:
        logger.error("No data loaded for priority analyses")
        return False

    # Combine all data
    combined_df = pd.concat(all_dfs, ignore_index=True)
    logger.info(f"Combined data: {len(combined_df):,} total rows")

    try:
        # Analysis 1: ABC Priority
        logger.info("Running A/B/C priority analysis...")
        abc_stats = analyze_abc_priority(combined_df)
        abc_diffs = calculate_priority_differences(abc_stats)

        # Analysis 2: Rekvireringskanal
        logger.info("Running rekvireringskanal analysis...")
        kanal_stats = analyze_rekvireringskanal(combined_df)

        # Analysis 3: Hastegrad changes (if columns exist)
        logger.info("Checking for hastegrad change data...")
        hastegrad_changes = analyze_hastegrad_changes(combined_df)

        # Export all results
        logger.info("Exporting priority analysis results...")
        files = export_priority_analyses(
            abc_stats, abc_diffs, kanal_stats, hastegrad_changes, output_dir
        )

        logger.info(f"✓ Priority analyses completed - {len(files)} files generated")
        return True

    except Exception as e:
        logger.error(f"Priority analyses failed: {e}", exc_info=True)
        return False


def run_temporal_analyses(config, logger):
    """Run temporal analyses (time-of-day and seasonal) for all regions.

    Args:
        config: Configuration dictionary
        logger: Logger instance

    Returns:
        bool: True if all analyses succeeded, False if any failed
    """
    import yaml
    import pandas as pd
    from analyzers.temporal_analysis import (
        calculate_hourly_stats,
        calculate_monthly_stats
    )

    # Load regional configuration
    regional_config_path = Path(__file__).parent / '2_processing' / 'regional_config.yaml'
    try:
        with open(regional_config_path, 'r', encoding='utf-8') as f:
            regional_config = yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load regional config: {e}")
        return False

    output_dir = Path(config['output']['directory'])
    regions_config = regional_config['regions']
    success_count = 0
    total_regions = len(regions_config)

    for region_name, region_config in regions_config.items():
        try:
            logger.info(f"Processing temporal analysis for {region_name}...")

            # Load raw data
            file_path = Path(region_config['file'])
            sheet_name = region_config['sheet']
            df = pd.read_excel(file_path, sheet_name=sheet_name)

            # Get column mappings
            cols = region_config['columns']
            timestamp_col = cols['timestamp']
            response_col = cols['response_time']
            priority_col = cols['priority']
            month_col = cols['month']

            # Handle Danish month names if needed
            if region_config.get('month_type') == 'danish':
                df = convert_danish_months(df, month_col, regional_config['danish_months'])

            # Filter for A+B priority cases
            df_filtered = df[df[priority_col].isin(['A', 'B'])].copy()

            # Convert response time to numeric
            df_filtered[response_col] = pd.to_numeric(df_filtered[response_col], errors='coerce')
            df_filtered = df_filtered[df_filtered[response_col].notna()].copy()

            # Extract hour from timestamp
            df_filtered['Hour'] = extract_hour_from_timestamp(df_filtered[timestamp_col])
            df_filtered = df_filtered[df_filtered['Hour'].notna()].copy()

            # Rename columns for analysis functions
            df_filtered = df_filtered.rename(columns={
                response_col: 'ResponstidMinutter',
                month_col: 'Måned' if region_config['month_type'] != 'danish' else month_col
            })

            if 'Maaned' in df_filtered.columns:
                df_filtered = df_filtered.rename(columns={'Maaned': 'Måned'})

            # Run time-of-day analysis
            hourly_stats = calculate_hourly_stats(df_filtered)
            hourly_stats = add_categorization(hourly_stats, 'Median_minutter')
            hourly_stats = add_time_periods(hourly_stats)

            # Export time-of-day results
            prefix = f"{region_name}_"
            export_temporal_results(
                hourly_stats, df_filtered, region_name, output_dir, prefix, 'time'
            )

            # Run seasonal analysis
            monthly_stats = calculate_monthly_stats(df_filtered, month_col='Måned')
            monthly_stats = add_categorization(monthly_stats, 'Median_minutter')

            # Export seasonal results
            export_temporal_results(
                monthly_stats, df_filtered, region_name, output_dir, prefix, 'seasonal'
            )

            success_count += 1
            logger.info(f"✓ {region_name} temporal analyses completed")

        except Exception as e:
            logger.error(f"✗ {region_name} temporal analysis failed: {e}", exc_info=True)

    # Generate consolidated summary if all succeeded
    if success_count == total_regions:
        try:
            logger.info("Generating consolidated temporal summary...")
            summary_path = generate_consolidated_summary(output_dir)
            logger.info(f"✓ Consolidated summary: {summary_path.name}")
        except Exception as e:
            logger.error(f"Failed to generate consolidated summary: {e}")
            return False

    return success_count == total_regions


def convert_danish_months(df, month_col, danish_months_map):
    """Convert Danish month names to numeric."""
    df = df.copy()
    df[month_col] = df[month_col].map(danish_months_map)
    return df


def extract_hour_from_timestamp(timestamp_series):
    """Extract hour from various timestamp formats."""
    import pandas as pd
    if pd.api.types.is_datetime64_any_dtype(timestamp_series):
        return timestamp_series.dt.hour
    elif timestamp_series.dtype == 'object':
        sample = timestamp_series.dropna().iloc[0] if len(timestamp_series.dropna()) > 0 else None
        if sample is not None and hasattr(sample, 'hour') and not hasattr(sample, 'date'):
            return timestamp_series.apply(lambda x: x.hour if pd.notna(x) and hasattr(x, 'hour') else None)
        else:
            return pd.to_datetime(timestamp_series, errors='coerce').dt.hour
    else:
        return pd.to_datetime(timestamp_series, errors='coerce').dt.hour


def add_categorization(stats, col_name='Median_minutter'):
    """Add color categories to statistics."""
    stats = stats.copy()
    def categorize(val):
        if val < 10:
            return 'Grøn'
        elif val <= 15:
            return 'Gul'
        else:
            return 'Rød'
    stats['Kategori'] = stats[col_name].apply(categorize)
    return stats


def add_time_periods(hourly_stats):
    """Add time period labels to hourly stats."""
    def get_period(hour):
        if 2 <= hour <= 5:
            return 'Nat'
        elif 6 <= hour <= 8:
            return 'Morgen'
        elif 9 <= hour <= 11:
            return 'Formiddag'
        elif hour == 12:
            return 'Middag'
        elif 13 <= hour <= 17:
            return 'Eftermiddag'
        elif 18 <= hour <= 23:
            return 'Aften'
        else:
            return 'Nat'

    hourly_stats = hourly_stats.copy()
    hourly_stats['Periode'] = hourly_stats['Time'].apply(get_period)
    hourly_stats['Time_label'] = hourly_stats['Time'].apply(
        lambda h: f"{int(h):02d}:00-{(int(h)+1)%24:02d}:00"
    )
    return hourly_stats


def export_temporal_results(stats, df_filtered, region_name, output_dir, prefix, analysis_type):
    """Export temporal analysis results to files."""
    if analysis_type == 'time':
        # Time-of-day exports
        excel_file = output_dir / f"{prefix}05_responstid_per_time.xlsx"
        stats.to_excel(excel_file, index=False, engine='openpyxl')

        fund_file = output_dir / f"{prefix}05_responstid_per_time_FUND.txt"
        with open(fund_file, 'w', encoding='utf-8') as f:
            f.write(f"TIDSMÆSSIGE ANALYSER - TID-PÅ-DØGNET\n")
            f.write(f"Region: {region_name}\n")
            f.write(f"A+B-kørsler analyseret: {len(df_filtered):,}\n\n")

            best_hour = stats.loc[stats['Median_minutter'].idxmin()]
            worst_hour = stats.loc[stats['Median_minutter'].idxmax()]

            f.write(f"Bedste time: kl. {int(best_hour['Time']):02d}:00 ({best_hour['Median_minutter']:.1f} min)\n")
            f.write(f"Værste time: kl. {int(worst_hour['Time']):02d}:00 ({worst_hour['Median_minutter']:.1f} min)\n")
            f.write(f"Variation: {100*(worst_hour['Median_minutter']-best_hour['Median_minutter'])/best_hour['Median_minutter']:.1f}%\n")

        dw_file = output_dir / f"{prefix}DATAWRAPPER_responstid_per_time.csv"
        dw_data = stats[['Time_label', 'Median_minutter', 'Antal_ture', 'Kategori', 'Periode']].copy()
        dw_data.to_csv(dw_file, index=False)

    else:  # seasonal
        # Seasonal exports
        excel_file = output_dir / f"{prefix}06_responstid_per_maaned.xlsx"
        stats.to_excel(excel_file, index=False, engine='openpyxl')

        fund_file = output_dir / f"{prefix}06_responstid_per_maaned_FUND.txt"
        with open(fund_file, 'w', encoding='utf-8') as f:
            f.write(f"TIDSMÆSSIGE ANALYSER - SÆSONVARIATION\n")
            f.write(f"Region: {region_name}\n")
            f.write(f"A+B-kørsler analyseret: {len(df_filtered):,}\n\n")

            best_month = stats.loc[stats['Median_minutter'].idxmin()]
            worst_month = stats.loc[stats['Median_minutter'].idxmax()]

            f.write(f"Bedste måned: {best_month['Maaned_navn']} ({best_month['Median_minutter']:.1f} min)\n")
            f.write(f"Værste måned: {worst_month['Maaned_navn']} ({worst_month['Median_minutter']:.1f} min)\n")
            f.write(f"Variation: {100*(worst_month['Median_minutter']-best_month['Median_minutter'])/best_month['Median_minutter']:.1f}%\n")

        dw_file = output_dir / f"{prefix}DATAWRAPPER_responstid_per_maaned.csv"
        dw_data = stats[['Maaned_navn', 'Median_minutter', 'Antal_ture', 'Kategori', 'Sæson']].copy()
        dw_data.to_csv(dw_file, index=False)


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
        print("\n[1/7] Loading regional data...")
        print("   → Auto-detecting Excel files from 1_input/")
        print("   → Reading 'Postnummer' ark (pre-aggregated by Nils)")
        df_raw = load_all_regions(config)
        logger.info(f"Loaded {len(df_raw)} rows from {df_raw['Region'].nunique()} regions")

        # Step 2: Normalize data
        print("[2/7] Normalizing data...")
        print("   → Standardizing column names")
        print("   → Coalescing multiple average/max columns")
        print("   → Validating postnumre (1000-9999)")
        df_clean = normalize_data(df_raw, config)
        logger.info(f"Normalized to {len(df_clean)} rows")

        # Step 3: Run analyses
        print("[3/7] Running postnummer analyses...")
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
        print("[4/7] Exporting postnummer results...")
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

        # Step 5: Run temporal analyses (time-of-day and seasonal)
        print("\n[5/7] Running temporal analyses...")
        print("   → Analyzing time-of-day patterns (rush hour)")
        print("   → Analyzing seasonal patterns (winter crisis)")
        print("   → Processing all 5 regions with A+B priority cases")

        temporal_success = run_temporal_analyses(config, logger)

        if temporal_success:
            print("   ✓ Temporal analyses completed")
            stats['analyses'].extend(['temporal_rush_hour', 'temporal_seasonal'])
        else:
            print("   ⚠ Temporal analyses had errors (check log)")
            logger.warning("Temporal analyses completed with errors")

        # Step 6: Run priority/system analyses
        print("\n[6/7] Running system analyses...")
        print("   → A vs B vs C prioritering")
        print("   → Hastegradomlægning (hvis data findes)")
        print("   → Rekvireringskanal-analyse")

        priority_success = run_priority_analyses(config, logger)

        if priority_success:
            print("   ✓ System analyses completed")
            stats['analyses'].extend(['abc_priority', 'rekvireringskanal'])
        else:
            print("   ⚠ System analyses had errors (check log)")
            logger.warning("System analyses completed with errors")

        # Step 7: Generate master findings report
        if temporal_success and priority_success:
            print("\n[7/7] Generating master findings report...")
            print("   → Combining all analyses (postnummer + temporal + system)")
            try:
                master_report = generate_master_findings_report(output_dir)
                print("   ✓ Master report generated")
                stats['analyses'].append('master_findings_report')
                logger.info(f"Generated master findings report: {master_report.name}")
            except Exception as e:
                print(f"   ⚠ Master report generation failed: {e}")
                logger.error(f"Failed to generate master report: {e}", exc_info=True)

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
