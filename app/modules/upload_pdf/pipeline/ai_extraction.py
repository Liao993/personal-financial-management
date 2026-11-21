from __future__ import annotations

import json
import re
import tempfile
from pathlib import Path

import pandas as pd

from modules.ai_semantic.ollama_client import ask_ollama
from modules.upload_pdf.middle_layer.common_category import (
    categorize_description_with_common_stores,
)
from modules.upload_pdf.middle_layer.travel_category import categorize_description_travel
from utils.data import (
    common_store_directory,
    expense_category_options,
    hotel_booking,
    traveling_category_options,
)


class AIExtractionError(RuntimeError):
    """Raised when the AI/OCR extraction route cannot produce review rows."""


def _docling_markdown(pdf_file) -> str:
    """Convert a PDF to layout-aware Markdown using Docling + OCR."""
    try:
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import PdfPipelineOptions, RapidOcrOptions
        from docling.document_converter import DocumentConverter, PdfFormatOption
    except ImportError as exc:
        raise AIExtractionError(
            "This PDF has no readable text layer. Install Docling to enable OCR "
            "for scanned statements."
        ) from exc

    pdf_file.seek(0)
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temporary_file:
        temporary_file.write(pdf_file.read())
        temporary_path = Path(temporary_file.name)

    try:
        options = PdfPipelineOptions()
        options.do_ocr = True
        options.do_table_structure = True
        options.ocr_options = RapidOcrOptions(lang=["en"], model_size="tiny")
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=options),
            }
        )
        result = converter.convert(str(temporary_path))
        markdown = result.document.export_to_markdown()
        if not markdown or not markdown.strip():
            raise AIExtractionError("Docling returned no readable text from the PDF.")
        return markdown
    finally:
        temporary_path.unlink(missing_ok=True)


def _pdfplumber_text(pdf_file) -> str:
    """Lightweight fallback for born-digital PDFs when Docling is unavailable."""
    import pdfplumber

    pdf_file.seek(0)
    pages = []
    with pdfplumber.open(pdf_file) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                pages.append(f"\n## Page {page_number}\n{text}")
    if not pages:
        raise AIExtractionError(
            "No text layer was found. Install Docling for layout recognition and OCR "
            "when processing scanned PDFs."
        )
    return "\n".join(pages)


def _extract_document_markdown(pdf_file) -> str:
    """Use the fast text path first; reserve Docling/OCR for scanned PDFs."""
    try:
        return _pdfplumber_text(pdf_file)
    except AIExtractionError:
        return _docling_markdown(pdf_file)


def _parse_json_response(raw_response: str):
    try:
        return json.loads(raw_response)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw_response, flags=re.DOTALL)
        if not match:
            raise AIExtractionError("The extraction model did not return valid JSON.")
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            raise AIExtractionError("The extraction model returned malformed JSON.") from exc


def _transaction_rows(payload) -> list[dict]:
    """Accept the canonical response and common equivalent model responses."""
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if not isinstance(payload, dict):
        return []

    for key in ("transactions", "expenses", "rows", "records", "data", "items"):
        candidate = payload.get(key)
        if isinstance(candidate, list):
            return [row for row in candidate if isinstance(row, dict)]

    # Some models return a single transaction object instead of a list.
    if any(key in payload for key in ("date", "transaction_date", "description", "merchant")):
        return [payload]
    return []


def _category_for_description(description: str, proposed_category: str | None) -> tuple[str, str | None]:
    """Apply deterministic existing rules before accepting an LLM category."""
    travel_category = categorize_description_travel(description)
    if travel_category:
        subcategory = "Hotel" if any(word in description.upper() for word in hotel_booking) else "Food"
        return travel_category, subcategory

    known_category = categorize_description_with_common_stores(
        description, common_store_directory
    )
    if known_category:
        return known_category, None

    if proposed_category in expense_category_options:
        proposed_travel = proposed_category == "Traveling"
        if proposed_travel:
            return "Traveling", "Food"
        return proposed_category, None
    return "Not Categorized", None


def _normalize_transactions(payload, payment_method: str) -> pd.DataFrame:
    rows = _transaction_rows(payload)
    if not rows:
        raise AIExtractionError(
            "The extraction model returned no recognizable transaction rows. "
            "Expected transactions, expenses, rows, records, or data."
        )

    normalized = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        item = str(
            row.get("items")
            or row.get("description")
            or row.get("merchant")
            or row.get("merchant_name")
            or ""
        ).strip()
        if not item:
            continue
        try:
            amount = float(
                row.get("amount")
                if row.get("amount") is not None
                else row.get("transaction_amount", row.get("charge", row.get("value")))
            )
        except (TypeError, ValueError):
            continue
        if amount < 0:
            amount = abs(amount)
        if re.search(r"\bpayment\b", item, flags=re.IGNORECASE):
            continue

        category, traveling_category = _category_for_description(
            item, row.get("category")
        )
        parsed_date = pd.to_datetime(
            row.get("date") or row.get("transaction_date") or row.get("purchase_date"),
            errors="coerce",
        )
        normalized_date = None if pd.isna(parsed_date) else parsed_date.date()
        normalized.append(
            {
                "date": normalized_date,
                "items": item,
                "amount": amount,
                "category": category,
                "traveling_category": traveling_category,
                "trip": None,
                "amount_for_number_of_travelers": None,
                "paid_for_number_of_travlerers": None,
                "source_notes": row.get("source_notes") or row.get("notes"),
                "payment_method": payment_method,
            }
        )

    return pd.DataFrame(normalized)


def extract_expenses_with_ai(pdf_file, payment_method: str) -> pd.DataFrame:
    markdown = _extract_document_markdown(pdf_file)
    # Keep prompts bounded while retaining the beginning and end of statements,
    # where headers and closing transactions commonly appear.
    if len(markdown) > 80000:
        markdown = markdown[:60000] + "\n...[middle omitted]...\n" + markdown[-20000:]

    categories = ", ".join(expense_category_options)
    travel_categories = ", ".join(traveling_category_options)
    store_rules = json.dumps(common_store_directory, sort_keys=True)
    system_prompt = f"""You convert credit-card statement content into expense review rows.
Return JSON only with this shape:
{{"transactions": [{{"date":"YYYY-MM-DD", "items":"merchant description", "amount": 0.0,
"category":"category", "source_notes":null}}]}}

Rules:
- Extract purchases/charges only; omit payments, credits, balances, fees without a purchase description, headers, and totals.
- Amount must be a positive number. Preserve the transaction date and infer the statement year from the document.
- category must be one of: {categories}, or "Not Categorized" when uncertain.
- Existing store mappings are authoritative where the merchant text matches: {store_rules}
- Use Traveling for travel merchants/locations only when clearly supported; otherwise use the best category or Not Categorized.
- Traveling subcategories available for later review are: {travel_categories}.
- Never invent a trip name. The human review page will assign trips and fund withdrawals.
"""
    user_prompt = (
        f"Statement source/card: {payment_method}\n\n"
        "Extract every transaction from this document:\n\n"
        f"{markdown}"
    )
    try:
        response = ask_ollama(system_prompt, user_prompt, expect_json=True)
    except Exception as exc:
        raise AIExtractionError(f"AI extraction failed: {exc}") from exc

    parsed_response = _parse_json_response(response)
    try:
        return _normalize_transactions(parsed_response, payment_method)
    except AIExtractionError as first_error:
        # A short repair call handles models that returned valid JSON with the
        # wrong top-level shape, without reprocessing the PDF.
        repair_prompt = f"""The previous extraction response was valid JSON but did not contain
recognizable transaction rows. Convert it to exactly this JSON shape:
{{"transactions": [{{"date":"YYYY-MM-DD", "items":"merchant", "amount": 0.0,
"category":"Not Categorized", "source_notes":null}}]}}
Keep every actual purchase, omit payments/totals, and return JSON only.

Previous response:
{response}
"""
        try:
            repaired = ask_ollama(
                "You repair transaction-extraction JSON. Return JSON only.",
                repair_prompt,
                expect_json=True,
            )
            return _normalize_transactions(_parse_json_response(repaired), payment_method)
        except Exception as repair_error:
            raise AIExtractionError(
                f"{first_error} Repair attempt also failed: {repair_error}"
            ) from repair_error
