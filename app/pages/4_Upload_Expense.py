import streamlit as st # type: ignore
from modules.upload_pdf.component.upload import pdf_upload # type: ignore
from modules.upload_pdf.pipeline.common import SOURCE_OPTIONS
from modules.upload_pdf.pipeline.pipeline import pipeline # type: ignore

st.set_page_config(page_title="Upload Expense", page_icon="💸", layout='wide')


def reset_upload_expense_state():
    for key in [
        "uploaded_pdf_files_list",
        "uploaded_pdf_sources",
        "selected_action",
        "pdf_uploader",
        "review_expense_data",
        "edit_mode_expense",
        "data_saved_expense",
    ]:
        st.session_state.pop(key, None)
    st.session_state["upload_pdf_state"] = True


def upload_expense():
    st.markdown(
        "<h1 style='color: #e74c3c; text-align: center;'>Upload Your Expenses PDF Here</h1>",
        unsafe_allow_html=True,
    )

    # ── Prepaid & Refund rules info box ──────────────────────────────────
    st.info(
        "**📌 Before you upload — Prepaid vs Refund rules:**\n\n"
        "**Prepaid items on your statement (e.g. you paid for a friend, expect full repayment soon):** "
        "Delete that row from the data editor before saving. "
        "It should not enter your bookkeeping.\n\n"
        "**Paid and waiting for a refund (e.g. hotel deposit, returned item, cancelled booking):** "
        "Keep the row and save it as normal. "
        "When the refund arrives, go to **Page 16 Expense Editor** to update the amount or delete the record. "
        "If it was a regular expense affecting that month's saving total, go to **Page 6** and click **Rerun Calculation**. "
        "If it had a Fund Withdrawal, the linked transaction updates automatically."
    )

    # ── Quick Reference Notes ─────────────────────────────────────────────
    with st.expander("📋 Quick Reference Notes (click to expand)", expanded=False):
        st.markdown("""
        | Topic | Note |
        |---|---|
        | 📅 **Statement Date** | Dates are read from the statement text when available. Confirm the year in the review table before saving. |
        | 🏠 **House Expenses** | Exclude house-related items (pre-filtered by the ETL pipeline). |
        | ✈️ **Traveling Rows** | Set the Trip and Traveling Category in the data editor for traveling rows. |
        | 💰 **Fund Withdrawal** | Set a Primary Target Fund in the editor to auto-create a withdrawal from Main Chequing. |
        | 🗑️ **Prepaid Rows** | Delete prepaid rows (friend's share you expect back soon) from the editor before saving. |
        | ✏️ **Refunds Later** | For paid items with pending refunds, save normally and edit on Page 16 when refund arrives. |
        """)

    # ── State init ────────────────────────────────────────────────────────
    if 'upload_pdf_state' not in st.session_state:
        st.session_state['upload_pdf_state'] = True
        st.session_state['uploaded_pdf_files_list'] = []
        st.session_state['uploaded_pdf_sources'] = {}

    if st.session_state['upload_pdf_state']:
        uploaded_pdf = pdf_upload()
        if uploaded_pdf:
            st.session_state['uploaded_pdf_files_list'] = uploaded_pdf
            st.success(f"Uploaded {len(uploaded_pdf)} file(s).")
            st.markdown("### Statement sources")
            st.caption("Choose the source for each file so each statement uses the right ETL pipeline.")
            selected_sources = {}
            for index, uploaded_file in enumerate(uploaded_pdf):
                current_source = st.session_state.get("uploaded_pdf_sources", {}).get(
                    uploaded_file.name,
                    SOURCE_OPTIONS[0],
                )
                selected_sources[uploaded_file.name] = st.selectbox(
                    uploaded_file.name,
                    SOURCE_OPTIONS,
                    index=SOURCE_OPTIONS.index(current_source)
                    if current_source in SOURCE_OPTIONS
                    else 0,
                    key=f"source_{index}_{uploaded_file.name}",
                )
            st.session_state["uploaded_pdf_sources"] = selected_sources

        if st.button("Submit"):
            if not st.session_state.get("uploaded_pdf_files_list"):
                st.warning("Upload at least one statement before submitting.")
            else:
                st.session_state['upload_pdf_state'] = False
                st.rerun()
    else:
        if st.session_state.get('uploaded_pdf_files_list'):
            done = pipeline(
                st.session_state['uploaded_pdf_files_list'],
                st.session_state.get("uploaded_pdf_sources", {}),
            )
            if done:
                reset_upload_expense_state()
                st.rerun()


if __name__ == "__main__":
    upload_expense()
