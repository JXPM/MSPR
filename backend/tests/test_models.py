"""
Tests unitaires des modèles SQLAlchemy
=========================================
Vérifie :
  - les clés primaires
  - les relations FK et back_populates (qu'elles tiennent à l'insertion)
  - la possibilité d'instancier chaque modèle
  - les types de colonnes
  - le mapping vers la table attendue

Compétence MSPR : « Construire la structure de stockage des données
                   (modèle de données) qui répond au mieux au besoin d'analyse »
"""
import pytest

from app.models import (
    Pays, Gare, Operateur, Ligne, TypeTrain, Trajet, Itineraire, Emission,
)


@pytest.mark.unit
class TestModelsTableNames:
    """Le nom de table doit correspondre au schéma Postgres réel."""

    def test_pays_table(self):
        assert Pays.__tablename__ == "pays"

    def test_gare_table(self):
        assert Gare.__tablename__ == "gare"

    def test_operateur_table(self):
        assert Operateur.__tablename__ == "operateur"

    def test_ligne_table(self):
        assert Ligne.__tablename__ == "ligne"

    def test_trajet_table(self):
        assert Trajet.__tablename__ == "trajet"

    def test_itineraire_table(self):
        assert Itineraire.__tablename__ == "itineraire"

    def test_emission_table(self):
        assert Emission.__tablename__ == "emission"


@pytest.mark.unit
class TestModelsPrimaryKeys:
    """Les clés primaires doivent être correctement déclarées."""

    def test_pays_pk_iso(self):
        assert Pays.__table__.primary_key.columns.keys() == ["iso_pays"]

    def test_gare_pk_uic(self):
        assert Gare.__table__.primary_key.columns.keys() == ["code_uic"]

    def test_operateur_pk_code(self):
        assert Operateur.__table__.primary_key.columns.keys() == ["code_operateur"]

    def test_ligne_pk_id(self):
        assert Ligne.__table__.primary_key.columns.keys() == ["id_ligne"]

    def test_trajet_pk_id(self):
        assert Trajet.__table__.primary_key.columns.keys() == ["trajet_id"]

    def test_itineraire_composite_pk(self):
        """Itineraire a une clé composite (trajet_id, id_itineraire)."""
        keys = set(Itineraire.__table__.primary_key.columns.keys())
        assert keys == {"trajet_id", "id_itineraire"}


@pytest.mark.unit
class TestModelsRelations:
    """Les relations doivent fonctionner après insertion."""

    def test_pays_has_gares(self, seed_data):
        france = seed_data.query(Pays).filter_by(iso_pays="FR").one()
        gare_names = {g.nom_gare for g in france.gares}
        assert gare_names == {"Paris Nord", "Paris Lyon"}

    def test_pays_has_operateurs(self, seed_data):
        france = seed_data.query(Pays).filter_by(iso_pays="FR").one()
        op_codes = {o.code_operateur for o in france.operateurs}
        assert op_codes == {"SNC"}

    def test_gare_back_to_pays(self, seed_data):
        gare = seed_data.query(Gare).filter_by(code_uic="DEBHF").one()
        assert gare.pays.nom_pays == "Allemagne"

    def test_ligne_has_trajets(self, seed_data):
        ligne = seed_data.query(Ligne).filter_by(id_ligne=1).one()
        trajet_ids = {t.trajet_id for t in ligne.trajets}
        assert trajet_ids == {"SNC-1001", "SNC-1002"}

    def test_trajet_back_to_ligne(self, seed_data):
        trajet = seed_data.query(Trajet).filter_by(trajet_id="OBB-2001").one()
        assert trajet.ligne.type_service == "NUIT"

    def test_itineraire_links_trajet_and_gare(self, seed_data):
        # OBB-2001 dessert 3 gares (Paris Lyon, München, Wien)
        stops = seed_data.query(Itineraire).filter_by(trajet_id="OBB-2001").all()
        assert len(stops) == 3
        for stop in stops:
            assert stop.gare is not None
            assert stop.trajet.trajet_id == "OBB-2001"


@pytest.mark.unit
class TestModelInstantiation:
    """Chaque modèle doit pouvoir être instancié sans erreur."""

    def test_pays(self):
        p = Pays(iso_pays="ES", nom_pays="Espagne")
        assert p.iso_pays == "ES"
        assert p.nom_pays == "Espagne"

    def test_gare_optional_coords(self):
        """Les coordonnées GPS sont optionnelles."""
        g = Gare(code_uic="ESPMD", nom_gare="Madrid Atocha", iso_pays="ES")
        assert g.latitude is None
        assert g.longitude is None

    def test_emission_avec_distances(self):
        e = Emission(
            id_emission=99, transporteur="train",
            distance_train_km=500.0, empreinte_train_kg=2.0,
        )
        assert e.distance_train_km == 500.0
        assert e.empreinte_avion_kg is None
