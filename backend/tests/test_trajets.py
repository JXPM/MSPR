"""
Tests des endpoints /trajets/*
=================================
Couvre :
  - GET /trajets/             (liste complète)
  - GET /trajets/{id}         (détail + 404)
  - GET /trajets/{id}/itineraire  (gares ordonnées)

Compétence MSPR : « Endpoints de consultation permettant d'interroger les
                   dessertes ferroviaires selon différents critères »
"""
import pytest


@pytest.mark.integration
class TestTrajetsListe:
    def test_get_all_returns_200(self, client):
        response = client.get("/trajets/")
        assert response.status_code == 200

    def test_get_all_returns_list(self, client):
        response = client.get("/trajets/")
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 4

    def test_trajet_has_required_fields(self, client):
        """Chaque trajet doit respecter le schéma Pydantic TrajetResponse."""
        response = client.get("/trajets/")
        trajet = response.json()[0]
        required_fields = {
            "trajet_id", "id_ligne", "gare_depart", "gare_arrivee",
            "heure_depart", "heure_arrivee",
        }
        assert required_fields.issubset(trajet.keys())

    def test_all_trajet_ids_are_unique(self, client):
        """Pas de doublon de trajet_id."""
        response = client.get("/trajets/")
        ids = [t["trajet_id"] for t in response.json()]
        assert len(ids) == len(set(ids))


@pytest.mark.integration
class TestTrajetDetail:
    def test_get_existing_trajet(self, client):
        response = client.get("/trajets/SNC-1001")
        assert response.status_code == 200
        data = response.json()
        assert data["trajet_id"] == "SNC-1001"
        assert data["gare_depart"] == "Paris Nord"
        assert data["gare_arrivee"] == "Berlin Hbf"

    def test_get_nonexistent_returns_404(self, client):
        response = client.get("/trajets/UNKNOWN-9999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Trajet not found"

    def test_get_trajet_returns_id_ligne(self, client):
        """La FK vers la ligne doit être renvoyée pour permettre la jointure côté front."""
        response = client.get("/trajets/OBB-2001")
        assert response.json()["id_ligne"] == 2


@pytest.mark.integration
class TestTrajetItineraire:
    def test_itineraire_returns_ordered_gares(self, client):
        """OBB-2001 a 3 gares dans l'ordre Paris Lyon → München → Wien."""
        response = client.get("/trajets/OBB-2001/itineraire")
        assert response.status_code == 200
        stops = response.json()
        assert len(stops) == 3

        # L'ordre doit être préservé via id_itineraire / split du chemin
        nom_gares = [s["nom_gare"] for s in stops]
        assert nom_gares == ["Paris Lyon", "München Hbf", "Wien Hbf"]

    def test_itineraire_includes_coordinates(self, client):
        """Les coordonnées GPS sont injectées via la jointure avec gare."""
        response = client.get("/trajets/OBB-2001/itineraire")
        stops = response.json()
        first = stops[0]
        assert "latitude" in first
        assert "longitude" in first
        assert first["latitude"] is not None
        assert first["longitude"] is not None

    def test_itineraire_includes_uic_and_iso(self, client):
        """Code UIC et ISO pays attendus pour chaque arrêt."""
        response = client.get("/trajets/OBB-2001/itineraire")
        stops = response.json()
        for stop in stops:
            assert "code_uic" in stop
            assert "iso_pays" in stop

    def test_itineraire_for_nonexistent_returns_404(self, client):
        response = client.get("/trajets/UNKNOWN-9999/itineraire")
        assert response.status_code == 404

    def test_itineraire_supports_slash_in_id(self, client, seed_data):
        """Le converter `:path` doit accepter les `/` dans le trajet_id (cas réel : 'CFR 78/1743')."""
        from app.models import Trajet, Itineraire
        seed_data.add(Trajet(
            trajet_id="CFR 78/1743",
            gare_depart="Paris Nord", gare_arrivee="Berlin Hbf",
            heure_depart="09:00", heure_arrivee="17:00",
            id_ligne=1,
        ))
        seed_data.add(Itineraire(
            trajet_id="CFR 78/1743", id_itineraire=1,
            chemin="Paris Nord - Berlin Hbf",
            code_uic="FRPNO",
        ))
        seed_data.commit()

        # Le client encode automatiquement les espaces, mais le slash passe en clair
        response = client.get("/trajets/CFR 78/1743/itineraire")
        assert response.status_code == 200
        assert len(response.json()) >= 1
