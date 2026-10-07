"""Run analytics pipeline after Excel data has been loaded into raw schema."""

import subprocess
import sys


steps = [
    "quality_report.py",
    "clean_data.py",
    "abc_xyz.py",
    "business_analysis.py",
    "create_views.py",
]


def run_uploaded_pipeline() -> None:
    for step in steps:
        print(f"\n=== Running {step} ===")

        result = subprocess.run(
            [sys.executable, f"src/{step}"],
            check=False,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"Pipeline failed while running {step}"
            )

    print("\n=== UPLOADED DATA PIPELINE COMPLETED SUCCESSFULLY ===")


if __name__ == "__main__":
    run_uploaded_pipeline()