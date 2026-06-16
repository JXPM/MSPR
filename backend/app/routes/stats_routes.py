from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import defaultdict

from app.database import get_db
from app.models.emission import Emission
from app.models.operateur import Operateur
from app.models.trajet import Trajet
from app.models.ligne import Ligne
from app.models.gare import Gare
from app.models.itineraire import Itineraire
from app.services import stats_service


router = APIRouter(prefix="/stats", tags=["Stats"])


# =========================
# KPI COUNTS
# =========================

@router.get("/trajets/count")
def count_trajets():
    return stats_service.count_trajets()


@router.get("/lignes/count")
def count_lignes():
    return stats_service.count_lignes()


@router.get("/gares/count")
def count_gares():
    return stats_service.count_gares()

@router.get("/pays/count")
def count_pays(db: Session = Depends(get_db)):
    from app.models.pays import Pays
    count = db.query(func.count(Pays.iso_pays)).scalar()
    return {"total_pays": count}


@router.get("/trajets/type")
def trajets_by_type(db: Session = Depends(get_db)):
    """Répartition des trajets par type de service (JOUR / NUIT)."""
    result = (
        db.query(Ligne.type_service, func.count(Trajet.trajet_id))
        .join(Trajet, Trajet.id_ligne == Ligne.id_ligne)
        .group_by(Ligne.type_service)
        .all()
    )
    counts = {r[0]: r[1] for r in result if r[0] is not None}
    return {
        "JOUR": counts.get("JOUR", 0),
        "NUIT": counts.get("NUIT", 0),
    }


# =========================
# EMISSIONS STATS
# =========================

@router.get("/emissions")
def emissions_stats(db: Session = Depends(get_db)):
    train = db.query(func.avg(Emission.empreinte_train_kg)).scalar()
    avion = db.query(func.avg(Emission.empreinte_avion_kg)).scalar()
    return {"train": train, "avion": avion}


# =========================
# OPERATEURS STATS
# =========================

@router.get("/operateurs")
def stats_operateurs(db: Session = Depends(get_db)):
    result = (
        db.query(
            Operateur.nom_operateur,
            Operateur.code_operateur,
            func.count(Trajet.trajet_id)
        )
        .outerjoin(
            Trajet,
            func.substring(Trajet.trajet_id, 1, 3) == Operateur.code_operateur
        )
        .group_by(Operateur.nom_operateur, Operateur.code_operateur)
        .all()
    )
    return [{"operateur": r[0], "code_operateur": r[1], "trajets": r[2]} for r in result]


# =========================
# TRAJETS MAP — segments réels via itineraire + gare
# =========================

@router.get("/trajets/map")
def trajets_map(db: Session = Depends(get_db)):
    """
    Construit les segments entre gares consécutives en utilisant :
      - itineraire.trajet_id + itineraire.id_itineraire  (ordre des gares)
      - itineraire.code_uic → gare.code_uic              (coordonnées)

    Stratégie :
      1. On prend un échantillon de trajets distincts (limite 200)
      2. On charge tous leurs arrêts avec lat/lon, triés par id_itineraire
      3. On construit les segments gare[i] → gare[i+1]
      4. On déduplique les segments identiques (même réseau = même tronçon)
    """

    # -- Étape 1 : sélectionner un sous-ensemble de trajets distincts --------
    trajet_ids = (
        db.query(Itineraire.trajet_id)
        .distinct()
        .limit(200)
        .all()
    )
    trajet_ids = [t[0] for t in trajet_ids]

    if not trajet_ids:
        return []

    # -- Étape 2 : récupérer tous les arrêts avec coordonnées ----------------
    rows = (
        db.query(
            Itineraire.trajet_id,
            Itineraire.id_itineraire,
            Gare.latitude,
            Gare.longitude,
            Gare.nom_gare,
        )
        .join(Gare, Gare.code_uic == Itineraire.code_uic)
        .filter(Itineraire.trajet_id.in_(trajet_ids))
        .filter(Gare.latitude.isnot(None))
        .filter(Gare.longitude.isnot(None))
        .order_by(Itineraire.trajet_id, Itineraire.id_itineraire)
        .all()
    )

    # -- Étape 3 : regrouper par trajet et construire les segments ------------
    by_trajet = defaultdict(list)
    for trajet_id, order_idx, lat, lon, nom in rows:
        by_trajet[trajet_id].append((order_idx, lat, lon, nom))

    seen = set()
    segments = []

    for trajet_id, stops in by_trajet.items():
        # Trier par id_itineraire (déjà fait en SQL mais on s'assure)
        stops.sort(key=lambda x: x[0])

        for i in range(len(stops) - 1):
            _, lat1, lon1, nom1 = stops[i]
            _, lat2, lon2, nom2 = stops[i + 1]

            # Déduplique les tronçons identiques (même segment dans trajets différents)
            key = (round(lat1, 4), round(lon1, 4), round(lat2, 4), round(lon2, 4))
            if key in seen:
                continue
            seen.add(key)

            segments.append({
                "lat_depart":  lat1,
                "lon_depart":  lon1,
                "lat_arrivee": lat2,
                "lon_arrivee": lon2,
                "nom_depart":  nom1,
                "nom_arrivee": nom2,
            })

    return segments
