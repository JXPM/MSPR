from typing import List
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.trajet import Trajet
from app.schemas.trajet_schema import TrajetResponse


def get_all_trajets() -> List[TrajetResponse]:

    db: Session = SessionLocal()

    trajets = db.query(Trajet).all()

    db.close()

    return trajets


def get_trajet_by_id(trajet_id: str):

    db: Session = SessionLocal()

    trajet = db.query(Trajet).filter(Trajet.trajet_id == trajet_id).first()

    db.close()

    return trajet