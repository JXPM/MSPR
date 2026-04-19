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
        .join(
            Trajet,
            func.split_part(Trajet.trajet_id, ' ', 1) == Operateur.code_operateur
        )
        .group_by(Operateur.nom_operateur, Operateur.code_operateur)
        .all()
    )
    return [{"operateur": r[0], "trajets": r[2]} for r in result]


# =========================
# TRAJETS MAP
# =========================

@router.get("/trajets/map")
def trajets_map(db: Session = Depends(get_db)):
    trajet_ids = (
        db.query(Itineraire.trajet_id)
        .distinct()
        .limit(200)
        .all()
    )
    trajet_ids = [t[0] for t in trajet_ids]

    if not trajet_ids:
        return []

    rows = (
        db.query(
            Itineraire.trajet_id,
            Itineraire.id_itineraire,
            Gare.latitude,
            Gare.longitude,
        )
        .join(Gare, Gare.code_uic == Itineraire.code_uic)
        .filter(Itineraire.trajet_id.in_(trajet_ids))
        .filter(Gare.latitude.isnot(None))
        .filter(Gare.longitude.isnot(None))
        .order_by(Itineraire.trajet_id, Itineraire.id_itineraire)
        .all()
    )

    by_trajet = defaultdict(list)
    for trajet_id, order_idx, lat, lon in rows:
        by_trajet[trajet_id].append((order_idx, lat, lon))

    seen = set()
    segments = []

    for trajet_id, stops in by_trajet.items():
        stops.sort(key=lambda x: x[0])
        for i in range(len(stops) - 1):
            _, lat1, lon1 = stops[i]
            _, lat2, lon2 = stops[i + 1]
            key = (round(lat1, 4), round(lon1, 4), round(lat2, 4), round(lon2, 4))
            if key in seen:
                continue
            seen.add(key)
            segments.append({
                "lat_depart":  lat1,
                "lon_depart":  lon1,
                "lat_arrivee": lat2,
                "lon_arrivee": lon2,
            })

    return segments