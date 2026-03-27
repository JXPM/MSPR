import plotly.graph_objects as go
import pandas as pd


def trajets_jour_nuit_chart(jour: int = 0, nuit: int = 0):
    total = jour + nuit or 1
    pct_jour = round(jour / total * 100, 1)
    pct_nuit = round(nuit / total * 100, 1)

    fig = go.Figure(go.Pie(
        labels=["Trajets jour", "Trajets nuit"],
        values=[jour, nuit],
        hole=0.0,
        marker=dict(
            colors=["#10b981", "#3b82f6"],
            line=dict(color="#080c14", width=2),
        ),
        textinfo="value+percent",
        textfont=dict(size=13, color="white", family="DM Mono, monospace"),
        hovertemplate="<b>%{label}</b><br>%{value:,} trajets — %{percent}<extra></extra>",
        pull=[0.03, 0],
        textposition="inside",
        insidetextorientation="radial",
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#8492a6"),
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.06,
            xanchor="center", x=0.5,
            font=dict(size=12, color="#8492a6"),
            bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(l=10, r=10, t=10, b=30),
        height=300,
    )
    return fig


def co2_chart(data: dict):
    train_val = round(float(data.get("train") or 0))
    avion_val = round(float(data.get("avion") or 0))

    train_kg = 8
    avion_kg = 54
    saved = max(0, avion_val - train_val)
    ratio = round(avion_val / train_val, 1) if train_val > 0 else 0

    ymax = max(train_val, avion_val, 1)
    top = ymax * 1.22
    bottom_band = ymax * 0.70

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=["Trains", "Avions"],
        y=[train_val, avion_val],
        marker=dict(
            color=["#10b981", "#f59e0b"],
            line_width=0,
        ),
        width=[0.42, 0.42],
        text=[f"{train_val:,}", f"{avion_val:,}"],
        textposition="outside",
        textfont=dict(size=20, color=["#6ee7b7", "#fbbf24"], family="DM Mono, monospace"),
        hovertemplate="<b>%{x}</b><br>%{y:,} tonnes CO₂<extra></extra>",
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#8492a6"),
        title=dict(
            text="Émissions CO₂ : Trains vs Avions",
            font=dict(size=13, color="#c8d3e8"),
            x=0,
            xanchor="left",
            pad=dict(l=2),
        ),
        showlegend=False,
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            tickfont=dict(size=14, color="#c8d3e8"),
            fixedrange=True,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.04)",
            zeroline=False,
            showticklabels=False,
            range=[-bottom_band, top],
            fixedrange=True,
        ),
        margin=dict(l=10, r=10, t=40, b=12),
        height=360,
        annotations=[
            # Ligne 1: tonnage sous chaque barre
            dict(x="Trains", y=-(bottom_band * 0.18), text=f"<b>{train_val:,}</b> tonnes", showarrow=False, font=dict(size=20, color="#f0f4ff", family="DM Sans, sans-serif"), xanchor="center"),
            dict(x="Avions", y=-(bottom_band * 0.18), text=f"<b>{avion_val:,}</b> tonnes", showarrow=False, font=dict(size=20, color="#f0f4ff", family="DM Sans, sans-serif"), xanchor="center"),
            # Ligne 2: facteurs sous chaque barre
            dict(x="Trains", y=-(bottom_band * 0.42), text=f"<span style='color:#60a5fa'><b>{train_kg} Kg CO₂</b></span> par 100 km", showarrow=False, font=dict(size=12, color="#9fb0c8", family="DM Sans, sans-serif"), xanchor="center"),
            dict(x="Avions", y=-(bottom_band * 0.42), text=f"<span style='color:#9ca3af'><b>{avion_kg} Kg CO₂</b></span> par 100 km", showarrow=False, font=dict(size=12, color="#9fb0c8", family="DM Sans, sans-serif"), xanchor="center"),
            # Ligne 3: économie globale
            dict(xref="paper", yref="y", x=0.50, y=-(bottom_band * 0.66), text=f"<span style='color:#10b981'><b>Train CO₂ Saved</b> ✓ {saved:,} tonnes ({ratio}× moins polluant)</span>", showarrow=False, font=dict(size=13, color="#10b981", family="DM Sans, sans-serif"), xanchor="center"),
        ],
    )
    return fig


def operateurs_chart(data: list):
    if not data:
        fig = go.Figure()
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=220,
        )
        return fig

    df = pd.DataFrame(data).sort_values("trajets", ascending=True).tail(8)

    fig = go.Figure(go.Bar(
        x=df["trajets"],
        y=df["operateur"],
        orientation="h",
        marker=dict(
            color=df["trajets"],
            colorscale=[[0, "#0ea5e9"], [0.5, "#0d9488"], [1, "#10b981"]],
            showscale=False,
            line_width=0,
            cornerradius=3,
        ),
        hovertemplate="<b>%{y}</b><br>%{x:,.0f} trajets<extra></extra>",
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#8492a6"),
        title=dict(
            text="Volume de Données par Opérateur",
            font=dict(size=12, color="#c8d3e8"),
            x=0, xanchor="left", pad=dict(l=2),
        ),
        showlegend=False,
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.04)",
            zeroline=False,
            tickfont=dict(size=9, color="#4b5875"),
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            tickfont=dict(size=11, color="#c8d3e8"),
        ),
        margin=dict(l=10, r=16, t=36, b=10),
        height=220,
    )
    return fig
