# Syddanmark Data Quality Fix

## Problem
Region Syddanmark data havde oprindeligt kun 58.3% data coverage (363,526 ud af 623,598 rækker).

### Årsag
41.7% af rækkerne (260,072 rækker) havde værdien `' '` (et enkelt mellemrum) i kolonnen `Responstid i minutter`.

Analyse viste at:
- **A-prioritet**: Responstid udfyldt i 99.9% af tilfældene
- **B-prioritet**: Responstid udfyldt i 99.9% af tilfældene  
- **C-prioritet**: Responstid manglede i ~90% af tilfældene
- **D-prioritet**: Responstid manglede i ~78% af tilfældene

## Løsning
Implementeret automatisk beregning af manglende responstider fra timestamps.

### Metode
For rækker hvor `Responstid i minutter` mangler, men hvor både:
- `Hændelse oprettet i disponeringssystem` (alarm modtaget)
- `Ankomst første sundhedsprofessionelle enhed` (ankomst)

er tilgængelige, beregnes responstiden som:
```python
responstid = (ankomst - alarm) i minutter
```

### Validering
Kun responstider der opfylder følgende kriterier bruges:
- `> 0 minutter` (positiv værdi)
- `< 300 minutter` (< 5 timer - sanity check)

## Resultat

| Metric | Før fix | Efter fix | Forbedring |
|--------|---------|-----------|------------|
| **Valid rækker** | 363,526 | 511,942 | +148,416 |
| **Data coverage** | 58.3% | 82.1% | +23.8% |

### Prioritetsfordeling af beregnede data
Fixen tilføjede primært data for lavere prioriteter:

| Prioritet | Tilføjet antal |
|-----------|----------------|
| C | 112,861 |
| D | 29,490 |
| B | 3,099 |
| A | 2,948 |
| X | 13 |
| E | 3 |
| L | 2 |

## Implementering

### Filer
1. **`2_processing/syddanmark_fixer.py`** - Ny modul med fix-logik
2. **`2_processing/data_cache.py`** - Automatisk anvendelse af fix ved data-indlæsning
3. **`2_processing/regional_config.yaml`** - Opdateret dokumentation

### Automatisk anvendelse
Fixen aktiveres automatisk når Syddanmark data indlæses via `load_all_regional_data_once()`. Ingen ændringer nødvendige i eksisterende analyse-scripts.

### Brug standalone
```python
from syddanmark_fixer import load_syddanmark_with_fixes

df, metadata = load_syddanmark_with_fixes()
print(f"Coverage: {metadata['coverage_after_pct']:.1f}%")
```

## Data Quality Status

Efter fixen har Syddanmark nu:
- **A-prioritet**: 99.9% coverage (205,842 / 206,035)
- **B-prioritet**: 99.9% coverage (163,507 / 163,591)
- **C-prioritet**: 95.4% coverage (113,049 / 118,543)
- **D-prioritet**: 21.8% coverage (29,522 / 135,387)

## Bemærkninger
- Fixen påvirker ikke eksisterende responstider - kun manglende værdier beregnes
- D-prioritet har stadig lavt coverage (21.8%), men det er en stor forbedring fra ~0%
- Beregnede responstider er lige så valide som originale data da de bruger samme timestamps

