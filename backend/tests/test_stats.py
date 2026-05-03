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

    def test_returns_jour_nuit_keys(self, client):
        data = client.get("/stats/trajets/type").json()
        assert set(data.keys()) == {"JOUR", "NUIT"}

    def test_jour_count(self, client):
        data = client.get("/stats/trajets/type").json()
        assert data["JOUR"] == 3

    def test_nuit_count(self, client):
        """OBB-2001 (ligne 2 NUIT) = 1."""
        data = client.get("/stats/trajets/type").json()
        assert data["NUIT"] == 1

    def test_total_matches_trajets_count(self, client):
        repartition = client.get("/stats/trajets/type").json()
        total_typed = repartition["JOUR"] + repartition["NUIT"]
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
        data = client.get("/stats/operateurs").json()
        sncf = next((o for o in data if o["operateur"] == "SNCF"), None)
        assert sncf is not None
        assert sncf["trajets"] == 2

    def test_total_par_operateur_matches_trajets(self, client):
        ops = client.get("/stats/operateurs").json()
        total = sum(o["trajets"] for o in ops)
        assert total == 4


@pytest.mark.integration
class TestStatsEmissions:
    def test_returns_train_avion(self, client):
        data = client.get("/stats/emissions").json()
        assert "train" in data
        assert "avion" in data

    def test_train_lower_than_avion(self, client):
        data = client.get("/stats/emissions").json()
        if data["train"] is not None and data["avion"] is not None:
            assert data["train"] < data["avion"]


@pytest.mark.integration
class TestTrajetsMap:
    def test_returns_list(self, client):
        data = client.get("/stats/trajets/map").json()
        assert isinstance(data, list)

    def test_segments_have_coordinates(self, client):
        data = client.get("/stats/trajets/map").json()
        for segment in data:
            assert {"lat_depart", "lon_depart",
                    "lat_arrivee", "lon_arrivee"}.issubset(segment.keys())

    def test_obb_2001_produces_2_segments(self, client):
        data = client.get("/stats/trajets/map").json()
        assert len(data) >= 2

    def test_segments_have_valid_lat_lon(self, client):
        data = client.get("/stats/trajets/map").json()
        for s in data:
            assert -90 <= s["lat_depart"] <= 90
            assert -90 <= s["lat_arrivee"] <= 90
            assert -180 <= s["lon_depart"] <= 180
            assert -180 <= s["lon_arrivee"] <= 180
