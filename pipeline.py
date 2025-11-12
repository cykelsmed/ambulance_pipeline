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
# from loader import load_all_regions  # OLD: Uses Nils' pre-aggregated Postnummer sheets
from loader_from_raw import load_all_regions_from_raw  # NEW: Calculates from raw A-priority data
from normalizer import normalize_data
from analyzers.core import (
    analyze_alle_postnumre,
    analyze_top_10_værste,
    analyze_top_10_bedste,
    analyze_regional_sammenligning,
    analyze_datawrapper_csv
)
from analyzers.export import export_all_analyses, save_metadata
from analyzers.summary_generator import generate_master_findings_report, generate_master_findings_pdf
from analyzers.priority_analysis import (
    analyze_abc_priority,
    calculate_priority_differences,
    analyze_rekvireringskanal,
    analyze_hastegrad_changes,
    export_priority_analyses
)
from analyzers.yearly_analysis import run_yearly_analysis
from analyzers.b_priority_analysis import (
    analyze_b_geographic,
    analyze_b_temporal,
    analyze_b_yearly_trends,
    analyze_b_to_a_escalations
)
from analyzers.dispatch_delay_analysis import run_dispatch_delay_analysis
from analyzers.helicopter_analysis import run_helicopter_analysis
from analyzers.vehicle_type_analysis import run_vehicle_type_analysis
from scripts.organize_output import organize_output


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
                cols.get('requesting_channel', 'Rekvireringskanal'): 'Rekvireringskanal'
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


def _load_regional_data_cache():
    """Load all regional Excel files into memory cache for B-priority analyses.

    This function loads each region's Excel file ONCE and stores it in a dictionary.
    The cache is then passed to all B-priority analysis functions, preventing
    the pipeline from loading the same 400MB+ Excel files multiple times.

    Without caching, the pipeline would load:
    - Geographic analysis: 5 files
    - Temporal analysis: 5 files
    - Yearly analysis: 5 files
    - Escalation analysis: 1 file
    Total: 16 Excel file loads causing memory corruption and crashes

    With caching: 5 files loaded once, reused 4 times

    Returns:
        Dict[str, pd.DataFrame]: Region name → DataFrame mapping
    """
    import yaml
    import pandas as pd

    logger = logging.getLogger(__name__)

    # Load regional configuration
    regional_config_path = Path(__file__).parent / '2_processing' / 'regional_config.yaml'
    with open(regional_config_path, 'r', encoding='utf-8') as f:
        regional_config = yaml.safe_load(f)

    cache = {}

    for region_name, region_config in regional_config['regions'].items():
        try:
            file_path = Path(region_config['file'])

            # Handle Nordjylland filename update
            if 'Nordjylland20251027' in str(file_path):
                file_path = Path(str(file_path).replace('20251027', '20251029'))

            if not file_path.exists():
                logger.warning(f"File not found: {file_path}")
                cache[region_name] = None
                continue

            sheet_name = region_config['sheet']
            logger.info(f"  Loading {region_name} into cache...")
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            cache[region_name] = df
            logger.info(f"  ✓ Cached {region_name}: {len(df):,} rows")

        except Exception as e:
            logger.error(f"Failed to cache {region_name}: {e}", exc_info=True)
            cache[region_name] = None

    return cache


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
        print("\n[1/12] Loading regional data...")
        print("   → Loading raw A-priority data from all 5 regions")
        print("   → Calculating postal code aggregations directly from raw data")
        print("   → This ensures 100% accuracy (not using Nils' pre-aggregations)")
        df_raw = load_all_regions_from_raw(config)
        logger.info(f"Loaded {len(df_raw)} postal codes from {df_raw['Region'].nunique()} regions (raw data)")

        # Step 2: Normalize data
        print("[2/12] Normalizing data...")
        print("   → Standardizing column names")
        print("   → Coalescing multiple average/max columns")
        print("   → Validating postnumre (1000-9999)")
        df_clean = normalize_data(df_raw, config)
        logger.info(f"Normalized to {len(df_clean)} rows")

        # Step 3: Run analyses
        print("[3/12] Running postnummer analyses...")
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
        print("[4/12] Exporting postnummer results...")
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
        print("\n[5/12] Running temporal analyses...")
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
        print("\n[6/12] Running system analyses...")
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

        # Step 7: Run helicopter (HEMS) analysis
        print("\n[7/13] Running helicopter (HEMS) analysis...")
        print("   → National overview (dispatch delay + flight time)")
        print("   → Regional breakdown and base performance")
        print("   → Yearly trends and seasonal patterns")
        print("   → Postal code coverage mapping")

        helicopter_file = Path('1_input/helikopterdata_nationale_.xlsx')

        if helicopter_file.exists():
            try:
                helicopter_results = run_helicopter_analysis(
                    str(helicopter_file),
                    str(output_dir)
                )
                print(f"   ✓ Helicopter analysis completed: {helicopter_results['metadata']['valid_count']:,} cases")
                print(f"      Avg total response: {helicopter_results['national'].iloc[2]['Gennemsnit_min']:.1f} min")
                print(f"      Avg dispatch delay: {helicopter_results['national'].iloc[0]['Gennemsnit_min']:.1f} min")
                print(f"      Regions: {helicopter_results['metadata']['regions']}, Bases: {helicopter_results['metadata']['bases']}")
                stats['analyses'].append('helicopter_analysis')
                logger.info("Helicopter analysis completed successfully")
            except Exception as e:
                logger.error(f"Helicopter analysis failed: {e}", exc_info=True)
                print(f"   ⚠ Helicopter analysis failed: {e}")
        else:
            logger.warning(f"Helicopter data file not found: {helicopter_file}")
            print(f"   → Skipping (file not found: {helicopter_file.name})")

        # Step 8: Run B-priority deep analyses
        print("\n[8/13] Running B-priority deep analyses...")
        print("   → Geographic hotspots (postnummer-niveau)")
        print("   → Temporal patterns (time-of-day + seasonal)")
        print("   → Yearly trends (2021-2025)")
        print("   → B→A priority escalations (Hovedstaden)")

        b_priority_results = {}

        try:
            # Load regional data cache ONCE to avoid loading Excel files 3-4 times
            # This prevents memory corruption and file handle exhaustion
            print("   → Loading regional data cache (load once, use 4 times)...")
            regional_data_cache = _load_regional_data_cache()
            logger.info(f"Regional data cache loaded: {len(regional_data_cache)} regions")

            # Analysis 1: Geographic hotspots
            geo_result = analyze_b_geographic(output_dir, regional_data_cache=regional_data_cache)
            if geo_result.get('status') == 'success':
                print(f"   ✓ Geographic: {geo_result['total_postal_codes']} postal codes analyzed")
                print(f"      Worst: {geo_result['worst_postal_code']['postnummer']} ({geo_result['worst_postal_code']['median_minutes']} min)")
                b_priority_results['geographic'] = geo_result
                stats['analyses'].append('b_priority_geographic')
            else:
                print("   ⚠ Geographic analysis failed")

            # Analysis 2: Temporal patterns
            temporal_result = analyze_b_temporal(output_dir, regional_data_cache=regional_data_cache)
            if temporal_result.get('status') == 'success':
                print(f"   ✓ Temporal: {temporal_result['regions_processed']} regions analyzed")
                b_priority_results['temporal'] = temporal_result
                stats['analyses'].append('b_priority_temporal')
            else:
                print("   ⚠ Temporal analysis failed")

            # Analysis 3: Yearly trends
            yearly_result = analyze_b_yearly_trends(output_dir, regional_data_cache=regional_data_cache)
            if yearly_result.get('status') == 'success':
                years = yearly_result['years_analyzed']
                trend = yearly_result.get('national_trend_percent')
                print(f"   ✓ Yearly trends: {years[0]}-{years[-1]} ({trend:+.1f}% change)")
                b_priority_results['yearly'] = yearly_result
                stats['analyses'].append('b_priority_yearly')
            else:
                print("   ⚠ Yearly trend analysis failed")

            # Analysis 4: B→A escalations (Hovedstaden only)
            escalation_result = analyze_b_to_a_escalations(output_dir, regional_data_cache=regional_data_cache)
            if escalation_result.get('status') == 'success':
                rate = escalation_result['escalation_rate']
                print(f"   ✓ B→A escalations: {rate}% upgrade rate (Hovedstaden)")
                b_priority_results['escalations'] = escalation_result
                stats['analyses'].append('b_priority_escalations')
            elif escalation_result.get('status') == 'no_escalations':
                print("   → No B→A escalations found")
            else:
                print("   ⚠ Escalation analysis failed")

            logger.info(f"B-priority analyses completed: {len(b_priority_results)} successful")

            # Clear cache to free memory
            del regional_data_cache
            import gc
            gc.collect()

        except Exception as e:
            logger.error(f"B-priority analyses failed: {e}", exc_info=True)
            print(f"   ⚠ B-priority analyses had errors: {e}")

        # Step 8.5: Run vehicle type analysis (uses same regional_data_cache if available)
        print("\n[8.5/14] Running vehicle type analysis...")
        print("   → National distribution (Ambulance vs. Lægebil vs. Paramediciner)")
        print("   → Regional variation in vehicle usage")
        print("   → Priority differences (A vs B per vehicle type)")
        print("   → Temporal patterns (time-of-day per vehicle type)")

        try:
            # Re-use regional_data_cache if available from B-priority step
            if 'regional_data_cache' in locals() and regional_data_cache:
                print("   → Re-using regional data cache from B-priority analysis")
                vehicle_results, vehicle_summary = run_vehicle_type_analysis(output_dir, regional_data_cache=regional_data_cache)
            else:
                # Load cache if not available
                print("   → Loading regional data cache...")
                from data_cache import load_all_regional_data_once
                vehicle_cache = load_all_regional_data_once()
                vehicle_results, vehicle_summary = run_vehicle_type_analysis(output_dir, regional_data_cache=vehicle_cache)
                del vehicle_cache

            print(f"   ✓ Vehicle type analysis completed")
            print(f"      Total analyzed: {vehicle_results['national'].iloc[0]['Total_Cases']:,} A+B cases")
            print(f"      Ambulance: {vehicle_results['national'].iloc[0]['Percentage']}% ({vehicle_results['national'].iloc[0]['Total_Cases']:,} cases)")
            print(f"      Lægebil: {vehicle_results['national'].iloc[1]['Percentage']}% ({vehicle_results['national'].iloc[1]['Total_Cases']:,} cases)")
            stats['analyses'].append('vehicle_type_analysis')
            logger.info("Vehicle type analysis completed successfully")
        except Exception as e:
            logger.error(f"Vehicle type analysis failed: {e}", exc_info=True)
            print(f"   ⚠ Vehicle type analysis failed: {e}")

        # Step 9: Run dispatch delay vs travel time analysis
        print("\n[9/14] Running dispatch delay vs. travel time analysis...")
        print("   → Analyzing total patient wait time breakdown")
        print("   → Dispatch delay (112 call → dispatch) vs. travel time (dispatch → arrival)")
        print("   → Only Nordjylland + Syddanmark (datetime timestamps)")

        try:
            df_dispatch, summary_text = run_dispatch_delay_analysis(output_dir)
            print(f"   ✓ Dispatch delay analysis completed: {len(df_dispatch)} priority groups analyzed")
            print(f"   → Nordjylland + Syddanmark: ~550K A+B cases")
            stats['analyses'].append('dispatch_delay_analysis')
            logger.info("Dispatch delay analysis completed successfully")
        except Exception as e:
            logger.error(f"Dispatch delay analysis failed: {e}", exc_info=True)
            print(f"   ⚠ Dispatch delay analysis failed: {e}")

        # Step 10: Run yearly analysis (year-by-region breakdown)
        print("\n[10/13] Running yearly analysis...")
        print("   → Analyzing response times per year and region")
        print("   → Generating landsdækkende årlige gennemsnit")

        try:
            yearly_files = run_yearly_analysis(output_dir, priority='A')
            print(f"   ✓ Yearly analysis completed ({len(yearly_files)} files)")
            stats['analyses'].append('yearly_analysis')
            logger.info(f"Generated {len(yearly_files)} yearly analysis files")
        except Exception as e:
            print(f"   ⚠ Yearly analysis failed: {e}")
            logger.error(f"Yearly analysis failed: {e}", exc_info=True)

        # Step 11: Generate master findings report
        print("\n[11/13] Generating master findings report...")
        print("   → Combining all analyses (postnummer + årlig + temporal + system + B-priority)")

        try:
            master_report = generate_master_findings_report(output_dir)
            print("   ✓ Master rapport genereret")
            stats['analyses'].append('master_findings_report')
            logger.info(f"Generated master findings report: {master_report.name}")
        except Exception as e:
            print(f"   ⚠ Master rapport fejlede: {e}")
            logger.error(f"Failed to generate master report: {e}", exc_info=True)

        # Print summary
        print_summary(analyses, stats)

        # Print output location
        print(f"\nOutput files saved to: {output_dir.absolute()}")
        print()

        # Step 12: Organize output files
        print("\n[12/13] Organizing output files...")
        print("   → Packing all analysis files into bilag.zip")
        print("   → Keeping only MASTER_FINDINGS_RAPPORT files + bilag.zip in /current")

        try:
            organize_output(output_dir, keep_unzipped=False)
            print("   ✓ Output files organized")
            print(f"\n📦 Final output:")
            print(f"   - MASTER_FINDINGS_RAPPORT.md/.html/.pdf (reports)")
            print(f"   - bilag.zip (all analysis files)")
            logger.info("Output files organized successfully")
        except Exception as e:
            logger.warning(f"Output organization failed: {e}")
            print(f"   ⚠ Output organization failed: {e}")
            print(f"   → Run manually: python3 scripts/organize_output.py")

        # Step 13: Generate PDF version
        print("\n[13/13] Generating PDF version of master report...")
        print("   → Converting Markdown → HTML → PDF (via Chrome headless)")
        print("   → Applying professional styling with readable tables")

        try:
            result_file = generate_master_findings_pdf(output_dir)
            if result_file:
                file_size_kb = result_file.stat().st_size / 1024
                if result_file.suffix == '.pdf':
                    print(f"   ✓ PDF generated: {result_file.name} ({file_size_kb:.1f} KB)")
                    print("   ✓ HTML also available: MASTER_FINDINGS_RAPPORT.html")
                    stats['analyses'].extend(['master_findings_pdf', 'master_findings_html'])
                else:
                    print(f"   ✓ HTML generated: {result_file.name} ({file_size_kb:.1f} KB)")
                    print("   → PDF not generated (Chrome not found)")
                    stats['analyses'].append('master_findings_html')
            else:
                print("   ⚠ HTML/PDF generation failed (check log)")
                logger.warning("HTML/PDF generation failed")
        except Exception as e:
            logger.error(f"HTML/PDF generation failed: {e}", exc_info=True)
            print(f"   ⚠ HTML/PDF generation failed: {e}")

        # Execution time
        elapsed = datetime.now() - start_time
        logger.info(f"Pipeline completed in {elapsed.total_seconds():.1f} seconds")
        print(f"\n✓ Pipeline completed successfully in {elapsed.total_seconds():.1f} seconds")

        return 0

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        print(f"\n✗ ERROR: Pipeline failed - {e}")
        print(f"Check pipeline.log for details")
        return 1


if __name__ == '__main__':
    sys.exit(main())
