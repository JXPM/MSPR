from app.database import SessionLocal
from app.models.trajet import Trajet
from app.models.ligne import Ligne
from app.models.gare import Gare


def count_trajets():
    db = SessionLocal()
    try:
        return {"total_trajets": db.query(Trajet).count()}
    finally:
        db.close()


def count_lignes():
    db = SessionLocal()
    try:
        return {"total_lignes": db.query(Ligne).count()}
    finally:
        db.close()


def count_gares():
    db = SessionLocal()
    try:
        return {"total_gares": db.query(Gare).count()}
    finally:
        db.close()
