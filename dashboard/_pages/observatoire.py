"""Maquette premium de la page Observatoire."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.charts import (
    co2_chart,
    operateurs_chart,
    pays_bar_chart,
    trajets_jour_nuit_chart,
)
from components.icons import lucide
from components.map import railway_map
from services.api_service import (
    get_emissions,
    get_gares,
    get_gares_count,
    get_lignes,
    get_lignes_count,
    get_operateurs,
    get_pays_count,
    get_trajets_count,
)


@st.cache_data(ttl=300)
def _load_stats() -> dict:
    return {
        "trajets": get_trajets_count().get("total_trajets", 0),
        "gares": get_gares_count().get("total_gares", 0),
        "lignes": get_lignes_count().get("total_lignes", 0),
        "pays": get_pays_count().get("total_pays", 0),
        "emissions": get_emissions() or {},
    }


@st.cache_data(ttl=300)
def _load_gares() -> pd.DataFrame:
    return pd.DataFrame(get_gares())


@st.cache_data(ttl=300)
def _load_lignes() -> pd.DataFrame:
    return pd.DataFrame(get_lignes())


@st.cache_data(ttl=300)
def _load_operateurs() -> list:
    return get_operateurs()


def _kpi(icon: str, color: str, label: str, value: str, hint: str) -> str:
    icon_svg = lucide(icon, size=28, color="currentColor", stroke_width=2)
    return f"""
    <div class="kpi-card kpi-card--filled" style="background:{color}; color:#f7efe4; border-color:transparent;">
      <div class="kpi-icon-clean" style="color:#f7efe4;">{icon_svg}</div>
      <div class="kpi-label" style="color:rgba(247,239,228,0.72);">{label}</div>
      <div class="kpi-value" style="color:#f7efe4;">{value}</div>
      <div class="kpi-hint" style="color:rgba(247,239,228,0.78);">{hint}</div>
    </div>
    """


def _metric_card(label: str, value: str, hint: str = "") -> str:
    hint_html = f'<div class="kpi-hint">{hint}</div>' if hint else ""
    return f"""
    <div class="kpi-card">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      {hint_html}
    </div>
    """


def render() -> None:
    stats = _load_stats()
    gares = _load_gares()
    lignes = _load_lignes()
    operateurs = _load_operateurs()

    if not lignes.empty and "type_service" in lignes.columns:
        type_counts = lignes["type_service"].astype(str).str.upper().value_counts()
        n_jour = int(type_counts.get("JOUR", 0))
        n_nuit = int(type_counts.get("NUIT", 0))
    else:
        n_jour = n_nuit = 0
    emissions = stats["emissions"]
    train_kg = round(float(emissions.get("train") or 0))
    avion_kg = round(float(emissions.get("avion") or 0))
    saved_kg = max(0, avion_kg - train_kg)
    saved_total = saved_kg * int(stats["trajets"])
    has_emissions = bool(emissions) and (train_kg > 0 or avion_kg > 0)
    saved_kg_display = f"{saved_kg:,} kg".replace(",", " ") if has_emissions else "—"
    saved_total_display = f"{saved_total:,} kg".replace(",", " ") if has_emissions else "—"
    saved_kg_hint = "Train contre scénario avion" if has_emissions else "Données émissions indisponibles"
    saved_total_hint = "Projection sur l'ensemble des trajets" if has_emissions else "Données émissions indisponibles"

    st.html(f"""
<div class="kpi-row">
  {_kpi("route", "#174936", "Trajets catalogués", f"{stats['trajets']:,}".replace(",", " "), "Dessertes suivies dans l'entrepôt")}
  {_kpi("landmark", "#1d2a53", "Gares documentées", f"{stats['gares']:,}".replace(",", " "), "Noms, pays et géolocalisation")}
  {_kpi("git-fork", "#245845", "Lignes actives", f"{stats['lignes']:,}".replace(",", " "), "Jour, nuit et longue distance")}
  {_kpi("globe", "#a15e3f", "Pays couverts", f"{stats['pays']:,}".replace(",", " "), "Empreinte réseau européenne")}
</div>
""")

    col_map, col_stats = st.columns([1.45, 1], gap="large")
    with col_map:
        st.markdown(
            '<div class="section-title"><div class="section-title__label">Réseau ferroviaire</div><div class="section-title__meta">Gares géolocalisées</div></div>',
            unsafe_allow_html=True,
        )
        map_df = gares.dropna(subset=["latitude", "longitude"]) if {"latitude", "longitude"}.issubset(gares.columns) else pd.DataFrame()
        if len(map_df) > 2500:
            map_df = map_df.sample(2500, random_state=42)
        st.plotly_chart(
            railway_map(map_df, show_segments=False, height=540),
            width="stretch",
            config={"displayModeBar": False, "scrollZoom": True},
        )

    with col_stats:
        st.markdown(
            '<div class="section-title"><div class="section-title__label">Lecture rapide</div><div class="section-title__meta">Structure et usage</div></div>',
            unsafe_allow_html=True,
        )
        st.html(
            _metric_card("Lignes de jour", f"{n_jour:,}".replace(",", " "), "Mobilité diurne du réseau")
            + _metric_card("Lignes de nuit", f"{n_nuit:,}".replace(",", " "), "Connectivité longue distance")
            + _metric_card("CO₂ économisé / trajet", saved_kg_display, saved_kg_hint)
            + _metric_card("CO₂ total évité", saved_total_display, saved_total_hint)
        )

    col_a, col_b = st.columns([1, 1], gap="large")
    with col_a:
        st.markdown(
            '<div class="section-title"><div class="section-title__label">Mix de service</div><div class="section-title__meta">Lignes jour contre nuit</div></div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            trajets_jour_nuit_chart(n_jour, n_nuit, unit_label="LIGNES"),
            width="stretch",
            config={"displayModeBar": False},
        )

    with col_b:
        st.markdown(
            '<div class="section-title"><div class="section-title__label">Empreinte géographique</div><div class="section-title__meta">Top pays par gares</div></div>',
            unsafe_allow_html=True,
        )
        if "iso_pays" in gares.columns:
            country_counts = gares["iso_pays"].value_counts().head(12)
            st.plotly_chart(
                pays_bar_chart(country_counts),
                width="stretch",
                config={"displayModeBar": False},
            )
        else:
            st.info("La ventilation par pays n'est pas disponible.")

    col_c, col_d = st.columns([1.2, 1], gap="large")
    with col_c:
        st.markdown(
            '<div class="section-title"><div class="section-title__label">Opérateurs</div><div class="section-title__meta">Volumes recensés</div></div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            operateurs_chart(operateurs),
            width="stretch",
            config={"displayModeBar": False},
        )

    with col_d:
        st.markdown(
            '<div class="section-title"><div class="section-title__label">Impact CO₂</div><div class="section-title__meta">Moyenne par trajet</div></div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            co2_chart(emissions),
            width="stretch",
            config={"displayModeBar": False},
        )

    st.markdown(
        '<div class="section-title" style="margin-top:0.6rem;"><div class="section-title__label">Économies par opérateur</div><div class="section-title__meta">Scénario train contre tout avion</div></div>',
        unsafe_allow_html=True,
    )
    if operateurs:
        ops_df = pd.DataFrame(operateurs).sort_values("trajets", ascending=False).head(8).copy()
        ops_df["saved"] = ops_df["trajets"] * saved_kg
        fig = go.Figure(
            go.Bar(
                x=ops_df["operateur"],
                y=ops_df["saved"],
                marker=dict(
                    color=ops_df["saved"],
                    colorscale=[[0, "#dbe7e0"], [0.45, "#5aa17e"], [1, "#0e7a50"]],
                    showscale=False,
                    line=dict(color="rgba(15,27,45,0.05)", width=1),
                ),
                text=[f"{value/1000:.0f} t" for value in ops_df["saved"]],
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>%{y:,.0f} kg CO₂ évités<extra></extra>",
            )
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=70),
            height=340,
            font=dict(family="Inter, sans-serif", color="#5a6b7e"),
            xaxis=dict(showgrid=False, tickangle=-22, color="#0f1b2d"),
            yaxis=dict(showgrid=True, gridcolor="rgba(15,27,45,0.08)", showticklabels=False, zeroline=False),
        )
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    else:
        st.info("La répartition par opérateur est indisponible.")
