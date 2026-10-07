"""Import an uploaded Excel workbook into the PostgreSQL raw schema."""

from pathlib import Path

import pandas as pd
from sqlalchemy import inspect, text

from src.db import get_engine


REQUIRED_SHEETS = [
    "products",
    "customers",
    "sales",
    "promotions",
]


class ExcelValidationError(Exception):
    """Raised when the uploaded workbook does not match the expected structure."""


def get_existing_columns(engine, table_name: str) -> list[str]:
    inspector = inspect(engine)

    if not inspector.has_table(table_name, schema="raw"):
        raise ExcelValidationError(
            f"Raw table raw.{table_name} does not exist. "
            "Run the demo pipeline at least once before using Excel upload."
        )

    columns = inspector.get_columns(table_name, schema="raw")

    return [column["name"] for column in columns]


def validate_workbook(file_path: str | Path) -> dict[str, pd.DataFrame]:
    file_path = Path(file_path)

    if file_path.suffix.lower() != ".xlsx":
        raise ExcelValidationError("Only .xlsx files are supported.")

    workbook = pd.ExcelFile(file_path)

    missing_sheets = [
        sheet
        for sheet in REQUIRED_SHEETS
        if sheet not in workbook.sheet_names
    ]

    if missing_sheets:
        raise ExcelValidationError(
            "Missing required sheets: "
            + ", ".join(missing_sheets)
        )

    engine = get_engine()

    datasets: dict[str, pd.DataFrame] = {}

    for sheet_name in REQUIRED_SHEETS:
        df = pd.read_excel(file_path, sheet_name=sheet_name)

        expected_columns = get_existing_columns(
            engine,
            sheet_name,
        )

        uploaded_columns = list(df.columns)

        missing_columns = [
            column
            for column in expected_columns
            if column not in uploaded_columns
        ]

        extra_columns = [
            column
            for column in uploaded_columns
            if column not in expected_columns
        ]

        if missing_columns:
            raise ExcelValidationError(
                f"Sheet '{sheet_name}' is missing columns: "
                + ", ".join(missing_columns)
            )

        if extra_columns:
            raise ExcelValidationError(
                f"Sheet '{sheet_name}' contains unexpected columns: "
                + ", ".join(extra_columns)
            )

        # Keep the exact database column order.
        df = df[expected_columns]

        datasets[sheet_name] = df

    return datasets


def import_excel_to_raw(file_path: str | Path) -> dict[str, int]:
    datasets = validate_workbook(file_path)

    engine = get_engine()

    result_counts = {}

    with engine.begin() as connection:
        # Child/dependent tables should be cleared before master tables
        # if constraints are added later.
        for table_name in [
            "sales",
            "promotions",
            "products",
            "customers",
        ]:
            connection.execute(
                text(f'TRUNCATE TABLE raw."{table_name}"')
            )

        for table_name in REQUIRED_SHEETS:
            df = datasets[table_name]

            df.to_sql(
                table_name,
                connection,
                schema="raw",
                if_exists="append",
                index=False,
                method="multi",
                chunksize=1000,
            )

            result_counts[table_name] = len(df)

    return result_counts