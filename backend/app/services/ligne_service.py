from typing import List
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.ligne import Ligne


def get_all_lignes() -> List[Ligne]:

    db: Session = SessionLocal()

    lignes = db.query(Ligne).all()

    db.close()

    return lignes
