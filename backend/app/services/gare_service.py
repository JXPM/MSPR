from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.gare import Gare


def get_all_gares():
    db: Session = SessionLocal()
    gares = db.query(Gare).all()
    db.close()
    return gares
