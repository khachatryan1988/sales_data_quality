"""FastAPI web interface for Excel upload, analytics and Data Quality."""

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
from src.excel_import import ExcelValidationError, import_excel_to_raw


BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR.parent
APP_DIR = SRC_DIR.parent
UPLOAD_DIR = APP_DIR / "data" / "uploads"

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
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


app = FastAPI(
    title="Sales & Data Quality Analytics System",
    description=(
        "Excel ingestion, Data Quality validation, "
        "business analytics, web dashboards, "
        "Excel reporting and Power BI-ready marts."
    ),
    version="2.0.0",
)


templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


def query_records(query: str) -> list[dict]:
    engine = get_engine()

    df = pd.read_sql(
        query,
        engine,
    )

    return df.to_dict(
        orient="records"
    )


def query_one(query: str) -> dict:
    records = query_records(query)

    if not records:
        return {}

    return records[0]


def render_error(
        request: Request,
        message: str,
):
    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "success": False,
            "error": message,
        },
    )


def get_statistics() -> dict:
    engine = get_engine()

    queries = {
        "raw_products":
            "SELECT COUNT(*) FROM raw.products",

        "raw_customers":
            "SELECT COUNT(*) FROM raw.customers",

        "raw_sales":
            "SELECT COUNT(*) FROM raw.sales",

        "raw_promotions":
            "SELECT COUNT(*) FROM raw.promotions",

        "clean_products":
            "SELECT COUNT(*) FROM clean.products",

        "clean_customers":
            "SELECT COUNT(*) FROM clean.customers",

        "clean_sales":
            "SELECT COUNT(*) FROM clean.sales",

        "clean_promotions":
            "SELECT COUNT(*) FROM clean.promotions",

        "data_quality_issues": """
            SELECT COUNT(*)
            FROM analytics.data_quality_issues
        """,
    }

    result = {}

    with engine.connect() as connection:

        for key, query in queries.items():

            result[key] = connection.execute(
                text(query)
            ).scalar_one()

        score = connection.execute(
            text(
                """
                SELECT data_quality_score_pct
                FROM analytics.data_quality_score
                LIMIT 1
                """
            )
        ).scalar_one_or_none()

        result["data_quality_score"] = score

    return result


def format_excel_sheet(
        writer: pd.ExcelWriter,
        sheet_name: str,
) -> None:

    worksheet = writer.book[
        sheet_name
    ]

    worksheet.freeze_panes = "A2"

    worksheet.auto_filter.ref = (
        worksheet.dimensions
    )

    for cells in worksheet.columns:

        max_length = 0

        column_letter = (
            cells[0]
            .column_letter
        )

        for cell in cells:

            if cell.value is not None:

                max_length = max(
                    max_length,
                    len(str(cell.value)),
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


@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@app.get(
    "/dashboard",
    response_class=HTMLResponse,
)
def dashboard(request: Request):

    kpi = query_one(
        """
        SELECT *
        FROM analytics.kpi_summary
        LIMIT 1
        """
    )

    monthly = query_records(
        """
        SELECT *
        FROM analytics.monthly_sales
        ORDER BY year_month
        """
    )

    channels = query_records(
        """
        SELECT *
        FROM analytics.channel_sales
        ORDER BY revenue DESC
        """
    )

    managers = query_records(
        """
        SELECT *
        FROM analytics.manager_sales
        ORDER BY revenue DESC
        """
    )

    top_products = query_records(
        """
        SELECT *
        FROM analytics.product_sales
        ORDER BY revenue DESC
        LIMIT 10
        """
    )

    categories = query_records(
        """
        SELECT *
        FROM analytics.v_sales_by_category
        ORDER BY revenue DESC
        """
    )

    # -----------------------------------------------------
    # Prepare JSON-safe data for Chart.js
    # -----------------------------------------------------

    monthly_labels = [
        str(row["year_month"])
        for row in monthly
    ]

    monthly_values = [
        float(row["revenue"] or 0)
        for row in monthly
    ]

    channel_labels = [
        str(row["channel"])
        for row in channels
    ]

    channel_values = [
        float(row["revenue"] or 0)
        for row in channels
    ]

    manager_labels = [
        str(row["manager"])
        for row in managers
    ]

    manager_values = [
        float(row["revenue"] or 0)
        for row in managers
    ]

    category_labels = [
        str(row["category"])
        for row in categories
    ]

    category_values = [
        float(row["revenue"] or 0)
        for row in categories
    ]

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "kpi": kpi,

            "monthly": monthly,
            "channels": channels,
            "managers": managers,
            "top_products": top_products,
            "categories": categories,

            "monthly_labels": monthly_labels,
            "monthly_values": monthly_values,

            "channel_labels": channel_labels,
            "channel_values": channel_values,

            "manager_labels": manager_labels,
            "manager_values": manager_values,

            "category_labels": category_labels,
            "category_values": category_values,
        },
    )



@app.get(
    "/products",
    response_class=HTMLResponse,
)
def product_analysis(request: Request):

    top_products = query_records(
        """
        SELECT *
        FROM analytics.product_sales
        ORDER BY revenue DESC
        LIMIT 15
        """
    )

    categories = query_records(
        """
        SELECT *
        FROM analytics.v_sales_by_category
        ORDER BY revenue DESC
        """
    )

    brands = query_records(
        """
        SELECT *
        FROM analytics.v_sales_by_brand
        ORDER BY revenue DESC
        LIMIT 15
        """
    )

    abc = query_records(
        """
        SELECT
            abc_class,
            COUNT(*) AS products
        FROM analytics.product_abc_xyz
        GROUP BY abc_class
        ORDER BY abc_class
        """
    )

    xyz = query_records(
        """
        SELECT
            xyz_class,
            COUNT(*) AS products
        FROM analytics.product_abc_xyz
        GROUP BY xyz_class
        ORDER BY xyz_class
        """
    )

    matrix = query_records(
        """
        SELECT
            abc_xyz_class,
            COUNT(*) AS products
        FROM analytics.product_abc_xyz
        GROUP BY abc_xyz_class
        ORDER BY abc_xyz_class
        """
    )

    return templates.TemplateResponse(
        request=request,
        name="products.html",
        context={
            "top_products": top_products,
            "categories": categories,
            "brands": brands,
            "abc": abc,
            "xyz": xyz,
            "matrix": matrix,
        },
    )


@app.get(
    "/customers",
    response_class=HTMLResponse,
)
def customer_analysis(
        request: Request,
):

    top_customers = query_records(
        """
        SELECT *
        FROM analytics.customer_sales
        ORDER BY revenue DESC
        LIMIT 15
        """
    )

    by_city = query_records(
        """
        SELECT
            city,
            SUM(revenue) AS revenue,
            SUM(orders) AS orders
        FROM analytics.customer_sales
        GROUP BY city
        ORDER BY revenue DESC
        """
    )

    by_type = query_records(
        """
        SELECT
            customer_type,
            SUM(revenue) AS revenue,
            SUM(orders) AS orders
        FROM analytics.customer_sales
        GROUP BY customer_type
        ORDER BY revenue DESC
        """
    )

    return templates.TemplateResponse(
        request=request,
        name="customers.html",
        context={
            "top_customers": top_customers,
            "by_city": by_city,
            "by_type": by_type,
        },
    )


@app.get(
    "/promotions",
    response_class=HTMLResponse,
)
def promotion_analysis(
        request: Request,
):

    promotions = query_records(
        """
        SELECT *
        FROM analytics.promo_analysis
        ORDER BY
            revenue_uplift_pct DESC
            NULLS LAST
        """
    )

    return templates.TemplateResponse(
        request=request,
        name="promotions.html",
        context={
            "promotions": promotions,
        },
    )


@app.get(
    "/data-quality",
    response_class=HTMLResponse,
)
def data_quality_dashboard(
        request: Request,
):

    score = query_one(
        """
        SELECT *
        FROM analytics.data_quality_score
        LIMIT 1
        """
    )

    summary = query_records(
        """
        SELECT *
        FROM analytics.data_quality_summary
        ORDER BY error_count DESC
        """
    )

    by_type = query_records(
        """
        SELECT
            issue_type,
            COUNT(*) AS issues
        FROM analytics.data_quality_issues
        GROUP BY issue_type
        ORDER BY issues DESC
        """
    )

    by_table = query_records(
        """
        SELECT
            table_name,
            COUNT(*) AS issues
        FROM analytics.data_quality_issues
        GROUP BY table_name
        ORDER BY issues DESC
        """
    )

    return templates.TemplateResponse(
        request=request,
        name="data_quality.html",
        context={
            "score": score,
            "summary": summary,
            "by_type": by_type,
            "by_table": by_table,
        },
    )


@app.get(
    "/issues",
    response_class=HTMLResponse,
)
def view_issues(request: Request):

    issues = query_records(
        """
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
    )

    return templates.TemplateResponse(
        request=request,
        name="issues.html",
        context={
            "issues": issues,
            "total": len(issues),
        },
    )


@app.get("/template")
def download_template():

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

            df = pd.read_sql(
                f"""
                SELECT *
                FROM raw.{table_name}
                LIMIT 0
                """,
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
        template_path,
        filename="sales_data_template.xlsx",
        media_type=EXCEL_MEDIA_TYPE,
    )


@app.get("/sample")
def download_sample():

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

            df = pd.read_sql(
                f"""
                SELECT *
                FROM raw.{table_name}
                ORDER BY 1
                """,
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
        sample_path,
        filename="sales_data_sample.xlsx",
        media_type=EXCEL_MEDIA_TYPE,
    )


@app.get("/report")
def download_report():

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
                check_name
        """,

        "Clean Products": """
            SELECT *
            FROM clean.products
        """,

        "Clean Customers": """
            SELECT *
            FROM clean.customers
        """,

        "Clean Sales": """
            SELECT *
            FROM clean.sales
        """,

        "Clean Promotions": """
            SELECT *
            FROM clean.promotions
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
        """,
    }

    with pd.ExcelWriter(
            report_path,
            engine="openpyxl",
    ) as writer:

        for sheet_name, query in (
                datasets.items()
        ):

            df = pd.read_sql(
                query,
                engine,
            )

            safe_name = (
                sheet_name[:31]
            )

            df.to_excel(
                writer,
                sheet_name=safe_name,
                index=False,
            )

            format_excel_sheet(
                writer,
                safe_name,
            )

    return FileResponse(
        report_path,
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

    destination = (
            UPLOAD_DIR
            / f"{uuid.uuid4().hex}_{safe_filename}"
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

            raise RuntimeError(
                result.stderr
                or result.stdout
                or "Pipeline failed."
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