import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlalchemy
import os

# ─────────────────────────────────────────────
# CONFIG PAGE
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ObRail Europe – Tableau de bord",
    page_icon="🚄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# STYLE CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Inter:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.main { background-color: #0a0f1e; }
.stApp { background-color: #0a0f1e; }

h1, h2, h3 { font-family: 'Syne', sans-serif !important; }

.metric-card {
    background: linear-gradient(135deg, #111827 0%, #1a2540 100%);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
    box-shadow: 0 4px 24px rgba(0,120,255,0.08);
}
.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
    color: #3b82f6;
    line-height: 1.1;
}
.metric-label {
    font-size: 0.78rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 4px;
}
.metric-sub {
    font-size: 0.85rem;
    color: #64748b;
    margin-top: 2px;
}

.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #e2e8f0;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 2px solid #1e3a5f;
}

.alert-ok {
    background: #052e16;
    border-left: 4px solid #22c55e;
    padding: 10px 16px;
    border-radius: 6px;
    color: #86efac;
    font-size: 0.88rem;
    margin: 6px 0;
}
.alert-warn {
    background: #2d1b00;
    border-left: 4px solid #f59e0b;
    padding: 10px 16px;
    border-radius: 6px;
    color: #fcd34d;
    font-size: 0.88rem;
    margin: 6px 0;
}
.alert-error {
    background: #1f0000;
    border-left: 4px solid #ef4444;
    padding: 10px 16px;
    border-radius: 6px;
    color: #fca5a5;
    font-size: 0.88rem;
    margin: 6px 0;
}

.sidebar-section {
    background: #111827;
    border-radius: 8px;
    padding: 14px;
    margin-bottom: 12px;
    border: 1px solid #1e3a5f;
}

[data-testid="stSidebar"] {
    background-color: #060d1a !important;
}
[data-testid="stSidebar"] * { color: #cbd5e1 !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# CONNEXION DB
# ─────────────────────────────────────────────
@st.cache_resource
def get_engine(url: str):
    return sqlalchemy.create_engine(url, connect_args={"connect_timeout": 5})

@st.cache_data(ttl=300)
def query(_engine, sql: str) -> pd.DataFrame:
    with _engine.connect() as conn:
        return pd.read_sql(sql, conn)


# ─────────────────────────────────────────────
# SIDEBAR – CONNEXION
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚄 ObRail Europe")
    st.markdown("---")

    st.markdown("### 🔌 Connexion à la base")
    host     = st.text_input("Hôte",     value="localhost")
    port     = st.text_input("Port",     value="5432")
    dbname   = st.text_input("Base",     value="mspr")
    user     = st.text_input("Utilisateur", value="postgres")
    password = st.text_input("Mot de passe", type="password")

    connect_btn = st.button("Se connecter", use_container_width=True, type="primary")
    st.markdown("---")
    st.caption("Tableau de bord – Livrable n°6\nMSPR Bloc E6.1 – ObRail Europe")

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div style='padding: 24px 0 8px 0;'>
  <span style='font-family:Syne;font-size:2rem;font-weight:800;color:#e2e8f0;'>
    ObRail Europe
  </span>
  <span style='font-family:Syne;font-size:1rem;font-weight:400;color:#3b82f6;margin-left:16px;'>
    Tableau de bord de contrôle des données
  </span>
</div>
<p style='color:#64748b;font-size:0.9rem;margin-bottom:24px;'>
  Qualité, complétude et analyse des flux ferroviaires européens
</p>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# LOGIQUE PRINCIPALE
# ─────────────────────────────────────────────
if not connect_btn and "engine" not in st.session_state:
    st.info("👈 Renseignez vos identifiants dans la barre latérale et cliquez sur **Se connecter**.")
    st.stop()

if connect_btn:
    db_url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
    try:
        engine = get_engine(db_url)
        with engine.connect() as c:
            c.execute(sqlalchemy.text("SELECT 1"))
        st.session_state["engine"] = engine
        st.session_state["db_url"] = db_url
        st.success("✅ Connexion réussie !")
    except Exception as e:
        st.error(f"❌ Connexion échouée : {e}")
        st.stop()

engine = st.session_state.get("engine")
if engine is None:
    st.stop()

# ─────────────────────────────────────────────
# CHARGEMENT DES DONNÉES
# ─────────────────────────────────────────────
try:
    # Comptages
    counts_sql = """
        SELECT 'pays'        AS t, COUNT(*) AS n FROM pays        UNION ALL
        SELECT 'operateur',              COUNT(*) FROM operateur   UNION ALL
        SELECT 'gare',                   COUNT(*) FROM gare        UNION ALL
        SELECT 'ligne',                  COUNT(*) FROM ligne       UNION ALL
        SELECT 'type_train',             COUNT(*) FROM type_train  UNION ALL
        SELECT 'trajet',                 COUNT(*) FROM trajet      UNION ALL
        SELECT 'itineraire',             COUNT(*) FROM itineraire  UNION ALL
        SELECT 'exploite',               COUNT(*) FROM exploite    UNION ALL
        SELECT 'utilisation',            COUNT(*) FROM utilisation UNION ALL
        SELECT 'emission',               COUNT(*) FROM emission
    """
    df_counts = query(engine, counts_sql).set_index("t")["n"].to_dict()

    # Lignes JOUR vs NUIT
    df_service = query(engine, "SELECT type_service, COUNT(*) AS n FROM ligne GROUP BY type_service")

    # Gares par pays (top 15)
    df_gares_pays = query(engine, """
        SELECT p.nom_pays, COUNT(g.code_uic) AS nb_gares
        FROM gare g JOIN pays p ON g.iso_pays = p.iso_pays
        GROUP BY p.nom_pays ORDER BY nb_gares DESC LIMIT 15
    """)

    # Trajets par ligne (top 10)
    df_trajets_ligne = query(engine, """
        SELECT l.nom_ligne, COUNT(t.trajet_id) AS nb_trajets,
               l.type_service
        FROM trajet t JOIN ligne l ON t.id_ligne = l.id_ligne
        GROUP BY l.nom_ligne, l.type_service
        ORDER BY nb_trajets DESC LIMIT 10
    """)

    # Émissions CO2 : top 10 économies train vs avion
    df_em = query(engine, """
        SELECT origine, destination,
               empreinte_train_kg, empreinte_avion_kg,
               ROUND((empreinte_avion_kg - empreinte_train_kg)::numeric, 4) AS economie_kg,
               distance_train_km
        FROM emission
        WHERE empreinte_avion_kg IS NOT NULL
        ORDER BY economie_kg DESC LIMIT 10
    """)

    # Qualité : valeurs NULL dans trajet
    df_null_trajet = query(engine, """
        SELECT
            SUM(CASE WHEN gare_depart  IS NULL OR gare_depart  = '' THEN 1 ELSE 0 END) AS gare_depart_null,
            SUM(CASE WHEN gare_arrivee IS NULL OR gare_arrivee = '' THEN 1 ELSE 0 END) AS gare_arrivee_null,
            SUM(CASE WHEN heure_depart IS NULL OR heure_depart = '' THEN 1 ELSE 0 END) AS heure_depart_null,
            SUM(CASE WHEN heure_arrivee IS NULL OR heure_arrivee= '' THEN 1 ELSE 0 END) AS heure_arrivee_null,
            COUNT(*) AS total
        FROM trajet
    """)

    # Intégrité référentielle
    orphelins = {
        "Gares sans pays":     query(engine, "SELECT COUNT(*) AS n FROM gare WHERE iso_pays NOT IN (SELECT iso_pays FROM pays)").iloc[0,0],
        "Trajets sans ligne":  query(engine, "SELECT COUNT(*) AS n FROM trajet WHERE id_ligne NOT IN (SELECT id_ligne FROM ligne)").iloc[0,0],
        "Itinéraires orphelins": query(engine, "SELECT COUNT(*) AS n FROM itineraire WHERE trajet_id NOT IN (SELECT trajet_id FROM trajet)").iloc[0,0],
        "Exploite orphelins":  query(engine, "SELECT COUNT(*) AS n FROM exploite WHERE code_operateur NOT IN (SELECT code_operateur FROM operateur) OR id_ligne NOT IN (SELECT id_ligne FROM ligne)").iloc[0,0],
    }

    # Opérateurs et lignes exploitées
    df_op_lignes = query(engine, """
        SELECT o.nom_operateur, COUNT(e.id_ligne) AS nb_lignes
        FROM exploite e JOIN operateur o ON e.code_operateur = o.code_operateur
        GROUP BY o.nom_operateur ORDER BY nb_lignes DESC LIMIT 12
    """)

except Exception as e:
    st.error(f"Erreur lors de la lecture des données : {e}")
    st.stop()

# ─────────────────────────────────────────────
# ONGLETS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Vue générale",
    "🌍 Géographie & Réseau",
    "🌿 Émissions CO₂",
    "🔍 Qualité des données",
])

# ══════════════════════════════════════════════
# ONGLET 1 – VUE GÉNÉRALE
# ══════════════════════════════════════════════
with tab1:
    # KPIs
    cols = st.columns(5)
    kpis = [
        (df_counts.get("pays", 0),       "Pays",         ""),
        (df_counts.get("gare", 0),       "Gares",        "référentiel UIC"),
        (df_counts.get("ligne", 0),      "Lignes",       "ferroviaires"),
        (df_counts.get("trajet", 0),     "Trajets",      "programmés"),
        (df_counts.get("operateur", 0),  "Opérateurs",   "européens"),
    ]
    for col, (val, label, sub) in zip(cols, kpis):
        with col:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-value'>{val:,}</div>
                <div class='metric-label'>{label}</div>
                <div class='metric-sub'>{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("<div class='section-title'>Répartition Jour / Nuit</div>", unsafe_allow_html=True)
        if not df_service.empty:
            colors = {"JOUR": "#3b82f6", "NUIT": "#8b5cf6"}
            fig_pie = px.pie(
                df_service, values="n", names="type_service",
                color="type_service",
                color_discrete_map=colors,
                hole=0.55,
            )
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e2e8f0", margin=dict(t=10, b=10, l=10, r=10),
                legend=dict(font=dict(color="#94a3b8")),
                showlegend=True,
            )
            fig_pie.update_traces(textfont_color="#e2e8f0")
            st.plotly_chart(fig_pie, use_container_width=True)

            for _, row in df_service.iterrows():
                pct = row["n"] / df_service["n"].sum() * 100
                st.markdown(f"**{row['type_service']}** : {row['n']} lignes ({pct:.1f}%)")

    with col2:
        st.markdown("<div class='section-title'>Top 10 lignes par nombre de trajets</div>", unsafe_allow_html=True)
        if not df_trajets_ligne.empty:
            color_map = {"JOUR": "#3b82f6", "NUIT": "#8b5cf6"}
            fig_bar = px.bar(
                df_trajets_ligne.sort_values("nb_trajets"),
                x="nb_trajets", y="nom_ligne",
                orientation="h",
                color="type_service",
                color_discrete_map=color_map,
                labels={"nb_trajets": "Nombre de trajets", "nom_ligne": ""},
            )
            fig_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e2e8f0",
                xaxis=dict(gridcolor="#1e3a5f"),
                yaxis=dict(gridcolor="rgba(0,0,0,0)"),
                margin=dict(t=10, b=10, l=10, r=10),
                legend_title_text="Service",
                legend=dict(font=dict(color="#94a3b8")),
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    # Opérateurs
    st.markdown("<div class='section-title'>Lignes exploitées par opérateur</div>", unsafe_allow_html=True)
    if not df_op_lignes.empty:
        fig_op = px.bar(
            df_op_lignes.sort_values("nb_lignes"),
            x="nb_lignes", y="nom_operateur",
            orientation="h",
            color="nb_lignes",
            color_continuous_scale=["#1e3a5f", "#3b82f6", "#60a5fa"],
            labels={"nb_lignes": "Lignes exploitées", "nom_operateur": ""},
        )
        fig_op.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e2e8f0",
            xaxis=dict(gridcolor="#1e3a5f"),
            yaxis=dict(gridcolor="rgba(0,0,0,0)"),
            margin=dict(t=10, b=10, l=10, r=10),
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_op, use_container_width=True)


# ══════════════════════════════════════════════
# ONGLET 2 – GÉOGRAPHIE & RÉSEAU
# ══════════════════════════════════════════════
with tab2:
    st.markdown("<div class='section-title'>Nombre de gares par pays (Top 15)</div>", unsafe_allow_html=True)
    if not df_gares_pays.empty:
        fig_geo = px.bar(
            df_gares_pays.sort_values("nb_gares"),
            x="nb_gares", y="nom_pays",
            orientation="h",
            color="nb_gares",
            color_continuous_scale=["#0f2744", "#1e3a5f", "#3b82f6", "#93c5fd"],
            labels={"nb_gares": "Nombre de gares", "nom_pays": ""},
        )
        fig_geo.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e2e8f0",
            xaxis=dict(gridcolor="#1e3a5f"),
            yaxis=dict(gridcolor="rgba(0,0,0,0)"),
            margin=dict(t=10, b=10),
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_geo, use_container_width=True)

    # Carte des gares
    st.markdown("<div class='section-title'>Carte des gares du réseau</div>", unsafe_allow_html=True)
    try:
        df_map = query(engine, """
            SELECT nom_gare, latitude, longitude, p.nom_pays
            FROM gare g JOIN pays p ON g.iso_pays = p.iso_pays
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
              AND latitude BETWEEN 35 AND 72
              AND longitude BETWEEN -12 AND 40
            LIMIT 5000
        """)
        if not df_map.empty:
            fig_map = px.scatter_mapbox(
                df_map, lat="latitude", lon="longitude",
                hover_name="nom_gare", hover_data={"nom_pays": True, "latitude": False, "longitude": False},
                color_discrete_sequence=["#3b82f6"],
                zoom=3.5, center={"lat": 50, "lon": 10},
                opacity=0.6,
            )
            fig_map.update_layout(
                mapbox_style="carto-darkmatter",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=0, b=0, l=0, r=0),
                height=500,
            )
            st.plotly_chart(fig_map, use_container_width=True)
            st.caption(f"Affichage de {len(df_map):,} gares sur {df_counts.get('gare', 0):,} au total.")
    except Exception as e:
        st.warning(f"Carte non disponible : {e}")


# ══════════════════════════════════════════════
# ONGLET 3 – ÉMISSIONS CO₂
# ══════════════════════════════════════════════
with tab3:
    col1, col2, col3 = st.columns(3)
    try:
        df_em_stats = query(engine, """
            SELECT
                ROUND(AVG(empreinte_train_kg)::numeric, 4) AS moy_train,
                ROUND(AVG(empreinte_avion_kg)::numeric, 4) AS moy_avion,
                ROUND(AVG((empreinte_avion_kg - empreinte_train_kg))::numeric, 4) AS moy_eco
            FROM emission WHERE empreinte_avion_kg IS NOT NULL
        """)
        moy_train = float(df_em_stats["moy_train"].iloc[0])
        moy_avion = float(df_em_stats["moy_avion"].iloc[0])
        moy_eco   = float(df_em_stats["moy_eco"].iloc[0])
        ratio = round(moy_avion / moy_train, 1) if moy_train > 0 else 0

        for col, (val, label, sub) in zip(
            st.columns(3),
            [
                (f"{moy_train:.4f} kg", "Empreinte moyenne TRAIN", "CO₂ par trajet"),
                (f"{moy_avion:.4f} kg", "Empreinte moyenne AVION", "CO₂ par trajet"),
                (f"×{ratio}", "Le train émet", f"{ratio}x moins que l'avion"),
            ]
        ):
            with col:
                st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-value'>{val}</div>
                    <div class='metric-label'>{label}</div>
                    <div class='metric-sub'>{sub}</div>
                </div>""", unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Stats émissions indisponibles : {e}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Top 10 trajets — économie CO₂ train vs avion</div>", unsafe_allow_html=True)

    if not df_em.empty:
        df_em_plot = df_em.copy()
        df_em_plot["trajet"] = df_em_plot["origine"] + " → " + df_em_plot["destination"]

        fig_em = go.Figure()
        fig_em.add_trace(go.Bar(
            y=df_em_plot["trajet"], x=df_em_plot["empreinte_avion_kg"],
            name="Avion", orientation="h",
            marker_color="#ef4444", opacity=0.85,
        ))
        fig_em.add_trace(go.Bar(
            y=df_em_plot["trajet"], x=df_em_plot["empreinte_train_kg"],
            name="Train", orientation="h",
            marker_color="#22c55e", opacity=0.85,
        ))
        fig_em.update_layout(
            barmode="group",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#e2e8f0",
            xaxis=dict(gridcolor="#1e3a5f", title="Empreinte CO₂ (kg)"),
            yaxis=dict(gridcolor="rgba(0,0,0,0)"),
            margin=dict(t=10, b=10),
            legend=dict(font=dict(color="#94a3b8")),
            height=420,
        )
        st.plotly_chart(fig_em, use_container_width=True)

    # Tableau détaillé
    st.markdown("<div class='section-title'>Données détaillées</div>", unsafe_allow_html=True)
    if not df_em.empty:
        df_display = df_em[["origine", "destination", "distance_train_km",
                             "empreinte_train_kg", "empreinte_avion_kg", "economie_kg"]].copy()
        df_display.columns = ["Origine", "Destination", "Dist. train (km)",
                               "CO₂ train (kg)", "CO₂ avion (kg)", "Économie (kg)"]
        st.dataframe(df_display, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════
# ONGLET 4 – QUALITÉ DES DONNÉES
# ══════════════════════════════════════════════
with tab4:
    st.markdown("<div class='section-title'>Intégrité référentielle</div>", unsafe_allow_html=True)

    all_ok = all(v == 0 for v in orphelins.values())
    if all_ok:
        st.markdown("<div class='alert-ok'>✅ Aucun enregistrement orphelin détecté — intégrité référentielle complète.</div>", unsafe_allow_html=True)

    cols_int = st.columns(len(orphelins))
    for col, (label, val) in zip(cols_int, orphelins.items()):
        with col:
            status = "✅" if val == 0 else "❌"
            card_class = "alert-ok" if val == 0 else "alert-error"
            st.markdown(f"<div class='{card_class}'>{status} <b>{label}</b><br>{val} orphelin(s)</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Complétude des champs — Table Trajet</div>", unsafe_allow_html=True)

    if not df_null_trajet.empty:
        total = int(df_null_trajet["total"].iloc[0])
        champs = {
            "Gare départ":  int(df_null_trajet["gare_depart_null"].iloc[0]),
            "Gare arrivée": int(df_null_trajet["gare_arrivee_null"].iloc[0]),
            "Heure départ": int(df_null_trajet["heure_depart_null"].iloc[0]),
            "Heure arrivée":int(df_null_trajet["heure_arrivee_null"].iloc[0]),
        }
        cols_q = st.columns(len(champs))
        for col, (label, n_null) in zip(cols_q, champs.items()):
            with col:
                taux = (1 - n_null / total) * 100 if total > 0 else 100
                color = "#22c55e" if taux >= 95 else "#f59e0b" if taux >= 80 else "#ef4444"
                st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-value' style='color:{color};font-size:1.8rem;'>{taux:.1f}%</div>
                    <div class='metric-label'>{label}</div>
                    <div class='metric-sub'>{n_null} valeurs manquantes / {total}</div>
                </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Synthèse globale
    st.markdown("<div class='section-title'>Volume de données par table</div>", unsafe_allow_html=True)
    df_vol = pd.DataFrame(list(df_counts.items()), columns=["Table", "Enregistrements"])
    df_vol = df_vol.sort_values("Enregistrements", ascending=True)

    fig_vol = px.bar(
        df_vol, x="Enregistrements", y="Table",
        orientation="h",
        color="Enregistrements",
        color_continuous_scale=["#0f2744", "#1e3a5f", "#3b82f6"],
        text="Enregistrements",
    )
    fig_vol.update_traces(textfont_color="#e2e8f0", textposition="outside")
    fig_vol.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e8f0",
        xaxis=dict(gridcolor="#1e3a5f"),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        margin=dict(t=10, b=10, r=80),
        coloraxis_showscale=False,
        height=380,
    )
    st.plotly_chart(fig_vol, use_container_width=True)

    # Alertes qualité
    st.markdown("<div class='section-title'>Alertes qualité</div>", unsafe_allow_html=True)

    nb_itin = df_counts.get("itineraire", 0)
    nb_trajet = df_counts.get("trajet", 0)
    ratio_itin = nb_itin / nb_trajet if nb_trajet > 0 else 0

    alertes = [
        (nb_itin < nb_trajet,      f"⚠️ {nb_itin} itinéraires pour {nb_trajet} trajets — certains trajets n'ont pas d'itinéraire détaillé.", "warn"),
        (df_counts.get("utilisation", 0) == 0, "⚠️ La table utilisation est vide — aucune relation opérateur/type de train.", "warn"),
        (df_counts.get("source", 0) == 0,      "ℹ️ La table source est vide — traçabilité ETL non documentée.", "warn"),
        (all_ok,                   "✅ Aucun enregistrement orphelin — intégrité référentielle parfaite.", "ok"),
        (df_counts.get("emission", 0) > 0, f"✅ {df_counts.get('emission', 0)} mesures d'émissions CO₂ chargées.", "ok"),
    ]
    for condition, msg, level in alertes:
        if condition:
            st.markdown(f"<div class='alert-{'warn' if level=='warn' else 'ok'}'>{msg}</div>", unsafe_allow_html=True)
