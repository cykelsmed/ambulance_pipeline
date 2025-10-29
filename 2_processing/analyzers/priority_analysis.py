"""Priority and System Analysis Module

This module analyzes system-level patterns:
1. A vs B vs C priority response times
2. Hastegrad changes (priority reclassification)
3. Rekvireringskanal (channel) effectiveness
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def analyze_abc_priority(df: pd.DataFrame, hastegrad_col: str = 'Hastegrad ved oprettelse',
                         response_col: str = 'ResponstidMinutter',
                         region_col: str = 'Region') -> pd.DataFrame:
    """Analyze response times per priority level (A/B/C).

    Args:
        df: Raw ambulance data
        hastegrad_col: Priority column name
        response_col: Response time column name
        region_col: Region column name

    Returns:
        DataFrame with priority statistics per region
    """
    logger.info("Analyzing A/B/C priority response times...")

    # Group by region and priority
    stats = df.groupby([region_col, hastegrad_col])[response_col].agg([
        ('Antal_ture', 'count'),
        ('Gennemsnit_minutter', 'mean'),
        ('Median_minutter', 'median'),
        ('Std_minutter', 'std'),
        ('Min_minutter', 'min'),
        ('Max_minutter', 'max')
    ]).reset_index()

    # Round to 1 decimal
    for col in ['Gennemsnit_minutter', 'Median_minutter', 'Std_minutter',
                'Min_minutter', 'Max_minutter']:
        stats[col] = stats[col].round(1)

    # Rename columns
    stats = stats.rename(columns={
        hastegrad_col: 'Hastegrad',
        region_col: 'Region'
    })

    logger.info(f"  Analyzed {len(stats)} region × priority combinations")
    logger.info(f"  Total ture: {stats['Antal_ture'].sum():,}")

    return stats


def calculate_priority_differences(abc_stats: pd.DataFrame) -> pd.DataFrame:
    """Calculate percentage differences between priority levels.

    Args:
        abc_stats: Output from analyze_abc_priority

    Returns:
        DataFrame with priority comparisons
    """
    comparisons = []

    for region in abc_stats['Region'].unique():
        region_data = abc_stats[abc_stats['Region'] == region]

        # Get median for each priority
        priorities = {}
        for _, row in region_data.iterrows():
            priorities[row['Hastegrad']] = row['Median_minutter']

        # Calculate differences
        if 'A' in priorities and 'B' in priorities:
            b_vs_a = ((priorities['B'] - priorities['A']) / priorities['A'] * 100)
            comparisons.append({
                'Region': region,
                'A_median': priorities.get('A', np.nan),
                'B_median': priorities.get('B', np.nan),
                'C_median': priorities.get('C', np.nan),
                'B_vs_A_procent': round(b_vs_a, 1) if not np.isnan(b_vs_a) else np.nan
            })

    return pd.DataFrame(comparisons)


def analyze_rekvireringskanal(df: pd.DataFrame,
                              kanal_col: str = 'Rekvireringskanal',
                              hastegrad_col: str = 'Hastegrad ved oprettelse',
                              response_col: str = 'ResponstidMinutter',
                              region_col: str = 'Region') -> pd.DataFrame:
    """Analyze response times by rekvireringskanal (112, Lægevagt, Hospital, etc.).

    Args:
        df: Raw ambulance data
        kanal_col: Channel column name
        hastegrad_col: Priority column name
        response_col: Response time column name
        region_col: Region column name

    Returns:
        DataFrame with channel statistics
    """
    logger.info("Analyzing rekvireringskanal effectiveness...")

    # Group by region, channel, and priority
    stats = df.groupby([region_col, kanal_col, hastegrad_col])[response_col].agg([
        ('Antal_ture', 'count'),
        ('Gennemsnit_minutter', 'mean'),
        ('Median_minutter', 'median')
    ]).reset_index()

    # Round
    for col in ['Gennemsnit_minutter', 'Median_minutter']:
        stats[col] = stats[col].round(1)

    # Rename
    stats = stats.rename(columns={
        kanal_col: 'Rekvireringskanal',
        hastegrad_col: 'Hastegrad',
        region_col: 'Region'
    })

    logger.info(f"  Analyzed {len(stats)} region × channel × priority combinations")

    return stats


def analyze_hastegrad_changes(df: pd.DataFrame,
                              initial_col: str = 'Hastegrad ved visitering',
                              final_col: str = 'Hastegrad ved ankomst',
                              response_col: str = 'ResponstidMinutter',
                              region_col: str = 'Region') -> Dict[str, Any]:
    """Analyze changes in priority classification during response.

    Args:
        df: Raw ambulance data
        initial_col: Initial priority column
        final_col: Final priority column
        response_col: Response time column
        region_col: Region column

    Returns:
        Dictionary with change statistics
    """
    logger.info("Analyzing hastegrad changes...")

    # Check if columns exist
    if initial_col not in df.columns or final_col not in df.columns:
        logger.warning(f"  Columns {initial_col} or {final_col} not found - skipping")
        return None

    # Identify changes
    df_changes = df.copy()
    df_changes['Hastegrad_ændret'] = df_changes[initial_col] != df_changes[final_col]

    # Count changes per region
    changes_by_region = df_changes.groupby(region_col).agg({
        'Hastegrad_ændret': ['sum', 'count']
    })
    changes_by_region.columns = ['Antal_ændringer', 'Total_ture']
    changes_by_region['Procent_ændret'] = (
        changes_by_region['Antal_ændringer'] / changes_by_region['Total_ture'] * 100
    ).round(1)
    changes_by_region = changes_by_region.reset_index()

    # Analyze type of changes (A→B, B→A, etc.)
    change_types = df_changes[df_changes['Hastegrad_ændret']].groupby(
        [region_col, initial_col, final_col]
    ).size().reset_index(name='Antal')

    # Compare response times for changed vs unchanged
    response_comparison = df_changes.groupby('Hastegrad_ændret')[response_col].agg([
        ('Median_minutter', 'median'),
        ('Antal', 'count')
    ]).reset_index()

    logger.info(f"  Total changes: {df_changes['Hastegrad_ændret'].sum():,}")
    logger.info(f"  Change rate: {(df_changes['Hastegrad_ændret'].sum() / len(df_changes) * 100):.1f}%")

    return {
        'changes_by_region': changes_by_region,
        'change_types': change_types,
        'response_comparison': response_comparison
    }


def export_priority_analyses(abc_stats: pd.DataFrame,
                             abc_diffs: pd.DataFrame,
                             kanal_stats: pd.DataFrame,
                             hastegrad_changes: Dict[str, Any],
                             output_dir: Path) -> list:
    """Export all priority analysis results.

    Args:
        abc_stats: A/B/C priority statistics
        abc_diffs: Priority comparisons
        kanal_stats: Channel statistics
        hastegrad_changes: Change analysis results
        output_dir: Output directory

    Returns:
        List of generated file paths
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    files_generated = []

    # Export ABC priority analysis
    abc_file = output_dir / "07_prioritering_ABC.xlsx"
    with pd.ExcelWriter(abc_file, engine='openpyxl') as writer:
        abc_stats.to_excel(writer, sheet_name='Detaljeret', index=False)
        abc_diffs.to_excel(writer, sheet_name='Sammenligninger', index=False)
    logger.info(f"✓ Exported: {abc_file.name}")
    files_generated.append(str(abc_file))

    # Export ABC findings
    abc_fund_file = output_dir / "07_prioritering_ABC_FUND.txt"
    with open(abc_fund_file, 'w', encoding='utf-8') as f:
        f.write("SYSTEMANALYSE - A vs B vs C PRIORITERING\n")
        f.write("="*50 + "\n\n")
        f.write(f"Total kørsler analyseret: {abc_stats['Antal_ture'].sum():,}\n\n")

        f.write("HOVEDFUND:\n")
        for _, row in abc_diffs.iterrows():
            f.write(f"\n{row['Region']}:\n")
            f.write(f"  A-prioritet: {row['A_median']:.1f} min median\n")
            f.write(f"  B-prioritet: {row['B_median']:.1f} min median\n")
            if not pd.isna(row['B_vs_A_procent']):
                f.write(f"  Forskel: B er {abs(row['B_vs_A_procent']):.1f}% {'langsommere' if row['B_vs_A_procent'] > 0 else 'hurtigere'} end A\n")
    logger.info(f"✓ Exported: {abc_fund_file.name}")
    files_generated.append(str(abc_fund_file))

    # Export Datawrapper CSV for ABC
    dw_abc = abc_stats[['Region', 'Hastegrad', 'Median_minutter', 'Antal_ture']].copy()
    dw_abc_file = output_dir / "DATAWRAPPER_prioritering_ABC.csv"
    dw_abc.to_csv(dw_abc_file, index=False)
    logger.info(f"✓ Exported: {dw_abc_file.name}")
    files_generated.append(str(dw_abc_file))

    # Export rekvireringskanal analysis
    kanal_file = output_dir / "09_rekvireringskanal.xlsx"
    kanal_stats.to_excel(kanal_file, index=False)
    logger.info(f"✓ Exported: {kanal_file.name}")
    files_generated.append(str(kanal_file))

    # Export kanal findings
    kanal_fund_file = output_dir / "09_rekvireringskanal_FUND.txt"
    with open(kanal_fund_file, 'w', encoding='utf-8') as f:
        f.write("SYSTEMANALYSE - REKVIRERINGSKANAL\n")
        f.write("="*50 + "\n\n")
        f.write(f"Total kørsler analyseret: {kanal_stats['Antal_ture'].sum():,}\n\n")

        f.write("KANALER:\n")
        for kanal in kanal_stats['Rekvireringskanal'].unique():
            kanal_data = kanal_stats[kanal_stats['Rekvireringskanal'] == kanal]
            avg_response = kanal_data['Median_minutter'].mean()
            total_ture = kanal_data['Antal_ture'].sum()
            f.write(f"  {kanal}: {avg_response:.1f} min gennemsnit ({total_ture:,} ture)\n")
    logger.info(f"✓ Exported: {kanal_fund_file.name}")
    files_generated.append(str(kanal_fund_file))

    # Export Datawrapper CSV for kanal (A-priority only)
    kanal_a = kanal_stats[kanal_stats['Hastegrad'] == 'A'][
        ['Region', 'Rekvireringskanal', 'Median_minutter', 'Antal_ture']
    ].copy()
    dw_kanal_file = output_dir / "DATAWRAPPER_rekvireringskanal.csv"
    kanal_a.to_csv(dw_kanal_file, index=False)
    logger.info(f"✓ Exported: {dw_kanal_file.name}")
    files_generated.append(str(dw_kanal_file))

    # Export hastegrad changes if available
    if hastegrad_changes is not None:
        change_file = output_dir / "08_hastegradomlaegning.xlsx"
        with pd.ExcelWriter(change_file, engine='openpyxl') as writer:
            hastegrad_changes['changes_by_region'].to_excel(writer, sheet_name='Per Region', index=False)
            hastegrad_changes['change_types'].to_excel(writer, sheet_name='Ændringstyper', index=False)
            hastegrad_changes['response_comparison'].to_excel(writer, sheet_name='Responstid sammenligning', index=False)
        logger.info(f"✓ Exported: {change_file.name}")
        files_generated.append(str(change_file))

        # Export hastegrad findings
        change_fund_file = output_dir / "08_hastegradomlaegning_FUND.txt"
        with open(change_fund_file, 'w', encoding='utf-8') as f:
            f.write("SYSTEMANALYSE - HASTEGRADOMLÆGNING\n")
            f.write("="*50 + "\n\n")

            total_changes = hastegrad_changes['changes_by_region']['Antal_ændringer'].sum()
            total_ture = hastegrad_changes['changes_by_region']['Total_ture'].sum()
            change_rate = (total_changes / total_ture * 100) if total_ture > 0 else 0

            f.write(f"Total ændringer: {total_changes:,} af {total_ture:,} ture ({change_rate:.1f}%)\n\n")

            f.write("PER REGION:\n")
            for _, row in hastegrad_changes['changes_by_region'].iterrows():
                f.write(f"  {row['Region']}: {row['Antal_ændringer']:,} ændringer ({row['Procent_ændret']:.1f}%)\n")
        logger.info(f"✓ Exported: {change_fund_file.name}")
        files_generated.append(str(change_fund_file))

    return files_generated
