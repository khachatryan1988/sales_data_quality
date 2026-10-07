"""FastAPI web interface for Excel upload and analytics execution."""

from pathlib import Path
import shutil
import subprocess
import sys
import uuid

import pandas as pd
from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text

from src.db import get_engine
from src.excel_import import (
    ExcelValidationError,
    import_excel_to_raw,
)


BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR.parent
APP_DIR = SRC_DIR.parent

UPLOAD_DIR = APP_DIR / "data" / "uploads"

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


app = FastAPI(
    title="Sales & Data Quality Analytics System",
    description=(
        "Upload Excel datasets, validate data quality, "
        "run the analytics pipeline, and export reports."
    ),
    version="1.0.0",
)


templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


RAW_TABLES = [
    "products",
    "customers",
    "sales",
    "promotions",
]


EXCEL_MEDIA_TYPE = (
    "application/vnd.openxmlformats-officedocument."
    "spreadsheetml.sheet"
)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """Render the Excel upload page."""

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@app.get("/template")
def download_template():
    """
    Generate an empty Excel workbook with the exact columns
    currently used by PostgreSQL raw tables.
    """

    engine = get_engine()

    template_path = (
            UPLOAD_DIR
            / "sales_data_template.xlsx"
    )

    with pd.ExcelWriter(
            template_path,
            engine="openpyxl",
    ) as writer:

        for table_name in RAW_TABLES:

            query = f"""
                SELECT *
                FROM raw.{table_name}
                LIMIT 0
            """

            df = pd.read_sql(
                query,
                engine,
            )

            df.to_excel(
                writer,
                sheet_name=table_name,
                index=False,
            )

            format_excel_sheet(
                writer,
                table_name,
            )

    return FileResponse(
        path=template_path,
        filename="sales_data_template.xlsx",
        media_type=EXCEL_MEDIA_TYPE,
    )


@app.get("/sample")
def download_sample():
    """
    Export the current PostgreSQL raw data
    into a complete Excel workbook.
    """

    engine = get_engine()

    sample_path = (
            UPLOAD_DIR
            / "sales_data_sample.xlsx"
    )

    with pd.ExcelWriter(
            sample_path,
            engine="openpyxl",
    ) as writer:

        for table_name in RAW_TABLES:

            query = f"""
                SELECT *
                FROM raw.{table_name}
                ORDER BY 1
            """

            df = pd.read_sql(
                query,
                engine,
            )

            df.to_excel(
                writer,
                sheet_name=table_name,
                index=False,
            )

            format_excel_sheet(
                writer,
                table_name,
            )

    return FileResponse(
        path=sample_path,
        filename="sales_data_sample.xlsx",
        media_type=EXCEL_MEDIA_TYPE,
    )


@app.get(
    "/issues",
    response_class=HTMLResponse,
)
def view_issues(request: Request):
    """
    Display the currently detected Data Quality issues.
    """

    engine = get_engine()

    query = """
        SELECT
            check_name,
            table_name,
            issue_type,
            row_key,
            detail
        FROM analytics.data_quality_issues
        ORDER BY
            table_name,
            check_name,
            row_key
    """

    issues_df = pd.read_sql(
        query,
        engine,
    )

    return templates.TemplateResponse(
        request=request,
        name="issues.html",
        context={
            "issues": issues_df.to_dict(
                orient="records"
            ),
            "total": len(issues_df),
        },
    )


@app.get("/report")
def download_report():
    """
    Generate a complete Excel analytics
    and Data Quality report.
    """

    engine = get_engine()

    report_path = (
            UPLOAD_DIR
            / "data_quality_report.xlsx"
    )

    datasets = {
        "Summary": """
            SELECT *
            FROM analytics.data_quality_score
        """,

        "Issue Summary": """
            SELECT *
            FROM analytics.data_quality_summary
            ORDER BY error_count DESC
        """,

        "Issues": """
            SELECT *
            FROM analytics.data_quality_issues
            ORDER BY
                table_name,
                check_name,
                row_key
        """,

        "Clean Products": """
            SELECT *
            FROM clean.products
            ORDER BY product_id
        """,

        "Clean Customers": """
            SELECT *
            FROM clean.customers
            ORDER BY customer_id
        """,

        "Clean Sales": """
            SELECT *
            FROM clean.sales
            ORDER BY
                order_date,
                order_id
        """,

        "Clean Promotions": """
            SELECT *
            FROM clean.promotions
            ORDER BY promotion_id
        """,

        "ABC_XYZ": """
            SELECT *
            FROM analytics.product_abc_xyz
            ORDER BY total_revenue DESC
        """,

        "KPI Summary": """
            SELECT *
            FROM analytics.kpi_summary
        """,

        "Product Sales": """
            SELECT *
            FROM analytics.product_sales
            ORDER BY revenue DESC
        """,

        "Customer Sales": """
            SELECT *
            FROM analytics.customer_sales
            ORDER BY revenue DESC
        """,

        "Channel Sales": """
            SELECT *
            FROM analytics.channel_sales
            ORDER BY revenue DESC
        """,

        "Manager Sales": """
            SELECT *
            FROM analytics.manager_sales
            ORDER BY revenue DESC
        """,

        "Monthly Sales": """
            SELECT *
            FROM analytics.monthly_sales
            ORDER BY year_month
        """,

        "Promo Analysis": """
            SELECT *
            FROM analytics.promo_analysis
            ORDER BY campaign_name
        """,
    }

    with pd.ExcelWriter(
            report_path,
            engine="openpyxl",
    ) as writer:

        for sheet_name, query in datasets.items():

            df = pd.read_sql(
                query,
                engine,
            )

            safe_sheet_name = sheet_name[:31]

            df.to_excel(
                writer,
                sheet_name=safe_sheet_name,
                index=False,
            )

            format_excel_sheet(
                writer,
                safe_sheet_name,
            )

    return FileResponse(
        path=report_path,
        filename="data_quality_report.xlsx",
        media_type=EXCEL_MEDIA_TYPE,
    )


@app.post(
    "/upload",
    response_class=HTMLResponse,
)
async def upload_excel(
        request: Request,
        file: UploadFile = File(...),
):
    """
    Upload an Excel workbook, validate it,
    load it into raw PostgreSQL tables,
    and execute the analytics pipeline.
    """

    if not file.filename:

        return render_error(
            request,
            "No file selected.",
        )

    if not file.filename.lower().endswith(
            ".xlsx"
    ):

        return render_error(
            request,
            "Only .xlsx files are allowed.",
        )

    safe_filename = Path(
        file.filename
    ).name

    unique_name = (
        f"{uuid.uuid4().hex}_"
        f"{safe_filename}"
    )

    destination = (
            UPLOAD_DIR
            / unique_name
    )

    try:

        with destination.open(
                "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer,
            )

        counts = import_excel_to_raw(
            destination
        )

        pipeline_script = (
                SRC_DIR
                / "run_uploaded_pipeline.py"
        )

        result = subprocess.run(
            [
                sys.executable,
                str(pipeline_script),
            ],
            cwd=str(APP_DIR),
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:

            error_message = (
                    result.stderr.strip()
                    or result.stdout.strip()
                    or "Pipeline failed."
            )

            raise RuntimeError(
                error_message
            )

        statistics = get_statistics()

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "success": True,
                "filename": safe_filename,
                "counts": counts,
                "statistics": statistics,
                "pipeline_output": result.stdout,
            },
        )

    except ExcelValidationError as exc:

        return render_error(
            request,
            str(exc),
        )

    except Exception as exc:

        return render_error(
            request,
            str(exc),
        )

    finally:

        try:
            await file.close()
        except Exception:
            pass

        if destination.exists():

            try:
                destination.unlink()

            except OSError:
                pass


def render_error(
        request: Request,
        message: str,
):
    """Render a user-friendly upload error."""

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "success": False,
            "error": message,
        },
    )


def get_statistics() -> dict:
    """
    Read the main processing statistics
    from PostgreSQL.
    """

    engine = get_engine()

    queries = {

        "raw_products": """
            SELECT COUNT(*)
            FROM raw.products
        """,

        "raw_customers": """
            SELECT COUNT(*)
            FROM raw.customers
        """,

        "raw_sales": """
            SELECT COUNT(*)
            FROM raw.sales
        """,

        "raw_promotions": """
            SELECT COUNT(*)
            FROM raw.promotions
        """,

        "clean_products": """
            SELECT COUNT(*)
            FROM clean.products
        """,

        "clean_customers": """
            SELECT COUNT(*)
            FROM clean.customers
        """,

        "clean_sales": """
            SELECT COUNT(*)
            FROM clean.sales
        """,

        "clean_promotions": """
            SELECT COUNT(*)
            FROM clean.promotions
        """,

        "data_quality_issues": """
            SELECT COUNT(*)
            FROM analytics.data_quality_issues
        """,
    }

    result = {}

    with engine.connect() as connection:

        for key, query in queries.items():

            result[key] = (
                connection.execute(
                    text(query)
                )
                .scalar_one()
            )

        try:

            score = connection.execute(
                text(
                    """
                    SELECT
                        data_quality_score_pct
                    FROM analytics.data_quality_score
                    LIMIT 1
                    """
                )
            ).scalar_one_or_none()

            result[
                "data_quality_score"
            ] = score

        except Exception:

            result[
                "data_quality_score"
            ] = None

    return result


def format_excel_sheet(
        writer: pd.ExcelWriter,
        sheet_name: str,
) -> None:
    """
    Apply basic usability formatting
    to an exported Excel worksheet.
    """

    worksheet = (
        writer.book[
            sheet_name
        ]
    )

    worksheet.freeze_panes = "A2"

    worksheet.auto_filter.ref = (
        worksheet.dimensions
    )

    for column_cells in (
            worksheet.columns
    ):

        max_length = 0

        column_letter = (
            column_cells[0]
            .column_letter
        )

        for cell in column_cells:

            value = cell.value

            if value is None:
                continue

            max_length = max(
                max_length,
                len(str(value)),
            )

        worksheet.column_dimensions[
            column_letter
        ].width = min(
            max(
                max_length + 2,
                10,
                ),
            45,
        )