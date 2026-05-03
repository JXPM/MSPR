from typing import List
import unicodedata

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.trajet import Trajet
from app.models.itineraire import Itineraire
from app.models.gare import Gare
from app.schemas.trajet_schema import TrajetResponse


def _fix_mojibake(value: str) -> str:
    """Best-effort fix for latin1→utf8 double-encoding mojibake.

    Many noms_gare et chemin sont stockés avec des séquences comme
    'TimiÈoara' qui correspondent en réalité à 'Timișoara' réinterprété
    via latin-1. On tente la rétro-conversion ; en cas d'échec on retourne
    la chaîne d'origine.
    """
    if not value:
        return value
    try:
        return value.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return value


def _normalize_name(value: str) -> str:
    """Clé de normalisation insensible aux accents/case pour comparer
    deux variantes encodage-foireuses du même nom de gare."""
    if not value:
        return ""
    cleaned = _fix_mojibake(value)
    decomposed = unicodedata.normalize("NFKD", cleaned)
    ascii_only = "".join(c for c in decomposed if not unicodedata.combining(c))
    return ascii_only.casefold().strip()


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


def get_itineraire_by_trajet(trajet_id: str):
    """Liste ordonnée et complète des gares desservies pour un trajet.

    Étapes :
      1. Récupérer la chaîne ``chemin`` (toutes les rows ont la même).
      2. Splitter par " - " pour obtenir la liste ordonnée des gares.
      3. Construire un index normalisé (sans accents, casefold) sur la
         table ``gare`` pour rapprocher les variantes d'encodage entre
         ``itineraire.chemin`` et ``gare.nom_gare``.
      4. Pour chaque arrêt : nettoyer le nom via fix-mojibake et joindre
         le code UIC + lat/lon quand disponibles dans ``gare``.
    """
    db: Session = SessionLocal()
    try:
        first = (
            db.query(Itineraire.chemin)
            .filter(Itineraire.trajet_id == trajet_id)
            .filter(Itineraire.chemin.isnot(None))
            .first()
        )
        if not first or not first.chemin:
            return []

        raw_names = [n.strip() for n in first.chemin.split(" - ") if n and n.strip()]
        if not raw_names:
            return []

        # Index normalisé sur les noms de gare présents en BDD
        all_gares = db.query(Gare).all()
        gare_index = {}
        for g in all_gares:
            key = _normalize_name(g.nom_gare)
            if key and key not in gare_index:
                gare_index[key] = g

        result = []
        prev_key = None
        for ordre, raw in enumerate(raw_names):
            key = _normalize_name(raw)
            if key and key == prev_key:
                continue
            g = gare_index.get(key)
            display_name = _fix_mojibake(raw)
            result.append({
                "ordre": ordre,
                "nom_gare": display_name,
                "code_uic": g.code_uic if g else None,
                "iso_pays": g.iso_pays if g else None,
                "latitude": float(g.latitude) if g and g.latitude is not None else None,
                "longitude": float(g.longitude) if g and g.longitude is not None else None,
            })
            prev_key = key
        return result
    finally:
        db.close()