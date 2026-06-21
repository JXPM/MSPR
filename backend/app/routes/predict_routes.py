# -*- coding: utf-8 -*-
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
    try:
        start = perf_counter()
        empreinte = _predict_emissions_fn(
            request.distance_km,
            request.operateur,
            request.type_service,
            request.duree_trajet_min,
            models,
        )
        ml_metrics.predict_latency_seconds.labels(endpoint="emissions").observe(perf_counter() - start)
        ml_metrics.record_emission(
            request.distance_km, request.operateur, request.type_service,
            request.duree_trajet_min, empreinte, models,
        )
        ml_metrics.predict_requests_total.labels(endpoint="emissions", status="success").inc()
    except Exception as exc:
        ml_metrics.predict_requests_total.labels(endpoint="emissions", status="error").inc()
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
    try:
        start = perf_counter()
        cluster_id, label = _predict_cluster_fn(
            request.distance_km,
            request.empreinte_train_kg,
            request.empreinte_avion_kg,
            request.ratio_co2,
            models,
        )
        ml_metrics.predict_latency_seconds.labels(endpoint="cluster").observe(perf_counter() - start)
        ml_metrics.record_cluster(cluster_id)
        ml_metrics.predict_requests_total.labels(endpoint="cluster", status="success").inc()
    except Exception as exc:
        ml_metrics.predict_requests_total.labels(endpoint="cluster", status="error").inc()
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
    try:
        start = perf_counter()
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
        ml_metrics.predict_latency_seconds.labels(endpoint="full").observe(perf_counter() - start)
        ml_metrics.record_emission(
            request.distance_km, request.operateur, request.type_service,
            request.duree_trajet_min, empreinte, models,
        )
        ml_metrics.record_cluster(cluster_id)
        ml_metrics.predict_requests_total.labels(endpoint="full", status="success").inc()
    except Exception as exc:
        ml_metrics.predict_requests_total.labels(endpoint="full", status="error").inc()
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
