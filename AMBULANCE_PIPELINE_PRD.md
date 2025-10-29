# PROJECT REQUIREMENTS DOCUMENT: AMBULANCE PIPELINE
**Projekt:** TV2 Ambulance Responstider Analyse Pipeline  
**Dato:** 28. oktober 2025  
**Version:** 1.0  
**Til:** Claude Code implementation

---

## EXECUTIVE SUMMARY

**Formål:**  
Automatiserbar pipeline til at generere TV2-klare analyser af ambulance-responstider i Danmark. Pipeline skal kunne re-køres når Nils leverer opdaterede rensede data fra regionerne.

**Input:**  
5 Excel-filer med rensede ambulancedata fra Nils (én per region)

**Output:**  
10+ Excel/CSV-filer med aggregerede analyser klar til TV2-publicering

**Nøgle-requirement:**  
Pipeline skal kunne sammenligne før/efter når data opdateres (fx når Nordjylland leverer nye data).

---

## BUSINESS GOALS

### TV2 Storylines
1. **Postnummer-lotteri:** Dit postnummer afgør dine overlevelseschancer
2. **Regional ulighed:** Nordjylland klarer sig værst
3. **Nedgraderinger:** Hvor nedgraderes livstruende kørsler til akutte?
4. **Tidstrend:** Er det blevet bedre eller værre? (2021-2025)
5. **A vs B:** Hvor store er forskelle mellem livstruende og akutte?

### Publication Deadline
- Regionsrådsvalg: 18. november 2025 (21 dage fra nu)
- Publikation skal ske inden valget

---

## DATA SOURCES

### Input Files (fra Nils)
**Location:** `ambulance_pipeline/1_input/`

**Files:**
```
Nordjylland20251027.xlsx    (9 kolonner, ~180k poster)
RegionSjælland.xlsx         (12 kolonner, ~315k poster)
Syddanmark20251025.xlsx     (16 kolonner, ~624k poster)
Midtjylland20251027.xlsx    (13 kolonner, ~359k poster)
Hovedstaden20251027.xlsx    (14 kolonner, ~514k poster)
```

**KRITISK:** Filnavne ændrer sig når Nils leverer opdaterede data!
Pipeline skal kunne **auto-detektere** filer baseret på navnemønstre.

### Data Structure (fra Nils' dokumentation)

**Fælles kolonner (alle regioner):**
- Postnummer (format varierer: "9000", "København K", etc.)
- År/Måned (nogle har fuld dato, andre kun år+måned)
- Hastegrad (A, B, C, D - men kun A+B i nuværende data)
- Responstid (nogle har beregnet, andre kun tidsstempler)
- Antal_ture

**Nedgraderinger (ikke alle regioner):**
- Syddanmark: Har op/nedgradering-kolonner ✓
- Sjælland: Op/ned kun fra juni 2023 ✓
- Nordjylland: Nye data har op/ned ✓
- Hovedstaden: ? (skal tjekkes)
- Midtjylland: ? (skal tjekkes)

**Ark-struktur:**
Nils' filer har ofte **flere ark**:
- Hovedark: Rå data
- "Postnummer"-ark: Aggregerede beregninger (gennemsnit per postnummer)
- Mulige andre: "Helikopter", "Nedgraderinger", etc.

**Pipeline skal læse primært fra "Postnummer"-ark hvis det findes, ellers beregne selv.**

---

## TECHNICAL REQUIREMENTS

### Performance
- Skal kunne processere ~2 millioner poster på <5 minutter
- Low memory footprint (pandas optimization)

### Robustness
- Håndter manglende kolonner gracefully (skip med warning)
- Håndter forskellige datoformater
- Håndter forskellige postnummer-formater (København K → 1000, etc.)

### Reproducibility
- Samme input → samme output (deterministisk)
- Version-stamped outputs (inkluder dato/tid i filnavn)
- Git-friendly (tekstbaserede diff-rapporter)

---

## PIPELINE ARCHITECTURE

### Module Structure

```
ambulance_pipeline/
│
├── 1_input/                      # Nils' rensede filer (Excel)
│   ├── Nordjylland20251027.xlsx
│   ├── Syddanmark20251025.xlsx
│   └── ... (auto-detekteres)
│
├── 2_processing/                 # Python modules
│   ├── __init__.py
│   ├── config.py                 # Load config.yaml
│   ├── loader.py                 # Indlæs alle regioner
│   ├── validator.py              # Data quality checks
│   ├── normalizer.py             # Normaliser kolonnenavne, postnumre, etc.
│   ├── calculator.py             # Beregn responstider (hvis ikke allerede gjort)
│   ├── aggregator.py             # Aggreger til postnummer-niveau
│   ├── statistics.py             # Statistisk validering (filtrer <50 ture)
│   ├── analyzers/                # Analyse-moduler
│   │   ├── __init__.py
│   │   ├── core.py               # Top 10, regional sammenligning
│   │   ├── timeseries.py         # Årlig tidsserie 2021-2025
│   │   ├── downgrades.py         # Nedgraderinger A→B
│   │   ├── ab_comparison.py      # A vs B kørsler
│   │   └── export.py             # Excel/CSV export
│   ├── differ.py                 # Sammenlign før/efter kørsler
│   └── utils.py                  # Hjælpefunktioner
│
├── 3_output/                     # TV2-klare filer
│   ├── current/                  # Seneste kørsel
│   │   ├── 01_alle_postnumre.xlsx
│   │   ├── 02_top_10_værste.xlsx
│   │   └── ...
│   └── archive/                  # Tidligere kørsler
│       ├── 2025-10-27_run/
│       └── 2025-10-28_run/
│
├── 4_reports/                    # Diff-rapporter
│   └── diff_2025-10-27_vs_2025-10-28.md
│
├── 5_tests/                      # Unit tests
│   ├── test_loader.py
│   ├── test_validator.py
│   └── ...
│
├── config.yaml                   # Konfiguration
├── pipeline.py                   # Main entry point
├── requirements.txt              # Dependencies
├── README.md                     # Setup & usage
└── .gitignore
```

### Data Flow

```
[Nils' Excel-filer]
        ↓
   [loader.py] ← Auto-detect files
        ↓
   [validator.py] ← Quality checks
        ↓
   [normalizer.py] ← Standardize formats
        ↓
   [calculator.py] ← Compute if needed
        ↓
   [aggregator.py] ← Aggregate to postnummer
        ↓
   [statistics.py] ← Filter <50 ture
        ↓
   [analyzers/*] ← Generate all analyses
        ↓
   [export.py] ← Save to Excel/CSV
        ↓
   [differ.py] ← Compare with previous run
        ↓
[TV2-klare outputs + diff-rapport]
```

---

## DETAILED SPECIFICATIONS

### TIER 1 ANALYSES (Kernestory - må aldrig fejle)

#### 1. TOP 10 VÆRSTE POSTNUMRE
**File:** `02_top_10_værste_VALIDERET.xlsx`

**Spec:**
- Filter: Kun postnumre med ≥50 ture (statistisk validering)
- Sort: Descending by Gennemsnit_minutter
- Take: Top 10

**Columns:**
```
Postnummer          int       (standardized: København K → 1000)
Gennemsnit_minutter float     (rounded to 1 decimal)
Antal_ture          int       (must be ≥50)
Region              string    (Nordjylland, Sjælland, etc.)
```

**Validation:**
- Warn if <10 postnumre meet ≥50 threshold
- Error if 0 postnumre meet threshold

**Edge cases:**
- Hvis København K/V/C: Map til 1000/1500/1800
- Hvis postnummer = null: Skip med warning

---

#### 2. TOP 10 BEDSTE POSTNUMRE
**File:** `03_top_10_bedste.xlsx`

**Spec:**
- Filter: Kun postnumre med ≥50 ture
- Sort: Ascending by Gennemsnit_minutter
- Take: Top 10

**Columns:** Samme som værste.

---

#### 3. REGIONAL SAMMENLIGNING
**File:** `04_regional_sammenligning.xlsx`

**Spec:**
- Group by: Region
- Aggregate: mean, median, sum(ture), count(postnumre)
- Sort: Descending by Gennemsnit_minutter (værst først)

**Columns:**
```
Region              string
Gennemsnit_minutter float     (rounded to 1 decimal)
Median_minutter     float     (rounded to 1 decimal)
Total_ture          int       (sum of all ture in region)
Antal_postnumre     int       (count of unique postnumre)
```

**Derived fields (add extra columns):**
```
Forskel_til_bedste  float     (difference from best region)
Procent_over_bedste float     (% difference from best region)
```

---

#### 4. DANMARKSKORT CSV
**File:** `DATAWRAPPER_alle_postnumre.csv`

**Spec:**
- Include: Alle postnumre (no filter)
- Add: Kategori (Grøn/Gul/Rød baseret på responstid)

**Columns:**
```
Postnummer          int
Gennemsnit_minutter float     (1 decimal)
Antal_ture          int
Region              string
Kategori            string    (Grøn <10, Gul 10-15, Rød >15)
```

**Color mapping:**
```
Grøn: <10 min    (#2ecc71)
Gul:  10-15 min  (#f39c12)
Rød:  >15 min    (#e74c3c)
```

**Note column (optional):**
- Add asterisk (*) if Antal_ture < 50

---

#### 5. ALLE POSTNUMRE (Master file)
**File:** `01_alle_postnumre.xlsx`

**Spec:**
- Include: Alle postnumre (no filter)
- Sort: Descending by Gennemsnit_minutter

**Columns:**
```
Postnummer          int
Antal_ture          int
Gennemsnit_minutter float (1 decimal)
Max_minutter        float (1 decimal)
Region              string
```

---

### TIER 2 ANALYSES (Dybde - vigtig for storyline)

#### 6. TIDSSERIE 2021-2025 (Årlig)
**File:** `07_tidsserie_årlig.xlsx`

**Spec:**
- Group by: År (extract from date column)
- Aggregate: mean, median, count per år
- Calculate for: Hele landet + per region

**Output structure:**
- **Sheet 1 "Landsdækkende":**
```
År                  int       (2021, 2022, 2023, 2024, 2025)
Gennemsnit_minutter float
Median_minutter     float
Antal_ture          int
```

- **Sheet 2-6:** Per region (5 ark)
  - Same columns as above
  - Separate sheet per region

**Validation:**
- 2025 kun delår (jan-jun) → annotér i note
- Warn if <1000 ture per år per region

**Derived fields:**
```
Ændring_vs_2021     float     (difference from baseline 2021)
Trend               string    (↑ Stigning / ↓ Fald / → Stabil)
```

---

#### 7. NEDGRADERINGER
**File:** `08_nedgraderinger.xlsx`

**KRITISK:** Ikke alle regioner har nedgraderinger-data!
Pipeline skal håndtere dette gracefully.

**Sheet 1: Regional oversigt**
```
Region              string
Total_A_kørsler     int       (original A-hastegrad)
Nedgraderet_A_til_B int       (A→B nedgraderinger)
Procent_nedgraderet float     (%)
Gns_responstid_A    float     (kun A-kørsler, ikke nedgraderet)
Gns_responstid_nedgr float    (A-kørsler der blev nedgraderet)
Forskel             float     (nedgr - ikke nedgr)
```

**Sheet 2: Top 20 postnumre med mest nedgradering**
```
Postnummer          int
Region              string
A_kørsler           int       (total A-kørsler i postnummer)
Nedgraderet_A_B     int       (antal nedgraderet)
Procent_nedgraderet float     (%)
Gns_responstid      float     (for dette postnummer)
```

**Sheet 3: Nedgraderings-mønstre**
Analyse af HVORNÅR nedgraderinger sker:
```
Type                string    (A→B, B→A, B→C, etc.)
Antal               int
Procent_af_total    float
```

**Validation:**
- If region mangler nedgradering-data: Skip med note
- Minimum 10 nedgraderinger for statistisk validitet

**Derived insights:**
- "Er nedgraderede kørsler langsommere?" (sammenlign responstider)
- "Hvilke regioner nedgraderer mest?" (ranking)

---

#### 8. A vs B KØRSLER (Separate analyser)
**File:** `09_A_vs_B_kørsler.xlsx`

**Sheet 1: Sammenligning**
```
Hastegrad           string    (A, B)
Antal_kørsler       int
Gennemsnit_minutter float
Median_minutter     float
Over_15_min         int       (antal over målet)
Procent_over_mål    float     (%)
```

**Sheet 2: Top 10 værste A-kørsler** (kun A)
Same columns as Top 10 værste, but filtered for hastegrad='A'

**Sheet 3: Top 10 værste B-kørsler** (kun B)
Same columns as Top 10 værste, but filtered for hastegrad='B'

**Sheet 4: Regional A vs B**
```
Region              string
A_gennemsnit        float
B_gennemsnit        float
Forskel_A_B         float     (A - B, forventet negativ)
```

**Journalistisk vinkel:**
"Er livstruende (A) hurtigere end akutte (B)?"

---

#### 9. TOP 20 PER REGION
**File:** `05_top_20_per_region.xlsx`

**Spec:**
- 5 separate ark (1 per region)
- Top 20 værste postnumre per region
- Filter: ≥30 ture (mere fleksibelt da det er per region)

**Columns per sheet:**
```
Postnummer          int
Gennemsnit_minutter float (1 decimal)
Antal_ture          int
Note                string (* hvis <50 ture)
```

---

### TIER 3 ANALYSES (Nice-to-have)

#### 10. HELIKOPTER-DATA (hvis tilgængelig)
**File:** `06_helikopter_data.xlsx`

**Spec:**
- Kun hvis helikopter-ark findes i input
- Tidsserie per år

**Columns:**
```
År                  int
Antal_ture          int
Gennemsnit_minutter float
Max_minutter        float
Region              string (hvilken base)
```

---

## CONFIGURATION (config.yaml)

```yaml
# Ambulance Pipeline Configuration
version: "1.0"

# Input settings
input:
  directory: "1_input"
  auto_detect: true
  patterns:
    nordjylland: "Nordjylland*.xlsx"
    sjælland: "*Sjælland*.xlsx"
    syddanmark: "Syddanmark*.xlsx"
    midtjylland: "Midtjylland*.xlsx"
    hovedstaden: "Hovedstaden*.xlsx"
  
  # Hvilke ark skal læses?
  preferred_sheet: "Postnummer"  # Prøv dette først
  fallback_sheet: null            # Eller første ark

# Statistical thresholds
statistics:
  top_10_min_ture: 50              # Minimum ture for Top 10
  regional_top_20_min_ture: 30     # Per region, mere fleksibel
  timeseries_min_ture_per_year: 30 # Per år
  
  # Color coding for Datawrapper
  color_green_max: 10.0  # <10 min = grøn
  color_yellow_max: 15.0 # 10-15 min = gul
  # >15 min = rød

# Postnummer normalization
postnummer_mapping:
  "København K": 1000
  "København V": 1500
  "Frederiksberg C": 1800

# Output settings
output:
  directory: "3_output/current"
  archive_directory: "3_output/archive"
  format: "xlsx"  # or "csv" for certain files
  decimal_places: 1
  
  # Enable/disable specific analyses
  enabled_analyses:
    - "top_10_værste"
    - "top_10_bedste"
    - "regional_sammenligning"
    - "alle_postnumre"
    - "datawrapper_csv"
    - "tidsserie"
    - "nedgraderinger"
    - "a_vs_b"
    - "top_20_per_region"
    - "helikopter"  # kun hvis data findes

# Diff settings
diff:
  enabled: true
  previous_run_path: "3_output/archive"  # Auto-find seneste
  output_path: "4_reports"
  
# Logging
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  file: "pipeline.log"
  console: true

# Validation rules
validation:
  min_rows_per_region: 1000        # Error hvis <1000 poster
  max_responstid: 300               # Warn hvis >300 min (5 timer)
  min_responstid: 0                 # Warn hvis <0 min
  required_columns:
    - "Postnummer"
    - "Gennemsnit_minutter"         # Eller tidsstempler til at beregne
```

---

## ERROR HANDLING

### Validation Checks

**Pre-processing:**
1. **File exists:** Alle 5 regionale filer skal findes
   - Error if <3 regioner (kan ikke lave landsdækkende)
   - Warning if <5 regioner (incomplete)

2. **Required columns:** Hver fil skal have minimum kolonner
   - Error if missing: Postnummer, År/Måned
   - Warning if missing: Responstid (kan beregnes fra tidsstempler)

3. **Data types:** Validér typer
   - Postnummer skal være int (eller konverterbart)
   - Responstid skal være float/int
   - Dato skal være parseable

**During processing:**
4. **Logical constraints:**
   - Responstid må ikke være negativ
   - Responstid >300 min er mistænkeligt (log warning)
   - Postnummer skal være 4 cifre (1000-9999)

5. **Statistical validity:**
   - Warn hvis <50 postnumre opfylder ≥50 ture threshold
   - Error hvis 0 postnumre opfylder threshold

**Post-processing:**
6. **Output completeness:**
   - Verify alle enabled analyses har genereret filer
   - Verify antal rækker er reasonable (>10 i Top 10, etc.)

### Error Recovery

**Graceful degradation:**
- Hvis nedgradering-data mangler i en region: Skip den region, fortsæt
- Hvis helikopter-ark ikke findes: Skip analyse, fortsæt
- Hvis tidsserie har huller: Annotér med note, fortsæt

**Failfast scenarios:**
- Hvis <3 regioner kan indlæses: Abort (kan ikke lave analyser)
- Hvis ingen postnumre opfylder ≥50 threshold: Abort (kan ikke lave Top 10)
- Hvis configuration er invalid: Abort

---

## DIFF GENERATION (Before/After Comparison)

### Trigger
Pipeline skal automatisk detektere hvis der er en tidligere kørsel i archive.

### Diff Report Structure

**File:** `4_reports/diff_YYYY-MM-DD_vs_YYYY-MM-DD.md`

**Sections:**

#### 1. Executive Summary
```markdown
# ÆNDRINGER: 2025-10-27 → 2025-10-28

**Trigger:** Nordjylland leverede nye data (+821 A-hændelser)

**Hovedændringer:**
- Nordjylland: 84.243 → 85.064 ture (+821, +1.0%)
- Regional ranking: Uændret (Nordjylland stadig værst)
- Top 10 værste: 2 postnumre ændret
```

#### 2. Regional Changes
```markdown
## REGIONAL SAMMENLIGNING

| Region      | Før    | Efter  | Ændring | % ændring |
|-------------|--------|--------|---------|-----------|
| Nordjylland | 13.0   | 12.9   | -0.1    | -0.8%     |
| Sjælland    | 12.7   | 12.7   | 0.0     | 0.0%      |
| ...         |        |        |         |           |
```

#### 3. Top 10 Changes
```markdown
## TOP 10 VÆRSTE

**Fjernet:**
- 8970 (19.4 min, 278 ture) → Nu #11

**Tilføjet:**
- 9140 (19.5 min, 156 ture) → Nu #10
```

#### 4. Statistical Summary
```markdown
## STATISTIK

**Før:**
- Total postnumre: 624
- Gennemsnit: 12.2 min

**Efter:**
- Total postnumre: 625 (+1)
- Gennemsnit: 12.1 min (-0.1 min, -0.8%)
```

---

## TESTING STRATEGY

### Unit Tests

**test_loader.py:**
- Test auto-detection af filer
- Test læsning af forskellige ark-strukturer
- Test error handling ved manglende filer

**test_normalizer.py:**
- Test postnummer-mapping (København K → 1000)
- Test dato-parsing (forskellige formater)
- Test håndtering af null-values

**test_statistics.py:**
- Test filtrering (≥50 ture)
- Test at Top 10 altid har præcis 10 rækker
- Test color categorization (grøn/gul/rød)

**test_differ.py:**
- Test sammenligning af to kørsler
- Test detection af ændringer
- Test markdown-generering

### Integration Tests

**test_full_pipeline.py:**
- Test komplet kørsel med mock data
- Verify alle output-filer genereres
- Verify output struktur er korrekt

### Test Data

**1_input/test_data/:**
- Små sample-filer (100 rækker hver)
- Dækker edge cases:
  - Region uden nedgraderinger
  - Postnumre med <50 ture
  - København K/V/C formatting
  - Manglende kolonner

---

## SETUP & USAGE

### Installation

```bash
# Clone repository
git clone [repo-url]
cd ambulance_pipeline

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Dependencies (requirements.txt)

```
pandas>=2.0.0
openpyxl>=3.1.0
pyyaml>=6.0
python-dateutil>=2.8.0
pytest>=7.4.0
```

### First Run

```bash
# 1. Place Nils' files in 1_input/
cp /path/to/Nordjylland*.xlsx 1_input/
cp /path/to/Syddanmark*.xlsx 1_input/
# ... (all 5 regions)

# 2. Review config
nano config.yaml

# 3. Run pipeline
python pipeline.py

# 4. Check outputs
ls 3_output/current/

# 5. Review diff report (if previous run exists)
cat 4_reports/diff_*.md
```

### Re-running After Data Update

```bash
# 1. Backup previous run (automatic)
# Pipeline auto-archives to 3_output/archive/

# 2. Place NEW files in 1_input/
# (Overwrite old files or pipeline will auto-detect newest)

# 3. Run pipeline
python pipeline.py

# 4. Review diff
cat 4_reports/diff_*.md
# Shows precisely what changed
```

### CLI Options

```bash
# Default: Run all analyses
python pipeline.py

# Dry run: Validate only, no output
python pipeline.py --dry-run

# Specific analyses only
python pipeline.py --analyses top_10,regional

# Skip archiving
python pipeline.py --no-archive

# Verbose logging
python pipeline.py --verbose

# Force re-run (ignore cache)
python pipeline.py --force
```

---

## DELIVERABLES

### Output Files (3_output/current/)

**Tier 1 (Must have):**
1. `01_alle_postnumre.xlsx` - Master file (alle 624 postnumre)
2. `02_top_10_værste_VALIDERET.xlsx` - Statistisk sikker Top 10
3. `03_top_10_bedste.xlsx` - Bedste 10 postnumre
4. `04_regional_sammenligning.xlsx` - 5 regioner ranket
5. `DATAWRAPPER_alle_postnumre.csv` - Klar til kort

**Tier 2 (Important):**
6. `07_tidsserie_årlig.xlsx` - Trends 2021-2025 (6 ark)
7. `08_nedgraderinger.xlsx` - A→B analyse (3 ark)
8. `09_A_vs_B_kørsler.xlsx` - A vs B sammenligning (4 ark)
9. `05_top_20_per_region.xlsx` - Regional deep-dive (5 ark)

**Tier 3 (Nice-to-have):**
10. `06_helikopter_data.xlsx` - Hvis data findes

**Metadata:**
11. `pipeline_run_metadata.json` - Timestamp, input files, versions

### Reports (4_reports/)

12. `diff_YYYY-MM-DD_vs_YYYY-MM-DD.md` - Comparison report
13. `validation_report.txt` - Data quality warnings

### Logs

14. `pipeline.log` - Detailed execution log

---

## EXAMPLE USAGE SCENARIOS

### Scenario 1: First Run (27. oktober)

```bash
# Nils har leveret første rensede data
$ python pipeline.py

Output:
✅ Loaded 5 regions (1,992,146 ture)
✅ Generated 10 analyses
✅ Saved to 3_output/current/
⚠️  No previous run found (skipping diff)

Files created:
- 01_alle_postnumre.xlsx
- 02_top_10_værste_VALIDERET.xlsx
- ... (10 files total)
```

### Scenario 2: Re-run After Nordjylland Update (28. oktober)

```bash
# Nordjylland leverede nye data (+821 ture)
# Overskriver Nordjylland20251027.xlsx med ny fil

$ python pipeline.py

Output:
✅ Loaded 5 regions (1,992,967 ture)
✅ Detected previous run (2025-10-27)
✅ Generated 10 analyses
✅ Saved to 3_output/current/
✅ Archived previous run to 3_output/archive/2025-10-27_run/
✅ Generated diff report → 4_reports/diff_2025-10-27_vs_2025-10-28.md

Key changes:
- Nordjylland: 84,243 → 85,064 ture (+821)
- Gennemsnit: 12.2 → 12.1 min (-0.1)
- Top 10: 2 postnumre changed
```

### Scenario 3: Re-run with Missing Region

```bash
# Syddanmark-fil er slettet ved en fejl

$ python pipeline.py

Output:
⚠️  WARNING: Only 4/5 regions found
   Missing: Syddanmark
✅ Loaded 4 regions (1,368,369 ture)
⚠️  Results incomplete (missing Syddanmark)
✅ Generated 10 analyses (where possible)

Files created: (marked as incomplete)
```

---

## SUCCESS CRITERIA

Pipeline er successfuld hvis:

1. **Correctness:** Output matcher Nils' bereg ninger (hvor sammenlignelige)
2. **Completeness:** Alle 10 analyses genereres fejlfrit
3. **Speed:** <5 minutter total execution time
4. **Robustness:** Håndterer manglende data gracefully
5. **Reproducibility:** Samme input → samme output
6. **Usability:** Adam kan køre uden at læse 100 linjer docs

---

## FUTURE ENHANCEMENTS (Post-MVP)

Ikke til første version, men mulige fremtidige tilføjelser:

1. **Web dashboard:** Interaktiv visualisering af outputs
2. **Månedlig granularitet:** Tidsserie per måned (ikke kun år)
3. **Automatisk email:** Send diff-rapport til Emil når kørsel er færdig
4. **Datawrapper API:** Upload CSV direkte til Datawrapper
5. **SQL database:** Gem historiske data for avancerede queries
6. **Machine learning:** Forudsig responstider baseret på features

---

## CONTACT & SUPPORT

**Project Owner:** Adam Hvidt (adam@km24.dk)

**Implementation:** Claude Code

**Questions during implementation:**
- Scope clarifications → Ask Adam
- Technical decisions → Use best practices
- Edge cases → Fail gracefully + log warning

---

## APPENDIX A: DATA DICTIONARY

### Nils' Kolonnenavne (varierer per region)

**Postnummer-variationer:**
- `Postnummer`, `PostNr`, `postnummer`, `Postnr`

**Responstid-variationer:**
- `Gennemsnit_minutter`, `Responstid`, `ResponseTid`, `gennemsnit_minutter`

**Hastegrad-variationer:**
- `Hastegrad`, `Prioritet`, `Priority`, `hastegrad`

**Dato-variationer:**
- `År`, `Aar`, `Year`, `Måned`, `Maaned`, `Month`, `Dato`, `Date`

**Nedgradering-variationer:**
- `OpNedgradering`, `Ændring`, `HastegradÆndring`, `PriorityChange`

Pipeline skal håndtere alle variationer via `normalizer.py`.

---

## APPENDIX B: POSTNUMMER-RANGES

**Danmark:** 1000-9999

**Specielle:**
- 1000-1799: København (multiple variants)
- 1800-1999: Frederiksberg
- 2000-2999: Hovedstadsområdet
- 3000-3999: Sjælland
- 4000-4999: Sjælland
- 5000-5999: Syddanmark
- 6000-6999: Syddanmark
- 7000-7999: Midtjylland
- 8000-8999: Midtjylland
- 9000-9999: Nordjylland

**Mapping-logik:**
```python
def standardize_postnummer(postnr):
    """Convert København K/V/C to numeric"""
    mapping = {
        "København K": 1000,
        "København V": 1500,
        "Frederiksberg C": 1800,
        # Add more as needed
    }
    
    if isinstance(postnr, str):
        return mapping.get(postnr, int(postnr))
    return int(postnr)
```

---

## VERSION HISTORY

- **v1.0** (28. oktober 2025): Initial PRD
  - All 7 beslutninger fra Adam implementeret
  - 10 analyser specificeret
  - Diff-strategi defineret

---

**KLAR TIL IMPLEMENTATION I CLAUDE CODE** ✅

