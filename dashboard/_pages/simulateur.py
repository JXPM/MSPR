# -*- coding: utf-8 -*-
"""Page Simulateur CO2 du tableau de bord ObRail Europe."""

from __future__ import annotations

import math

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.icons import lucide
from services.api_service import (
    get_operateurs,
    get_trajets_map,
    predict_full,
)

GREEN = "#174936"
ORANGE = "#c95f37"
RED = "#8d4040"
NAVY = "#1d2a53"

# Ratio CO2 train/avion moyen par cluster (profils KMeans du training notebook).
# Ordonne de facon monotone avec la distance / la severite des labels :
# cluster 0 (fort potentiel, trajets courts) = meilleur ratio (plus faible),
# cluster 2 (potentiel limite, trajets longs) = ratio le plus eleve.
# => l'economie CO2 affichee decroit bien de 0 vers 2 (97% > 89% > 86%).
_CLUSTER_RATIO_CO2 = {0: 0.03, 1: 0.11, 2: 0.14}
_CLUSTER_LABELS = {
    0: "Fort potentiel",
    1: "Potentiel modere",
    2: "Potentiel limite",
}
_CLUSTER_COLORS = {0: GREEN, 1: ORANGE, 2: RED}
_CLUSTER_NAMES = {
    0: "Fort potentiel (< 600 km)",
    1: "Potentiel modere (600-1100 km)",
    2: "Potentiel limite (> 1100 km)",
}

# Tranches de distance affichees sur la carte. Ce sont des ESTIMATIONS par
# distance (Haversine), volontairement distinctes du cluster KMeans renvoye par
# le modele dans la carte de resultat : on evite donc le terme "Cluster N" ici
# pour ne pas laisser croire qu'il s'agit du meme identifiant.
_FILTER_OPTIONS: dict[str, int | None] = {
    "Toutes les tranches": None,
    "Fort potentiel (< 600 km)": 0,
    "Potentiel modéré (600-1100 km)": 1,
    "Potentiel limité (> 1100 km)": 2,
}


@st.cache_data(ttl=300)
def _load_operateurs() -> list[str]:
    """Charge et trie la liste des operateurs depuis l'API.

    Lève une exception sur liste vide pour ne pas figer en cache un échec
    transitoire de l'API (cf. _load_segments_with_clusters).
    """
    data = get_operateurs()
    operateurs = sorted({op["operateur"] for op in data if op.get("operateur")})
    if not operateurs:
        raise RuntimeError("API /stats/operateurs indisponible ou vide")
    return operateurs


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcule la distance en km entre deux points GPS via la formule de Haversine."""
    R = 6371
    lat1, lon1, lat2, lon2 = (math.radians(x) for x in [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * R * math.asin(math.sqrt(max(0.0, a)))


def _estimate_cluster(distance_km: float) -> int:
    """Estime le cluster de substitution a partir de la distance du segment en km.

    Heuristique derivee des profils de clusters identifies par KMeans :
    - Cluster 0 (fort potentiel) : trajets courts, ratio CO2 train/avion tres faible.
    - Cluster 1 (potentiel modere) : trajets moyens.
    - Cluster 2 (potentiel limite) : trajets longs.
    """
    if distance_km < 600:
        return 0
    if distance_km < 1100:
        return 1
    return 2


@st.cache_data(ttl=3600)
def _load_segments_with_clusters() -> list[dict]:
    """Charge les segments de la carte et calcule le profil CO2 de chacun.

    Lève une exception si l'API ne renvoie rien : st.cache_data ne met pas en
    cache les exceptions, donc un échec transitoire (API down, timeout) n'est
    pas figé pour toute la durée du TTL et sera réessayé au prochain rendu.
    """
    segments = get_trajets_map()
    if not segments:
        raise RuntimeError("API /stats/trajets/map indisponible ou vide")
    result = []
    for seg in segments:
        try:
            dist = _haversine(
                seg["lat_depart"],
                seg["lon_depart"],
                seg["lat_arrivee"],
                seg["lon_arrivee"],
            )
            cluster = _estimate_cluster(dist)
            ratio = _CLUSTER_RATIO_CO2[cluster]
            empreinte_avion = round(dist * 0.158, 2)
            empreinte_train = round(empreinte_avion * ratio, 2)
            economie_pct = round((1 - ratio) * 100)
            result.append({
                **seg,
                "cluster": cluster,
                "distance_km": round(dist),
                "empreinte_train_kg": empreinte_train,
                "empreinte_avion_kg": empreinte_avion,
                "economie_pct": economie_pct,
                "label": _CLUSTER_LABELS[cluster],
            })
        except Exception:
            continue
    return result


def _cluster_map(segments: list[dict], height: int = 460) -> go.Figure:
    """Cree une carte Plotly avec les segments colores par cluster et tooltips au survol."""
    fig = go.Figure()

    for cluster_id, color in _CLUSTER_COLORS.items():
        name = _CLUSTER_NAMES[cluster_id]
        lats: list = []
        lons: list = []
        mid_lats: list = []
        mid_lons: list = []
        customdata_rows: list = []

        cluster_segs = [s for s in segments if s["cluster"] == cluster_id]
        for seg in cluster_segs:
            lats.extend([seg["lat_depart"], seg["lat_arrivee"], None])
            lons.extend([seg["lon_depart"], seg["lon_arrivee"], None])
            mid_lats.append((seg["lat_depart"] + seg["lat_arrivee"]) / 2)
            mid_lons.append((seg["lon_depart"] + seg["lon_arrivee"]) / 2)
            customdata_rows.append([
                seg.get("nom_depart", "?"),
                seg.get("nom_arrivee", "?"),
                seg.get("distance_km", 0),
                seg.get("empreinte_train_kg", 0.0),
                seg.get("empreinte_avion_kg", 0.0),
                seg.get("economie_pct", 0),
                seg.get("label", ""),
            ])

        if not lats:
            continue

        # Trace des lignes — pas de hover sur les lignes elles-memes
        fig.add_trace(
            go.Scattermapbox(
                lat=lats,
                lon=lons,
                mode="lines",
                line=dict(width=2.5, color=color),
                name=name,
                hoverinfo="skip",
                showlegend=True,
            )
        )

        # Points invisibles au milieu de chaque segment pour les tooltips
        if mid_lats:
            fig.add_trace(
                go.Scattermapbox(
                    lat=mid_lats,
                    lon=mid_lons,
                    mode="markers",
                    marker=dict(size=10, color=color, opacity=0.01),
                    customdata=customdata_rows,
                    hovertemplate=(
                        "<b>%{customdata[0]} → %{customdata[1]}</b><br>"
                        "Distance : %{customdata[2]} km<br>"
                        "CO₂ train estimé : %{customdata[3]} kg<br>"
                        "CO₂ avion équivalent : %{customdata[4]} kg<br>"
                        "Économie : %{customdata[5]}%<br>"
                        "Profil : %{customdata[6]}"
                        "<extra></extra>"
                    ),
                    showlegend=False,
                    name=name,
                )
            )

    fig.update_layout(
        mapbox=dict(
            style="carto-positron",
            zoom=3.3,
            center={"lat": 48.7, "lon": 9.5},
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        height=height,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=0.01,
            xanchor="right",
            x=0.99,
            bgcolor="rgba(255,255,255,0.88)",
            bordercolor="rgba(223,211,194,0.8)",
            borderwidth=1,
            font=dict(size=12),
        ),
        uirevision="cluster-map",
    )
    return fig


def _result_cards_html(result: dict) -> str:
    """Genere le HTML des cartes KPI de prediction CO2."""
    empreinte = result["empreinte_train_kg"]
    distance = result["distance_km"]
    empreinte_avion = distance * 0.158
    economie_pct = max(0.0, (1 - empreinte / empreinte_avion) * 100) if empreinte_avion > 0 else 0.0
    train_pct = min(100, round(empreinte / max(empreinte_avion, 0.001) * 100))

    zap_icon = lucide("zap", size=26, color="#f7efe4")
    leaf_icon = lucide("leaf", size=26, color="#f7efe4")

    return f"""
    <div class="kpi-row" style="grid-template-columns: repeat(3, minmax(0, 1fr)); margin-bottom:0.75rem;">
      <div class="kpi-card kpi-card--filled"
           style="background:{GREEN}; color:#f7efe4; border-color:transparent;">
        <div class="kpi-icon-clean" style="color:#f7efe4;">{zap_icon}</div>
        <div class="kpi-label" style="color:rgba(247,239,228,0.72);">Empreinte train</div>
        <div class="kpi-value" style="color:#f7efe4; font-size:2.4rem;">{empreinte:.2f}</div>
        <div class="kpi-hint" style="color:rgba(247,239,228,0.78);">kg CO2</div>
      </div>
      <div class="kpi-card kpi-card--filled"
           style="background:{NAVY}; color:#f7efe4; border-color:transparent;">
        <div class="kpi-icon-clean" style="color:rgba(247,239,228,0.5);">
          <svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 24 24"
               fill="none" stroke="currentColor" stroke-width="2"
               stroke-linecap="round" stroke-linejoin="round">
            <path d="M17.8 19.2 16 11l3.5-3.5C21 6 21 4 19 2c-2-2-4 0-5.5 1.5L10 7
                     1.8 8.8a.5.5 0 0 0-.3.8l1.5 1.5 2.4-.4 1.8 1.8-.4 2.4 1.5 1.5
                     a.5.5 0 0 0 .8-.3z"/>
          </svg>
        </div>
        <div class="kpi-label" style="color:rgba(247,239,228,0.72);">Equivalent avion</div>
        <div class="kpi-value" style="color:#f7efe4; font-size:2.4rem;">{empreinte_avion:.2f}</div>
        <div class="kpi-hint" style="color:rgba(247,239,228,0.78);">kg CO2 (facteur 0.158 kg/km)</div>
      </div>
      <div class="kpi-card kpi-card--filled"
           style="background:{ORANGE}; color:#f7efe4; border-color:transparent;">
        <div class="kpi-icon-clean" style="color:#f7efe4;">{leaf_icon}</div>
        <div class="kpi-label" style="color:rgba(247,239,228,0.72);">Economie CO2</div>
        <div class="kpi-value" style="color:#f7efe4; font-size:2.4rem;">{economie_pct:.0f}%</div>
        <div class="kpi-hint" style="color:rgba(247,239,228,0.78);">par rapport a l'avion</div>
      </div>
    </div>
    <div style="background:rgba(255,255,255,0.75); border:1px solid #dfd3c2;
                border-radius:16px; padding:1rem 1.2rem;">
      <div style="font-size:0.75rem; letter-spacing:0.3em; text-transform:uppercase;
                  color:#3d5a52; font-family:'IBM Plex Mono',monospace; margin-bottom:0.5rem;">
        Rapport CO2 train / avion
      </div>
      <div style="background:#e8e0d4; border-radius:999px; height:12px;
                  overflow:hidden; margin-bottom:0.4rem;">
        <div style="background:{GREEN}; border-radius:999px; height:100%;
                    width:{train_pct}%; transition:width 0.5s ease;"></div>
      </div>
      <div style="font-size:0.88rem; color:#3d5a52; line-height:1.5;">
        Le train emet <strong>{train_pct}%</strong> des emissions equivalentes
        de l'avion sur ce trajet de <strong>{distance:.0f} km</strong>.
      </div>
    </div>
    """


def _cluster_card_html(result: dict) -> str:
    """Genere le HTML de la carte de cluster de substitution."""
    cluster_id = result.get("cluster", -1)
    label = result.get("label", "Inconnu")
    description = result.get("description", "")

    colors = {0: GREEN, 1: ORANGE, 2: RED}
    bg = colors.get(cluster_id, NAVY)

    layers_icon = lucide("layers", size=20, color=bg)

    return f"""
    <div class="panel" style="background:rgba(255,255,255,0.75); margin-top:0.75rem;">
      <div class="section-title">
        <div style="display:flex; align-items:center; gap:0.5rem;">
          {layers_icon}
          <span class="section-title__label">Profil de substitution</span>
        </div>
        <div style="background:{bg}; color:#f7efe4; border-radius:999px;
                    padding:0.25rem 0.9rem; font-size:0.82rem; font-weight:600;
                    font-family:'IBM Plex Mono',monospace;">
          Cluster {cluster_id}
        </div>
      </div>
      <div style="font-family:'Cormorant Garamond',serif; font-size:1.85rem;
                  color:#143d35; margin-bottom:0.45rem; line-height:1.1;">
        {label}
      </div>
      <div style="color:#3d5a52; font-size:0.96rem; line-height:1.6;">
        {description}
      </div>
    </div>
    """


def _render_liaisons_table(segments: list[dict]) -> None:
    """Affiche le tableau des liaisons filtrees, triees par economie CO2 decroissante."""
    st.html("""
    <div class="section-title" style="margin-top:1.5rem; margin-bottom:0.5rem;">
      <span class="section-title__label">Liaisons prioritaires</span>
      <span class="section-title__meta" style="font-size:0.8rem;">
        Triees par economie CO2 decroissante &middot; estimation par Haversine
      </span>
    </div>
    """)

    if not segments:
        st.html("""
        <div class="panel" style="background:rgba(255,255,255,0.75);
                    text-align:center; color:#6d877f; padding:1.5rem;">
          Aucune liaison pour ce filtre.
        </div>
        """)
        return

    rows = []
    for seg in segments:
        rows.append({
            "Liaison": (
                f"{seg.get('nom_depart', '?')} → {seg.get('nom_arrivee', '?')}"
            ),
            "Distance (km)": seg.get("distance_km", 0),
            "CO2 train (kg)": seg.get("empreinte_train_kg", 0.0),
            "CO2 avion (kg)": seg.get("empreinte_avion_kg", 0.0),
            "Economie CO2 (%)": seg.get("economie_pct", 0),
            "Potentiel de substitution": seg.get("label", ""),
        })

    df = (
        pd.DataFrame(rows)
        .sort_values("Economie CO2 (%)", ascending=False)
        .reset_index(drop=True)
    )

    show_all = st.session_state.get("table_show_all", False)
    n_total = len(df)
    display_df = df if show_all else df.head(20)

    st.dataframe(
        display_df,
        use_container_width=True,
        column_config={
            "Distance (km)": st.column_config.NumberColumn(format="%d km"),
            "CO2 train (kg)": st.column_config.NumberColumn(format="%.2f kg"),
            "CO2 avion (kg)": st.column_config.NumberColumn(format="%.2f kg"),
            "Economie CO2 (%)": st.column_config.NumberColumn(
                "Economie CO2 (%)", format="%d%%"
            ),
        },
        hide_index=True,
    )

    if n_total > 20:
        if not show_all:
            if st.button(
                f"Voir plus ({n_total - 20} liaisons supplementaires)",
                key="table_voir_plus",
            ):
                st.session_state["table_show_all"] = True
                st.rerun()
        else:
            if st.button("Reduire le tableau", key="table_reduire"):
                st.session_state["table_show_all"] = False
                st.rerun()


def render() -> None:
    """Affiche la page Simulateur CO2 avec formulaire, carte des clusters et tableau."""

    st.html("""
    <div class="panel" style="background:rgba(255,255,255,0.75); margin-bottom:1.25rem;">
      <div class="section-title">
        <span class="section-title__label">Parametres du trajet</span>
        <span class="section-title__meta">Renseignez les caracteristiques du trajet</span>
      </div>
    </div>
    """)

    try:
        operateurs = _load_operateurs()
    except Exception:
        operateurs = []
    fallback_ops = ["OBB Nightjet", "SNCF", "Deutsche Bahn"] if not operateurs else operateurs

    col1, col2 = st.columns(2)
    with col1:
        operateur = st.selectbox(
            "Operateur ferroviaire",
            options=fallback_ops,
            index=0,
            help="Selectionnez l'operateur ferroviaire du trajet.",
        )
        type_service = st.radio(
            "Type de service",
            options=["JOUR", "NUIT"],
            index=1,
            horizontal=True,
            help="NUIT pour les trains de nuit (couchettes), JOUR pour les trains intercites.",
        )
    with col2:
        distance_km = st.slider(
            "Distance (km)",
            min_value=389,
            max_value=1847,
            value=800,
            step=10,
            help="Distance du trajet en kilometres.",
        )
        duree_trajet_min = st.slider(
            "Duree du trajet (minutes)",
            min_value=86,
            max_value=1362,
            value=480,
            step=10,
            help="Duree totale du trajet en minutes.",
        )

    calcul_btn = st.button(
        ":material/bolt: Calculer l'empreinte CO2",
        type="primary",
        use_container_width=True,
    )

    if calcul_btn:
        with st.spinner("Prediction en cours..."):
            result = predict_full(
                distance_km=float(distance_km),
                operateur=operateur,
                type_service=type_service,
                duree_trajet_min=float(duree_trajet_min),
            )
        st.session_state["simulateur_result"] = result

    if "simulateur_result" in st.session_state:
        result = st.session_state["simulateur_result"]
        if result:
            st.html(_result_cards_html(result))
            st.html(_cluster_card_html(result))
        else:
            st.html("""
            <div class="panel" style="background:rgba(255,255,255,0.75);
                        text-align:center; color:#6d877f; padding:2rem;">
              Service de prediction non disponible.<br>
              Verifiez que le backend est lance avec les modeles ML charges
              (<code>docker compose up</code>).
            </div>
            """)

    st.html("<div style='margin:2.5rem 0 0.25rem;'></div>")

    st.html("""
    <div class="section-title">
      <span class="section-title__label">Carte des liaisons par potentiel de substitution</span>
      <span class="section-title__meta" style="font-size:0.8rem;">
        Estimation par tranches de distance (Haversine) - distincte du cluster
        KMeans du modele affiche ci-dessus - segments issus de l'itineraire reel
      </span>
    </div>
    """)

    with st.spinner("Chargement de la carte..."):
        try:
            segments = _load_segments_with_clusters()
        except Exception:
            segments = []

    if not segments:
        st.html("""
        <div class="panel" style="background:rgba(255,255,255,0.75);
                    text-align:center; color:#6d877f; padding:3rem;">
          Segments non disponibles - verifiez que l'API est accessible.
        </div>
        """)
        return

    # Placeholder : la carte sera rendue ICI apres lecture du filtre
    map_placeholder = st.empty()

    # --- Filtre par cluster (sous la carte dans l'UI) ---
    st.html("""
    <div style="padding:0.7rem 0 0.2rem;">
      <div style="font-size:0.75rem; letter-spacing:0.3em; text-transform:uppercase;
                  color:#3d5a52; font-family:'IBM Plex Mono',monospace;">
        Filtrer par profil de substitution
      </div>
    </div>
    """)

    selected_filter = st.radio(
        "Filtrer par profil de substitution",
        options=list(_FILTER_OPTIONS.keys()),
        horizontal=True,
        label_visibility="collapsed",
        key="cluster_filter_radio",
    )
    cluster_filter = _FILTER_OPTIONS[selected_filter]

    # Reinitialise la pagination quand le filtre change
    if st.session_state.get("_prev_cluster_filter") != cluster_filter:
        st.session_state["table_show_all"] = False
        st.session_state["_prev_cluster_filter"] = cluster_filter

    filtered_segments = (
        segments if cluster_filter is None
        else [s for s in segments if s["cluster"] == cluster_filter]
    )

    # Remplit le placeholder avec la carte filtree
    with map_placeholder:
        st.plotly_chart(_cluster_map(filtered_segments), use_container_width=True)

    # --- Legende ---
    st.html(f"""
    <div style="display:flex; gap:1.5rem; align-items:center; margin-top:0.6rem;
                padding:0.85rem 1.1rem; background:rgba(255,255,255,0.72);
                border:1px solid #dfd3c2; border-radius:14px; flex-wrap:wrap;">
      <div style="display:flex; align-items:center; gap:0.5rem;">
        <div style="width:28px; height:4px; background:{GREEN}; border-radius:2px;"></div>
        <span style="font-size:0.84rem; color:#143d35;">
          <strong>Fort potentiel</strong> - &lt; 600 km
        </span>
      </div>
      <div style="display:flex; align-items:center; gap:0.5rem;">
        <div style="width:28px; height:4px; background:{ORANGE}; border-radius:2px;"></div>
        <span style="font-size:0.84rem; color:#143d35;">
          <strong>Potentiel modere</strong> - 600-1100 km
        </span>
      </div>
      <div style="display:flex; align-items:center; gap:0.5rem;">
        <div style="width:28px; height:4px; background:{RED}; border-radius:2px;"></div>
        <span style="font-size:0.84rem; color:#143d35;">
          <strong>Potentiel limite</strong> - &gt; 1100 km
        </span>
      </div>
    </div>
    """)

    # --- Tableau des liaisons prioritaires ---
    _render_liaisons_table(filtered_segments)
