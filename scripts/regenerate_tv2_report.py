"""Quick script to regenerate MASTER_FINDINGS_RAPPORT.md with TV2 format"""
import sys
from pathlib import Path

# Add 2_processing to path
sys.path.insert(0, str(Path(__file__).parent / "2_processing"))

from analyzers.summary_generator import generate_master_findings_report

# Regenerate report
output_dir = Path("3_output/current")
print("Regenerating MASTER_FINDINGS_RAPPORT.md with TV2-focused format...")
report_path = generate_master_findings_report(output_dir)
print(f"✓ Report regenerated: {report_path}")
print(f"\nFirst 100 lines of new TV2-focused report:")
print("=" * 80)

# Show first 100 lines
with open(report_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines[:100], 1):
        print(f"{i:4d} | {line}", end='')
