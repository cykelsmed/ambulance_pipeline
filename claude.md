# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an ambulance response time analysis pipeline for Danish TV2, processing data from all 5 Danish regions (2021-2025). The pipeline generates publication-ready analysis files in ~6 seconds for postal code aggregations and ~3.5 minutes for temporal analyses across all regions.

## Essential Commands

### Run Complete Pipeline
```bash
# Runs ALL analyses (postnummer + temporal + priority + yearly + master report + HTML/PDF)
# Automatically organizes output into MASTER_FINDINGS_RAPPORT files + bilag.zip
python3 pipeline.py

# Final output: 3_output/current/
#   - MASTER_FINDINGS_RAPPORT.md (Markdown version)
#   - MASTER_FINDINGS_RAPPORT.html (HTML version with TOC)
#   - MASTER_FINDINGS_RAPPORT.pdf (PDF version - ready to print/share)
#   - bilag.zip (all 49 analysis files)
# Execution: ~11 minutes total (10 steps)
```

### Run Individual Analysis Types
```bash
# Temporal analysis only (all 5 regions)
python3 scripts/run_all_regions_temporal.py

# Temporal analysis (single region - Nordjylland)
python3 scripts/run_temporal_analysis.py
```

### Organize Output Files (Manual - Only if Needed)
```bash
# NOTE: pipeline.py now runs this automatically in Step 9/9
# Only use this if you need to re-organize existing files

# Create organized ZIP archive
python3 scripts/organize_output.py

# Keep unzipped files after organizing
python3 scripts/organize_output.py --keep-unzipped
```

### Testing & Validation
```bash
# View pipeline execution log
cat pipeline.log

# Check for errors/warnings
grep -E "WARNING|ERROR" pipeline.log

# View temporal analysis log
cat temporal_analysis.log
```

## Architecture Overview

### Multi-Phase Pipeline Design (10 Steps)

The pipeline executes 10 sequential steps:

1. **Step 1-2: Data Loading & Normalization**
   - Auto-detects Excel files from all 5 regions
   - Normalizes column names and validates postal codes

2. **Step 3-4: Postal Code Analyses**
   - Reads pre-aggregated "Postnummer" sheets
   - Generates 5 analyses: all postal codes, top 10 worst/best, regional comparison, Datawrapper CSV
   - Fast execution (~6 seconds)

3. **Step 5: Temporal Analyses**
   - Reads raw timestamp data from all 5 regions (excluding Nordjylland due to column mismatch)
   - Analyzes time-of-day (rush hour) and seasonal patterns
   - Uses config-driven regional column mapping
   - Outputs 24 files (6 per region × 4 regions)

4. **Step 6: Priority/System Analyses**
   - Analyzes A/B/C priority differences (all regions)
   - Studies priority changes (hastegradomlægning)
   - Examines channel analysis (rekvireringskanal)
   - Outputs 6 files

5. **Step 7: Yearly Analysis**
   - Analyzes year-by-year trends (2021-2025) for all regions
   - Generates landsdækkende (national) yearly averages
   - Outputs 5 files (year×region matrix, yearly summary, regional totals, pivot table, findings)

6. **Step 8: Master Findings Report**
   - Combines all analyses into comprehensive MASTER_FINDINGS_RAPPORT.md
   - Includes postal code, yearly, temporal, and priority sections
   - Markdown format for easy reading

7. **Step 9: Output Organization**
   - Automatically packs all 48 analysis files into bilag.zip
   - Keeps only MASTER_FINDINGS_RAPPORT files + bilag.zip in 3_output/current/
   - Clean, publication-ready output structure

8. **Step 10: HTML/PDF Generation (NEW!)**
   - Converts Markdown report to professional HTML using Pandoc
   - Automatically converts HTML to PDF using Chrome headless
   - PDF includes table of contents and professionally styled tables
   - Requires: `brew install pandoc` + Chrome browser (standard on macOS)
   - Output: Both .html and .pdf files (~636KB PDF, ~23KB HTML)

### Configuration-Driven Regional Handling

**Critical Design Pattern:** Regional data variations are handled through `2_processing/regional_config.yaml`:

```yaml
regions:
  Hovedstaden:
    file: "1_input/Hovedstaden20251027.xlsx"
    columns:
      timestamp: "Alarmopkald_modtaget"  # Region-specific column name
      response_time: "ResponsMinutter"
      month: "Maaned"
    month_type: danish  # Requires "Januar" → 1 conversion
```

**When adding region support or modifying columns:**
1. Update `regional_config.yaml` with new mappings
2. The pipeline automatically handles conversion/normalization
3. No code changes needed for column name variations

### Data Flow Architecture

```
1_input/
  ├── {Region}*.xlsx (5 files)
  │
  ├─> loader.py (auto-detection)
  │
  ├─> normalizer.py (column coalescing, validation)
  │
  ├─> analyzers/
  │   ├─> core.py (Phase 1: postal code analyses)
  │   ├─> temporal_analysis.py (Phase 2: time patterns)
  │   └─> priority_analysis.py (Phase 3: priority/channel)
  │
  └─> export.py → 3_output/current/
```

### Key Design Principles

1. **Config Over Code**: Regional variations handled in YAML, not Python
2. **Fault Tolerance**: Each region processed independently; failures don't cascade
3. **Automatic Detection**: `loader.py` finds Excel files by pattern matching
4. **Column Coalescing**: Handles multiple column name variations per metric
5. **Modular Phases**: Each phase can run independently without others

## Regional Data Quirks (IMPORTANT)

Each region has unique data characteristics that the pipeline handles automatically:

- **Nordjylland**: Baseline region, 100% coverage, numeric months
- **Hovedstaden**: Uses Danish month names ("Januar") requiring conversion
- **Sjælland**: 100% coverage, uses "Kald modtaget (tid)" for timestamp
- **Midtjylland**: Uses "Tid_HændelseOprettet", "Måned_HændelseOprettet"
- **Syddanmark**: 58% coverage, has empty strings in response time column (requires `pd.to_numeric(..., errors='coerce')`)

**When debugging regional issues:**
1. Check `regional_config.yaml` for correct column mappings
2. Verify month_type (numeric vs danish)
3. Look at `pipeline.log` for data coverage warnings

## Common Development Tasks

### Adding a New Analysis

1. Create analysis function in appropriate module:
   - Postal code analyses → `2_processing/analyzers/core.py`
   - Time-based analyses → `2_processing/analyzers/temporal_analysis.py`
   - Priority analyses → `2_processing/analyzers/priority_analysis.py`

2. Add to enabled_analyses in `config.yaml`:
   ```yaml
   enabled_analyses:
     - "your_new_analysis"
   ```

3. Add export logic in `analyzers/export.py`

### Updating Regional Column Mappings

Edit `2_processing/regional_config.yaml`:
```yaml
regions:
  YourRegion:
    file: "1_input/YourRegion.xlsx"
    sheet: "SheetName"
    columns:
      timestamp: "ActualColumnName"
      response_time: "ActualColumnName"
      priority: "ActualColumnName"
      month: "ActualColumnName"
    month_type: numeric  # or 'danish'
```

### Updating Data Files

When Nils provides new Excel files:
```bash
# 1. Move new files to 1_input/
cp ~/Downloads/NewRegion.xlsx 1_input/

# 2. Run pipeline (auto-detects newest files)
python3 pipeline.py

# 3. Old outputs automatically archived to 3_output/archive/
```

## Output File Structure

### Phase 1 Output (Postal Code)
- `01_alle_postnumre.xlsx` - All 624 postal codes ranked
- `02_top_10_værste_VALIDERET.xlsx` - Top 10 worst (≥50 trips validated)
- `03_top_10_bedste.xlsx` - Top 10 best
- `04_regional_sammenligning.xlsx` - Regional comparison (5 regions)
- `DATAWRAPPER_alle_postnumre.csv` - Map visualization data

### Phase 2 Output (Temporal - per region)
- `{Region}_05_responstid_per_time.xlsx` - Hourly stats (0-23)
- `{Region}_05_responstid_per_time_FUND.txt` - Key findings (time-of-day)
- `{Region}_DATAWRAPPER_responstid_per_time.csv` - Time curve visualization
- `{Region}_06_responstid_per_maaned.xlsx` - Monthly stats (1-12)
- `{Region}_06_responstid_per_maaned_FUND.txt` - Key findings (seasonal)
- `{Region}_DATAWRAPPER_responstid_per_maaned.csv` - Monthly curve visualization
- `TIDSMÆSSIGE_ANALYSER_SAMMENFATNING.md` - Consolidated multi-region summary

### Phase 3 Output (Priority/System)
- `07_abc_prioritering.xlsx` - A vs B vs C comparison
- `08_prioritetsforskelle.xlsx` - Statistical differences
- `09_rekvireringskanal.xlsx` - Channel analysis
- (Optional) Hastegrad change analysis if data exists

## Data Validation Notes

**Verified Accuracy**: Phase 1 aggregations have been 100% verified against raw data for 4/5 regions (76.4% of total data):
- Nordjylland: 100% match (84,243 trips)
- Hovedstaden: 100% match (230,101 trips)
- Sjælland: 100% match (163,489 trips)
- Midtjylland: 99.99% match (180,946 trips, 5 trip difference)
- Syddanmark: Not verified (raw data response time column empty)

See `VERIFICATION.md` for detailed validation methodology.

## Logging & Debugging

All pipeline operations log to:
- `pipeline.log` - Main pipeline execution
- `temporal_analysis.log` - Temporal analysis details

Log format includes:
- Timestamp
- Module name
- Log level
- Message

**Common debugging patterns:**
```python
logger.info(f"Processing {region_name}: {len(df):,} rows")
logger.warning(f"Low data coverage: {coverage:.1f}%")
logger.error(f"Failed to load {file_path}: {e}", exc_info=True)
```

## Dependencies

Core dependencies (requirements.txt):
- `pandas>=2.0` - Data manipulation
- `openpyxl>=3.1` - Excel I/O
- `pyyaml>=6.0` - Config parsing

All analyses use standard library + these three packages only.

## Performance Characteristics

- Phase 1 (postal codes): ~6 seconds (624 postal codes, 861,757 trips)
- Phase 2 (temporal, all regions): ~3.5 minutes (875,513 A-cases, 30 files)
- Phase 3 (priority): ~30 seconds (system-wide analysis)
- Total pipeline: ~4 minutes for all phases

Memory footprint: Low (only loads one region at a time for temporal analyses)
- allways use descriptive variable names