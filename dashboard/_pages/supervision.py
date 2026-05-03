"""Maquette premium de la page Supervision."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

from components.charts import latency_chart
from services.api_service import API_URL, SUPERVISED_ENDPOINTS, ping

try:
    from streamlit_autorefresh import st_autorefresh

    _HAS_AUTOREFRESH = True
except ImportError:
    _HAS_AUTOREFRESH = False


REFRESH_SECONDS = 10
HISTORY_MAX = 60


def _autorefresh(seconds: int) -> None:
    if _HAS_AUTOREFRESH:
        st_autorefresh(interval=seconds * 1000, key="supervision_tick")
    else:
        import streamlit.components.v1 as components

        components.html(f'<meta http-equiv="refresh" content="{seconds}">', height=0)


def _kpi(label: str, value: str, hint: str = "", tone: str = "default") -> str:
    bg = {
        "default": "rgba(255,255,255,0.82)",
        "success": "linear-gradient(135deg, #174936 0%, #12372d 100%)",
        "warning": "linear-gradient(135deg, #b47343 0%, #91562c 100%)",
        "danger": "linear-gradient(135deg, #8d4040 0%, #6a2d2d 100%)",
    }[tone]
    color = "#f7efe4" if tone != "default" else "#143d35"
    sub = "rgba(247,239,228,0.72)" if tone != "default" else "#6d877f"
    label_color = "rgba(247,239,228,0.72)" if tone != "default" else "#6d877f"
    border = "transparent" if tone != "default" else "#dfd3c2"
    return f"""
    <div class="kpi-card" style="background:{bg}; color:{color}; border-color:{border};">
      <div class="kpi-label" style="color:{label_color};">{label}</div>
      <div class="kpi-value" style="color:{color};">{value}</div>
      <div class="kpi-hint" style="color:{sub};">{hint}</div>
    </div>
    """


def _status_pill(probe: dict[str, Any]) -> str:
    if probe["ok"]:
        label = f"{probe['status']} OK"
        klass = "pill-ok"
    elif probe["error"] == "timeout":
        label = "TIMEOUT"
        klass = "pill-warn"
    else:
        label = f"{probe['status']} ERR"
        klass = "pill-err"
    return f'<span class="pill {klass}"><span class="pill-dot"></span>{label}</span>'


def render() -> None:
    _autorefresh(REFRESH_SECONDS)

    if "supervision_history" not in st.session_state:
        st.session_state.supervision_history = []

    now = datetime.now()
    probes = [ping(endpoint) for endpoint in SUPERVISED_ENDPOINTS]
    health_probe = next((probe for probe in probes if probe["endpoint"] == "/health"), probes[0])

    st.session_state.supervision_history.append(
        {"ts": now, "latency_ms": health_probe["latency_ms"], "ok": health_probe["ok"]}
    )
    st.session_state.supervision_history = st.session_state.supervision_history[-HISTORY_MAX:]
    history = st.session_state.supervision_history

    total = len(probes)
    ok_count = sum(1 for probe in probes if probe["ok"])
    availability = round(ok_count / total * 100, 1) if total else 0
    average_latency = round(sum(probe["latency_ms"] for probe in probes if probe["ok"]) / max(ok_count, 1))
    errors = total - ok_count
    rolling = round(sum(1 for sample in history if sample["ok"]) / max(len(history), 1) * 100, 1)

    if availability == 100:
        title = "Operationnel"
        subtitle = f"Derniere sonde : {now:%H:%M:%S} — {health_probe['latency_ms']:.0f} ms"
        tone = "success"
    elif availability >= 50:
        title = "Degradation partielle"
        subtitle = f"{errors} endpoint(s) en echec au dernier cycle"
        tone = "warning"
    else:
        title = "Incident en cours"
        subtitle = f"{errors} endpoint(s) indisponibles sur {total}"
        tone = "danger"

    st.html(f"""
<section class="status-band">
  <div class="status-band__eyebrow">API backend</div>
  <div class="status-band__title">{title}</div>
  <div class="status-band__hint">{subtitle}</div>
</section>
""")

    st.html(f"""
<div class="kpi-row">
  {_kpi("Disponibilite", f"{availability}%", f"{ok_count}/{total} endpoints OK", tone)}
  {_kpi("Latence moyenne", f"{average_latency} ms", "Moyenne des endpoints sains")}
  {_kpi("Erreurs", str(errors), "Sur la fenetre du dernier sondage")}
  {_kpi("Sondes collectees", str(len(history)), "Historique glissant sur 60 points")}
</div>
""")

    col_a, col_b = st.columns([1, 1], gap="large")
    with col_a:
        st.html('<div class="section-title"><div class="section-title__label">Temps de reponse</div><div class="section-title__meta">Latence /health</div></div>')
        st.plotly_chart(
            latency_chart(history),
            width="stretch",
            config={"displayModeBar": False},
        )

    with col_b:
        st.html('<div class="section-title"><div class="section-title__label">Historique</div><div class="section-title__meta">Disponibilite recente</div></div>')
        bars = []
        recent = history[-40:] if history else []
        for sample in recent:
            color = "#174936" if sample["ok"] else "#b94d4d"
            bars.append(
                f'<div style="width:12px;height:34px;border-radius:6px;background:{color};opacity:0.92;"></div>'
            )
        if not bars:
            bars = ['<div style="color:#6d877f;">Aucune sonde disponible.</div>']
        st.html(f"""
<div class="panel">
  <div style="display:flex; gap:6px; align-items:flex-end; min-height:58px;">{''.join(bars)}</div>
  <div style="display:flex; justify-content:space-between; margin-top:1rem; color:#6d877f;">
    <span>Plus anciennes</span>
    <span>Plus recentes →</span>
  </div>
  <div style="margin-top:1rem; color:#6d877f;">
    Disponibilite glissante : <strong style="color:#143d35;">{rolling}%</strong>
  </div>
</div>
""")

    st.html('<div class="section-title"><div class="section-title__label">Points de contact</div><div class="section-title__meta">Verification automatique toutes les 10 secondes</div></div>')

    rows = []
    for probe in probes:
        latency = f"{probe['latency_ms']:.0f} ms" if probe["latency_ms"] else "—"
        error = probe["error"] or "Aucune"
        rows.append(
            f"""<div class="endpoint-row">
  <div>
    <div style="font-weight:700;color:#143d35;">{probe['endpoint'].replace('/stats/', '').strip('/') or 'health'}</div>
    <div class="endpoint-row__path">GET {probe['endpoint']}</div>
  </div>
  <div>{_status_pill(probe)}</div>
  <div style="justify-self:end; color:#143d35; font-family:'IBM Plex Mono', monospace;">{latency}</div>
  <div style="color:#6d877f;">{error}</div>
</div>
"""
        )

    st.html(f"""
<div class="panel">
  <div style="margin-bottom:0.85rem; color:#6d877f;">Base surveillee : <strong style="color:#143d35;">{API_URL}</strong></div>
  {''.join(rows)}
</div>
""")
