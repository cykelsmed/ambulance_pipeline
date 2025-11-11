# AMBULANCE PIPELINE - BILAG
**Genereret:** 10. November 2025 kl. 11:05

Dette arkiv indeholder alle datafiler og analyser fra ambulance-pipeline kørslen.

## 📊 FILSTRUKTUR

### Postnummer-analyser
- `01_alle_postnumre.xlsx` - Alle 624 postnumre med responstider
- `02_top_10_værste_VALIDERET.xlsx` - De 10 postnumre med længst responstid (≥50 ture)
- `03_top_10_bedste.xlsx` - De 10 postnumre med kortest responstid
- `04_regional_sammenligning.xlsx` - Aggregeret sammenligning på tværs af 5 regioner

### Tidsmæssige analyser (per region)
**Format:** `[Region]_05_responstid_per_time.xlsx` og `[Region]_06_responstid_per_maaned.xlsx`

- **05_responstid_per_time:** Responstider per time på døgnet (0-23)
- **06_responstid_per_maaned:** Responstider per måned (Jan-Dec)
- **_FUND.txt:** Automatisk genererede fund og konklusioner

Regioner: Nordjylland, Hovedstaden, Sjælland, Midtjylland, Syddanmark

### System-analyser
- `07_prioritering_ABC.xlsx` - A vs B vs C prioritering (hastegradskoder)
- `09_rekvireringskanal.xlsx` - Responstid per rekvireringskanal
- `*_FUND.txt` - Automatisk genererede fund til hver analyse

### Datawrapper CSV-filer
CSV-filer optimeret til import i Datawrapper visualiseringstool:
- `DATAWRAPPER_alle_postnumre.csv` - Alle postnumre med farve-kategorier
- `DATAWRAPPER_prioritering_ABC.csv` - ABC prioritering
- `DATAWRAPPER_rekvireringskanal.csv` - Rekvireringskanal data
- `[Region]_DATAWRAPPER_responstid_per_*.csv` - Regionale tidsmønstre

### Rapporter
- `TIDSMÆSSIGE_ANALYSER_SAMMENFATNING.md` - Konsolideret sammenfatning af tidsmønstre

### Metadata
- `pipeline_run_metadata.json` - Teknisk metadata om pipeline-kørslen

## 🔍 BRUG AF FILER

**For journalister:**
1. Start med hovedrapporten (MASTER_FINDINGS_RAPPORT.md i rod-mappen)
2. Undersøg relevante Excel-filer for detaljer
3. Brug _FUND.txt-filer for hurtig opsummering
4. Import DATAWRAPPER CSV-filer direkte i Datawrapper

**For analytikere:**
1. Alle Excel-filer kan åbnes direkte i Excel/LibreOffice
2. CSV-filer kan importeres i ethvert dataværktøj
3. JSON metadata indeholder kørselsinfo

## ✅ VALIDERING

Pipeline er 100% valideret mod Nils Mulvads beregninger:
- 549 postnumre sammenlignet
- Maksimal afvigelse: 0.05 minutter (3 sekunder - kun afrundingsfejl)
- Se validering.md i rod-mappen for detaljer

## 📞 KONTAKT

Ved spørgsmål til data eller metode, kontakt Adam Holm eller Nils Mulvad.
