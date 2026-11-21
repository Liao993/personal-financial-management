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
        return _pdfplumber_text(pdf_file)

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


def _parse_json_response(raw_response: str) -> dict:
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


def _normalize_transactions(payload: dict, payment_method: str) -> pd.DataFrame:
    rows = payload.get("transactions") if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        raise AIExtractionError("The extraction model returned no transaction list.")

    normalized = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        item = str(row.get("items") or "").strip()
        if not item:
            continue
        try:
            amount = float(row.get("amount"))
        except (TypeError, ValueError):
            continue
        if amount < 0:
            amount = abs(amount)
        if re.search(r"\bpayment\b", item, flags=re.IGNORECASE):
            continue

        category, traveling_category = _category_for_description(
            item, row.get("category")
        )
        normalized.append(
            {
                "date": row.get("date"),
                "items": item,
                "amount": amount,
                "category": category,
                "traveling_category": traveling_category,
                "trip": None,
                "amount_for_number_of_travelers": None,
                "paid_for_number_of_travlerers": None,
                "source_notes": row.get("source_notes"),
                "payment_method": payment_method,
            }
        )

    return pd.DataFrame(normalized)


def extract_expenses_with_ai(pdf_file, payment_method: str) -> pd.DataFrame:
    markdown = _docling_markdown(pdf_file)
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
    return _normalize_transactions(_parse_json_response(response), payment_method)
