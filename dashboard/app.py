import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import base64

from services.api_service import (
    get_gares,
    get_emissions,
    get_operateurs,
    get_pays_count,
    get_trajets_count,
    get_gares_count,
    get_lignes_count,
    get_trajets_map,
    get_trajets_type,
)
from components.charts import operateurs_chart, trajets_jour_nuit_chart, co2_chart
from components.map import railway_map


def icon_svg(name: str, color: str = "#c8d3e8", size: int = 20) -> str:
    paths = {
        "menu": '<line x1="4" y1="6" x2="20" y2="6"></line><line x1="4" y1="12" x2="20" y2="12"></line><line x1="4" y1="18" x2="20" y2="18"></line>',
        "train": '<line x1="8" y1="3" x2="16" y2="3"></line><line x1="12" y1="3" x2="12" y2="1.8"></line><path d="M6 5h12a2 2 0 0 1 2 2v7a3 3 0 0 1-3 3H7a3 3 0 0 1-3-3V7a2 2 0 0 1 2-2z"></path><line x1="8" y1="9" x2="10.7" y2="9"></line><line x1="13.3" y1="9" x2="16" y2="9"></line><circle cx="8" cy="14.2" r="1.2"></circle><circle cx="16" cy="14.2" r="1.2"></circle><line x1="7" y1="19" x2="5" y2="22"></line><line x1="17" y1="19" x2="19" y2="22"></line><line x1="8.5" y1="20.5" x2="15.5" y2="20.5"></line>',
        "business": '<rect x="4" y="5" width="7" height="15" rx="1"></rect><rect x="13" y="3" width="7" height="17" rx="1"></rect><line x1="6" y1="8" x2="9" y2="8"></line><line x1="6" y1="11" x2="9" y2="11"></line><line x1="15" y1="6" x2="18" y2="6"></line><line x1="15" y1="9" x2="18" y2="9"></line>',
        "route": '<circle cx="5" cy="18" r="2"></circle><circle cx="12" cy="6" r="2"></circle><circle cx="19" cy="18" r="2"></circle><path d="M6.5 16.5 L10.5 8.2 L17.5 16.5"></path>',
        "globe": '<rect x="3" y="5" width="18" height="14" rx="2"></rect><path d="M6.5 10.2l1.8-.9 1.4.8 1.2-.5 1.5 1.2-.6 1.4-1.8.7-.8 1.5-2.1-.3-1.1-1.4z"></path><path d="M13.5 9.8l1.6-.8 1.6.6 1.1 1.5-.6 1.7-1.8.6-1.6-.6-.8-1.5z"></path>',
        "flag": '<line x1="6" y1="3" x2="6" y2="21"></line><path d="M6 4h11l-2.3 3L17 10H6z"></path>',
        "place": '<path d="M12 21s-6-5-6-10a6 6 0 0 1 12 0c0 5-6 10-6 10z"></path><circle cx="12" cy="11" r="2"></circle>',
        "flight": '<path d="M3 13l8-2 8-7 2 2-7 8-2 8-2-2 2-7-7 0z"></path>',
        "balance": '<line x1="12" y1="4" x2="12" y2="19"></line><line x1="5" y1="7" x2="19" y2="7"></line><path d="M5 7l-3 5h6z"></path><path d="M19 7l-3 5h6z"></path><line x1="8" y1="19" x2="16" y2="19"></line>',
        "eco": '<path d="M20 4c-8 0-13 4-13 11 0 3 2 5 5 5 7 0 11-5 11-13 0-2-1-3-3-3z"></path><path d="M9 15c2-2 5-4 9-5"></path>',
        "verified": '<circle cx="12" cy="12" r="9"></circle><path d="M8 12l2.5 2.5L16 9"></path>',
        "warning": '<path d="M12 3l9 17H3z"></path><line x1="12" y1="9" x2="12" y2="13"></line><circle cx="12" cy="17" r="1"></circle>',
        "copy": '<rect x="8" y="8" width="11" height="12" rx="1"></rect><rect x="5" y="4" width="11" height="12" rx="1"></rect>',
        "storage": '<ellipse cx="12" cy="6" rx="7" ry="3"></ellipse><path d="M5 6v10c0 1.7 3.1 3 7 3s7-1.3 7-3V6"></path><path d="M5 11c0 1.7 3.1 3 7 3s7-1.3 7-3"></path>',
    }
    content = paths.get(name, paths["verified"])
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        'viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
        f"{content}</svg>"
    )
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return (
        f'<img src="data:image/svg+xml;base64,{encoded}" '
        f'width="{size}" height="{size}" '
        'style="display:inline-block;vertical-align:middle;" />'
    )


# ══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="ObRail Europe",
    page_icon="🚄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
# INITIALISATION SESSION STATE POUR LA SIDEBAR
# ══════════════════════════════════════════════════════════════

if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = True

sidebar_class = "sidebar-visible" if st.session_state.sidebar_open else "sidebar-hidden"

st.markdown(f"""
<div class="{sidebar_class}">
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# NAVIGATION STATE
# ══════════════════════════════════════════════════════════════

PAGES = ["Aperçu", "Réseau", "Impact Environnemental", "Qualité des Données"]

if "page" not in st.session_state:
    st.session_state.page = "Aperçu"


# ══════════════════════════════════════════════════════════════
# GLOBAL STYLES + SIDEBAR TOGGLE CSS
# ══════════════════════════════════════════════════════════════

st.html("""
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
    *, *::before, *::after { box-sizing: border-box; }
    html, body,
    [data-testid="stAppViewContainer"],
    [data-testid="stApp"] {
        background: #080c14 !important;
        font-family: 'DM Sans', sans-serif;
        color: #c8d3e8;
    }

    /* Masquage des éléments Streamlit par défaut */
    #MainMenu, footer, header,
    [data-testid="stDecoration"] { display: none !important; }

    /* Styles Sidebar */
    [data-testid="stSidebar"] {
        background: #0b1018 !important;
        border-right: 1px solid rgba(255,255,255,0.05) !important;
        min-width: 220px !important;
        max-width: 220px !important;
        transition: margin-left 0.3s ease;
    }
    [data-testid="stSidebar"] > div:first-child { padding: 0 !important; }

    [data-testid="stMainBlockContainer"] {
        padding: 0 1.5rem 1.5rem !important;
        max-width: 100% !important;
    }
    .block-container { padding-top: 0 !important; }

    /* Toggle Sidebar */
    .sidebar-hidden [data-testid="stSidebar"] {
        margin-left: -220px !important;
    }
    .sidebar-visible [data-testid="stSidebar"] {
        margin-left: 0px !important;
    }

    /* Topbar */
    .topbar {
        display:flex; 
        align-items:center; 
        padding:13px 0;
        border-bottom:1px solid rgba(255,255,255,0.05); 
        margin-bottom:14px;
    }

    .topbar button {
        background: transparent !important;
        border: none !important;
        font-size: 1.4rem !important;
        cursor: pointer;
        padding: 4px 8px;
        margin-right: 8px;
        color: #4b5875;
        transition: color 0.2s;
    }
    .topbar button:hover {
        color: #c8d3e8;
    }

    /* Autres styles existants */
    .kpi-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 10px;
        margin-bottom: 14px;
    }
    .kpi-card {
        background: #0d1422;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 13px 15px;
        display: flex; align-items: center; gap: 13px;
        transition: border-color .2s, transform .2s;
    }
    .kpi-card:hover { border-color: rgba(16,185,129,.3); transform: translateY(-1px); }
    .kpi-icon-box {
        width: 44px; height: 44px; border-radius: 11px;
        display: flex; align-items: center; justify-content: center; flex-shrink: 0;
    }
    .kpi-body { flex: 1; min-width: 0; }
    .kpi-label {
        font-size:.62rem; font-weight:600; color:#4b5875;
        text-transform:uppercase; letter-spacing:.1em; margin-bottom:1px;
    }
    .kpi-value {
        font-size:1.55rem; font-weight:700; color:#f0f4ff;
        letter-spacing:-.04em; font-family:'DM Mono',monospace; line-height:1.1;
    }
    .kpi-delta-up   { font-size:.65rem; font-weight:500; color:#10b981; margin-top:2px; }
    .kpi-delta-mute { font-size:.65rem; font-weight:500; color:#4b5875;  margin-top:2px; }

    .chart-header {
        display:flex; align-items:center; justify-content:space-between; margin-bottom:4px;
    }
    .chart-title {
        font-size:.72rem; font-weight:600; color:#c8d3e8;
        text-transform:uppercase; letter-spacing:.08em;
    }
    .dots { display:flex; gap:3px; align-items:center; }
    .dots span { width:4px; height:4px; border-radius:50%; background:#2e3d52; }

    [data-testid="stPlotlyChart"] > div { border-radius: 8px; overflow: hidden; }
    div[data-testid="stPlotlyChart"] { margin: 0 !important; }

    [data-testid="stSidebar"] .stButton > button {
        background: transparent !important; border: none !important;
        border-radius: 8px !important; color: #8492a6 !important;
        font-size: .85rem !important; font-weight: 500 !important;
        text-align: left !important; width: 100% !important;
        padding: 9px 14px !important;
        transition: background .15s, color .15s !important; box-shadow: none !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,.05) !important; color: #c8d3e8 !important;
    }
    [data-testid="stSlider"] { padding: 0 4px; }
</style>
""")


# ══════════════════════════════════════════════════════════════
# DATA CACHE
# ══════════════════════════════════════════════════════════════

@st.cache_data
def load_stats():
    return (
        get_trajets_count()["total_trajets"],
        get_gares_count()["total_gares"],
        get_lignes_count()["total_lignes"],
        get_pays_count()["total_pays"],
    )

trajets, gares, lignes, nb_pays = load_stats()

@st.cache_data
def load_gares():        return pd.DataFrame(get_gares())
@st.cache_data
def load_emissions():    return get_emissions()
@st.cache_data
def load_operateurs():   return get_operateurs()
@st.cache_data
def load_trajets_map():  return pd.DataFrame(get_trajets_map())
@st.cache_data
def load_trajets_type(): return get_trajets_type()

df_gares      = load_gares()
df_trajets    = load_trajets_map()
emissions     = load_emissions()
operateurs    = load_operateurs()
trajets_type  = load_trajets_type()

nb_jour = trajets_type.get("JOUR", 0)
nb_nuit = trajets_type.get("NUIT", 0)


# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════

with st.sidebar:
    st.html(f"""
    <div style="padding:20px 16px 12px;display:flex;align-items:center;gap:10px;">
        <div style="width:36px;height:36px;background:linear-gradient(135deg,#10b981,#059669);
                    border-radius:9px;display:flex;align-items:center;justify-content:center;
                    box-shadow:0 4px 14px rgba(16,185,129,.35);flex-shrink:0;">
            {icon_svg("train", "white", 18)}
        </div>
        <div>
            <div style="font-size:.95rem;font-weight:700;color:#f0f4ff;letter-spacing:-.02em;line-height:1.1;">ObRail</div>
            <div style="font-size:.6rem;color:#4b5875;text-transform:uppercase;letter-spacing:.1em;font-weight:500;">Europe</div>
        </div>
    </div>
    <div style="height:1px;background:rgba(255,255,255,.05);margin:0 16px 14px;"></div>
    <div style="padding:0 12px 6px;font-size:.6rem;font-weight:700;color:#2e3d52;
                text-transform:uppercase;letter-spacing:.14em;">Navigation</div>
    """)

    for page in PAGES:
        if st.button(page, key=f"nav_{page}", width="stretch"):
            st.session_state.page = page

    st.html("""
    <div style="height:1px;background:rgba(255,255,255,.05);margin:14px 16px;"></div>
    <div style="padding:0 12px 6px;font-size:.6rem;font-weight:700;color:#2e3d52;
                text-transform:uppercase;letter-spacing:.14em;">Filtres</div>
    """)

    st.caption("Jauge d'affichage des gares")
    if "map_display_count" not in st.session_state:
        st.session_state.map_display_count = min(2000, len(df_gares))

    minus_col, plus_col = st.columns(2, gap="small")
    with minus_col:
        if st.button("− Diminuer", width="stretch"):
            st.session_state.map_display_count = max(100, st.session_state.map_display_count - 100)
    with plus_col:
        if st.button("+ Augmenter", width="stretch"):
            st.session_state.map_display_count = min(len(df_gares), st.session_state.map_display_count + 100)

    current_gauge = st.slider(
        "Nombre de gares affichées",
        min_value=100,
        max_value=max(100, len(df_gares)),
        value=min(st.session_state.map_display_count, max(100, len(df_gares))),
        step=100,
    )
    st.session_state.map_display_count = current_gauge

    selected_countries = []
    if "iso_pays" in df_gares.columns:
        country_options = sorted([c for c in df_gares["iso_pays"].dropna().unique().tolist() if c])
        selected_countries = st.multiselect(
            "Filtrer par pays (optionnel)",
            options=country_options,
            default=[],
            placeholder="Tous les pays",
        )


# ══════════════════════════════════════════════════════════════
# TOPBAR AVEC BOUTON ☰ FONCTIONNEL
# ══════════════════════════════════════════════════════════════

def topbar(subtitle: str):
    col_btn, col_title = st.columns([0.1, 0.9], gap="small")
    
    with col_btn:
        if st.button("☰", key="toggle_sidebar", help="Ouvrir/Fermer la sidebar"):
            st.session_state.sidebar_open = not st.session_state.sidebar_open
            st.rerun()

    with col_title:
        st.html(f"""
        <div class="topbar">
            <span style="font-size:.95rem;font-weight:600;color:#c8d3e8;">ObRail Europe</span>
            <span style="color:#2e3d52;margin:0 6px;">—</span>
            <span style="font-size:.95rem;font-weight:400;color:#4b5875;">{subtitle}</span>
        </div>
        """)


current_page = st.session_state.page

if selected_countries and "iso_pays" in df_gares.columns:
    df_map_base = df_gares[df_gares["iso_pays"].isin(selected_countries)].copy()
else:
    df_map_base = df_gares.copy()

target_count = min(st.session_state.get("map_display_count", 1200), len(df_map_base))
df_map = df_map_base.sample(target_count, random_state=42) if target_count > 0 else df_map_base

df_trajets_map = df_trajets.sample(1000, random_state=42) if len(df_trajets) > 1000 else df_trajets

# ══════════════════════════════════════════════════════════════
# PAGE: APERÇU
# ══════════════════════════════════════════════════════════════

if current_page == "Aperçu":

    topbar("Railway Data Dashboard")

    st.html(f"""
    <div class="kpi-row">
        <div class="kpi-card">
            <div class="kpi-icon-box" style="background:rgba(16,185,129,.12);">
                {icon_svg("train", "#10b981", 20)}
            </div>
            <div class="kpi-body">
                <div class="kpi-label">Trajets</div>
                <div class="kpi-value">{trajets:,}</div>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon-box" style="background:rgba(59,130,246,.12);">
                {icon_svg("business", "#3b82f6", 20)}
            </div>
            <div class="kpi-body">
                <div class="kpi-label">Opérateurs</div>
                <div class="kpi-value">{len(operateurs)}</div>
                <div class="kpi-delta-mute">Actifs en Europe</div>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon-box" style="background:rgba(245,158,11,.12);">
                {icon_svg("route", "#f59e0b", 20)}
            </div>
            <div class="kpi-body">
                <div class="kpi-label">Lignes</div>
                <div class="kpi-value">{lignes:,}</div>
                <div class="kpi-delta-mute">Réseau actif</div>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon-box" style="background:rgba(167,139,250,.12);">
                {icon_svg("flag", "#a78bfa", 20)}
            </div>
            <div class="kpi-body">
                <div class="kpi-label">Pays couverts</div>
                <div class="kpi-value">{nb_pays}</div>
                <div class="kpi-delta-mute">Europe entière</div>
            </div>
        </div>
    </div>
    """)

    col_left, col_right = st.columns([1, 1.65], gap="small")

    with col_left:
        st.html("""
        <div class="chart-header">
            <span class="chart-title">Trajets Jour vs Nuit</span>
            <div class="dots"><span></span><span></span><span></span></div>
        </div>""")
        st.plotly_chart(
            trajets_jour_nuit_chart(nb_jour, nb_nuit),
            width="stretch",
            config={"displayModeBar": False},
        )

        st.html("""
        <div class="chart-header" style="margin-top:4px;">
            <span class="chart-title">Impact Environnemental</span>
            <div class="dots"><span></span><span></span><span></span></div>
        </div>""")
        st.plotly_chart(
            co2_chart(emissions),
            width="stretch",
            config={"displayModeBar": False},
        )

    with col_right:
        st.html("""
        <div class="chart-header">
            <span class="chart-title">Réseau Ferroviaire Européen</span>
            <div class="dots"><span></span><span></span><span></span></div>
        </div>""")
        st.plotly_chart(
            railway_map(df_map, df_trajets_map),
            width="stretch",
            config={
                "scrollZoom": True,
                "displayModeBar": True,
                "modeBarButtonsToRemove": ["select2d", "lasso2d", "toImage", "sendDataToCloud"],
                "displaylogo": False,
            },
        )

        col_qual, col_ops = st.columns([1, 1], gap="small")

        with col_qual:
            missing      = int(df_gares.isnull().sum().sum())
            total_cells  = int(df_gares.size)
            missing_rate = round(missing / total_cells * 100, 1) if total_cells > 0 else 0
            duplicates   = int(df_gares.duplicated().sum())
            dup_pct      = round(duplicates / len(df_gares) * 100, 1) if len(df_gares) > 0 else 0
            op_miss      = int(round(missing_rate * 0.55))
            em_miss      = int(round(missing_rate * 0.45))
            dup_color    = "#f59e0b" if dup_pct > 0 else "#10b981"

            components.html(f"""
<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:transparent;font-family:'DM Sans',sans-serif}}
.card{{background:#0d1422;border:1px solid rgba(255,255,255,.06);border-radius:12px;
       padding:14px 16px;display:flex;flex-direction:column;gap:10px;height:210px}}
.hd{{display:flex;align-items:center;justify-content:space-between}}
.title{{font-size:.68rem;font-weight:600;color:#c8d3e8;text-transform:uppercase;letter-spacing:.08em}}
.dots{{display:flex;gap:3px}}
.dot{{width:4px;height:4px;border-radius:50%;background:#2e3d52}}
.sub{{font-size:.58rem;color:#4b5875;text-transform:uppercase;letter-spacing:.1em;font-weight:600;margin-bottom:7px}}
.row{{display:flex;align-items:center;gap:16px;margin-bottom:5px}}
.item{{display:flex;align-items:center;gap:5px}}
.dg{{width:8px;height:8px;border-radius:50%;background:#10b981;flex-shrink:0}}
.db{{width:8px;height:8px;border-radius:50%;background:#3b82f6;flex-shrink:0}}
.val{{font-size:1.05rem;font-weight:700;color:#f0f4ff;font-family:'DM Mono',monospace}}
.bars{{margin-left:auto;display:flex;gap:3px;align-items:flex-end;height:20px}}
.leg{{display:flex;gap:14px}}
.li{{font-size:.58rem;color:#4b5875}}
.div{{height:1px;background:rgba(255,255,255,.04)}}
.bot{{display:flex;justify-content:space-between;align-items:flex-end}}
.big{{font-size:1.1rem;font-weight:700;color:#f0f4ff;font-family:'DM Mono',monospace;letter-spacing:-.03em}}
.s2{{font-size:.58rem;color:#4b5875;text-transform:uppercase;letter-spacing:.1em;font-weight:600;margin-top:2px}}
</style></head><body>
<div class="card">
  <div class="hd">
    <div class="title">Qualité des Données</div>
    <div class="dots"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>
  </div>
  <div>
    <div class="sub">Valeurs Manquantes</div>
    <div class="row">
      <div class="item"><div class="dg"></div><span class="val">{op_miss}%</span></div>
      <div class="item"><div class="db"></div><span class="val">{em_miss}%</span></div>
      <div class="bars">
        <div style="width:12px;height:18px;background:#3b82f6;border-radius:2px;opacity:.8"></div>
        <div style="width:8px;height:12px;background:#3b82f6;border-radius:2px;opacity:.5"></div>
        <div style="width:6px;height:8px;background:#8492a6;border-radius:2px;opacity:.3"></div>
        <div style="width:5px;height:5px;background:#8492a6;border-radius:2px;opacity:.2"></div>
      </div>
    </div>
    <div class="leg">
      <span class="li">● Opérateur</span>
      <span class="li">● Émission</span>
    </div>
  </div>
  <div class="div"></div>
  <div class="bot">
    <div>
      <div class="big">{len(df_gares):,}</div>
      <div class="s2">Lignes au total</div>
    </div>
    <div style="text-align:right">
      <div style="display:flex;align-items:baseline;gap:3px;justify-content:flex-end">
        <span style="font-size:.62rem;color:#4b5875">x%</span>
        <span style="font-size:1.1rem;font-weight:700;color:{dup_color};font-family:'DM Mono',monospace">{dup_pct}%</span>
      </div>
      <div class="s2">Doublons</div>
    </div>
  </div>
</div>
</body></html>""", height=220)

        with col_ops:
            st.plotly_chart(
                operateurs_chart(operateurs),
                width="stretch",
                config={"displayModeBar": False},
            )


# ══════════════════════════════════════════════════════════════
# PAGE: RÉSEAU
# ══════════════════════════════════════════════════════════════

elif current_page == "Réseau":

    topbar("Réseau Ferroviaire")

    st.html(f"""
    <div class="kpi-row" style="grid-template-columns:repeat(3,1fr);">
        <div class="kpi-card">
            <div class="kpi-icon-box" style="background:rgba(16,185,129,.12);">
                {icon_svg("place", "#10b981", 20)}
            </div>
            <div class="kpi-body">
                <div class="kpi-label">Gares référencées</div>
                <div class="kpi-value">—</div>
                <div class="kpi-delta-mute">Coordonnées GPS</div>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon-box" style="background:rgba(59,130,246,.12);">
                {icon_svg("route", "#3b82f6", 20)}
            </div>
            <div class="kpi-body">
                <div class="kpi-label">Segments cartographiés</div>
                <div class="kpi-value">1 000+</div>
                <div class="kpi-delta-mute">Tronçons inter-gares</div>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon-box" style="background:rgba(245,158,11,.12);">
                {icon_svg("flag", "#f59e0b", 20)}
            </div>
            <div class="kpi-body">
                <div class="kpi-label">Pays couverts</div>
                <div class="kpi-value">{nb_pays}</div>
                <div class="kpi-delta-mute">Europe entière</div>
            </div>
        </div>
    </div>
    """)

    st.html("""
    <div class="chart-header">
        <span class="chart-title">Carte complète du réseau</span>
        <div class="dots"><span></span><span></span><span></span></div>
    </div>""")

    df_full_map = df_gares.sample(min(3000, len(df_gares)), random_state=1)
    st.plotly_chart(
        railway_map(df_full_map, df_trajets_map),
        width="stretch",
        config={"scrollZoom": True, "displayModeBar": True, "displaylogo": False},
    )

    if not df_gares.empty and "iso_pays" in df_gares.columns:
        st.html("""
        <div class="chart-header" style="margin-top:10px;">
            <span class="chart-title">Répartition des gares par pays</span>
            <div class="dots"><span></span><span></span><span></span></div>
        </div>""")
        import plotly.graph_objects as go
        pays_counts = df_gares["iso_pays"].value_counts().head(15)
        fig_pays = go.Figure(go.Bar(
            x=pays_counts.index,
            y=pays_counts.values,
            marker=dict(
                color=pays_counts.values,
                colorscale=[[0, "#0ea5e9"], [1, "#10b981"]],
                showscale=False, line_width=0,
            ),
            hovertemplate="<b>%{x}</b><br>%{y} gares<extra></extra>",
        ))
        fig_pays.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Sans", color="#8492a6"),
            xaxis=dict(showgrid=False, tickfont=dict(color="#c8d3e8", size=11)),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)", zeroline=False,
                       tickfont=dict(color="#4b5875", size=10)),
            margin=dict(l=10, r=10, t=10, b=10),
            height=260,
        )
        st.plotly_chart(fig_pays, width="stretch", config={"displayModeBar": False})


# ══════════════════════════════════════════════════════════════
# PAGE: IMPACT ENVIRONNEMENTAL
# ══════════════════════════════════════════════════════════════

elif current_page == "Impact Environnemental":

    topbar("Impact Environnemental")

    train_val = round(float(emissions.get("train") or 0))
    avion_val = round(float(emissions.get("avion") or 0))
    saved     = max(0, avion_val - train_val)
    ratio     = round(avion_val / train_val, 1) if train_val > 0 else 0
    total_saved = saved * trajets

    st.html(f"""
    <div class="kpi-row">
        <div class="kpi-card">
            <div class="kpi-icon-box" style="background:rgba(16,185,129,.12);">
                {icon_svg("train", "#10b981", 20)}
            </div>
            <div class="kpi-body">
                <div class="kpi-label">CO₂ moyen / trajet train</div>
                <div class="kpi-value">{train_val:,} kg</div>
                <div class="kpi-delta-mute">8 kg CO₂ / 100 km</div>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon-box" style="background:rgba(249,115,22,.12);">
                {icon_svg("flight", "#f97316", 20)}
            </div>
            <div class="kpi-body">
                <div class="kpi-label">CO₂ moyen / trajet avion</div>
                <div class="kpi-value">{avion_val:,} kg</div>
                <div class="kpi-delta-mute">54 kg CO₂ / 100 km</div>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon-box" style="background:rgba(167,139,250,.12);">
                {icon_svg("balance", "#a78bfa", 20)}
            </div>
            <div class="kpi-body">
                <div class="kpi-label">Rapport avion / train</div>
                <div class="kpi-value">{ratio}×</div>
                <div class="kpi-delta-mute">Plus polluant en avion</div>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon-box" style="background:rgba(16,185,129,.12);">
                {icon_svg("eco", "#10b981", 20)}
            </div>
            <div class="kpi-body">
                <div class="kpi-label">CO₂ économisé (total)</div>
                <div class="kpi-value">{total_saved:,}</div>
                <div class="kpi-delta-up">↓ kg vs scénario tout-avion</div>
            </div>
        </div>
    </div>
    """)

    import plotly.graph_objects as go

    col1, col2 = st.columns(2, gap="small")

    with col1:
        st.html("""
        <div class="chart-header">
            <span class="chart-title">Émissions CO₂ : Train vs Avion</span>
            <div class="dots"><span></span><span></span><span></span></div>
        </div>""")
        st.plotly_chart(
            co2_chart(emissions),
            width="stretch",
            config={"displayModeBar": False},
        )

    with col2:
        st.html("""
        <div class="chart-header">
            <span class="chart-title">Économies CO₂ par opérateur</span>
            <div class="dots"><span></span><span></span><span></span></div>
        </div>""")

        if operateurs:
            df_ops = pd.DataFrame(operateurs).sort_values("trajets", ascending=False).head(8)
            df_ops["co2_saved"] = df_ops["trajets"] * saved
            fig_eco = go.Figure(go.Bar(
                x=df_ops["operateur"],
                y=df_ops["co2_saved"],
                marker=dict(
                    color=df_ops["co2_saved"],
                    colorscale=[[0, "#059669"], [1, "#10b981"]],
                    showscale=False, line_width=0, cornerradius=4,
                ),
                hovertemplate="<b>%{x}</b><br>%{y:,.0f} kg CO₂ économisés<extra></extra>",
            ))
            fig_eco.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="DM Sans", color="#8492a6"),
                xaxis=dict(showgrid=False, tickfont=dict(color="#c8d3e8", size=10),
                           tickangle=-30),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)",
                           zeroline=False, tickfont=dict(color="#4b5875", size=10)),
                margin=dict(l=10, r=10, t=10, b=60),
                height=300,
            )
            st.plotly_chart(fig_eco, width="stretch", config={"displayModeBar": False})

    st.html("""
    <div class="chart-header" style="margin-top:10px;">
        <span class="chart-title">Répartition Jour vs Nuit — Impact CO₂</span>
        <div class="dots"><span></span><span></span><span></span></div>
    </div>""")

    col3, col4 = st.columns(2, gap="small")
    with col3:
        st.plotly_chart(
            trajets_jour_nuit_chart(nb_jour, nb_nuit),
            width="stretch",
            config={"displayModeBar": False},
        )
    with col4:
        co2_jour = nb_jour * train_val
        co2_nuit = nb_nuit * train_val
        fig_jn = go.Figure(go.Bar(
            x=["Trains de jour", "Trains de nuit"],
            y=[co2_jour, co2_nuit],
            marker=dict(
                color=["#10b981", "#3b82f6"], line_width=0, cornerradius=4,
            ),
            text=[f"{co2_jour:,} kg", f"{co2_nuit:,} kg"],
            textposition="outside",
            textfont=dict(color="#c8d3e8", size=11),
            hovertemplate="<b>%{x}</b><br>%{y:,.0f} kg CO₂ total<extra></extra>",
        ))
        fig_jn.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Sans", color="#8492a6"),
            xaxis=dict(showgrid=False, tickfont=dict(color="#c8d3e8", size=12)),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)",
                       zeroline=False, showticklabels=False,
                       range=[0, max(co2_jour, co2_nuit) * 1.2 or 1]),
            margin=dict(l=10, r=10, t=30, b=10),
            height=300,
            showlegend=False,
        )
        st.plotly_chart(fig_jn, width="stretch", config={"displayModeBar": False})


# ══════════════════════════════════════════════════════════════
# PAGE: QUALITÉ DES DONNÉES
# ══════════════════════════════════════════════════════════════

elif current_page == "Qualité des Données":

    topbar("Qualité des Données")

    missing_total = int(df_gares.isnull().sum().sum())
    total_cells   = int(df_gares.size)
    missing_rate  = round(missing_total / total_cells * 100, 2) if total_cells > 0 else 0
    dup_count     = int(df_gares.duplicated().sum())
    dup_pct_q     = round(dup_count / len(df_gares) * 100, 2) if len(df_gares) > 0 else 0
    completeness  = round(100 - missing_rate, 1)

    st.html(f"""
    <div class="kpi-row">
        <div class="kpi-card">
            <div class="kpi-icon-box" style="background:rgba(16,185,129,.12);">
                {icon_svg("verified", "#10b981", 20)}
            </div>
            <div class="kpi-body">
                <div class="kpi-label">Complétude globale</div>
                <div class="kpi-value">{completeness}%</div>
                <div class="kpi-delta-up">Taux de remplissage</div>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon-box" style="background:rgba(249,115,22,.12);">
                {icon_svg("warning", "#f97316", 20)}
            </div>
            <div class="kpi-body">
                <div class="kpi-label">Valeurs manquantes</div>
                <div class="kpi-value">{missing_total:,}</div>
                <div class="kpi-delta-mute">{missing_rate}% des cellules</div>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon-box" style="background:rgba(245,158,11,.12);">
                {icon_svg("copy", "#f59e0b", 20)}
            </div>
            <div class="kpi-body">
                <div class="kpi-label">Doublons détectés</div>
                <div class="kpi-value">{dup_count:,}</div>
                <div class="kpi-delta-mute">{dup_pct_q}% du jeu de données</div>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon-box" style="background:rgba(59,130,246,.12);">
                {icon_svg("storage", "#3b82f6", 20)}
            </div>
            <div class="kpi-body">
                <div class="kpi-label">Enregistrements totaux</div>
                <div class="kpi-value">{len(df_gares):,}</div>
                <div class="kpi-delta-mute">Table gares</div>
            </div>
        </div>
    </div>
    """)

    import plotly.graph_objects as go

    col_a, col_b = st.columns(2, gap="small")
    quality_cols_df = df_gares.drop(columns=["latitude", "longitude"], errors="ignore")

    with col_a:
        st.html("""
        <div class="chart-header">
            <span class="chart-title">Valeurs manquantes par colonne</span>
            <div class="dots"><span></span><span></span><span></span></div>
        </div>""")
        missing_by_col = quality_cols_df.isnull().sum()
        missing_by_col = missing_by_col[missing_by_col > 0].sort_values(ascending=True)
        if not missing_by_col.empty:
            fig_miss = go.Figure(go.Bar(
                x=missing_by_col.values,
                y=missing_by_col.index,
                orientation="h",
                marker=dict(
                    color=missing_by_col.values,
                    colorscale=[[0, "#f59e0b"], [1, "#f97316"]],
                    showscale=False, line_width=0, cornerradius=3,
                ),
                hovertemplate="<b>%{y}</b><br>%{x} valeurs manquantes<extra></extra>",
            ))
            fig_miss.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="DM Sans", color="#8492a6"),
                xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)",
                           zeroline=False, tickfont=dict(color="#4b5875", size=10)),
                yaxis=dict(showgrid=False, zeroline=False,
                           tickfont=dict(color="#c8d3e8", size=12)),
                margin=dict(l=10, r=10, t=10, b=10),
                height=280,
            )
            st.plotly_chart(fig_miss, width="stretch", config={"displayModeBar": False})
        else:
            st.html(f"""
            <div style="background:#0d1422;border:1px solid rgba(255,255,255,.06);
                        border-radius:12px;padding:40px;text-align:center;color:#10b981;">
                <span style="display:block;margin-bottom:8px;">{icon_svg("verified", "#10b981", 36)}</span>
                Aucune valeur manquante détectée
            </div>""")

    with col_b:
        st.html("""
        <div class="chart-header">
            <span class="chart-title">Taux de complétude par colonne</span>
            <div class="dots"><span></span><span></span><span></span></div>
        </div>""")
        completeness_by_col = ((1 - quality_cols_df.isnull().mean()) * 100).round(1).sort_values()
        fig_comp = go.Figure(go.Bar(
            x=completeness_by_col.values,
            y=completeness_by_col.index,
            orientation="h",
            marker=dict(
                color=completeness_by_col.values,
                colorscale=[[0, "#f97316"], [0.5, "#f59e0b"], [1, "#10b981"]],
                showscale=False, line_width=0, cornerradius=3,
                cmin=0, cmax=100,
            ),
            text=[f"{v}%" for v in completeness_by_col.values],
            textposition="outside",
            textfont=dict(color="#8492a6", size=10),
            hovertemplate="<b>%{y}</b><br>%{x:.1f}% complet<extra></extra>",
        ))
        fig_comp.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Sans", color="#8492a6"),
            xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)",
                       zeroline=False, tickfont=dict(color="#4b5875", size=10),
                       range=[0, 115]),
            yaxis=dict(showgrid=False, zeroline=False,
                       tickfont=dict(color="#c8d3e8", size=12)),
            margin=dict(l=10, r=10, t=10, b=10),
            height=280,
        )
        st.plotly_chart(fig_comp, width="stretch", config={"displayModeBar": False})

    st.html("""
    <div class="chart-header" style="margin-top:10px;">
        <span class="chart-title">Couverture géographique (gares avec coordonnées GPS)</span>
        <div class="dots"><span></span><span></span><span></span></div>
    </div>""")

    df_with_coords    = df_gares.dropna(subset=["latitude", "longitude"])
    df_without_coords = df_gares[df_gares["latitude"].isna() | df_gares["longitude"].isna()]
    pct_with    = round(len(df_with_coords) / len(df_gares) * 100, 1) if len(df_gares) > 0 else 0
    pct_without = round(100 - pct_with, 1)

    col_c, col_d = st.columns([2, 1], gap="small")
    with col_c:
        df_geo_sample = df_with_coords.sample(min(2000, len(df_with_coords)), random_state=42)
        st.plotly_chart(
            railway_map(df_geo_sample, pd.DataFrame()),
            width="stretch",
            config={"scrollZoom": True, "displayModeBar": False},
        )
    with col_d:
        components.html(f"""
<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700&family=DM+Mono:wght@500&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:transparent;font-family:'DM Sans',sans-serif;color:#c8d3e8}}
.card{{background:#0d1422;border:1px solid rgba(255,255,255,.06);border-radius:12px;
       padding:16px;display:flex;flex-direction:column;gap:14px;height:100%}}
.row{{display:flex;justify-content:space-between;align-items:center;padding:10px 0;
      border-bottom:1px solid rgba(255,255,255,.04)}}
.lbl{{font-size:.65rem;color:#4b5875;text-transform:uppercase;letter-spacing:.08em}}
.val{{font-size:1.05rem;font-weight:700;font-family:'DM Mono',monospace}}
.bar-bg{{height:6px;background:rgba(255,255,255,.06);border-radius:3px;margin-top:6px}}
.bar-fill{{height:6px;border-radius:3px;background:#10b981}}
</style></head><body>
<div class="card">
  <div style="font-size:.68rem;font-weight:600;text-transform:uppercase;letter-spacing:.08em;color:#c8d3e8">
    Couverture GPS
  </div>
  <div class="row">
    <div><div class="lbl">Avec coordonnées</div><div class="val" style="color:#10b981">{len(df_with_coords):,}</div></div>
    <div style="text-align:right"><div class="lbl">Taux</div><div class="val" style="color:#10b981">{pct_with}%</div></div>
  </div>
  <div>
    <div class="bar-bg"><div class="bar-fill" style="width:{pct_with}%"></div></div>
  </div>
  <div class="row" style="border-bottom:none">
    <div><div class="lbl">Sans coordonnées</div><div class="val" style="color:#f59e0b">{len(df_without_coords):,}</div></div>
    <div style="text-align:right"><div class="lbl">Taux</div><div class="val" style="color:#f59e0b">{pct_without}%</div></div>
  </div>
  <div>
    <div class="bar-bg"><div class="bar-fill" style="width:{pct_without}%;background:#f59e0b"></div></div>
  </div>
  <div style="margin-top:auto;font-size:.65rem;color:#2e3d52;text-align:center">
    Total : {len(df_gares):,} gares
  </div>
</div>
</body></html>""", height=320)

st.html("<div style='height:1rem;'></div>")

