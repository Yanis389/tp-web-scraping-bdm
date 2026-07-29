# 🎬 Projet Scrapy : Extraction de Films sur AlloCiné

**Framework :** Scrapy  
**Formation :** Mastère Dev, Data & IA — IPSSI  
**Sujet traité :** Extraction des fiches films (titre, réalisateur, année, notes presse/spectateurs) depuis AlloCiné

---

## 🎯 1. Objectifs du Projet

Ce projet met en place une araignée (*spider*) Scrapy chargée de parcourir des fiches films sur `www.allocine.fr` afin d'en extraire les informations éditoriales principales, de les nettoyer via un pipeline dédié, puis de les exporter automatiquement dans deux formats (`JSON` et `CSV`).

Les champs collectés pour chaque film sont :

| Champ | Type | Description |
| :--- | :--- | :--- |
| `titre` | `str` | Titre du film, généralement suivi du nom du réalisateur |
| `annee` | `str` | Date de sortie brute |
| `realisateur` | `str` | Nom du réalisateur |
| `note_presse` | `float` | Note moyenne de la presse (sur 5) |
| `note_spectateurs` | `float` | Note moyenne des spectateurs (sur 5), peut être `null` si le film n'a pas encore de notes |
| `url` | `str` | URL de la fiche film AlloCiné |

---

## 🗂️ 2. Structure du Projet

```
allocine/
├── scrapy.cfg              # Point d'entrée Scrapy (projet = allocine)
└── allocine/
    ├── __init__.py
    ├── items.py             # Définition du FilmItem
    ├── pipelines.py         # CleanPipeline : nettoyage & typage
    ├── settings.py          # Configuration (politesse, feeds, pipelines...)
    └── spiders/
        └── films.py         # Spider "films"
```

---

## 🕷️ 3. Le Spider `films`

```python
class FilmsSpider(scrapy.Spider):
    name = "films"
    allowed_domains = ["www.allocine.fr"]
    start_urls = ["https://www.allocine.fr"]

    def parse(self, response):
        pass
```

> ⚠️ **État actuel :** la méthode `parse()` est un squelette (`pass`) à compléter. Elle doit :
> 1. Sélectionner les fiches films de la page (sélecteurs CSS/XPath sur les blocs de contenu AlloCiné).
> 2. Instancier un `FilmItem` par film trouvé et le renvoyer (`yield`).
> 3. Gérer la pagination éventuelle (`response.follow` vers la page suivante).
>
> Le fichier `films.json` fourni dans ce dépôt illustre le résultat attendu une fois le spider finalisé (10 films, dont la trilogie *Le Seigneur des Anneaux* en version longue, dont les notes spectateurs sont encore à `null`).

---

## 🧼 4. Le Pipeline `CleanPipeline`

Défini dans `pipelines.py`, ce pipeline s'exécute sur chaque item collecté :

- **Nettoyage des champs texte** (`titre`, `realisateur`, `annee`) : suppression des espaces superflus via `.strip()`.
- **Typage des notes** (`note_presse`, `note_spectateurs`) :
  - Remplacement de la virgule décimale par un point (`"4,5"` → `4.5`).
  - Conversion en `float`.
  - Si la conversion échoue ou si la valeur est absente, le champ est mis à `None` plutôt que de faire échouer l'item.

---

## ⚙️ 5. Configuration (`settings.py`)

| Paramètre | Valeur | Rôle |
| :--- | :--- | :--- |
| `ROBOTSTXT_OBEY` | `True` | Respect du `robots.txt` du site |
| `USER_AGENT` | `IPSSI-scraper (+contact@ipssi.fr)` | Identification honnête du bot |
| `DOWNLOAD_DELAY` | `1.0` s | Délai de politesse entre les requêtes |
| `RANDOMIZE_DOWNLOAD_DELAY` | `True` | Évite un pattern de requêtes trop régulier |
| `CONCURRENT_REQUESTS` / `_PER_DOMAIN` | `4` / `2` | Limite la charge sur le serveur cible |
| `AUTOTHROTTLE_ENABLED` | `True` | Ajuste dynamiquement le débit (1s → 10s) |
| `RETRY_ENABLED` | `True` (3 essais) | Relance en cas d'erreur `500/502/503/429` |
| `ITEM_PIPELINES` | `CleanPipeline` (priorité 100) | Nettoyage systématique avant export |
| `FEEDS` | `films.json`, `films.csv` | Double export automatique en UTF-8, JSON indenté |

---

## 📦 6. Format des Exports

### `films.json`
Export JSON indenté (2 espaces), tableau d'objets `FilmItem`. Exemple d'entrée :

```json
{
  "titre": "Le Parrain de Francis Ford Coppola",
  "annee": "18 octobre 1972",
  "realisateur": "18 octobre 1972",
  "note_presse": 4.6,
  "note_spectateurs": 4.5,
  "url": "https://www.allocine.fr/film/fichefilm_gen_cfilm=1628.html"
}
```

> 💡 À noter : dans les données actuelles, les champs `annee` et `realisateur` contiennent la même valeur (la date de sortie). Cela suggère que le sélecteur du réalisateur reste à ajuster dans le spider pour extraire réellement le nom du metteur en scène plutôt que la date.

### `films.csv`
Export CSV équivalent, une ligne par film, généré automatiquement par Scrapy à partir des mêmes items.

---

## 🚀 7. Guide d'Exécution

```bash
# 1. Installer les dépendances
pip install scrapy itemadapter

# 2. Se placer à la racine du projet (là où se trouve scrapy.cfg)
cd allocine/

# 3. Lancer le spider (les fichiers films.json et films.csv sont générés automatiquement)
scrapy crawl films

# 4. Vérifier les exports
cat films.json
cat films.csv
```

---

## 🔧 8. Pistes d'Amélioration

- Compléter la logique d'extraction dans `parse()` (sélecteurs CSS/XPath réels d'AlloCiné).
- Corriger l'extraction du champ `realisateur` pour qu'il ne duplique pas `annee`.
- Ajouter une gestion de pagination pour parcourir plusieurs pages de classement (ex. Top Films).
- Ajouter des tests unitaires sur `CleanPipeline` (valeurs manquantes, virgules, chaînes vides).
