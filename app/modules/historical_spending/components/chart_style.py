import math

import plotly.graph_objects as go  # type: ignore


CHART_BG = "#0e1117"
CHART_TEXT = "#f4f6f8"
CHART_GRID = "#30363d"
CHART_AXIS = "#8b949e"
CHART_HEIGHT = 700
LEGEND_FONT_SIZE = 15
AXIS_FONT_SIZE = 15


def apply_plotly_chart_style(fig, *, top_margin=20, bottom_margin=20, show_legend=True):
    fig.update_layout(
        height=CHART_HEIGHT,
        paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG,
        font=dict(color=CHART_TEXT, size=AXIS_FONT_SIZE),
        margin=dict(l=20, r=20, t=top_margin, b=bottom_margin),
        xaxis=dict(
            color=CHART_TEXT,
            gridcolor=CHART_GRID,
            zerolinecolor=CHART_GRID,
            linecolor=CHART_AXIS,
            tickfont=dict(size=AXIS_FONT_SIZE),
            title_font=dict(size=AXIS_FONT_SIZE + 1),
        ),
        yaxis=dict(
            color=CHART_TEXT,
            gridcolor=CHART_GRID,
            zerolinecolor=CHART_GRID,
            linecolor=CHART_AXIS,
            tickfont=dict(size=AXIS_FONT_SIZE),
            title_font=dict(size=AXIS_FONT_SIZE + 1),
        ),
    )
    if show_legend:
        fig.update_layout(
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0,
                font=dict(size=LEGEND_FONT_SIZE, color=CHART_TEXT),
            )
        )


def house_percentage_table(values, labels):
    return go.Table(
        header=dict(
            values=["House %"] + labels,
            fill_color="#161b22",
            line_color=CHART_GRID,
            font=dict(color=CHART_TEXT, size=13),
            align="center",
            height=28,
        ),
        cells=dict(
            values=[["%"]] + [[f"{value:.1f}%"] for value in values],
            fill_color=CHART_BG,
            line_color=CHART_GRID,
            font=dict(color=CHART_TEXT, size=13),
            align="center",
            height=28,
        ),
    )


def nice_percentage_ticks(max_value):
    if max_value is None or math.isnan(max_value) or max_value <= 0:
        max_value = 10
    upper = int(math.ceil(max_value)) + 5
    if upper <= 10:
        return list(range(0, upper + 1))
    return list(range(0, 11)) + list(range(15, upper + 1, 5))
