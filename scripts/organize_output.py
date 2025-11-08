#!/usr/bin/env python3
"""Output Organization Script

Organizes pipeline output files for easy sharing:
- Main report (MASTER_FINDINGS_RAPPORT.md) stays in root
- All other files moved to bilag/ subdirectory and zipped

Usage:
    python3 organize_output.py [--output-dir PATH] [--keep-unzipped]
"""

import argparse
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


def create_bilag_readme():
    """Generate README content for bilag directory."""
    return f"""# AMBULANCE PIPELINE - BILAG
**Genereret:** {datetime.now().strftime('%d. %B %Y kl. %H:%M')}

Dette arkiv indeholder alle datafiler og analyser fra ambulance-pipeline kørslen.

## 📊 FILSTRUKTUR

### Postnummer-analyser
- `01_alle_postnumre.xlsx` - Alle 624 postnumre med responstider
- `02_top_10_værste_VALIDERET.xlsx` - De 10 postnumre med længst responstid (≥50 ture)
- `03_top_10_bedste.xlsx` - De 10 postnumre med kortest responstid
- `04_regional_sammenligning.xlsx` - Aggregeret sammenligning på tværs af 5 regioner

### Tidsmæssige analyser (per region)
**Format:** `[Region]_05_responstid_per_time.xlsx` og `[Region]_06_responstid_per_maaned.xlsx`

- **05_responstid_per_time:** Responstider per time på døgnet (0-23)
- **06_responstid_per_maaned:** Responstider per måned (Jan-Dec)
- **_FUND.txt:** Automatisk genererede fund og konklusioner

Regioner: Nordjylland, Hovedstaden, Sjælland, Midtjylland, Syddanmark

### System-analyser
- `07_prioritering_ABC.xlsx` - A vs B vs C prioritering (hastegradskoder)
- `09_rekvireringskanal.xlsx` - Responstid per rekvireringskanal
- `*_FUND.txt` - Automatisk genererede fund til hver analyse

### Datawrapper CSV-filer
CSV-filer optimeret til import i Datawrapper visualiseringstool:
- `DATAWRAPPER_alle_postnumre.csv` - Alle postnumre med farve-kategorier
- `DATAWRAPPER_prioritering_ABC.csv` - ABC prioritering
- `DATAWRAPPER_rekvireringskanal.csv` - Rekvireringskanal data
- `[Region]_DATAWRAPPER_responstid_per_*.csv` - Regionale tidsmønstre

### Rapporter
- `TIDSMÆSSIGE_ANALYSER_SAMMENFATNING.md` - Konsolideret sammenfatning af tidsmønstre

### Metadata
- `pipeline_run_metadata.json` - Teknisk metadata om pipeline-kørslen

## 🔍 BRUG AF FILER

**For journalister:**
1. Start med hovedrapporten (MASTER_FINDINGS_RAPPORT.md i rod-mappen)
2. Undersøg relevante Excel-filer for detaljer
3. Brug _FUND.txt-filer for hurtig opsummering
4. Import DATAWRAPPER CSV-filer direkte i Datawrapper

**For analytikere:**
1. Alle Excel-filer kan åbnes direkte i Excel/LibreOffice
2. CSV-filer kan importeres i ethvert dataværktøj
3. JSON metadata indeholder kørselsinfo

## ✅ VALIDERING

Pipeline er 100% valideret mod Nils Mulvads beregninger:
- 549 postnumre sammenlignet
- Maksimal afvigelse: 0.05 minutter (3 sekunder - kun afrundingsfejl)
- Se validering.md i rod-mappen for detaljer

## 📞 KONTAKT

Ved spørgsmål til data eller metode, kontakt Adam Holm eller Nils Mulvad.
"""


def organize_output(output_dir: Path, keep_unzipped: bool = False):
    """Organize output files into structured format.

    Args:
        output_dir: Path to output directory (default: 3_output/current)
        keep_unzipped: If True, keep bilag/ folder after zipping
    """
    print(f"\n{'='*80}")
    print("ORGANIZING OUTPUT FILES")
    print(f"{'='*80}\n")

    # Define main report file that stays in root
    main_report = "MASTER_FINDINGS_RAPPORT.md"

    # Check if main report exists
    main_report_path = output_dir / main_report
    if not main_report_path.exists():
        print(f"⚠️  WARNING: Main report not found: {main_report}")
        print(f"   Expected location: {main_report_path}")
        print(f"   Continuing anyway...\n")

    # Create bilag subdirectory
    bilag_dir = output_dir / "bilag"
    bilag_dir.mkdir(exist_ok=True)
    print(f"✓ Created bilag directory: {bilag_dir}")

    # Find all files to move (everything except main report and .gitkeep)
    files_to_move = []
    for item in output_dir.iterdir():
        if item.is_file() and item.name not in [main_report, '.gitkeep', 'bilag.zip']:
            files_to_move.append(item)

    print(f"✓ Found {len(files_to_move)} files to organize\n")

    # Move files to bilag directory
    print("Moving files to bilag/...")
    moved_count = 0
    for file_path in files_to_move:
        dest_path = bilag_dir / file_path.name
        shutil.move(str(file_path), str(dest_path))
        moved_count += 1
        if moved_count <= 5:  # Show first 5 files
            print(f"   → {file_path.name}")

    if moved_count > 5:
        print(f"   ... and {moved_count - 5} more files")

    print(f"\n✓ Moved {moved_count} files to bilag/\n")

    # Create README in bilag directory
    readme_path = bilag_dir / "README.txt"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(create_bilag_readme())
    print(f"✓ Created README.txt in bilag/")

    # Create ZIP archive
    zip_path = output_dir / "bilag.zip"
    print(f"\nCreating ZIP archive: {zip_path.name}...")

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in bilag_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(output_dir)
                zipf.write(file_path, arcname)

    zip_size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"✓ Created bilag.zip ({zip_size_mb:.2f} MB)")

    # Optionally remove unzipped bilag directory
    if not keep_unzipped:
        print(f"\nRemoving unzipped bilag/ directory...")
        shutil.rmtree(bilag_dir)
        print(f"✓ Removed bilag/ directory")
    else:
        print(f"\n✓ Keeping unzipped bilag/ directory")

    # Final summary
    print(f"\n{'='*80}")
    print("ORGANIZATION COMPLETE")
    print(f"{'='*80}\n")

    print("Final structure:")
    print(f"  {output_dir}/")
    if main_report_path.exists():
        print(f"    ├── {main_report} (hovedrapport)")
    print(f"    └── bilag.zip ({moved_count + 1} filer)")
    if keep_unzipped:
        print(f"    └── bilag/ (unzipped kopi)")

    print(f"\n✓ Output klar til deling!")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Organize pipeline output files for easy sharing"
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path(__file__).parent.parent / '3_output' / 'current',
        help='Path to output directory (default: 3_output/current)'
    )
    parser.add_argument(
        '--keep-unzipped',
        action='store_true',
        help='Keep unzipped bilag/ directory after creating ZIP'
    )

    args = parser.parse_args()

    # Verify output directory exists
    if not args.output_dir.exists():
        print(f"ERROR: Output directory not found: {args.output_dir}")
        return 1

    # Run organization
    try:
        organize_output(args.output_dir, args.keep_unzipped)
        return 0
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
