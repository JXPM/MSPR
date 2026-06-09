"""Carte du reseau ferroviaire pour la maquette ObRail."""

from __future__ import annotations

import plotly.graph_objects as go


GREEN = "#0e7a50"
NAVY = "#2d4a8a"
ACCENT = "#c2683a"
CREAM = "#ffffff"
TEXT = "#0f1b2d"


def railway_map(df_gares, df_segments=None, show_segments: bool = False, height: int = 460):
    fig = go.Figure()

    if show_segments and df_segments is not None and not df_segments.empty:
        latitudes = []
        longitudes = []
        for _, row in df_segments.iterrows():
            try:
                latitudes.extend([float(row["lat_depart"]), float(row["lat_arrivee"]), None])
                longitudes.extend([float(row["lon_depart"]), float(row["lon_arrivee"]), None])
            except Exception:
                continue
        if latitudes:
            fig.add_trace(
                go.Scattermapbox(
                    lat=latitudes,
                    lon=longitudes,
                    mode="lines",
                    line=dict(width=3.2, color="rgba(29,42,83,0.12)"),
                    hoverinfo="skip",
                    showlegend=False,
                )
            )
            fig.add_trace(
                go.Scattermapbox(
                    lat=latitudes,
                    lon=longitudes,
                    mode="lines",
                    line=dict(width=1.15, color="rgba(23,73,54,0.44)"),
                    hoverinfo="skip",
                    showlegend=False,
                )
            )

    if df_gares is not None and not df_gares.empty:
        fig.add_trace(
            go.Scattermapbox(
                lat=df_gares["latitude"],
                lon=df_gares["longitude"],
                mode="markers",
                marker=dict(size=18, color="rgba(14,122,80,0.14)"),
                hoverinfo="skip",
                showlegend=False,
            )
        )
        fig.add_trace(
            go.Scattermapbox(
                lat=df_gares["latitude"],
                lon=df_gares["longitude"],
                mode="markers",
                marker=dict(size=6, color=GREEN, opacity=0.95),
                text=df_gares["nom_gare"] if "nom_gare" in df_gares.columns else None,
                hovertemplate="<b>%{text}</b><extra></extra>",
                showlegend=False,
            )
        )

    fig.update_layout(
        mapbox=dict(
            style="carto-positron",
            zoom=3.35,
            center={"lat": 48.7, "lon": 9.5},
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=CREAM,
        height=height,
        uirevision="map",
    )
    return fig
