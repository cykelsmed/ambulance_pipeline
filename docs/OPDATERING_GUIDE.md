# GUIDE: Opdatering med Nye Datasæt

**Til:** TV2 team
**Dato:** 28. oktober 2025
**Formål:** Vejledning til opdatering af pipeline når nye regionale data modtages

---

## Hvornår bruges denne guide?

Når I modtager opdaterede Excel-filer fra Nils med nye data fra én eller flere regioner (fx Sjælland, Syddanmark).

---

## Trin-for-trin Opdatering

### 1. Modtag nye filer fra Nils

Nils sender opdaterede Excel-filer i samme format som de nuværende:
- Excel-fil med "Postnummer"-ark (aggregerede data)
- Eksempel: `Sjælland20251105.xlsx`, `Syddanmark_opdateret.xlsx`

### 2. Arkivér gamle filer (valgfrit men anbefalet)

```bash
# Flyt gamle versioner til arkiv-mappe
mv 1_input/RegionSjælland.xlsx 1_input/_archive/RegionSjælland_20251028.xlsx
mv 1_input/Syddanmark20251025.xlsx 1_input/_archive/Syddanmark_20251028.xlsx
```

### 3. Kopier nye filer til 1_input/

```bash
# Kopier fra Downloads (eller hvor Nils' filer ligger)
cp ~/Downloads/Sjælland_ny.xlsx 1_input/
cp ~/Downloads/Syddanmark_ny.xlsx 1_input/
```

**OBS:** Filnavnet er ligegyldigt - så længe det indeholder regionsnavnet:
- ✅ `RegionSjælland.xlsx`
- ✅ `Sjælland_nov2025.xlsx`
- ✅ `Syddanmark_final.xlsx`

### 4. Kør pipeline

```bash
python3 pipeline.py
```

**Det er det!** Pipeline'n vil automatisk:
- Finde alle 5 regionale filer (inkl. de nye)
- Læse "Postnummer"-arkene
- Kombinere data fra alle regioner
- Generere 5 opdaterede output-filer

### 5. Verificer output

Tjek at de nye data er med:

```bash
# Se hvilke regioner blev processeret
cat 3_output/current/pipeline_run_metadata.json

# Sammenlign med tidligere version
diff 3_output/current/01_alle_postnumre.xlsx 3_output/_old/01_alle_postnumre.xlsx
```

---

## Automatisk Håndtering

Pipeline'n håndterer automatisk:

### ✅ Forskellige filnavne
- Matcher på regionsnavn i filnavn (fx "*Sjælland*", "*Syddanmark*")
- Virker med alle variationer: `RegionSjælland.xlsx`, `Sjaelland_2025.xlsx`, etc.

### ✅ Forskellige Excel-strukturer
- Finder automatisk "Postnummer"-ark (også "postnummer", "Postnumre")
- Detekterer header-række automatisk (søger efter "Row Labels")
- Håndterer forskellige kolonnenavne per region

### ✅ Forskellige dataformater
- Kombinerer kolonner med forskellige navne ("Average of ResponstidMinutter", "Average of Minutter", etc.)
- Filtrerer automatisk ugyldige rækker ("Grand Total", blanke, etc.)
- Validerer postnumre (kun 1000-9999)

---

## Hvad hvis noget går galt?

### Problem: Pipeline finder ikke den nye fil

**Løsning:** Tjek filnavnet indeholder regionsnavnet
```bash
# Se hvilke filer pipeline'n fandt
grep "Found" pipeline.log
```

### Problem: Forkert antal rækker i output

**Løsning:** Tjek om den nye fil har "Postnummer"-ark
```bash
python3 << 'EOF'
import pandas as pd
xls = pd.ExcelFile('1_input/Sjælland_ny.xlsx')
print("Ark tilgængelige:", xls.sheet_names)
EOF
```

### Problem: Dublet-postnumre mellem regioner

**Dette er kendt issue:** 20 postnumre findes i flere regioner (grænseområder).
- Se `VERIFICATION.md` sektion om duplikerede postnumre
- Kræver afklaring med Nils

---

## Re-kørbarhed

Pipelinen kan køres uendeligt mange gange:
- ✅ Tidligere output overskrives automatisk
- ✅ Ingen manuel konfiguration nødvendig
- ✅ Samme 5 output-filer genereres hver gang

---

## Output Filer

Hver kørsel genererer:

| Fil | Beskrivelse | Rækker |
|-----|-------------|---------|
| `01_alle_postnumre.xlsx` | Alle postnumre sorteret efter responstid | 624 |
| `02_top_10_værste_VALIDERET.xlsx` | Top 10 værste (≥50 ture) | 10 |
| `03_top_10_bedste.xlsx` | Top 10 bedste (≥50 ture) | 10 |
| `04_regional_sammenligning.xlsx` | Sammenligning af 5 regioner | 5 |
| `DATAWRAPPER_alle_postnumre.csv` | Til Datawrapper-kort | 624 |
| `pipeline_run_metadata.json` | Metadata om kørsel | 1 |

---

## Arkivering af Output (Anbefalet)

Før I kører pipeline med nye data:

```bash
# Gem nuværende output med timestamp
cp -r 3_output/current 3_output/backup_20251028
```

Så kan I sammenligne før/efter:
```bash
diff 3_output/backup_20251028/01_alle_postnumre.xlsx \
     3_output/current/01_alle_postnumre.xlsx
```

---

## Spørgsmål?

Kontakt Nils eller se:
- `README.md` - Komplet dokumentation
- `VERIFICATION.md` - Dataverificering
- `pipeline.log` - Detaljeret log fra sidste kørsel

---

**Status:** Pipeline er klar til opdateringer - ingen kode-ændringer nødvendige! ✅
