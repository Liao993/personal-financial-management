import streamlit as st  # type: ignore

from modules.ai_semantic.router import METRICS, answer_question


st.set_page_config(
    page_title="AI Semantic Chat",
    page_icon=":material/query_stats:",
    layout="wide",
    initial_sidebar_state="expanded",
)


def semantic_chat_page():
    st.markdown(
        "<h1 style='color: #16a085; text-align: center;'>AI Financial Assistant</h1>",
        unsafe_allow_html=True,
    )
    st.caption(
        "Answers are routed through metrics defined in semantic_layer.yml. "
        "The model selects a metric; it does not write SQL."
    )

    with st.expander("Available semantic metrics"):
        for name, definition in METRICS.items():
            st.markdown(f"**{name}**: {definition.get('description', '')}")

    if "semantic_chat_history" not in st.session_state:
        st.session_state["semantic_chat_history"] = []

    for entry in st.session_state["semantic_chat_history"]:
        with st.chat_message(entry["role"]):
            st.write(entry["content"])
            if entry.get("metric"):
                st.caption(f"Metric: `{entry['metric']}` = {entry['value']:.2f}")

    question = st.chat_input("Ask about income, spending, savings, or portfolio value")
    if not question:
        return

    st.session_state["semantic_chat_history"].append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Routing through semantic layer..."):
            result = answer_question(question)
        st.write(result["answer"])
        if result["mode"] == "semantic_layer":
            st.caption(f"Metric: `{result['metric']}` = {result['value']:.2f}")

    st.session_state["semantic_chat_history"].append(
        {
            "role": "assistant",
            "content": result["answer"],
            "metric": result["metric"] if result["mode"] == "semantic_layer" else None,
            "value": result["value"] if result["mode"] == "semantic_layer" else None,
        }
    )


if __name__ == "__main__":
    semantic_chat_page()
