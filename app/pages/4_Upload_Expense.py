import streamlit as st # type: ignore
from modules.upload_pdf.component.upload import pdf_upload # type: ignore
from modules.upload_pdf.pipeline.pipeline import pipeline # type: ignore

st.set_page_config(page_title="Upload Expense", page_icon="💸", layout='wide')


def reset_upload_expense_state():
    for key in [
        "uploaded_pdf_files_list",
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
        | 📁 **File Name** | Don't rename the PDF — the filename is used to extract the statement year. |
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
        st.session_state['selected_action'] = None

    if st.session_state['upload_pdf_state']:
        action_options = ["RBC", "PC", "Scotia_Red"]
        st.session_state['selected_action'] = st.selectbox(
            "Which Bank for your statements?", action_options
        )
        uploaded_pdf = pdf_upload()
        if uploaded_pdf:
            st.session_state['uploaded_pdf_files_list'] = uploaded_pdf
            st.success(f"Uploaded {len(uploaded_pdf)} file(s).")

        if st.button("Submit"):
            st.session_state['upload_pdf_state'] = False
            st.rerun()
    else:
        if st.session_state.get('uploaded_pdf_files_list'):
            done = pipeline(
                st.session_state['selected_action'],
                st.session_state['uploaded_pdf_files_list'],
            )
            if done:
                reset_upload_expense_state()
                st.rerun()


if __name__ == "__main__":
    upload_expense()
