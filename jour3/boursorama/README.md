# 📈 Projet Scrapy : Extraction de Valeurs Boursières (Boursorama)

**Framework :** Scrapy  
**Formation :** Mastère Dev, Data & IA — IPSSI  
**Sujet traité :** Extraction de cotations boursières (libellé, cours, variation, volume, ISIN) et persistance en base SQLite

---

## 🎯 1. Objectifs du Projet

Ce projet met en place un pipeline Scrapy destiné à collecter des données de cotation boursière (a priori depuis `boursorama.com`) et à les stocker directement dans une base de données **SQLite** (`bourse.db`), avec une protection contre les doublons via la clé ISIN.

Les champs collectés pour chaque action sont :

| Champ | Type | Description |
| :--- | :--- | :--- |
| `libelle` | `str` | Nom de la valeur boursière |
| `cours` | `float` | Cours de l'action |
| `variation` | `float` | Variation (en %) par rapport à la séance précédente |
| `volume` | `int` | Volume de titres échangés |
| `isin` | `str` | Code ISIN (identifiant unique international de la valeur) |

---

## 🗂️ 2. Structure du Projet

```
boursorama/
├── scrapy.cfg              # Point d'entrée Scrapy (projet = boursorama)
├── bourse.db                # Base SQLite générée à l'exécution (table "actions")
└── boursorama/
    ├── __init__.py
    ├── items.py             # Définition de l'ActionItem
    ├── pipelines.py         # SQLitePipeline : persistance en base
    ├── settings.py          # Configuration (politesse, pipelines...)
    └── spiders/
        └── (spider à implémenter, ex. "bourse.py")
```

> ⚠️ Le fichier du spider (logique de parsing des pages Boursorama) n'a pas été fourni dans ce dépôt : seuls `items.py`, `pipelines.py`, `settings.py` et `scrapy.cfg` sont présents, aux côtés de la base `bourse.db` déjà générée par une exécution précédente. Le spider reste donc à créer/compléter dans `boursorama/spiders/`.

---

## 🗄️ 3. Le Pipeline `SQLitePipeline`

Défini dans `pipelines.py`, ce pipeline gère tout le cycle de vie de la base de données :

- **`open_spider`** : connexion à `bourse.db` et création de la table `actions` si elle n'existe pas (via le DDL ci-dessous).
- **`process_item`** : insertion de chaque item avec `INSERT OR IGNORE`, ce qui **évite les doublons** grâce à la contrainte `UNIQUE` sur `isin`. Les erreurs SQLite sont capturées et journalisées (`spider.logger.error`) sans interrompre le crawl.
- **`close_spider`** : log du nombre total d'actions enregistrées, puis fermeture propre de la connexion.

### Schéma de la table `actions`

```sql
CREATE TABLE IF NOT EXISTS actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    libelle TEXT NOT NULL,
    cours REAL,
    variation REAL,
    volume INTEGER,
    isin TEXT UNIQUE,
    scraped_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

Le champ `scraped_at` est horodaté automatiquement (`CURRENT_TIMESTAMP`) à chaque insertion, ce qui permet de tracer la date de collecte de chaque cotation.

---

## ⚙️ 4. Configuration (`settings.py`)

| Paramètre | Valeur | Rôle |
| :--- | :--- | :--- |
| `ROBOTSTXT_OBEY` | `True` | Respect du `robots.txt` du site |
| `USER_AGENT` | `IPSSI-scraper (+contact@ipssi.fr)` | Identification honnête du bot |
| `DOWNLOAD_DELAY` | `1.0` s | Délai de politesse entre les requêtes |
| `RANDOMIZE_DOWNLOAD_DELAY` | `True` | Évite un pattern de requêtes trop régulier |
| `ITEM_PIPELINES` | `SQLitePipeline` (priorité 300) | Persistance directe en base SQLite |
| `REQUEST_FINGERPRINTER_IMPLEMENTATION` | `"2.7"` | Empreinte de requêtes conforme aux versions récentes de Scrapy |
| `TWISTED_REACTOR` | `AsyncioSelectorReactor` | Réacteur asynchrone requis pour les fonctionnalités Scrapy récentes |

> ℹ️ Contrairement au projet AlloCiné, aucun export `FEEDS` (JSON/CSV) n'est configuré ici : la donnée est directement persistée en base, ce qui est adapté à un usage de suivi/mise à jour régulier des cotations (upsert implicite via `INSERT OR IGNORE`).

---

## 🚀 5. Guide d'Exécution

```bash
# 1. Installer les dépendances
pip install scrapy itemadapter

# 2. Se placer à la racine du projet (là où se trouve scrapy.cfg)
cd boursorama/

# 3. Lancer le spider (adapter "bourse" au nom réel du spider une fois créé)
scrapy crawl bourse

# 4. Interroger la base générée
python3 -c "
import sqlite3
cx = sqlite3.connect('bourse.db')
for row in cx.execute('SELECT * FROM actions LIMIT 10'):
    print(row)
"
```

---

## 🔧 6. Pistes d'Amélioration

- Implémenter le spider manquant : sélection des lignes de cotation sur les pages Boursorama, extraction des champs `libelle`, `cours`, `variation`, `volume`, `isin`.
- Ajouter une politique de retry (`RETRY_ENABLED`, `AUTOTHROTTLE_ENABLED`) similaire au projet AlloCiné pour renforcer la robustesse face aux erreurs `429`/`5xx`.
- Ajouter une commande ou un script de purge/rafraîchissement (ex. `UPSERT` au lieu de `INSERT OR IGNORE` pour mettre à jour le cours d'une valeur déjà connue plutôt que de l'ignorer).
- Ajouter des index sur `libelle` pour accélérer les recherches si le volume de données augmente.
