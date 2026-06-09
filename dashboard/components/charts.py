"""Graphiques Plotly harmonises avec la maquette ObRail."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go


GREEN = "#0e7a50"
GREEN_2 = "#0b6442"
NAVY = "#2d4a8a"
ACCENT = "#c2683a"
TEXT = "#0f1b2d"
MUTED = "#5a6b7e"
GRID = "rgba(15,27,45,0.08)"
CREAM = "#ffffff"
OK = "#0e7a50"
DANGER = "#c0392b"

FONT_BODY = "Inter, sans-serif"
FONT_SERIF = "Cormorant Garamond, serif"
FONT_MONO = "IBM Plex Mono, monospace"


def _base_layout(height: int = 300, **overrides) -> dict:
    layout = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT_BODY, color=MUTED, size=12),
        margin=dict(l=10, r=10, t=12, b=12),
        height=height,
    )
    layout.update(overrides)
    return layout


def trajets_jour_nuit_chart(jour: int = 0, nuit: int = 0, unit_label: str = "TRAJETS") -> go.Figure:
    total = jour + nuit
    fig = go.Figure(
        go.Pie(
            labels=["Jour", "Nuit"],
            values=[jour, nuit],
            hole=0.68,
            marker=dict(colors=[GREEN, NAVY], line=dict(color=CREAM, width=4)),
            textinfo="percent",
            textfont=dict(size=13, color=CREAM, family=FONT_MONO),
            hovertemplate=f"<b>%{{label}}</b><br>%{{value:,}} {unit_label.lower()}<extra></extra>",
        )
    )
    fig.update_layout(
        **_base_layout(height=320),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.08,
            xanchor="center",
            x=0.5,
            font=dict(size=12, color=TEXT),
        ),
        annotations=[
            dict(
                x=0.5,
                y=0.52,
                showarrow=False,
                text=(
                    f"<span style='font-family:{FONT_SERIF};font-size:34px;color:{TEXT};'>{total:,}</span>"
                    f"<br><span style='font-family:{FONT_MONO};font-size:11px;letter-spacing:.18em;color:{MUTED};'>{unit_label}</span>"
                ),
            )
        ],
    )
    return fig


def co2_chart(data: dict) -> go.Figure:
    train = round(float(data.get("train") or 0))
    avion = round(float(data.get("avion") or 0))
    saved = max(0, avion - train)
    ratio = round(avion / train, 1) if train else 0

    fig = go.Figure(
        go.Bar(
            x=["Train", "Avion"],
            y=[train, avion],
            marker=dict(color=[GREEN, ACCENT], line=dict(color="rgba(15,27,45,0.06)", width=1.2)),
            text=[f"{train:,} kg", f"{avion:,} kg"],
            textposition="outside",
            textfont=dict(family=FONT_MONO, color=TEXT, size=12),
            hovertemplate="<b>%{x}</b><br>%{y:,} kg CO₂<extra></extra>",
        )
    )
    fig.update_layout(
        **_base_layout(height=320),
        xaxis=dict(showgrid=False, zeroline=False, color=TEXT),
        yaxis=dict(showgrid=True, gridcolor=GRID, showticklabels=False, zeroline=False),
        annotations=[
            dict(
                x=0.5,
                y=-0.17,
                xref="paper",
                yref="paper",
                showarrow=False,
                text=f"<span style='color:{GREEN};'><b>−{saved:,} kg</b></span> <span style='color:{MUTED};'>soit {ratio}x moins en train</span>",
            )
        ],
    )
    return fig


def operateurs_chart(data: list) -> go.Figure:
    if not data:
        fig = go.Figure()
        fig.update_layout(**_base_layout(height=240))
        return fig

    df = pd.DataFrame(data).sort_values("trajets", ascending=True)
    fig = go.Figure(
        go.Bar(
            x=df["trajets"],
            y=df["operateur"],
            orientation="h",
            marker=dict(
                color=df["trajets"],
                colorscale=[[0, "#dbe7e0"], [0.45, "#5aa17e"], [1, GREEN]],
                showscale=False,
                line=dict(color="rgba(15,27,45,0.05)", width=1),
            ),
            text=[f"{value:,}" for value in df["trajets"]],
            textposition="outside",
            textfont=dict(family=FONT_MONO, color=TEXT, size=11),
            hovertemplate="<b>%{y}</b><br>%{x:,.0f} trajets<extra></extra>",
        )
    )
    fig.update_layout(
        **_base_layout(height=max(260, len(df) * 36)),
        xaxis=dict(showgrid=True, gridcolor=GRID, zeroline=False, color=MUTED),
        yaxis=dict(showgrid=False, zeroline=False, color=TEXT),
    )
    return fig


def pays_bar_chart(counts: pd.Series) -> go.Figure:
    fig = go.Figure(
        go.Bar(
            x=counts.index,
            y=counts.values,
            marker=dict(
                color=counts.values,
                colorscale=[[0, "#dde3ef"], [0.5, "#7d97c8"], [1, NAVY]],
                showscale=False,
                line=dict(color="rgba(15,27,45,0.05)", width=1),
            ),
            hovertemplate="<b>%{x}</b><br>%{y:,} gares<extra></extra>",
        )
    )
    fig.update_layout(
        **_base_layout(height=320),
        xaxis=dict(showgrid=False, zeroline=False, color=TEXT),
        yaxis=dict(showgrid=True, gridcolor=GRID, zeroline=False, color=MUTED),
    )
    return fig


def latency_chart(history: list[dict]) -> go.Figure:
    if not history:
        fig = go.Figure()
        fig.update_layout(**_base_layout(height=260))
        return fig

    df = pd.DataFrame(history)
    marker_colors = [OK if ok else DANGER for ok in df["ok"]]
    average = df["latency_ms"].mean()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["ts"],
            y=df["latency_ms"],
            mode="lines",
            line=dict(color=GREEN, width=3, shape="spline", smoothing=0.45),
            fill="tozeroy",
            fillcolor="rgba(14,122,80,0.08)",
            hoverinfo="skip",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["ts"],
            y=df["latency_ms"],
            mode="markers",
            marker=dict(color=marker_colors, size=8, line=dict(color=CREAM, width=1.2)),
            hovertemplate="<b>%{x|%H:%M:%S}</b><br>%{y:.0f} ms<extra></extra>",
            showlegend=False,
        )
    )
    fig.add_hline(y=average, line_dash="dot", line_color="#b6c7c1", line_width=1.5)
    fig.update_layout(
        **_base_layout(height=300),
        xaxis=dict(showgrid=False, zeroline=False, tickformat="%H:%M:%S", color=MUTED),
        yaxis=dict(showgrid=True, gridcolor=GRID, zeroline=False, title=None, color=MUTED),
    )
    return fig
