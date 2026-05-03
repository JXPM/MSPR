"""Maquette premium de la page Trajets."""

from __future__ import annotations

import math
import unicodedata

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def _fix_mojibake(value: str) -> str:
    if not isinstance(value, str) or not value:
        return value
    try:
        return value.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return value


def _normalize_name(value: str) -> str:
    if not isinstance(value, str) or not value:
        return ""
    cleaned = _fix_mojibake(value)
    decomposed = unicodedata.normalize("NFKD", cleaned)
    ascii_only = "".join(c for c in decomposed if not unicodedata.combining(c))
    return ascii_only.casefold().strip()

from components.icons import lucide
from services.api_service import (
    get_gares,
    get_lignes,
    get_operateurs,
    get_trajet_itineraire,
    get_trajets,
)


@st.cache_data(ttl=300)
def _load_trajets() -> pd.DataFrame:
    return pd.DataFrame(get_trajets())


@st.cache_data(ttl=300)
def _load_gares() -> pd.DataFrame:
    return pd.DataFrame(get_gares())


@st.cache_data(ttl=300)
def _load_lignes() -> pd.DataFrame:
    return pd.DataFrame(get_lignes())


@st.cache_data(ttl=300)
def _load_operateurs() -> list:
    return get_operateurs()


@st.cache_data(ttl=300)
def _load_itineraire(trajet_id: str) -> list:
    return get_trajet_itineraire(trajet_id)


def _fmt_int(value: int) -> str:
    return f"{int(value):,}".replace(",", " ")


def _safe_text(value, fallback: str = "Non renseigne") -> str:
    if value is None:
        return fallback
    if isinstance(value, float) and math.isnan(value):
        return fallback
    text = str(value).strip()
    return text if text else fallback


def _format_time(value, fallback: str = "--:--") -> str:
    """Extrait HH:MM d'une valeur datetime/ISO/string."""
    if value is None:
        return fallback
    if isinstance(value, float) and math.isnan(value):
        return fallback
    try:
        ts = pd.to_datetime(value, errors="coerce")
        if pd.isna(ts):
            text = str(value).strip()
            if "T" in text:
                return text.split("T", 1)[1][:5] or fallback
            return text[:5] if text else fallback
        return ts.strftime("%H:%M")
    except Exception:
        return fallback


def _compute_duration(depart, arrivee) -> str:
    """Calcule la durée entre deux heures (gère le passage minuit)."""
    try:
        d = pd.to_datetime(depart, errors="coerce")
        a = pd.to_datetime(arrivee, errors="coerce")
        if pd.isna(d) or pd.isna(a):
            return "Non calculee"
        secs = int((a - d).total_seconds())
        if secs < 0:
            secs += 24 * 3600
        h, rem = divmod(secs, 3600)
        m = rem // 60
        return f"{h}h{m:02d}"
    except Exception:
        return "Non calculee"


def _service_badge(value: str) -> str:
    if value and "NUIT" in value.upper():
        return "Nuit"
    if value:
        return value.title()
    return "Service"


def _duration_from_row(row: pd.Series) -> str:
    for key in ["duree", "duration", "temps_trajet"]:
        if key in row and pd.notna(row[key]):
            return str(row[key])
    return _compute_duration(row.get("heure_depart"), row.get("heure_arrivee"))


def _format_distance(value) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return ""
    try:
        km = float(value)
        if km <= 0:
            return ""
        return f"{int(round(km))} km"
    except (TypeError, ValueError):
        return ""


def _trip_card(row: pd.Series) -> str:
    distance_str = _format_distance(row.get("distance"))
    distance_html = f'<div class="trip-card__distance">{distance_str}</div>' if distance_str else ""
    return f"""
    <article class="trip-card">
      <div class="trip-card__top">
        <div class="trip-card__id">{_safe_text(row.get('code_operateur'), 'ATC')} · {_safe_text(row.get('trajet_id'), 'Trajet')}</div>
        <div class="trip-card__badge">{_service_badge(_safe_text(row.get('type_service'), 'Service'))}</div>
      </div>
      <div class="trip-card__line">
        <div>
          <div class="trip-card__time">{_format_time(row.get('heure_depart'))}</div>
          <div class="trip-card__station">{_safe_text(row.get('gare_depart'), 'Depart')}</div>
        </div>
        <div class="trip-card__duration">{_duration_from_row(row)}</div>
        <div style="text-align:right;">
          <div class="trip-card__time">{_format_time(row.get('heure_arrivee'))}</div>
          <div class="trip-card__station">{_safe_text(row.get('gare_arrivee'), 'Arrivee')}</div>
        </div>
      </div>
      <div class="trip-card__footer trip-card__footer--with-cta">
        <div class="trip-card__footer-left">
          <span>Ligne</span>
          <strong>{_safe_text(row.get('nom_ligne'), 'Non renseignee')}</strong>
          {distance_html}
        </div>
      </div>
    </article>
    """


@st.cache_data(ttl=300)
def _gare_index(df_gares: pd.DataFrame) -> dict:
    """Construit un index normalisé sur les noms de gares (gestion mojibake)."""
    if df_gares is None or df_gares.empty or "nom_gare" not in df_gares.columns:
        return {}
    index = {}
    for _, row in df_gares.iterrows():
        key = _normalize_name(row.get("nom_gare"))
        if key and key not in index:
            index[key] = {
                "code_uic": row.get("code_uic"),
                "iso_pays": row.get("iso_pays"),
                "latitude": row.get("latitude"),
                "longitude": row.get("longitude"),
                "nom_gare_clean": _fix_mojibake(row.get("nom_gare")),
            }
    return index


def _gare_lookup(df_gares: pd.DataFrame, nom_gare: str) -> dict:
    """Retourne (code_uic, iso_pays, latitude, longitude) pour une gare,
    avec normalisation des noms pour gérer les variantes d'encodage."""
    if not nom_gare:
        return {}
    index = _gare_index(df_gares)
    return index.get(_normalize_name(nom_gare), {})


def _route_map(stops: list) -> go.Figure:
    """Construit une carte Plotly traçant l'itinéraire complet entre toutes les gares."""
    fig = go.Figure()

    valid = [
        s for s in stops
        if s.get("latitude") is not None and s.get("longitude") is not None
        and not pd.isna(s.get("latitude")) and not pd.isna(s.get("longitude"))
    ]

    if not valid:
        fig.update_layout(
            mapbox=dict(style="carto-positron", zoom=3.5, center={"lat": 48.7, "lon": 9.5}),
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            height=360,
        )
        return fig

    lats = [float(s["latitude"]) for s in valid]
    lons = [float(s["longitude"]) for s in valid]

    if len(valid) >= 2:
        fig.add_trace(
            go.Scattermapbox(
                lat=lats,
                lon=lons,
                mode="lines",
                line=dict(width=4, color="rgba(234,125,87,0.85)"),
                hoverinfo="skip",
                showlegend=False,
            )
        )

    intermediate_lats, intermediate_lons, intermediate_text = [], [], []
    endpoint_lats, endpoint_lons, endpoint_text = [], [], []
    last_idx = len(valid) - 1
    for idx, stop in enumerate(valid):
        label = _safe_text(stop.get("nom_gare"), "Gare")
        if idx == 0:
            endpoint_lats.append(float(stop["latitude"]))
            endpoint_lons.append(float(stop["longitude"]))
            endpoint_text.append(f"Depart · {label}")
        elif idx == last_idx:
            endpoint_lats.append(float(stop["latitude"]))
            endpoint_lons.append(float(stop["longitude"]))
            endpoint_text.append(f"Arrivee · {label}")
        else:
            intermediate_lats.append(float(stop["latitude"]))
            intermediate_lons.append(float(stop["longitude"]))
            intermediate_text.append(f"Arret · {label}")

    if intermediate_lats:
        fig.add_trace(
            go.Scattermapbox(
                lat=intermediate_lats,
                lon=intermediate_lons,
                mode="markers",
                marker=dict(size=10, color="#ea7d57"),
                text=intermediate_text,
                hovertemplate="<b>%{text}</b><extra></extra>",
                showlegend=False,
            )
        )

    if endpoint_lats:
        fig.add_trace(
            go.Scattermapbox(
                lat=endpoint_lats,
                lon=endpoint_lons,
                mode="markers",
                marker=dict(size=15, color="#174936"),
                text=endpoint_text,
                hovertemplate="<b>%{text}</b><extra></extra>",
                showlegend=False,
            )
        )

    center_lat = (max(lats) + min(lats)) / 2
    center_lon = (max(lons) + min(lons)) / 2
    span = max(max(lats) - min(lats), max(lons) - min(lons))
    if span < 1:
        zoom = 7.5
    elif span < 3:
        zoom = 6.3
    elif span < 6:
        zoom = 5.4
    elif span < 10:
        zoom = 4.7
    else:
        zoom = 3.8

    fig.update_layout(
        mapbox=dict(
            style="carto-positron",
            zoom=zoom,
            center={"lat": center_lat, "lon": center_lon},
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        height=400,
    )
    return fig


@st.dialog("Detail du trajet", width="large")
def _trip_dialog(trip: dict, depart: dict, arrivee: dict) -> None:
    row = pd.Series(trip)
    trajet_id = _safe_text(row.get("trajet_id"), "")

    raw_stops = _load_itineraire(trajet_id) if trajet_id else []

    stops = []
    prev_uic = None
    prev_name = None
    for stop in raw_stops:
        uic = stop.get("code_uic")
        name = stop.get("nom_gare")
        if (uic is not None and uic == prev_uic) or (uic is None and name == prev_name):
            continue
        stops.append(stop)
        prev_uic = uic
        prev_name = name

    if not stops:
        # Fallback : reconstruire un itinéraire minimal a partir des deux extremites
        stops = [
            {
                "id_itineraire": 0,
                "code_uic": depart.get("code_uic"),
                "nom_gare": row.get("gare_depart"),
                "iso_pays": depart.get("iso_pays"),
                "latitude": depart.get("latitude"),
                "longitude": depart.get("longitude"),
                "chemin": None,
            },
            {
                "id_itineraire": 1,
                "code_uic": arrivee.get("code_uic"),
                "nom_gare": row.get("gare_arrivee"),
                "iso_pays": arrivee.get("iso_pays"),
                "latitude": arrivee.get("latitude"),
                "longitude": arrivee.get("longitude"),
                "chemin": None,
            },
        ]

    st.html(f"""
<div class="dialog-header">
  <div class="dialog-header__id">{_safe_text(row.get('code_operateur'), 'ATC')} · {_safe_text(row.get('trajet_id'), 'Trajet')}</div>
  <div class="dialog-header__badge">{_service_badge(_safe_text(row.get('type_service'), 'Service'))}</div>
</div>
""")

    nb_arrets = max(len(stops) - 2, 0)
    arrets_label = f"{nb_arrets} arret{'s' if nb_arrets > 1 else ''} intermediaire{'s' if nb_arrets > 1 else ''}" if nb_arrets > 0 else "Sans arret intermediaire"

    st.html(f"""
<div class="dialog-route">
  <div class="dialog-route__col">
    <div class="dialog-route__meta">Depart</div>
    <div class="dialog-route__time">{_format_time(row.get('heure_depart'))}</div>
    <div class="dialog-route__station">{_safe_text(row.get('gare_depart'), 'Depart')}</div>
    <div class="dialog-route__country">{_safe_text(depart.get('iso_pays'), 'Europe')}</div>
  </div>
  <div class="dialog-route__col dialog-route__col--center">
    {lucide("train-front", size=28, color="#ea7d57", stroke_width=1.9)}
    <div class="dialog-route__duration">{_duration_from_row(row)}</div>
    <div class="dialog-route__line">{_safe_text(row.get('nom_ligne'), 'Ligne non renseignee')}</div>
    <div class="dialog-route__line">{arrets_label}</div>
  </div>
  <div class="dialog-route__col dialog-route__col--right">
    <div class="dialog-route__meta">Arrivee</div>
    <div class="dialog-route__time">{_format_time(row.get('heure_arrivee'))}</div>
    <div class="dialog-route__station">{_safe_text(row.get('gare_arrivee'), 'Arrivee')}</div>
    <div class="dialog-route__country">{_safe_text(arrivee.get('iso_pays'), 'Europe')}</div>
  </div>
</div>
""")

    st.html('<div class="dialog-section-title">Itineraire sur la carte</div>')
    st.plotly_chart(
        _route_map(stops),
        width="stretch",
        config={"displayModeBar": False, "scrollZoom": True},
    )

    st.html(f'<div class="dialog-section-title">Liste des gares ({len(stops)})</div>')

    last_idx = len(stops) - 1
    rows_html = []
    for idx, stop in enumerate(stops):
        if idx == 0:
            kind = "depart"
            kind_label = "Depart"
        elif idx == last_idx:
            kind = "arrivee"
            kind_label = "Arrivee"
        else:
            kind = "stop"
            kind_label = "Arret"

        lat = stop.get("latitude")
        lon = stop.get("longitude")
        gps = (
            f"{float(lat):.4f}, {float(lon):.4f}"
            if lat is not None and lon is not None and not pd.isna(lat) and not pd.isna(lon)
            else "GPS indisponibles"
        )

        rows_html.append(f"""
<li class="stop-row stop-row--{kind}">
  <div class="stop-row__bullet"><span></span></div>
  <div class="stop-row__body">
    <div class="stop-row__head">
      <div class="stop-row__name">{_safe_text(stop.get('nom_gare'), 'Gare')}</div>
      <div class="stop-row__kind">{kind_label}</div>
    </div>
    <div class="stop-row__meta">
      <span>UIC {_safe_text(stop.get('code_uic'), '—')}</span>
      <span>{_safe_text(stop.get('iso_pays'), '—')}</span>
      <span>{gps}</span>
    </div>
  </div>
</li>
""")

    st.html('<ol class="stop-list">' + "".join(rows_html) + "</ol>")

    st.html('<div class="dialog-section-title">Informations service</div>')
    distance_label = _format_distance(row.get("distance")) or "Non renseignee"
    st.html(f"""
<div class="city-grid">
  <div class="city-block">
    <div class="city-block__meta">Operateur</div>
    <div class="city-block__name">{_safe_text(row.get('code_operateur'), 'ATC')}</div>
    <div class="city-block__row"><span>Type service</span><strong>{_service_badge(_safe_text(row.get('type_service'), 'Service'))}</strong></div>
    <div class="city-block__row"><span>Trajet ID</span><strong>{_safe_text(row.get('trajet_id'), 'Non renseigne')}</strong></div>
  </div>
  <div class="city-block">
    <div class="city-block__meta">Ligne</div>
    <div class="city-block__name">{_safe_text(row.get('nom_ligne'), 'Non renseignee')}</div>
    <div class="city-block__row"><span>Distance</span><strong>{distance_label}</strong></div>
    <div class="city-block__row"><span>Duree</span><strong>{_duration_from_row(row)}</strong></div>
  </div>
</div>
""")


def render() -> None:
    df_trajets = _load_trajets()
    df_gares = _load_gares()
    df_lignes = _load_lignes()
    operateurs = _load_operateurs()

    if df_trajets.empty:
        st.warning("Aucun trajet disponible pour construire la maquette.")
        return

    df = df_trajets.copy()
    df["code_operateur"] = df["trajet_id"].astype(str).str[:3]

    if not df_lignes.empty and "id_ligne" in df.columns and "id_ligne" in df_lignes.columns:
        meta = df_lignes.set_index("id_ligne")
        for col in ["nom_ligne", "type_service", "distance"]:
            if col in meta.columns:
                df[col] = df["id_ligne"].map(meta[col])

    operateurs_df = pd.DataFrame(operateurs) if operateurs else pd.DataFrame()

    gare_options = sorted(df_gares["nom_gare"].dropna().unique().tolist()) if "nom_gare" in df_gares else []
    type_options = sorted([v for v in df["type_service"].dropna().astype(str).unique().tolist() if v])
    line_options = sorted(df["nom_ligne"].dropna().astype(str).unique().tolist()) if "nom_ligne" in df else []
    operator_options = (
        sorted(operateurs_df["operateur"].dropna().astype(str).unique().tolist())
        if not operateurs_df.empty and "operateur" in operateurs_df.columns else []
    )

    st.html(f"""
<div class="section-title">
  <div class="section-title__label">Filtres</div>
  <div class="section-title__meta">{_fmt_int(len(df))} trajets</div>
</div>
""")

    with st.container():
        col_a, col_b = st.columns(2, gap="medium")
        with col_a:
            depart = st.selectbox("Gare de depart", ["Toutes les gares"] + gare_options, index=0)
        with col_b:
            arrivee = st.selectbox("Gare d'arrivee", ["Toutes les gares"] + gare_options, index=0)

        col_c, col_d, col_e = st.columns(3, gap="medium")
        with col_c:
            type_filter = st.selectbox("Type de service", ["Tous les types"] + type_options, index=0)
        with col_d:
            operator_filter = st.selectbox("Operateur", ["Tous les operateurs"] + operator_options, index=0)
        with col_e:
            line_filter = st.selectbox("Ligne", ["Toutes les lignes"] + line_options, index=0)

    if depart != "Toutes les gares":
        df = df[df["gare_depart"] == depart]
    if arrivee != "Toutes les gares":
        df = df[df["gare_arrivee"] == arrivee]
    if type_filter != "Tous les types":
        df = df[df["type_service"] == type_filter]
    if line_filter != "Toutes les lignes":
        df = df[df["nom_ligne"] == line_filter]
    if operator_filter != "Tous les operateurs":
        if not operateurs_df.empty and {"operateur", "code_operateur"}.issubset(operateurs_df.columns):
            selected_codes = operateurs_df.loc[
                operateurs_df["operateur"] == operator_filter, "code_operateur"
            ].astype(str)
            df = df[df["code_operateur"].isin(selected_codes)]
        else:
            df = df[df["code_operateur"] == operator_filter]

    if df.empty:
        st.info("Aucun trajet ne correspond aux filtres choisis.")
        return

    page_size = 6
    total_results = len(df)
    if "trajets_visible" not in st.session_state:
        st.session_state.trajets_visible = page_size
    filter_signature = (depart, arrivee, type_filter, operator_filter, line_filter)
    if st.session_state.get("trajets_filter_sig") != filter_signature:
        st.session_state.trajets_filter_sig = filter_signature
        st.session_state.trajets_visible = page_size
    visible = min(st.session_state.trajets_visible, total_results)

    st.html(
        f'<div class="section-title" style="margin-top:1rem;">'
        f'<div class="section-title__label">Dessertes visibles</div>'
        f'<div class="section-title__meta">{_fmt_int(visible)} sur {_fmt_int(total_results)} resultats</div>'
        f'</div>'
    )

    col_1, col_2 = st.columns(2, gap="medium")
    cards = df.head(visible).to_dict("records")
    for index, row_dict in enumerate(cards):
        target = col_1 if index % 2 == 0 else col_2
        with target:
            with st.container(key=f"tripcard_{index}"):
                st.html(_trip_card(pd.Series(row_dict)))
                trajet_id = _safe_text(row_dict.get("trajet_id"), f"row-{index}")
                if st.button("Voir le detail →", key=f"detail_{trajet_id}_{index}"):
                    depart_info = _gare_lookup(df_gares, row_dict.get("gare_depart"))
                    arrivee_info = _gare_lookup(df_gares, row_dict.get("gare_arrivee"))
                    _trip_dialog(row_dict, depart_info, arrivee_info)

    if visible < total_results:
        remaining = total_results - visible
        next_batch = min(page_size, remaining)
        _, mid, _ = st.columns([1, 1, 1])
        with mid:
            if st.button(
                f"Charger {next_batch} trajets de plus  ({_fmt_int(remaining)} restants)",
                key="trajets_load_more",
                width="stretch",
            ):
                st.session_state.trajets_visible = visible + next_batch
                st.rerun()
