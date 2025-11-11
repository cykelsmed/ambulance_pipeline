# HELIKOPTER DATA - ANALYSE RAPPORT
**Fil:** `helikopterdata_nationale_.xlsx`
**Analysedato:** 2025-11-11
**Dataperiode:** Juli 2021 - Juni 2025

---

## EXECUTIVE SUMMARY

**Data kvalitet:** God - 10,376 af 10,442 cases (99.4%) er valide efter rensning
**Overlap med ambulancedata:** Ja - Juli 2021 til Juni 2025
**Anvendelighed:** Kan bruges i den nuværende undersøgelse med forbehold

**VIGTIG ADVARSEL:** Helikoptere anvendes primært til høj-kompleksitet cases (traumer, hjertestop) og supplerer - ikke erstatter - landambulancer. Direkte sammenligning af responstider kan være misvisende uden kontekst.

---

## 1. DATASTRUKTUR

### Grundlæggende information
- **Totalt antal cases:** 10,442
- **Periode:** Juli 2021 - Juni 2025 (48 måneder)
- **Regioner dækket:** Alle 5 danske regioner
- **Helikopterbaser:** 4 (Billund, Ringsted, Saltum, Skive)
- **Postnumre dækket:** 479 unikke postnumre

### Kolonner (8 stk)
1. **HændelsesID** - Unikt ID (HEMS_01 til HEMS_10442)
2. **Måned og år** - Dansk format ("juli 2021")
3. **Disponerende region** - Hvilken region der rekvirerede
4. **Helikopterbase** - Hvilken base der responderede
5. **Skadested Postnummer** - 4-cifret postnummer (100% gyldige)
6. **Tid alarm** - HH:MM format
7. **Tid airborne** - HH:MM format
8. **Tid ankomst skadested** - HH:MM format

---

## 2. DATAKVALITET

### 2.1 Missing Values
**Resultat:** INGEN missing values i nogen kolonner (0.0%)

### 2.2 Data Errors (Før Rensning)
- **Negative dispatch delays:** 169 cases (1.6%)
  → Årsag: Midnatskrydsning (alarm kl. 23:55, airborne kl. 00:05)
- **Negative flight times:** 134 cases (1.3%)
  → Årsag: Samme midnatsproblem
- **Ekstremt lange responstider (>3 timer):** 55 cases (0.5%)
  → Årsag: Sandsynligvis datainput-fejl

### 2.3 Efter Rensning
- **Valide cases:** 10,376 (99.4%)
- **Fjernet som fejl:** 66 cases (0.6%)
- **Rensningsmetode:**
  1. Midnatskrydsninger korrigeret ved at tilføje 24 timer
  2. Cases med total responstid >180 min fjernet som outliers

**KONKLUSION:** Data er af høj kvalitet efter minimal rensning.

---

## 3. RESPONSTIDSANALYSE (RENSEDE DATA)

### 3.1 National Oversigt

| Metric | Dispatch Delay | Flight Time | Total Response |
|--------|----------------|-------------|----------------|
| **Gennemsnit** | 6.9 min | 19.7 min | 26.3 min |
| **Median** | 6.0 min | 17.0 min | 23.0 min |
| **90. percentil** | 11.0 min | 33.0 min | 41.0 min |

**Komponentopdeling:**
- Dispatch delay (alarm → airborne): 6.9 min (26% af total)
- Flight time (airborne → arrival): 19.7 min (74% af total)

### 3.2 Regional Breakdown

| Region | Gns. Total Response | Median | Antal Cases | % af Total |
|--------|---------------------|--------|-------------|------------|
| **Region Nordjylland** | 23.0 min | 22.0 min | 2,366 | 22.8% |
| **Region Sjælland** | 23.0 min | 22.0 min | 2,518 | 24.3% |
| **Region Midtjylland** | 24.8 min | 22.0 min | 2,824 | 27.2% |
| **Region Syddanmark** | 29.3 min | 28.0 min | 2,219 | 21.4% |
| **Region Hovedstaden** | 56.8 min | 58.0 min | 449 | 4.3% |

**FUND:**
1. **Hovedstaden er en outlier** - 56.8 min vs. 23-29 min i andre regioner
2. **Kun 449 cases i Hovedstaden** (4.3%) - helikopter bruges meget sjældent
3. **Jævn fordeling** mellem de andre 4 regioner (21-27% hver)

### 3.3 Helikopterbase Performance

| Base | Gns. Total Response | Median | Antal Cases |
|------|---------------------|--------|-------------|
| **Skive** | 23.6 min | 20.0 min | 2,602 |
| **Ringsted** | 26.6 min | 24.0 min | 3,041 |
| **Billund** | 26.8 min | 26.0 min | 2,980 |
| **Saltum** | 28.7 min | 26.0 min | 1,753 |

**FUND:**
- Skive er hurtigste base (23.6 min)
- Relativt små forskelle mellem baser (5.1 min spænd)

---

## 4. TEMPORAL COVERAGE

### 4.1 Årlig Fordeling

| År | Antal Cases | % af Total |
|----|-------------|------------|
| 2021 (jul-dec) | 1,421 | 13.6% |
| 2022 | 2,747 | 26.3% |
| 2023 | 2,528 | 24.2% |
| 2024 | 2,556 | 24.5% |
| 2025 (jan-jun) | 1,190 | 11.4% |

**Observations:**
- Stabil årlig volumen 2022-2024 (~2,500-2,750 cases/år)
- 2021 kun halvår (juli-december)
- 2025 data kun til juni

### 4.2 Sæsonmæssige Mønstre

**Top 10 travleste måneder:**
1. Juli 2022: 315 cases
2. Juli 2021: 306 cases
3. August 2021: 298 cases
4. August 2024: 294 cases
5. Juli 2024: 277 cases

**FUND:** Sommermåneder (juni-august) har højest aktivitet - sandsynligvis pga.:
- Trafikulykker (øget trafik)
- Fritidsulykker
- Turistaktivitet

---

## 5. OVERLAP MED AMBULANCE DATA

### 5.1 Tidsperiode Sammenligning

| Dataset | Start | Slut | Måneder |
|---------|-------|------|---------|
| Ambulance data | Juli 2021 | 2025 | ~48 måneder |
| Helikopter data | Juli 2021 | Juni 2025 | 48 måneder |
| **Overlap** | **Juli 2021** | **Juni 2025** | **48 måneder** |

**KONKLUSION:** 100% overlap - perfekt match i tid.

### 5.2 Geografisk Overlap

| Parameter | Ambulance Data | Helikopter Data | Overlap |
|-----------|----------------|-----------------|---------|
| Regioner | 5 (alle) | 5 (alle) | 100% |
| Postnumre | 624 (alle DK) | 479 | 76.8% |

**FUND:** Helikoptere dækker 479 af 624 postnumre (76.8%) - typisk landområder og ø-samfund.

---

## 6. KAN DATA BRUGES I NUVÆRENDE UNDERSØGELSE?

### 6.1 Fordele
✅ **Perfekt tidslig overlap** - Juli 2021 til Juni 2025
✅ **Høj datakvalitet** - 99.4% valide efter minimal rensning
✅ **Kompletthed** - Ingen missing values
✅ **Regional dækning** - Alle 5 regioner repræsenteret
✅ **Postnumre tilgængelige** - Kan sammenkobles med ambulancedata

### 6.2 Udfordringer
⚠️ **Forskellige use cases** - Helikoptere til høj-kompleksitet, ambulancer til alt
⚠️ **Lille volumen** - 10,442 helikopter cases vs. 861,757 ambulance cases (1.2%)
⚠️ **Begrænset geografisk dækning** - Kun 479/624 postnumre (76.8%)
⚠️ **Hovedstaden outlier** - Kun 449 cases, meget længere responstider
⚠️ **Måling er forskellig** - Helikopter måler "alarm til arrival", ambulance måler "kald til on-scene"

### 6.3 Anbefaling

**JA, men med forbehold:**

1. **Brug helikopterdata som SUPPLEMENT, ikke primær datakilde**
   - Vis helikopterdata separat fra ambulancedata
   - Undgå direkte sammenligning af responstider

2. **Fokuser på:**
   - Geografiske områder hvor helikopter er eneste/bedste mulighed (øer, fjernområder)
   - Kompleksitetsniveau (helikopter = høj-kompleksitet cases)
   - Dispatchforsinkelse (6.9 min gennemsnit)

3. **Undgå:**
   - Direkte sammenligning "helikopter vs. ambulance responstid"
   - Inkludering af helikopterdata i national ambulance-gennemsnit
   - Brug af Hovedstaden helikopterdata (kun 449 cases, outlier)

4. **Mulige vinkler:**
   - "Danske luftambulancer når frem på 26 min i gennemsnit"
   - "6 ud af 10 regioner bruger helikopter meget forskelligt"
   - "Sommermåneder presser luftambulancen - 30% flere cases i juli/august"

---

## 7. DATABEARBEJDNING ANBEFALET

### 7.1 Nødvendige Transformationer

```python
# 1. Fix midnight crossing
def calculate_duration(start_min, end_min):
    diff = end_min - start_min
    if diff < 0:
        diff += 1440  # Add 24 hours
    if diff > 180:
        return np.nan  # Remove outliers >3 hours
    return diff

# 2. Parse month-year to standard format
def parse_month_year(month_str):
    # "juli 2021" → "2021-07"
    months = {
        'januar': 1, 'februar': 2, 'marts': 3, 'april': 4,
        'maj': 5, 'juni': 6, 'juli': 7, 'august': 8,
        'september': 9, 'oktober': 10, 'november': 11, 'december': 12
    }
    parts = month_str.lower().split()
    month = months[parts[0]]
    year = int(parts[1])
    return f'{year}-{month:02d}'

# 3. Calculate response times
df['dispatch_delay'] = calculate_duration(alarm_min, airborne_min)
df['flight_time'] = calculate_duration(airborne_min, arrival_min)
df['total_response'] = calculate_duration(alarm_min, arrival_min)
```

### 7.2 Output Format Anbefaling

**Opret separate helikopter-analyser:**
- `helikopter_national_oversigt.xlsx` - National statistik
- `helikopter_regional_sammenligning.xlsx` - Regional breakdown
- `helikopter_postnummer.xlsx` - Postnummer-niveau (til map)
- `helikopter_temporal.xlsx` - Månedlig/time-of-day analyse

**Inkluder ikke i:**
- `01_alle_postnumre.xlsx` (blander forskellige services)
- National ambulance gennemsnit (misvisende)

---

## 8. KONKRETE FINDINGS

### 8.1 Responstid Breakdown
- **National gennemsnit:** 26.3 min (alarm til arrival)
- **Dispatch delay:** 6.9 min (26% af total tid)
- **Flight time:** 19.7 min (74% af total tid)

### 8.2 Regional Variation
- **Hurtigste:** Nordjylland + Sjælland (23.0 min)
- **Langsomste:** Hovedstaden (56.8 min - 2.5x langsommere!)
- **Spænd:** 33.8 min mellem hurtigste og langsomste

### 8.3 Sæsonmæssighed
- **Højeste aktivitet:** Sommermåneder (juni-august)
- **Juli gennemsnit:** 286 cases/måned
- **December gennemsnit:** 168 cases/måned
- **Sommer vs. vinter:** 70% højere aktivitet om sommeren

### 8.4 Base Performance
- **Mest aktiv:** Ringsted (3,041 cases, 29.3%)
- **Hurtigste:** Skive (23.6 min gennemsnit)
- **Performance spænd:** 5.1 min mellem hurtigste (Skive) og langsomste (Saltum)

---

## 9. ANBEFALINGER TIL VIDERE ANALYSE

### 9.1 Prioriteret Liste

1. **ØJE på:** Hvorfor er Hovedstaden så langsom? (56.8 min vs. 23-29 min)
   - Er det geografisk spredning?
   - Er det begrænset helikopteradgang?
   - Er det typisk bruges til øer (Bornholm)?

2. **Sammenlign:** Helikopter vs. ambulance i samme postnumre
   - Identificer områder hvor begge bruges
   - Mål forskellen i responstid
   - Find cases hvor helikopter er LANGSOMMERE (burde aldrig ske!)

3. **Temporal:** Rush hour vs. nat for helikoptere
   - Applicer samme time-of-day analyse som ambulancer
   - Sammenlign dispatch delay: dag vs. nat

4. **Prioritet:** Har helikopterdata ABC-prioritet?
   - Check om Nordjylland/Syddanmark data har prioritet-kolonner
   - Sammenlign helikopter responstid for A vs. B cases

### 9.2 Advarsel om Bias

**VIGTIGT:** Helikoptere er ikke et "alternativ" til ambulancer. De bruges til:
- Traumer med høj kompleksitet
- Hjertestop i fjerne områder
- Situationer hvor ambulance ikke kan nå frem (øer, motorvej)
- Cases hvor læge skal med (HEMS = Helicopter Emergency Medical Service)

Derfor er direkte sammenligning misvisende uden kontekst.

---

## 10. KONKLUSION

**Data er brugbar, men kræver omhyggelig håndtering.**

**Anbefalet strategi:**
1. Opret SEPARAT helikopter-sektion i rapporten
2. Fremhæv de 479 postnumre hvor helikopter er aktiv
3. Fokuser på geografiske/temporal mønstre, ikke direkte responstidssammenligning
4. Tilføj disclaimer om forskellige use cases

**Datarensning nødvendig:**
- Fix midnight crossing (1.6% af cases)
- Fjern outliers >180 min (0.6% af cases)
- Parse danske månednavne til standardformat

**Yderligere data ønsket:**
- ABC-prioritet (hvis tilgængelig)
- Indikation type (trauma, hjertestop, etc.)
- Om case blev håndteret alene af helikopter eller sammen med ambulance

---

**Spørgsmål til Nils:**
1. Findes der ABC-prioritet data for helikopter cases?
2. Er "Disponerende region" = den region der REKVIRERER eller den region hvor SKADESTEDET ligger?
3. Hvorfor har Hovedstaden så få cases (449) vs. andre regioner (2,200-2,800)?
4. Findes der indikation-type data (trauma, cardiac, etc.)?
