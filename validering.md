# VALIDERING AF PIPELINE OUTPUT

**Genereret:** 29. October 2025 kl. 13:16
**Formål:** Verificere at pipeline-beregninger matcher Nils Mulvads analyser

---

## 📊 EXECUTIVE SUMMARY

**RESULTAT:** ✅ Pipeline valideret med 100% præcision

- **Regioner sammenlignet:** 4 (Hovedstaden, Midtjylland, Sjælland, Syddanmark)
- **Postnumre analyseret:** 549
- **Præcision:** 100% af postnumre inden for 1% forskel
- **Maksimal afvigelse:** 0.05 minutter (3 sekunder)

**Konklusion:** Pipeline og Nils' beregninger er identiske. Små forskelle (0.0-0.05 min) skyldes kun afrundingsdifferencer.

---

## 🔬 METODOLOGI

**Sammenligningsgrundlag:**
- **Nils' data:** Regionale Excel-filer med aggregerede postnummer-beregninger
- **Pipeline data:** `3_output/current/01_alle_postnumre.xlsx`

**Sammenlignede metrics:**
1. Antal postnumre per region
2. Gennemsnitlig responstid per postnummer (minutter)
3. Antal kørsler (ture) per postnummer

**Præcisionskriterier:**
- ✅ **Excellent:** >95% af postnumre inden for 5% forskel
- ✅ **Good:** 90-95% inden for 5%
- ⚠️ **Acceptable:** 80-90% inden for 5%
- ❌ **Poor:** <80% inden for 5%

---

## 📍 REGIONAL SAMMENLIGNING

### Hovedstaden

| Metric | Nils | Pipeline | Status |
|--------|------|----------|--------|
| Antal postnumre | 98 | 98 | ✅ Match |
| Gennemsnitlig responstid | 11.0 min | 11.0 min | ✅ Match |
| Total antal ture | 230,101 | 230,101 | ✅ Match |

**Præcisionsanalyse:**
- Mean difference: +0.002 min
- Median difference: +0.005 min
- Std deviation: 0.030 min
- Max difference: 0.049 min

**Præcisionsfordeling:**
- Inden for 1%: 98/98 (100.0%)
- Inden for 5%: 98/98 (100.0%)

**Top 5 største afvigelser:**

| Postnr | Nils (min) | Pipeline (min) | Forskel (min) | Forskel (%) |
|--------|------------|----------------|---------------|-------------|
| 2200 | 7.95 | 7.90 | -0.05 | 0.62% |
| 3782 | 7.16 | 7.20 | +0.04 | 0.59% |
| 2100 | 8.85 | 8.80 | -0.05 | 0.56% |
| 1000 | 8.96 | 9.00 | +0.04 | 0.48% |
| 2500 | 9.26 | 9.30 | +0.04 | 0.46% |

---

### Midtjylland

| Metric | Nils | Pipeline | Status |
|--------|------|----------|--------|
| Antal postnumre | 153 | 153 | ✅ Match |
| Gennemsnitlig responstid | 12.6 min | 12.5 min | ✅ Match |
| Total antal ture | 180,946 | 180,946 | ✅ Match |

**Præcisionsanalyse:**
- Mean difference: -0.003 min
- Median difference: -0.004 min
- Std deviation: 0.030 min
- Max difference: 0.049 min

**Præcisionsfordeling:**
- Inden for 1%: 153/153 (100.0%)
- Inden for 5%: 153/153 (100.0%)

**Top 5 største afvigelser:**

| Postnr | Nils (min) | Pipeline (min) | Forskel (min) | Forskel (%) |
|--------|------------|----------------|---------------|-------------|
| 8900 | 6.64 | 6.60 | -0.04 | 0.66% |
| 7500 | 7.45 | 7.40 | -0.05 | 0.63% |
| 8700 | 7.74 | 7.70 | -0.04 | 0.56% |
| 7330 | 8.25 | 8.20 | -0.05 | 0.55% |
| 8600 | 8.55 | 8.50 | -0.05 | 0.55% |

---

### Sjælland

| Metric | Nils | Pipeline | Status |
|--------|------|----------|--------|
| Antal postnumre | 131 | 131 | ✅ Match |
| Gennemsnitlig responstid | 12.7 min | 12.7 min | ✅ Match |
| Total antal ture | 163,489 | 163,489 | ✅ Match |

**Præcisionsanalyse:**
- Mean difference: -0.001 min
- Median difference: -0.003 min
- Std deviation: 0.029 min
- Max difference: 0.050 min

**Præcisionsfordeling:**
- Inden for 1%: 131/131 (100.0%)
- Inden for 5%: 131/131 (100.0%)

**Top 5 største afvigelser:**

| Postnr | Nils (min) | Pipeline (min) | Forskel (min) | Forskel (%) |
|--------|------------|----------------|---------------|-------------|
| 4300 | 7.95 | 8.00 | +0.05 | 0.61% |
| 4200 | 7.95 | 8.00 | +0.05 | 0.58% |
| 4500 | 9.15 | 9.20 | +0.05 | 0.50% |
| 4990 | 9.14 | 9.10 | -0.04 | 0.47% |
| 4100 | 9.64 | 9.60 | -0.04 | 0.46% |

---

### Syddanmark

| Metric | Nils | Pipeline | Status |
|--------|------|----------|--------|
| Antal postnumre | 167 | 167 | ✅ Match |
| Gennemsnitlig responstid | 11.8 min | 11.8 min | ✅ Match |
| Total antal ture | 202,978 | 202,978 | ✅ Match |

**Præcisionsanalyse:**
- Mean difference: +0.003 min
- Median difference: +0.004 min
- Std deviation: 0.027 min
- Max difference: 0.050 min

**Præcisionsfordeling:**
- Inden for 1%: 167/167 (100.0%)
- Inden for 5%: 167/167 (100.0%)

**Top 5 største afvigelser:**

| Postnr | Nils (min) | Pipeline (min) | Forskel (min) | Forskel (%) |
|--------|------------|----------------|---------------|-------------|
| 6430 | 5.94 | 5.90 | -0.04 | 0.72% |
| 6270 | 8.05 | 8.00 | -0.05 | 0.58% |
| 7323 | 8.75 | 8.70 | -0.05 | 0.54% |
| 6780 | 8.95 | 9.00 | +0.05 | 0.53% |
| 5200 | 7.04 | 7.00 | -0.04 | 0.52% |

---

## 📈 SAMLET STATISTIK

| Metric | Værdi |
|--------|-------|
| Total postnumre sammenlignet | 549 |
| Gennemsnitlig afvigelse | 0.0001 min |
| Median afvigelse | 0.0000 min |
| Standardafvigelse | 0.0289 min |
| Maksimal afvigelse | 0.0499 min |

**Præcisionsfordeling på tværs af alle regioner:**

- ✅ Inden for 1%: 549/549 (100.0%)
- ✅ Inden for 5%: 549/549 (100.0%)

---

## ✅ KONKLUSION

**Pipeline er fuldt valideret:**

1. **100% postnummer-match:** Alle postnumre fra Nils' analyser findes i pipeline output
2. **100% præcision:** Alle beregninger inden for 1% afvigelse
3. **Identiske resultater:** Maksimal forskel på 0.05 min skyldes kun afrundingsfejl

**Implikationer:**
- Pipeline kan anvendes med fuld tillid til beregningernes korrekthed
- Resultater kan sammenlignes direkte med Nils' analyser
- Eventuelle forskelle i konklusioner skyldes ikke beregningsfejl, men fortolkning

---

## 🔧 TEKNISKE DETALJER

**Nils' input filer:**
- `validering/Hovedstaden20251027.xlsx` (sheet: Postnumre)
- `validering/Midtjylland20251027.xlsx` (sheet: Postnummer)
- `validering/RegionSjælland.xlsx` (sheet: postnummer)
- `validering/Syddanmark20251025.xlsx` (sheet: Postnummer)

**Pipeline output:**
- `3_output/current/01_alle_postnumre.xlsx` (sheet: Data)

**Validerings-script:**
- `2_processing/validate_against_nils.py`

**Kør validering igen:**
```bash
cd 2_processing
python3 validate_against_nils.py
```

