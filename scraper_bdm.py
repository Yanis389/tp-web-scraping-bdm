"""
Veille Technologique Automatisée - Scraper Blog du Modérateur
Ce script extrait les 200 derniers articles via une boucle de pagination robuste.
Il utilise requests, BeautifulSoup4, CSV et SQLite.
"""

import argparse
import csv
import sqlite3
import time
import requests
from bs4 import BeautifulSoup

# En-têtes HTTP éthiques pour s'identifier auprès du serveur cible
HEADERS = {
    "User-Agent": "IPSSI-scraper (+contact@ipssi.fr)",
    "Accept-Language": "fr-FR,fr;q=0.9",
}

BASE_URL = "https://www.blogdumoderateur.com/page/{n}/"
MAX_ARTICLES_DEFAULT = 200

# Requête de création de la table SQLite
# L'attribut UNIQUE sur l'URL permet de dédupliquer les données lors de l'insertion
DDL_SQLITE = """
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    date TEXT,
    categorie TEXT,
    chapeau TEXT,
    scraped_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

def get_page(url: str, tries: int = 3) -> BeautifulSoup:
    """
    Récupère le code HTML d'une page avec un mécanisme de retry exponentiel.
    Gère spécifiquement l'erreur 429 (Too Many Requests).
    """
    for attempt in range(tries):
        try:
            # Requête avec un timeout de 10 secondes pour éviter les blocages
            response = requests.get(url, headers=HEADERS, timeout=10)

            # Si le serveur nous dit d'attendre (Throttle / Code 429)
            if response.status_code == 429:
                wait = int(response.headers.get("Retry-After", 10))
                print(f"[429] Trop de requêtes. Pause de {wait} secondes...")
                time.sleep(wait)
                continue

            # Lève une exception pour les autres erreurs HTTP (ex: 404, 500)
            response.raise_for_status()
            
            # Retourne l'objet BeautifulSoup pour le parsing HTML
            return BeautifulSoup(response.text, "lxml")

        except requests.Timeout:
            print(f"[Timeout] Échec de la tentative {attempt + 1}/{tries} (Délai dépassé).")
            time.sleep(2 ** attempt)  # Backoff exponentiel : 1s, 2s, 4s...
            
        except requests.HTTPError as e:
            # Si c'est une erreur client (ex: 404), on arrête tout (ne sert à rien de réessayer)
            if e.response is not None and e.response.status_code < 500:
                print(f"[Erreur 4xx] Erreur définitive sur {url}")
                raise
            print(f"[Erreur Serveur] Tentative {attempt + 1}/{tries} : {e}")
            time.sleep(2 ** attempt)
            
        except requests.RequestException as e:
            print(f"[Erreur Réseau] Tentative {attempt + 1}/{tries} : {e}")
            time.sleep(2 ** attempt)

    # Si la boucle se termine sans succès
    raise RuntimeError(f"Échec définitif de la requête après {tries} tentatives sur {url}")


def parse_articles(soup: BeautifulSoup) -> list[dict]:
    """
    Extrait les données (titre, url, date, catégorie, chapeau) via les sélecteurs CSS.
    Utilisation exigée d'une list-comprehension.
    """
    # Sélectionne toutes les cartes d'articles sur la page
    cards = soup.select("article.post")

    return [
        {
            # Extraction du texte du titre sans espaces superflus
            "titre": card.select_one("h2.post-title a").get_text(strip=True),
            
            # Gestion des URLs : on s'assure qu'elles soient absolues
            "url": (
                card.select_one("h2.post-title a")["href"]
                if card.select_one("h2.post-title a")["href"].startswith("http")
                else f"https://www.blogdumoderateur.com{card.select_one('h2.post-title a')['href']}"
            ),
            
            # Extraction des 10 premiers caractères de l'attribut datetime (YYYY-MM-DD)
            "date": (card.select_one("time[datetime]") or {}).get("datetime", "")[:10],
            
            # Extraction de la catégorie, ou "Non classé" par défaut
            "categorie": (
                card.select_one(".cat-links a") or card.select_one(".category") or {"get_text": lambda **k: "Non classé"}
            ).get_text(strip=True) if (card.select_one(".cat-links a") or card.select_one(".category")) else "Non classé",
            
            # Extraction du chapeau limité aux 300 premiers caractères
            "chapeau": (
                card.select_one(".entry-summary") or card.select_one(".post-excerpt") or {"get_text": lambda **k: ""}
            ).get_text(strip=True)[:300] if (card.select_one(".entry-summary") or card.select_one(".post-excerpt")) else "",
        }
        for card in cards
        # Condition de la list-comprehension : on ne prend que si un titre existe
        if card.select_one("h2.post-title a")
    ]


def scrape_all(max_articles: int = MAX_ARTICLES_DEFAULT) -> list[dict]:
    """
    Boucle de pagination pour scraper les pages une par une jusqu'à atteindre l'objectif.
    """
    tous_articles = []
    page = 1

    while len(tous_articles) < max_articles:
        # Construction de l'URL (la page 1 n'a pas de /page/1/)
        url = "https://www.blogdumoderateur.com/" if page == 1 else BASE_URL.format(n=page)
        
        # Log via f-string comme exigé
        print(f"[Scraping] Interrogation de la page {page} : {url}")

        try:
            soup = get_page(url)
        except Exception as e:
            print(f"[Stop] Erreur fatale rencontrée : {e}")
            break

        nouveaux = parse_articles(soup)
        
        if not nouveaux:
            print(f"[Info] Plus aucun article trouvé à la page {page}. Fin du scraping.")
            break

        tous_articles.extend(nouveaux)
        print(f"[Avancement] {len(nouveaux)} articles trouvés | Cumul total : {len(tous_articles)}/{max_articles}")

        page += 1
        
        # Throttling imposé : délai de 1.5s entre chaque requête pour être éthique
        time.sleep(1.5)

    return tous_articles[:max_articles]


def sauver_csv(articles: list[dict], chemin: str = "articles.csv") -> None:
    """Sauvegarde les articles extraits dans un fichier CSV (UTF-8)."""
    champs = ["titre", "url", "date", "categorie", "chapeau"]
    with open(chemin, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=champs, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(articles)
    print(f"[Export] Fichier CSV généré : {chemin} ({len(articles)} lignes)")


def sauver_sqlite(articles: list[dict], chemin: str = "articles.db") -> None:
    """Sauvegarde les articles en base de données SQLite avec déduplication."""
    with sqlite3.connect(chemin) as cx:
        cx.execute(DDL_SQLITE)
        inserted = 0
        for article in articles:
            # INSERT OR IGNORE permet de ne pas planter ni dupliquer si l'URL existe déjà
            cursor = cx.execute(
                """
                INSERT OR IGNORE INTO articles (titre, url, date, categorie, chapeau)
                VALUES (:titre, :url, :date, :categorie, :chapeau)
                """,
                article,
            )
            inserted += cursor.rowcount
        cx.commit()
    print(f"[Export] Base SQLite mise à jour : {chemin} ({inserted} nouvelles insertions)")


def main():
    """Point d'entrée du script avec gestion des arguments en ligne de commande."""
    parser = argparse.ArgumentParser(description="Script de Web Scraping - Blog du Modérateur")
    parser.add_argument("--max", type=int, default=MAX_ARTICLES_DEFAULT, help="Nb max d'articles")
    parser.add_argument("--csv", default="articles.csv", help="Fichier CSV de sortie")
    parser.add_argument("--db", default="articles.db", help="Base SQLite de sortie")

    args = parser.parse_args()

    print(f"=== Début du traitement | Objectif : {args.max} articles ===")
    
    articles = scrape_all(args.max)

    if articles:
        sauver_csv(articles, args.csv)
        sauver_sqlite(articles, args.db)
        print("=== Scraping terminé avec succès ===")
    else:
        print("=== Aucun article n'a pu être récupéré ===")

if __name__ == "__main__":
    main()