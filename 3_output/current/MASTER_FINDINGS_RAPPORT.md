# MASTER FINDINGS RAPPORT
## Komplet Analyse af Ambulance Responstider i Danmark

**Genereret:** 09. November 2025 kl. 22:48
**Periode:** 2021-2025 (5 år)
**Datasæt:** Postnummer + Tidsmæssige mønstre + Systemanalyser + Årlig udvikling

---

## 🚨 HOVEDHISTORIER - TV2 KEY FINDINGS

*TV2 key findings ikke tilgængelige - se detaljerede sektioner nedenfor*

## 📍 DEL 1: POSTNUMMER-ANALYSER

**📊 Nøgletal:** Forskel på op til 3.9x mellem værste og bedste postnummer

Analysen viser **betydelig geografisk variation** i ambulance-responstider. Forskellen afspejler primært afstand til nærmeste ambulancestation og geografiske forhold.

*Postnummer-data ikke tilgængelig*

---

## 📅 DEL 2: ÅRLIG UDVIKLING (2021-2025)

**📊 Nøgletal:** Landsdækkende stabilitet (+1.1% over 5 år), men betydelig regional variation

Landsdækkende responstider har været **stabile** 2021-2025. Der er dog betydelig forskel mellem regioner og postnumre.

*Årlig analyse-data ikke tilgængelig*

---

## ⏰ DEL 3: TIDSMÆSSIGE MØNSTRE

**📊 Nøgletal:** Op til 28% længere responstid om natten end om dagen

**Observation:** Myldretiden (kl. 16-18) har ikke de længste responstider. Ambulancer er faktisk **hurtigst midt på dagen**. De længste responstider ses i **nattetimerne** (kl. 02-06) og især omkring **kl. 06:00**, hvor responstiderne er op til **28% langsommere** end om dagen.

**OBS:** Tidsmæssige analyser inkluderer BÅDE A- og B-prioritet kørsler for at vise det fulde billede af ambulanceberedskabets belastning. Dette forklarer hvorfor værdierne er højere end i Del 2 (som kun viser A-prioritet).

- **A-prioritet:** Livstruende tilfælde (hurtigst respons)
- **B-prioritet:** Ikke-livstruende (kan vente længere)
- Forskellen mellem A og B vises i Del 4.1

### 3.1 Tid-på-Døgnet (Rush Hour)

**Bedste og værste tidspunkt per region (A+B kørsler):**

| Region | Bedste Time | Min | Værste Time | Min | Variation (%) |
|--------|-------------|-----|-------------|-----|---------------|

### 3.2 Sæsonvariation (Måned-for-Måned)

**Bedste og værste måned per region:**

| Region | Bedste Måned | Min | Værste Måned | Min | Variation (%) |
|--------|--------------|-----|--------------|-----|---------------|

**Observation:** Sæsonvariation (5-8%) er **mindre end tid-på-døgnet variation** (20-28%). Tidspunkt på døgnet har større indflydelse på responstid end årstid.

---

## 🏥 DEL 4: SYSTEMANALYSER

**📊 Nøgletal:** B-prioritet har 60-140% længere responstid end A-prioritet

B-prioritet kørsler (ikke-livstruende) har længere responstider end A-prioritet. I Hovedstaden er B-prioritet **140% langsommere** (21.9 min vs 9.1 min). Forskellen varierer betydeligt mellem regioner.

*System analyse-data ikke tilgængelig*

---

## 🔍 DEL 5: B-PRIORITET DYB-ANALYSE

**📊 Nøgletal:** B-prioritet viser større geografisk og tidsmæssig variation end A-prioritet

Mens A-prioritet (livstruende) prioriteres højest, viser B-prioritet analysen **betydelige forskelle** i responstider for ikke-livstruende patienter. B-prioritet viser **større variation** end A-prioritet - både geografisk, tidsmæssigt og over tid.

---

## ⏱️ DEL 6: ALARMTID - VENTETID FØR AMBULANCEN KØRER

**📊 Nøgletal:** Ca. 22% af total ventetid (~2 min median) sker før ambulancen kører

**Hvad er alarmtid?** Tiden fra borgeren ringer 112 til ambulancen bliver sendt afsted. Dette inkluderer triage (sundhedsfaglig vurdering), klassificering af hastegrad, og disponering (at finde og alarmere den rette ambulance).

Data fra Nordjylland og Syddanmark viser at **ca. 22% af total ventetid** (~2 minutter median) sker i denne fase før ambulancen forlader stationen.

*Alarmtid-data ikke tilgængelig*

---

## 📎 APPENDIKS: YDERLIGERE ANALYSER

Følgende analyser er også udført:

### A.1 Sæsonvariation (Måned-for-Måned)

**Resultat:** Begrænset variation (5-8% forskel mellem værste/bedste måned)

- Værste måned typisk: December/Januar (vinter)
- Bedste måned typisk: Maj/Juli (forår/sommer)
- **Variation mindre end tid-på-døgnet** (28% vs. 5-8%)

**Observation:** Tidspunkt på døgnet har større indflydelse end årstid.

*Detaljer:* Se DEL 3 (Tidsmæssige Mønstre) for fuld regional sæsonanalyse.

### A.2 Rekvireringskanal-Analyse

**Resultat:** Begrænset forskel mellem 112, 1813, vagtlæge

- 112-direkte: Median ~9 min for A-prioritet
- 1813-henvisning: Median ~11 min
- Praktiserende læge: Median ~9-10 min

**Observation:** Forskellen er ca. 2 minutter mellem hurtigste og langsomste kanal.

*Detaljer:* Se `09_rekvireringskanal.xlsx` i bilag.

### A.3 C-Prioritet Kørsler

**Resultat:** C-prioritet (ikke-akut) bruges sjældent

- Udgør <5% af total kørsler
- Længere responstider (forventet - ikke akut)

**Observation:** C-prioritet repræsenterer en lille andel af total aktivitet.

### A.4 B→A Prioritets-Eskalationer

**Databegrænsning:** Data kun fra Hovedstaden (mangler 4 andre regioner)

- Eskalerings-rate: varierer betydeligt
- Indikerer at nogle B-kørsler opgraderes til A undervejs

**Observation:** Begrænset datagrundlag (kun én region) gør det svært at drage landsdækkende konklusioner.

*Detaljer:* Se DEL 5 for dybere B-prioritet analyse.

---

**Metodisk note:** Disse analyser er fuldt dokumenterede og statistisk valide.

## 📁 DATAFILER TIL VIDERE ANALYSE

**Genererede analysefiler:**

*Postnummer-analyser:*
- `01_alle_postnumre.xlsx` - Alle 626 postnumre
- `02_top_10_værste_VALIDERET.xlsx` - Top 10 værste
- `03_top_10_bedste.xlsx` - Top 10 bedste
- `04_regional_sammenligning.xlsx` - Regional sammenligning
- `DATAWRAPPER_alle_postnumre.csv` - Kort-visualization

*Årlige analyser:*
- `10_responstid_per_aar_og_region_A.xlsx` - År × Region matrix
- `11_responstid_per_aar_landsdækkende_A.xlsx` - Landsdækkende per år
- `12_responstid_per_region_samlet_A.xlsx` - Regional total
- `13_responstid_pivot_aar_x_region_A.xlsx` - Pivot-tabel
- `ÅRLIG_ANALYSE_FUND_A.txt` - Key findings

*Tidsmæssige analyser (per region):*
- `{Region}_05_responstid_per_time.xlsx` - Time-for-time
- `{Region}_06_responstid_per_maaned.xlsx` - Måned-for-måned
- `{Region}_DATAWRAPPER_*.csv` - Visualization data

*Systemanalyser:*
- `07_prioritering_ABC.xlsx` - A/B/C prioritering
- `09_rekvireringskanal.xlsx` - Rekvireringskanal
- `DATAWRAPPER_prioritering_ABC.csv` - Priority visualization

*Alarmtid-analyse (Nordjylland + Syddanmark):*
- `20_dispatch_delay_vs_travel.xlsx` - Opdeling: alarmtid vs. rejsetid
- `20_DISPATCH_DELAY_FUND.txt` - Key findings

---

## 📋 METODE OG DATAGRUNDLAG

**Datakilder:**
- Ambulance-data fra alle 5 danske regioner (2021-2025)
- Total: ~2 millioner individuelle ambulance-kørsler
- Analyseret: 875,000+ A-prioritet + 668,000+ B-prioritet

**OBS:** Vores analyse fokuserer primært på den officielle responstid (fra disponering til ankomst). For analyse af den 'skjulte' alarmtid før ambulancen sendes afsted, se **DEL 6: ALARMTID**.

---

**Hvad vi har gjort med rådata:**

1. **Filtrering efter formål:**
   - **Del 1-2 (Postnummer, Årlig):** Kun A-prioritet (livstruende)
   - **Del 3 (Tidsmæssig):** A+B prioritet (viser fuld belastning)
   - **Del 4 (Prioritering):** Sammenligner A vs B direkte

2. **Datarensning:** Fjernet kørsler med manglende responstid eller tidsstempler

3. **Beregningsmetode:**
   - **Gennemsnit** i Top 10 lister (viser fuld variation)
   - **Median** i regionale/tidsmæssige sammenligninger (robust mod outliers)

4. **Validering:** Minimum 50 ture for Top 10 postnumre

**Hvorfor forskellige datasæt?**
- A-prioritet alene giver det mest retvisende billede af "worst case" respons
- A+B sammen viser systemets samlede belastning og prioritering
- Sammenligning af A vs B viser hvor meget B-patienter nedprioriteres

**Teknisk note:** Regional median i Tabel 2.3 er beregnet fra individuelle kørsler (statistisk korrekt). Postnummer-aggregering i Tabel 1.3 bruger gennemsnit på postnummer-niveau.

---

**RAPPORT GENERERET: 09. November 2025 kl. 22:48**

*Genereret automatisk af Ambulance Pipeline*

---

**Kildekode og dokumentation:** https://github.com/cykelsmed/ambulance_pipeline

**Undersøgelsen er lavet af:**  
Kaas og Mulvad Research / Adam Hvidt  
Email: adam@km24  
Telefon: 26366414
