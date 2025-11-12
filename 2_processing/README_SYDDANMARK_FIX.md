# Syddanmark Data Quality Fix

## Status: ✅ Implementeret og testet

## Overblik
Automatisk fix der forbedrer Region Syddanmark data coverage fra **58.3%** til **82.1%** ved at beregne manglende responstider fra timestamps.

## Resultat

| Metric | Før | Efter | Forbedring |
|--------|-----|-------|------------|
| Valid data | 363,526 rækker | 511,942 rækker | +148,416 |
| Coverage | 58.3% | 82.1% | +23.8% |

## Implementering

### Automatisk aktivering
Fixen køres automatisk ved data-indlæsning via `data_cache.load_all_regional_data_once()`.

**Ingen ændringer nødvendige i eksisterende analyser.**

### Filer modificeret
1. ✅ `2_processing/syddanmark_fixer.py` - Ny modul (fix-logik)
2. ✅ `2_processing/data_cache.py` - Automatisk anvendelse af fix
3. ✅ `2_processing/regional_config.yaml` - Opdateret dokumentation
4. ✅ `docs/SYDDANMARK_DATA_FIX.md` - Detaljeret dokumentation

### Test & Verifikation
```bash
cd /Users/adamh/Projects/ambulance_pipeline_pro
python3 2_processing/syddanmark_fixer.py  # Standalone test
```

Output:
```
Original rows:              623,598
Valid before fix:           363,526 ( 58.3%)
Valid after fix:            511,942 ( 82.1%)
Improvement:                148,416 (+23.8%)
```

## Teknisk løsning
For rækker hvor `Responstid i minutter` mangler, beregnes værdien fra:
```python
responstid = (ankomst_timestamp - alarm_timestamp) / 60 sekunder
```

Med validering: `0 < responstid < 300 minutter`

## Data Quality (efter fix)
- **A-prioritet**: 99.9% coverage ✅
- **B-prioritet**: 99.9% coverage ✅
- **C-prioritet**: 95.4% coverage ✅
- **D-prioritet**: 21.8% coverage ⚠️

## Se også
- `docs/SYDDANMARK_DATA_FIX.md` - Detaljeret dokumentation
- `2_processing/syddanmark_fixer.py` - Source code

