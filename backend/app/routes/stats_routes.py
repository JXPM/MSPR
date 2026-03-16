from fastapi import APIRouter
from sqlalchemy import func
from app.services import stats_service
from app.database import SessionLocal
from app.models.emission import Emission

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("/emissions")
def get_emissions_stats():
    return stats_service.get_emissions_stats()


router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("/trajets/count")
def count_trajets():
    return stats_service.count_trajets()


@router.get("/lignes/count")
def count_lignes():
    return stats_service.count_lignes()


@router.get("/gares/count")
def count_gares():
    return stats_service.count_gares()





@router.get("/top-gares-depart")
def emissions():
    db = SessionLocal()

    result = db.query(
        func.avg(Emission.empreinte_train_kg),
        func.avg(Emission.empreinte_avion_kg)
    ).first()

    db.close()

    return {
        "train": result[0],
        "avion": result[1]
    }

