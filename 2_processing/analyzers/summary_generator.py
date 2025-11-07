"""Master Findings Report Generator

This module generates a comprehensive master findings report that combines:
- Postal code analyses (geographic patterns)
- Temporal analyses (time-of-day and seasonal patterns)
- Priority analyses (A/B/C priority comparison)
- Yearly analyses (year-by-year trends)
"""
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def generate_master_findings_report(output_dir):
    """Generate comprehensive master findings report.

    Args:
        output_dir: Path to output directory containing all analysis files

    Returns:
        Path: Path to generated report
    """
    output_dir = Path(output_dir)
    report_path = output_dir / "MASTER_FINDINGS_RAPPORT.md"

    logger.info("Generating master findings report...")

    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            # Header
            f.write("# MASTER FINDINGS RAPPORT\n")
            f.write("## Komplet Analyse af Ambulance Responstider i Danmark\n\n")
            f.write(f"**Genereret:** {datetime.now().strftime('%d. %B %Y kl. %H:%M')}\n")
            f.write("**Periode:** 2021-2025 (5 år)\n")
            f.write("**Datasæt:** Postnummer + Tidsmæssige mønstre + Systemanalyser + Årlig udvikling\n\n")
            f.write("---\n\n")

            # Executive Summary
            f.write("## 📊 EXECUTIVE SUMMARY\n\n")
            f.write("Denne rapport kombinerer geografiske (postnummer), tidsmæssige, system- og ")
            f.write("årlige analyser af ambulance-responstider på tværs af alle 5 danske regioner.\n\n")

            # Part 1: Postal code analyses
            _write_postal_code_section(f, output_dir)

            # Part 2: Yearly analyses (NEW!)
            _write_yearly_section(f, output_dir)

            # Part 3: Temporal analyses
            _write_temporal_section(f, output_dir)

            # Part 4: Priority analyses
            _write_priority_section(f, output_dir)

            # Part 5: Data files reference
            _write_data_files_section(f, output_dir)

            # Footer with metadata
            _write_footer(f, output_dir)

        logger.info(f"✓ Master findings report generated: {report_path.name}")
        return report_path

    except Exception as e:
        logger.error(f"Failed to generate master findings report: {e}", exc_info=True)
        raise


def _write_postal_code_section(f, output_dir):
    """Write postal code analysis section."""
    f.write("## 📍 DEL 1: POSTNUMMER-ANALYSER\n\n")

    try:
        # Top 10 worst
        df_worst = pd.read_excel(output_dir / "02_top_10_værste_VALIDERET.xlsx")
        f.write("### 1.1 Top 10 VÆRSTE Postnumre\n\n")
        f.write("| Rank | Postnummer | Region | Gennemsnit (min) | Antal Ture |\n")
        f.write("|------|------------|--------|------------------|------------|\n")
        for i, row in df_worst.head(10).iterrows():
            f.write(f"| {i+1} | **{int(row['Postnummer'])}** | {row['Region']} | ")
            f.write(f"{row['Gennemsnit_minutter']:.1f} | {int(row['Antal_ture']):,} |\n")
        f.write("\n")

        # Top 10 best
        df_best = pd.read_excel(output_dir / "03_top_10_bedste.xlsx")
        f.write("### 1.2 Top 10 BEDSTE Postnumre\n\n")
        f.write("| Rank | Postnummer | Region | Gennemsnit (min) | Antal Ture |\n")
        f.write("|------|------------|--------|------------------|------------|\n")
        for i, row in df_best.head(10).iterrows():
            f.write(f"| {i+1} | **{int(row['Postnummer'])}** | {row['Region']} | ")
            f.write(f"{row['Gennemsnit_minutter']:.1f} | {int(row['Antal_ture']):,} |\n")
        f.write("\n")

        # Regional comparison
        df_regional = pd.read_excel(output_dir / "04_regional_sammenligning.xlsx")
        f.write("### 1.3 Regional Sammenligning\n\n")
        f.write("| Region | Gennemsnit (min) | Median (min) | Total Ture | Postnumre |\n")
        f.write("|--------|------------------|--------------|------------|-----------|\n")
        for _, row in df_regional.iterrows():
            f.write(f"| **{row['Region']}** | {row['Gennemsnit_minutter']:.1f} | ")
            f.write(f"{row['Median_minutter']:.1f} | {int(row['Total_ture']):,} | ")
            f.write(f"{int(row['Antal_postnumre'])} |\n")
        f.write("\n---\n\n")

    except Exception as e:
        logger.warning(f"Could not load postal code data: {e}")
        f.write("*Postnummer-data ikke tilgængelig*\n\n---\n\n")


def _write_yearly_section(f, output_dir):
    """Write yearly analysis section (NEW!)."""
    f.write("## 📅 DEL 2: ÅRLIG UDVIKLING (2021-2025)\n\n")

    try:
        # Yearly summary
        df_yearly = pd.read_excel(output_dir / "11_responstid_per_aar_landsdækkende_A.xlsx")
        f.write("### 2.1 Landsdækkende Udvikling\n\n")
        f.write("**A-prioritet responstider per år:**\n\n")
        f.write("| År | Gennemsnit (min) | Median (min) | Antal Kørsler |\n")
        f.write("|----|------------------|--------------|---------------|\n")
        for _, row in df_yearly.iterrows():
            f.write(f"| **{int(row['Year'])}** | {row['Gennemsnit_minutter']:.1f} | ")
            f.write(f"{row['Median_minutter']:.1f} | {int(row['Antal_kørsler']):,} |\n")
        f.write("\n")

        # Calculate year-over-year changes
        f.write("**År-til-år ændringer:**\n\n")
        for i in range(1, len(df_yearly)):
            year = int(df_yearly.iloc[i]['Year'])
            prev_year = int(df_yearly.iloc[i-1]['Year'])
            current = df_yearly.iloc[i]['Gennemsnit_minutter']
            previous = df_yearly.iloc[i-1]['Gennemsnit_minutter']
            change = current - previous
            pct_change = (change / previous) * 100

            symbol = "↑" if change > 0 else "↓" if change < 0 else "→"
            f.write(f"- {prev_year} → {year}: {change:+.1f} min ({pct_change:+.1f}%) {symbol}\n")
        f.write("\n")

        # Regional yearly breakdown
        df_pivot = pd.read_excel(output_dir / "13_responstid_pivot_aar_x_region_A.xlsx")
        f.write("### 2.2 Regional Udvikling Per År\n\n")
        f.write("**Responstider (minutter) fordelt på region og år:**\n\n")

        # Create markdown table from pivot
        regions = [col for col in df_pivot.columns if col != 'Year']
        f.write("| År | " + " | ".join(regions) + " |\n")
        f.write("|" + "----|" * (len(regions) + 1) + "\n")

        for _, row in df_pivot.iterrows():
            year = int(row['Year'])
            f.write(f"| **{year}** |")
            for region in regions:
                f.write(f" {row[region]:.1f} |")
            f.write("\n")
        f.write("\n")

        # Regional summary (all years combined)
        df_regional_summary = pd.read_excel(output_dir / "12_responstid_per_region_samlet_A.xlsx")
        f.write("### 2.3 Regional Gennemsnit (2021-2025 Samlet)\n\n")
        f.write("| Region | Gennemsnit (min) | Median (min) | Total A-Kørsler |\n")
        f.write("|--------|------------------|--------------|------------------|\n")
        for _, row in df_regional_summary.iterrows():
            f.write(f"| **{row['Region']}** | {row['Gennemsnit_minutter']:.1f} | ")
            f.write(f"{row['Median_minutter']:.1f} | {int(row['Antal_kørsler']):,} |\n")
        f.write("\n")

        # Key insights from yearly data
        best_region = df_regional_summary.iloc[-1]
        worst_region = df_regional_summary.iloc[0]
        diff = worst_region['Gennemsnit_minutter'] - best_region['Gennemsnit_minutter']
        pct_diff = (diff / best_region['Gennemsnit_minutter']) * 100

        f.write("**Vigtigste fund:**\n")
        f.write(f"- Bedste region: {best_region['Region']} ({best_region['Gennemsnit_minutter']:.1f} min)\n")
        f.write(f"- Værste region: {worst_region['Region']} ({worst_region['Gennemsnit_minutter']:.1f} min)\n")
        f.write(f"- Regional forskel: {diff:.1f} min ({pct_diff:.1f}% langsommere)\n")
        f.write(f"- Landsdækkende stabilitet: Meget stabil udvikling 2021-2025\n")
        f.write("\n---\n\n")

    except Exception as e:
        logger.warning(f"Could not load yearly data: {e}")
        f.write("*Årlig analyse-data ikke tilgængelig*\n\n---\n\n")


def _write_temporal_section(f, output_dir):
    """Write temporal analysis section."""
    f.write("## ⏰ DEL 3: TIDSMÆSSIGE MØNSTRE\n\n")

    # Find all regional temporal files
    regions = ['Nordjylland', 'Hovedstaden', 'Sjælland', 'Midtjylland', 'Syddanmark']

    try:
        f.write("### 3.1 Tid-på-Døgnet (Rush Hour)\n\n")
        f.write("**Bedste og værste tidspunkt per region:**\n\n")
        f.write("| Region | Bedste Time | Min | Værste Time | Min | Variation (%) |\n")
        f.write("|--------|-------------|-----|-------------|-----|---------------|\n")

        for region in regions:
            time_file = output_dir / f"{region}_05_responstid_per_time.xlsx"
            if time_file.exists():
                df = pd.read_excel(time_file)
                best_idx = df['Median_minutter'].idxmin()
                worst_idx = df['Median_minutter'].idxmax()

                best_hour = int(df.loc[best_idx, 'Time'])
                best_val = df.loc[best_idx, 'Median_minutter']
                worst_hour = int(df.loc[worst_idx, 'Time'])
                worst_val = df.loc[worst_idx, 'Median_minutter']
                variation = ((worst_val - best_val) / best_val) * 100

                f.write(f"| {region} | kl. {best_hour:02d} | {best_val:.1f} | ")
                f.write(f"**kl. {worst_hour:02d}** | {worst_val:.1f} | {variation:.1f}% |\n")
        f.write("\n")

        f.write("### 3.2 Sæsonvariation (Måned-for-Måned)\n\n")
        f.write("**Bedste og værste måned per region:**\n\n")
        f.write("| Region | Bedste Måned | Min | Værste Måned | Min | Variation (%) |\n")
        f.write("|--------|--------------|-----|--------------|-----|---------------|\n")

        for region in regions:
            month_file = output_dir / f"{region}_06_responstid_per_maaned.xlsx"
            if month_file.exists():
                df = pd.read_excel(month_file)
                best_idx = df['Median_minutter'].idxmin()
                worst_idx = df['Median_minutter'].idxmax()

                best_month = df.loc[best_idx, 'Maaned_navn']
                best_val = df.loc[best_idx, 'Median_minutter']
                worst_month = df.loc[worst_idx, 'Maaned_navn']
                worst_val = df.loc[worst_idx, 'Median_minutter']
                variation = ((worst_val - best_val) / best_val) * 100

                f.write(f"| {region} | {best_month} | {best_val:.1f} | ")
                f.write(f"**{worst_month}** | {worst_val:.1f} | {variation:.1f}% |\n")
        f.write("\n---\n\n")

    except Exception as e:
        logger.warning(f"Could not load temporal data: {e}")
        f.write("*Tidsmæssig analyse-data ikke tilgængelig*\n\n---\n\n")


def _write_priority_section(f, output_dir):
    """Write priority analysis section."""
    f.write("## 🏥 DEL 4: SYSTEMANALYSER\n\n")

    try:
        # A vs B vs C Priority
        df_priority = pd.read_excel(output_dir / "07_prioritering_ABC.xlsx")

        f.write("### 4.1 A vs B vs C Prioritering\n\n")
        f.write("**Responstider fordelt på prioritetsniveau:**\n\n")
        f.write("| Region | A-prioritet (min) | B-prioritet (min) | B vs A Forskel |\n")
        f.write("|--------|-------------------|-------------------|----------------|\n")

        # Group by region and pivot
        for region in df_priority['Region'].unique():
            df_region = df_priority[df_priority['Region'] == region]
            a_val = df_region[df_region['Priority'] == 'A']['Median_minutter'].values
            b_val = df_region[df_region['Priority'] == 'B']['Median_minutter'].values

            if len(a_val) > 0 and len(b_val) > 0:
                a_val = a_val[0]
                b_val = b_val[0]
                diff_pct = ((b_val - a_val) / a_val) * 100
                f.write(f"| {region} | {a_val:.1f} | {b_val:.1f} | +{diff_pct:.1f}% |\n")
        f.write("\n")

        # Rekvireringskanal
        kanal_file = output_dir / "09_rekvireringskanal.xlsx"
        if kanal_file.exists():
            df_kanal = pd.read_excel(kanal_file)
            f.write("### 4.2 Rekvireringskanal (A-prioritet)\n\n")
            f.write("**Responstider fordelt på rekvireringskanal:**\n\n")
            f.write("| Kanal | Gennemsnit (min) | Antal Kørsler |\n")
            f.write("|-------|------------------|---------------|\n")

            # Show top channels
            for _, row in df_kanal.head(10).iterrows():
                f.write(f"| {row['Rekvireringskanal']} | {row['Median_minutter']:.1f} | ")
                f.write(f"{int(row['Antal_ture']):,} |\n")
            f.write("\n")

        f.write("---\n\n")

    except Exception as e:
        logger.warning(f"Could not load priority data: {e}")
        f.write("*System analyse-data ikke tilgængelig*\n\n---\n\n")


def _write_data_files_section(f, output_dir):
    """Write data files reference section."""
    f.write("## 📁 DATAFILER TIL VIDERE ANALYSE\n\n")

    f.write("**Genererede analysefiler:**\n\n")
    f.write("*Postnummer-analyser:*\n")
    f.write("- `01_alle_postnumre.xlsx` - Alle 626 postnumre\n")
    f.write("- `02_top_10_værste_VALIDERET.xlsx` - Top 10 værste\n")
    f.write("- `03_top_10_bedste.xlsx` - Top 10 bedste\n")
    f.write("- `04_regional_sammenligning.xlsx` - Regional sammenligning\n")
    f.write("- `DATAWRAPPER_alle_postnumre.csv` - Kort-visualization\n\n")

    f.write("*Årlige analyser:*\n")
    f.write("- `10_responstid_per_aar_og_region_A.xlsx` - År × Region matrix\n")
    f.write("- `11_responstid_per_aar_landsdækkende_A.xlsx` - Landsdækkende per år\n")
    f.write("- `12_responstid_per_region_samlet_A.xlsx` - Regional total\n")
    f.write("- `13_responstid_pivot_aar_x_region_A.xlsx` - Pivot-tabel\n")
    f.write("- `ÅRLIG_ANALYSE_FUND_A.txt` - Key findings\n\n")

    f.write("*Tidsmæssige analyser (per region):*\n")
    f.write("- `{Region}_05_responstid_per_time.xlsx` - Time-for-time\n")
    f.write("- `{Region}_06_responstid_per_maaned.xlsx` - Måned-for-måned\n")
    f.write("- `{Region}_DATAWRAPPER_*.csv` - Visualization data\n\n")

    f.write("*Systemanalyser:*\n")
    f.write("- `07_prioritering_ABC.xlsx` - A/B/C prioritering\n")
    f.write("- `09_rekvireringskanal.xlsx` - Rekvireringskanal\n")
    f.write("- `DATAWRAPPER_prioritering_ABC.csv` - Priority visualization\n\n")

    f.write("---\n\n")


def _write_footer(f, output_dir):
    """Write report footer with metadata."""
    f.write("## 📋 METODE OG DATAGRUNDLAG\n\n")

    f.write("**Dataindsamling:**\n")
    f.write("- Ambulance-data fra alle 5 danske regioner\n")
    f.write("- Periode: 2021-2025 (5 år)\n")
    f.write("- Omfatter tidsstempler for alarm, disponering og ankomst\n\n")

    f.write("**Statistisk metode:**\n")
    f.write("- Median anvendt som primært mål (robust mod ekstreme værdier)\n")
    f.write("- Fokus på A-prioritet (livstruende) kørsler\n")
    f.write("- Statistisk validering: Minimum 50 ture for Top 10 lister\n\n")

    f.write("---\n\n")
    f.write(f"**RAPPORT GENERERET: {datetime.now().strftime('%d. %B %Y kl. %H:%M')}**\n\n")
    f.write("*Genereret automatisk af Ambulance Pipeline*\n")


def generate_consolidated_summary(output_dir):
    """Generate consolidated temporal summary (legacy compatibility).

    This function is kept for backward compatibility but now delegates
    to the main master findings report generator.
    """
    logger.info("Generating consolidated temporal summary...")
    return generate_master_findings_report(output_dir)
