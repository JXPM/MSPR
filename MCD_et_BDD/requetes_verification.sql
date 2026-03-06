-- Vérifier le nombre de lignes dans chaque table
SELECT 'pays'        AS table_name, COUNT(*) FROM pays
UNION ALL
SELECT 'operateur',                  COUNT(*) FROM operateur
UNION ALL
SELECT 'gare',                       COUNT(*) FROM gare
UNION ALL
SELECT 'ligne',                      COUNT(*) FROM ligne
UNION ALL
SELECT 'type_train',                 COUNT(*) FROM type_train
UNION ALL
SELECT 'trajet',                     COUNT(*) FROM trajet
UNION ALL
SELECT 'itineraire',                 COUNT(*) FROM itineraire
UNION ALL
SELECT 'exploite',                   COUNT(*) FROM exploite
UNION ALL
SELECT 'utilisation',                COUNT(*) FROM utilisation
UNION ALL
SELECT 'emission',                   COUNT(*) FROM emission;

--  Vérifier les clés étrangères — pas de valeurs orphelines

-- Gares sans pays valide
SELECT COUNT(*) AS gares_orphelines FROM gare
WHERE iso_pays NOT IN (SELECT iso_pays FROM pays);

-- Trajets sans ligne valide
SELECT COUNT(*) AS trajets_orphelins FROM trajet
WHERE id_ligne NOT IN (SELECT id_ligne FROM ligne);

-- Itinéraires sans trajet valide
SELECT COUNT(*) AS itin_orphelins FROM itineraire
WHERE trajet_id NOT IN (SELECT trajet_id FROM trajet);

-- Itinéraires avec code_uic inconnu
SELECT COUNT(*) AS uic_inconnus FROM itineraire
WHERE code_uic NOT IN (SELECT code_uic FROM gare);

-- Exploite sans opérateur ou ligne valide
SELECT COUNT(*) AS exploite_orphelins FROM exploite
WHERE code_operateur NOT IN (SELECT code_operateur FROM operateur)
   OR id_ligne NOT IN (SELECT id_ligne FROM ligne);

   