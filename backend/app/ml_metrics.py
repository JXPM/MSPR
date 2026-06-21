# -*- coding: utf-8 -*-
"""Metriques Prometheus propres au modele ML (supervision MLOps).

Ces metriques completent l'instrumentation generique de l'API
(prometheus-fastapi-instrumentator) en exposant la sante et le comportement
*du modele* : disponibilite, volume et latence des predictions, distribution
des sorties (empreinte/cluster) et des entrees (distance/duree/service) pour
detecter une derive (data drift), et le recours au fallback "operateur inconnu".

Tous les objets s'enregistrent dans le registre Prometheus par defaut, deja
expose sur /metrics par l'instrumentator -> aucun cablage supplementaire.
"""

from prometheus_client import Counter, Gauge, Histogram

# --- Sante du service modele ---------------------------------------------
model_loaded = Gauge(
    "obrail_model_loaded",
    "1 si les modeles ML sont charges en memoire, 0 sinon",
)

predict_requests_total = Counter(
    "obrail_predict_requests_total",
    "Nombre d'appels aux endpoints de prediction",
    ["endpoint", "status"],  # endpoint=emissions|cluster|full, status=success|error
)

predict_latency_seconds = Histogram(
    "obrail_predict_latency_seconds",
    "Latence d'inference du modele (hors I/O HTTP)",
    ["endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5),
)

# --- Sorties du modele (derive des predictions) --------------------------
predict_emission_kg = Histogram(
    "obrail_predict_emission_kg",
    "Distribution de l'empreinte CO2 predite (kg)",
    buckets=(0.5, 1, 2, 5, 10, 15, 20, 25, 30, 40),
)

predict_cluster_total = Counter(
    "obrail_predict_cluster_total",
    "Nombre de predictions par cluster de substitution",
    ["cluster"],  # 0|1|2
)

# --- Entrees du modele (data drift vs distribution d'entrainement) -------
predict_distance_km = Histogram(
    "obrail_predict_distance_km",
    "Distribution des distances demandees (km)",
    buckets=(400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000),
)

predict_duree_min = Histogram(
    "obrail_predict_duree_min",
    "Distribution des durees demandees (min)",
    buckets=(120, 240, 360, 480, 600, 720, 900, 1200, 1500),
)

predict_service_total = Counter(
    "obrail_predict_service_total",
    "Repartition des predictions par type de service",
    ["type_service"],  # JOUR|NUIT
)

# Robustesse : Target Encoding retombe sur la moyenne globale quand l'operateur
# n'a jamais ete vu a l'entrainement -> signal de derive du referentiel operateurs.
predict_unknown_operator_total = Counter(
    "obrail_predict_unknown_operator_total",
    "Nombre de predictions avec un operateur inconnu (fallback moyenne globale)",
)


def set_model_loaded(loaded: bool) -> None:
    model_loaded.set(1 if loaded else 0)


def _operator_is_known(operateur: str, models: dict) -> bool:
    encoding_map = models.get("encoding_map")
    if encoding_map is None:
        return True  # pas d'info -> on ne compte pas a tort un inconnu
    try:
        return operateur in encoding_map.index
    except Exception:
        return True


def record_emission(distance_km, operateur, type_service, duree_trajet_min,
                    empreinte, models) -> None:
    """Enregistre les metriques liees a une prediction d'empreinte."""
    predict_emission_kg.observe(empreinte)
    predict_distance_km.observe(distance_km)
    predict_duree_min.observe(duree_trajet_min)
    predict_service_total.labels(type_service=str(type_service)).inc()
    if not _operator_is_known(operateur, models):
        predict_unknown_operator_total.inc()


def record_cluster(cluster_id: int) -> None:
    predict_cluster_total.labels(cluster=str(cluster_id)).inc()
