# -*- coding: utf-8 -*-
"""Tests unitaires de la page Simulateur CO2 (dashboard/_pages/simulateur.py).

Couvre la logique métier pure (Haversine, estimation de cluster, profils CO2),
la génération HTML des cartes et — surtout — la non-régression du fix anti-cache :
un échec transitoire de l'API ne doit jamais être mis en cache (il doit lever une
exception, que st.cache_data ne mémorise pas), afin que le « Segments non
disponibles » se répare tout seul au rendu suivant au lieu de rester figé 1h.
"""
from unittest.mock import patch

import pytest

from _pages import simulateur


# ──────────────────────────────────────────────────────────
#  Haversine
# ──────────────────────────────────────────────────────────
@pytest.mark.unit
class TestHaversine:
    def test_paris_lyon_distance_realiste(self):
        # Paris (48.8566, 2.3522) -> Lyon (45.7640, 4.8357) ≈ 390 km à vol d'oiseau
        d = simulateur._haversine(48.8566, 2.3522, 45.7640, 4.8357)
        assert 380 <= d <= 400

    def test_distance_nulle_pour_meme_point(self):
        assert simulateur._haversine(46.18, 21.32, 46.18, 21.32) == pytest.approx(0.0, abs=1e-6)

    def test_symetrie(self):
        aller = simulateur._haversine(48.85, 2.35, 45.76, 4.83)
        retour = simulateur._haversine(45.76, 4.83, 48.85, 2.35)
        assert aller == pytest.approx(retour, rel=1e-9)

    def test_retourne_float_positif(self):
        d = simulateur._haversine(40.0, 0.0, 50.0, 10.0)
        assert isinstance(d, float)
        assert d > 0


# ──────────────────────────────────────────────────────────
#  Estimation de cluster (heuristique KMeans par distance)
# ──────────────────────────────────────────────────────────
@pytest.mark.unit
class TestEstimateCluster:
    @pytest.mark.parametrize(
        "distance,attendu",
        [
            (0, 0),
            (599.9, 0),
            (600, 1),
            (800, 1),
            (1099.9, 1),
            (1100, 2),
            (3000, 2),
        ],
    )
    def test_bornes_clusters(self, distance, attendu):
        assert simulateur._estimate_cluster(distance) == attendu

    def test_retourne_entier(self):
        assert isinstance(simulateur._estimate_cluster(450), int)


# ──────────────────────────────────────────────────────────
#  Cohérence des tables de constantes des clusters
# ──────────────────────────────────────────────────────────
@pytest.mark.unit
class TestClusterConstants:
    def test_toutes_les_tables_couvrent_les_trois_clusters(self):
        attendu = {0, 1, 2}
        assert set(simulateur._CLUSTER_LABELS) == attendu
        assert set(simulateur._CLUSTER_COLORS) == attendu
        assert set(simulateur._CLUSTER_NAMES) == attendu

    def test_facteurs_emission_coherents(self):
        # Le train doit emettre nettement moins au km que la croisiere avion,
        # et l'avion doit porter un surcout fixe (LTO) strictement positif.
        assert 0 < simulateur._TRAIN_PER_KM < simulateur._AVION_PER_KM
        assert simulateur._AVION_LTO_KG > 0

    def test_estimate_cluster_renvoie_toujours_une_cle_connue(self):
        for distance in (10, 600, 1100, 5000):
            cluster = simulateur._estimate_cluster(distance)
            assert cluster in simulateur._CLUSTER_LABELS


# ──────────────────────────────────────────────────────────
#  _load_segments_with_clusters — NON-RÉGRESSION FIX ANTI-CACHE
# ──────────────────────────────────────────────────────────
@pytest.mark.unit
class TestLoadSegmentsWithClusters:
    def test_leve_si_api_vide(self):
        """Régression : un résultat vide doit LEVER (pour ne pas être mis en cache),
        pas renvoyer []. C'est ce qui évite le 'Segments non disponibles' figé 1h."""
        with patch("_pages.simulateur.get_trajets_map", return_value=[]):
            with pytest.raises(Exception):
                simulateur._load_segments_with_clusters()

    def test_enrichit_les_segments_valides(self):
        seg = {
            "lat_depart": 48.8566, "lon_depart": 2.3522,
            "lat_arrivee": 45.7640, "lon_arrivee": 4.8357,
            "nom_depart": "Paris", "nom_arrivee": "Lyon",
        }
        with patch("_pages.simulateur.get_trajets_map", return_value=[seg]):
            result = simulateur._load_segments_with_clusters()
        assert len(result) == 1
        enriched = result[0]
        # champs ajoutés par l'enrichissement
        for champ in ("cluster", "distance_km", "empreinte_train_kg",
                      "empreinte_avion_kg", "economie_pct", "label"):
            assert champ in enriched
        # données d'origine préservées
        assert enriched["nom_depart"] == "Paris"
        # cluster cohérent avec la distance Paris-Lyon (~390 km -> cluster 0)
        assert enriched["cluster"] == 0
        assert 380 <= enriched["distance_km"] <= 400

    def test_train_emet_moins_que_avion(self):
        seg = {
            "lat_depart": 48.8566, "lon_depart": 2.3522,
            "lat_arrivee": 45.7640, "lon_arrivee": 4.8357,
            "nom_depart": "Paris", "nom_arrivee": "Lyon",
        }
        with patch("_pages.simulateur.get_trajets_map", return_value=[seg]):
            enriched = simulateur._load_segments_with_clusters()[0]
        assert enriched["empreinte_train_kg"] < enriched["empreinte_avion_kg"]
        assert 0 < enriched["economie_pct"] <= 100

    def test_ignore_les_segments_de_distance_nulle(self):
        """Régression fix #1 : un segment dont le départ == l'arrivée (0 km, ex.
        Bratislava hl.st. -> Bratislava hl.st.) ne doit PAS apparaître : 0 km =
        aucune émission, donc aucune économie CO2 à afficher."""
        boucle = {
            "lat_depart": 48.1486, "lon_depart": 17.1077,
            "lat_arrivee": 48.1486, "lon_arrivee": 17.1077,
            "nom_depart": "Bratislava hl.st.", "nom_arrivee": "Bratislava hl.st.",
        }
        with patch("_pages.simulateur.get_trajets_map", return_value=[boucle]):
            result = simulateur._load_segments_with_clusters()
        assert result == []

    def test_economie_varie_avec_la_distance(self):
        """Régression fix #2 : l'économie CO2 ne doit plus être figée à 3 valeurs
        par cluster. Deux trajets de longueurs différentes doivent afficher des
        économies différentes, et un trajet plus court doit économiser DAVANTAGE
        (le surcoût fixe LTO de l'avion pèse plus lourd sur les courts trajets)."""
        court = {
            "lat_depart": 46.18, "lon_depart": 21.31,   # Arad
            "lat_arrivee": 46.17, "lon_arrivee": 21.58,  # Curtici (~17 km)
            "nom_depart": "Arad", "nom_arrivee": "Curtici",
        }
        long = {
            "lat_depart": 48.8566, "lon_depart": 2.3522,   # Paris
            "lat_arrivee": 45.7640, "lon_arrivee": 4.8357,  # Lyon (~390 km)
            "nom_depart": "Paris", "nom_arrivee": "Lyon",
        }
        with patch("_pages.simulateur.get_trajets_map", return_value=[court, long]):
            result = simulateur._load_segments_with_clusters()
        eco = {s["nom_arrivee"]: s["economie_pct"] for s in result}
        assert eco["Curtici"] != eco["Lyon"]
        assert eco["Curtici"] > eco["Lyon"]

    def test_ignore_les_segments_malformes_sans_planter(self):
        bon = {
            "lat_depart": 48.85, "lon_depart": 2.35,
            "lat_arrivee": 45.76, "lon_arrivee": 4.83,
            "nom_depart": "Paris", "nom_arrivee": "Lyon",
        }
        mauvais = {"nom_depart": "X"}  # coordonnées manquantes
        with patch("_pages.simulateur.get_trajets_map", return_value=[mauvais, bon]):
            result = simulateur._load_segments_with_clusters()
        # le mauvais segment est ignoré, le bon est conservé
        assert len(result) == 1
        assert result[0]["nom_depart"] == "Paris"


# ──────────────────────────────────────────────────────────
#  _load_operateurs — même garde-fou anti-cache
# ──────────────────────────────────────────────────────────
@pytest.mark.unit
class TestLoadOperateurs:
    def test_leve_si_api_vide(self):
        with patch("_pages.simulateur.get_operateurs", return_value=[]):
            with pytest.raises(Exception):
                simulateur._load_operateurs()

    def test_trie_et_dedoublonne(self):
        data = [
            {"operateur": "SNCF"},
            {"operateur": "OBB Nightjet"},
            {"operateur": "SNCF"},
            {"operateur": "Deutsche Bahn"},
        ]
        with patch("_pages.simulateur.get_operateurs", return_value=data):
            result = simulateur._load_operateurs()
        assert result == ["Deutsche Bahn", "OBB Nightjet", "SNCF"]

    def test_filtre_operateurs_vides(self):
        data = [{"operateur": "SNCF"}, {"operateur": ""}, {"operateur": None}, {}]
        with patch("_pages.simulateur.get_operateurs", return_value=data):
            result = simulateur._load_operateurs()
        assert result == ["SNCF"]


# ──────────────────────────────────────────────────────────
#  Génération HTML des cartes de résultat
# ──────────────────────────────────────────────────────────
@pytest.mark.unit
class TestResultCardsHtml:
    def test_contient_empreinte_et_distance(self):
        result = {"empreinte_train_kg": 10.08, "distance_km": 450}
        html = simulateur._result_cards_html(result)
        assert "10.08" in html
        assert "450" in html
        assert "kg CO2" in html

    def test_gere_distance_nulle_sans_division_par_zero(self):
        result = {"empreinte_train_kg": 0.0, "distance_km": 0}
        # ne doit pas lever ZeroDivisionError
        html = simulateur._result_cards_html(result)
        assert isinstance(html, str) and html


@pytest.mark.unit
class TestClusterCardHtml:
    def test_affiche_label_et_cluster(self):
        result = {"cluster": 1, "label": "Potentiel modere", "description": "desc test"}
        html = simulateur._cluster_card_html(result)
        assert "Potentiel modere" in html
        assert "Cluster 1" in html
        assert "desc test" in html

    def test_valeurs_par_defaut_si_champs_manquants(self):
        html = simulateur._cluster_card_html({})
        assert "Cluster -1" in html
        assert "Inconnu" in html
