"""
Tests de qualité des données
==============================
Vérifie les invariants métier sur les données seedées (et qui devraient
tenir aussi sur la production).

Compétence MSPR : « Garantir la fiabilité et la traçabilité des informations
                   collectées » + « Suppression des doublons, gestion des
                   valeurs manquantes »
"""
import pytest


@pytest.mark.quality
class TestInvariantsTrajets:
    def test_no_duplicate_trajet_ids(self, client):
        ids = [t["trajet_id"] for t in client.get("/trajets/").json()]
        assert len(ids) == len(set(ids))

    def test_all_trajets_have_horaires(self, client):
        """Heure départ et arrivée toujours présentes (champs obligatoires)."""
        for t in client.get("/trajets/").json():
            assert t["heure_depart"] is not None
            assert t["heure_arrivee"] is not None

    def test_all_trajets_have_gares(self, client):
        for t in client.get("/trajets/").json():
            assert t["gare_depart"]
            assert t["gare_arrivee"]

    def test_no_circular_trajets(self, client):
        """Un trajet ne peut pas avoir départ = arrivée (sauf cas exceptionnel)."""
        for t in client.get("/trajets/").json():
            assert t["gare_depart"] != t["gare_arrivee"]


@pytest.mark.quality
class TestInvariantsLignes:
    def test_type_service_only_jour_or_nuit(self, client):
        """Le type_service ne peut être que JOUR, NUIT ou null."""
        for ligne in client.get("/lignes/").json():
            ts = ligne["type_service"]
            assert ts in (None, "JOUR", "NUIT"), (
                f"type_service inattendu : {ts!r} sur ligne {ligne['id_ligne']}"
            )


@pytest.mark.quality
class TestInvariantsGares:
    def test_no_duplicate_uic(self, client):
        codes = [g["code_uic"] for g in client.get("/gares/").json()]
        assert len(codes) == len(set(codes))

    def test_iso_pays_format(self, client):
        """ISO 3166-1 alpha-2 (2 caractères majuscules)."""
        for gare in client.get("/gares/").json():
            iso = gare.get("iso_pays")
            if iso is not None:
                assert len(iso) == 2
                assert iso.isupper()

    def test_coordinates_within_europe_bounds(self, client):
        """Toutes les gares seedées sont en Europe (sanity check : lat/lon raisonnables)."""
        for gare in client.get("/gares/").json():
            if gare["latitude"] is not None and gare["longitude"] is not None:
                assert 35 <= gare["latitude"] <= 70
                assert -10 <= gare["longitude"] <= 35
