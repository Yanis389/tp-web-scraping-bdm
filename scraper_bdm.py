"""
Veille Technologique Automatisée - Scraper Blog du Modérateur
Ce script extrait les 200 derniers articles via une boucle de pagination robuste.
Il utilise requests, BeautifulSoup4, CSV et SQLite.

NOTE (mise à jour) : le thème du Blog du Modérateur a changé depuis la rédaction
initiale du TP. Les sélecteurs CSS ont été ré-identifiés en juillet 2026 :
  - titre      : h2.post-title a   ->  h3.entry-title
  - catégorie  : .cat-links a      ->  .favtag
  - date       : time[datetime]    ->  inchangé
  - URL        : h2.post-title a   ->  aucun <a> direct dans <article>,
                 on remonte jusqu'au premier ancêtre <a> (find_parent).
  - chapeau    : .entry-summary    ->  absent sur la page d'accueil : on tente
                 plusieurs fallback, sinon chaîne vide.
"""

import argparse
import csv
import sqlite3
import time
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "IPSSI-scraper (+contact@ipssi.fr)",
    "Accept-Language": "fr-FR,fr;q=0.9",
}

BASE_URL = "https://www.blogdumoderateur.com/page/{n}/"
MAX_ARTICLES_DEFAULT = 200

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
            response = requests.get(url, headers=HEADERS, timeout=10)

            if response.status_code == 429:
                wait = int(response.headers.get("Retry-After", 10))
                print(f"[429] Trop de requêtes. Pause de {wait} secondes...")
                time.sleep(wait)
                continue

            response.raise_for_status()
            return BeautifulSoup(response.text, "lxml")

        except requests.Timeout:
            print(f"[Timeout] Échec de la tentative {attempt + 1}/{tries} (Délai dépassé).")
            time.sleep(2 ** attempt)

        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code < 500:
                print(f"[Erreur 4xx] Erreur définitive sur {url}")
                raise
            print(f"[Erreur Serveur] Tentative {attempt + 1}/{tries} : {e}")
            time.sleep(2 ** attempt)

        except requests.RequestException as e:
            print(f"[Erreur Réseau] Tentative {attempt + 1}/{tries} : {e}")
            time.sleep(2 ** attempt)

    raise RuntimeError(f"Échec définitif de la requête après {tries} tentatives sur {url}")


def _extraire_url(card) -> str:
    """
    Cherche l'URL de l'article. Le nouveau thème ne place plus le <a> à
    l'intérieur de <article> : on remonte donc les ancêtres jusqu'au
    premier <a href>. Si rien n'est trouvé, on cherche un <a> à l'intérieur
    de la carte (au cas où une future variante du thème en aurait un).
    """
    lien_ancetre = card.find_parent("a")
    if lien_ancetre and lien_ancetre.get("href"):
        href = lien_ancetre["href"]
    else:
        lien_interne = card.select_one("a[href]")
        href = lien_interne["href"] if lien_interne else ""

    if not href:
        return ""
    if href.startswith("http"):
        return href
    return f"https://www.blogdumoderateur.com{href}"


def parse_articles(soup: BeautifulSoup) -> list[dict]:
    """
    Extrait les données (titre, url, date, catégorie, chapeau) via les sélecteurs CSS.
    Utilisation exigée d'une list-comprehension.
    """
    cards = soup.select("article.post")

    return [
        {
            "titre": card.select_one("h3.entry-title").get_text(strip=True),

            "url": _extraire_url(card),

            "date": (card.select_one("time[datetime]") or {}).get("datetime", "")[:10],

            "categorie": (
                card.select_one(".favtag").get_text(strip=True)
                if card.select_one(".favtag") else "Non classé"
            ),

            "chapeau": (
                (card.select_one(".entry-summary") or card.select_one(".post-excerpt"))
                .get_text(strip=True)[:300]
                if (card.select_one(".entry-summary") or card.select_one(".post-excerpt"))
                else ""
            ),
        }
        for card in cards
        if card.select_one("h3.entry-title")
    ]


def scrape_all(max_articles: int = MAX_ARTICLES_DEFAULT) -> list[dict]:
    """
    Boucle de pagination pour scraper les pages une par une jusqu'à atteindre l'objectif.
    """
    tous_articles = []
    page = 1

    while len(tous_articles) < max_articles:
        url = "https://www.blogdumoderateur.com/" if page == 1 else BASE_URL.format(n=page)
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

        # On ignore les articles sans URL valide pour ne pas violer la contrainte UNIQUE
        avant = len(nouveaux)
        nouveaux = [a for a in nouveaux if a["url"]]
        if len(nouveaux) < avant:
            print(f"[Avertissement] {avant - len(nouveaux)} article(s) sans URL détectable, ignorés.")

        tous_articles.extend(nouveaux)
        print(f"[Avancement] {len(nouveaux)} articles trouvés | Cumul total : {len(tous_articles)}/{max_articles}")

        page += 1
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
