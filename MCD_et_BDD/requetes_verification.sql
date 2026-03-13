
-- TESTS DE COHÉRENCE  

-- 1. Y a-t-il des trajets qui ne sont liés à aucune ligne ?
SELECT t.trajet_id
FROM trajet t
LEFT JOIN ligne l ON t.id_ligne = l.id_ligne
WHERE l.id_ligne IS NULL;

-- 2. Y a-t-il des émissions qui ne correspondent à aucun trajet ?
SELECT e.id_emission
FROM emission e
LEFT JOIN trajet t ON e.trajet_id = t.trajet_id
WHERE t.trajet_id IS NULL;

-- 3. Quels sont les trajets qui émettent le plus de CO2 ?
SELECT trajet_id, empreinte_train_kg
FROM emission
ORDER BY empreinte_train_kg DESC
LIMIT 10;

-- 4. Quelle ligne produit le plus de CO2 au total ?
SELECT l.id_ligne, SUM(e.empreinte_train_kg) AS co2_total
FROM ligne l
JOIN trajet t ON l.id_ligne = t.id_ligne
JOIN emission e ON t.trajet_id = e.trajet_id
GROUP BY l.id_ligne
ORDER BY co2_total DESC;

-- 5. Existe-t-il des itinéraires qui pointent vers une gare inexistante ?
SELECT i.trajet_id, i.code_uic
FROM itineraire i
LEFT JOIN gare g ON i.code_uic = g.code_uic
WHERE g.code_uic IS NULL
AND i.code_uic IS NOT NULL;

-- 6. Combien de gares par pays ?
SELECT p.nom_pays, COUNT(g.code_uic) AS nombre_gares
FROM pays p
LEFT JOIN gare g ON p.iso_pays = g.iso_pays
GROUP BY p.nom_pays
ORDER BY nombre_gares DESC;

-- 7. Quels opérateurs exploitent quelles lignes ?
SELECT o.nom_operateur, l.id_ligne
FROM exploite e
JOIN operateur o ON e.code_operateur = o.code_operateur
JOIN ligne l ON e.id_ligne = l.id_ligne;

-- 8. Quels types de trains sont utilisés par les opérateurs ?
SELECT o.nom_operateur, t.type_nom
FROM utilisation u
JOIN operateur o ON u.code_operateur = o.code_operateur
JOIN type_train t ON u.id_type_train = t.id_type_train;

-- 9. Existe-t-il des lignes sans trajet ?
SELECT l.id_ligne
FROM ligne l
LEFT JOIN trajet t ON l.id_ligne = t.id_ligne
WHERE t.trajet_id IS NULL;

-- 10. Combien de trajets par ligne ?
SELECT l.id_ligne, COUNT(t.trajet_id) AS nombre_trajets
FROM ligne l
LEFT JOIN trajet t ON l.id_ligne = t.id_ligne
GROUP BY l.id_ligne
ORDER BY nombre_trajets DESC;

-- 11. Voir un exemple complet d’un trajet avec ses informations liées
SELECT
t.trajet_id,
l.nom_ligne,
t.gare_depart,
t.gare_arrivee,
e.empreinte_train_kg,
e.empreinte_avion_kg,
i.code_uic
FROM trajet t
JOIN ligne l ON t.id_ligne = l.id_ligne
LEFT JOIN emission e ON t.trajet_id = e.trajet_id
LEFT JOIN itineraire i ON t.trajet_id = i.trajet_id
LIMIT 20;

-- 12. Analyse globale : comparaison CO2 train vs avion
SELECT
SUM(empreinte_train_kg) AS total_co2_train,
SUM(empreinte_avion_kg) AS total_co2_avion,
SUM(empreinte_avion_kg) - SUM(empreinte_train_kg) AS economie_co2
FROM emission;