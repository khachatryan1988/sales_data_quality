"""Run the complete analytics pipeline in the required execution order."""

import subprocess
import sys

steps = [
    "generate_data.py",
    "load_raw.py",
    "quality_report.py",
    "clean_data.py",
    "abc_xyz.py",
    "business_analysis.py",
    "create_views.py",
]

for step in steps:
    print(f"\n=== Running {step} ===")
    result = subprocess.run([sys.executable, f"src/{step}"])
    if result.returncode != 0:
        raise SystemExit(result.returncode)

print("\n=== PIPELINE COMPLETED SUCCESSFULLY ===")
