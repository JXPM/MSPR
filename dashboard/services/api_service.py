import time
from urllib.parse import quote

import requests

import os

API_URL = os.getenv("API_URL", "http://localhost:8000")
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")

# ──────────────────────────────────────────────────────────
#  Données métier
# ──────────────────────────────────────────────────────────

def get_trajets():
    response = requests.get(f"{API_URL}/trajets", timeout=10)
    return response.json()


def get_trajet_itineraire(trajet_id: str):
    """Liste ordonnée des gares desservies pour un trajet donné."""
    try:
        encoded = quote(trajet_id, safe="")
        response = requests.get(f"{API_URL}/trajets/{encoded}/itineraire", timeout=10)
        if response.status_code != 200:
            return []
        return response.json()
    except Exception:
        return []


def get_gares():
    response = requests.get(f"{API_URL}/gares", timeout=10)
    return response.json()


def get_lignes():
    response = requests.get(f"{API_URL}/lignes", timeout=10)
    return response.json()


# ──────────────────────────────────────────────────────────
#  Statistiques agrégées
# ──────────────────────────────────────────────────────────

def get_trajets_count():
    return requests.get(f"{API_URL}/stats/trajets/count", timeout=10).json()


def get_gares_count():
    return requests.get(f"{API_URL}/stats/gares/count", timeout=10).json()


def get_lignes_count():
    return requests.get(f"{API_URL}/stats/lignes/count", timeout=10).json()


def get_pays_count():
    return requests.get(f"{API_URL}/stats/pays/count", timeout=10).json()


def get_emissions():
    return requests.get(f"{API_URL}/stats/emissions", timeout=10).json()


def get_operateurs():
    response = requests.get(f"{API_URL}/stats/operateurs", timeout=10)
    if response.status_code != 200:
        return []
    try:
        return response.json()
    except Exception:
        return []


def get_trajets_map():
    response = requests.get(f"{API_URL}/stats/trajets/map", timeout=15)
    if response.status_code != 200:
        return []
    return response.json()


def get_trajets_type():
    try:
        response = requests.get(f"{API_URL}/stats/trajets/type", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return {"JOUR": 0, "NUIT": 0}


# ──────────────────────────────────────────────────────────
#  Supervision : ping + mesure de latence
# ──────────────────────────────────────────────────────────

def ping(endpoint: str = "/health", timeout: float = 3.0) -> dict:
    """Sonde un endpoint et retourne {ok, status, latency_ms, error}."""
    url = f"{API_URL}{endpoint}"
    started = time.perf_counter()
    try:
        response = requests.get(url, timeout=timeout)
        latency_ms = (time.perf_counter() - started) * 1000
        return {
            "endpoint": endpoint,
            "url": url,
            "ok": response.status_code == 200,
            "status": response.status_code,
            "latency_ms": round(latency_ms, 1),
            "error": None,
        }
    except requests.exceptions.Timeout:
        return {
            "endpoint": endpoint,
            "url": url,
            "ok": False,
            "status": 0,
            "latency_ms": round((time.perf_counter() - started) * 1000, 1),
            "error": "timeout",
        }
    except Exception as exc:
        return {
            "endpoint": endpoint,
            "url": url,
            "ok": False,
            "status": 0,
            "latency_ms": round((time.perf_counter() - started) * 1000, 1),
            "error": str(exc)[:80],
        }


def get_error_rate() -> dict:
    """Taux d'erreurs 5xx via PromQL."""
    try:
        query = 'sum(rate(http_request_duration_seconds_count{status_code=~"5.."}[5m]))'
        response = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={"query": query},
            timeout=5,
        )
        result = response.json().get("data", {}).get("result", [])
        if result:
            return {"value": float(result[0]["value"][1])}
        return {"value": None}
    except Exception:
        return {"value": None}


def get_api_latency_p95() -> dict:
    """Latence p95 via PromQL."""
    try:
        query = "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))"
        response = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={"query": query},
            timeout=5,
        )
        result = response.json().get("data", {}).get("result", [])
        if result:
            return {"value": float(result[0]["value"][1])}
        return {"value": None}
    except Exception:
        return {"value": None}


SUPERVISED_ENDPOINTS = [
    "/health",
    "/stats/trajets/count",
    "/stats/gares/count",
    "/stats/lignes/count",
    "/stats/pays/count",
    "/stats/emissions",
    "/stats/operateurs",
    "/stats/trajets/type",
]
