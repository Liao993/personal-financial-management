import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import plotly.graph_objects as go  # type: ignore


def render_horizontal_bar(
    grouped: pd.DataFrame,
    label_col: str,
    value_col: str,
    usd_cad_rate,
    title: str,
    color_map: dict,
    chart_key: str,
    preserve_order: bool = False,
):
    """
    Shared horizontal-bar renderer used by every Portfolio Holdings
    breakdown chart (ETF category, Stock category, Stock-vs-ETF split,
    Purpose).

    Design notes:
    - Title renders via st.markdown ABOVE the chart, not as a Plotly
      figure title, so it never collides with bar-end annotations.
    - No legend — each bar already carries its category name on the
      y-axis.
    - Annotation is two lines: the top line shows the USD value + % of
      total, the bottom line shows the CAD-equivalent in parentheses.
      Two short lines avoid the "longest single-line label gets clipped"
      problem.
    - The x-axis range is padded ~45% past the largest bar so that even
      the dominant category's label (the one that previously got hidden
      when a single category was ~90% of the total) always has room to
      render, instead of the chart auto-scaling its range to exactly
      match the longest bar.
    - value_col is expected to already be CAD-normalized
      (market_value_cad) — that's what each bar's LENGTH represents, so
      percentages stay comparable across USD and CAD holdings regardless
      of original currency. usd_cad_rate is only used to compute the
      USD-equivalent text.
    - preserve_order=True skips the default ascending-by-value sort and
      plots `grouped` in the exact row order given (Plotly draws the
      first row at the bottom, the last row at the top) — used by the
      Single-Stock-vs-ETF chart to always pin "Single Stock" at the top.
    """
    st.markdown(
        f"<p style='font-size:18px; font-weight:600; margin-bottom:4px;'>{title}</p>",
        unsafe_allow_html=True,
    )

    if grouped.empty:
        st.info("No data with a CAD market value yet.")
        return

    total = grouped[value_col].sum()
    if not total:
        st.info("No data with a CAD market value yet.")
        return

    if not preserve_order:
        grouped = grouped.sort_values(value_col, ascending=True).reset_index(drop=True)

    labels = grouped[label_col].astype(str)
    cad_values = grouped[value_col]
    pct = (cad_values / total * 100).round(1)

    if usd_cad_rate:
        usd_values = cad_values / usd_cad_rate
        # USD first (top line) + percentage, CAD-equivalent below it.
        text_labels = [
            f"${usd:,.0f} USD — {p:.1f}%<br>(${cad:,.0f} CAD)"
            for cad, usd, p in zip(cad_values, usd_values, pct)
        ]
    else:
        text_labels = [
            f"${cad:,.0f} CAD — {p:.1f}%<br>(USD eq. unavailable)"
            for cad, p in zip(cad_values, pct)
        ]

    colors = [color_map.get(lbl, "#aab7b8") for lbl in labels]

    # Pad the x-axis range so even the largest bar's outside text has
    # room to render instead of getting clipped at the right edge.
    max_value = float(cad_values.max())
    x_range_max = max_value * 1.45 if max_value > 0 else 1

    fig = go.Figure(
        data=[
            go.Bar(
                x=cad_values,
                y=labels,
                orientation="h",
                marker_color=colors,
                text=text_labels,
                textposition="outside",
                textfont=dict(size=14),
            )
        ]
    )
    fig.update_layout(
        margin=dict(l=10, r=40, t=10, b=10),
        height=max(180, 90 * len(labels) + 60),
        xaxis=dict(
            title=dict(text="Market Value (CAD)", font=dict(size=16)),
            tickfont=dict(size=14),
            range=[0, x_range_max],
        ),
        yaxis=dict(tickfont=dict(size=18)),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, key=chart_key)
