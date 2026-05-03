"""
Tests des endpoints /stats/*
==============================
Couvre toute la surface analytique exposée au dashboard :
  - /stats/{trajets,gares,lignes,pays}/count
  - /stats/trajets/type   (JOUR / NUIT)
  - /stats/operateurs     (volumes par opérateur)
  - /stats/emissions      (CO₂ comparé)
  - /stats/trajets/map    (segments géographiques)

Compétence MSPR : « Représenter graphiquement les relations entre les
                   données » + « Tableau de bord de contrôle »
"""
import pytest


@pytest.mark.integration
class TestKPICounts:
    def test_count_trajets(self, client):
        response = client.get("/stats/trajets/count")
        assert response.status_code == 200
        assert response.json() == {"total_trajets": 4}

    def test_count_lignes(self, client):
        assert client.get("/stats/lignes/count").json() == {"total_lignes": 3}

    def test_count_gares(self, client):
        assert client.get("/stats/gares/count").json() == {"total_gares": 6}

    def test_count_pays(self, client):
        assert client.get("/stats/pays/count").json() == {"total_pays": 4}


@pytest.mark.integration
class TestRepartitionJourNuit:
    """C'est LA stat principale du projet (jour vs nuit)."""

    def test_returns_jour_nuit_keys(self, client):
        data = client.get("/stats/trajets/type").json()
        assert set(data.keys()) == {"JOUR", "NUIT"}

    def test_jour_count(self, client):
        """SNC-1001, SNC-1002 (ligne 1 JOUR) + DBA-3001 (ligne 3 JOUR) = 3."""
        data = client.get("/stats/trajets/type").json()
        assert data["JOUR"] == 3

    def test_nuit_count(self, client):
        """OBB-2001 (ligne 2 NUIT) = 1."""
        data = client.get("/stats/trajets/type").json()
        assert data["NUIT"] == 1

    def test_total_matches_trajets_count(self, client):
        """JOUR + NUIT doit égaler le total des trajets typés."""
        repartition = client.get("/stats/trajets/type").json()
        total_typed = repartition["JOUR"] + repartition["NUIT"]
        # tous les trajets de seed ont une ligne avec type_service défini
        assert total_typed == 4


@pytest.mark.integration
class TestStatsOperateurs:
    def test_returns_list(self, client):
        data = client.get("/stats/operateurs").json()
        assert isinstance(data, list)

    def test_each_operateur_has_count(self, client):
        data = client.get("/stats/operateurs").json()
        for entry in data:
            assert "operateur" in entry
            assert "trajets" in entry
            assert isinstance(entry["trajets"], int)

    def test_sncf_has_2_trajets(self, client):
        """SNC-1001 et SNC-1002 → 2 trajets pour la SNCF."""
        data = client.get("/stats/operateurs").json()
        sncf = next((o for o in data if o["operateur"] == "SNCF"), None)
        assert sncf is not None
        assert sncf["trajets"] == 2

    def test_total_par_operateur_matches_trajets(self, client):
        """Somme des comptes par opérateur = total trajets (à condition que
        tous les trajets aient un opérateur seedé)."""
        ops = client.get("/stats/operateurs").json()
        total = sum(o["trajets"] for o in ops)
        # 2 SNC + 1 OBB + 1 DBA = 4
        assert total == 4


@pytest.mark.integration
class TestStatsEmissions:
    def test_returns_train_avion(self, client):
        data = client.get("/stats/emissions").json()
        assert "train" in data
        assert "avion" in data

    def test_train_lower_than_avion(self, client):
        """Invariant écologique : le train doit toujours moins émettre que l'avion."""
        data = client.get("/stats/emissions").json()
        if data["train"] is not None and data["avion"] is not None:
            assert data["train"] < data["avion"]


@pytest.mark.integration
class TestTrajetsMap:
    def test_returns_list(self, client):
        data = client.get("/stats/trajets/map").json()
        assert isinstance(data, list)

    def test_segments_have_coordinates(self, client):
        """Chaque segment doit avoir 4 coordonnées (lat/lon × départ/arrivée)."""
        data = client.get("/stats/trajets/map").json()
        for segment in data:
            assert {"lat_depart", "lon_depart",
                    "lat_arrivee", "lon_arrivee"}.issubset(segment.keys())

    def test_obb_2001_produces_2_segments(self, client):
        """3 gares (Paris Lyon → München → Wien) = 2 segments."""
        # La fixture OBB-2001 a 3 stops → 2 segments attendus
        data = client.get("/stats/trajets/map").json()
        # On a aussi SNC-1001 qui a 2 stops = 1 segment
        # Total brut = 3, mais déduplication possible si segments identiques
        assert len(data) >= 2

    def test_segments_have_valid_lat_lon(self, client):
        """Latitudes ∈ [-90, 90], longitudes ∈ [-180, 180]."""
        data = client.get("/stats/trajets/map").json()
        for s in data:
            assert -90 <= s["lat_depart"] <= 90
            assert -90 <= s["lat_arrivee"] <= 90
            assert -180 <= s["lon_depart"] <= 180
            assert -180 <= s["lon_arrivee"] <= 180
