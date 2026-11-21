from __future__ import annotations

import pandas as pd
import streamlit as st  # type: ignore

from modules.upload_pdf.pipeline.rbc.rbc_extracted import rbc_extracted
from modules.upload_pdf.pipeline.rbc.rbc_transformed import rbc_transformed
from modules.upload_pdf.pipeline.pc.pc_extracted import pc_extracted
from modules.upload_pdf.pipeline.pc.pc_transformed import pc_transformed
from modules.upload_pdf.pipeline.scotia_red.scotia_red_extracted import scotia_red_extracted
from modules.upload_pdf.pipeline.scotia_red.scotia_red_transformed import scotia_red_transformed
from modules.upload_pdf.pipeline.display import display_editable_dataframe
from modules.upload_pdf.pipeline.common import SOURCE_OPTIONS
from modules.upload_pdf.pipeline.common import AI_SOURCE
from modules.upload_pdf.pipeline.ai_extraction import extract_expenses_with_ai


PIPELINES = {
    "RBC": (rbc_extracted, rbc_transformed),
    "PC": (pc_extracted, pc_transformed),
    "Scotia_Red": (scotia_red_extracted, scotia_red_transformed),
}


def pipeline(pdf_files, source_by_filename, payment_method_by_filename=None):
    payment_method_by_filename = payment_method_by_filename or {}
    transformed_frames = []

    for pdf_file in pdf_files:
        source = source_by_filename.get(pdf_file.name, SOURCE_OPTIONS[0])
        selected_payment_method = payment_method_by_filename.get(pdf_file.name) or source
        if source == AI_SOURCE:
            payment_method = selected_payment_method
            try:
                transformed_data = extract_expenses_with_ai(
                    pdf_file,
                    payment_method,
                    filename=pdf_file.name,
                )
            except Exception as exc:
                st.error(f"Could not process {pdf_file.name} with AI/OCR: {exc}")
                continue
        else:
            if source not in PIPELINES:
                st.error(f"Unsupported statement source for {pdf_file.name}: {source}")
                continue

            extract_fn, transform_fn = PIPELINES[source]
            try:
                pdf_file.seek(0)
                extracted_data = extract_fn([pdf_file])
                transformed_data = transform_fn(extracted_data)
            except Exception as exc:
                st.error(f"Could not process {pdf_file.name} as {source}: {exc}")
                continue

        if transformed_data is None or transformed_data.empty:
            st.warning(f"No expense rows found in {pdf_file.name}.")
            continue

        transformed_data["payment_method"] = selected_payment_method
        transformed_data["statement_source"] = source
        transformed_data["statement_file"] = pdf_file.name
        transformed_data["injection_source"] = pdf_file.name  # persisted to DB
        transformed_frames.append(transformed_data)

    if not transformed_frames:
        st.error("No valid expense rows were extracted from the uploaded statements.")
        return False

    combined_data = pd.concat(transformed_frames, ignore_index=True)
    return display_editable_dataframe(combined_data)
