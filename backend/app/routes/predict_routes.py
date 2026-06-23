# -*- coding: utf-8 -*-
import json
import logging
import os
import sys
from time import perf_counter
from typing import Callable, Optional

from fastapi import APIRouter, HTTPException

from app import ml_metrics
from app.schemas.predict_schema import (
    ClusterRequest,
    ClusterResponse,
    EmissionsRequest,
    EmissionsResponse,
    PredictFullRequest,
    PredictFullResponse,
)

router = APIRouter(prefix="/predict", tags=["Predictions"])

# Journalisation des predictions : premiere brique du feedback loop MLOps.
# Chaque appel ecrit une ligne JSON (entrees + sortie + latence + statut), ce
# qui permet ensuite de rejouer les predictions face a la valeur reelle pour
# detecter une derive (data drift) et declencher un reentrainement.
logger = logging.getLogger("obrail.predictions")


def _log_prediction(endpoint, status, inputs, latency_s, output=None, error=None):
    """Journalise une prediction sous forme d'une ligne JSON exploitable."""
    record = {
        "event": "prediction",
        "endpoint": endpoint,
        "status": status,
        "inputs": inputs,
        "latency_ms": round(latency_s * 1000, 2),
    }
    if output is not None:
        record["output"] = output
    if error is not None:
        record["error"] = error
    payload = json.dumps(record, ensure_ascii=False, default=str)
    if status == "success":
        logger.info(payload)
    else:
        logger.error(payload)


_MODELS: Optional[dict] = None
_predict_emissions_fn: Optional[Callable] = None
_predict_cluster_fn: Optional[Callable] = None
_LOAD_ERROR: Optional[str] = None

_CLUSTER_DESCRIPTIONS: dict[int, str] = {
    0: "Liaison prioritaire pour la substitution avion vers train. Empreinte CO2 tres faible.",
    1: "Liaison a potentiel modere. Gains environnementaux significatifs possibles.",
    2: "Liaison longue distance. Substitution moins evidente mais des gains restent possibles.",
}


def _load_ml_models() -> None:
    """Charge les modeles ML depuis ml/api/predict.py au demarrage du module.

    Echoue silencieusement si ml/ n'est pas accessible: _MODELS reste None
    et les endpoints renvoient une HTTPException 500 a l'appel.
    """
    global _MODELS, _predict_emissions_fn, _predict_cluster_fn, _LOAD_ERROR

    # Recherche du repertoire racine contenant le package `ml/` en remontant
    # l'arborescence depuis ce fichier. Robuste quel que soit l'agencement :
    # - en local : <repo>/backend/app/routes -> racine = <repo>
    # - en conteneur : /app/app/routes avec ml monte sur /app -> racine = /app
    # Un simple comptage de ".." ne fonctionne pas car la profondeur differe.
    here = os.path.dirname(os.path.abspath(__file__))
    project_root = None
    current = here
    while True:
        if os.path.isfile(os.path.join(current, "ml", "api", "predict.py")):
            project_root = current
            break
        parent = os.path.dirname(current)
        if parent == current:  # racine du systeme de fichiers atteinte
            break
        current = parent

    if project_root is None:
        _LOAD_ERROR = "package ml/ introuvable en remontant depuis " + here
        return
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    try:
        from ml.api.predict import (  # noqa: PLC0415
            load_models,
            predict_cluster,
            predict_emissions,
        )
        _MODELS = load_models()
        _predict_emissions_fn = predict_emissions
        _predict_cluster_fn = predict_cluster
    except Exception as exc:
        _LOAD_ERROR = str(exc)


_load_ml_models()
ml_metrics.set_model_loaded(_MODELS is not None)


def _require_models() -> dict:
    """Retourne les modeles charges ou leve une HTTPException 500."""
    if _MODELS is None:
        detail = f"Modeles ML non disponibles: {_LOAD_ERROR or 'erreur inconnue'}"
        raise HTTPException(status_code=500, detail=detail)
    return _MODELS


@router.post("/emissions", response_model=EmissionsResponse)
def predict_co2_emissions(request: EmissionsRequest) -> EmissionsResponse:
    """Predit l'empreinte CO2 d'un trajet ferroviaire en kg de CO2."""
    models = _require_models()
    inputs = {
        "distance_km": request.distance_km,
        "operateur": request.operateur,
        "type_service": request.type_service,
        "duree_trajet_min": request.duree_trajet_min,
    }
    start = perf_counter()
    try:
        empreinte = _predict_emissions_fn(
            request.distance_km,
            request.operateur,
            request.type_service,
            request.duree_trajet_min,
            models,
        )
        latency = perf_counter() - start
        ml_metrics.predict_latency_seconds.labels(endpoint="emissions").observe(latency)
        ml_metrics.record_emission(
            request.distance_km, request.operateur, request.type_service,
            request.duree_trajet_min, empreinte, models,
        )
        ml_metrics.predict_requests_total.labels(endpoint="emissions", status="success").inc()
        _log_prediction("emissions", "success", inputs, latency,
                        output={"empreinte_train_kg": round(empreinte, 3)})
    except Exception as exc:
        ml_metrics.predict_requests_total.labels(endpoint="emissions", status="error").inc()
        _log_prediction("emissions", "error", inputs, perf_counter() - start, error=str(exc))
        raise HTTPException(status_code=500, detail=f"Erreur de prediction: {exc}")
    return EmissionsResponse(
        empreinte_train_kg=empreinte,
        operateur=request.operateur,
        distance_km=request.distance_km,
        type_service=request.type_service,
    )


@router.post("/cluster", response_model=ClusterResponse)
def predict_substitution_cluster(request: ClusterRequest) -> ClusterResponse:
    """Identifie le profil de substitution avion/train d'un trajet (cluster KMeans)."""
    models = _require_models()
    inputs = {
        "distance_km": request.distance_km,
        "empreinte_train_kg": request.empreinte_train_kg,
        "empreinte_avion_kg": request.empreinte_avion_kg,
        "ratio_co2": request.ratio_co2,
    }
    start = perf_counter()
    try:
        cluster_id, label = _predict_cluster_fn(
            request.distance_km,
            request.empreinte_train_kg,
            request.empreinte_avion_kg,
            request.ratio_co2,
            models,
        )
        latency = perf_counter() - start
        ml_metrics.predict_latency_seconds.labels(endpoint="cluster").observe(latency)
        ml_metrics.record_cluster(cluster_id)
        ml_metrics.predict_requests_total.labels(endpoint="cluster", status="success").inc()
        _log_prediction("cluster", "success", inputs, latency,
                        output={"cluster": cluster_id, "label": label})
    except Exception as exc:
        ml_metrics.predict_requests_total.labels(endpoint="cluster", status="error").inc()
        _log_prediction("cluster", "error", inputs, perf_counter() - start, error=str(exc))
        raise HTTPException(status_code=500, detail=f"Erreur de clustering: {exc}")
    return ClusterResponse(
        cluster=cluster_id,
        label=label,
        description=_CLUSTER_DESCRIPTIONS.get(cluster_id, "Profil non classe."),
    )


@router.post("/full", response_model=PredictFullResponse)
def predict_full(request: PredictFullRequest) -> PredictFullResponse:
    """Calcule l'empreinte CO2 et le cluster de substitution en un seul appel."""
    models = _require_models()
    inputs = {
        "distance_km": request.distance_km,
        "operateur": request.operateur,
        "type_service": request.type_service,
        "duree_trajet_min": request.duree_trajet_min,
    }
    start = perf_counter()
    try:
        empreinte = _predict_emissions_fn(
            request.distance_km,
            request.operateur,
            request.type_service,
            request.duree_trajet_min,
            models,
        )
        # distance_km est valide gt=0 (cf. PredictFullRequest), donc avion > 0
        empreinte_avion = request.distance_km * 0.158
        ratio = empreinte / empreinte_avion
        cluster_id, label = _predict_cluster_fn(
            request.distance_km,
            empreinte,
            empreinte_avion,
            ratio,
            models,
        )
        latency = perf_counter() - start
        ml_metrics.predict_latency_seconds.labels(endpoint="full").observe(latency)
        ml_metrics.record_emission(
            request.distance_km, request.operateur, request.type_service,
            request.duree_trajet_min, empreinte, models,
        )
        ml_metrics.record_cluster(cluster_id)
        ml_metrics.predict_requests_total.labels(endpoint="full", status="success").inc()
        _log_prediction("full", "success", inputs, latency, output={
            "empreinte_train_kg": round(empreinte, 3),
            "cluster": cluster_id,
            "label": label,
        })
    except Exception as exc:
        ml_metrics.predict_requests_total.labels(endpoint="full", status="error").inc()
        _log_prediction("full", "error", inputs, perf_counter() - start, error=str(exc))
        raise HTTPException(status_code=500, detail=f"Erreur de prediction: {exc}")
    return PredictFullResponse(
        empreinte_train_kg=empreinte,
        operateur=request.operateur,
        distance_km=request.distance_km,
        type_service=request.type_service,
        cluster=cluster_id,
        label=label,
        description=_CLUSTER_DESCRIPTIONS.get(cluster_id, "Profil non classe."),
    )
