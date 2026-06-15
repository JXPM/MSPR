# Contexte notebooks — ObRail Europe ML

Extraction textuelle des trois notebooks dans l'ordre exact.
Aucune reformulation. Outputs tronqués signalés explicitement.

---

# NOTEBOOK 1 — analyse-de-données.ipynb (01_eda.ipynb)

---

## [MARKDOWN]

# EDA  ObRail Europe
## Analyse Exploratoire des Données

 Ce notebook contient uniquement du code d'observation.   
 Il produit des constats écrits utilisés dans la phase de preprocessing.

---

## [CODE]

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import missingno as msno
from scipy import stats
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.manifold import TSNE
import warnings
warnings.filterwarnings('ignore')

from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
```

---

## [CODE]

```python
# connexion a la base de données  
load_dotenv(dotenv_path=r'C:\Users\josep\Mspr2\MSPR2\MSPR\.env')

user     = os.getenv("POSTGRES_USER", "postgres")
password = os.getenv("POSTGRES_PASSWORD", "postgres")
db       = os.getenv("POSTGRES_DB", "mspr2")

engine = create_engine(f"postgresql://{user}:{password}@localhost:5433/{db}")
```

---

## [CODE]

```python
query = """
SELECT DISTINCT
    e.distance_km,
    e.empreinte_train_kg,
    e.empreinte_avion_kg,
    ROUND(e.empreinte_train_kg / NULLIF(e.empreinte_avion_kg, 0), 4) AS ratio_co2,
    o.nom_operateur                                                    AS operateur,
    o.iso_pays                                                         AS pays_operateur,
    t.trajet_id,
    t.gare_depart,
    t.gare_arrivee,
    t.heure_depart,
    t.heure_arrivee,
    l.type_service
FROM emission e
JOIN trajet    t ON e.trajet_id       = t.trajet_id
JOIN ligne     l ON t.id_ligne        = l.id_ligne
JOIN exploite  x ON l.id_ligne        = x.id_ligne
JOIN operateur o ON x.code_operateur  = o.code_operateur
WHERE e.distance_km IS NOT NULL
  AND e.empreinte_train_kg IS NOT NULL;
"""

df = pd.read_sql(query, engine)
```

---

## [MARKDOWN]

### Données extraites

ObRail Europe mesure l'impact environnemental des trajets ferroviaires européens 
et évalue leur potentiel comme alternative à l'avion.

Dans ce cadre, nous cherchons à répondre à trois questions concrètes :
**prédire l'empreinte CO2 d'un trajet ferroviaire à partir de ses caractéristiques,**
**identifier automatiquement les liaisons les plus susceptibles de remplacer l'avion,**
**identifier les lignes à fort potentiel de croissance**

Pour répondre à ces objectifs, les colonnes suivantes ont été extraites et construites.

**Colonnes sur le trajet :**
**distance_km**, **gare_depart**, **gare_arrivee**, **heure_depart**, **heure_arrivee**, **trajet_id**

**Colonnes sur les émissions :**
**empreinte_train_kg**, **empreinte_avion_kg**, **ratio_co2**

**ratio_co2** a été calculé directement dans la requête SQL comme 
`empreinte_train_kg / empreinte_avion_kg`. Un ratio de 0.12 signifie que le train 
émet 12% de ce qu'émet l'avion, soit environ 8 fois moins sur le même trajet.

**Colonnes sur l'opérateur :**
**operateur**, **pays_operateur** , **type_service**

---

## [CODE]

```python
df.to_csv(r'C:\Users\josep\Mspr2\MSPR2\MSPR\ml\data\raw\dataset_final.csv', index=False)
```

---

## [CODE]

```python
df.head()
```

**Résultat :**

```
   distance_km  empreinte_train_kg  empreinte_avion_kg  ratio_co2  \
0       1115.0                19.2             176.170     0.1090   
1        875.0                 2.6             138.250     0.0188   
2       1032.0                20.8             163.056     0.1276   
3        867.0                17.7             136.986     0.1292   
4        493.0                10.3              77.894     0.1322   

              operateur pays_operateur          trajet_id       gare_depart  \
0          Укрзалізниця             UA             UZ 064              Lviv   
1     SNCF Voyageurs SA             FR  SNCF IC Nuit 3971  Paris Austerlitz   
2      Trenitalia S.p.A             IT    FS IC Notte 755   Milano Centrale   
3      Trenitalia S.p.A             IT   FS IC Notte 1954  Palermo Centrale   
4  C.F.R. Călători S.A.             RO      CFR 1641 (CN)    București Nord   

                         gare_arrivee              heure_depart  \
0                             Kharkiv  1899-12-30T15:30:00.000Z   
1  Latour-de-Carol / La Tor de Querol  1899-12-30T21:40:00.000Z   
2                               Lecce  1899-12-30T21:50:00.000Z   
3                        Roma Termini  1899-12-30T18:48:00.000Z   
4                         Cluj-Napoca  1899-12-30T21:03:00.000Z   

              heure_arrivee type_service  
0  1899-12-30T05:56:00.000Z         NUIT  
1  1899-12-30T10:07:00.000Z         NUIT  
2  1899-12-30T09:30:00.000Z         NUIT  
3  1899-12-30T07:18:00.000Z         NUIT  
4  1899-12-30T07:02:00.000Z         NUIT  
```

---

## [MARKDOWN]

##  Compréhension des données (EDA)

Les cellules suivantes contiennent uniquement des observations.  
Aucune transformation n'est appliquée.  
Chaque constat est documenté en Markdown après le code.

---

## [CODE]

```python
# Vue d'ensemble
print("Forme du dataset :", df.shape)
print("\nTypes des colonnes :")
print(df.dtypes)
```

**Résultat :**

```
Forme du dataset : (400, 12)

Types des colonnes :
distance_km           float64
empreinte_train_kg    float64
empreinte_avion_kg    float64
ratio_co2             float64
operateur                 str
pays_operateur            str
trajet_id                 str
gare_depart               str
gare_arrivee              str
heure_depart              str
heure_arrivee             str
type_service              str
dtype: object
```

---

## [CODE]

```python
print("\n 5 premières lignes :")
df.head(5)
```

**Résultat :**

```
   distance_km  empreinte_train_kg  empreinte_avion_kg  ratio_co2  \
0       1115.0                19.2             176.170     0.1090   
1        875.0                 2.6             138.250     0.0188   
2       1032.0                20.8             163.056     0.1276   
3        867.0                17.7             136.986     0.1292   
4        493.0                10.3              77.894     0.1322   

              operateur pays_operateur          trajet_id       gare_depart  \
0          Укрзалізниця             UA             UZ 064              Lviv   
1     SNCF Voyageurs SA             FR  SNCF IC Nuit 3971  Paris Austerlitz   
2      Trenitalia S.p.A             IT    FS IC Notte 755   Milano Centrale   
3      Trenitalia S.p.A             IT   FS IC Notte 1954  Palermo Centrale   
4  C.F.R. Călători S.A.             RO      CFR 1641 (CN)    București Nord   

                         gare_arrivee              heure_depart  \
0                             Kharkiv  1899-12-30T15:30:00.000Z   
1  Latour-de-Carol / La Tor de Querol  1899-12-30T21:40:00.000Z   
2                               Lecce  1899-12-30T21:50:00.000Z   
3                        Roma Termini  1899-12-30T18:48:00.000Z   
4                         Cluj-Napoca  1899-12-30T21:03:00.000Z   

              heure_arrivee type_service  
0  1899-12-30T05:56:00.000Z         NUIT  
1  1899-12-30T10:07:00.000Z         NUIT  
2  1899-12-30T09:30:00.000Z         NUIT  
3  1899-12-30T07:18:00.000Z         NUIT  
4  1899-12-30T07:02:00.000Z         NUIT  
```

---

## [CODE]

```python
print("\nStatistiques descriptives :")
print(df.describe())
```

**Résultat :**

```
       distance_km  empreinte_train_kg  empreinte_avion_kg   ratio_co2
count   400.000000          400.000000          400.000000  400.000000
mean    837.825000           14.616199          132.375225    0.114614
std     284.425736            7.194792           44.943073    0.051509
min     389.000000            0.160000           61.462000    0.001900
25%     607.500000           10.700250           95.985000    0.098425
50%     805.000000           15.237500          127.190000    0.124650
75%    1033.000000           18.977500          163.214000    0.143475
max    1847.000000           30.500000          291.826000    0.245700
```

---

## [MARKDOWN]

### Observations générales

Le dataset contient 400 lignes et 12 colonnes.

Les colonnes numériques sont : **distance_km**, **empreinte_train_kg**, **empreinte_avion_kg**, **ratio_co2**.

Les colonnes catégorielles sont : **operateur**, **pays_operateur**, **heure_depart**, **heure_arrivee**, **type_service**.

Les colonnes exclues du modèle sont :

**trajet_id** a été exclu car c'est un identifiant unique sans valeur prédictive.

**gare_depart** a été exclue car elle présente trop de modalités (200+ villes) et son information géographique est déjà capturée par **distance_km**. Principe de minimisation des données RGPD Art. 5.1.c.

**gare_arrivee** a été exclue pour les mêmes raisons que **gare_depart**.

Note : **heure_depart** et **heure_arrivee** seront transformées en **duree_trajet_min** lors du preprocessing.

La cible pour la régression est **empreinte_train_kg**.

---

## [CODE] — Figure : valeurs_manquantes.png

```python
# Analyse des valeurs manquantes

print("\n pourcentage de valeurs manquantes par colonne :")
print((df.isnull().sum() / len(df) * 100).round(2), '%')

# Visualisation
msno.matrix(df)
plt.savefig(r'C:\Users\josep\Mspr2\MSPR2\MSPR\ml\reports\figures\valeurs_manquantes.png', dpi=150)
plt.show()
```

**Résultat :** [output image trop volumineux — figure sauvegardée : `reports/figures/valeurs_manquantes.png`]

---

## [MARKDOWN]

### Valeurs manquantes

Le matrix plot affiche une barre noire pour chaque valeur présente et une barre blanche pour chaque 
valeur manquante. Le graphique est entièrement noir : le dataset ne contient aucune valeur manquante 
sur les 310 lignes et 12 colonnes. Aucune imputation ne sera nécessaire.

---

## [CODE] — Figure : distributions.png

```python
colonnes_numeriques = ['distance_km', 'empreinte_train_kg', 'empreinte_avion_kg', 'ratio_co2']

fig, axes = plt.subplots(2, 2, figsize=(12, 8))
for i, col in enumerate(colonnes_numeriques):
    ax = axes[i//2, i%2]
    ax.hist(df[col], bins=30, edgecolor='black', color='steelblue')
    ax.set_title(f'Distribution de {col}')
    ax.set_xlabel(col)
    ax.set_ylabel('Fréquence')

plt.suptitle('Distribution des variables numériques', fontsize=14)
plt.tight_layout()
plt.savefig(r'C:\Users\josep\Mspr2\MSPR2\MSPR\ml\reports\figures\distributions.png', dpi=150)
plt.show()

print("Skewness par variable :")
for col in colonnes_numeriques:
    print(f"  {col} : {df[col].skew():.2f}")
```

**Résultat :** [output image trop volumineux — figure sauvegardée : `reports/figures/distributions.png`]

---

## [MARKDOWN]

### Distribution des variables numériques

Le skewness(asymetrie) mesure si les valeurs sont bien réparties ou si certaines s'éloignent 
fortement de la majorité. Au-delà de 2.0 en valeur absolue, une transformation 
logarithmique est nécessaire.

**distance_km** : skewness = 0.68, pic autour de 800 km, quelques trajets isolés 
au-delà de 1500 km tirent légèrement la distribution vers la droite.

**empreinte_train_kg** : skewness = -0.13, distribution équilibrée centrée autour 
de 15 kg CO2. Quelques valeurs proches de 0 à investiguer.

**empreinte_avion_kg** : skewness = 0.68, distribution très similaire à distance_km, 
ce qui confirme leur relation quasi linéaire.

**ratio_co2** : skewness = -0.42, distribution centrée autour de 0.12.

Aucune variable ne dépasse le seuil de 2.0, aucune transformation logarithmique 
n'est nécessaire.

---

## [MARKDOWN]

### Détection des outliers

Un outlier est une valeur anormalement éloignée du reste des données.
Il peut s'agir d'une erreur de saisie ou d'un cas réel mais exceptionnel.

La méthode du Z-score détecte les outliers en se basant sur la moyenne 
et l'écart-type de la distribution.

La méthode IQR se base sur les percentiles : elle identifie comme outlier 
toute valeur qui s'éloigne trop de la moitié centrale des données 
(entre le 25e et le 75e percentile). Le seuil utilisé est 1.5 x IQR, 
une convention établie par le statisticien John Tukey. Ce seuil capture 
environ 99.3% des données sur une distribution normale, ce qui représente 
le bon équilibre entre détecter les vraies anomalies sans exclure 
des valeurs légitimes.

Sur un dataset de 400 lignes, il serait plus pertinent d'utiliser l'IQR 
car les percentiles ne sont pas influencés par les valeurs extrêmes, 
ce qui rend la détection plus fiable sur de petits volumes de données.

---

## [CODE] — Figure : boxplots.png

```python
colonnes_numeriques = ['distance_km', 'empreinte_train_kg', 'empreinte_avion_kg', 'ratio_co2']

def detecter_outliers_iqr(df, col):
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    borne_basse = Q1 - 1.5 * IQR
    borne_haute = Q3 + 1.5 * IQR
    outliers = df[(df[col] < borne_basse) | (df[col] > borne_haute)]
    print(f"{col} : {len(outliers)} outliers")
    print(f"  Borne basse : {borne_basse:.2f}, Borne haute : {borne_haute:.2f}")
    return outliers

for col in colonnes_numeriques:
    detecter_outliers_iqr(df, col)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

df[['distance_km', 'empreinte_train_kg', 'empreinte_avion_kg']].boxplot(ax=axes[0])
axes[0].set_title('Outliers : distance et émissions')
axes[0].set_ylabel('Valeurs')

df[['ratio_co2']].boxplot(ax=axes[1])
axes[1].set_title('Outliers : ratio_co2 (échelle dédiée)')
axes[1].set_ylabel('ratio_co2')

plt.suptitle('Détection des outliers par variable numérique', fontsize=13)
plt.tight_layout()
plt.savefig(r'C:\Users\josep\Mspr2\MSPR2\MSPR\ml\reports\figures\boxplots.png', dpi=150)
plt.show()
```

**Résultat :** [output image trop volumineux — figure sauvegardée : `reports/figures/boxplots.png`]

---

## [MARKDOWN]

### Interprétation des outliers

**distance_km** : 2 outliers détectés au-dessus de 1671 km. 
Ce sont les deux trajets les plus longs du dataset, réels et cohérents 
avec le réseau ferroviaire européen. Ils sont conservés.

**empreinte_train_kg** : aucun outlier détecté. 
Les valeurs proches de 0 correspondent aux opérateurs nordiques 
dont le réseau est quasi entièrement électrifié avec une énergie 
hydraulique très propre. Elles restent dans les bornes acceptables.

**empreinte_avion_kg** : 2 outliers détectés, cohérents avec les 2 outliers 
de distance_km. Ce sont les mêmes trajets longs qui génèrent 
logiquement une empreinte avion plus élevée. Ils sont conservés.

**ratio_co2** : 58 outliers détectés soit 14.5% du dataset. 
Le graphique dédié montre deux types d'outliers : vers le bas, 
les opérateurs nordiques (SJ, VR) avec un ratio proche de 0 
car leur énergie est quasi entièrement hydraulique. Vers le haut, 
les opérateurs à fort mix thermique dont le ratio dépasse 0.21. 
Ces cas sont réels et informatifs pour le clustering. Ils sont conservés.

Aucun outlier ne sera supprimé. Tous correspondent à des cas réels 
et leur suppression appauvrirait l'analyse.

---

## [MARKDOWN]

### Analyse des corrélations

La corrélation mesure la force du lien entre deux variables numériques.
Deux méthodes existent.

La corrélation de **Pearson** compare directement les valeurs brutes 
des variables entre elles. Elle est sensible aux valeurs extrêmes.

La corrélation de **Spearman** ne compare pas les valeurs brutes mais 
les rangs : chaque valeur est classée de la plus petite à la plus grande, 
et ce sont ces classements qui sont comparés. Elle est robuste aux outliers.

Nos variables numériques peuvent toutes être classées par ordre croissant, 
ce qui rend l'usage de Spearman pertinent. De plus, 58 outliers ont été 
détectés sur **ratio_co2**, soit 14.5% du dataset, ce qui renforce ce choix.

---

## [CODE] — Figure : matrice_correlation.png

```python
colonnes_numeriques = ['distance_km', 'empreinte_train_kg', 'empreinte_avion_kg', 'ratio_co2']

corr_matrix = df[colonnes_numeriques].corr(method='spearman')
print("Matrice de corrélation Spearman :")
print(corr_matrix.round(2))

print("\nCorrélation avec empreinte_train_kg :")
print(corr_matrix['empreinte_train_kg'].sort_values(ascending=False).round(2))

plt.figure(figsize=(8, 6))
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm',
            vmin=-1, vmax=1, center=0)
plt.title('Matrice de corrélation Spearman')
plt.savefig(r'C:\Users\josep\Mspr2\MSPR2\MSPR\ml\reports\figures\matrice_correlation.png', dpi=150)
plt.show()
```

**Résultat :** [output image trop volumineux — figure sauvegardée : `reports/figures/matrice_correlation.png`]

---

## [MARKDOWN]

### Interprétation de la matrice de corrélation

La corrélation Spearman va de -1 à 1. 
Plus elle est proche de 1, plus les deux variables évoluent dans le même sens. 
Plus elle est proche de -1, plus elles évoluent en sens inverse.
Proche de 0, elles n'ont pas de lien.

**distance_km et empreinte_avion_kg** : corrélation = 1.00, relation quasi parfaite. 
Ces deux variables portent la même information car empreinte_avion_kg est calculée 
directement à partir de distance_km. **empreinte_avion_kg** sera exclue 
de la régression pour éviter la redondance.

**distance_km et empreinte_train_kg** : corrélation = 0.54, relation modérée. 
La distance explique une partie des émissions CO2 du train mais pas tout, 
l'opérateur joue également un rôle important.

**ratio_co2 et empreinte_train_kg** : corrélation = 0.49, relation modérée. 
Le ratio sera conservé pour le clustering.

**ratio_co2 et distance_km** : corrélation = -0.38, relation faible inverse. 
Plus un trajet est long, plus le ratio tend à baisser légèrement.

La variable **empreinte_avion_kg** sera exclue de la régression 
et conservée uniquement pour le clustering.

---

## [MARKDOWN]

### Analyse de la multicolinéarité (VIF)

La matrice de corrélation nous a montré que certaines variables sont très liées entre elles.
Le VIF (Variance Inflation Factor) permet de quantifier précisément ce phénomène.

Pour chaque variable, le VIF mesure dans quelle mesure elle est expliquée 
par les autres variables du dataset. Plus le VIF est élevé, plus la variable 
est redondante avec les autres.

VIF = 1 : aucune redondance.
VIF entre 1 et 5 : acceptable.
VIF entre 5 et 10 : à surveiller.
VIF supérieur à 10 : variable redondante, à exclure du modèle.

---

## [CODE]

```python
from statsmodels.stats.outliers_influence import variance_inflation_factor

colonnes_vif = ['distance_km', 'empreinte_train_kg', 'empreinte_avion_kg', 'ratio_co2']

X_vif = df[colonnes_vif].dropna()

vif_data = pd.DataFrame()
vif_data['variable'] = X_vif.columns
vif_data['VIF'] = [variance_inflation_factor(X_vif.values, i)
                   for i in range(X_vif.shape[1])]

vif_data['VIF_affiche'] = vif_data['VIF'].apply(
    lambda x: 'infini' if x > 1000 else round(x, 1)
)

vif_data_sorted = vif_data.sort_values('VIF', ascending=False)
print(vif_data_sorted[['variable', 'VIF_affiche']])
```

**Résultat :**

```
             variable VIF_affiche
0         distance_km      infini
2  empreinte_avion_kg      infini
1  empreinte_train_kg        19.5
3           ratio_co2        10.1
```

---

## [MARKDOWN]

### Interprétation du VIF

La matrice de corrélation avait montré que **distance_km** et **empreinte_avion_kg** 
avaient une corrélation de 1.00. Le VIF confirme ce constat : ces deux variables 
sont entièrement redondantes l'une avec l'autre, leur VIF est infini.

**empreinte_train_kg** et **ratio_co2** ont un VIF élevé (19.5 et 10.1) 
car elles sont toutes les deux corrélées à **distance_km** (0.54 et 0.49).

En résumé : pour la régression on utilisera uniquement **distance_km** et **operateur**.
Pour le clustering on conserve toutes les variables numériques.

---

## [MARKDOWN]

# analyse de l'opérateur

---

## [CODE] — Figure : emissions_par_operateur.png

```python
## Distribution des opérateurs
print("Distribution des opérateurs :")
print(df['operateur'].value_counts())
print("\nEn pourcentage :")
print((df['operateur'].value_counts(normalize=True) * 100).round(2))

# Emission moyenne par opérateur
emission_par_op = df.groupby('operateur')['empreinte_train_kg'].agg(
    ['mean', 'std', 'count']
).sort_values('mean', ascending=False)
print("\nEmission moyenne par opérateur :")
print(emission_par_op.round(2))

# Barplot horizontal emissions moyennes par opérateur
plt.figure(figsize=(10, 10))
emission_par_op['mean'].sort_values().plot(kind='barh', color='steelblue')
plt.title('Emission CO2 moyenne par opérateur (kg)')
plt.xlabel('empreinte_train_kg moyenne')
plt.ylabel('Opérateur')
plt.tight_layout()
plt.savefig(r'C:\Users\josep\Mspr2\MSPR2\MSPR\ml\reports\figures\emissions_par_operateur.png', dpi=150)
plt.show()
```

**Résultat :** [output image trop volumineux — figure sauvegardée : `reports/figures/emissions_par_operateur.png`]

---

## [MARKDOWN]

### Analyse de l'opérateur

Le dataset contient 25 opérateurs ferroviaires européens.

**Déséquilibre des données :** Укрзалізниця (UZ) représente 94 trajets soit 23.5% 
du dataset. Le modèle verra beaucoup plus d'exemples UZ que les autres opérateurs. 
Les prédictions pour les petits opérateurs comme Vygruppen AS et Go-Ahead Norge AS 
(2 trajets chacun, soit 0.5%) seront moins fiables.

**Les émissions varient fortement selon l'opérateur :** PKP Intercity émet en moyenne 
23.86 kg CO2 par trajet contre 0.16 kg pour Vygruppen AS. Cet écart confirme que 
l'opérateur est une feature pertinente pour la régression car le matériel roulant 
et le mix énergétique diffèrent significativement d'un pays à l'autre.

**Opérateurs à faibles émissions :** SJ Norge AS, Go-Ahead Norge AS et Vygruppen AS 
affichent des émissions quasi nulles, liées au réseau ferroviaire norvégien 
quasi entièrement alimenté par énergie hydraulique. SNCF et SJ AB affichent 
également des émissions très basses grâce au mix nucléaire français 
et hydraulique suédois.

**Opérateurs à fortes émissions :** PKP Intercity (Pologne), MÁV (Hongrie) 
et TCDD (Turquie) affichent les émissions les plus élevées, cohérent 
avec un mix énergétique plus dépendant du charbon et du thermique.

---

## [MARKDOWN]

### Réduction de dimensionnalité exploratoire (PCA)

La PCA (Principal Component Analysis) est utilisée ici uniquement pour visualiser 
la structure des données en 2D. Elle ne modifie pas les données et ne sera pas 
utilisée comme preprocessing pour le modèle.

Au vu de la corrélation quasi parfaite entre distance_km et empreinte_avion_kg (1.00) 
et des VIF infinis observés, on s'attend à ce que la PCA fusionne ces deux variables 
en une seule composante principale. La PCA servira ici de confirmation visuelle 
de ce qu'on a déjà observé dans l'analyse des corrélations.

Avant d'appliquer la PCA, une normalisation est obligatoire car la PCA est sensible 
aux échelles : une variable en km (389 à 1847) dominerait une variable en ratio 
(0 à 0.25) sans normalisation.

---

## [CODE] — Figures : scree_plot.png, pca_2d.png

```python
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

features_pca = ['distance_km', 'empreinte_train_kg', 'empreinte_avion_kg', 'ratio_co2']
X_pca = df[features_pca].dropna()

# Normalisation obligatoire avant PCA
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_pca)

# Calculer toutes les composantes
pca_full = PCA(random_state=42)
pca_full.fit(X_scaled)

variance_expliquee = pca_full.explained_variance_ratio_
variance_cumulee = np.cumsum(variance_expliquee)

print("Variance par composante :", variance_expliquee.round(3))
print("Variance cumulée :", variance_cumulee.round(3))

# Scree plot
plt.figure(figsize=(8, 5))
plt.bar(range(1, 5), variance_expliquee, label='Par composante', color='steelblue')
plt.plot(range(1, 5), variance_cumulee, 'ro-', label='Cumulée')
plt.axhline(y=0.80, color='g', linestyle='--', label='Seuil 80%')
plt.xlabel('Composante principale')
plt.ylabel('Variance expliquée')
plt.title('Scree plot')
plt.legend()
plt.savefig(r'C:\Users\josep\Mspr2\MSPR2\MSPR\ml\reports\figures\scree_plot.png', dpi=150)
plt.show()

# Projection 2D
pca_2d = PCA(n_components=2, random_state=42)
X_2d = pca_2d.fit_transform(X_scaled)

plt.figure(figsize=(10, 7))
plt.scatter(X_2d[:, 0], X_2d[:, 1], alpha=0.6, color='steelblue')
plt.xlabel(f'PC1 ({variance_expliquee[0]*100:.1f}% variance)')
plt.ylabel(f'PC2 ({variance_expliquee[1]*100:.1f}% variance)')
plt.title('Projection PCA 2D des 400 trajets')
plt.savefig(r'C:\Users\josep\Mspr2\MSPR2\MSPR\ml\reports\figures\pca_2d.png', dpi=150)
plt.show()
```

**Résultat :** [output image trop volumineux — figures sauvegardées : `reports/figures/scree_plot.png`, `reports/figures/pca_2d.png`]

---

## [MARKDOWN]

### Interprétation de la PCA

Le scree plot confirme ce qu'on avait anticipé.

**PC1** capte 58.5% de la variance. Elle représente principalement 
la direction commune entre distance_km et empreinte_avion_kg, 
les deux variables quasi identiques détectées précédemment.

**PC2** capte 40.6% de la variance. Elle représente ce qui différencie 
empreinte_train_kg et ratio_co2 des deux autres variables.

**PC3 et PC4** captent respectivement 0.9% et 0% de la variance. 
Elles n'apportent aucune information supplémentaire.

Deux composantes suffisent à expliquer 99.1% de la variance totale du dataset. 
Cela confirme que nos 4 variables numériques ne contiennent en réalité 
que deux directions d'information distinctes.

La projection 2D ne montre pas de groupes clairement séparés. 
Les points sont répartis de façon continue, ce qui suggère que 
le clustering KMeans devra trouver des frontières non évidentes visuellement.

---

## [MARKDOWN]

### Visualisation t-SNE

Le t-SNE (t-distributed Stochastic Neighbor Embedding) est un algorithme 
de visualisation 2D plus puissant que la PCA pour révéler des groupes naturels.

Là où la PCA cherche les directions de variance maximale à l'échelle globale, 
le t-SNE cherche à préserver les relations de voisinage : des points proches 
dans l'espace original restent proches dans la visualisation 2D.

Limite absolue : le t-SNE ne peut pas transformer de nouvelles donnée). Il est utilisé uniquement pour la visualisation, 
jamais comme preprocessing pour le modèle.

---

## [CODE] — Figure : tsne_2d.png

```python
from sklearn.manifold import TSNE

tsne = TSNE(n_components=2, random_state=42, perplexity=30)
X_tsne = tsne.fit_transform(X_scaled)

plt.figure(figsize=(10, 7))
plt.scatter(X_tsne[:, 0], X_tsne[:, 1], alpha=0.6, color='steelblue')
plt.title('Projection t-SNE 2D des 400 trajets')
plt.xlabel('Dimension 1')
plt.ylabel('Dimension 2')
plt.savefig(r'C:\Users\josep\Mspr2\MSPR2\MSPR\ml\reports\figures\tsne_2d.png', dpi=150)
plt.show()
```

**Résultat :** [output image trop volumineux — figure sauvegardée : `reports/figures/tsne_2d.png`]

---

## [MARKDOWN]

### Interprétation du t-SNE

Contrairement à la PCA qui ne montrait pas de groupes distincts, 
le t-SNE révèle plusieurs nuages de points relativement séparés.

On distingue visuellement entre 3 a 4 groupes naturels dans les données, 
sans pouvoir trancher précisément sur leur nombre. Ce résultat confirme 
que des structures existent bien dans le dataset. Le clustering KMeans 
aura des frontières naturelles à identifier et permettra de déterminer 
le nombre optimal de groupes de façon statistique.

La différence entre PCA et t-SNE est normale et attendue : 
la PCA cherche la variance globale et ne voit pas les structures locales. 
Le t-SNE cherche à préserver les voisinages locaux et révèle 
les groupes que la PCA ne capte pas.

Ce graphique sera mis en parallèle avec les résultats du KMeans 
lors de la phase de modélisation.

---

## [MARKDOWN]

### Sélection des variables

A partir de l'ensemble des analyses réalisées, voici les décisions retenues 
pour chaque modèle.

**Pour la régression (prédire empreinte_train_kg) :**

**distance_km** est retenue. Corrélation de 0.54 avec la cible, 
variable la plus informative disponible.

**operateur** est retenue. Les émissions varient fortement selon l'opérateur 
(de 0.16 kg à 23.86 kg en moyenne), ce qui en fait une feature métier essentielle.

**type_service** est retenue. Elle distingue les trajets JOUR et NUIT, 
ce qui peut influencer les émissions selon le type de matériel roulant utilisé.

**empreinte_avion_kg** est exclue. Corrélation parfaite de 1.00 avec distance_km, 
VIF infini, redondance totale.

**Pour le clustering (identifier les profils de liaisons) :**

**distance_km**, **empreinte_train_kg**, **empreinte_avion_kg** et **ratio_co2** 
sont toutes conservées. Le clustering bénéficie de la richesse des variables 
pour former des groupes pertinents selon le profil d'émissions complet du trajet.

---

## [MARKDOWN]

### Conclusion de l'EDA

#### Ce que les données nous ont appris

Le dataset contient 400 trajets ferroviaires européens répartis sur 25 opérateurs, 
couvrant des distances allant de 389 à 1847 km avec deux types de service JOUR et NUIT.

Les analyses ont mis en évidence les points suivants :

Aucune valeur manquante n'a été détectée. Le dataset est complet et exploitable tel quel.

Les distributions des variables numériques sont acceptables avec des skewness 
tous inférieurs à 0.68 en valeur absolue. Aucune transformation logarithmique n'est nécessaire.

**distance_km** et **empreinte_avion_kg** sont entièrement redondantes 
(corrélation = 1.00, VIF infini). **empreinte_avion_kg** sera exclue de la régression.

58 outliers ont été détectés sur **ratio_co2**, soit 14.5% du dataset. 
Ils correspondent aux opérateurs nordiques à très faibles émissions et aux opérateurs 
à fort mix thermique. Ils sont conservés car informatifs pour le clustering.

Le dataset présente un déséquilibre opérateur : Укрзалізниця représente 23.5% 
des trajets. Ce biais sera atténué par le Target Encoding dans le preprocessing.

Le t-SNE révèle entre 3 et 4 groupes naturels dans les données, 
ce qui valide l'approche clustering.

#### Variables retenues

Pour la régression : **distance_km**, **operateur**, **type_service**

Pour le clustering : **distance_km**, **empreinte_train_kg**, **empreinte_avion_kg**, **ratio_co2**

#### Etapes de preprocessing à réaliser

**Colonnes à supprimer :** trajet_id, gare_depart, gare_arrivee, 
et empreinte_avion_kg pour la régression uniquement.

**Feature engineering :** transformer heure_depart et heure_arrivee 
en duree_trajet_min en calculant la différence entre les deux.

**Encodage :** appliquer le Target Encoding sur operateur 
en utilisant la moyenne de empreinte_train_kg par opérateur. 
Appliquer un encodage binaire (0/1) sur type_service (JOUR=0, NUIT=1).

**Normalisation :** appliquer un StandardScaler sur toutes les variables 
numériques avant l'entraînement des modèles et avant le clustering.

**Split des données :** découper le dataset en trois ensembles, 
70% entraînement, 15% validation, 15% test avec random_state=42.

---

---

# NOTEBOOK 2 — preprocessing.ipynb (02_preprocessing.ipynb)

---

## [MARKDOWN]

# Preprocessing ObRail Europe

Ce notebook prototype toutes les transformations appliquées au dataset brut.
Une fois validées, ces transformations seront industrialisées dans `src/preprocessing.py`.

Entrée : `data/raw/dataset_final.csv`
Sorties :
- `data/processed/dataset_cleaned.csv`
- `data/splits/X_train.csv`, `X_val.csv`, `X_test.csv`
- `data/splits/y_train.csv`, `y_val.csv`, `y_test.csv`
- `data/processed/target_encoding.csv`

---

## [CODE]

```python
import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Chemins relatifs au projet
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath('__file__')))
RAW_DIR       = os.path.join(BASE_DIR, 'data', 'raw')
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')
SPLITS_DIR    = os.path.join(BASE_DIR, 'data', 'splits')

# Créer les dossiers s'ils n'existent pas
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(SPLITS_DIR, exist_ok=True)

print("Imports OK")
print(f"BASE_DIR : {BASE_DIR}")
```

**Résultat :**

```
Imports OK
BASE_DIR : c:\Users\josep\Mspr2\MSPR2\MSPR\ml
```

---

## [CODE]

```python
# Chargement du dataset brut
df = pd.read_csv(os.path.join(RAW_DIR, 'dataset_final.csv'))

print(f"Dataset chargé : {df.shape[0]} lignes, {df.shape[1]} colonnes")
df.head()
```

**Résultat :**

```
Dataset chargé : 400 lignes, 12 colonnes

   distance_km  empreinte_train_kg  empreinte_avion_kg  ratio_co2  \
0       1115.0                19.2             176.170     0.1090   
1        875.0                 2.6             138.250     0.0188   
2       1032.0                20.8             163.056     0.1276   
3        867.0                17.7             136.986     0.1292   
4        493.0                10.3              77.894     0.1322   

              operateur pays_operateur          trajet_id       gare_depart  \
0          Укрзалізниця             UA             UZ 064              Lviv   
1     SNCF Voyageurs SA             FR  SNCF IC Nuit 3971  Paris Austerlitz   
2      Trenitalia S.p.A             IT    FS IC Notte 755   Milano Centrale   
3      Trenitalia S.p.A             IT   FS IC Notte 1954  Palermo Centrale   
4  C.F.R. Călători S.A.             RO      CFR 1641 (CN)    București Nord   

                         gare_arrivee              heure_depart  \
0                             Kharkiv  1899-12-30T15:30:00.000Z   
1  Latour-de-Carol / La Tor de Querol  1899-12-30T21:40:00.000Z   
2                               Lecce  1899-12-30T21:50:00.000Z   
3                        Roma Termini  1899-12-30T18:48:00.000Z   
4                         Cluj-Napoca  1899-12-30T21:03:00.000Z   

              heure_arrivee type_service  
0  1899-12-30T05:56:00.000Z         NUIT  
1  1899-12-30T10:07:00.000Z         NUIT  
2  1899-12-30T09:30:00.000Z         NUIT  
3  1899-12-30T07:18:00.000Z         NUIT  
4  1899-12-30T07:02:00.000Z         NUIT  
```

---

## [MARKDOWN]

### Nettoyage : suppression des colonnes non pertinentes

**trajet_id** est supprimé car c'est un identifiant unique sans valeur prédictive.

**gare_depart** et **gare_arrivee** sont supprimées car elles présentent trop 
de modalités distinctes et leur information géographique est déjà capturée 
par **distance_km**. Principe de minimisation des données RGPD Art. 5.1.c.

**pays_operateur** est supprimé car cette information est déjà portée 
par **operateur** qui sera encodé par ses émissions moyennes. 
Garder les deux introduirait une redondance.

---

## [CODE]

```python
# Suppression des colonnes exclues du modèle
colonnes_a_supprimer = ['trajet_id', 'gare_depart', 'gare_arrivee', 'pays_operateur']
df = df.drop(columns=colonnes_a_supprimer)

print(f"Colonnes restantes : {df.shape[1]}")
print(df.columns.tolist())
```

**Résultat :**

```
Colonnes restantes : 8
['distance_km', 'empreinte_train_kg', 'empreinte_avion_kg', 'ratio_co2', 'operateur', 'heure_depart', 'heure_arrivee', 'type_service']
```

---

## [MARKDOWN]

### Feature engineering : durée du trajet

**heure_depart** et **heure_arrivee** sont des chaînes de caractères 
sans valeur directe pour le modèle. On les transforme en **duree_trajet_min** 
qui représente la durée réelle du trajet en minutes.

Les trains de nuit partent le soir et arrivent le lendemain matin. 
La soustraction brute donnerait une durée négative dans ce cas. 
On corrige en ajoutant 1440 minutes (24h) aux durées négatives.

Une fois **duree_trajet_min** calculée, **heure_depart** et **heure_arrivee** 
sont supprimées.

---

## [CODE]

```python
df['heure_depart'] = pd.to_datetime(df['heure_depart'])
df['heure_arrivee'] = pd.to_datetime(df['heure_arrivee'])

df['duree_trajet_min'] = (df['heure_arrivee'] - df['heure_depart']).dt.total_seconds() / 60

df['duree_trajet_min'] = df['duree_trajet_min'].apply(
    lambda x: x + 1440 if x < 0 else x
)

df = df.drop(columns=['heure_depart', 'heure_arrivee'])

print(f"Durée min : {df['duree_trajet_min'].min():.0f} min")
print(f"Durée max : {df['duree_trajet_min'].max():.0f} min")
print(df[['distance_km', 'duree_trajet_min']].head(10))
```

**Résultat :**

```
Durée min : 8 min
Durée max : 1362 min
   distance_km  duree_trajet_min
0       1115.0             866.0
1        875.0             747.0
2       1032.0             700.0
3        867.0             750.0
4        493.0             599.0
5        849.0            1041.0
6        561.0             283.0
7        760.0             696.0
8       1209.0            1167.0
9       1110.0            1208.0
```

---

## [CODE]

```python
print(df[df['duree_trajet_min'] < 30][['distance_km', 'duree_trajet_min', 'operateur']].sort_values('duree_trajet_min'))
```

**Résultat :**

```
     distance_km  duree_trajet_min     operateur
283       1212.0               8.0  Укрзалізниця
42        1036.0              17.0  Укрзалізниця
206       1036.0              27.0  Укрзалізниця
```

---

## [MARKDOWN]

### Anomalies détectées sur duree_trajet_min

Trois trajets présentent des durées inférieures à 60 minutes 
pour des distances supérieures à 1000 km, ce qui est physiquement impossible.

Ces anomalies proviennent d'erreurs dans les heures de départ et d'arrivée 
enregistrées en base de données pour ces trajets Укрзалізниця.

Ces 3 lignes représentent 0.75% du dataset. Leur suppression est préférable 
à une imputation qui introduirait des valeurs artificielles. 
Le dataset passera de 400 à 397 lignes après suppression.

---

## [CODE]

```python
# Suppression des trajets avec durée < 30 min ET distance > 1000 km
avant = df.shape[0]
df = df[~((df['duree_trajet_min'] < 30) & (df['distance_km'] > 1000))].reset_index(drop=True)
apres = df.shape[0]

print(f"Lignes supprimées : {avant - apres}")
print(f"Dataset final : {apres} lignes")
print(f"Durée min après nettoyage : {df['duree_trajet_min'].min():.0f} min")
print(f"Durée max : {df['duree_trajet_min'].max():.0f} min")
```

**Résultat :**

```
Lignes supprimées : 0
Dataset final : 393 lignes
Durée min après nettoyage : 86 min
Durée max : 1362 min
```

---

## [MARKDOWN]

### Résultat du nettoyage

7 lignes ont été supprimées car elles présentaient des durées inférieures 
à 30 minutes, sont incohérentes avec les distances enregistrées 
pour ces trajets. Ces anomalies semblent liées à des erreurs dans les heures 
de départ ou d'arrivée en base de données.

Le dataset passe de 400 à 393 lignes. La durée minimale est désormais 
de 86 minutes.

---

## [MARKDOWN]

### Encodage des variables catégorielles

Deux variables catégorielles doivent être transformées en valeurs numériques 
avant l'entraînement des modèles.

**operateur** sera encodé par Target Encoding : chaque opérateur est remplacé 
par la moyenne de **empreinte_train_kg** calculée uniquement sur les données 
d'entraînement. Cette approche est robuste au déséquilibre des opérateurs 
et évite la malédiction de la dimensionnalité qu'introduirait un One-Hot Encoding 
sur 25 modalités.

**type_service** sera encodé en binaire : JOUR = 0, NUIT = 1.

Note : le Target Encoding sera fitté uniquement sur le train après le split 
pour éviter toute fuite de données vers la validation et le test.

---

## [CODE]

```python
# Encodage binaire type_service
df['type_service'] = df['type_service'].map({'JOUR': 0, 'NUIT': 1})

print("Encodage type_service :")
print(df['type_service'].value_counts())
```

**Résultat :**

```
Encodage type_service :
type_service
1    303
0     90
Name: count, dtype: int64
```

---

## [MARKDOWN]

### Split des données

Le dataset est découpé en trois ensembles avant d'appliquer le Target Encoding 
sur operateur, afin d'éviter tout data leakage.

70% entraînement, 15% validation, 15% test avec random_state=42.

Le train sert à apprendre. La validation sert à comparer les modèles 
et choisir le meilleur sans toucher au test. Le test sert à l'évaluation 
finale une seule fois, pour avoir un score honnête qui n'a pas été 
influencé par les choix de modélisation.

---

## [CODE]

```python
from sklearn.model_selection import train_test_split

# Features et cible pour la régression
features_regression = ['distance_km', 'operateur', 'type_service', 'duree_trajet_min']
cible = 'empreinte_train_kg'

X = df[features_regression]
y = df[cible]

# Split 70% train, 15% val, 15% test
X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.30, random_state=42
)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.50, random_state=42
)

print(f"Train : {X_train.shape[0]} lignes")
print(f"Validation : {X_val.shape[0]} lignes")
print(f"Test : {X_test.shape[0]} lignes")
```

**Résultat :**

```
Train : 275 lignes
Validation : 59 lignes
Test : 59 lignes
```

---

## [MARKDOWN]

### Target Encoding sur operateur

Le Target Encoding est appliqué après le split pour éviter le data leakage.
Si on l'avait appliqué avant, les moyennes auraient été calculées 
sur l'ensemble du dataset, y compris les données de validation et de test. 
Le modèle aurait indirectement vu ces données pendant l'entraînement.

Concrètement, on calcule la moyenne de **empreinte_train_kg** 
par opérateur uniquement sur les 275 lignes d'entraînement.
Cette moyenne remplace le nom de l'opérateur dans les trois ensembles.

PKP Intercity qui émet en moyenne 23.86 kg devient 23.86.
SNCF qui émet en moyenne 3.02 kg devient 3.02.

Si un opérateur apparaît dans la validation ou le test 
mais pas dans le train, il reçoit la moyenne globale du train 
comme valeur par défaut.

---

## [CODE]

```python
# Target Encoding sur operateur
# Calculé uniquement sur le train pour éviter le data leakage
target_encoding = X_train.copy()
target_encoding['empreinte_train_kg'] = y_train.values

encoding_map = target_encoding.groupby('operateur')['empreinte_train_kg'].mean()

# Appliquer sur train, val et test
X_train['operateur'] = X_train['operateur'].map(encoding_map)
X_val['operateur']   = X_val['operateur'].map(encoding_map)
X_test['operateur']  = X_test['operateur'].map(encoding_map)

# Gérer les opérateurs non vus dans le train (valeur par défaut = moyenne globale)
moyenne_globale = y_train.mean()
X_train['operateur'] = X_train['operateur'].fillna(moyenne_globale)
X_val['operateur']   = X_val['operateur'].fillna(moyenne_globale)
X_test['operateur']  = X_test['operateur'].fillna(moyenne_globale)

# Sauvegarder la table d'encodage
encoding_map.reset_index().rename(
    columns={'empreinte_train_kg': 'target_encoding'}
).to_csv(os.path.join(PROCESSED_DIR, 'target_encoding.csv'), index=False)

print("Target Encoding appliqué :")
print(encoding_map.sort_values(ascending=False).round(2))
```

**Résultat :**

```
Target Encoding appliqué :
operateur
PKP Intercity S.A.                       23.10
MÁV-START Vasúti Személyszállító Zrt.    22.08
TCDD Taşımacılık A.Ş.                    20.43
Trenitalia S.p.A                         18.78
České dráhy a.s.                         17.58
Укрзалізниця                             17.25
RegioJet a.s.                            15.90
Caledonian Sleeper Ltd.                  15.77
Astra Trans Carpatic SRL                 15.67
C.F.R. Călători S.A.                     15.04
Железнице Србије ад                      14.68
ÖBB-Personenverkehr AG                   14.18
First Greater Western Ltd.               13.40
European Sleeper Cooperatïe              13.39
VR-Yhtymä Oy                             12.78
БДЖ - Пътнически превози ЕООД            12.25
Calea Ferată din Moldova                 11.68
Merresor AB                              11.10
Železničná spoločnosť Slovensko a.s.      8.36
HŽ Putnički prijevoz d.o.o.               8.25
SJ AB                                     3.33
SNCF Voyageurs SA                         3.02
SJ Norge AS                               0.23
Go-Ahead Norge AS                         0.18
Vygruppen AS                              0.16
Name: empreinte_train_kg, dtype: float64
```

---

## [MARKDOWN]

### Normalisation des variables numériques

Le StandardScaler centre chaque variable autour de 0 et la réduit 
à un écart-type de 1. Cela évite qu'une variable avec de grandes valeurs 
comme **distance_km** (389 à 1847) domine une variable avec de petites valeurs 
comme **type_service** (0 ou 1).

Le scaler est fitté uniquement sur le train puis appliqué 
sur la validation et le test, pour les mêmes raisons que le Target Encoding : 
éviter le data leakage.

---

## [CODE]

```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled   = scaler.transform(X_val)
X_test_scaled  = scaler.transform(X_test)

# Reconvertir en DataFrame
X_train_scaled = pd.DataFrame(X_train_scaled, columns=features_regression)
X_val_scaled   = pd.DataFrame(X_val_scaled,   columns=features_regression)
X_test_scaled  = pd.DataFrame(X_test_scaled,  columns=features_regression)

print("Normalisation OK")
print(X_train_scaled.describe().round(2))
```

**Résultat :**

```
Normalisation OK
       distance_km  operateur  type_service  duree_trajet_min
count       275.00     275.00        275.00            275.00
mean         -0.00       0.00          0.00              0.00
std           1.00       1.00          1.00              1.00
min          -1.54      -2.64         -1.76             -1.91
25%          -0.78      -0.33          0.57             -0.80
50%          -0.15       0.21          0.57              0.06
75%           0.62       0.49          0.57              0.67
max           3.59       1.55          0.57              2.34
```

---

## [MARKDOWN]

### Résultat de la normalisation

Après normalisation, toutes les variables ont une moyenne de 0 et un écart-type de 1.

Avant la normalisation, **distance_km** allait de 389 à 1847 
et **type_service** valait 0 ou 1. Le modèle aurait accordé plus d'importance 
à **distance_km** uniquement parce que ses chiffres sont plus grands, 
pas parce qu'elle est plus informative.

Après la normalisation, toutes les variables partent sur un pied d'égalité. 
Le modèle peut comparer leur influence de façon équitable.

**type_service** présente des percentiles identiques au 25e, 50e et 75e (0.57). 
C'est normal car c'est une variable binaire : le StandardScaler la transforme 
mais elle ne prend que deux valeurs distinctes.

---

## [MARKDOWN]

### Conclusion du notebook de preprocessing

Ce notebook avait pour objectif d'explorer et valider chaque transformation 
appliquée au dataset brut. Travailler dans un notebook permet d'observer 
le résultat de chaque étape sur les données réelles et d'ajuster les décisions 
de transformation en conséquence.

Les étapes suivantes ont été validées :

La suppression des colonnes non pertinentes pour les modèles.
Le calcul de **duree_trajet_min** à partir des heures de départ et d'arrivée, 
avec détection et suppression de 7 anomalies.
L'encodage binaire de **type_service** et le Target Encoding de **operateur**, 
appliqués après le split pour éviter tout data leakage.
La normalisation via StandardScaler fitté uniquement sur le train.
Le split 70/15/15 avec random_state=42.

L'ensemble de ces transformations sera maintenant industrialisé 
dans `src/preprocessing.py`, le script final reproductible 
qui pourra être exécuté directement en ligne de commande.

---

---

# NOTEBOOK 3 — training.ipynb (03_training.ipynb)

---

## [MARKDOWN]

# Entraînement des modèles — ObRail Europe

Ce notebook entraîne et compare les modèles pour répondre 
aux trois problématiques d'ObRail Europe.

Il prend en entrée les fichiers produits par preprocessing.py :
- `data/splits/X_train.csv`, `X_val.csv`, `X_test.csv`
- `data/splits/y_train.csv`, `y_val.csv`, `y_test.csv`
- `data/processed/dataset_cleaned.csv` pour le clustering

Il produit en sortie :
- `models/model_final.joblib`
- `models/model_clustering.joblib`
- `reports/tableau_comparatif.csv`
- `reports/figures/shap_summary.png`
- `reports/figures/clustering_kmeans.png`

## Partie 1 : Régression supervisée

Objectif : prédire l'empreinte CO2 d'un trajet ferroviaire.

**LinearRegression** : modèle de référence, suppose une relation linéaire.
**Ridge** : régression linéaire avec pénalité, plus robuste aux variables corrélées.
**RandomForestRegressor** : ensemble d'arbres de décision, capture les relations non linéaires.
**XGBoostRegressor** : boosting séquentiel, très performant sur données tabulaires.
**LGBMRegressor** : alternative optimisée de XGBoost, plus rapide sur petits datasets.

## Partie 2 : Clustering non supervisé

Objectif : identifier les liaisons candidates à la substitution avion/train 
et les lignes à fort potentiel de croissance.

**KMeans** : regroupe les trajets en k groupes, k déterminé par méthode du coude et silhouette score.
**DBSCAN** : découvre les groupes automatiquement sans fixer k, détecte les outliers.
**AgglomerativeClustering** : regroupe les trajets de façon hiérarchique du plus proche au plus éloigné.
**GaussianMixture** : regroupe les trajets en supposant que chaque groupe suit une distribution statistique.

Le meilleur modèle de chaque partie sera sélectionné et sauvegardé.

---

## [CODE]

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os
import warnings
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.mixture import GaussianMixture
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.metrics import silhouette_score
from sklearn.model_selection import GridSearchCV
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
import shap

warnings.filterwarnings('ignore')

BASE_DIR    = os.path.abspath(os.path.join(os.getcwd(), '..'))
SPLITS_DIR  = os.path.join(BASE_DIR, 'data', 'splits')
MODELS_DIR  = os.path.join(BASE_DIR, 'models')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
FIGURES_DIR = os.path.join(BASE_DIR, 'reports', 'figures')

print(f"BASE_DIR : {BASE_DIR}")
print(f"SPLITS_DIR : {SPLITS_DIR}")
print("Imports OK")
```

**Résultat :**

```
BASE_DIR : c:\Users\josep\Mspr2\MSPR2\MSPR\ml
SPLITS_DIR : c:\Users\josep\Mspr2\MSPR2\MSPR\ml\data\splits
Imports OK
```

---

## [CODE]

```python
# Chargement des splits
X_train = pd.read_csv(os.path.join(SPLITS_DIR, 'X_train.csv'))
X_val   = pd.read_csv(os.path.join(SPLITS_DIR, 'X_val.csv'))
X_test  = pd.read_csv(os.path.join(SPLITS_DIR, 'X_test.csv'))

y_train = pd.read_csv(os.path.join(SPLITS_DIR, 'y_train.csv')).squeeze()
y_val   = pd.read_csv(os.path.join(SPLITS_DIR, 'y_val.csv')).squeeze()
y_test  = pd.read_csv(os.path.join(SPLITS_DIR, 'y_test.csv')).squeeze()

# Chargement du dataset nettoyé pour le clustering
df_clean = pd.read_csv(os.path.join(BASE_DIR, 'data', 'processed', 'dataset_cleaned.csv'))

print(f"X_train : {X_train.shape}")
print(f"X_val   : {X_val.shape}")
print(f"X_test  : {X_test.shape}")
print(f"df_clean : {df_clean.shape}")
```

**Résultat :**

```
X_train : (277, 4)
X_val   : (60, 4)
X_test  : (60, 4)
df_clean : (397, 7)
```

---

## [MARKDOWN]

## Partie 1 : Régression supervisée

Objectif : prédire l'empreinte CO2 d'un trajet ferroviaire à partir 
de la distance, de l'opérateur, du type de service et de la durée du trajet.

---

## [MARKDOWN]

### Démarche

On va suivre ces étapes dans l'ordre :

**Etape 1 : Baseline**
On entraîne les 5 modèles avec leurs paramètres par défaut sur le train 
et on mesure leurs performances sur la validation. 
L'objectif est d'identifier quel modèle est le plus prometteur.

**Etape 2 : Sélection**
On compare les résultats dans un tableau et on retient 
le modèle avec le meilleur RMSE sur la validation.

**Etape 3 : Optimisation**
On applique GridSearchCV avec cross-validation k=5 uniquement 
sur le meilleur modèle pour trouver ses hyperparamètres optimaux.

**Etape 4 : Evaluation finale**
On évalue le modèle optimisé une seule fois sur le test. 
Ce score est le score officiel qu'on présente au jury.

**Etape 5 : Explication**
On utilise SHAP pour expliquer quelles variables influencent 
le plus les prédictions du modèle.

---

## [CODE]

```python
modeles = {
    'LinearRegression' : LinearRegression(),
    'Ridge'            : Ridge(random_state=42),
    'RandomForest'     : RandomForestRegressor(random_state=42),
    'XGBoost'          : XGBRegressor(random_state=42, verbosity=0),
    'LightGBM'         : LGBMRegressor(random_state=42, verbose=-1)
}

for nom, modele in modeles.items():
    modele.fit(X_train, y_train)
    print(f"{nom} entraîné")
```

**Résultat :**

```
LinearRegression entraîné
Ridge entraîné
RandomForest entraîné
XGBoost entraîné
LightGBM entraîné
```

---

## [CODE]

```python
def evaluer_modele(modele, X_val, y_val):
    """Retourne MAE, RMSE et R² d'un modèle sur un ensemble donné."""
    y_pred = modele.predict(X_val)
    mae  = mean_absolute_error(y_val, y_pred)
    rmse = mean_squared_error(y_val, y_pred) ** 0.5
    r2   = r2_score(y_val, y_pred)
    return {'MAE': round(mae, 3), 'RMSE': round(rmse, 3), 'R2': round(r2, 3)}

resultats = {}
for nom, modele in modeles.items():
    resultats[nom] = evaluer_modele(modele, X_val, y_val)

df_resultats = pd.DataFrame(resultats).T.sort_values('RMSE')
print("Classement par RMSE :")
print(df_resultats)
```

**Résultat :**

```
Classement par RMSE :
                    MAE   RMSE     R2
XGBoost           0.751  1.308  0.964
RandomForest      1.130  1.642  0.943
LightGBM          1.605  2.280  0.890
LinearRegression  2.695  3.593  0.728
Ridge             2.697  3.594  0.728
```

---

## [MARKDOWN]

### Optimisation par GridSearchCV

XGBoost est retenu comme meilleur modèle. On va maintenant chercher 
ses hyperparamètres optimaux via GridSearchCV avec cross-validation k=5.

Les hyperparamètres testés sont :

**n_estimators** : nombre d'arbres construits. On teste 100, 200 et 300. 
Plus il y en a, plus le modèle est précis mais plus il est lent à entraîner.

**max_depth** : profondeur maximale de chaque arbre. On teste 3, 5 et 7. 
Un arbre trop profond mémorise les données au lieu d'apprendre des règles générales. 
Les valeurs impaires 3, 5 et 7 couvrent suffisamment le spectre 
sans alourdir inutilement la recherche sur un dataset de 277 lignes.

**learning_rate** : vitesse d'apprentissage. On teste 0.01, 0.05 et 0.1. 
Un taux bas apprend lentement mais précisément et nécessite plus d'arbres. 
Un taux élevé apprend vite mais risque de rater des patterns subtils.

**subsample** : proportion des données utilisées pour chaque arbre. 
On teste 0.8 et 1.0. Utiliser 80% des données introduit de la diversité 
entre les arbres et réduit le risque que le modèle mémorise les données.

Ces valeurs couvrent 54 combinaisons évaluées chacune 5 fois 
par cross-validation, soit 270 entraînements au total.

---

## [CODE]

```python
param_grid = {
    'n_estimators'  : [100, 200, 300],
    'max_depth'     : [3, 5, 7],
    'learning_rate' : [0.01, 0.05, 0.1],
    'subsample'     : [0.8, 1.0]
}
```

---

## [CODE]

```python
xgb_grid = GridSearchCV(
    estimator  = XGBRegressor(random_state=42, verbosity=0),
    param_grid = param_grid,
    cv         = 5,
    scoring    = 'neg_root_mean_squared_error',
    n_jobs     = 1,
    verbose    = 1
)

xgb_grid.fit(X_train, y_train)

print(f"Meilleurs paramètres : {xgb_grid.best_params_}")
print(f"Meilleur RMSE cross-val : {-xgb_grid.best_score_:.3f}")
```

**Résultat :**

```
Fitting 5 folds for each of 54 candidates, totalling 270 fits
Meilleurs paramètres : {'learning_rate': 0.1, 'max_depth': 5, 'n_estimators': 300, 'subsample': 0.8}
Meilleur RMSE cross-val : 2.535
```

---

## [MARKDOWN]

### Résultats du GridSearchCV

GridSearchCV a testé 54 combinaisons d'hyperparamètres, évaluées 5 fois 
chacune par cross-validation, soit 270 entraînements au total.

Pour chaque combinaison, le modèle est entraîné et évalué sur des données 
qu'il n'a jamais vues. La combinaison avec le plus petit RMSE moyen est retenue.

La meilleure combinaison trouvée :

**n_estimators** : 300 arbres au lieu de 100 par défaut. 
Plus d'arbres permettent un apprentissage plus fin.

**max_depth** : profondeur de 5 au lieu de 6 par défaut. 
Un arbre légèrement moins profond réduit le risque de mémorisation.

**learning_rate** : 0.1 au lieu de 0.3 par défaut. 
Le modèle apprend plus lentement mais plus précisément.

**subsample** : 0.8 au lieu de 1.0 par défaut. 
Chaque arbre utilise 80% des données, ce qui introduit de la diversité 
et évite que le modèle mémorise les données d'entraînement.

Le RMSE cross-validation obtenu est de 2.535. Ce score est plus élevé 
que le 1.308 obtenu sur la validation simple car la cross-validation 
est plus sévère : elle teste le modèle sur des données jamais vues 
à chaque fold, ce qui donne une estimation plus honnête des performances.

---

## [MARKDOWN]

### Evaluation finale sur le test

Jusqu'ici toutes les décisions ont été prises en regardant uniquement 
la validation : choix du meilleur modèle, optimisation des hyperparamètres. 
Le test n'a jamais été utilisé.

Le test est un ensemble de 60 trajets que le modèle n'a jamais vus 
sous aucune forme depuis le début du projet. C'est pour cette raison 
qu'il donne l'estimation la plus honnête des performances réelles du modèle.

Si le score sur le test est proche du score sur la validation, 
le modèle généralise bien sur des données inconnues.
Si le score est beaucoup moins bon, le modèle a mémorisé 
les données d'entraînement au lieu d'apprendre des règles générales.

---

## [CODE]

```python
# evaluation finale
meilleur_modele = xgb_grid.best_estimator_

resultats_val  = evaluer_modele(meilleur_modele, X_val, y_val)
resultats_test = evaluer_modele(meilleur_modele, X_test, y_test)

print("Performance sur la validation :")
print(f"  MAE  : {resultats_val['MAE']}")
print(f"  RMSE : {resultats_val['RMSE']}")
print(f"  R²   : {resultats_val['R2']}")

print("\nPerformance finale sur le test :")
print(f"  MAE  : {resultats_test['MAE']}")
print(f"  RMSE : {resultats_test['RMSE']}")
print(f"  R²   : {resultats_test['R2']}")
```

**Résultat :**

```
Performance sur la validation :
  MAE  : 0.68
  RMSE : 1.173
  R²   : 0.971

Performance finale sur le test :
  MAE  : 0.758
  RMSE : 1.419
  R²   : 0.959
```

---

## [MARKDOWN]

### Interprétation des résultats finaux

**Sur la validation :**
MAE = 0.68 kg, RMSE = 1.173 kg, R² = 0.971

**Sur le test :**
MAE = 0.758 kg, RMSE = 1.419 kg, R² = 0.959

Le modèle se trompe en moyenne de 0.758 kg CO2 sur des trajets 
qu'il n'a jamais vus. Pour rappel les émissions vont de 0.16 kg 
à 30.5 kg dans notre dataset, une erreur de 0.758 kg est très faible.

Le R² de 0.959 sur le test signifie que le modèle explique 95.9% 
de la variabilité des émissions CO2 sur des données inconnues.

Les scores entre validation et test sont très proches 
(R² 0.971 vs 0.959), ce qui confirme que le modèle généralise bien 
et n'a pas mémorisé les données d'entraînement.

XGBoost avec les hyperparamètres optimisés est retenu 
comme modèle final de régression.

---

## [MARKDOWN]

### Explication des prédictions avec SHAP

Un modèle comme XGBoost est une boîte noire : il prédit bien 
mais on ne sait pas pourquoi. SHAP ouvre cette boîte.

Pour chaque prédiction, SHAP calcule la contribution de chaque variable. 
Il part d'une valeur de base qui est la moyenne des émissions du dataset, 
puis il ajoute ou soustrait la contribution de chaque variable 
pour arriver à la prédiction finale.

Par exemple pour un trajet PKP Intercity de 891 km :

Valeur de base = 14.6 kg
distance_km élevée = +5.2 kg
operateur PKP = +3.8 kg
type_service NUIT = -0.4 kg
duree_trajet_min = +0.2 kg
Prédiction finale = 23.4 kg

Le graphique SHAP summary montre quelles variables influencent 
le plus les prédictions sur l'ensemble du dataset. 
Une variable en haut du graphique a plus d'influence qu'une variable en bas.

C'est aussi une exigence RGPD : toute prédiction algorithmique 
doit pouvoir être expliquée et justifiée.

---

## [CODE] — Figure : shap_summary.png

```python
explainer = shap.Explainer(meilleur_modele, X_train)
shap_values = explainer(X_train)

# Summary plot
plt.figure()
shap.summary_plot(shap_values, X_train, show=False)
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, 'shap_summary.png'), dpi=150)
plt.show()

print("SHAP summary sauvegardé")
```

**Résultat :** [output image trop volumineux — figure sauvegardée : `reports/figures/shap_summary.png`]

---

## [MARKDOWN]

### Interprétation du graphique SHAP

Le graphique SHAP (SHapley Additive exPlanations) montre l'impact 
de chaque variable sur les prédictions du modèle.

Chaque point représente un trajet. La couleur indique la valeur 
de la variable : rose = valeur élevée, bleu = valeur faible.

L'axe horizontal représente l'impact en kg CO2 sur la prédiction 
par rapport à la moyenne du dataset. Un point à droite augmente 
la prédiction, un point à gauche la diminue. 
Plus un point est éloigné de 0, plus son impact est fort.

**operateur** est la variable la plus influente avec un impact 
allant de -15 à +15 kg CO2, soit un écart possible de 30 kg 
selon l'opérateur.

**distance_km** est la deuxième variable la plus influente. 
Les trajets longs (rose) augmentent les émissions prédites, 
les trajets courts (bleu) les réduisent.

**duree_trajet_min** a une influence modérée et concentrée 
autour de 0. Elle affine la prédiction sans la dominer.

**type_service** a la plus faible influence sur les prédictions. 
La distinction JOUR et NUIT impacte peu les émissions CO2 prédites.

---

## [MARKDOWN]

### Sauvegarde du modèle et tableau comparatif

Le modèle XGBoost optimisé est sauvegardé au format joblib 
(Java Object Library) dans `models/model_regression.joblib`.

On sauvegarde le modèle pour deux raisons. La première est de ne pas 
avoir à réentraîner à chaque fois : l'entraînement prend du temps, 
sauvegarder le modèle permet de le recharger instantanément pour faire 
des prédictions. La seconde est l'intégration dans l'API : 
le fichier joblib sera chargé par `api/predict.py` pour répondre 
aux requêtes de prédiction sans avoir besoin du code d'entraînement.

On produit également un tableau comparatif de tous les modèles testés 
sauvegardé dans `reports/tableau_comparatif.csv`. Ce tableau constitue 
un livrable officiel du projet qui documente et justifie le choix 
du modèle final devant le jury.

---

## [MARKDOWN]

### Vérification de l'optimisation

Le GridSearchCV a trouvé les meilleurs hyperparamètres via cross-validation. 
Pour vérifier que ces hyperparamètres améliorent réellement les performances, 
on réentraîne XGBoost avec ces paramètres directement sur le train 
sans cross-validation.

On compare ensuite les résultats sur la validation et le test 
avec ceux du modèle par défaut. Si le modèle optimisé performe mieux, 
le GridSearchCV a bien fait son travail. Sinon, les paramètres par défaut 
étaient déjà suffisants pour ce dataset.

On mettra à jour le tableau comparatif avec ces nouveaux résultats.

---

## [CODE]

```python
xgb_optimise = XGBRegressor(
    n_estimators  = 300,
    max_depth     = 5,
    learning_rate = 0.1,
    subsample     = 0.8,
    random_state  = 42,
    verbosity     = 0
)

xgb_optimise.fit(X_train, y_train)

res_val  = evaluer_modele(xgb_optimise, X_val, y_val)
res_test = evaluer_modele(xgb_optimise, X_test, y_test)

print("XGBoost par défaut (baseline) :")
print(f"  Val  -> MAE={resultats['XGBoost']['MAE']} RMSE={resultats['XGBoost']['RMSE']} R²={resultats['XGBoost']['R2']}")

print("\nXGBoost optimisé :")
print(f"  Val  -> MAE={res_val['MAE']} RMSE={res_val['RMSE']} R²={res_val['R2']}")
print(f"  Test -> MAE={res_test['MAE']} RMSE={res_test['RMSE']} R²={res_test['R2']}")
```

**Résultat :**

```
XGBoost par défaut (baseline) :
  Val  -> MAE=0.751 RMSE=1.308 R²=0.964

XGBoost optimisé :
  Val  -> MAE=0.68 RMSE=1.173 R²=0.971
  Test -> MAE=0.758 RMSE=1.419 R²=0.959
```

---

## [MARKDOWN]

### Résultat de la vérification

Le modèle optimisé améliore les performances par rapport au modèle par défaut.

Sur la validation :
RMSE passe de 1.308 à 1.173, soit une amélioration de 10%.
R² passe de 0.964 à 0.971.
MAE passe de 0.751 à 0.68.

Sur le test, le modèle optimisé obtient un RMSE de 1.419 et un R² de 0.959, 
ce qui confirme qu'il généralise bien sur des données inconnues.

Le GridSearchCV a bien identifié des hyperparamètres plus adaptés 
à notre dataset. Le modèle optimisé est retenu comme modèle final.

---

## [CODE]

```python
joblib.dump(xgb_optimise, os.path.join(MODELS_DIR, 'model_regression.joblib'))
print("Modèle sauvegardé : models/model_regression.joblib")

tableau = []
for nom, modele in modeles.items():
    res = evaluer_modele(modele, X_val, y_val)
    res['modele'] = nom
    res['ensemble'] = 'Validation'
    res['optimise'] = 'Non'
    tableau.append(res)

res_opt_val = evaluer_modele(xgb_optimise, X_val, y_val)
res_opt_val['modele'] = 'XGBoost_optimise'
res_opt_val['ensemble'] = 'Validation'
res_opt_val['optimise'] = 'Oui'
tableau.append(res_opt_val)

res_opt_test = evaluer_modele(xgb_optimise, X_test, y_test)
res_opt_test['modele'] = 'XGBoost_optimise'
res_opt_test['ensemble'] = 'Test'
res_opt_test['optimise'] = 'Oui'
tableau.append(res_opt_test)

df_tableau = pd.DataFrame(tableau)[['modele', 'optimise', 'ensemble', 'MAE', 'RMSE', 'R2']]
df_tableau = df_tableau.sort_values('RMSE').reset_index(drop=True)

df_tableau.to_csv(os.path.join(REPORTS_DIR, 'tableau_comparatif.csv'), index=False)

print("\nTableau comparatif :")
print(df_tableau.to_string())
```

**Résultat :**

```
Modèle sauvegardé : models/model_regression.joblib

Tableau comparatif :
             modele optimise    ensemble    MAE   RMSE     R2
0  XGBoost_optimise      Oui  Validation  0.680  1.173  0.971
1           XGBoost      Non  Validation  0.751  1.308  0.964
2  XGBoost_optimise      Oui        Test  0.758  1.419  0.959
3      RandomForest      Non  Validation  1.130  1.642  0.943
4          LightGBM      Non  Validation  1.605  2.280  0.890
5  LinearRegression      Non  Validation  2.695  3.593  0.728
6             Ridge      Non  Validation  2.697  3.594  0.728
```

---

## [MARKDOWN]

### Tableau comparatif final

XGBoost optimisé obtient le meilleur RMSE de 1.173 sur la validation 
et 1.419 sur le test, avec un R² de 0.971 et 0.959 respectivement.

Les modèles linéaires LinearRegression et Ridge obtiennent des performances 
similaires avec un R² de 0.728, confirmant que la relation entre 
les features et les émissions CO2 n'est pas linéaire.

Le modèle final `model_regression.joblib` est sauvegardé dans `models/` 
et sera utilisé par l'API pour les prédictions en production.

---

## [MARKDOWN]

## Partie 2 : Clustering non supervisé

Objectif : identifier les liaisons candidates à la substitution avion/train 
et les lignes à fort potentiel de croissance via règles métier.

Les features utilisées sont : **distance_km**, **empreinte_train_kg**, 
**empreinte_avion_kg**, **ratio_co2**.

Ces variables capturent le profil d'émissions complet de chaque trajet 
et permettent de regrouper les liaisons selon leur potentiel 
de substitution avion/train.

---

## [MARKDOWN]

### Démarche

**Etape 1 : Préparation**
Extraire et normaliser les features de clustering depuis le dataset nettoyé.

**Etape 2 : Nombre optimal de clusters**
Tester KMeans de k=2 à k=8 via la méthode du coude et le silhouette score 
(SS) pour déterminer le nombre optimal de groupes.

**Etape 3 : Comparaison des modèles**
Comparer KMeans, DBSCAN, AgglomerativeClustering et GaussianMixture 
sur le nombre de clusters retenu.

**Etape 4 : Visualisation**
Projeter les clusters en 2D via PCA (Principal Component Analysis) 
pour visualiser les groupes formés.

**Etape 5 : Règles métier**
Appliquer des critères ObRail sur les clusters pour identifier 
les lignes à fort potentiel de substitution avion/train.

---

## [CODE]

```python
from sklearn.preprocessing import StandardScaler as SC

features_clustering = ['distance_km', 'empreinte_train_kg', 'empreinte_avion_kg', 'ratio_co2']

X_clust = df_clean[features_clustering].copy()

scaler_clust = SC()
X_clust_scaled = scaler_clust.fit_transform(X_clust)
X_clust_scaled = pd.DataFrame(X_clust_scaled, columns=features_clustering)

print(f"Features clustering : {X_clust_scaled.shape}")
print(X_clust_scaled.describe().round(2))
```

**Résultat :**

```
Features clustering : (397, 4)
       distance_km  empreinte_train_kg  empreinte_avion_kg  ratio_co2
count       397.00              397.00              397.00     397.00
mean         -0.00               -0.00                0.00       0.00
std           1.00                1.00                1.00       1.00
min          -1.57               -2.00               -1.57      -2.18
25%          -0.81               -0.55               -0.81      -0.33
50%          -0.12                0.08               -0.12       0.20
75%           0.68                0.61                0.68       0.57
max           3.56                2.21                3.56       2.54
```

---

## [MARKDOWN]

### Détermination du nombre optimal de clusters

Avant d'entraîner KMeans, on doit déterminer le nombre de clusters k 
car c'est un paramètre qu'on fixe à l'avance. Deux méthodes complémentaires 
sont utilisées.

**Méthode du coude** : on mesure l'inertie (somme des distances entre 
chaque point et le centre de son cluster) pour k=2 à k=8. 
Plus k augmente, plus l'inertie diminue. On cherche le point 
où la diminution ralentit brusquement, formant un coude. 
Ce point indique le k optimal.

**Silhouette score (SS)** : pour chaque trajet, il mesure à quel point 
il est proche des autres trajets de son cluster et éloigné des autres clusters. 
Un score proche de 1 signifie que les clusters sont bien séparés. 
On retient le k avec le silhouette score le plus élevé.

On combine les deux méthodes pour choisir le k le plus cohérent.

---

## [CODE] — Figure : kmeans_coude_silhouette.png

```python
inerties = []
silhouettes = []
k_range = range(2, 9)

for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_clust_scaled)
    inerties.append(kmeans.inertia_)
    silhouettes.append(silhouette_score(X_clust_scaled, labels))

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].plot(k_range, inerties, 'bo-')
axes[0].set_xlabel('Nombre de clusters k')
axes[0].set_ylabel('Inertie')
axes[0].set_title('Méthode du coude')

axes[1].plot(k_range, silhouettes, 'ro-')
axes[1].set_xlabel('Nombre de clusters k')
axes[1].set_ylabel('Silhouette score')
axes[1].set_title('Silhouette score par k')

plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, 'kmeans_coude_silhouette.png'), dpi=150)
plt.show()

print("Silhouette scores :")
for k, s in zip(k_range, silhouettes):
    print(f"  k={k} : {s:.3f}")
```

**Résultat :** [output image trop volumineux — figure sauvegardée : `reports/figures/kmeans_coude_silhouette.png`]

---

## [MARKDOWN]

### Interprétation

**Méthode du coude :** la courbe bleue descend rapidement jusqu'à k=3, 
puis la descente ralentit. Ajouter des clusters au-delà de 3 
n'améliore plus significativement le regroupement.

**Silhouette score (SS) :** le score le plus élevé est obtenu à k=3 
avec 0.467. Plus ce score est proche de 1, mieux les clusters 
sont séparés les uns des autres.

Les deux méthodes indiquent k=3. On retient 3 clusters pour la suite.

---

## [MARKDOWN]

### Entraînement des modèles de clustering

On entraîne les 4 modèles avec k=3 comme nombre de clusters, 
sauf DBSCAN qui détermine le nombre de clusters automatiquement.

**KMeans** : on fixe k=3, random_state=42 pour la reproductibilité 
et n_init=10 pour lancer 10 initialisations différentes 
et garder la meilleure.

**DBSCAN** : deux paramètres à fixer. eps définit la distance maximale 
entre deux points pour qu'ils soient considérés comme voisins. 
min_samples définit le nombre minimum de points pour former un cluster. 
Les points qui n'appartiennent à aucun cluster sont étiquetés -1 
et considérés comme du bruit.

**AgglomerativeClustering** : clustering hiérarchique ascendant, 
on fixe k=3 comme nombre final de groupes.

**GaussianMixture** : on fixe 3 composantes gaussiennes, 
random_state=42 pour la reproductibilité.

---

## [CODE]

```python
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
labels_kmeans = kmeans.fit_predict(X_clust_scaled)

dbscan = DBSCAN(eps=0.8, min_samples=5)
labels_dbscan = dbscan.fit_predict(X_clust_scaled)

agglo = AgglomerativeClustering(n_clusters=3)
labels_agglo = agglo.fit_predict(X_clust_scaled)

gmm = GaussianMixture(n_components=3, random_state=42)
labels_gmm = gmm.fit_predict(X_clust_scaled)

print("Nombre de clusters par modèle :")
print(f"  KMeans                  : {len(set(labels_kmeans))} clusters")
print(f"  DBSCAN                  : {len(set(labels_dbscan)) - (1 if -1 in labels_dbscan else 0)} clusters + {(labels_dbscan == -1).sum()} points bruit")
print(f"  AgglomerativeClustering : {len(set(labels_agglo))} clusters")
print(f"  GaussianMixture         : {len(set(labels_gmm))} clusters")
```

**Résultat :**

```
Nombre de clusters par modèle :
  KMeans                  : 3 clusters
  DBSCAN                  : 2 clusters + 6 points bruit
  AgglomerativeClustering : 3 clusters
  GaussianMixture         : 3 clusters
```

---

## [MARKDOWN]

### Evaluation des modèles de clustering

On compare les 4 modèles via le silhouette score (SS).

Le silhouette score (SS) mesure pour chaque trajet à quel point 
il est proche des autres trajets de son cluster et éloigné 
des clusters voisins. Un score proche de 1 indique des clusters 
bien séparés. Un score proche de 0 indique des clusters qui se chevauchent.

Pour DBSCAN, les 6 points de bruit sont exclus du calcul 
car ils n'appartiennent à aucun cluster.

Le modèle avec le silhouette score le plus élevé sera retenu 
comme modèle de clustering final.

---

## [CODE]

```python
scores = {}

scores['KMeans'] = silhouette_score(X_clust_scaled, labels_kmeans)
scores['AgglomerativeClustering'] = silhouette_score(X_clust_scaled, labels_agglo)
scores['GaussianMixture'] = silhouette_score(X_clust_scaled, labels_gmm)

mask = labels_dbscan != -1
if mask.sum() > 1 and len(set(labels_dbscan[mask])) > 1:
    scores['DBSCAN'] = silhouette_score(
        X_clust_scaled[mask], labels_dbscan[mask]
    )
else:
    scores['DBSCAN'] = None

print("Silhouette scores par modèle :")
for nom, score in scores.items():
    if score:
        print(f"  {nom:25} : {score:.3f}")
    else:
        print(f"  {nom:25} : non calculable")
```

**Résultat :**

```
Silhouette scores par modèle :
  KMeans                    : 0.467
  AgglomerativeClustering   : 0.466
  GaussianMixture           : 0.437
  DBSCAN                    : 0.400
```

---

## [MARKDOWN]

### Résultats de l'évaluation

Le silhouette score (SS) va de -1 à 1 :
- Proche de 1 : les clusters sont bien séparés
- Proche de 0 : les trajets sont à la frontière entre deux clusters
- Négatif : les trajets sont mal assignés

KMeans obtient le meilleur silhouette score (SS) de 0.467, 
suivi de très près par AgglomerativeClustering à 0.466.
GaussianMixture obtient 0.437 et DBSCAN 0.400.

Tous les scores sont entre 0.4 et 0.467, ce qui indique des clusters 
corrects mais pas parfaitement séparés. Ce résultat est cohérent 
avec le t-SNE qui montrait des groupes relativement distincts 
sans frontières totalement nettes.

KMeans est retenu comme modèle de clustering final pour deux raisons.
Il obtient le meilleur silhouette score (SS) et il est le plus 
interprétable : les centres de clusters ont une signification 
concrète en termes de distance et d'émissions CO2, 
ce qui facilite l'application des règles métier ObRail.

---

## [MARKDOWN]

### Visualisation des clusters

Pour visualiser les clusters en 2D on utilise le t-SNE 
(t-distributed Stochastic Neighbor Embedding) plutôt que la PCA 
(Principal Component Analysis).

La PCA cherche les directions de variance maximale à l'échelle globale 
et ne capte pas bien les structures locales. Le t-SNE au contraire 
préserve les relations de voisinage : des trajets proches 
dans l'espace original restent proches dans la visualisation 2D. 
Il révèle donc mieux les groupes naturels dans les données.

On l'avait déjà observé dans l'EDA : la PCA ne montrait pas 
de groupes distincts alors que le t-SNE révélait entre 3 et 4 
groupes naturels.

Chaque point représente un trajet. La couleur indique 
le cluster auquel il appartient. Pour DBSCAN, les points 
étiquetés -1 sont les trajets considérés comme bruit.

---

## [CODE] — Figure : clustering_comparaison.png

```python
from sklearn.manifold import TSNE

tsne_viz = TSNE(n_components=2, random_state=42, perplexity=30)
X_tsne_viz = tsne_viz.fit_transform(X_clust_scaled)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

modeles_clust = {
    'KMeans'                  : labels_kmeans,
    'DBSCAN'                  : labels_dbscan,
    'AgglomerativeClustering' : labels_agglo,
    'GaussianMixture'         : labels_gmm
}

for ax, (nom, labels) in zip(axes.flatten(), modeles_clust.items()):
    scatter = ax.scatter(X_tsne_viz[:, 0], X_tsne_viz[:, 1],
                         c=labels, cmap='tab10', alpha=0.6, s=20)
    ax.set_title(nom)
    ax.set_xlabel('Dimension 1')
    ax.set_ylabel('Dimension 2')
    plt.colorbar(scatter, ax=ax)

plt.suptitle('Visualisation des clusters en 2D (t-SNE)', fontsize=13)
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, 'clustering_comparaison.png'), dpi=150)
plt.show()
```

**Résultat :** [output image trop volumineux — figure sauvegardée : `reports/figures/clustering_comparaison.png`]

---

## [MARKDOWN]

### Interprétation de la visualisation

Les 4 graphiques montrent les mêmes 397 trajets colorés selon 
le cluster attribué par chaque modèle.

**KMeans** : 3 groupes clairement distincts et bien séparés visuellement. 
Le groupe en bas à gauche, celui du milieu à droite et celui en haut 
à gauche sont cohérents avec les structures observées dans le t-SNE de l'EDA.

**DBSCAN** : 2 groupes principaux avec quelques points isolés en bleu foncé 
représentant le bruit. DBSCAN a fusionné deux des groupes KMeans en un seul, 
ce qui explique son silhouette score (SS) plus faible.

**AgglomerativeClustering** : regroupement très similaire à KMeans 
avec 3 clusters bien séparés, ce qui explique leurs silhouette scores 
quasi identiques (0.467 vs 0.466).

**GaussianMixture** : regroupement différent des autres, 
le cluster cyan s'étend sur une zone plus large à droite du graphique. 
Les frontières entre clusters sont moins nettes, 
ce qui explique son silhouette score (SS) plus faible à 0.437.

KMeans produit le regroupement le plus cohérent visuellement 
et statistiquement. Il est confirmé comme modèle de clustering final.

---

## [MARKDOWN]

### Règles métier ObRail

Une fois les 3 clusters identifiés par KMeans, on analyse 
le profil moyen de chaque cluster pour lui attribuer 
une signification métier.

On calcule les moyennes de chaque feature par cluster 
pour comprendre ce que représente chaque groupe, 
puis on applique des critères ObRail pour qualifier 
le potentiel de substitution avion/train de chaque cluster.

Les critères retenus sont :

**ratio_co2 faible** : le train émet peu par rapport à l'avion, 
la substitution est environnementalement pertinente.

**distance_km modérée** : les trajets courts à moyens sont 
les plus susceptibles d'être remplacés par le train.

**empreinte_train_kg faible** : le train est peu émetteur 
sur ce trajet.

---

## [CODE]

```python
df_clust = df_clean[features_clustering].copy()
df_clust['cluster'] = labels_kmeans

# Profil moyen par cluster
profil = df_clust.groupby('cluster')[features_clustering].mean().round(2)
print("Profil moyen par cluster :")
print(profil)

# Taille de chaque cluster
taille = df_clust['cluster'].value_counts().sort_index()
print("\nNombre de trajets par cluster :")
print(taille)
```

**Résultat :**

```
Profil moyen par cluster :
         distance_km  empreinte_train_kg  empreinte_avion_kg  ratio_co2
cluster                                                                
0             819.49                3.23              129.48       0.03
1             672.77               15.15              106.29       0.14
2            1201.77               21.09              189.88       0.11

Nombre de trajets par cluster :
cluster
0     70
1    224
2    103
Name: count, dtype: int64
```

---

## [MARKDOWN]

### Analyse des clusters

**Cluster 0 (70 trajets) : Fort potentiel de substitution**
Distance moyenne de 820 km, empreinte train très faible à 3.23 kg CO2 
et ratio_co2 de 0.03. Le train émet 97% moins que l'avion sur ces trajets. 
Ce sont les liaisons les plus candidates à la substitution avion/train. 
Ces trajets correspondent aux opérateurs à très faibles émissions.

**Cluster 1 (224 trajets) : Potentiel modéré**
Distance moyenne de 673 km, empreinte train de 15.15 kg CO2 
et ratio_co2 de 0.14. Le train émet 86% moins que l'avion. 
C'est le groupe le plus large, représentant la majorité des trajets européens.

**Cluster 2 (103 trajets) : Potentiel limité**
Distance moyenne de 1202 km, empreinte train de 21.09 kg CO2 
et ratio_co2 de 0.11. Ce sont les trajets les plus longs 
avec les émissions les plus élevées. La substitution avion/train 
est moins évidente sur ces longues distances.

**Conclusion métier :**
70 liaisons sur 397 présentent un fort potentiel de substitution avion/train. 
ObRail peut recommander ces liaisons en priorité aux décideurs européens 
pour orienter les investissements ferroviaires.

---

## [MARKDOWN]

### Sauvegarde du modèle de clustering

On sauvegarde deux fichiers.

**model_clustering.joblib** : le modèle KMeans entraîné avec ses 3 centres 
de clusters. Il sera utilisé par l'API pour prédire le cluster 
d'un nouveau trajet.

**scaler_clustering.joblib** : le StandardScaler (SS) fitté sur les features 
de clustering. Il est indispensable car pour prédire le cluster 
d'un nouveau trajet, il faut d'abord normaliser ses données 
avec le même scaler utilisé pendant l'entraînement. 
Sans ça les distances calculées par KMeans seraient faussées.

---

## [CODE]

```python
joblib.dump(kmeans, os.path.join(MODELS_DIR, 'model_clustering.joblib'))
joblib.dump(scaler_clust, os.path.join(MODELS_DIR, 'scaler_clustering.joblib'))

print("Modèle clustering sauvegardé : models/model_clustering.joblib")
print("Scaler clustering sauvegardé : models/scaler_clustering.joblib")
```

**Résultat :**

```
Modèle clustering sauvegardé : models/model_clustering.joblib
Scaler clustering sauvegardé : models/scaler_clustering.joblib
```

---

## [MARKDOWN]

# conclusion 

---

## [MARKDOWN]

## Synthèse des modèles

### Régression supervisée

XGBoost optimisé est retenu comme modèle final de régression.
Après optimisation par GridSearchCV (CV k=5), il obtient :
- RMSE = 1.173 sur la validation
- RMSE = 1.419 sur le test
- R² = 0.959 sur le test

Avec un R² (mesure de la capacité du modèle à expliquer la variabilité 
des données par rapport à une prédiction naïve) de 0.959, le modèle 
explique 95.9% de la variation des émissions CO2 sur des trajets 
qu'il n'a jamais vus. L'opérateur est la variable la plus influente 
selon l'analyse SHAP (SHapley Additive exPlanations), 
suivi de la distance.

Modèle sauvegardé : `models/model_regression.joblib`

### Clustering non supervisé

KMeans avec k=3 est retenu comme modèle final de clustering 
avec un silhouette score (SS) de 0.467.

3 profils de liaisons ont été identifiés :
- Cluster 0 (70 trajets) : fort potentiel de substitution avion/train
- Cluster 1 (224 trajets) : potentiel modéré
- Cluster 2 (103 trajets) : potentiel limité

Modèle sauvegardé : `models/model_clustering.joblib`

---

## Figures produites (récapitulatif)

| Notebook | Nom du fichier | Description |
|---|---|---|
| EDA | `valeurs_manquantes.png` | Matrix plot missingno - aucune valeur manquante |
| EDA | `distributions.png` | Histogrammes des 4 variables numeriques |
| EDA | `boxplots.png` | Boxplots outliers par variable |
| EDA | `matrice_correlation.png` | Heatmap correlation Spearman |
| EDA | `emissions_par_operateur.png` | Barplot horizontal emissions moyennes par operateur |
| EDA | `scree_plot.png` | Scree plot PCA - variance expliquee par composante |
| EDA | `pca_2d.png` | Projection PCA 2D des 400 trajets |
| EDA | `tsne_2d.png` | Projection t-SNE 2D des 400 trajets |
| Training | `shap_summary.png` | SHAP summary plot - importance des variables XGBoost |
| Training | `kmeans_coude_silhouette.png` | Methode du coude et silhouette score k=2 a 8 |
| Training | `clustering_comparaison.png` | t-SNE 2D des 4 modeles de clustering compares |
