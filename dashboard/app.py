"""Shell principal du dashboard ObRail Europe."""

import importlib

import streamlit as st

from components.icons import lucide


st.set_page_config(
    page_title="ObRail Europe",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.html("""
<a href="#main-content" class="skip-link">Aller au contenu principal</a>
<div id="main-content">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root {
    --bg: #f6f1e8;
    --bg-2: #efe7db;
    --surface: rgba(255,255,255,0.72);
    --surface-strong: #fffdfa;
    --border: #dfd3c2;
    --text: #143d35;
    --muted: #3d5a52;
    --muted-2: #6d877f;
    --green: #174936;
    --green-2: #255845;
    --green-soft: rgba(23,73,54,0.08);
    --navy: #1d2a53;
    --navy-soft: rgba(29,42,83,0.10);
    --accent: #c95f37;
    --accent-soft: rgba(234,125,87,0.12);
    --ok: #1f6e4e;
    --warn: #d68740;
    --danger: #b94d4d;
    --shadow: 0 18px 44px rgba(27, 45, 38, 0.10);
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background:
        radial-gradient(circle at top left, rgba(255,255,255,0.75), transparent 30%),
        linear-gradient(180deg, #faf7f1 0%, var(--bg) 100%) !important;
    color: var(--text);
    font-family: 'Inter', sans-serif !important;
}

*, *::before, *::after { box-sizing: border-box; }
#MainMenu, header, footer, [data-testid="stDecoration"], [data-testid="stSidebar"] { display: none !important; }
[data-testid="stMainBlockContainer"] { padding: 0 2rem 2rem !important; max-width: 1440px !important; margin: 0 auto !important; }
.block-container { padding-top: 0 !important; }

:focus-visible {
    outline: 2px solid var(--green) !important;
    outline-offset: 3px !important;
    border-radius: 6px;
}
.stButton > button:focus-visible {
    outline-offset: 4px !important;
}

.shell-brand-marker { display: none; }
[data-testid="stHorizontalBlock"]:has(.shell-brand-marker) {
    position: sticky;
    top: 0;
    z-index: 20;
    margin: 0 -2rem 1.75rem !important;
    padding: 0.75rem 2rem !important;
    background: rgba(248, 243, 235, 0.92) !important;
    backdrop-filter: blur(18px);
    border-bottom: 1px solid rgba(223,211,194,0.8);
    align-items: center !important;
    gap: 0.6rem !important;
}
[data-testid="stHorizontalBlock"]:has(.shell-brand-marker) [data-testid="stColumn"] {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}
[data-testid="stHorizontalBlock"]:has(.shell-brand-marker) [data-testid="stColumn"]:first-child {
    justify-content: flex-start !important;
}
[data-testid="stHorizontalBlock"]:has(.shell-brand-marker) .stButton {
    margin: 0 !important;
}
[data-testid="stHorizontalBlock"]:has(.shell-brand-marker) .stButton > button {
    padding: 0.5rem 1rem !important;
    font-size: 0.88rem !important;
    min-height: 0 !important;
    height: 40px !important;
    width: 100% !important;
    white-space: nowrap !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 0.45rem !important;
}
[data-testid="stHorizontalBlock"]:has(.shell-brand-marker) .stButton > button p {
    margin: 0 !important;
    line-height: 1 !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
}
.brand {
    display: flex;
    align-items: center;
    gap: 0.85rem;
}
.brand__icon {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    background: linear-gradient(135deg, #1c543f 0%, #143d35 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #f7efe4;
    font-size: 1.15rem;
    box-shadow: inset 0 0 0 1px rgba(255,255,255,0.12);
}
.brand__name {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.85rem;
    line-height: 0.9;
    color: var(--text);
}
.brand__sub {
    margin-top: 0.12rem;
    font-size: 0.72rem;
    letter-spacing: 0.32em;
    text-transform: uppercase;
    color: var(--muted);
}

.hero {
    padding: 1rem 0 2rem;
}
.eyebrow {
    font-size: 0.8rem;
    letter-spacing: 0.38em;
    text-transform: uppercase;
    color: var(--muted);
    font-family: 'IBM Plex Mono', monospace;
    margin-bottom: 0.6rem;
}
.hero h1 {
    margin: 0;
    color: var(--text);
    font-family: 'Cormorant Garamond', serif !important;
    font-size: clamp(3.2rem, 6vw, 5rem);
    line-height: 0.9;
    font-weight: 600 !important;
}
.hero p {
    max-width: 900px;
    font-size: 1.12rem;
    line-height: 1.55;
    color: var(--muted);
    margin: 1rem 0 0;
}
.hero code {
    font-family: 'IBM Plex Mono', monospace;
    background: rgba(255,255,255,0.55);
    padding: 0.15rem 0.45rem;
    border-radius: 999px;
    color: var(--green);
}

.glass-card, .panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 24px;
    box-shadow: var(--shadow);
    backdrop-filter: blur(14px);
}
.panel {
    padding: 1.35rem;
    margin-bottom: 1rem;
}
.section-title {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    margin: 0 0 1rem;
}
.section-title__label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    letter-spacing: 0.28em;
    text-transform: uppercase;
    color: var(--muted);
}
.section-title__meta {
    color: var(--muted);
    font-size: 0.92rem;
}

.kpi-row {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 1rem;
    margin: 0 0 1.25rem;
}
.kpi-card {
    background: var(--surface-strong);
    border: 1px solid var(--border);
    border-radius: 22px;
    padding: 1.1rem 1.2rem;
    min-height: 150px;
    position: relative;
    overflow: hidden;
}
.kpi-card::after {
    content: "";
    position: absolute;
    inset: auto -40px -40px auto;
    width: 120px;
    height: 120px;
    border-radius: 50%;
    background: linear-gradient(135deg, rgba(255,255,255,0), rgba(23,73,54,0.05));
}
.kpi-icon {
    width: 36px;
    height: 36px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 999px;
    background: rgba(255,255,255,0.9);
    border: 1px solid rgba(255,255,255,0.7);
    font-size: 1rem;
}
.kpi-icon-clean {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    width: 32px;
    height: 32px;
    margin-bottom: 0.4rem;
}
.kpi-icon-clean svg {
    width: 100%;
    height: 100%;
    display: block;
}
.kpi-card--filled::after { display: none; }
.kpi-card--filled .kpi-label { margin-top: 0.4rem; }
.kpi-label {
    margin-top: 0.95rem;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.32em;
    color: var(--muted);
    font-family: 'IBM Plex Mono', monospace;
}
.kpi-value {
    margin-top: 0.45rem;
    font-family: 'Cormorant Garamond', serif;
    font-size: 3rem;
    line-height: 0.95;
    color: var(--text);
}
.kpi-hint {
    margin-top: 0.45rem;
    color: var(--muted);
    font-size: 0.96rem;
}

.status-band {
    background: linear-gradient(135deg, var(--green) 0%, #12372d 100%);
    color: #f7efe4;
    border-radius: 22px;
    padding: 1.35rem 1.55rem;
    margin-bottom: 1rem;
    box-shadow: 0 18px 44px rgba(20,61,53,0.18);
}
.status-band__eyebrow {
    color: rgba(247,239,228,0.72);
    font-family: 'IBM Plex Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 0.3em;
    font-size: 0.75rem;
}
.status-band__title {
    margin-top: 0.45rem;
    font-family: 'Cormorant Garamond', serif;
    font-size: 3rem;
    line-height: 0.95;
}
.status-band__hint {
    margin-top: 0.35rem;
    color: rgba(247,239,228,0.72);
    font-size: 0.98rem;
}

.trip-hero {
    display: grid;
    grid-template-columns: 1.1fr 1fr 1.1fr;
    overflow: hidden;
    border-radius: 24px;
    margin-bottom: 1.25rem;
}
.trip-hero__segment {
    min-height: 220px;
    padding: 2rem;
    color: #f7efe4;
}
.trip-hero__segment--left, .trip-hero__segment--right {
    background: linear-gradient(135deg, #184835 0%, #12372d 100%);
}
.trip-hero__segment--center {
    background: linear-gradient(135deg, #202f63 0%, #18244b 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
}
.trip-meta {
    font-family: 'IBM Plex Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 0.34em;
    color: rgba(247,239,228,0.58);
    font-size: 0.76rem;
}
.trip-time {
    margin-top: 0.95rem;
    font-family: 'Cormorant Garamond', serif;
    font-size: 4.6rem;
    line-height: 0.9;
}
.trip-station {
    margin-top: 0.85rem;
    font-size: 1.45rem;
}
.trip-country {
    margin-top: 0.2rem;
    color: rgba(247,239,228,0.65);
    font-size: 0.92rem;
}
.trip-duration {
    font-family: 'Cormorant Garamond', serif;
    font-size: 3.1rem;
    line-height: 0.95;
}
.trip-duration-meta {
    margin-top: 0.6rem;
    color: rgba(247,239,228,0.62);
    font-family: 'IBM Plex Mono', monospace;
    letter-spacing: 0.26em;
    text-transform: uppercase;
    font-size: 0.78rem;
}

.info-card {
    background: rgba(255,255,255,0.82);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1.1rem 1.2rem;
    min-height: 124px;
}
.info-card__label {
    font-family: 'IBM Plex Mono', monospace;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.3em;
    font-size: 0.74rem;
}
.info-card__value {
    margin-top: 0.55rem;
    font-family: 'Cormorant Garamond', serif;
    font-size: 2rem;
    line-height: 1;
    color: var(--text);
}
.info-card__hint {
    margin-top: 0.45rem;
    color: var(--muted);
    font-size: 0.94rem;
}

.trip-card {
    background: linear-gradient(135deg, #1a2348 0%, #182243 100%);
    color: #f7efe4;
    border-radius: 18px;
    border-left: 4px solid var(--accent);
    padding: 1.1rem 1.2rem 1rem;
    margin-bottom: 0.95rem;
    box-shadow: 0 14px 36px rgba(24,34,67,0.20);
}
.trip-card__top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.8rem;
}
.trip-card__id {
    font-family: 'IBM Plex Mono', monospace;
    color: rgba(247,239,228,0.62);
    font-size: 0.78rem;
    letter-spacing: 0.15em;
}
.trip-card__badge {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.06);
    color: #efe5d5;
    padding: 0.22rem 0.58rem;
    border-radius: 999px;
    font-size: 0.78rem;
}
.trip-card__line {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    gap: 0.8rem;
    align-items: center;
    margin: 1.05rem 0 0.9rem;
}
.trip-card__time {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2.55rem;
    line-height: 0.9;
}
.trip-card__station {
    margin-top: 0.3rem;
    color: rgba(247,239,228,0.82);
    font-size: 0.98rem;
}
.trip-card__duration {
    text-align: center;
    color: rgba(234,125,87,0.95);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.9rem;
}
.trip-card__footer {
    display: flex;
    justify-content: space-between;
    gap: 0.8rem;
    padding-top: 0.95rem;
    border-top: 1px solid rgba(255,255,255,0.08);
}
.trip-card__footer--with-cta { padding-right: 0; }
.trip-card__footer-left { display: block; }
.trip-card__footer span {
    color: rgba(247,239,228,0.64);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.74rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
}
.trip-card__footer strong {
    display: block;
    margin-top: 0.35rem;
    color: #f7efe4;
    font-size: 1rem;
    letter-spacing: 0;
    font-family: 'Inter', sans-serif;
}
.trip-card__distance {
    margin-top: 0.25rem;
    color: rgba(234,125,87,0.92);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    letter-spacing: 0.04em;
}

/* Detail button positioned INSIDE the trip card, aligned with the footer line.
   Targeted via st.container(key="tripcard_N") which adds the .st-key-tripcard_N class. */
[class*="st-key-tripcard_"] {
    position: relative;
}
[class*="st-key-tripcard_"] .trip-card {
    padding-bottom: 1.2rem;
    margin-bottom: 0.95rem;
}
[class*="st-key-tripcard_"] .trip-card__footer--with-cta {
    padding-right: 9rem;
    min-height: 3.2rem;
}
[class*="st-key-tripcard_"] > [data-testid="stElementContainer"]:last-child {
    position: absolute !important;
    bottom: 1.55rem !important;
    right: 1.4rem !important;
    left: auto !important;
    width: auto !important;
    margin: 0 !important;
    padding: 0 !important;
    z-index: 5;
}
[class*="st-key-tripcard_"] .stButton {
    width: auto !important;
    margin: 0 !important;
}
[class*="st-key-tripcard_"] .stButton > button {
    background: linear-gradient(135deg, #ea7d57 0%, #d56b48 100%) !important;
    color: #f7efe4 !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    border-radius: 999px !important;
    padding: 0.45rem 1.1rem !important;
    width: auto !important;
    min-width: 0 !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.04em !important;
    line-height: 1 !important;
    box-shadow: 0 8px 18px rgba(20,30,60,0.35) !important;
    min-height: 0 !important;
    height: auto !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    white-space: nowrap !important;
}
[class*="st-key-tripcard_"] .stButton > button:hover {
    background: linear-gradient(135deg, #f08862 0%, #df7551 100%) !important;
    border-color: rgba(255,255,255,0.35) !important;
    color: #ffffff !important;
}
[class*="st-key-tripcard_"] .stButton > button p {
    color: inherit !important;
    margin: 0 !important;
    font-weight: 600 !important;
    white-space: nowrap !important;
    line-height: 1 !important;
}

.dialog-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    padding: 0.4rem 0 1rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.2rem;
    flex-wrap: nowrap;
}
.dialog-header__id {
    font-family: 'IBM Plex Mono', monospace;
    color: var(--text);
    letter-spacing: 0.14em;
    font-size: 0.95rem;
    font-weight: 600;
    text-transform: uppercase;
    line-height: 1.2;
    flex: 1 1 auto;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.dialog-header__badge {
    background: var(--accent-soft);
    color: var(--accent);
    padding: 0.35rem 0.85rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-family: 'IBM Plex Mono', monospace;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-weight: 600;
    line-height: 1;
    flex: 0 0 auto;
    white-space: nowrap;
}
.dialog-route {
    display: grid;
    grid-template-columns: 1fr 0.9fr 1fr;
    gap: 1rem;
    padding: 1.2rem;
    background: linear-gradient(135deg, #184835 0%, #12372d 100%);
    color: #f7efe4;
    border-radius: 18px;
    margin-bottom: 1.2rem;
}
.dialog-route__col { display: flex; flex-direction: column; gap: 0.35rem; }
.dialog-route__col--center {
    background: rgba(29,42,83,0.55);
    border-radius: 14px;
    padding: 0.85rem;
    align-items: center;
    text-align: center;
    justify-content: center;
}
.dialog-route__col--right { text-align: right; align-items: flex-end; }
.dialog-route__meta {
    font-family: 'IBM Plex Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 0.32em;
    color: rgba(247,239,228,0.6);
    font-size: 0.72rem;
}
.dialog-route__time {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2.8rem;
    line-height: 1;
}
.dialog-route__station {
    font-size: 1.1rem;
    color: #f7efe4;
}
.dialog-route__country {
    color: rgba(247,239,228,0.68);
    font-size: 0.88rem;
}
.dialog-route__duration {
    margin-top: 0.5rem;
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.9rem;
    line-height: 1;
    color: #f7efe4;
}
.dialog-route__line {
    margin-top: 0.35rem;
    color: rgba(247,239,228,0.7);
    font-size: 0.86rem;
}

.dialog-section-title {
    font-family: 'IBM Plex Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 0.28em;
    color: var(--muted);
    font-size: 0.78rem;
    margin: 1.2rem 0 0.7rem;
}
.city-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.85rem;
}
.city-block {
    background: rgba(255,255,255,0.78);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1rem 1.1rem;
}
.city-block__meta {
    font-family: 'IBM Plex Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 0.28em;
    color: var(--muted);
    font-size: 0.7rem;
}
.city-block__name {
    margin-top: 0.4rem;
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.55rem;
    line-height: 1.05;
    color: var(--text);
    margin-bottom: 0.65rem;
}
.city-block__row {
    display: flex;
    justify-content: space-between;
    gap: 0.6rem;
    padding: 0.35rem 0;
    border-top: 1px solid rgba(223,211,194,0.6);
    font-size: 0.92rem;
}
.city-block__row span {
    color: var(--muted);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.74rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
}
.city-block__row strong {
    color: var(--text);
    font-family: 'Inter', sans-serif;
    font-weight: 600;
}

.stop-list {
    list-style: none;
    margin: 0;
    padding: 0.4rem 0 0.6rem;
    position: relative;
}
.stop-list::before {
    content: "";
    position: absolute;
    left: 11px;
    top: 18px;
    bottom: 18px;
    width: 2px;
    background: linear-gradient(180deg, #174936, #ea7d57, #174936);
    opacity: 0.45;
}
.stop-row {
    display: grid;
    grid-template-columns: 28px 1fr;
    gap: 0.85rem;
    padding: 0.65rem 0;
    align-items: flex-start;
    position: relative;
}
.stop-row__bullet {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    margin-top: 0.15rem;
    z-index: 1;
}
.stop-row__bullet span {
    display: block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: #ea7d57;
    box-shadow: 0 0 0 4px var(--bg);
}
.stop-row--depart .stop-row__bullet span,
.stop-row--arrivee .stop-row__bullet span {
    width: 16px;
    height: 16px;
    background: #174936;
    box-shadow: 0 0 0 4px var(--bg), inset 0 0 0 3px #f6f1e8;
}
.stop-row__body {
    background: rgba(255,255,255,0.78);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 0.7rem 0.95rem;
}
.stop-row--depart .stop-row__body,
.stop-row--arrivee .stop-row__body {
    background: rgba(23,73,54,0.07);
    border-color: rgba(23,73,54,0.22);
}
.stop-row__head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.7rem;
}
.stop-row__name {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.25rem;
    color: var(--text);
    line-height: 1.1;
}
.stop-row__kind {
    font-family: 'IBM Plex Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 0.22em;
    font-size: 0.68rem;
    color: var(--muted);
    padding: 0.18rem 0.55rem;
    border-radius: 999px;
    background: rgba(255,255,255,0.7);
    border: 1px solid var(--border);
}
.stop-row--depart .stop-row__kind,
.stop-row--arrivee .stop-row__kind {
    color: var(--green);
    border-color: rgba(23,73,54,0.4);
    background: rgba(23,73,54,0.08);
}
.stop-row__meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.45rem 1.1rem;
    margin-top: 0.45rem;
    color: var(--muted);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
}

@media (max-width: 760px) {
    .dialog-route { grid-template-columns: 1fr; }
    .city-grid { grid-template-columns: 1fr; }
    .stop-row__head { flex-direction: column; align-items: flex-start; }
}

.map-empty {
    min-height: 420px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    border: 1px dashed var(--border);
    border-radius: 20px;
    color: var(--muted);
    text-align: center;
    padding: 2rem;
}
.map-empty strong {
    font-family: 'IBM Plex Mono', monospace;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    font-size: 0.82rem;
}

.endpoint-row {
    display: grid;
    grid-template-columns: 1.3fr auto auto 1fr;
    gap: 1rem;
    align-items: center;
    padding: 0.95rem 0;
    border-bottom: 1px solid rgba(223,211,194,0.7);
}
.endpoint-row:last-child { border-bottom: none; }
.endpoint-row__path {
    font-family: 'IBM Plex Mono', monospace;
    color: var(--green);
}
.pill {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.3rem 0.72rem;
    border-radius: 999px;
    font-size: 0.8rem;
    font-family: 'IBM Plex Mono', monospace;
}
.pill-ok { background: rgba(31,110,78,0.12); color: var(--ok); }
.pill-warn { background: rgba(214,135,64,0.12); color: var(--warn); }
.pill-err { background: rgba(185,77,77,0.12); color: var(--danger); }
.pill-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: currentColor;
}

.stButton > button {
    background: transparent !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 999px !important;
    padding: 0.72rem 1.15rem !important;
    font-weight: 600 !important;
    box-shadow: none !important;
    transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
}
.stButton > button:hover {
    border-color: var(--green) !important;
    color: var(--green) !important;
    background: rgba(255,255,255,0.6) !important;
}
.stButton > button[kind="primary"],
.stButton > button[data-testid*="baseButton-primary"] {
    background: var(--green) !important;
    color: #f7efe4 !important;
    border-color: var(--green) !important;
}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid*="baseButton-primary"]:hover {
    background: var(--green-2) !important;
    border-color: var(--green-2) !important;
    color: #ffffff !important;
}

.stSelectbox label, .stMultiSelect label, .stTextInput label, .stSlider label {
    color: var(--muted) !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.73rem !important;
    letter-spacing: 0.26em !important;
    text-transform: uppercase !important;
}
[data-baseweb="select"] > div,
.stTextInput > div > div {
    border-radius: 14px !important;
    border-color: var(--border) !important;
    background: rgba(255,255,255,0.92) !important;
    min-height: 52px !important;
}
[data-baseweb="select"] > div > div,
[data-baseweb="select"] [data-baseweb="select-control"],
[data-baseweb="select"] [class*="ValueContainer"],
[data-baseweb="select"] [class*="singleValue"],
[data-baseweb="select"] [class*="placeholder"],
[data-baseweb="select"] span,
[data-baseweb="select"] input {
    color: var(--text) !important;
}
[data-baseweb="select"] svg { color: var(--muted) !important; }
[data-baseweb="popover"] li,
[data-baseweb="menu"] li,
[data-baseweb="popover"] [role="option"] {
    color: var(--text) !important;
    background: #fffdfa !important;
}
[data-baseweb="popover"] [role="option"]:hover,
[data-baseweb="menu"] li:hover {
    background: rgba(23,73,54,0.08) !important;
    color: var(--green) !important;
}

div[data-testid="stPlotlyChart"] {
    background: transparent !important;
}
div[data-testid="stPlotlyChart"] > div {
    border-radius: 20px;
    overflow: hidden;
}

.skip-link {
    position: absolute;
    top: -999px;
    left: 0;
    background: var(--green);
    color: #fff;
    padding: 0.5rem 1rem;
    z-index: 9999;
    border-radius: 0 0 8px 0;
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
    text-decoration: none;
}
.skip-link:focus {
    top: 0;
}

@media (max-width: 1100px) {
    .kpi-row { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .trip-hero { grid-template-columns: 1fr; }
}

@media (max-width: 760px) {
    [data-testid="stMainBlockContainer"] { padding: 0 1rem 2rem !important; }
    [data-testid="stHorizontalBlock"]:has(.shell-brand-marker) {
        margin: 0 -1rem 1rem !important;
        padding: 0.7rem 1rem !important;
        flex-wrap: wrap !important;
    }
    .kpi-row { grid-template-columns: 1fr; }
    .endpoint-row { grid-template-columns: 1fr; gap: 0.45rem; }
}
</style>
</div>
""")


PAGES = [
    ("Trajets", ":material/route:"),
    ("Observatoire", ":material/insights:"),
    ("Supervision", ":material/monitor_heart:"),
    ("Simulateur", ":material/bolt:"),
]

if "page" not in st.session_state:
    st.session_state.page = "Trajets"


def render_shell_header() -> None:
    cols = st.columns([2, 1, 1, 1, 1], gap="small")
    with cols[0]:
        train_icon = lucide("train-front", size=22, color="#f7efe4", stroke_width=1.9)
        st.html(f"""
        <div class="shell-brand-marker"></div>
        <div class="brand">
          <div class="brand__icon">{train_icon}</div>
          <div>
            <div class="brand__name">ObRail</div>
            <div class="brand__sub">Europe</div>
          </div>
        </div>
        """)
    active_page = st.session_state.page
    for idx, (label, icon) in enumerate(PAGES, start=1):
        with cols[idx]:
            is_active = label == active_page
            if st.button(
                f"{icon} {label}",
                key=f"nav_{label}",
                width="stretch",
                type="primary" if is_active else "secondary",
            ):
                st.session_state.page = label
                st.rerun()


def page_hero(eyebrow: str, title: str, description: str) -> None:
    st.html(f"""
    <section class="hero">
      <div class="eyebrow">{eyebrow}</div>
      <h1>{title}</h1>
      <p>{description}</p>
    </section>
    """)


ROUTES = {
    "Trajets": (
        "_pages.trajets",
        "Exploration · 01",
        "Trajets",
        "Consultation des dessertes ferroviaires europeennes recensees dans l'entrepot unifie. Filtrez par ville, type de service, operateur ou ligne.",
    ),
    "Observatoire": (
        "_pages.observatoire",
        "Analyse · 02",
        "Observatoire",
        "Vue d'ensemble du reseau ObRail: densite du maillage, poids des operateurs et lecture environnementale du rail europeen.",
    ),
    "Supervision": (
        "_pages.supervision",
        "Observabilite · 03",
        "Supervision",
        "Surveillance en temps reel de l'API ObRail. Une sonde /health est emise toutes les 10 secondes pour suivre la disponibilite et la latence.",
    ),
    "Simulateur": (
        "_pages.simulateur",
        "Machine Learning · 04",
        "Simulateur CO2",
        "Estimez l'empreinte carbone d'un trajet ferroviaire et identifiez son potentiel de substitution avion/train grace aux modeles XGBoost et KMeans entraines sur 400 liaisons europeennes.",
    ),
}


render_shell_header()

module_path, eyebrow, title, description = ROUTES[st.session_state.page]
page_hero(eyebrow, title, description)

page_module = importlib.import_module(module_path)
page_module.render()
