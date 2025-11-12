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
import sys
import subprocess

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from postal_code_names import get_postal_code_name

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

            # Executive Summary - TV2 FOCUSED
            f.write("## 📋 HOVEDHISTORIER - KEY FINDINGS\n\n")

            # Load key data for executive summary
            try:
                # Files may be in bilag/ subdirectory or root
                bilag_dir = output_dir / "bilag"
                data_dir = bilag_dir if bilag_dir.exists() else output_dir

                df_worst = pd.read_excel(data_dir / "02_top_10_værste_VALIDERET.xlsx")
                df_best = pd.read_excel(data_dir / "03_top_10_bedste.xlsx")
                df_regional = pd.read_excel(data_dir / "04_regional_sammenligning.xlsx")
                df_yearly = pd.read_excel(data_dir / "11_responstid_per_aar_landsdækkende_A.xlsx")

                # Calculate key stats
                worst_postal = df_worst.iloc[0]
                best_postal = df_best.iloc[0]
                postal_ratio = worst_postal['Gennemsnit_minutter'] / best_postal['Gennemsnit_minutter']

                # Get postal code names
                worst_postal_name = get_postal_code_name(worst_postal['Postnummer'])
                best_postal_name = get_postal_code_name(best_postal['Postnummer'])

                worst_region = df_regional.iloc[0]
                best_region = df_regional.iloc[-1]
                regional_diff_pct = ((worst_region['Gennemsnit_minutter'] - best_region['Gennemsnit_minutter']) / best_region['Gennemsnit_minutter']) * 100
                regional_diff_min = worst_region['Gennemsnit_minutter'] - best_region['Gennemsnit_minutter']

                # Write key findings with journalistic headlines
                f.write("### 📊 Top 8 Fund:\n\n")

                # 1. Geografisk variation
                f.write(f"**1. \"Ambulancen kommer fire gange hurtigere i Esbjerg end i Hobro. ")
                f.write(f"Din adresse kan betyde 15 minutters forskel.\"**  \n")
                f.write(f"*{postal_ratio:.1f}x forskel mellem bedste og værste postnummer*\n\n")
                f.write(f"Værste postnummer ({worst_postal_name}: {worst_postal['Gennemsnit_minutter']:.1f} min) ")
                f.write(f"har {postal_ratio:.1f}x længere responstid end bedste ({best_postal_name}: ")
                f.write(f"{best_postal['Gennemsnit_minutter']:.1f} min). Variationen følger et geografisk mønster ")
                f.write(f"med landdistriker langsommere end bycentre.\n\n")

                # 2. Regional forskel
                f.write(f"**2. \"Alle regioner når deres servicemål – men Nordjylland er alligevel 45% langsommere end Syddanmark. ")
                f.write(f"Rigsrevisionen kritiserer at regionerne bruger forskellige målemetoder.\"**  \n")
                f.write(f"*{regional_diff_min:.1f} minutters forskel mellem hurtigste og langsomste region*\n\n")
                f.write(f"{worst_region['Region']} er **{regional_diff_pct:.1f}% langsommere** end ")
                f.write(f"{best_region['Region']} ({worst_region['Gennemsnit_minutter']:.1f} min vs ")
                f.write(f"{best_region['Gennemsnit_minutter']:.1f} min). Alle regioner opfylder formelt deres servicemål. ")
                f.write(f"Rigsrevisionen (SR 11/2024) påpeger at regionerne opererer med forskellige definitioner ")
                f.write(f"og tællemetoder.\n\n")

                # 3. Tidsmæssig variation
                f.write(f"**3. \"Når trafikken letter om natten, bliver ambulancerne langsommere. ")
                f.write(f"Myldretiden kl. 17 er faktisk blandt dagens hurtigste timer.\"**  \n")
                f.write(f"*20-28% variation mellem tidspunkter på døgnet*\n\n")
                f.write(f"Ambulancer er 20-28% langsommere om natten (kl. 02-06) end på dagen. ")
                f.write(f"Værste tidspunkt: kl. 06:00. Responstider er korteste kl. 08, mens kl. 17 (myldretid) ")
                f.write(f"er blandt de hurtigste timer.\n\n")

                # 4. B-prioritet
                f.write(f"**4. \"Ikke livstruende? Så venter du over dobbelt så længe. ")
                f.write(f"I Hovedstaden er B-patienter 140% langsommere end A-patienter.\"**  \n")
                f.write(f"*60-140% forskel mellem A og B-prioritet*\n\n")
                f.write(f"B-prioritet kørsler er 60-140% langsommere end A-prioritet. ")
                f.write(f"Hovedstaden: A=9.1 min, B=21.9 min (+140.7%). A-prioritet dækker livstruende tilfælde, ")
                f.write(f"mens B-prioritet omfatter ikke-livstruende tilfælde.\n\n")

                # 5. Alarmtid
                f.write(f"**5. \"To minutter går før ambulancen overhovedet forlader stationen. ")
                f.write(f"Regionernes servicemål starter først når ambulancen sendes afsted – ikke når du ringer 112.\"**  \n")
                f.write(f"*Ca. 22% af ventetid sker før ambulancen sendes afsted*\n\n")
                f.write(f"Tiden fra 112-opkald til ambulancen sendes afsted udgør ca. 22% af total ventetid ")
                f.write(f"(~2 min median). Data fra Nordjylland + Syddanmark (549,000 kørsler). ")
                f.write(f"Rigsrevisionens notat (SR 11/2024): Denne tid medregnes ikke i regionernes servicemål. ")
                f.write(f"**Databegrænsning:** Kun 2 ud af 5 regioner har datetime-data der muliggør denne analyse. ")
                f.write(f"Hovedstaden, Sjælland og Midtjylland bruger time-only format.\n\n")

                # 6. 1813 vs 112
                f.write(f"**6. \"Ring 112 - ikke 1813. Lægevagten sender 46% langsommere ambulancer\"**  \n")
                f.write(f"*8.6 minutter forskel mellem 112 og 1813*\n\n")
                f.write(f"Ambulancer rekvireret gennem 1813 (lægevagten) har 26.9 minutters gennemsnitlig ")
                f.write(f"responstid, sammenlignet med 18.3 minutter for 112-opkald. Forskellen er særligt ")
                f.write(f"markant i Hovedstaden, hvor B-prioritet gennem 1813 har 25.4 minutters median responstid. ")
                f.write(f"Data dækker 1.7 millioner kørsler fra alle regioner. ")
                f.write(f"**Datadetalje:** 112: 1,055,902 kørsler | 1813: 98,169 kørsler\n\n")

                # 7. Indre by ekstrem
                f.write(f"**7. \"I indre København venter ikke-livstruende patienter syv gange længere end livstruende\"**  \n")
                f.write(f"*B/A-ratio på 6.9x i postnummer 1461*\n\n")
                f.write(f"Mens den gennemsnitlige forskel mellem A og B-prioritet i Hovedstaden er 140%, ")
                f.write(f"viser postnumre i indre København (1xxx) ekstremt større forskelle. ")
                f.write(f"Top 10 postnumre med størst B/A-forskel er alle i Hovedstaden: ")
                f.write(f"Postnummer 1461 (B=27.6 min, A=4.0 min, ratio: 6.9x), ")
                f.write(f"Postnummer 1126 (B=39.7 min, A=6.2 min, ratio: 6.4x), ")
                f.write(f"Postnummer 1777 (B=36.9 min, A=5.9 min, ratio: 6.3x). ")
                f.write(f"**Mønster:** Je tættere på København centrum, desto større forskel mellem A og B-prioritet.\n\n")

                # 8. Hovedstaden kl. 23
                f.write(f"**8. \"Hovedstaden skiller sig ud: Værst kl. 23 - ikke ved morgenvagt-skifte\"**  \n")
                f.write(f"*Eneste region hvor aften er problemet*\n\n")
                f.write(f"Alle regioner undtagen Hovedstaden har værste responstider tidlig morgen (kl. 05-06). ")
                f.write(f"Hovedstaden har værste responstid kl. 23 (14.9 min). Tidsperiode-gennemsnit Hovedstaden: ")
                f.write(f"Dag (06-18): 13.3 min, Nat (00-06): 14.1 min, Aften (18-24): 14.0 min (værst kl. 23). ")
                f.write(f"Til sammenligning har Nordjylland værst kl. 06 (16.1 min), Sjælland værst kl. 06 (13.2 min), ")
                f.write(f"Midtjylland værst kl. 05 (12.6 min), Syddanmark værst kl. 06 (9.2 min).\n\n")

                f.write("---\n\n")
                f.write("### 📊 Datagrundlag:\n")
                f.write("- **875,000+ A-prioritet kørsler** analyseret (livstruende tilfælde)\n")
                f.write("- **493,000+ A+B-kørsler** i tidsmæssige analyser (fuld belastning)\n")
                f.write("- **549,000+ kørsler** med alarmtid-analyse (Nordjylland + Syddanmark)\n")
                f.write("- **1,543,000+ total kørsler** analyseret (inkl. C-prioritet)\n")
                f.write("- **1,724,810 total kørsler** analyseret inkl. rekvireringskanal-data\n")
                f.write("- **5 års data** (2021-2025) fra alle 5 danske regioner\n")
                f.write(f"- **{len(pd.read_excel(data_dir / '01_alle_postnumre.xlsx'))} postnumre** kortlagt\n")
                f.write("- **Top 10 B/A ekstreme postnumre** alle i Hovedstaden (København centrum)\n\n")

                # Add data quality disclaimer about helicopter data
                f.write("### ⚠️ Datakvalitet-Note: Helikopter-Data\n\n")
                f.write("**Vigtigt:** Analysen inkluderer alle A-prioritet kørsler i regionernes data, ")
                f.write("inklusiv kørsler hvor helikopter var den første responder. De regionale datasæt ")
                f.write("indeholder ikke oplysninger om hvem der var \"først på skadestedet\" (ambulance vs. helikopter). ")
                f.write("Dette kan påvirke postnummer-statistikkerne for øer og yderområder hvor helikopter ")
                f.write("ofte indsættes.\n\n")
                f.write("**Eksempler fra data:**\n")
                f.write("- Nordjylland: 142 helikopter-kørsler ud af 85,063 A-kørsler (0.17%)\n")
                f.write("- Øer som Fur (7884) og Fejø (4944) i Top 10 værste kan være påvirket\n\n")
                f.write("**Konsekvens:** Postnummer-responstider kan være en blanding af ambulance- og ")
                f.write("helikopter-responstider. For at få det fulde billede bør nationale helikopter-data ")
                f.write("analyseres separat.\n\n")

            except Exception as e:
                logger.warning(f"Could not generate executive summary stats: {e}")
                f.write("*TV2 key findings ikke tilgængelige - se detaljerede sektioner nedenfor*\n\n")

            # Part 1: Postal code analyses
            _write_postal_code_section(f, output_dir)

            # Part 2: Yearly analyses (NEW!)
            _write_yearly_section(f, output_dir)

            # Part 3: Temporal analyses
            _write_temporal_section(f, output_dir)

            # Part 4: Priority analyses
            _write_priority_section(f, output_dir)

            # Part 5: B-Priority deep analyses
            _write_b_priority_section(f, output_dir)

            # Part 6: Alarm Time Analysis (NEW!)
            _write_alarm_time_section(f, output_dir)

            # Part 7: Helicopter Analysis (NEW!)
            _write_helicopter_section(f, output_dir)

            # Part 8: Vehicle Type Analysis (NEW!)
            _write_vehicle_type_section(f, output_dir)

            # Part 9: Data files reference
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
    f.write("**Hovedfund:** Markant geografisk variation i ambulance-responstider.\n\n")
    f.write("Analysen viser betydelig geografisk variation i responstider. ")
    f.write("Forskellen mellem langsomste og hurtigste postnummer er op til 4 gange. ")
    f.write("Variationen følger et geografisk mønster.\n\n")

    try:
        # Files may be in bilag/ subdirectory or root
        bilag_dir = output_dir / "bilag"
        data_dir = bilag_dir if bilag_dir.exists() else output_dir

        # Top 10 worst
        df_worst = pd.read_excel(data_dir / "02_top_10_værste_VALIDERET.xlsx")
        f.write("### 1.1 Top 10 VÆRSTE Postnumre\n\n")
        f.write("**Her venter du længst på ambulancen:**\n\n")
        f.write("*Primært landdistriker med store geografiske afstande - bemærk især Midtjylland dominerer top 10.*\n\n")
        f.write("| Rank | Postnummer | Region | Gennemsnit (min) | Antal Ture |\n")
        f.write("|------|------------|--------|------------------|------------|\n")
        for i, row in df_worst.head(10).iterrows():
            postal_name = get_postal_code_name(row['Postnummer'])
            f.write(f"| {i+1} | **{postal_name}** | {row['Region']} | ")
            f.write(f"{row['Gennemsnit_minutter']:.1f} | {int(row['Antal_ture']):,} |\n")
        f.write("\n")

        # Add note about islands and helicopter data
        f.write("**Note om øer:** Fur (#2) og Fejø (#4) er øer med kun færgeforbindelse. ")
        f.write("Responstider inkluderer helikopter-kørsler, men datasættet indeholder ikke ")
        f.write("oplysning om hvem der var først på skadestedet. Se datakvalitet-note i executive summary.\n\n")

        # Top 10 best
        df_best = pd.read_excel(data_dir / "03_top_10_bedste.xlsx")
        f.write("### 1.2 Top 10 BEDSTE Postnumre\n\n")
        f.write("**Her er ambulancen hurtigst:**\n\n")
        f.write("*Syddanske bycentre dominerer totalt - høj befolkningstæthed og kort afstand til hospitaler.*\n\n")
        f.write("| Rank | Postnummer | Region | Gennemsnit (min) | Antal Ture |\n")
        f.write("|------|------------|--------|------------------|------------|\n")
        for i, row in df_best.head(10).iterrows():
            postal_name = get_postal_code_name(row['Postnummer'])
            f.write(f"| {i+1} | **{postal_name}** | {row['Region']} | ")
            f.write(f"{row['Gennemsnit_minutter']:.1f} | {int(row['Antal_ture']):,} |\n")
        f.write("\n")

        # Add journalistic context with postal code names
        worst_time = df_worst.iloc[0]['Gennemsnit_minutter']
        best_time = df_best.iloc[0]['Gennemsnit_minutter']
        ratio = worst_time / best_time
        worst_name = get_postal_code_name(df_worst.iloc[0]['Postnummer'])
        best_name = get_postal_code_name(df_best.iloc[0]['Postnummer'])

        f.write(f"**Sammenligning:** {worst_name} ({worst_time:.1f} min) er **{ratio:.1f}x langsommere** ")
        f.write(f"end {best_name} ({best_time:.1f} min). ")
        f.write("Rigsrevisionens notat (SR 11/2024) påpeger at de regionale servicemål ")
        f.write("dækker over 'store geografiske forskelle'. Forskellen viser den geografiske forskel ")
        f.write("mellem landdistriker og bycentre.\n\n")

        # Regional comparison
        df_regional = pd.read_excel(data_dir / "04_regional_sammenligning.xlsx")
        f.write("### 1.3 Regional Sammenligning\n\n")
        f.write("**Regional ulighed - alle opfylder servicemål, men med forskellige definitioner:**\n\n")
        f.write("| Region | Gennemsnit (min) | Total Ture | Postnumre |\n")
        f.write("|--------|------------------|------------|-----------|\n")
        for _, row in df_regional.iterrows():
            f.write(f"| **{row['Region']}** | {row['Gennemsnit_minutter']:.1f} | ")
            f.write(f"{int(row['Total_ture']):,} | {int(row['Antal_postnumre'])} |\n")
        f.write("\n")
        f.write("*Regional median beregnes på case-niveau - se Tabel 2.3 (Årlig Udvikling)*\n\n")
        f.write("---\n\n")

    except Exception as e:
        logger.warning(f"Could not load postal code data: {e}")
        f.write("*Postnummer-data ikke tilgængelig*\n\n---\n\n")


def _write_yearly_section(f, output_dir):
    """Write yearly analysis section (NEW!)."""
    f.write("## 📅 DEL 2: ÅRLIG UDVIKLING (2021-2025)\n\n")
    f.write("**Hovedfund:** Stabil udvikling med vedvarende geografisk variation.\n\n")
    f.write("Landsdækkende responstider har været bemærkelsesværdigt stabile 2021-2025. ")
    f.write("Der ses markant geografisk variation ")
    f.write("mellem regioner og postnumre.\n\n")

    try:
        # Files may be in bilag/ subdirectory or root
        bilag_dir = output_dir / "bilag"
        data_dir = bilag_dir if bilag_dir.exists() else output_dir

        # Yearly summary
        df_yearly = pd.read_excel(data_dir / "11_responstid_per_aar_landsdækkende_A.xlsx")
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
        df_pivot = pd.read_excel(data_dir / "13_responstid_pivot_aar_x_region_A.xlsx")
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
        df_regional_summary = pd.read_excel(data_dir / "12_responstid_per_region_samlet_A.xlsx")
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
    f.write("**Hovedfund:** Nat og tidlig morgen langsommere end myldretid.\n\n")
    f.write("Data viser at myldretiden (kl. 16-18) ikke er det langsomste tidspunkt. ")
    f.write("Ambulancer er hurtigst midt på dagen. ")
    f.write("Nattevagter (kl. 02-06) og tidlig morgen (kl. 06:00) ")
    f.write("har responstider op til 28% langsommere end dagen.\n\n")

    # Find all regional temporal files
    regions = ['Nordjylland', 'Hovedstaden', 'Sjælland', 'Midtjylland', 'Syddanmark']

    # Files may be in bilag/ subdirectory or root
    bilag_dir = output_dir / "bilag"
    data_dir = bilag_dir if bilag_dir.exists() else output_dir

    try:
        f.write("**OBS:** Tidsmæssige analyser inkluderer BÅDE A- og B-prioritet kørsler for at vise det fulde billede af ambulanceberedskabets belastning. Dette forklarer hvorfor værdierne er højere end i Del 2 (som kun viser A-prioritet).\n\n")
        f.write("- **A-prioritet:** Livstruende tilfælde (hurtigst respons)\n")
        f.write("- **B-prioritet:** Ikke-livstruende (kan vente længere)\n")
        f.write("- Forskellen mellem A og B vises i Del 4.1\n\n")

        f.write("### 3.1 Tid-på-Døgnet (Rush Hour)\n\n")
        f.write("**Bedste og værste tidspunkt per region (A+B kørsler):**\n\n")
        f.write("| Region | Bedste Time | Min | Værste Time | Min | Variation (%) |\n")
        f.write("|--------|-------------|-----|-------------|-----|---------------|\n")

        for region in regions:
            time_file = data_dir / f"{region}_05_responstid_per_time.xlsx"
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
            month_file = data_dir / f"{region}_06_responstid_per_maaned.xlsx"
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
        f.write("\n")

        f.write("**Sammenfatning:** Sæsonvariation (5-8%) er markant mindre end tid-på-døgnet variation (20-28%).\n\n")
        f.write("---\n\n")

    except Exception as e:
        logger.warning(f"Could not load temporal data: {e}")
        f.write("*Tidsmæssig analyse-data ikke tilgængelig*\n\n---\n\n")


def _write_priority_section(f, output_dir):
    """Write priority analysis section."""
    f.write("## 🏥 DEL 4: SYSTEMANALYSER\n\n")
    f.write("**Hovedfund:** Markant forskel mellem prioritetsniveauer.\n\n")
    f.write("B-prioritet kørsler (ikke-livstruende) har markant længere ventetid end A-prioritet. ")
    f.write("I Hovedstaden er B-prioritet 140% langsommere (21.9 min vs 9.1 min).\n\n")

    try:
        # Files may be in bilag/ subdirectory or root
        bilag_dir = output_dir / "bilag"
        data_dir = bilag_dir if bilag_dir.exists() else output_dir

        # A vs B vs C Priority
        df_priority = pd.read_excel(data_dir / "07_prioritering_ABC.xlsx")

        f.write("### 4.1 A vs B vs C Prioritering\n\n")
        f.write("**Responstider fordelt på prioritetsniveau:**\n\n")
        f.write("| Region | A-prioritet (min) | B-prioritet (min) | B vs A Forskel |\n")
        f.write("|--------|-------------------|-------------------|----------------|\n")

        # Group by region and pivot
        for region in df_priority['Region'].unique():
            df_region = df_priority[df_priority['Region'] == region]
            a_val = df_region[df_region['Hastegrad'] == 'A']['Median_minutter'].values
            b_val = df_region[df_region['Hastegrad'] == 'B']['Median_minutter'].values

            if len(a_val) > 0 and len(b_val) > 0:
                a_val = a_val[0]
                b_val = b_val[0]
                diff_pct = ((b_val - a_val) / a_val) * 100
                f.write(f"| {region} | {a_val:.1f} | {b_val:.1f} | +{diff_pct:.1f}% |\n")
        f.write("\n")

        # Rekvireringskanal
        kanal_file = data_dir / "09_rekvireringskanal.xlsx"
        if kanal_file.exists():
            df_kanal = pd.read_excel(kanal_file)

            # Filter out rows with 0 cases (NaN values)
            df_kanal_valid = df_kanal[df_kanal['Antal_ture'] > 0].copy()

            f.write("### 4.2 Rekvireringskanal (Alle Prioriteter)\n\n")
            f.write("**Responstider fordelt på rekvireringskanal:**\n\n")

            if len(df_kanal_valid) > 0:
                # Get list of regions with data
                regions_with_data = df_kanal_valid['Region'].unique()
                total_cases = df_kanal_valid['Antal_ture'].sum()

                f.write(f"*Data fra {len(regions_with_data)} regioner: {', '.join(sorted(regions_with_data))}*\n")
                f.write(f"*Total kørsler: {int(total_cases):,}*\n\n")

                f.write("| Region | Kanal | Prioritet | Median (min) | Antal Kørsler |\n")
                f.write("|--------|-------|-----------|--------------|---------------|\n")

                # Show top 15 channels (across all regions)
                df_kanal_sorted = df_kanal_valid.sort_values('Antal_ture', ascending=False)
                for _, row in df_kanal_sorted.head(15).iterrows():
                    f.write(f"| {row['Region']} | {row['Rekvireringskanal']} | {row['Hastegrad']} | ")
                    f.write(f"{row['Median_minutter']:.1f} | {int(row['Antal_ture']):,} |\n")
                f.write("\n")
            else:
                f.write("*Rekvireringskanal-data ikke tilgængelig for nogen regioner*\n\n")

        f.write("---\n\n")

    except Exception as e:
        logger.warning(f"Could not load priority data: {e}")
        f.write("*System analyse-data ikke tilgængelig*\n\n---\n\n")


def _write_b_priority_section(f, output_dir):
    """Write B-priority deep analysis section."""
    f.write("## 🔍 DEL 5: B-PRIORITET DYB-ANALYSE\n\n")
    f.write("**Hovedfund:** Større variation i B-prioritet end A-prioritet.\n\n")
    f.write("Mens A-prioritet (livstruende) prioriteres højest, viser B-prioritet analysen ")
    f.write("markante forskelle i hvordan ikke-livstruende patienter behandles. ")
    f.write("B-prioritet viser større variation end A-prioritet - både geografisk, tidsmæssigt og over tid.\n\n")

    try:
        # Files may be in bilag/ subdirectory or root
        bilag_dir = output_dir / "bilag"
        data_dir = bilag_dir if bilag_dir.exists() else output_dir

        # 5.1: Geographic hotspots
        b_postal_file = data_dir / "14_B_prioritet_per_postnummer.xlsx"
        b_worst_file = data_dir / "15_B_top_10_værste_postnumre.xlsx"

        if b_postal_file.exists() and b_worst_file.exists():
            df_b_worst = pd.read_excel(b_worst_file)

            f.write("### 5.1 Geografiske Hotspots - B-Prioritet Postnumre\n\n")
            f.write("**De 10 værste postnumre for B-prioritet kørsler:**\n\n")
            f.write("| Placering | Postnummer | Navn | Median (min) | Antal B-Kørsler | Region |\n")
            f.write("|-----------|------------|------|--------------|-----------------|--------|\n")

            for idx, row in df_b_worst.iterrows():
                postal_name = get_postal_code_name(row['Postnummer'])
                f.write(f"| {idx+1} | {row['Postnummer']} | {postal_name} | {row['Median_minutter']:.1f} | ")
                f.write(f"{int(row['Antal_ture']):,} | {row['Region']} |\n")

            f.write("\n**Fund:** B-prioritet viser større geografisk variation end A-prioritet. ")
            f.write(f"Værste postnummer ({df_b_worst.iloc[0]['Postnummer']}) har {df_b_worst.iloc[0]['Median_minutter']:.1f} min ")
            f.write("median responstid for ikke-livstruende tilfælde.\n\n")

        # 5.2: Temporal patterns
        b_temporal_file = data_dir / "B_TEMPORAL_SAMMENFATNING.txt"
        if b_temporal_file.exists():
            f.write("### 5.2 Tidsmæssige Mønstre - B-Prioritet\n\n")
            f.write("**Hvordan påvirkes B-prioritet af tidspunkt på døgnet og årstid?**\n\n")

            # Read temporal findings
            with open(b_temporal_file, 'r', encoding='utf-8') as temp_f:
                temporal_content = temp_f.read()

            # Extract key stats (simplified - just include summary)
            f.write("**Sammenfatning:** B-prioritet patienter oplever større tidsmæssig variation end A-prioritet.\n\n")

            # Show sample data for one region if available
            hovedstaden_temporal = data_dir / "Hovedstaden_16_B_responstid_per_time.xlsx"
            if hovedstaden_temporal.exists():
                df_h_temporal = pd.read_excel(hovedstaden_temporal)
                worst_hour = df_h_temporal.loc[df_h_temporal['Median_minutter'].idxmax()]
                best_hour = df_h_temporal.loc[df_h_temporal['Median_minutter'].idxmin()]

                f.write(f"**Eksempel - Hovedstaden B-prioritet:**\n")
                f.write(f"- Værste time: kl. {int(worst_hour['Time']):02d} ({worst_hour['Median_minutter']:.1f} min median)\n")
                f.write(f"- Bedste time: kl. {int(best_hour['Time']):02d} ({best_hour['Median_minutter']:.1f} min median)\n")
                variation_pct = ((worst_hour['Median_minutter'] - best_hour['Median_minutter']) / best_hour['Median_minutter']) * 100
                f.write(f"- Variation: {variation_pct:.1f}%\n\n")

        # 5.3: Yearly trends
        b_yearly_file = data_dir / "18_B_responstid_per_aar.xlsx"
        b_trend_file = data_dir / "19_B_årlig_udvikling.xlsx"

        if b_trend_file.exists():
            df_b_trend = pd.read_excel(b_trend_file, sheet_name='Udvikling')

            f.write("### 5.3 Årlig Udvikling - B-Prioritet 2021-2025\n\n")
            f.write("**Er B-prioritet blevet bedre eller værre over tid?**\n\n")

            f.write("| Region | 2021 Median (min) | 2025 Median (min) | Ændring | % Ændring |\n")
            f.write("|--------|-------------------|-------------------|---------|------------|\n")

            for _, row in df_b_trend.iterrows():
                region_display = "**" + row['Region'] + "**" if row['Region'] == 'LANDSDÆKKENDE' else row['Region']
                change_symbol = "+" if row['Ændring_procent'] > 0 else ""
                f.write(f"| {region_display} | {row['Median_start']:.1f} | {row['Median_slut']:.1f} | ")
                f.write(f"{change_symbol}{row['Ændring_minutter']:.1f} min | ")
                f.write(f"{change_symbol}{row['Ændring_procent']:.1f}% |\n")

            f.write("\n")

            # Analysis
            national_trend = df_b_trend[df_b_trend['Region'] == 'LANDSDÆKKENDE'].iloc[0]
            if abs(national_trend['Ændring_procent']) < 5:
                f.write("**Fund:** B-prioritet har været relativt stabil på landsplan over perioden. ")
            elif national_trend['Ændring_procent'] > 5:
                f.write(f"**Fund:** B-prioritet er blevet {national_trend['Ændring_procent']:.1f}% langsommere over perioden. ")
            else:
                f.write(f"**Fund:** B-prioritet er blevet {abs(national_trend['Ændring_procent']):.1f}% hurtigere over perioden. ")

            f.write("\n\n")

        # 5.4: B→A escalations
        b_escalation_file = data_dir / "20_B_til_A_omlægning.xlsx"
        if b_escalation_file.exists():
            df_escalation = pd.read_excel(b_escalation_file, sheet_name='Statistik')
            df_summary = pd.read_excel(b_escalation_file, sheet_name='Sammenfatning')

            f.write("### 5.4 B→A Prioritets-Omlægninger (Hovedstaden)\n\n")
            f.write("**Hvor ofte fejlvurderes B-kørsler som skulle have været A-prioritet?**\n\n")

            escalation_rate = df_summary[df_summary['Metrik'] == 'Opgraderings-rate (%)']['Værdi'].values[0]
            extra_delay = df_summary[df_summary['Metrik'] == 'Ekstra forsinkelse (min)']['Værdi'].values[0]

            f.write(f"**Opgraderings-rate:** {escalation_rate:.1f}% af alle B-kørsler bliver opgraderet til A undervejs.\n\n")

            f.write("| Kategori | Antal Kørsler | Median Responstid (min) |\n")
            f.write("|----------|---------------|-------------------------|\n")

            for _, row in df_escalation.iterrows():
                f.write(f"| {row['Kategori']} | {int(row['Antal_ture']):,} | {row['Median_minutter']:.1f} |\n")

            f.write("\n")
            f.write(f"**Fund:** Patienter der starter som B-prioritet men opgraderes til A oplever ")
            f.write(f"{extra_delay:+.1f} min ekstra forsinkelse sammenlignet med korrekt A-vurdering fra start.\n\n")

        f.write("---\n\n")

    except Exception as e:
        logger.warning(f"Could not load B-priority data: {e}")
        f.write("*B-prioritet dyb-analyse data ikke tilgængelig*\n\n---\n\n")


def _write_alarm_time_section(f, output_dir):
    """Write alarm time (dispatch delay) analysis section."""
    f.write("## ⏱️ DEL 6: ALARMTID\n\n")
    f.write("**Hovedfund:** Ca. 22% af ventetid sker før ambulancen sendes afsted.\n\n")

    f.write("**Hvad er alarmtid?** Tiden fra borgeren ringer 112 til ambulancen bliver sendt afsted. ")
    f.write("Dette inkluderer triage (sundhedsfaglig vurdering), klassificering af hastegrad, og disponering ")
    f.write("(at finde og alarmere den rette ambulance).\n\n")

    f.write("Data fra Nordjylland og Syddanmark viser at ca. 22% af total ventetid (~2 minutter median) ")
    f.write("sker i denne fase. Dette fremgår ikke af regionernes officielle servicemål.\n\n")

    try:
        # Files may be in bilag/ subdirectory or root
        bilag_dir = output_dir / "bilag"
        data_dir = bilag_dir if bilag_dir.exists() else output_dir

        dispatch_file = data_dir / "20_dispatch_delay_vs_travel.xlsx"
        if dispatch_file.exists():
            df_dispatch = pd.read_excel(dispatch_file)

            f.write("### 6.1 Opdeling af Total Ventetid\n\n")
            f.write("**Geografisk begrænsning:** Regionerne kan måle alarmtid, men vi fandt kun brugbare datetime-data ")
            f.write("i 2 ud af 5 regioner (Nordjylland + Syddanmark). Hovedstaden, Sjælland og Midtjylland bruger ")
            f.write("time-only format, hvilket ikke kan beregne tidsforskel hen over midnat. Derfor kan deres ")
            f.write("alarmtid ikke analyseres med de tilgængelige data.\n\n")

            f.write("| Region | Prioritet | Analyseret | Total Ventetid (median) | Alarmtid | Rejsetid |\n")
            f.write("|--------|-----------|------------|-------------------------|----------|----------|\n")

            for _, row in df_dispatch.iterrows():
                region = row['Region']
                priority = row['Priority']
                valid_cases = int(row['Valid_Cases'])
                total_wait = row['Total_Wait_Median']
                dispatch_delay = row['Dispatch_Delay_Median']
                travel_time = row['Travel_Time_Median']
                dispatch_pct = row['Dispatch_Pct']
                travel_pct = row['Travel_Pct']

                f.write(f"| {region} | {priority} | {valid_cases:,} | {total_wait:.1f} min | ")
                f.write(f"{dispatch_delay:.1f} min ({dispatch_pct:.0f}%) | ")
                f.write(f"{travel_time:.1f} min ({travel_pct:.0f}%) |\n")

            f.write("\n")

            # Key findings
            avg_dispatch_pct_a = df_dispatch[df_dispatch['Priority'] == 'A']['Dispatch_Pct'].mean()
            avg_dispatch_pct_b = df_dispatch[df_dispatch['Priority'] == 'B']['Dispatch_Pct'].mean()

            f.write("### 6.2 Vigtigste Fund\n\n")
            f.write(f"**A-prioritet (livstruende):**\n")
            f.write(f"- Alarmtid udgør **ca. {avg_dispatch_pct_a:.0f}%** af total ventetid\n")
            f.write(f"- Median alarmtid: ~2.0-2.2 minutter\n")
            f.write(f"- Median rejsetid: ~7.0-7.6 minutter\n\n")

            f.write(f"**B-prioritet (ikke-livstruende):**\n")
            f.write(f"- Alarmtid udgør **ca. {avg_dispatch_pct_b:.0f}%** af total ventetid\n")
            f.write(f"- Median alarmtid: ~3.0 minutter\n")
            f.write(f"- Median rejsetid: ~11.0-13.6 minutter\n\n")

            f.write("**Rigsrevisionens notat (SR 11/2024):** Regionernes servicemål medregner ikke ")
            f.write("denne alarmtid. Den officielle 'responstid' starter først når ambulancen disponeres ")
            f.write("(sendes afsted), ikke når borgeren ringer 112.\n\n")

        else:
            f.write("*Alarmtid-data ikke tilgængelig*\n\n")

        f.write("---\n\n")

    except Exception as e:
        logger.warning(f"Could not load alarm time data: {e}")
        f.write("*Alarmtid analyse-data ikke tilgængelig*\n\n---\n\n")


def _write_helicopter_section(f, output_dir):
    """Write helicopter (HEMS) analysis section."""
    f.write("## 🚁 DEL 7: HELIKOPTER (HEMS) ANALYSE\n\n")
    f.write("**Hovedfund:** Helikoptere supplerer ambulanceberedskabet med gennemsnitlig responstid på 26.3 minutter.\n\n")

    f.write("**VIGTIGT:** Akutlægehelikoptere er *supplerende* beredskab, ikke primær responder. ")
    f.write("Data dækker 10,376 missioner (juli 2021 - juni 2025) hvor helikopter var fremme ved patient ")
    f.write("(ekskl. interhospitale transporter). Helikoptere disponeres primært til hastegrad A, ")
    f.write("men også til øer og yderområder uanset hastegrad.\n\n")

    try:
        # Files may be in bilag/ subdirectory or root
        bilag_dir = output_dir / "bilag"
        data_dir = bilag_dir if bilag_dir.exists() else output_dir

        # Check if helicopter analysis files exist
        heli_findings_file = data_dir / "HELIKOPTER_FUND.txt"
        heli_regional_file = data_dir / "helikopter_regional_sammenligning.xlsx"
        heli_national_file = data_dir / "helikopter_national_oversigt.xlsx"

        if not heli_findings_file.exists() and not heli_regional_file.exists():
            f.write("*Helikopter-data ikke tilgængelig i denne analyse*\n\n---\n\n")
            logger.warning("Helicopter data files not found")
            return

        # National overview
        if heli_national_file.exists():
            df_national = pd.read_excel(heli_national_file, sheet_name='National Stats')

            f.write("### 7.1 National Oversigt\n\n")
            f.write("**Responstidskomponenter (alarm → arrival):**\n\n")
            f.write("| Komponent | Gennemsnit | Median | 90. Percentil |\n")
            f.write("|-----------|------------|--------|---------------|\n")

            for _, row in df_national.iterrows():
                f.write(f"| {row['Metric']} | {row['Gennemsnit_min']:.1f} min | ")
                f.write(f"{row['Median_min']:.1f} min | {row['Percentil_90']:.1f} min |\n")
            f.write("\n")

            # Extract specific values for narrative
            dispatch_delay = df_national[df_national['Metric'] == 'Dispatch Delay']['Gennemsnit_min'].values[0]
            total_response = df_national[df_national['Metric'] == 'Total Response']['Gennemsnit_min'].values[0]
            dispatch_pct = (dispatch_delay / total_response) * 100

            f.write(f"**Dispatch delay** (alarm → airborne): {dispatch_delay:.1f} min ({dispatch_pct:.0f}% af total tid)  \n")
            f.write(f"**Sammenligning:** Helikopter dispatch delay er ~3.5x længere end ambulance (~2 min)\n\n")

        # Regional breakdown
        if heli_regional_file.exists():
            df_regional = pd.read_excel(heli_regional_file)

            f.write("### 7.2 Regional Fordeling\n\n")
            f.write("**Responstider og aktivitet per region:**\n\n")
            f.write("| Region | Gns. Responstid | Median | Antal Cases | % af Total |\n")
            f.write("|--------|-----------------|--------|-------------|------------|\n")

            for _, row in df_regional.iterrows():
                f.write(f"| {row['Region']} | {row['Total_Response_Gennemsnit']:.1f} min | ")
                f.write(f"{row['Total_Response_Median']:.1f} min | {row['Antal_Cases']:.0f} | ")
                f.write(f"{row['Procent_af_Total']:.1f}% |\n")
            f.write("\n")

            # Highlight extremes
            fastest = df_regional.iloc[0]
            slowest = df_regional.iloc[-1]

            f.write(f"**Variation:** {slowest['Region']} har {slowest['Total_Response_Gennemsnit']:.1f} min ")
            f.write(f"vs. {fastest['Region']} {fastest['Total_Response_Gennemsnit']:.1f} min ")
            f.write(f"({(slowest['Total_Response_Gennemsnit']/fastest['Total_Response_Gennemsnit']-1)*100:.0f}% længere)\n\n")

            f.write(f"**FUND:** {slowest['Region']} har kun {slowest['Antal_Cases']:.0f} cases ({slowest['Procent_af_Total']:.1f}%), ")
            f.write(f"mens andre regioner har 2,200-2,800 cases. Dette tyder på at helikopter bruges meget sjældent i Hovedstaden.\n\n")

        # Key findings from text file
        if heli_findings_file.exists():
            with open(heli_findings_file, 'r', encoding='utf-8') as hf:
                findings_text = hf.read()

                # Extract seasonal finding
                if "SÆSONMÆSSIGHED" in findings_text:
                    f.write("### 7.3 Sæsonmæssighed\n\n")
                    f.write("**Helikopteraktivitet varierer kraftigt over året:**\n\n")

                    # Look for the percentage in findings
                    import re
                    match = re.search(r'(\d+)% flere cases i travleste måned', findings_text)
                    if match:
                        pct = match.group(1)
                        f.write(f"- Sommermåneder (juni-august): +{pct}% flere udrykninger\n")
                        f.write("- Højeste aktivitet: Juli (primært trafikulykker og fritidsulykker)\n")
                        f.write("- Laveste aktivitet: December\n\n")

        f.write("### 7.4 Anvendelse i Analyse\n\n")
        f.write("**Helikopterdata bruges til:**\n\n")
        f.write("1. **Kontekst for \"værste postnumre\"** - Ø-samfund (Fur, Fejø) får primært helikopter\n")
        f.write("2. **Dispatch delay sammenligning** - Helikopter 6.9 min vs. ambulance ~2 min\n")
        f.write("3. **Regional variation** - Forklarer hvorfor nogle regioner virker \"langsommere\"\n")
        f.write("4. **Sæsonmønstre** - Sommeren presser både helikopter og ambulance\n\n")

        f.write("**ADVARSEL:** Helikopter-responstider må IKKE sammenlignes direkte med ambulance-responstider. ")
        f.write("Helikoptere bruges til høj-kompleksitet cases (traumer, hjertestop) og lange afstande. ")
        f.write("De er *supplement*, ikke alternativ til ambulancer.\n\n")

        f.write("**Datakilde:** Sundhedsstyrelsen - Nationale helikopterdata (1. juli 2021 - 30. juni 2025)  \n")
        f.write("*Driftsdata - ikke kvalitetssikret. Enkelte fejlregistreringer er rensede fra analyse.*\n\n")

        f.write("---\n\n")

    except Exception as e:
        logger.warning(f"Could not load helicopter data: {e}")
        f.write("*Helikopter analyse-data ikke tilgængelig*\n\n---\n\n")


def _write_vehicle_type_section(f, output_dir):
    """Write vehicle type analysis section."""
    f.write("## 🚑 DEL 8: KØRETØJSTYPE-ANALYSE\n\n")
    f.write("**Hovedfund:** Ambulancer dominerer med 93% af alle akutte udkald, ")
    f.write("men lægebiler har længere responstider end standardambulancer.\n\n")

    try:
        # Files may be in bilag/ subdirectory or root
        bilag_dir = output_dir / "bilag"
        data_dir = bilag_dir if bilag_dir.exists() else output_dir

        # Check if vehicle type analysis files exist
        national_file = data_dir / "vehicle_type_national_distribution.xlsx"
        regional_file = data_dir / "vehicle_type_regional_variation.xlsx"
        priority_file = data_dir / "vehicle_type_priority_differences.xlsx"

        if not national_file.exists():
            f.write("*Køretøjstype-data ikke tilgængelig i denne analyse*\n\n---\n\n")
            logger.warning("Vehicle type data files not found")
            return

        # National distribution
        df_national = pd.read_excel(national_file)

        f.write("### 8.1 National Fordeling (Landsdækkende)\n\n")
        f.write("**Køretøjstyper ved A+B prioritet (4 regioner):**\n\n")
        f.write("| Køretøjstype | Antal Cases | % af Total | Median Responstid |\n")
        f.write("|--------------|-------------|------------|-------------------|\n")

        for _, row in df_national.iterrows():
            f.write(f"| {row['Vehicle_Type']} | {row['Total_Cases']:,.0f} | ")
            f.write(f"{row['Percentage']:.1f}% | {row['Median_Response']:.1f} min |\n")
        f.write("\n")

        # Extract key stats
        ambulance_row = df_national[df_national['Vehicle_Type'] == 'Ambulance'].iloc[0]
        laegebil_row = df_national[df_national['Vehicle_Type'] == 'Lægebil'].iloc[0]

        f.write(f"**Nøgletal:**\n")
        f.write(f"- Ambulance er den absolut dominerende enhedstype ({ambulance_row['Percentage']:.1f}%)\n")
        f.write(f"- Lægebiler bruges i {laegebil_row['Percentage']:.1f}% af tilfældene ({laegebil_row['Total_Cases']:,.0f} cases)\n")
        f.write(f"- Lægebiler har **{laegebil_row['Median_Response'] - ambulance_row['Median_Response']:.1f} min længere** ")
        f.write(f"median responstid end standardambulancer ({laegebil_row['Median_Response']:.1f} vs {ambulance_row['Median_Response']:.1f} min)\n\n")

        # Regional variation (if available)
        if regional_file.exists():
            df_regional = pd.read_excel(regional_file)

            f.write("### 8.2 Regional Variation i Køretøjsbrug\n\n")
            f.write("**Procentvis fordeling af køretøjstyper per region:**\n\n")
            f.write("| Region | Ambulance | Lægebil | Paramediciner | Andre |\n")
            f.write("|--------|-----------|---------|---------------|-------|\n")

            for _, row in df_regional.iterrows():
                f.write(f"| {row['Region']} | {row['Ambulance_Pct']:.1f}% | ")
                f.write(f"{row['Laegebil_Pct']:.1f}% | {row['Paramediciner_Pct']:.1f}% | ")
                f.write(f"{row['Andre_Pct']:.1f}% |\n")
            f.write("\n")

            # Find extremes
            max_laegebil_region = df_regional.loc[df_regional['Laegebil_Pct'].idxmax()]
            min_laegebil_region = df_regional.loc[df_regional['Laegebil_Pct'].idxmin()]

            f.write(f"**Regional forskel:** {max_laegebil_region['Region']} bruger mest lægebil ")
            f.write(f"({max_laegebil_region['Laegebil_Pct']:.1f}%), mens {min_laegebil_region['Region']} ")
            f.write(f"bruger mindst ({min_laegebil_region['Laegebil_Pct']:.1f}%)\n\n")

        # Priority differences (if available)
        if priority_file.exists():
            df_priority = pd.read_excel(priority_file)

            f.write("### 8.3 Køretøjstype per Prioritet\n\n")
            f.write("**Responstider fordelt på køretøjstype og prioritet:**\n\n")
            f.write("| Prioritet | Køretøjstype | Median Responstid | Antal Cases |\n")
            f.write("|-----------|--------------|-------------------|-------------|\n")

            for _, row in df_priority.iterrows():
                f.write(f"| {row['Priority']} | {row['Vehicle_Type']} | ")
                f.write(f"{row['Median_Response']:.1f} min | {row['Total_Cases']:,.0f} |\n")
            f.write("\n")

            # A vs B comparison for Ambulance
            amb_a = df_priority[(df_priority['Vehicle_Type'] == 'Ambulance') & (df_priority['Priority'] == 'A')]
            amb_b = df_priority[(df_priority['Vehicle_Type'] == 'Ambulance') & (df_priority['Priority'] == 'B')]

            if not amb_a.empty and not amb_b.empty:
                diff = amb_b.iloc[0]['Median_Response'] - amb_a.iloc[0]['Median_Response']
                pct_diff = (diff / amb_a.iloc[0]['Median_Response']) * 100
                f.write(f"**Prioritetsforskel:** Ambulancer til B-prioritet har {diff:.1f} min længere ")
                f.write(f"responstid end A-prioritet (+{pct_diff:.0f}%)\n\n")

        f.write("**Datadækning:** Analysen dækker 4 ud af 5 regioner (Sjælland mangler køretøjstype-data)\n\n")
        f.write("---\n\n")

    except Exception as e:
        logger.warning(f"Could not load vehicle type data: {e}")
        f.write("*Køretøjstype analyse-data ikke tilgængelig*\n\n---\n\n")


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

    f.write("*Alarmtid-analyse (Nordjylland + Syddanmark):*\n")
    f.write("- `20_dispatch_delay_vs_travel.xlsx` - Opdeling: alarmtid vs. rejsetid\n")
    f.write("- `20_DISPATCH_DELAY_FUND.txt` - Key findings\n\n")

    f.write("*Helikopter-analyse (nationale data):*\n")
    f.write("- `helikopter_national_oversigt.xlsx` - National statistik\n")
    f.write("- `helikopter_regional_sammenligning.xlsx` - Regional breakdown\n")
    f.write("- `helikopter_base_performance.xlsx` - Base performance\n")
    f.write("- `helikopter_årlig_udvikling.xlsx` - Årlige trends\n")
    f.write("- `helikopter_månedlig_sæsonmønstre.xlsx` - Sæsonvariation\n")
    f.write("- `helikopter_postnummer_dækning.xlsx` - Postnummer dækning\n")
    f.write("- `HELIKOPTER_FUND.txt` - Key findings\n\n")

    f.write("*Køretøjstype-analyse (4 regioner):*\n")
    f.write("- `vehicle_type_national_distribution.xlsx` - National fordeling\n")
    f.write("- `vehicle_type_regional_variation.xlsx` - Regional variation\n")
    f.write("- `vehicle_type_priority_differences.xlsx` - A vs B prioritet\n")
    f.write("- `vehicle_type_temporal_patterns.xlsx` - Tidsmæssige mønstre\n")
    f.write("- `VEHICLE_TYPE_SUMMARY.txt` - Key findings\n")
    f.write("- `DATAWRAPPER_vehicle_type.csv` - Visualization data\n\n")

    f.write("---\n\n")


def _write_footer(f, output_dir):
    """Write report footer with metadata."""
    f.write("## 📋 METODE OG DATAGRUNDLAG\n\n")

    f.write("**Datakilder:**\n")
    f.write("- Ambulance-data fra alle 5 danske regioner (2021-2025)\n")
    f.write("- Total: ~2 millioner individuelle ambulance-kørsler\n")
    f.write("- Analyseret: 875,000+ A-prioritet + 668,000+ B-prioritet\n\n")

    # NOTE: Reference to alarm time analysis (detailed coverage in DEL 6)
    f.write("**OBS:** Vores analyse fokuserer primært på den officielle responstid (fra disponering til ankomst). ")
    f.write("For analyse af den 'skjulte' alarmtid før ambulancen sendes afsted, se **DEL 6: ALARMTID**.\n\n")

    f.write("---\n\n")
    f.write("**Hvad vi har gjort med rådata:**\n\n")

    f.write("1. **Filtrering efter formål:**\n")
    f.write("   - **Del 1-2 (Postnummer, Årlig):** Kun A-prioritet (livstruende)\n")
    f.write("   - **Del 3 (Tidsmæssig):** A+B prioritet (viser fuld belastning)\n")
    f.write("   - **Del 4 (Prioritering):** Sammenligner A vs B direkte\n\n")

    f.write("2. **Datarensning:** Fjernet kørsler med manglende responstid eller tidsstempler\n\n")

    f.write("3. **Beregningsmetode:**\n")
    f.write("   - **Gennemsnit** i Top 10 lister (viser fuld variation)\n")
    f.write("   - **Median** i regionale/tidsmæssige sammenligninger (robust mod outliers)\n\n")

    f.write("4. **Validering:** Minimum 50 ture for Top 10 postnumre\n\n")

    f.write("**Hvorfor forskellige datasæt?**\n")
    f.write("- A-prioritet alene giver det mest retvisende billede af \"worst case\" respons\n")
    f.write("- A+B sammen viser systemets samlede belastning og prioritering\n")
    f.write("- Sammenligning af A vs B viser hvor meget B-patienter nedprioriteres\n\n")

    f.write("**Teknisk note:** Regional median i Tabel 2.3 er beregnet fra individuelle kørsler (statistisk korrekt). ")
    f.write("Postnummer-aggregering i Tabel 1.3 bruger gennemsnit på postnummer-niveau.\n\n")

    f.write("---\n\n")
    f.write(f"**RAPPORT GENERERET: {datetime.now().strftime('%d. %B %Y kl. %H:%M')}**\n\n")
    f.write("*Genereret automatisk af Ambulance Pipeline*\n\n")

    # GitHub repository and attribution
    f.write("---\n\n")
    f.write("**Kildekode og dokumentation:** https://github.com/cykelsmed/ambulance_pipeline\n\n")
    f.write("**Undersøgelsen er lavet af:**  \n")
    f.write("Kaas og Mulvad Research / Adam Hvidt  \n")
    f.write("Email: adam@km24  \n")
    f.write("Telefon: 26366414\n")


def generate_consolidated_summary(output_dir):
    """Generate consolidated temporal summary (legacy compatibility).

    This function is kept for backward compatibility but now delegates
    to the main master findings report generator.
    """
    logger.info("Generating consolidated temporal summary...")
    return generate_master_findings_report(output_dir)


def generate_master_findings_pdf(output_dir):
    """Generate professional HTML and PDF versions of the master findings report.

    Converts the Markdown master findings report to:
    1. HTML file using Pandoc (with TOC and professional styling)
    2. PDF file using Chrome headless to convert HTML → PDF

    The PDF is generated automatically if Chrome is installed on the system.
    If Chrome is not found, only HTML is generated.

    Args:
        output_dir: Path to output directory containing the markdown report

    Returns:
        Path to generated PDF file (or HTML file if PDF generation fails)
    """
    logger.info("Generating HTML and PDF versions of master findings report...")

    output_dir = Path(output_dir)
    md_file = output_dir / "MASTER_FINDINGS_RAPPORT.md"
    html_file = output_dir / "MASTER_FINDINGS_RAPPORT.html"
    pdf_file = output_dir / "MASTER_FINDINGS_RAPPORT.pdf"
    css_file = Path(__file__).parent / "report_styles.css"

    try:
        # Check if markdown file exists
        if not md_file.exists():
            logger.error(f"Markdown report not found: {md_file}")
            return None

        # Build pandoc command for HTML output with professional styling
        pandoc_cmd = [
            "pandoc",
            str(md_file),
            "-o", str(html_file),
            "--standalone",  # Generate complete HTML document
            "--toc",  # Generate table of contents
            "--toc-depth=2",  # TOC depth (h1 and h2 only)
            "--metadata", "title=Ambulance Responstidsanalyse - TV2",
        ]

        # Add CSS if available
        if css_file.exists():
            pandoc_cmd.extend(["-c", str(css_file)])

        # Run pandoc command for HTML
        logger.debug(f"Running pandoc command: {' '.join(pandoc_cmd)}")
        result = subprocess.run(
            pandoc_cmd,
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode != 0:
            logger.error(f"Pandoc command failed with code {result.returncode}")
            logger.error(f"Pandoc stderr: {result.stderr}")
            return None

        # Check if HTML was created
        if not html_file.exists():
            logger.error("HTML file was not created")
            return None

        # Get file size for logging
        file_size_kb = html_file.stat().st_size / 1024

        logger.info(f"✓ HTML report generated: {html_file}")
        logger.info(f"  File size: {file_size_kb:.1f} KB")

        # Try to generate PDF using Chrome headless (best effort, don't fail if not available)
        try:
            # Check for Chrome installation
            chrome_paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Chromium.app/Contents/MacOS/Chromium",
                "google-chrome",
                "chromium",
                "chrome"
            ]

            chrome_executable = None
            for chrome_path in chrome_paths:
                if Path(chrome_path).exists() or subprocess.run(
                    ["which", chrome_path],
                    capture_output=True,
                    check=False
                ).returncode == 0:
                    chrome_executable = chrome_path
                    break

            if chrome_executable:
                # Use Chrome headless to convert HTML to PDF
                html_file_absolute = html_file.resolve()
                pdf_cmd = [
                    chrome_executable,
                    "--headless",
                    "--disable-gpu",
                    f"--print-to-pdf={pdf_file}",
                    f"file://{html_file_absolute}"
                ]

                pdf_result = subprocess.run(
                    pdf_cmd,
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=30
                )

                if pdf_result.returncode == 0 and pdf_file.exists():
                    pdf_size_kb = pdf_file.stat().st_size / 1024
                    logger.info(f"✓ PDF also generated: {pdf_file} ({pdf_size_kb:.1f} KB)")
                    return pdf_file
                else:
                    logger.warning(f"Chrome PDF generation failed: {pdf_result.stderr}")
            else:
                logger.info("Chrome not found - PDF not generated (HTML available)")
        except Exception as e:
            logger.warning(f"PDF generation failed: {e}")

        return html_file

    except FileNotFoundError:
        logger.error("Pandoc not found. Please install pandoc: brew install pandoc")
        return None
    except Exception as e:
        logger.error(f"Failed to generate report: {e}", exc_info=True)
        return None
