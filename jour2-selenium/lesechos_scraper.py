"""
TP Web Scraping Jour 2 - Les Echos Scraper
Vérification requests vs Selenium, benchmark Headless vs Headed.
"""

import json
import os
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By


def tester_requests(url: str) -> int:
    """Test avec requests + BeautifulSoup."""
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "lxml")
        titres = soup.select("article h2, article h3")
        return len(titres)
    except Exception:
        return 0


def make_driver(headless: bool = False) -> webdriver.Chrome:
    """Instancie le navigateur avec User-Agent explicite."""
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(options=options)


def gerer_cookies_lesechos(driver: webdriver.Chrome) -> None:
    """Ferme la bannière cookies si elle apparaît."""
    time.sleep(2)
    try:
        boutons = driver.find_elements(
            By.CSS_SELECTOR, "#didomi-notice-agree-button, button[class*='accept']"
        )
        if boutons:
            boutons[0].click()
            time.sleep(1)
    except Exception:
        pass


def extraire_articles(driver: webdriver.Chrome) -> list[dict]:
    """Extrait les cartes d'articles de la page d'accueil."""
    articles_elements = driver.find_elements(
        By.CSS_SELECTOR, "article, [class*='article-card'], [class*='story-card']"
    )
    results = []

    for art in articles_elements[:20]:
        try:
            titres = art.find_elements(By.CSS_SELECTOR, "h1, h2, h3, [class*='title']")
            titre = titres[0].text.strip() if titres else ""
            if not titre:
                continue

            rubriques = art.find_elements(By.CSS_SELECTOR, "[class*='rubrique'], [class*='section'], span")
            rubrique = rubriques[0].text.strip() if rubriques else "Économie"

            chapeaux = art.find_elements(By.CSS_SELECTOR, "p, [class*='chapo']")
            chapeau = chapeaux[0].text.strip()[:200] if chapeaux else ""

            heures = art.find_elements(By.CSS_SELECTOR, "time, [class*='date']")
            heure_publi = heures[0].text.strip() if heures else "Récent"

            premium = bool(art.find_elements(By.CSS_SELECTOR, "[class*='premium'], svg[class*='lock']"))

            results.append({
                "titre": titre,
                "rubrique": rubrique,
                "chapeau": chapeau,
                "heure_publi": heure_publi,
                "premium": premium,
            })
        except Exception:
            continue

    return results


def benchmark_modes(url: str) -> tuple[float, float, list[dict]]:
    """Mesure le temps d'exécution en mode Headed puis Headless."""
    # 1. Mode Normal
    print("[Benchmark] Lancement en mode normal (Headed)...")
    t0 = time.time()
    driver_normal = make_driver(headless=False)
    driver_normal.get(url)
    gerer_cookies_lesechos(driver_normal)
    articles_data = extraire_articles(driver_normal)
    t_normal = time.time() - t0
    driver_normal.quit()

    # 2. Mode Headless
    print("[Benchmark] Lancement en mode Headless...")
    t0 = time.time()
    driver_headless = make_driver(headless=True)
    driver_headless.get(url)
    gerer_cookies_lesechos(driver_headless)
    t_headless = time.time() - t0
    driver_headless.quit()

    return t_normal, t_headless, articles_data


def main():
    target_url = "https://www.lesechos.fr"

    print("=== ÉTAPE 1 : Test de faisabilité avec requests ===")
    nb_titres = tester_requests(target_url)
    print(f"[Requests] Balises trouvées : {nb_titres}")
    print("[Analyse] Le contenu est injecté dynamiquement -> Selenium nécessaire.\n")

    print("=== ÉTAPE 2 : Benchmark et Extraction Selenium ===")
    t_normal, t_headless, articles = benchmark_modes(target_url)

    print(f"\n--- RÉSULTATS BENCHMARK ---")
    print(f"Mode Normal   : {t_normal:.2f} s")
    print(f"Mode Headless : {t_headless:.2f} s")
    if t_headless > 0:
        print(f"Gain relatif  : {t_normal / t_headless:.2f}x plus rapide en Headless")

    with open("lesechos.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)

    print(f"\n[Les Echos] {len(articles)} articles exportés dans 'lesechos.json'.")


if __name__ == "__main__":
    main()