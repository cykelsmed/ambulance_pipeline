"""
Dispatch Delay vs Travel Time Analysis

Analyzes the breakdown of total ambulance response time into:
1. Dispatch delay: Time from 112 call to unit dispatch
2. Travel time: Time from dispatch to arrival

Only available for regions with DATETIME timestamps (Nordjylland + Syddanmark).
Other regions use TIME-ONLY format which cannot calculate time differences across midnight.

Author: Claude Code
Created: 2025-11-08
"""

import pandas as pd
import logging
from pathlib import Path
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


# Regional timestamp column mappings (only regions with DATETIME format)
REGIONAL_CONFIGS = {
    'Nordjylland': {
        'file': '1_input/Nordjylland20251029.xlsx',
        'sheet': 'Nordjylland',
        'priority_col': 'Hastegrad ved oprettelse',
        't1_call_received': 'Alarm modtaget',
        't2_dispatch': 'Alarmering af første enhed',
        't3_arrival': 'Ankomst første professionelle præhospitale enhed'
    },
    'Syddanmark': {
        'file': '1_input/Syddanmark20251025.xlsx',
        'sheet': 'Syddanmark',
        'priority_col': 'Hastegrad ved oprettelse',
        't1_call_received': 'Hændelse oprettet i disponeringssystem',
        't2_dispatch': 'Disponering af første enhed',
        't3_arrival': 'Ankomst første sundhedsprofessionelle enhed'
    }
}


def calculate_dispatch_and_travel_times(region_name: str, config: Dict) -> pd.DataFrame:
    """
    Calculate dispatch delay and travel time for a single region.

    Returns DataFrame with columns:
    - Region
    - Priority
    - Total_Cases
    - Valid_Cases (with all 3 timestamps)
    - Total_Wait_Median (minutes)
    - Dispatch_Delay_Median (minutes)
    - Travel_Time_Median (minutes)
    - Dispatch_Pct (% of total wait time)
    - Travel_Pct (% of total wait time)
    """
    logger.info(f"Analyzing dispatch delay for {region_name}...")

    # Load data
    df = pd.read_excel(config['file'], sheet_name=config['sheet'])
    logger.info(f"  Loaded {len(df):,} rows from {region_name}")

    # Filter to A and B priority
    priority_col = config['priority_col']
    df_priority = df[df[priority_col].isin(['A', 'B'])].copy()
    logger.info(f"  A+B priority cases: {len(df_priority):,}")

    # Convert timestamps to datetime
    t1_col = config['t1_call_received']
    t2_col = config['t2_dispatch']
    t3_col = config['t3_arrival']

    df_priority['t1_call'] = pd.to_datetime(df_priority[t1_col], errors='coerce')
    df_priority['t2_dispatch'] = pd.to_datetime(df_priority[t2_col], errors='coerce')
    df_priority['t3_arrival'] = pd.to_datetime(df_priority[t3_col], errors='coerce')

    # Filter to valid rows (all 3 timestamps present)
    valid_mask = (
        df_priority['t1_call'].notna() &
        df_priority['t2_dispatch'].notna() &
        df_priority['t3_arrival'].notna()
    )
    df_valid = df_priority[valid_mask].copy()

    logger.info(f"  Valid cases (all 3 timestamps): {len(df_valid):,} ({len(df_valid)/len(df_priority)*100:.1f}%)")

    # Calculate time differences (in minutes)
    df_valid['dispatch_delay_min'] = (df_valid['t2_dispatch'] - df_valid['t1_call']).dt.total_seconds() / 60
    df_valid['travel_time_min'] = (df_valid['t3_arrival'] - df_valid['t2_dispatch']).dt.total_seconds() / 60
    df_valid['total_wait_min'] = (df_valid['t3_arrival'] - df_valid['t1_call']).dt.total_seconds() / 60

    # Filter out invalid time differences (negative or unreasonably large)
    # Reasonable limits: dispatch delay 0-60 min, travel time 0-120 min
    filter_mask = (
        (df_valid['dispatch_delay_min'] >= 0) & (df_valid['dispatch_delay_min'] <= 60) &
        (df_valid['travel_time_min'] >= 0) & (df_valid['travel_time_min'] <= 120) &
        (df_valid['total_wait_min'] >= 0) & (df_valid['total_wait_min'] <= 180)
    )
    df_clean = df_valid[filter_mask].copy()

    logger.info(f"  Clean cases (valid time ranges): {len(df_clean):,} ({len(df_clean)/len(df_valid)*100:.1f}%)")

    # Calculate statistics by priority
    results = []
    for priority in ['A', 'B']:
        df_p = df_clean[df_clean[priority_col] == priority]
        if len(df_p) == 0:
            continue

        total_wait_median = df_p['total_wait_min'].median()
        dispatch_delay_median = df_p['dispatch_delay_min'].median()
        travel_time_median = df_p['travel_time_min'].median()

        # Calculate percentages
        dispatch_pct = (dispatch_delay_median / total_wait_median * 100) if total_wait_median > 0 else 0
        travel_pct = (travel_time_median / total_wait_median * 100) if total_wait_median > 0 else 0

        results.append({
            'Region': region_name,
            'Priority': priority,
            'Total_Cases': len(df_priority[df_priority[priority_col] == priority]),
            'Valid_Cases': len(df_p),
            'Total_Wait_Median': round(total_wait_median, 1),
            'Dispatch_Delay_Median': round(dispatch_delay_median, 1),
            'Travel_Time_Median': round(travel_time_median, 1),
            'Dispatch_Pct': round(dispatch_pct, 1),
            'Travel_Pct': round(travel_pct, 1)
        })

    return pd.DataFrame(results)


def run_dispatch_delay_analysis(output_dir: str = '3_output/current') -> Tuple[pd.DataFrame, str]:
    """
    Run dispatch delay analysis for all supported regions.

    Returns:
    - DataFrame with analysis results
    - Text summary report
    """
    logger.info("Starting dispatch delay vs. travel time analysis...")
    logger.info(f"Analyzing {len(REGIONAL_CONFIGS)} regions: {', '.join(REGIONAL_CONFIGS.keys())}")

    all_results = []

    for region_name, config in REGIONAL_CONFIGS.items():
        try:
            df_region = calculate_dispatch_and_travel_times(region_name, config)
            all_results.append(df_region)
        except Exception as e:
            logger.error(f"Failed to analyze {region_name}: {e}", exc_info=True)

    # Combine all results
    df_combined = pd.concat(all_results, ignore_index=True)

    # Generate text summary
    summary = generate_summary_report(df_combined)

    # Export to Excel
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    excel_file = output_path / '20_dispatch_delay_vs_travel.xlsx'
    df_combined.to_excel(excel_file, index=False, sheet_name='Dispatch_vs_Travel')
    logger.info(f"Exported analysis to {excel_file}")

    # Export text summary
    summary_file = output_path / '20_DISPATCH_DELAY_FUND.txt'
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    logger.info(f"Exported summary to {summary_file}")

    return df_combined, summary


def generate_summary_report(df: pd.DataFrame) -> str:
    """Generate human-readable summary report."""

    lines = []
    lines.append("DISPATCH DELAY VS. TRAVEL TIME")
    lines.append("=" * 60)
    lines.append("")
    lines.append("ANALYSE AF TOTAL VENTETID FOR BORGEREN")
    lines.append("Opdeling: 112-opkald → dispatch → ankomst")
    lines.append("")
    lines.append("GEOGRAFISK BEGRÆNSNING:")
    lines.append("Kun Nordjylland + Syddanmark har datetime-format timestamps.")
    lines.append("Hovedstaden, Sjælland, og Midtjylland bruger time-only format,")
    lines.append("hvilket ikke kan håndtere tidsdifference hen over midnat.")
    lines.append("")
    lines.append("=" * 60)
    lines.append("")

    for _, row in df.iterrows():
        region = row['Region']
        priority = row['Priority']
        total_cases = int(row['Total_Cases'])
        valid_cases = int(row['Valid_Cases'])

        total_wait = row['Total_Wait_Median']
        dispatch_delay = row['Dispatch_Delay_Median']
        travel_time = row['Travel_Time_Median']
        dispatch_pct = row['Dispatch_Pct']
        travel_pct = row['Travel_Pct']

        lines.append(f"{region} - {priority}-prioritet:")
        lines.append(f"  Analyseret: {valid_cases:,} kørsler (af {total_cases:,} total)")
        lines.append(f"  Total ventetid (median): {total_wait:.1f} min")
        lines.append(f"    → Dispatch delay: {dispatch_delay:.1f} min ({dispatch_pct:.0f}%)")
        lines.append(f"    → Rejsetid: {travel_time:.1f} min ({travel_pct:.0f}%)")
        lines.append("")

    lines.append("=" * 60)
    lines.append("")
    lines.append("KONKLUSION:")

    # Calculate overall averages
    a_priority = df[df['Priority'] == 'A']
    b_priority = df[df['Priority'] == 'B']

    if len(a_priority) > 0:
        avg_dispatch_pct_a = a_priority['Dispatch_Pct'].mean()
        avg_travel_pct_a = a_priority['Travel_Pct'].mean()
        lines.append(f"A-prioritet: Dispatch delay udgør ca. {avg_dispatch_pct_a:.0f}% af total ventetid,")
        lines.append(f"             Rejsetid udgør ca. {avg_travel_pct_a:.0f}%")

    if len(b_priority) > 0:
        avg_dispatch_pct_b = b_priority['Dispatch_Pct'].mean()
        avg_travel_pct_b = b_priority['Travel_Pct'].mean()
        lines.append(f"B-prioritet: Dispatch delay udgør ca. {avg_dispatch_pct_b:.0f}% af total ventetid,")
        lines.append(f"             Rejsetid udgør ca. {avg_travel_pct_b:.0f}%")

    lines.append("")
    lines.append("Dette viser hvor stor andel af borgerens ventetid der skyldes")
    lines.append("system-delay (triage + dispatch) vs. faktisk transporttid.")
    lines.append("")

    return "\n".join(lines)


if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Run analysis
    df_results, summary = run_dispatch_delay_analysis()

    print("\n" + summary)
    print(f"\nAnalyzed {len(df_results)} priority groups across 2 regions")
