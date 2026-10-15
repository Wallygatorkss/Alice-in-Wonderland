# BookWorm

### Analysez, résumez et explorez les grands textes de Project Gutenberg

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![NLP](https://img.shields.io/badge/NLP-spaCy%20%7C%20Transformers-09A3D5)](https://spacy.io/)
[![Machine Learning](https://img.shields.io/badge/ML-scikit--learn-F7931E?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Source](https://img.shields.io/badge/Source-Project%20Gutenberg-6B3F1F)](https://www.gutenberg.org/)

## Aperçu du projet

**BookWorm** est une application en ligne de commande dédiée à l’analyse
automatique de livres disponibles sur [Project Gutenberg](https://www.gutenberg.org/).
À partir de l’identifiant d’un livre, elle télécharge et met en cache le texte,
le nettoie, puis combine des techniques de traitement automatique du langage
(NLP), de résumé automatique et de machine learning pour produire une fiche
de lecture exploitable.

Le projet a été conçu autour d’un cas concret : explorer *Alice's Adventures
in Wonderland* (ID Gutenberg `11`), tout en restant suffisamment générique
pour analyser d’autres ouvrages du catalogue.

## Fonctionnalités clés

- **Analyse lexicale** : nombre de tokens, vocabulaire utilisé, hapax,
  diversité lexicale (TTR), longueur moyenne des mots et fréquence moyenne.
- **Résumé automatique** : extraction de phrases importantes avec BERT, puis
  génération d’un résumé court avec BART (`facebook/bart-large-cnn`).
- **Analyse sémantique** : identification des mots-clés par section et
  extraction des personnages et lieux avec spaCy.
- **Exploration et comparaison** : téléchargement de couvertures, génération
  de nuages de mots et recherche de livres similaires par similarité TF-IDF /
  cosinus.
- **Mise en cache locale** : les textes téléchargés, analyses et résumés sont
  conservés localement afin de limiter les traitements et requêtes répétitifs.

## Prérequis

- Python **3.8 ou supérieur**
- `pip` et `venv`
- Une connexion Internet pour accéder à Project Gutenberg et télécharger les
  modèles NLP lors de la première utilisation
- Plusieurs gigaoctets d’espace disque peuvent être nécessaires pour les
  modèles PyTorch et Transformers

## Installation

### 1. Récupérer le projet

```bash
git clone https://github.com/Wallygatorkss/Alice-in-Wonderland.git
cd Alice-in-Wonderland
```

### 2. Créer et activer un environnement virtuel

Sous Linux ou macOS :

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Sous Windows PowerShell :

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Installer les dépendances Python

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Installer le modèle spaCy utilisé pour les entités

Cette étape est nécessaire pour activer l’extraction des personnages et des
lieux :

```bash
python -m spacy download en_core_web_sm
```

Les ressources NLTK nécessaires au résumé sont téléchargées automatiquement
par le programme. Si votre environnement bloque ce téléchargement, vous pouvez
les installer manuellement :

```bash
python -c "import nltk; nltk.download('punkt')"
```

## Utilisation

La syntaxe générale est :

```bash
python bookworm.py [OPTIONS] ID_LIVRE
```

`ID_LIVRE` correspond à l’identifiant du livre sur Project Gutenberg. Par
exemple, `11` désigne *Alice's Adventures in Wonderland*.

### Exemples rapides

Analyser la diversité lexicale d’Alice au pays des merveilles :

```bash
python bookworm.py --lexdiv 11
```

Générer un résumé automatique :

```bash
python bookworm.py --summary 11
```

Extraire les thèmes et les entités nommées :

```bash
python bookworm.py --topics 11
python bookworm.py --entities 11
```

Générer une couverture et un nuage de mots :

```bash
python bookworm.py --cover 11
python bookworm.py --cloud 11
```

Rechercher des livres similaires parmi les résumés disponibles :

```bash
python bookworm.py --similar 11
```

Afficher la fiche complète du livre :

```bash
python bookworm.py --card 11
```

Afficher toutes les options disponibles :

```bash
python bookworm.py --help
```

### Options disponibles

| Option | Description |
| --- | --- |
| `--lexdiv` | Calcule les statistiques de diversité lexicale |
| `--summary` | Génère un résumé automatique du livre |
| `--summarize` | Alias de résumé pris en charge par le CLI |
| `--topics` | Extrait les mots-clés principaux de chaque section |
| `--entities` | Extrait les personnages et les lieux |
| `--cover` | Télécharge la couverture du livre |
| `--cloud` | Génère un nuage de mots au format PNG |
| `--similar` | Recherche jusqu’à cinq livres similaires |
| `--card` | Produit une fiche regroupant les analyses principales |

## Arborescence du projet

```text
Alice-in-Wonderland/
├── bookworm.py                 # Point d’entrée de la CLI
├── requirements.txt            # Dépendances Python
├── summaries.json              # Cache des résumés générés
└── src/
    ├── loader.py               # Téléchargement, nettoyage et cache des textes
    ├── book_summarizer.py      # Résumés BERT et BART
    ├── similarity.py           # Similarité TF-IDF et cosinus
    ├── topic_and_entities.py   # Thèmes, entités et validation des livres
    ├── summarizer_test.py      # Scénario de test sur plusieurs ouvrages
    └── data/
        ├── raw/                # Textes Gutenberg téléchargés
        └── processed/          # Analyses lexicales et fichiers générés
```

Les dossiers `src/data/raw/` et `src/data/processed/` sont alimentés
automatiquement au fil des analyses. Les modèles de langage peuvent également
être téléchargés dans le cache local de votre environnement Python.

## Ce que j’ai appris / Défis techniques

### Mettre en place une chaîne NLP complète

Le projet m’a permis de construire une chaîne de traitement de bout en bout :
acquisition des données, nettoyage des métadonnées Gutenberg, découpage par
chapitres, tokenisation, extraction d’informations et génération d’un résultat
présentable à l’utilisateur.

### Combiner plusieurs approches de résumé

Un texte long ne peut pas toujours être envoyé directement à un modèle de
transformers. J’ai donc appris à le découper en blocs, à extraire d’abord les
phrases les plus représentatives avec BERT, puis à produire un résumé plus
naturel avec BART. Cette approche impose de gérer les limites de longueur des
modèles, les textes courts et les résultats incomplets.

### Gérer les données externes et le cache

Les données provenant de Project Gutenberg ne sont pas toujours disponibles
avec exactement la même URL ou le même format. Le chargeur prévoit plusieurs
URLs de secours et un cache local pour éviter de retélécharger un ouvrage à
chaque exécution. Les analyses lexicales et les résumés sont eux aussi
persistés dans des fichiers JSON.

### Réduire le bruit dans l’extraction d’entités

L’extraction automatique d’entités produit parfois des résultats indésirables
dans les titres de chapitres, les métadonnées ou les notes éditoriales. La
normalisation des noms, la suppression des mots parasites et la déduplication
des résultats améliorent la qualité des personnages et lieux retournés.

### Comparer des livres avec des représentations vectorielles

La recherche de livres similaires m’a permis d’appliquer TF-IDF et la
similarité cosinus à des résumés textuels. Cette étape illustre comment
transformer des textes en vecteurs numériques afin de comparer leur contenu
et de classer les ouvrages les plus proches.

## Limites et pistes d’amélioration

- Ajouter des tests unitaires automatisés pour chaque module et chaque option
  de la CLI.
- Rendre la langue d’analyse configurable au lieu de cibler principalement
  les textes anglais.
- Remplacer les imports globaux par des imports explicites et améliorer la
  gestion centralisée des erreurs réseau.
- Ajouter une sortie structurée (JSON ou CSV) pour faciliter l’exploitation
  des résultats dans une autre application.
- Fournir une interface web légère pour consulter les fiches et visualisations.

## Licence et données

BookWorm s’appuie sur les textes et métadonnées accessibles via
[Project Gutenberg](https://www.gutenberg.org/). Vérifiez les conditions
d’utilisation et le statut légal d’un ouvrage selon votre pays avant toute
redistribution.
