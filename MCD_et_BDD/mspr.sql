-- =====================================================
-- SCRIPT DE CRÉATION DE LA BASE DE DONNÉES
-- VERSION FINALE CORRIGÉE - TOUT EN MINUSCULES
-- =====================================================

-- Suppression des tables (ordre inverse des dépendances)
DROP TABLE IF EXISTS utilisation CASCADE;
DROP TABLE IF EXISTS exploite CASCADE;
DROP TABLE IF EXISTS emission CASCADE;
DROP TABLE IF EXISTS itineraire CASCADE;
DROP TABLE IF EXISTS trajet CASCADE;
DROP TABLE IF EXISTS type_train CASCADE;
DROP TABLE IF EXISTS ligne CASCADE;
DROP TABLE IF EXISTS source CASCADE;
DROP TABLE IF EXISTS gare CASCADE;
DROP TABLE IF EXISTS operateur CASCADE;
DROP TABLE IF EXISTS pays CASCADE;

-- =====================================================
-- CRÉATION DES TABLES
-- =====================================================

-- 1. pays
CREATE TABLE pays (
    iso_pays VARCHAR(2)   PRIMARY KEY,
    nom_pays VARCHAR(100)
);

-- Pays hors Europe nécessaires pour les opérateurs
INSERT INTO pays (iso_pays, nom_pays) VALUES
    ('US', 'United States of America'),
    ('MA', 'Morocco');

-- 2. operateur
CREATE TABLE operateur (
    code_operateur VARCHAR(100) PRIMARY KEY,
    nom_operateur  VARCHAR(200),
    iso_pays       VARCHAR(2),
    FOREIGN KEY (iso_pays) REFERENCES pays(iso_pays)
);

-- 3. gare
-- Source : stations.csv — code_uic = 7 chiffres
CREATE TABLE gare (
    code_uic  VARCHAR(10)  PRIMARY KEY,
    nom_gare  VARCHAR(200),
    longitude DECIMAL(9,6),
    latitude  DECIMAL(9,6),
    iso_pays  VARCHAR(2)   NOT NULL,
    FOREIGN KEY (iso_pays) REFERENCES pays(iso_pays)
);

-- 4. source
CREATE TABLE source (
    id_source      SERIAL PRIMARY KEY,
    url            VARCHAR(500),
    nom_fichier    VARCHAR(200),
    format         VARCHAR(50),
    nombre_fichier INT
);

-- 5. ligne
-- id_ligne = INT (pas SERIAL) pour conserver le route_id de routes.json
-- Cela permet la jointure directe avec trips.json et routes.json
CREATE TABLE ligne (
    id_ligne     INT          PRIMARY KEY,
    nom_ligne    VARCHAR(100),
    distance     DECIMAL(15,2),
    type_service VARCHAR(50)  CHECK (type_service IN ('JOUR', 'NUIT'))
);

-- 6. type_train
CREATE TABLE type_train (
    id_type_train SERIAL PRIMARY KEY,
    type_nom      VARCHAR(50)
);

-- 7. trajet
-- heure_depart et heure_arrivee en VARCHAR(10) 
-- car Talend ne convertit pas String → TIME nativement
-- Format stocké : HH:mm:ss (ex: 19:28:00)
CREATE TABLE trajet (
    trajet_id     VARCHAR(50)  PRIMARY KEY,
    gare_depart   VARCHAR(200),
    gare_arrivee  VARCHAR(200),
    heure_depart  VARCHAR(30),
    heure_arrivee VARCHAR(30),
    id_ligne      INT          NOT NULL,
    FOREIGN KEY (id_ligne) REFERENCES ligne(id_ligne)
);

-- 8. itineraire
-- code_uic nullable — Inner Join dans Talend filtre les non-matchs
CREATE TABLE itineraire (
    trajet_id     VARCHAR(50),
    id_itineraire SERIAL,
    chemin        VARCHAR(1000),
    code_uic      VARCHAR(10),
    PRIMARY KEY (trajet_id, id_itineraire),
    FOREIGN KEY (trajet_id) REFERENCES trajet(trajet_id),
    FOREIGN KEY (code_uic)  REFERENCES gare(code_uic)
);

-- 9. emission
CREATE TABLE emission (
    id_emission         SERIAL        PRIMARY KEY,
    transporteur        VARCHAR(200),
    origine             VARCHAR(300)  NOT NULL,
    destination         VARCHAR(300)  NOT NULL,
    distance_train_km   DECIMAL(10,3) NOT NULL,
    empreinte_train_kg  DECIMAL(10,6) NOT NULL,
    distance_avion_km   DECIMAL(10,3),
    empreinte_avion_kg  DECIMAL(10,6)
);

-- 10. exploite
CREATE TABLE exploite (
    code_operateur VARCHAR(100),
    id_ligne       INT,
    rang           VARCHAR(50),
    PRIMARY KEY (code_operateur, id_ligne),
    FOREIGN KEY (code_operateur) REFERENCES operateur(code_operateur),
    FOREIGN KEY (id_ligne)       REFERENCES ligne(id_ligne)
);

-- 11. utilisation
CREATE TABLE utilisation (
    code_operateur VARCHAR(100),
    id_type_train  INT,
    PRIMARY KEY (code_operateur, id_type_train),
    FOREIGN KEY (code_operateur) REFERENCES operateur(code_operateur),
    FOREIGN KEY (id_type_train)  REFERENCES type_train(id_type_train)
);

