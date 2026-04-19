from app.database import SessionLocal
from app.models.trajet import Trajet
from app.models.ligne import Ligne
from app.models.gare import Gare


def count_trajets():
    db = SessionLocal()
    count = db.query(Trajet).count()
    db.close()
    return {"total_trajets": count}


def count_lignes():
    db = SessionLocal()
    count = db.query(Ligne).count()
    db.close()
    return {"total_lignes": count}


def count_gares():
    db = SessionLocal()
    count = db.query(Gare).count()
    db.close()
    return {"total_gares": count}