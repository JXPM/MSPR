import plotly.graph_objects as go


def railway_map(df_gares, df_segments=None, show_segments=False):
    """
    df_gares   : DataFrame with columns [nom_gare, latitude, longitude]
    df_segments: DataFrame with columns [lat_depart, lon_depart, lat_arrivee, lon_arrivee]
                 Each row is a segment between two *consecutive* stations on a route.
                 These come from splitting itineraire.chemin → pairs of adjacent stations.
    """
    fig = go.Figure()

    # ── Railway segments (optional) ────────────────────────────
    if show_segments and df_segments is not None and not df_segments.empty:
        all_lats: list = []
        all_lons: list = []

        for _, row in df_segments.iterrows():
            try:
                all_lats.extend([float(row["lat_depart"]), float(row["lat_arrivee"]), None])
                all_lons.extend([float(row["lon_depart"]), float(row["lon_arrivee"]), None])
            except Exception:
                continue

        if all_lats:
            # Outer glow
            fig.add_trace(go.Scattermapbox(
                lat=all_lats,
                lon=all_lons,
                mode="lines",
                line=dict(width=3.2, color="rgba(16,185,129,0.14)"),
                hoverinfo="skip",
                showlegend=False,
            ))
            # Core line
            fig.add_trace(go.Scattermapbox(
                lat=all_lats,
                lon=all_lons,
                mode="lines",
                line=dict(width=1.2, color="rgba(110,255,210,0.34)"),
                hoverinfo="skip",
                showlegend=False,
            ))

    # ── Station glow — 3 layers ───────────────────────────────
    # Layer 1: wide soft halo
    fig.add_trace(go.Scattermapbox(
        lat=df_gares["latitude"],
        lon=df_gares["longitude"],
        mode="markers",
        marker=dict(size=10, color="rgba(80,255,180,0.08)"),
        hoverinfo="skip",
        showlegend=False,
    ))

    # Layer 2: mid glow
    fig.add_trace(go.Scattermapbox(
        lat=df_gares["latitude"],
        lon=df_gares["longitude"],
        mode="markers",
        marker=dict(size=5, color="rgba(100,255,190,0.28)"),
        hoverinfo="skip",
        showlegend=False,
    ))

    # Layer 3: bright core
    fig.add_trace(go.Scattermapbox(
        lat=df_gares["latitude"],
        lon=df_gares["longitude"],
        mode="markers",
        marker=dict(size=2.5, color="#d4fff0", opacity=1.0),
        text=df_gares["nom_gare"],
        hovertemplate="<b>%{text}</b><extra></extra>",
        showlegend=False,
    ))

    fig.update_layout(
        mapbox=dict(
            style="carto-darkmatter",
            zoom=3.2,
            center={"lat": 48.5, "lon": 10},
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=460,
        uirevision="map",
    )

    return fig