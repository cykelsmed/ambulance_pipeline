# MASTER FINDINGS RAPPORT
## Komplet Analyse af Ambulance Responstider i Danmark

**Genereret:** 10. November 2025 kl. 01:12
**Periode:** 2021-2025 (5 år)
**Datasæt:** Postnummer + Tidsmæssige mønstre + Systemanalyser + Årlig udvikling

---

## 📋 HOVEDHISTORIER - KEY FINDINGS

### 📊 Top 8 Fund:

**1. "Ambulancen kommer fire gange hurtigere i Esbjerg end i Hobro. Din adresse kan betyde 15 minutters forskel."**  
*3.9x forskel mellem bedste og værste postnummer*

Værste postnummer (9500 Hobro: 19.8 min) har 3.9x længere responstid end bedste (6705 Esbjerg Ø: 5.1 min). Variationen følger et geografisk mønster med landdistriker langsommere end bycentre.

**2. "Alle regioner når deres servicemål – men Nordjylland er alligevel 45% langsommere end Syddanmark. Rigsrevisionen kritiserer at regionerne bruger forskellige målemetoder."**  
*3.5 minutters forskel mellem hurtigste og langsomste region*

Nordjylland er **44.9% langsommere** end Syddanmark (11.3 min vs 7.8 min). Alle regioner opfylder formelt deres servicemål. Rigsrevisionen (SR 11/2024) påpeger at regionerne opererer med forskellige definitioner og tællemetoder.

**3. "Når trafikken letter om natten, bliver ambulancerne langsommere. Myldretiden kl. 17 er faktisk blandt dagens hurtigste timer."**  
*20-28% variation mellem tidspunkter på døgnet*

Ambulancer er 20-28% langsommere om natten (kl. 02-06) end på dagen. Værste tidspunkt: kl. 06:00. Responstider er korteste kl. 08, mens kl. 17 (myldretid) er blandt de hurtigste timer.

**4. "Ikke livstruende? Så venter du over dobbelt så længe. I Hovedstaden er B-patienter 140% langsommere end A-patienter."**  
*60-140% forskel mellem A og B-prioritet*

B-prioritet kørsler er 60-140% langsommere end A-prioritet. Hovedstaden: A=9.1 min, B=21.9 min (+140.7%). A-prioritet dækker livstruende tilfælde, mens B-prioritet omfatter ikke-livstruende tilfælde.

**5. "To minutter går før ambulancen overhovedet forlader stationen. Regionernes servicemål starter først når ambulancen sendes afsted – ikke når du ringer 112."**  
*Ca. 22% af ventetid sker før ambulancen sendes afsted*

Tiden fra 112-opkald til ambulancen sendes afsted udgør ca. 22% af total ventetid (~2 min median). Data fra Nordjylland + Syddanmark (549,000 kørsler). Rigsrevisionens notat (SR 11/2024): Denne tid medregnes ikke i regionernes servicemål. **Databegrænsning:** Kun 2 ud af 5 regioner har datetime-data der muliggør denne analyse. Hovedstaden, Sjælland og Midtjylland bruger time-only format.

**6. "Ring 112 - ikke 1813. Lægevagten sender 46% langsommere ambulancer"**  
*8.6 minutter forskel mellem 112 og 1813*

Ambulancer rekvireret gennem 1813 (lægevagten) har 26.9 minutters gennemsnitlig responstid, sammenlignet med 18.3 minutter for 112-opkald. Forskellen er særligt markant i Hovedstaden, hvor B-prioritet gennem 1813 har 25.4 minutters median responstid. Data dækker 1.7 millioner kørsler fra alle regioner. **Datadetalje:** 112: 1,055,902 kørsler | 1813: 98,169 kørsler

**7. "I indre København venter ikke-livstruende patienter syv gange længere end livstruende"**  
*B/A-ratio på 6.9x i postnummer 1461*

Mens den gennemsnitlige forskel mellem A og B-prioritet i Hovedstaden er 140%, viser postnumre i indre København (1xxx) ekstremt større forskelle. Top 10 postnumre med størst B/A-forskel er alle i Hovedstaden: Postnummer 1461 (B=27.6 min, A=4.0 min, ratio: 6.9x), Postnummer 1126 (B=39.7 min, A=6.2 min, ratio: 6.4x), Postnummer 1777 (B=36.9 min, A=5.9 min, ratio: 6.3x). **Mønster:** Je tættere på København centrum, desto større forskel mellem A og B-prioritet.

**8. "Hovedstaden skiller sig ud: Værst kl. 23 - ikke ved morgenvagt-skifte"**  
*Eneste region hvor aften er problemet*

Alle regioner undtagen Hovedstaden har værste responstider tidlig morgen (kl. 05-06). Hovedstaden har værste responstid kl. 23 (14.9 min). Tidsperiode-gennemsnit Hovedstaden: Dag (06-18): 13.3 min, Nat (00-06): 14.1 min, Aften (18-24): 14.0 min (værst kl. 23). Til sammenligning har Nordjylland værst kl. 06 (16.1 min), Sjælland værst kl. 06 (13.2 min), Midtjylland værst kl. 05 (12.6 min), Syddanmark værst kl. 06 (9.2 min).

---

### 📊 Datagrundlag:
- **875,000+ A-prioritet kørsler** analyseret (livstruende tilfælde)
- **493,000+ A+B-kørsler** i tidsmæssige analyser (fuld belastning)
- **549,000+ kørsler** med alarmtid-analyse (Nordjylland + Syddanmark)
- **1,543,000+ total kørsler** analyseret (inkl. C-prioritet)
- **1,724,810 total kørsler** analyseret inkl. rekvireringskanal-data
- **5 års data** (2021-2025) fra alle 5 danske regioner
- **1095 postnumre** kortlagt
- **Top 10 B/A ekstreme postnumre** alle i Hovedstaden (København centrum)

## 📍 DEL 1: POSTNUMMER-ANALYSER

**Hovedfund:** Markant geografisk variation i ambulance-responstider.

Analysen viser betydelig geografisk variation i responstider. Forskellen mellem langsomste og hurtigste postnummer er op til 4 gange. Variationen følger et geografisk mønster.

### 1.1 Top 10 VÆRSTE Postnumre

**Her venter du længst på ambulancen:**

*Primært landdistriker med store geografiske afstande - bemærk især Midtjylland dominerer top 10.*

| Rank | Postnummer | Region | Gennemsnit (min) | Antal Ture |
|------|------------|--------|------------------|------------|
| 1 | **9500 Hobro** | Midtjylland | 19.8 | 144 |
| 2 | **7884 Fur** | Midtjylland | 19.8 | 117 |
| 3 | **8970 Havndal** | Midtjylland | 19.6 | 293 |
| 4 | **4944 Fejø** | Sjælland | 19.6 | 68 |
| 5 | **7790 Thyholm** | Midtjylland | 19.0 | 520 |
| 6 | **5390 Martofte** | Syddanmark | 18.6 | 109 |
| 7 | **7741 Frøstrup** | Nordjylland | 18.5 | 216 |
| 8 | **4874 Gedser** | Sjælland | 18.3 | 433 |
| 9 | **5935 Bagenkop** | Syddanmark | 18.2 | 189 |
| 10 | **9620 Aalestrup** | Midtjylland | 18.0 | 82 |

### 1.2 Top 10 BEDSTE Postnumre

**Her er ambulancen hurtigst:**

*Syddanske bycentre dominerer totalt - høj befolkningstæthed og kort afstand til hospitaler.*

| Rank | Postnummer | Region | Gennemsnit (min) | Antal Ture |
|------|------------|--------|------------------|------------|
| 1 | **6705 Esbjerg Ø** | Syddanmark | 5.1 | 2,631 |
| 2 | **5200 Odense V** | Syddanmark | 5.4 | 1,842 |
| 3 | **5000 Odense C** | Syddanmark | 5.6 | 9,344 |
| 4 | **6700 Esbjerg** | Syddanmark | 5.6 | 5,660 |
| 5 | **6000 Kolding** | Syddanmark | 5.7 | 10,212 |
| 6 | **6753 Agerbæk** | Syddanmark | 5.7 | 218 |
| 7 | **6430 Nordborg** | Syddanmark | 5.8 | 2,577 |
| 8 | **5900 Rudkøbing** | Syddanmark | 5.8 | 1,510 |
| 9 | **6400 Sønderborg** | Syddanmark | 6.0 | 6,243 |
| 10 | **6840 Oksbøl** | Syddanmark | 6.1 | 662 |

**Sammenligning:** 9500 Hobro (19.8 min) er **3.9x langsommere** end 6705 Esbjerg Ø (5.1 min). Rigsrevisionens notat (SR 11/2024) påpeger at de regionale servicemål dækker over 'store geografiske forskelle'. Forskellen viser den geografiske forskel mellem landdistriker og bycentre.

### 1.3 Regional Sammenligning

**Regional ulighed - alle opfylder servicemål, men med forskellige definitioner:**

| Region | Gennemsnit (min) | Total Ture | Postnumre |
|--------|------------------|------------|-----------|
| **Nordjylland** | 11.3 | 85,063 | 77 |
| **Sjælland** | 10.4 | 163,489 | 131 |
| **Hovedstaden** | 10.0 | 235,590 | 572 |
| **Midtjylland** | 9.6 | 187,519 | 153 |
| **Syddanmark** | 7.8 | 202,893 | 162 |

*Regional median beregnes på case-niveau - se Tabel 2.3 (Årlig Udvikling)*

---

## 📅 DEL 2: ÅRLIG UDVIKLING (2021-2025)

**Hovedfund:** Stabil udvikling med vedvarende geografisk variation.

Landsdækkende responstider har været bemærkelsesværdigt stabile 2021-2025. Der ses markant geografisk variation mellem regioner og postnumre.

### 2.1 Landsdækkende Udvikling

**A-prioritet responstider per år:**

| År | Gennemsnit (min) | Median (min) | Antal Kørsler |
|----|------------------|--------------|---------------|
| **2021** | 9.5 | 8.4 | 118,372 |
| **2022** | 9.5 | 8.6 | 224,726 |
| **2023** | 9.6 | 8.6 | 216,621 |
| **2024** | 9.6 | 8.7 | 208,862 |
| **2025** | 9.6 | 8.7 | 107,753 |

**År-til-år ændringer:**

- 2021 → 2022: +0.0 min (+0.0%) →
- 2022 → 2023: +0.1 min (+1.1%) ↑
- 2023 → 2024: +0.0 min (+0.0%) →
- 2024 → 2025: +0.0 min (+0.0%) →

### 2.2 Regional Udvikling Per År

**Responstider (minutter) fordelt på region og år:**

| År | Hovedstaden | Midtjylland | Nordjylland | Sjælland | Syddanmark |
|----|----|----|----|----|----|
| **2021** | 9.7 | 9.2 | 11.5 | 10.8 | 7.8 |
| **2022** | 10.1 | 9.4 | 11.1 | 10.3 | 7.8 |
| **2023** | 10.1 | 9.6 | 11.2 | 10.6 | 7.7 |
| **2024** | 10.1 | 9.9 | 11.2 | 10.2 | 7.8 |
| **2025** | 10.1 | 9.9 | 11.5 | 9.8 | 7.6 |

### 2.3 Regional Gennemsnit (2021-2025 Samlet)

| Region | Gennemsnit (min) | Median (min) | Total A-Kørsler |
|--------|------------------|--------------|------------------|
| **Nordjylland** | 11.3 | 10.2 | 85,063 |
| **Sjælland** | 10.4 | 9.3 | 163,489 |
| **Hovedstaden** | 10.0 | 9.1 | 237,357 |
| **Midtjylland** | 9.6 | 8.5 | 187,531 |
| **Syddanmark** | 7.8 | 7.0 | 202,894 |

**Vigtigste fund:**
- Bedste region: Syddanmark (7.8 min)
- Værste region: Nordjylland (11.3 min)
- Regional forskel: 3.5 min (44.9% langsommere)
- Landsdækkende stabilitet: Meget stabil udvikling 2021-2025

---

## ⏰ DEL 3: TIDSMÆSSIGE MØNSTRE

**Hovedfund:** Nat og tidlig morgen langsommere end myldretid.

Data viser at myldretiden (kl. 16-18) ikke er det langsomste tidspunkt. Ambulancer er hurtigst midt på dagen. Nattevagter (kl. 02-06) og tidlig morgen (kl. 06:00) har responstider op til 28% langsommere end dagen.

**OBS:** Tidsmæssige analyser inkluderer BÅDE A- og B-prioritet kørsler for at vise det fulde billede af ambulanceberedskabets belastning. Dette forklarer hvorfor værdierne er højere end i Del 2 (som kun viser A-prioritet).

- **A-prioritet:** Livstruende tilfælde (hurtigst respons)
- **B-prioritet:** Ikke-livstruende (kan vente længere)
- Forskellen mellem A og B vises i Del 4.1

### 3.1 Tid-på-Døgnet (Rush Hour)

**Bedste og værste tidspunkt per region (A+B kørsler):**

| Region | Bedste Time | Min | Værste Time | Min | Variation (%) |
|--------|-------------|-----|-------------|-----|---------------|
| Nordjylland | kl. 08 | 12.3 | **kl. 06** | 16.1 | 30.9% |
| Hovedstaden | kl. 08 | 12.2 | **kl. 23** | 14.9 | 22.1% |
| Sjælland | kl. 08 | 11.7 | **kl. 06** | 13.2 | 12.8% |
| Midtjylland | kl. 08 | 10.9 | **kl. 05** | 12.6 | 15.6% |
| Syddanmark | kl. 08 | 8.0 | **kl. 06** | 9.2 | 15.0% |

### 3.2 Sæsonvariation (Måned-for-Måned)

**Bedste og værste måned per region:**

| Region | Bedste Måned | Min | Værste Måned | Min | Variation (%) |
|--------|--------------|-----|--------------|-----|---------------|
| Nordjylland | Maj | 13.1 | **December** | 14.0 | 6.9% |
| Hovedstaden | Juli | 13.2 | **Juni** | 13.8 | 4.5% |
| Sjælland | Maj | 11.8 | **December** | 12.7 | 7.6% |
| Midtjylland | Juli | 11.8 | **Juni** | 12.4 | 5.1% |
| Syddanmark | April | 8.4 | **Januar** | 8.6 | 2.4% |

**Sammenfatning:** Sæsonvariation (5-8%) er markant mindre end tid-på-døgnet variation (20-28%).

---

## 🏥 DEL 4: SYSTEMANALYSER

**Hovedfund:** Markant forskel mellem prioritetsniveauer.

B-prioritet kørsler (ikke-livstruende) har markant længere ventetid end A-prioritet. I Hovedstaden er B-prioritet 140% langsommere (21.9 min vs 9.1 min).

### 4.1 A vs B vs C Prioritering

**Responstider fordelt på prioritetsniveau:**

| Region | A-prioritet (min) | B-prioritet (min) | B vs A Forskel |
|--------|-------------------|-------------------|----------------|
| Hovedstaden | 9.1 | 21.9 | +140.7% |
| Midtjylland | 8.5 | 19.1 | +124.7% |
| Nordjylland | 10.2 | 18.4 | +80.4% |
| Sjælland | 9.3 | 17.5 | +88.2% |
| Syddanmark | 7.0 | 11.4 | +62.9% |

### 4.2 Rekvireringskanal (Alle Prioriteter)

**Responstider fordelt på rekvireringskanal:**

*Data fra 5 regioner: Hovedstaden, Midtjylland, Nordjylland, Sjælland, Syddanmark*
*Total kørsler: 1,724,810*

| Region | Kanal | Prioritet | Median (min) | Antal Kørsler |
|--------|-------|-----------|--------------|---------------|
| Hovedstaden | 112 | B | 21.7 | 164,906 |
| Hovedstaden | 112 | A | 8.6 | 156,849 |
| Syddanmark | 112 | A | 6.9 | 146,532 |
| Syddanmark | 112 | B | 11.3 | 132,589 |
| Sjælland | 112 | B | 17.8 | 116,381 |
| Midtjylland | 112 | A | 8.6 | 112,243 |
| Midtjylland | 112 | B | 18.7 | 110,920 |
| Sjælland | 112 | A | 9.7 | 105,977 |
| Nordjylland | Alarm112 | A | 10.4 | 76,509 |
| Nordjylland | Alarm112 | B | 18.7 | 63,746 |
| Hovedstaden | 1813 | A | 11.8 | 56,891 |
| Hovedstaden | 1813 | B | 25.4 | 40,726 |
| Midtjylland | Vagtlæge/LVN | A | 8.7 | 39,462 |
| Midtjylland | Praktiserende læge | A | 8.2 | 35,422 |
| Sjælland | Andre | A | 8.8 | 33,433 |

---

## 🔍 DEL 5: B-PRIORITET DYB-ANALYSE

**Hovedfund:** Større variation i B-prioritet end A-prioritet.

Mens A-prioritet (livstruende) prioriteres højest, viser B-prioritet analysen markante forskelle i hvordan ikke-livstruende patienter behandles. B-prioritet viser større variation end A-prioritet - både geografisk, tidsmæssigt og over tid.

### 5.1 Geografiske Hotspots - B-Prioritet Postnumre

**De 10 værste postnumre for B-prioritet kørsler:**

| Placering | Postnummer | Navn | Median (min) | Antal B-Kørsler | Region |
|-----------|------------|------|--------------|-----------------|--------|
| 1 | 4305 | 4305 | 47.6 | 191 | Sjælland |
| 2 | 4944 | 4944 Fejø | 39.5 | 40 | Sjælland |
| 3 | 7884 | 7884 Fur | 33.9 | 113 | Midtjylland |
| 4 | 1301 | 1301 | 33.5 | 20 | Hovedstaden |
| 5 | 8970 | 8970 Havndal | 31.2 | 304 | Midtjylland |
| 6 | 1430 | 1430 | 31.1 | 43 | Hovedstaden |
| 7 | 7540 | 7540 Haderup | 31.0 | 171 | Midtjylland |
| 8 | 7790 | 7790 Thyholm | 30.7 | 452 | Midtjylland |
| 9 | 1432 | 1432 | 30.1 | 297 | Hovedstaden |
| 10 | 1154 | 1154 | 29.9 | 30 | Hovedstaden |

**Fund:** B-prioritet viser større geografisk variation end A-prioritet. Værste postnummer (4305) har 47.6 min median responstid for ikke-livstruende tilfælde.

### 5.2 Tidsmæssige Mønstre - B-Prioritet

**Hvordan påvirkes B-prioritet af tidspunkt på døgnet og årstid?**

**Sammenfatning:** B-prioritet patienter oplever større tidsmæssig variation end A-prioritet.

**Eksempel - Hovedstaden B-prioritet:**
- Værste time: kl. 18 (25.9 min median)
- Bedste time: kl. 04 (17.9 min median)
- Variation: 44.7%

### 5.3 Årlig Udvikling - B-Prioritet 2021-2025

**Er B-prioritet blevet bedre eller værre over tid?**

| Region | 2021 Median (min) | 2025 Median (min) | Ændring | % Ændring |
|--------|-------------------|-------------------|---------|------------|
| Hovedstaden | 20.5 | 22.6 | +2.1 min | +10.2% |
| Midtjylland | 18.4 | 20.2 | +1.8 min | +9.8% |
| Nordjylland | 18.5 | 18.1 | -0.4 min | -2.2% |
| Sjælland | 18.5 | 17.4 | -1.1 min | -5.9% |
| Syddanmark | 11.5 | 11.6 | +0.1 min | +0.9% |
| **LANDSDÆKKENDE** | 17.7 | 18.4 | +0.7 min | +4.0% |

**Fund:** B-prioritet har været relativt stabil på landsplan over perioden. 

---

## ⏱️ DEL 6: ALARMTID

**Hovedfund:** Ca. 22% af ventetid sker før ambulancen sendes afsted.

**Hvad er alarmtid?** Tiden fra borgeren ringer 112 til ambulancen bliver sendt afsted. Dette inkluderer triage (sundhedsfaglig vurdering), klassificering af hastegrad, og disponering (at finde og alarmere den rette ambulance).

Data fra Nordjylland og Syddanmark viser at ca. 22% af total ventetid (~2 minutter median) sker i denne fase. Dette fremgår ikke af regionernes officielle servicemål.

### 6.1 Opdeling af Total Ventetid

**Geografisk begrænsning:** Regionerne kan måle alarmtid, men vi fandt kun brugbare datetime-data i 2 ud af 5 regioner (Nordjylland + Syddanmark). Hovedstaden, Sjælland og Midtjylland bruger time-only format, hvilket ikke kan beregne tidsforskel hen over midnat. Derfor kan deres alarmtid ikke analyseres med de tilgængelige data.

| Region | Prioritet | Analyseret | Total Ventetid (median) | Alarmtid | Rejsetid |
|--------|-----------|------------|-------------------------|----------|----------|
| Nordjylland | A | 85,016 | 10.2 min | 2.2 min (22%) | 7.6 min (75%) |
| Nordjylland | B | 95,562 | 18.4 min | 3.0 min (16%) | 13.6 min (74%) |
| Syddanmark | A | 205,766 | 9.0 min | 2.0 min (22%) | 7.0 min (78%) |
| Syddanmark | B | 163,453 | 14.0 min | 3.0 min (21%) | 11.0 min (79%) |

### 6.2 Vigtigste Fund

**A-prioritet (livstruende):**
- Alarmtid udgør **ca. 22%** af total ventetid
- Median alarmtid: ~2.0-2.2 minutter
- Median rejsetid: ~7.0-7.6 minutter

**B-prioritet (ikke-livstruende):**
- Alarmtid udgør **ca. 19%** af total ventetid
- Median alarmtid: ~3.0 minutter
- Median rejsetid: ~11.0-13.6 minutter

**Rigsrevisionens notat (SR 11/2024):** Regionernes servicemål medregner ikke denne alarmtid. Den officielle 'responstid' starter først når ambulancen disponeres (sendes afsted), ikke når borgeren ringer 112.

---

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

**RAPPORT GENERERET: 10. November 2025 kl. 01:12**

*Genereret automatisk af Ambulance Pipeline*

---

**Kildekode og dokumentation:** https://github.com/cykelsmed/ambulance_pipeline

**Undersøgelsen er lavet af:**  
Kaas og Mulvad Research / Adam Hvidt  
Email: adam@km24  
Telefon: 26366414
