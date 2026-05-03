from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ajout du répertoire backend au PYTHONPATH (pour `from app...`)
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import (  # noqa: E402
    Pays, Gare, Operateur, Ligne, TypeTrain, Trajet, Itineraire, Emission,
)


@pytest.fixture(scope="function")
def db_engine():
    """Crée un engine SQLite en mémoire pour un seul test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Session SQLAlchemy liée à l'engine de test."""
    SessionLocal = sessionmaker(bind=db_engine, autocommit=False, autoflush=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def seed_data(db_session):
    # Pays
    db_session.add_all([
        Pays(iso_pays="FR", nom_pays="France"),
        Pays(iso_pays="DE", nom_pays="Allemagne"),
        Pays(iso_pays="IT", nom_pays="Italie"),
        Pays(iso_pays="AT", nom_pays="Autriche"),
    ])

    # Gares
    db_session.add_all([
        Gare(code_uic="FRPNO", nom_gare="Paris Nord",
             latitude=48.880, longitude=2.355, iso_pays="FR"),
        Gare(code_uic="FRPLY", nom_gare="Paris Lyon",
             latitude=48.844, longitude=2.374, iso_pays="FR"),
        Gare(code_uic="DEBHF", nom_gare="Berlin Hbf",
             latitude=52.525, longitude=13.369, iso_pays="DE"),
        Gare(code_uic="DEMUC", nom_gare="München Hbf",
             latitude=48.140, longitude=11.558, iso_pays="DE"),
        Gare(code_uic="ITMIL", nom_gare="Milano Centrale",
             latitude=45.486, longitude=9.205, iso_pays="IT"),
        Gare(code_uic="ATWIE", nom_gare="Wien Hbf",
             latitude=48.185, longitude=16.376, iso_pays="AT"),
    ])

    # Opérateurs (le code_operateur = 3 caractères uppercase, c'est l'invariant)
    db_session.add_all([
        Operateur(code_operateur="SNC", nom_operateur="SNCF", iso_pays="FR"),
        Operateur(code_operateur="OBB", nom_operateur="ÖBB Nightjet", iso_pays="AT"),
        Operateur(code_operateur="DBA", nom_operateur="Deutsche Bahn", iso_pays="DE"),
    ])

    # Types_train
    db_session.add_all([
        TypeTrain(id_type_train=1, type_nom="Train à Grande Vitesse"),
        TypeTrain(id_type_train=2, type_nom="Nightjet"),
        TypeTrain(id_type_train=3, type_nom="Inter-City Express"),
    ])

    # Lignes — 2 JOUR + 1 NUIT
    db_session.add_all([
        Ligne(id_ligne=1, nom_ligne="Paris–Berlin Day",
              distance=1050.0, type_service="JOUR"),
        Ligne(id_ligne=2, nom_ligne="Paris–Vienne Sleeper",
              distance=1240.0, type_service="NUIT"),
        Ligne(id_ligne=3, nom_ligne="Berlin–Milano",
              distance=1200.0, type_service="JOUR"),
    ])

    # Trajets — code op = 3 premières lettres
    db_session.add_all([
        Trajet(trajet_id="SNC-1001",
               gare_depart="Paris Nord", gare_arrivee="Berlin Hbf",
               heure_depart="08:00:00", heure_arrivee="16:30:00",
               id_ligne=1),
        Trajet(trajet_id="SNC-1002",
               gare_depart="Paris Nord", gare_arrivee="Berlin Hbf",
               heure_depart="14:00:00", heure_arrivee="22:30:00",
               id_ligne=1),
        Trajet(trajet_id="OBB-2001",
               gare_depart="Paris Lyon", gare_arrivee="Wien Hbf",
               heure_depart="20:30:00", heure_arrivee="08:45:00",
               id_ligne=2),
        Trajet(trajet_id="DBA-3001",
               gare_depart="Berlin Hbf", gare_arrivee="Milano Centrale",
               heure_depart="07:45:00", heure_arrivee="18:30:00",
               id_ligne=3),
    ])

    # Itinéraire (chemin = chaîne « gare1 - gare2 - gare3 »)
    db_session.add_all([
        Itineraire(trajet_id="SNC-1001", id_itineraire=1,
                   chemin="Paris Nord - Berlin Hbf",
                   code_uic="FRPNO"),
        Itineraire(trajet_id="SNC-1001", id_itineraire=2,
                   chemin="Paris Nord - Berlin Hbf",
                   code_uic="DEBHF"),
        Itineraire(trajet_id="OBB-2001", id_itineraire=1,
                   chemin="Paris Lyon - München Hbf - Wien Hbf",
                   code_uic="FRPLY"),
        Itineraire(trajet_id="OBB-2001", id_itineraire=2,
                   chemin="Paris Lyon - München Hbf - Wien Hbf",
                   code_uic="DEMUC"),
        Itineraire(trajet_id="OBB-2001", id_itineraire=3,
                   chemin="Paris Lyon - München Hbf - Wien Hbf",
                   code_uic="ATWIE"),
    ])

    # Emission
    db_session.add(Emission(
        id_emission=1, transporteur="train_electrique",
        distance_train_km=1050.0, empreinte_train_kg=4.5,
        distance_route_km=1050.0,
        distance_avion_km=1050.0, empreinte_avion_kg=185.0,
    ))

    db_session.commit()
    return db_session


@pytest.fixture(scope="function")
def client(seed_data, db_engine):
    """
    Client FastAPI qui pointe vers la BDD test grâce à dependency override.
    Note : les services importent SessionLocal directement, donc on patche
    aussi à ce niveau-là.
    """
    SessionLocal = sessionmaker(bind=db_engine, autocommit=False, autoflush=False)

    # Override get_db (utilisé par les routes via Depends)
    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # Patch SessionLocal dans les modules services (utilisé directement)
    import app.services.trajet_service as trajet_svc
    import app.services.gare_service as gare_svc
    import app.services.ligne_service as ligne_svc
    import app.services.stats_service as stats_svc

    original_sessions = {
        "trajet": trajet_svc.SessionLocal,
        "gare": gare_svc.SessionLocal,
        "ligne": ligne_svc.SessionLocal,
        "stats": stats_svc.SessionLocal,
    }
    trajet_svc.SessionLocal = SessionLocal
    gare_svc.SessionLocal = SessionLocal
    ligne_svc.SessionLocal = SessionLocal
    stats_svc.SessionLocal = SessionLocal

    with TestClient(app) as c:
        yield c

    # Restauration
    app.dependency_overrides.clear()
    trajet_svc.SessionLocal = original_sessions["trajet"]
    gare_svc.SessionLocal = original_sessions["gare"]
    ligne_svc.SessionLocal = original_sessions["ligne"]
    stats_svc.SessionLocal = original_sessions["stats"]
