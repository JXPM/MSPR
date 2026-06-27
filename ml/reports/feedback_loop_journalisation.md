# Journalisation et feedback loop MLOps — ObRail Europe

> Support de rédaction pour le rapport technique (section « Supervision de la
> solution IA ») et pour la soutenance. À recopier/adapter dans le `.docx`.

---

## 1. Paragraphe prêt à insérer dans le rapport

### Supervision : trois niveaux complémentaires

La supervision de la solution IA s'organise en trois niveaux qui se complètent.

**Niveau 1 — Monitoring infrastructure.** Hérité de la phase précédente,
Prometheus collecte les métriques génériques de l'API (débit, taux d'erreurs
4xx/5xx, latence p50/p95/p99) ; Grafana les restitue sous forme de tableaux de
bord.

**Niveau 2 — Monitoring du modèle.** Des métriques Prometheus dédiées
(`backend/app/ml_metrics.py`) exposent la santé et le comportement *du modèle* :
disponibilité (`obrail_model_loaded`), volume et latence d'inférence,
distribution des sorties (empreinte CO₂ prédite, clusters) et des entrées
(distance, durée, type de service). Ces distributions permettent de détecter une
**dérive des données** (*data drift*), c'est-à-dire un écart entre les requêtes
reçues en production et les données d'entraînement. Le compteur
`obrail_predict_unknown_operator_total` signale en particulier l'apparition
d'opérateurs absents du référentiel d'entraînement.

**Niveau 3 — Journalisation des prédictions.** Chaque appel aux endpoints de
prédiction écrit une ligne de log structurée au format JSON (logger
`obrail.predictions`), contenant l'horodatage, les entrées, la sortie, la latence
et le statut :

```json
{"event": "prediction", "endpoint": "emissions", "status": "success",
 "inputs": {"distance_km": 850.0, "operateur": "ÖBB", "type_service": "NUIT",
            "duree_trajet_min": 600.0},
 "latency_ms": 32.57, "output": {"empreinte_train_kg": 14.43}}
```

Là où le monitoring fournit des **agrégats** (courbes, moyennes), la
journalisation conserve la **trace détaillée de chaque requête**, indispensable
pour l'audit et — surtout — pour alimenter le *feedback loop*.

### Du déploiement au feedback loop

Le déploiement de l'API n'est pas l'aboutissement du projet mais le point de
départ d'une **boucle d'amélioration continue** (*feedback loop* MLOps) :

1. le modèle déployé produit une prédiction ;
2. la prédiction est **journalisée** (entrées + sortie) ;
3. la valeur réelle est collectée a posteriori (vérité terrain) ;
4. prédiction et réalité sont comparées : le modèle dérive-t-il ?
5. en cas de dérive avérée, le modèle est **réentraîné** sur les données
   enrichies (`ml/src/train_regression.py`) ;
6. le nouveau modèle est redéployé, et la boucle reprend.

La journalisation mise en place constitue la **première brique opérationnelle**
de cette boucle : sans trace exploitable des prédictions, aucune comparaison à la
réalité — donc aucune détection de dérive ni réentraînement fondé — n'est
possible.

### Industrialisation : ce qui est en place, ce qui reste

« Déployer » signifie mettre l'application en ligne une fois ; « industrialiser »
signifie rendre tout le **cycle de vie du modèle** reproductible et automatisé.
L'état actuel :

| Brique d'industrialisation | État |
|---|---|
| Code versionné (Git) | En place |
| Tests automatisés + CI/CD (GitHub Actions) | En place |
| Déploiement automatisé (Render) | En place |
| Monitoring du modèle (Grafana) | En place |
| Journalisation des prédictions | En place |
| Réentraînement automatisé + redéploiement / rollback | Perspective |

L'étape restante — l'automatisation du réentraînement déclenché par un seuil de
dérive — est volontairement laissée en perspective : sur un jeu de 310 lignes
sans flux continu de données, un réentraînement **périodique et supervisé par un
humain** est plus pertinent qu'une boucle entièrement automatique.

---

## 2. À dire à l'oral (3–4 phrases)

> « Nous avons mis en place trois niveaux de supervision : l'infrastructure de
> l'API, le modèle lui-même via des métriques Prometheus dédiées, et la
> journalisation détaillée de chaque prédiction au format JSON.

> Cette journalisation est la première brique concrète du *feedback loop* : elle
> nous permet de rejouer les prédictions face à la valeur réelle, de détecter une
> dérive des données — par exemple un opérateur jamais vu à l'entraînement — puis
> de réentraîner le modèle.

> Le déploiement n'est donc pas la fin du projet mais le début de cette boucle
> d'amélioration continue.

> Nous avons laissé l'automatisation complète du réentraînement en perspective :
> avec 310 lignes et sans flux temps réel, un réentraînement périodique supervisé
> est plus raisonnable qu'une boucle entièrement automatisée. »

---

## 3. Questions jury probables

**« Quelle différence entre votre monitoring et votre journalisation ? »**
Le monitoring agrège (courbes, moyennes, latence p95) ; la journalisation garde
le détail requête par requête. L'un répond à « comment se porte le service
globalement ? », l'autre à « qu'a exactement prédit le modèle à 14h03 ? ».

**« Votre feedback loop est-il automatisé ? »**
Non, et c'est un choix assumé. Les briques d'observation (journalisation +
métriques de dérive) sont en place ; le réentraînement reste supervisé par un
humain, car le volume de données (310 lignes, 100 % trains de nuit) ne justifie
pas une boucle entièrement automatique qui risquerait de réapprendre du bruit.

**« Pourquoi journaliser en JSON plutôt qu'en texte libre ? »**
Le JSON est directement *parsable* : on peut extraire les prédictions des logs
par programme et les joindre à la vérité terrain, sans réécrire de parseur.
