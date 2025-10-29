# PLAN: Tidsmæssige Analyser (PRIORITERET)

**Projekt:** Ambulance Pipeline - TV2 Responstidsanalyse
**Oprettet:** 29. oktober 2025
**Status:** 🟡 Ikke påbegyndt (afventer prioritering)
**Estimeret tid:** 6-8 timer (nedprioriteret fra 10-15t)

---

## ⚡ FOKUS: Quick Wins Med Størst Impact

Baseret på hård prioritering fokuserer vi på:

1. **🥇 PRIORITET 1: Tid-på-Døgnet** ("Rush Hour") - 3-4 timer
   - Nemmest at implementere
   - Klar journalistisk vinkel
   - Simpel at verificere

2. **🥈 PRIORITET 2: Sæsonvariation** ("Vinterkrise") - 2-3 timer
   - Genbruger samme kode som Rush Hour
   - Aktuel vinkel (vinter kommer)
   - Mindre kontroversiel end prioritetsændringer

3. **🥉 SENERE: Prioritetsændringer** ("Når 112 Tager Fejl") - GEMMES TIL SENERE
   - Mest kompleks
   - Kræver ekspert-validering
   - Potentielt kontroversiel (kræver juridisk review?)

**BESLUTNING: Start kun med Prioritet 1 + 2**

---

## 🥇 Analyse 1: Tid-på-Døgnet ("Rush Hour") - PRIORITET 1

### Journalistisk Vinkel
> "Er ambulancerne langsommere i myldretiden? Ny analyse viser hvordan responstider varierer time for time."

### Datakilde
- **Fil:** `1_input/Nordjylland20251027.xlsx`
- **Ark:** `Nordjylland` (rådata, 180,267 rækker)
- **Nøglekolonner:** `Tid_HændelseOprettet`, `ResponstidMinutter`, `Hastegrad ved oprettelse`

### Metode (SIMPLIFICERET)
1. Filtrér til A-kørsler
2. Udtræk time (0-23)
3. Beregn median per time
4. Output: Excel + CSV

**SKÅRET FRA MVP:**
- ❌ Weekend vs Hverdag split (kan tilføjes senere)
- ❌ By vs Land opdeling (kræver ekstra work)
- ❌ PNG auto-generering (Datawrapper håndterer dette)
- ❌ Multi-region test (kun Nordjylland i første omgang)

### MVP Todo Liste (KUN ESSENTIALS)

- [ ] **Kode (2-3 timer)**
  - [ ] Opret `temporal_analysis.py` modul
  - [ ] Læs Nordjylland rådata
  - [ ] Filtrér til A-kørsler
  - [ ] Udtræk time + beregn median per time
  - [ ] Export til Excel + CSV

- [ ] **Test & Output (30 min)**
  - [ ] Kør på Nordjylland data
  - [ ] Verificer at timer med <100 kørsler markeres
  - [ ] Generér key findings tekstfil (3 bullet points)

- [ ] **Dokumentation (30 min)**
  - [ ] Tilføj kort beskrivelse til README
  - [ ] Dokumentér TOP 3 faldgruber

---

## 🥈 Analyse 2: Sæsonvariation ("Vinterkrise") - PRIORITET 2

### Journalistisk Vinkel
> "Vinterkrise: Ambulancer 19% langsommere i december end i marts."

### Datakilde
- **Fil:** `1_input/Nordjylland20251027.xlsx`
- **Ark:** `Nordjylland` (samme som Rush Hour - GENBRUGER KODE!)
- **Nøglekolonner:** `Måned_HændelseOprettet`, `ResponstidMinutter`

### Metode (SIMPLIFICERET)
1. Filtrér til A-kørsler
2. Gruppér per måned (1-12)
3. Beregn median per måned
4. Output: Excel + CSV

**SKÅRET FRA MVP:**
- ❌ Covid-periode isolation (acceptér at 2021-2022 kan være afvigende)
- ❌ 5-års trend-analyse (bare vis samlet gennemsnit)
- ❌ DMI vejrdata sammenkørsel (for komplekst)
- ❌ Vinter vs Sommer t-test (ikke nødvendigt journalistisk)

### MVP Todo Liste (KUN ESSENTIALS)

- [ ] **Kode (1-2 timer)**
  - [ ] Udvid `temporal_analysis.py` med måned-funktion
  - [ ] Gruppér per måned (genbruger Rush Hour kode)
  - [ ] Beregn median per måned
  - [ ] Export til Excel + CSV

- [ ] **Test & Output (30 min)**
  - [ ] Kør på Nordjylland data
  - [ ] Verificer at december/januar/februar er langsomst
  - [ ] Key findings: "December er XX% langsommere end marts"

- [ ] **Dokumentation (15 min)**
  - [ ] Tilføj advarsel: "Korrelation ≠ kausalitet"
  - [ ] Note om Covid-periode (2021-2022 muligvis afvigende)

---

## 🥉 Analyse 3: Prioritetsændringer - UDSAT TIL SENERE

### Hvorfor Udsat?
- ⚠️ Mest kompleks implementering
- ⚠️ Kræver ekspert-validering (upgrade ≠ fejl)
- ⚠️ Potentielt kontroversiel (juridisk review?)
- ⚠️ Kun Hovedstaden-data anvendelig (Sjælland data korrupt)

### Når I Genoptager Dette Senere:
Se original "Analyse 2" sektion længere nede i dokumentet for fuld beskrivelse.

**Estimat når I vender tilbage:** 4-5 timer

---

## 🚨 NEDPRIORITERET INDHOLD HERUNDER

### Journalistisk Vinkel
> "1 ud af 7 akutopkald får ændret prioritet EFTER ambulancen er afsted. Hvad betyder det for responstiden?"

### Datakilde
- **Fil:** `1_input/Hovedstaden20251027.xlsx`
- **Ark:** `RegionHovedstaden` (rådata, 513,897 rækker)
- **Nøglekolonner:**
  - `Forste_respons` (A/B/C - initial prioritet)
  - `Afsluttende_respons` (A/B/C - final prioritet)
  - `ResponsMinutter` (float)

### Metode
- Sammenlign `Forste_respons` med `Afsluttende_respons`
- Kategorisér:
  - **UNCHANGED:** A→A, B→B (korrekt vurdering)
  - **UPGRADED:** B→A, C→A, C→B (blev mere akut)
  - **DOWNGRADED:** A→B, A→C, B→C (blev mindre akut)
- Beregn responstid-forskel mellem kategorier
- Analysér HVORNÅR ændringer sker (tidslinje)

### Forventede Fund (fra agent-analyse)
- 15.5% af opkald ændrer prioritet
- 14.9% UPGRADES (B→A primært)
- 0.7% DOWNGRADES
- Upgraded kørsler er 41% langsommere (fordi ambulancen startede langsomt)

### Output
- Excel: `3_output/temporal/prioritets_analyse.xlsx` (3 ark)
  - Ark 1: Summary (antal + % per kategori)
  - Ark 2: Responstid-sammenligning
  - Ark 3: Tidslinje (minutter efter alarm)
- Tekstfil: Key findings + advarsler

### Todo Liste

- [ ] **Foundation**
  - [ ] Opret `2_processing/analyzers/priority_analysis.py`
  - [ ] Implementér kategoriserings-logik

- [ ] **Databehandling**
  - [ ] Læs Hovedstaden rådata
  - [ ] Valider: Check at begge prioritetskolonner findes
  - [ ] Drop rækker med missing priority data
  - [ ] **VIGTIGT:** Verificér at Sjælland data IKKE bruges (100% downgrade = datakvalitetsproblem)

- [ ] **Kategorisering**
  - [ ] Implementér comparison-logik:
    ```python
    if forste == afsluttende:
        kategori = "UNCHANGED"
    elif (forste == 'B' and afsluttende == 'A') or (forste == 'C' and afsluttende in ['A', 'B']):
        kategori = "UPGRADED"
    elif (forste == 'A' and afsluttende in ['B', 'C']) or (forste == 'B' and afsluttende == 'C'):
        kategori = "DOWNGRADED"
    ```
  - [ ] Test på sample data
  - [ ] Valider: Summen af kategorier = total antal kørsler

- [ ] **Statistisk Analyse**
  - [ ] Beregn antal + % per kategori
  - [ ] Beregn median responstid per kategori
  - [ ] Sammenlign: Upgraded vs Unchanged A-kørsler (% forskel)
  - [ ] **Tidslinje:** Hvornår sker upgrades? (hvis tidsstempel findes)

- [ ] **Fortolkning & Advarsler**
  - [ ] Dokumentér: "Upgrade ≠ fejl" (patient kan forværres)
  - [ ] Identificér early vs late upgrades (inden/efter 5 min)
  - [ ] Beregn baseline: Hvad er "normal" upgrade-rate? (ekspertinterview?)

- [ ] **Output & Test**
  - [ ] Generér 3-arks Excel-fil
  - [ ] Skriv key findings med journalistiske angles
  - [ ] Inkludér advarsels-sektion (fortolkning)
  - [ ] Test: Kan andre regioner bruges? (Midtjylland har `OpNedgradering`)

- [ ] **Dokumentation**
  - [ ] Forklar metodiske valg (hvorfor kun Hovedstaden)
  - [ ] Dokumentér Sjællands dataproblem
  - [ ] Lav ekspertspørgsmål til follow-up interviews

---

## ❄️ Analyse 3: Sæsonvariation ("Vinterkrise")

### Journalistisk Vinkel
> "Ambulancerne er 19% langsommere i december end i marts. Er det vejret, trafikken eller manglende beredskab?"

### Datakilde
- **Fil:** `1_input/Nordjylland20251027.xlsx`
- **Ark:** `Nordjylland` (rådata, 5 års data 2021-2025)
- **Nøglekolonner:**
  - `År_HændelseOprettet` (int)
  - `Måned_HændelseOprettet` (int, 1-12)
  - `ResponstidMinutter` (float)
  - `Hastegrad ved oprettelse` (A/B)

### Metode
- Filtrér til A-kørsler
- Gruppér per måned (1-12)
- Beregn median responstid per måned
- Sammenlign vinter (dec, jan, feb) vs sommer (jun, jul, aug)
- **Kritisk:** Isolér Covid-periode (2021-2022) fra post-Covid (2023-2024)

### Forventede Fund (fra agent-analyse)
- December: 72 min gennemsnit (værst)
- Marts: 59 min gennemsnit (bedst)
- 19% langsommere om vinteren

### Output
- Excel: `3_output/temporal/saeson_analyse.xlsx` (3 ark)
  - Ark 1: Månedlig gennemsnit (alle år samlet)
  - Ark 2: År-til-år sammenligning (trend-analyse)
  - Ark 3: Vinter vs Sommer statistik
- CSV: Datawrapper månedskurve
- Tekstfil: Key findings + fortolknings-advarsler

### Todo Liste

- [ ] **Foundation**
  - [ ] Udvid `temporal_analysis.py` med sæson-modul
  - [ ] Implementér måned-gruppering logik

- [ ] **Databehandling**
  - [ ] Læs Nordjylland rådata (alle år)
  - [ ] Filtrér til A-kørsler
  - [ ] Valider: Check at år + måned kolonner findes
  - [ ] **Covid-markering:** Tag 2021-2022 som separat segment

- [ ] **Månedlig Analyse**
  - [ ] Gruppér per måned (1-12)
  - [ ] Beregn per måned:
    - [ ] Median responstid
    - [ ] Antal kørsler
    - [ ] Afvigelse fra årsmean (%)
  - [ ] Valider: Hver måned skal have ≥500 kørsler

- [ ] **Sæson-Sammenligning**
  - [ ] Definér sæsoner:
    - Vinter: Dec (12), Jan (1), Feb (2)
    - Forår: Mar (3), Apr (4), Maj (5)
    - Sommer: Jun (6), Jul (7), Aug (8)
    - Efterår: Sep (9), Okt (10), Nov (11)
  - [ ] Beregn median per sæson
  - [ ] Beregn % forskel vinter vs sommer
  - [ ] Test statistisk signifikans (t-test eller Mann-Whitney)

- [ ] **Trend-Analyse (Optional)**
  - [ ] Bliver problemet værre? 5-års udvikling
  - [ ] Sammenlign vinter 2021 vs vinter 2024
  - [ ] Lineær regression: Trend over tid

- [ ] **Fortolkning & Advarsler**
  - [ ] **Advarsel 1:** Korrelation ≠ kausalitet
  - [ ] **Advarsel 2:** Covid-effekt (lockdowns, færre ulykker)
  - [ ] **Advarsel 3:** Organisatoriske ændringer (kontakt regioner)
  - [ ] **Advarsel 4:** Vejr vs Sæson (sne den dag vs generel vinter)

- [ ] **Output & Test**
  - [ ] Generér 3-arks Excel-fil
  - [ ] Generér CSV til Datawrapper (månedskurve)
  - [ ] Skriv key findings + disclaimer
  - [ ] Test på andre regioner (Hovedstaden har også 5 års data?)

- [ ] **Supplerende Data (Optional)**
  - [ ] Sammenkør med DMI vejrdata (temperatur, nedbør)
  - [ ] Kontakt regioner: Har beredskabet ændret sig i perioden?
  - [ ] Analyse: Ferieperioder (jul, sommer) vs normal måneder

- [ ] **Dokumentation**
  - [ ] Forklar metodiske valg (hvorfor median, ikke mean?)
  - [ ] Dokumentér Covid-perioden isolation
  - [ ] Lav liste over mulige ikke-vejr-forklaringer

---

## 🏗️ Teknisk Implementering

### Arkitektur

```
ambulance_pipeline_pro/
├── pipeline.py                          # Eksisterende (aggregeret data)
├── temporal_pipeline.py                 # NYT: Kører tidsmæssige analyser
├── 1_input/                             # Uændret
├── 2_processing/
│   ├── config.yaml                      # Uændret
│   ├── loader.py                        # Uændret
│   ├── normalizer.py                    # Uændret
│   └── analyzers/
│       ├── core.py                      # Eksisterende (postnummer-analyser)
│       ├── export.py                    # Eksisterende
│       ├── temporal_analysis.py         # NYT: Rush hour + Sæson
│       └── priority_analysis.py         # NYT: Prioritetsændringer
├── 3_output/
│   ├── current/                         # Eksisterende output
│   └── temporal/                        # NYT: Tidsmæssige analyser
│       ├── rush_hour_analyse.xlsx
│       ├── prioritets_analyse.xlsx
│       ├── saeson_analyse.xlsx
│       └── key_findings/                # Tekstfiler til journalist
└── TEMPORAL_ANALYSE_GUIDE.md            # NYT: Bruger-manual
```

### Hvorfor Separat Pipeline?

**Fordele:**
- ✅ Klare datakilder (aggregeret vs rådata)
- ✅ Forskellige execution-tider (6 sek vs 2-5 min)
- ✅ Lettere fejlfinding
- ✅ Kan køres uafhængigt

**Ulemper:**
- ⚠️ To scripts at vedligeholde
- ⚠️ Duplikering af nogle funktioner (loader, validering)

**Beslutning:** Separat er bedst for fleksibilitet og klarhed.

### Todo: Teknisk Setup

- [ ] **Opret nye filer**
  - [ ] `temporal_pipeline.py` (hovedscript)
  - [ ] `2_processing/analyzers/temporal_analysis.py`
  - [ ] `2_processing/analyzers/priority_analysis.py`
  - [ ] `3_output/temporal/` folder
  - [ ] `3_output/temporal/key_findings/` folder

- [ ] **Genbrugsmoduler**
  - [ ] Implementér fælles `load_raw_data(file, sheet, min_rows)` funktion
  - [ ] Implementér fælles `validate_time_column(df, col_name)` funktion
  - [ ] Implementér fælles `export_to_excel(df, filename, sheet_names)` funktion

- [ ] **Configuration**
  - [ ] Udvid `config.yaml` med temporal-settings:
    ```yaml
    temporal_analysis:
      rush_hour:
        min_incidents_per_hour: 100
        regions: ['nordjylland', 'hovedstaden']
      priority_changes:
        regions: ['hovedstaden']  # Kun pålidelig kilde
      seasonal:
        min_incidents_per_month: 500
        covid_years: [2021, 2022]
    ```

- [ ] **Testing**
  - [ ] Unit tests for kategorisering-logik (priority changes)
  - [ ] Integration test: Kør alle 3 analyser på sample data
  - [ ] Valider output-filformater (Excel kan åbnes, CSV import virker)
  - [ ] Performance test: Måle execution-tid per analyse

---

## 📈 Forventede Resultater & Journalistiske Produkter

### Analyse 1: Rush Hour

**Overskrifter:**
- "Ambulancerne er 15% langsommere i myldretiden"
- "Ring ikke til 112 mellem 17-19 hvis du kan undgå det"

**Grafik:**
- Linjediagram: Responstid time-for-time (0-24)
- Søjlediagram: Antal kørsler per time (viser peak hours)

**Key Quote til Artikel:**
> "Analysen viser at responstiderne topper kl. 17-19, hvor ambulancerne kæmper mod aftentrafikken. I disse timer tager det i gennemsnit 12.3 minutter før hjælpen når frem - 15% langsommere end om natten."

### Analyse 2: Prioritetsændringer

**Overskrifter:**
- "1 ud af 7 akutopkald bliver opgraderet undervejs"
- "Når vagtcentralen fejlvurderer: Opgraderede opkald venter 41% længere"

**Grafik:**
- Pie chart: Unchanged (85%) vs Upgraded (15%) vs Downgraded (0.7%)
- Bar chart: Responstid-sammenligning mellem kategorier

**Key Quote til Artikel:**
> "Hvis dit opkald først vurderes som 'ikke-livstruende' men senere opgraderes, har du allerede tabt værdifulde minutter. Vores analyse viser at disse opkald kommer 41% langsommere end dem der straks vurderes korrekt."

**Kritisk Advarsel:**
> "Det er vigtigt at understrege at en upgrade ikke nødvendigvis er en fejl fra vagtcentralen. I mange tilfælde forværres patientens tilstand efter opkaldet, f.eks. hvis en person får hjertestop EFTER at have ringet."

### Analyse 3: Sæsonvariation

**Overskrifter:**
- "Vinterkrise: Ambulancer 19% langsommere i december"
- "December er årets værste måned for akuthjælp"

**Grafik:**
- Linjediagram: Median responstid per måned (1-12)
- Skyggede områder: Vinter vs Sommer
- Inset: 5-års trend (bliver det værre?)

**Key Quote til Artikel:**
> "I december måned tager det i gennemsnit 10.2 minutter før ambulancen når frem - 19% langsommere end i marts. Det kan være forskellen på liv og død ved hjertestop, hvor hvert minut tæller."

**Kritisk Advarsel:**
> "Analysen viser et klart mønster, men kan ikke isolere én enkelt årsag. Det kan være vejret (is, sne), trafikken (juletravlhed), eller færre ambulancer på vagt. Det kræver videre undersøgelse at afgøre den præcise årsag."

---

## ⚠️ Kritiske Metodiske Advarsler

### 1. Datakvalitet

**Problem:** Ikke alle regioner har samme datakvalitet i rådata

**Verificeret Pålidelige:**
- ✅ Nordjylland: Komplet, ren, 5 års data
- ✅ Hovedstaden: Mest detaljeret (26 kolonner)

**Kendt Problematiske:**
- ⚠️ Sjælland: 100% priority downgrade i sample (datakvalitetsproblem)
- ⚠️ Syddanmark: 76.7% hospital-transporter (ikke akut)
- ⚠️ Midtjylland: Time-formatering inkonsistent

**Anbefaling:** Start med Nordjylland + Hovedstaden, test andre regioner grundigt før publicering.

### 2. Statistisk Signifikans vs Journalistisk Relevans

**Problem:** Med 180K+ kørsler er næsten alle forskelle statistisk signifikante

**Løsning:** Sæt journalistisk threshold
- Forskel skal være >10% ELLER >2 minutter for at være relevant
- Eksempel: 9.1 min vs 9.3 min = statistisk signifikant, men irrelevant journalistisk

### 3. Korrelation ≠ Kausalitet

**Problem:** At responstider er langsomme kl 17 betyder ikke at det ER trafikken

**Alternative Forklaringer:**
- Flere alvorlige ulykker på det tidspunkt
- Vagtskifte-forsinkelser
- Færre ambulancer på vagt om aftenen
- Geografisk fordeling af opkald ændrer sig

**Løsning:** Brug forsigtige formuleringer
- ✅ "Mønster", "tendens", "sammenfald"
- ❌ "Forårsaget af", "skyldes", "grundet"

### 4. Regional Forskellighed

**Problem:** Nordjylland ≠ Hovedstaden

**Forskelle:**
- Hovedstaden: Tæt by, trafik-domineret, korte afstande
- Nordjylland: Spredt bebyggelse, afstands-domineret, lange ture

**Løsning:**
- Lav separate analyser per region
- IKKE nationale gennemsnit (skjuler lokale mønstre)
- Sammenlign trends, ikke absolutte tal

### 5. Missing Data & Outliers

**Problem:** Ikke alle kørsler har komplette data

**Check Altid:**
- Hvor mange rækker droppes pga. missing data?
- Fjern outliers (responstid >120 min = datainput-fejl)
- Dokumentér hvor stort datasæt analysen baseres på

**Eksempel:**
> "Analysen baseres på 84,243 A-kørsler i Nordjylland fra 2021-2025. 387 kørsler (0.5%) blev ekskluderet grundet manglende tidsstempler."

---

## 📋 SIMPLIFICERET Roadmap (MVP Focus)

### ⚡ Sprint 1: Rush Hour Analysis (3-4 timer)

**Dag 1 - Morgen (2 timer):**
- [ ] Opret `temporal_analysis.py` modul
- [ ] Implementér time-udtrækning fra Nordjylland rådata
- [ ] Beregn median responstid per time (0-23)
- [ ] Generér Excel output

**Dag 1 - Eftermiddag (1-2 timer):**
- [ ] Generér Datawrapper CSV
- [ ] Skriv key findings tekstfil (3 bullets)
- [ ] Test: Verificer at peak hours identificeres korrekt
- [ ] Opdatér README med kort beskrivelse

**Deliverable:** Publikationsklar Rush Hour analyse til TV2

---

### ⚡ Sprint 2: Sæsonvariation (2-3 timer)

**Dag 2 - Morgen (1-2 timer):**
- [ ] Udvid `temporal_analysis.py` med måned-funktion
- [ ] Genbruge Rush Hour kode (kun ændre gruppering fra "hour" til "month")
- [ ] Beregn median responstid per måned (1-12)
- [ ] Generér Excel + CSV output

**Dag 2 - Eftermiddag (1 time):**
- [ ] Skriv key findings (fokus: "December XX% langsommere end marts")
- [ ] Tilføj advarsel om korrelation ≠ kausalitet
- [ ] Opdatér README

**Deliverable:** Publikationsklar Sæson-analyse til TV2

---

### 🎯 Total MVP Timeline: 6-8 timer (fordelt over 2 dage)

**IKKE inkluderet i MVP:**
- ❌ Prioritetsændringer-analyse (gemmes til senere)
- ❌ Separat `temporal_pipeline.py` script (kør direkte fra Python)
- ❌ Auto-genererede PNG grafer (Datawrapper håndterer dette)
- ❌ Multi-region test (kun Nordjylland)
- ❌ Ekspert-review (kan gøres efter publicering)
- ❌ Omfattende dokumentation (kun README update)

---

## 🎯 Succeskriterier (REVIDERET - MVP Focus)

### ✅ Sprint 1 Success (Rush Hour)
- [ ] Excel-fil med time-for-time data (0-23) genereres korrekt
- [ ] CSV til Datawrapper kan importeres uden fejl
- [ ] Key findings indeholder mindst 3 publikationsklare indsigter
- [ ] Peak hours (9-12) og slowest hours (17-19) identificeres

**Definition of Done:**
> "En journalist kan skrive en artikel baseret på output UDEN at stille opklarende spørgsmål"

### ✅ Sprint 2 Success (Sæsonvariation)
- [ ] Excel-fil med måned-for-måned data (1-12) genereres korrekt
- [ ] December identificeres som langsomste måned
- [ ] % forskel mellem bedste og værste måned beregnes korrekt
- [ ] Advarsel om fortolkning inkluderet i output

**Definition of Done:**
> "Output kan bruges direkte i TV2-artikel med overskrift: 'Vinterkrise i akuthjælpen'"

### 🚫 IKKE Succeskriterier for MVP
- ❌ Alle 3 analyser (kun 2 i MVP)
- ❌ Multi-region (kun Nordjylland acceptabelt)
- ❌ Ekspert-review (kan ske efter publicering)
- ❌ PNG-grafer (Datawrapper laver dem)
- ❌ Omfattende dokumentation (README-update er nok)

---

## 📞 Beslutninger Taget (Hård Prioritering)

1. **Prioritering:** ✅ KUN 2 analyser (Rush Hour + Sæson), ikke 3
2. **Timeline:** ✅ MVP kan leveres på 6-8 timer fordelt over 2 dage
3. **Grafikproduktion:** ✅ Kun data-filer, Datawrapper laver graferne
4. **Multi-region:** ✅ Kun Nordjylland (mest pålidelige data)
5. **Ekspert-review:** ✅ Ikke før publicering (kan ske bagefter hvis nødvendigt)
6. **Vejrdata:** ✅ IKKE inkluderet (for komplekst for MVP)

## 🚀 Klar til Start?

**Hvis I vil implementere denne MVP-plan:**

1. Start med Sprint 1 (Rush Hour) - 3-4 timer
2. Test output grundigt
3. Hvis tilfredsstillende → Sprint 2 (Sæson) - 2-3 timer
4. Publicér resultaterne
5. Evaluer respons før I beslutter om Prioritetsændringer-analyse skal laves senere

**MVP kan være klar inden for 2 arbejdsdage** (hvis dedikeret tid)

---

## 📚 Ressourcer & Referencer

### Datakvalitet (fra tidligere verification)
- Nordjylland: 100% verificeret korrekt ✅
- Hovedstaden: 100% verificeret korrekt ✅
- Sjælland: 100% verificeret korrekt ✅ (på aggregeret niveau)
- Midtjylland: 96.7% verificeret korrekt ✅
- Syddanmark: Kunne ikke verificeres (responstid-kolonne tom) ⚠️

### Eksisterende Output (refereres til)
- `3_output/current/01_alle_postnumre.xlsx` (624 postnumre)
- `3_output/current/02_top_10_værste_VALIDERET.xlsx`
- `3_output/current/04_regional_sammenligning.xlsx`
- `VERIFICATION.md` (metodedokumentation)

### Ekspertkilder (til follow-up interviews)
- Professor Søren Mikkelsen (Syddansk Universitet)
- Forskningsleder Ulla Væggemose (Region Midtjylland)
- Forskningsansvarlig Morten Breinholt Søvsø (Aalborg UH)
- Forskningsleder Helle Collatz Christensen (Region Sjælland)

---

## ✅ Definition of Done

**En analyse er "færdig" når:**

1. [ ] Koden kører fejlfrit på alle målregioner
2. [ ] Output-filer genereres korrekt (Excel + CSV + tekstfil)
3. [ ] Dokumentation forklarer:
   - Hvad analysen viser
   - Hvordan den beregnes
   - Hvilke advarsler der gælder
4. [ ] Key findings er journalistisk formuleret (klar til artikel)
5. [ ] Metodiske faldgruber er dokumenteret
6. [ ] Test på sample data viser forventede resultater
7. [ ] Code review er gennemført (anden person kan forstå koden)
8. [ ] User manual er opdateret (hvordan kører man analysen?)

---

## 🔄 Vedligeholdelse & Opdatering

**Når nye data ankommer fra regionerne:**

1. Kør eksisterende pipeline: `python3 pipeline.py` (postnummer-analyser)
2. Kør tidsmæssige analyser: `python3 temporal_pipeline.py` (når implementeret)
3. Sammenlign output med tidligere version (er trends konsistente?)
4. Opdatér key findings hvis mønstre har ændret sig

**Periodisk review (hver 6. måned):**
- Verificér at datastrukturer ikke har ændret sig
- Check om nye kolonner er tilføjet i rådata
- Opdatér Covid-periode definition (hvis relevant)
- Review ekspert-feedback fra publicerede historier

---

**Status: 🟡 Klar til prioritering og scheduling**

**Næste step:** Beslut hvilken analyse skal implementeres først, og allokér tid til udvikling.
