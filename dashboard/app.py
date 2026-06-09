"""Shell principal du dashboard ObRail Europe."""

import importlib

import streamlit as st


st.set_page_config(
    page_title="ObRail Europe",
    page_icon="assets/obrail-logo.svg",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.html("""
<a href="#main-content" class="skip-link">Aller au contenu principal</a>
<div id="main-content">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root {
    --bg: #f5f7f9;
    --bg-2: #eef1f5;
    --surface: #ffffff;
    --surface-strong: #ffffff;
    --surface-2: #f4f6f9;
    --border: #e6e9ef;
    --border-strong: #d6dbe4;
    --text: #0f1b2d;
    --muted: #5a6b7e;
    --muted-2: #8a98a8;
    --green: #0e7a50;            /* émeraude — accent unique */
    --green-2: #0b6442;
    --green-deep: #0e7a50;
    --green-soft: rgba(14, 122, 80, 0.08);
    --navy: #2d4a8a;
    --navy-soft: rgba(45, 74, 138, 0.08);
    --accent: #c2683a;           /* terracotta sobre — secondaire, parcimonie */
    --accent-soft: rgba(194, 104, 58, 0.10);
    --ok: #0e7a50;
    --warn: #b9740f;
    --danger: #c0392b;
    --shadow: 0 1px 2px rgba(16, 24, 40, 0.04), 0 14px 30px rgba(16, 24, 40, 0.07);
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background:
        radial-gradient(1000px 520px at 100% -10%, rgba(14, 122, 80, 0.05), transparent 55%),
        linear-gradient(180deg, #ffffff 0%, var(--bg) 100%) !important;
    color: var(--text);
    font-family: 'Inter', sans-serif !important;
}
.hero h1, .kpi-value, .info-card__value, .trip-time, .trip-duration,
.trip-card__time, .dialog-route__time, .status-band__title,
.brand__name, .stop-row__name, .city-block__name {
    font-weight: 700 !important;
    letter-spacing: -0.02em;
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
[data-testid="stApp"] { overflow-x: clip; }
[data-testid="stHorizontalBlock"]:has(.shell-brand-marker) {
    position: sticky;
    top: 0;
    z-index: 20;
    width: 100vw !important;
    max-width: 100vw !important;
    margin-left: calc(50% - 50vw) !important;
    margin-right: calc(50% - 50vw) !important;
    margin-top: 0 !important;
    margin-bottom: 1.75rem !important;
    padding: 0.85rem 2.75rem !important;
    background: rgba(255, 255, 255, 0.90) !important;
    backdrop-filter: blur(16px) saturate(120%);
    border-bottom: 1px solid var(--border);
    box-shadow: 0 1px 0 rgba(16, 24, 40, 0.03);
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
    width: 42px;
    height: 42px;
    flex: 0 0 42px;
    border-radius: 12px;
    background: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA0OCA0OCI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjQ4IiByeD0iMTMiIGZpbGw9IiMwZTdhNTAiLz48cGF0aCBkPSJNMjQgMTIuNWMtNSAwLTkgMi4xLTkgNS43VjMwYTQuMiA0LjIgMCAwIDAgNC4yIDQuMmg5LjZBNC4yIDQuMiAwIDAgMCAzMyAzMFYxOC4yYzAtMy42LTQtNS43LTktNS43eiIgZmlsbD0iIzBiNjQ0MiIvPjxwYXRoIGQ9Ik0yNCAxNC40Yy0zLjkgMC03LjEgMS41LTcuMSA0LjN2MS4yaDE0LjJ2LTEuMmMwLTIuOC0zLjItNC4zLTcuMS00LjN6IiBmaWxsPSIjZmZmZmZmIi8+PHJlY3QgeD0iMTYuOSIgeT0iMjIuMSIgd2lkdGg9IjE0LjIiIGhlaWdodD0iNC40IiByeD0iMS41IiBmaWxsPSIjZmZmZmZmIi8+PGNpcmNsZSBjeD0iMjAiIGN5PSIzMC40IiByPSIxLjciIGZpbGw9IiNmZmZmZmYiLz48Y2lyY2xlIGN4PSIyOCIgY3k9IjMwLjQiIHI9IjEuNyIgZmlsbD0iI2ZmZmZmZiIvPjxwYXRoIGQ9Ik0xOSAzMy44bC0yLjEgMy43TTI5IDMzLjhsMi4xIDMuNyIgc3Ryb2tlPSIjZmZmZmZmIiBzdHJva2Utd2lkdGg9IjIuMSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIi8+PC9zdmc+") center / 42px 42px no-repeat;
    filter: drop-shadow(0 6px 14px rgba(14, 122, 80, 0.22));
}
.brand__name {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 800;
    font-size: 1.5rem;
    line-height: 0.95;
    letter-spacing: -0.02em;
    color: var(--text);
}
.brand__sub {
    margin-top: 0.16rem;
    font-size: 0.66rem;
    font-family: 'IBM Plex Mono', monospace;
    letter-spacing: 0.34em;
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
    font-family: 'Plus Jakarta Sans', sans-serif !important;
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
    background: var(--green-soft);
    border: 1px solid rgba(14,122,80,0.22);
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
    width: 150px;
    height: 150px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(14,122,80,0.16), transparent 68%);
}
.kpi-card:hover::after { background: radial-gradient(circle, rgba(14,122,80,0.26), transparent 68%); }
.kpi-icon {
    width: 36px;
    height: 36px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 999px;
    background: rgba(14,122,80,0.10);
    border: 1px solid rgba(14,122,80,0.22);
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
    font-family: 'Plus Jakarta Sans', sans-serif;
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
    position: relative;
    overflow: hidden;
    background: linear-gradient(135deg, #0f8a59 0%, #0b6442 100%);
    color: #f3fbf6;
    border: 1px solid rgba(14,122,80,0.30);
    border-radius: 22px;
    padding: 1.35rem 1.55rem;
    margin-bottom: 1rem;
    box-shadow: 0 18px 40px rgba(14,122,80,0.22);
}
.status-band::before {
    content: "";
    position: absolute;
    inset: 0 auto 0 0;
    width: 4px;
    background: linear-gradient(180deg, #f6c976, rgba(246,201,118,0.35));
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
    font-family: 'Plus Jakarta Sans', sans-serif;
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
    font-family: 'Plus Jakarta Sans', sans-serif;
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
    font-family: 'Plus Jakarta Sans', sans-serif;
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
    background: var(--surface-strong);
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
    font-family: 'Plus Jakarta Sans', sans-serif;
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
    background: var(--surface);
    color: var(--text);
    border: 1px solid var(--border);
    border-left: 4px solid var(--green);
    border-radius: 18px;
    padding: 1.1rem 1.2rem 1rem;
    margin-bottom: 0.95rem;
    box-shadow: var(--shadow);
}
.trip-card__top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.8rem;
}
.trip-card__id {
    font-family: 'IBM Plex Mono', monospace;
    color: var(--muted);
    font-size: 0.78rem;
    letter-spacing: 0.15em;
}
.trip-card__badge {
    background: var(--green-soft);
    border: 1px solid rgba(14,122,80,0.18);
    color: var(--green);
    padding: 0.22rem 0.58rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
}
.trip-card__line {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    gap: 0.8rem;
    align-items: center;
    margin: 1.05rem 0 0.9rem;
}
.trip-card__time {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 2.55rem;
    line-height: 0.9;
}
.trip-card__station {
    margin-top: 0.3rem;
    color: var(--muted);
    font-size: 0.98rem;
}
.trip-card__duration {
    text-align: center;
    color: rgba(246,178,74,0.95);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.9rem;
}
.trip-card__footer {
    display: flex;
    justify-content: space-between;
    gap: 0.8rem;
    padding-top: 0.95rem;
    border-top: 1px solid var(--border);
}
.trip-card__footer--with-cta { padding-right: 0; }
.trip-card__footer-left { display: block; }
.trip-card__footer span {
    color: var(--muted-2);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.74rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
}
.trip-card__footer strong {
    display: block;
    margin-top: 0.35rem;
    color: var(--text);
    font-size: 1rem;
    letter-spacing: 0;
    font-family: 'Inter', sans-serif;
}
.trip-card__distance {
    margin-top: 0.25rem;
    color: rgba(246,178,74,0.92);
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
    background: linear-gradient(135deg, #f6b24a 0%, #d56b48 100%) !important;
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
    font-family: 'Plus Jakarta Sans', sans-serif;
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
    font-family: 'Plus Jakarta Sans', sans-serif;
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
    background: var(--surface-strong);
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
    font-family: 'Plus Jakarta Sans', sans-serif;
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
    border-top: 1px solid var(--border);
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
    background: linear-gradient(180deg, #174936, #f6b24a, #174936);
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
    background: #f6b24a;
    box-shadow: 0 0 0 4px var(--bg);
}
.stop-row--depart .stop-row__bullet span,
.stop-row--arrivee .stop-row__bullet span {
    width: 16px;
    height: 16px;
    background: var(--green);
    box-shadow: 0 0 0 4px var(--surface), inset 0 0 0 3px #ffffff;
}
.stop-row__body {
    background: var(--surface-strong);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 0.7rem 0.95rem;
}
.stop-row--depart .stop-row__body,
.stop-row--arrivee .stop-row__body {
    background: rgba(14,122,80,0.08);
    border-color: rgba(14,122,80,0.28);
}
.stop-row__head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.7rem;
}
.stop-row__name {
    font-family: 'Plus Jakarta Sans', sans-serif;
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
    background: rgba(255,255,255,0.04);
    border: 1px solid var(--border);
}
.stop-row--depart .stop-row__kind,
.stop-row--arrivee .stop-row__kind {
    color: var(--green);
    border-color: rgba(14,122,80,0.4);
    background: rgba(14,122,80,0.10);
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
    border-bottom: 1px solid var(--border);
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
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 999px !important;
    padding: 0.72rem 1.15rem !important;
    font-weight: 600 !important;
    box-shadow: none !important;
    transition: background 0.18s ease, color 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
}
.stButton > button:hover {
    border-color: var(--green) !important;
    color: var(--green) !important;
    background: rgba(14,122,80,0.08) !important;
    box-shadow: 0 0 0 1px rgba(14,122,80,0.25), 0 0 20px rgba(14,122,80,0.12) !important;
}
.stButton > button[kind="primary"],
.stButton > button[data-testid*="baseButton-primary"] {
    background: var(--green) !important;
    color: #ffffff !important;
    border-color: var(--green) !important;
    box-shadow: 0 8px 18px rgba(14,122,80,0.22) !important;
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
    background: var(--surface-strong) !important;
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
/* Les selectbox deviennent des listes déroulantes nettes (pas de curseur ni liseré texte) */
[data-baseweb="select"] input {
    caret-color: transparent !important;
    cursor: pointer !important;
}
[data-baseweb="select"] input:focus,
[data-baseweb="select"] input:focus-visible {
    outline: none !important;
    box-shadow: none !important;
}
[data-baseweb="select"] > div { cursor: pointer !important; }
/* Focus visible reporté proprement sur le conteneur du select (accessibilité) */
[data-baseweb="select"]:focus-within > div {
    border-color: var(--green) !important;
    box-shadow: 0 0 0 3px var(--green-soft) !important;
}
[data-baseweb="popover"] li,
[data-baseweb="menu"] li,
[data-baseweb="popover"] [role="option"] {
    color: var(--text) !important;
    background: #ffffff !important;
}
[data-baseweb="popover"] [role="option"]:hover,
[data-baseweb="menu"] li:hover {
    background: rgba(14,122,80,0.12) !important;
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
    /* Laisse la place à la barre d'onglets fixée en bas */
    [data-testid="stMainBlockContainer"] { padding: 0 1rem calc(72px + env(safe-area-inset-bottom, 0px)) !important; }

    /* Barre du haut : uniquement la marque (les boutons partent en bas) */
    [data-testid="stHorizontalBlock"]:has(.shell-brand-marker) {
        padding: 0.65rem 1rem !important;
        margin-bottom: 1.25rem !important;
        flex-wrap: nowrap !important;
        backdrop-filter: none !important;          /* sinon devient le bloc de référence des enfants fixed */
    }
    [data-testid="stHorizontalBlock"]:has(.shell-brand-marker) [data-testid="stColumn"]:first-child {
        flex: 1 1 auto !important;
    }

    /* Les 3 onglets deviennent une barre fixée en bas, type app mobile */
    [data-testid="stHorizontalBlock"]:has(.shell-brand-marker) [data-testid="stColumn"]:not(:first-child) {
        position: fixed !important;
        bottom: 0 !important;
        height: calc(64px + env(safe-area-inset-bottom, 0px)) !important;
        padding-bottom: env(safe-area-inset-bottom, 0px) !important;
        width: 33.3333% !important;
        min-width: 0 !important;
        max-width: 33.3333% !important;
        flex: 0 0 33.3333% !important;
        z-index: 60 !important;
        margin: 0 !important;
        background: rgba(255, 255, 255, 0.97) !important;
        backdrop-filter: blur(18px) saturate(120%);
        border-top: 1px solid var(--border) !important;
        box-shadow: 0 -2px 16px rgba(16, 24, 40, 0.06) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    [data-testid="stHorizontalBlock"]:has(.shell-brand-marker) [data-testid="stColumn"]:nth-child(2) { left: 0 !important; }
    [data-testid="stHorizontalBlock"]:has(.shell-brand-marker) [data-testid="stColumn"]:nth-child(3) { left: 33.3333% !important; }
    [data-testid="stHorizontalBlock"]:has(.shell-brand-marker) [data-testid="stColumn"]:nth-child(4) { left: 66.6666% !important; }

    /* Boutons d'onglet : pleine surface, sans look "carte" */
    [data-testid="stHorizontalBlock"]:has(.shell-brand-marker) [data-testid="stColumn"]:not(:first-child) .stButton,
    [data-testid="stHorizontalBlock"]:has(.shell-brand-marker) [data-testid="stColumn"]:not(:first-child) .stButton > button {
        height: 100% !important;
        width: 100% !important;
        border: none !important;
        border-radius: 0 !important;
        background: transparent !important;
        box-shadow: none !important;
    }
    [data-testid="stHorizontalBlock"]:has(.shell-brand-marker) [data-testid="stColumn"]:not(:first-child) .stButton > button {
        flex-direction: column !important;
        gap: 0.12rem !important;
        color: var(--muted) !important;
    }
    [data-testid="stHorizontalBlock"]:has(.shell-brand-marker) [data-testid="stColumn"]:not(:first-child) .stButton > button p {
        font-size: 0.68rem !important;
        font-weight: 600 !important;
    }
    /* Onglet actif (primary) : accent vert, sans pastille pleine */
    [data-testid="stHorizontalBlock"]:has(.shell-brand-marker) [data-testid="stColumn"]:not(:first-child) .stButton > button[kind="primary"] {
        background: var(--green-soft) !important;
        color: var(--green) !important;
        box-shadow: inset 0 2px 0 var(--green) !important;
    }
    [data-testid="stHorizontalBlock"]:has(.shell-brand-marker) [data-testid="stColumn"]:not(:first-child) .stButton > button[kind="primary"] p {
        color: var(--green) !important;
    }

    .kpi-row { grid-template-columns: 1fr; }
    .endpoint-row { grid-template-columns: 1fr; gap: 0.45rem; }
}

/* ── Premium polish pass (redesign skill) ───────────────────────── */
html { scroll-behavior: smooth; }

/* Keep main content above the ambient grain layer */
[data-testid="stMainBlockContainer"] { position: relative; z-index: 1; }

/* Subtle film grain to break digital flatness (behind content, non-interactive) */
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    opacity: 0.03;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}

/* Tabular figures so columns of numbers line up like a real data product */
.kpi-value, .info-card__value, .trip-time, .trip-duration,
.trip-card__time, .dialog-route__time, .status-band__title {
    font-variant-numeric: tabular-nums;
    font-feature-settings: "tnum" 1, "lnum" 1;
}

/* Cards come alive: weighted lift + tinted shadow on hover */
.kpi-card, .info-card, .glass-card, .panel {
    transition: transform 0.28s cubic-bezier(0.2, 0.8, 0.2, 1),
                box-shadow 0.28s ease, border-color 0.28s ease;
}
.kpi-card:hover, .info-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 24px 52px rgba(27, 45, 38, 0.16);
}

/* True glass: 1px inner edge highlight simulates refraction */
.glass-card, .panel {
    box-shadow: var(--shadow), inset 0 1px 0 rgba(255, 255, 255, 0.55);
}

/* Honour users who prefer reduced motion (accessibility) */
@media (prefers-reduced-motion: reduce) {
    html { scroll-behavior: auto; }
    .kpi-card, .info-card, .glass-card, .panel { transition: none; }
    .kpi-card:hover, .info-card:hover { transform: none; }
}
</style>
</div>
""")


PAGES = [
    ("Trajets", ":material/route:"),
    ("Observatoire", ":material/insights:"),
    ("Supervision", ":material/monitor_heart:"),
]

if "page" not in st.session_state:
    st.session_state.page = "Trajets"


def render_shell_header() -> None:
    cols = st.columns([4, 1.15, 1.15, 1.15], gap="small")
    with cols[0]:
        st.html("""
        <div class="shell-brand-marker"></div>
        <div class="brand">
          <div class="brand__icon" role="img" aria-label="ObRail"></div>
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
        "Consultation des dessertes ferroviaires européennes recensées dans l'entrepôt unifié. Filtrez par ville, type de service, opérateur ou ligne.",
    ),
    "Observatoire": (
        "_pages.observatoire",
        "Analyse · 02",
        "Observatoire",
        "Vue d'ensemble du réseau ObRail : densité du maillage, poids des opérateurs et lecture environnementale du rail européen.",
    ),
    "Supervision": (
        "_pages.supervision",
        "Observabilité · 03",
        "Supervision",
        "Surveillance en temps réel de l'API ObRail. Une sonde /health est émise toutes les 10 secondes pour suivre la disponibilité et la latence.",
    ),
}


render_shell_header()

module_path, eyebrow, title, description = ROUTES[st.session_state.page]
page_hero(eyebrow, title, description)

page_module = importlib.import_module(module_path)
page_module.render()
