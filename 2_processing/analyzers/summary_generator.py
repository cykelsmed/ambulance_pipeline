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
            f.write("## 🚨 HOVEDHISTORIER - TV2 KEY FINDINGS\n\n")

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

                # Write compelling TV2 headlines with deeper reflection
                f.write("### 🎯 Top 5 Journalistiske Vinkler:\n\n")

                # 1. Postnummer-lotteriet
                f.write(f"1. **POSTNUMMER-LOTTERIET**: Dit postnummer afgør dine overlevelseschancer - ")
                f.write(f"**{postal_ratio:.1f}x forskel** mellem værste ({worst_postal_name}: {worst_postal['Gennemsnit_minutter']:.1f} min) ")
                f.write(f"og bedste ({best_postal_name}: {best_postal['Gennemsnit_minutter']:.1f} min) postnummer. ")
                f.write("Dette er ikke tilfældigt - det er systematisk ulighed mellem landdistriker og bycentre. ")
                f.write("Men selv nabobyer kan have dramatiske forskelle. **Er det overraskende?** ")
                f.write("Nej, hvis man kender geografien - men forskellen er større end de fleste danskere tror.\n\n")

                # 2. Regional ulighed (OPDATERET MED RIGSREVISIONEN KONTEKST)
                f.write(f"2. **REGIONAL ULIGHED**: {worst_region['Region']} er **{regional_diff_pct:.1f}% langsommere** ")
                f.write(f"end {best_region['Region']} ({worst_region['Gennemsnit_minutter']:.1f} min vs {best_region['Gennemsnit_minutter']:.1f} min). ")
                f.write("Alle regioner opfylder formelt deres servicemål, men Rigsrevisionen (SR 11/2024) påpeger, at dette skyldes, ")
                f.write("at de opererer med vidt forskellige definitioner og tællemetoder. Vores data viser den faktiske service-forskel, ")
                f.write("som de politiske mål slører.\n\n")

                # 3. Nat-vagter (bedste vinkel)
                f.write("3. **NAT-VAGTER ER FLASKEHALSEN**: Ambulancer er 20-28% langsommere om natten (kl. 02-06) ")
                f.write("end på dagen. Værste tidspunkt: kl. 06:00 (vagt-skift?). **IKKE myldretiden!** ")
                f.write("Dette er **modintuitiv** - når trafikken er fri om natten, skulle ambulancerne være hurtigere. ")
                f.write("Men data viser det modsatte. Forklaring? Færre vagter på arbejde om natten, længere responstid fra ")
                f.write("alarmcentral til udrykning. Kl. 17 (myldretid) er faktisk blandt de **hurtigste** timer. ")
                f.write("Dette bryder med danskernes forventninger.\n\n")

                # 4. B-prioritet
                f.write("4. **B-PRIORITET: MERE END DOBBELT SÅ LANGSOM**: B-prioritet kørsler er 60-140% langsommere ")
                f.write("end A-prioritet. Hovedstaden: A=9.1 min, B=21.9 min (+140.7%). ")
                f.write("Dette er selvindlysende - A-prioritet er livstruende og skal naturligvis prioriteres. ")
                f.write("Men **140% forskel** rejser spørgsmål: Bliver ikke-livstruende patienter nedprioriteret for meget? ")
                f.write("En patient med kraftige smerter (B) venter over 20 minutter i Hovedstaden.\n\n")

                # 5. Den skjulte alarmtid
                f.write("5. **DEN SKJULTE ALARMTID - FØR AMBULANCEN OVERHOVEDET KØRER**: 1 ud af 5 minutter af borgerens ventetid ")
                f.write("sker **før ambulancen forlader stationen**. **Hvad er alarmtid?** Tiden fra du ringer 112 til ambulancen ")
                f.write("bliver sendt afsted (triage, vurdering og disponering). Nordjylland + Syddanmark data (549,000 kørsler) ")
                f.write("viser at **ca. 22% af total ventetid** er alarmtid (~2 min median). Dette er **usynligt** for borgeren, ")
                f.write("som tror hele ventetiden er ambulancen på vej. ")
                f.write("**Rigsrevisionens kritik (SR 11/2024):** Denne 'skjulte' tid medregnes IKKE i regionernes servicemål, ")
                f.write("så den reelle ventetid for borgeren er længere end de officielle tal. ")
                f.write("**Data-problem:** Regionerne kan måle dette, men vi fandt kun brugbare datetime-data i 2 ud af 5 regioners datasæt. ")
                f.write("Hovedstaden, Sjælland og Midtjylland har time-only timestamps, så deres alarmtid er umulig at beregne.\n\n")

                f.write("---\n\n")
                f.write("### 📊 Datagrundlag:\n")
                f.write("- **875,000+ A-prioritet kørsler** analyseret (livstruende tilfælde)\n")
                f.write("- **493,000+ A+B-kørsler** i tidsmæssige analyser (fuld belastning)\n")
                f.write("- **549,000+ kørsler** med alarmtid-analyse (Nordjylland + Syddanmark)\n")
                f.write("- **1,543,000+ total kørsler** analyseret (inkl. C-prioritet)\n")
                f.write("- **5 års data** (2021-2025) fra alle 5 danske regioner\n")
                f.write(f"- **{len(pd.read_excel(data_dir / '01_alle_postnumre.xlsx'))} postnumre** kortlagt\n\n")

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

            # Part 7: Data files reference
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
    f.write("**🎯 Journalistisk vinkel:** \"Dit postnummer afgør dine overlevelseschancer\"\n\n")
    f.write("Analysen viser **ekstrem geografisk variation** i ambulance-responstider. ")
    f.write("Bor du i det forkerte postnummer, kan du vente op til 4 gange så længe på ")
    f.write("en ambulance som nabopostnummeret. Dette er ikke tilfældigt - det er systematisk.\n\n")

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

        f.write(f"**Konklusion:** {worst_name} ({worst_time:.1f} min) er **{ratio:.1f}x langsommere** ")
        f.write(f"end {best_name} ({best_time:.1f} min). Dette er ikke acceptable variation i et velfærdssamfund. ")
        f.write("Vores analyse bekræfter Rigsrevisionens kritik (SR 11/2024), som påpeger, at de regionale servicemål ")
        f.write("dækker over 'store geografiske forskelle'. Forskellen illustrerer den fundamentale **by/land-kløft** ")
        f.write("i dansk sundhedsvæsen: Landdistriktsbeboere får systematisk ringere akut-service, ikke pga. dårlig planlægning, ")
        f.write("men pga. **geografiske realiteter** som er svære at ændre.\n\n")

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
    f.write("**🎯 Journalistisk vinkel:** \"Problemet er IKKE forværring - det er ulighed\"\n\n")
    f.write("Landsdækkende responstider har været **bemærkelsesværdigt stabile** 2021-2025. ")
    f.write("Det reelle problem er ikke generel forværring, men **ekstrem geografisk ulighed** ")
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
    f.write("**🎯 Journalistisk vinkel:** \"Myldretids-myten: Nat-vagter er det reelle problem\"\n\n")
    f.write("**Modintuitiv opdagelse:** Myldretiden (kl. 16-18) er IKKE problemet. ")
    f.write("Ambulancer er faktisk **hurtigst midt på dagen**. Det reelle problem er ")
    f.write("**nattevagter** (kl. 02-06) og især **morgenvagt-skiftet** (kl. 06:00), ")
    f.write("hvor responstiderne er op til **28% langsommere** end dagen.\n\n")

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

        f.write("**Konklusion:** Sæsonvariation (5-8%) er **meget mindre end tid-på-døgnet variation** (20-28%). ")
        f.write("Problemet er IKKE vintervejr - det er nattevagter og bemanding.\n\n")
        f.write("---\n\n")

    except Exception as e:
        logger.warning(f"Could not load temporal data: {e}")
        f.write("*Tidsmæssig analyse-data ikke tilgængelig*\n\n---\n\n")


def _write_priority_section(f, output_dir):
    """Write priority analysis section."""
    f.write("## 🏥 DEL 4: SYSTEMANALYSER\n\n")
    f.write("**🎯 Journalistisk vinkel:** \"B-prioritet: Mere end dobbelt så langsom\"\n\n")
    f.write("B-prioritet kørsler (ikke-livstruende) venter **dramatisk længere** end A-prioritet. ")
    f.write("I Hovedstaden er B-prioritet **140% langsommere** (21.9 min vs 9.1 min). ")
    f.write("Dette rejser spørgsmål om ressource-allokering.\n\n")

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
    f.write("**🎯 Journalistisk vinkel:** \"Når du ikke er døende - hvor meget betyder dit postnummer så?\"\n\n")
    f.write("Mens A-prioritet (livstruende) naturligvis prioriteres højest, viser B-prioritet analysen ")
    f.write("**dramatiske forskelle** i hvordan ikke-livstruende patienter behandles. ")
    f.write("B-prioritet viser **større variation** end A-prioritet - både geografisk, tidsmæssigt og over tid.\n\n")

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

            f.write("\n**Key Finding:** B-prioritet viser endnu større geografisk variation end A-prioritet. ")
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
            f.write("**Konklusion:** B-prioritet patienter oplever større tidsmæssig variation end A-prioritet. ")
            f.write("Dette indikerer at ikke-akutte patienter er mere påvirket af systemets kapacitetsbegrænsninger ")
            f.write("på bestemte tidspunkter (nat, morgenvagter, weekender).\n\n")

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
                f.write("**Key Finding:** B-prioritet har været **relativt stabil** på landsplan over perioden. ")
            elif national_trend['Ændring_procent'] > 5:
                f.write(f"**Key Finding:** B-prioritet er blevet **{national_trend['Ændring_procent']:.1f}% langsommere** over perioden. ")
                f.write("Dette indikerer at mens A-prioritet holdes stabil, nedprioriteres B-kørsler mere. ")
            else:
                f.write(f"**Key Finding:** B-prioritet er blevet **{abs(national_trend['Ændring_procent']):.1f}% hurtigere** over perioden. ")

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
            f.write(f"**Key Finding:** Patienter der starter som B-prioritet men opgraderes til A oplever ")
            f.write(f"**{extra_delay:+.1f} min ekstra forsinkelse** sammenlignet med korrekt A-vurdering fra start. ")
            f.write("Dette understreger vigtigheden af præcis initial triagering.\n\n")

        f.write("---\n\n")

    except Exception as e:
        logger.warning(f"Could not load B-priority data: {e}")
        f.write("*B-prioritet dyb-analyse data ikke tilgængelig*\n\n---\n\n")


def _write_alarm_time_section(f, output_dir):
    """Write alarm time (dispatch delay) analysis section."""
    f.write("## ⏱️ DEL 6: ALARMTID - DEN SKJULTE VENTETID\n\n")
    f.write("**🎯 Journalistisk vinkel:** \"1 ud af 5 minutter sker før ambulancen overhovedet kører\"\n\n")

    f.write("**Hvad er alarmtid?** Tiden fra borgeren ringer 112 til ambulancen bliver sendt afsted. ")
    f.write("Dette inkluderer triage (sundhedsfaglig vurdering), klassificering af hastegrad, og disponering ")
    f.write("(at finde og alarmere den rette ambulance). Mens borgeren venter, tror de fleste at ambulancen ")
    f.write("allerede er på vej - men i virkeligheden går der værdifuld tid i systemet **før** ambulancen ")
    f.write("overhovedet forlader stationen.\n\n")

    f.write("Data fra Nordjylland og Syddanmark afslører at **ca. 22% af total ventetid** (~2 minutter median) ")
    f.write("sker i denne 'skjulte' fase. Dette er usynligt for borgeren, men alligevel afgørende.\n\n")

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

            f.write("**Rigsrevisionens kritik (SR 11/2024):** Rigsrevisionen påpeger at regionernes servicemål IKKE ")
            f.write("medregner denne alarmtid. Den officielle 'responstid' starter først når ambulancen disponeres ")
            f.write("(sendes afsted), ikke når borgeren ringer 112. Vores data viser at denne 'skjulte' tid udgør ")
            f.write("**over 1/5 af borgerens reelle ventetid**.\n\n")

            f.write("**Konklusion:** Mens alle diskuterer ambulance-placeringer og køreruter (geografisk problem), ")
            f.write("er der 2 minutter 'skjult' i systemet som kunne optimeres gennem bedre bemanding af ")
            f.write("alarmcentraler og effektivisering af triage-processer. Dette er et system-problem, ikke et ")
            f.write("geografi-problem - og derfor potentielt lettere at løse.\n\n")

        else:
            f.write("*Alarmtid-data ikke tilgængelig*\n\n")

        f.write("---\n\n")

    except Exception as e:
        logger.warning(f"Could not load alarm time data: {e}")
        f.write("*Alarmtid analyse-data ikke tilgængelig*\n\n---\n\n")


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
