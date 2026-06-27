#!/usr/bin/env python3
"""
generate_predictions.py - Generateur de trafic de predictions ObRail Europe

Envoie une serie de requetes realistes vers les endpoints /predict du backend
afin d'alimenter les metriques de supervision du modele (obrail_predict_*) qui
remontent vers Grafana Cloud via Alloy.

Aucune dependance externe : utilise uniquement la bibliotheque standard.

Usage :
    python ml/scripts/generate_predictions.py                 # 60 iterations sur la prod
    python ml/scripts/generate_predictions.py -n 200          # 200 iterations
    python ml/scripts/generate_predictions.py --delay 0.5     # 0.5 s entre chaque tour
    BASE_URL=http://localhost:8000 python ml/scripts/generate_predictions.py

Variable d'environnement :
    BASE_URL   URL de base du backend (defaut : https://obrail-backend.onrender.com)
"""

import argparse
import json
import os
import random
import sys
import time
import urllib.error
import urllib.request

# random_state=42 : reproductibilite, conformement aux regles du projet.
random.seed(42)

DEFAULT_BASE_URL = "https://obrail-backend.onrender.com"

# Operateurs reellement presents dans le dataset (cf. CLAUDE.md). Les inconnus
# du target encoding retombent sur la moyenne globale cote modele, sans erreur.
OPERATEURS = [
    "ATC", "BDZ", "CD", "CFM", "CFR", "CS", "ES", "FS", "GA", "GWR",
    "HZPP", "MAV", "MT", "OBB", "OTE", "PKP", "RDC", "RJ", "UZ",
]

# Le dataset est 100% NUIT ; on garde une majorite NUIT et un peu de JOUR
# pour exercer aussi cette branche du modele sans biaiser les panels.
TYPES_SERVICE = ["NUIT"] * 5 + ["JOUR"]

# Facteur d'emission avion moyen utilise par l'endpoint /predict/full.
FACTEUR_AVION_KG_PAR_KM = 0.158


def _post(base_url: str, path: str, payload: dict, timeout: float = 30.0):
    """POST JSON et retourne (status_code, corps_decode_ou_texte)."""
    url = base_url.rstrip("/") + path
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace")
    except urllib.error.URLError as exc:
        return None, str(exc.reason)


def _random_trajet() -> dict:
    """Genere des caracteristiques de trajet plausibles."""
    distance_km = round(random.uniform(120, 1600), 1)
    operateur = random.choice(OPERATEURS)
    type_service = random.choice(TYPES_SERVICE)
    # ~ vitesse commerciale 70-110 km/h -> duree en minutes.
    vitesse = random.uniform(70, 110)
    duree_trajet_min = round(distance_km / vitesse * 60, 1)
    return {
        "distance_km": distance_km,
        "operateur": operateur,
        "type_service": type_service,
        "duree_trajet_min": duree_trajet_min,
    }


def run(base_url: str, iterations: int, delay: float) -> int:
    print(f"Cible        : {base_url}")
    print(f"Iterations   : {iterations}  (delai {delay}s entre chaque tour)")
    print("-" * 60)

    ok = 0
    errors = 0

    for i in range(1, iterations + 1):
        trajet = _random_trajet()

        # 1) /predict/emissions
        status, body = _post(base_url, "/predict/emissions", trajet)
        if status == 200:
            ok += 1
            empreinte = body.get("empreinte_train_kg", 0.0)
        else:
            errors += 1
            empreinte = None
            print(f"  [emissions] echec status={status} : {str(body)[:120]}")

        # 2) /predict/full (emissions + cluster en un appel)
        status_f, body_f = _post(base_url, "/predict/full", trajet)
        if status_f == 200:
            ok += 1
            cluster = body_f.get("cluster")
        else:
            errors += 1
            cluster = None
            print(f"  [full]      echec status={status_f} : {str(body_f)[:120]}")

        # 3) /predict/cluster (avec des empreintes derivees coherentes)
        empreinte_train = empreinte if empreinte else round(trajet["distance_km"] * 0.02, 3)
        empreinte_avion = round(trajet["distance_km"] * FACTEUR_AVION_KG_PAR_KM, 3)
        ratio = round(empreinte_train / empreinte_avion, 4) if empreinte_avion else 0.1
        cluster_payload = {
            "distance_km": trajet["distance_km"],
            "empreinte_train_kg": max(empreinte_train, 0.001),
            "empreinte_avion_kg": max(empreinte_avion, 0.001),
            "ratio_co2": max(ratio, 0.0001),
        }
        status_c, body_c = _post(base_url, "/predict/cluster", cluster_payload)
        if status_c == 200:
            ok += 1
        else:
            errors += 1
            print(f"  [cluster]   echec status={status_c} : {str(body_c)[:120]}")

        if i % 10 == 0 or i == iterations:
            emp_txt = f"{empreinte:.1f} kg" if empreinte is not None else "n/a"
            print(
                f"  {i:>4}/{iterations}  {trajet['operateur']:<5} "
                f"{trajet['distance_km']:>6.0f} km {trajet['type_service']:<4} "
                f"-> {emp_txt:<10} cluster={cluster}"
            )

        if delay > 0 and i < iterations:
            time.sleep(delay)

    print("-" * 60)
    total = ok + errors
    print(f"Termine : {ok}/{total} requetes OK, {errors} echecs.")
    return 0 if errors == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Generateur de predictions ObRail.")
    parser.add_argument("-n", "--iterations", type=int, default=60,
                        help="Nombre de tours (3 requetes par tour). Defaut : 60.")
    parser.add_argument("--delay", type=float, default=1.0,
                        help="Delai en secondes entre chaque tour. Defaut : 1.0.")
    parser.add_argument("--base-url", default=os.environ.get("BASE_URL", DEFAULT_BASE_URL),
                        help="URL de base du backend.")
    args = parser.parse_args()
    return run(args.base_url, args.iterations, args.delay)


if __name__ == "__main__":
    sys.exit(main())
