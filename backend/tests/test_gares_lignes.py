import pytest


@pytest.mark.integration
class TestGares:
    def test_returns_200(self, client):
        assert client.get("/gares/").status_code == 200

    def test_returns_all_seeded_gares(self, client):
        data = client.get("/gares/").json()
        assert len(data) == 6

    def test_gare_has_required_fields(self, client):
        gare = client.get("/gares/").json()[0]
        assert "code_uic" in gare
        assert "nom_gare" in gare
        assert "latitude" in gare
        assert "longitude" in gare
        assert "iso_pays" in gare

    def test_gares_have_iso_pays(self, client):
        gares = client.get("/gares/").json()
        iso_codes = {g["iso_pays"] for g in gares}
        assert iso_codes == {"FR", "DE", "IT", "AT"}


@pytest.mark.integration
class TestLignes:
    def test_returns_200(self, client):
        assert client.get("/lignes/").status_code == 200

    def test_returns_all_seeded_lignes(self, client):
        data = client.get("/lignes/").json()
        assert len(data) == 3

    def test_ligne_has_required_fields(self, client):
        ligne = client.get("/lignes/").json()[0]
        assert "id_ligne" in ligne
        assert "nom_ligne" in ligne
        assert "type_service" in ligne
        assert "distance" in ligne

    def test_lignes_type_service_in_jour_nuit(self, client):
        lignes = client.get("/lignes/").json()
        types = {l["type_service"] for l in lignes}
        assert types.issubset({"JOUR", "NUIT", None})

    def test_lignes_distance_is_positive(self, client):
        lignes = client.get("/lignes/").json()
        for ligne in lignes:
            if ligne["distance"] is not None:
                assert ligne["distance"] > 0
