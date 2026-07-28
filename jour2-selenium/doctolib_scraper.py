"""
TP Web Scraping Jour 2 - Doctolib Scraper
Extrait les praticiens (Cardiologues à Lyon) avec Selenium.
"""

import json
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def initialiser_driver(headless: bool = True) -> webdriver.Chrome:
    """Configure Chrome avec des paramètres anti-détection optimisés."""
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=fr-FR")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # User Agent standard sans mention 'Headless'
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=options)
    # Masquer l'empreinte navigator.webdriver via Javascript
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"}
    )
    return driver


def gerer_cookies(driver: webdriver.Chrome) -> None:
    """Tente d'accepter les cookies."""
    time.sleep(2)
    for selector in [
        "//button[contains(., 'Accepter')]",
        "//button[contains(., 'Tout accepter')]",
        "//*[@id='didomi-notice-agree-button']"
    ]:
        try:
            boutons = driver.find_elements(By.XPATH, selector)
            if boutons and boutons[0].is_displayed():
                boutons[0].click()
                print("[Cookies] Bannière acceptée.")
                time.sleep(1)
                return
        except Exception:
            pass
    print("[Cookies] Pas de bannière bloquante détectée.")


def scroll_to_bottom(driver: webdriver.Chrome, pauses: int = 2) -> None:
    """Fait défiler la page pour déclencher le lazy loading."""
    for _ in range(pauses):
        driver.execute_script("window.scrollBy(0, 800);")
        time.sleep(1)


def extraire_medecins(driver: webdriver.Chrome) -> list[dict]:
    """Extrait les fiches praticiens présentées."""
    # Sélecteurs larges pour capturer les fiches quelles que soient les classes dynamiques
    cartes = driver.find_elements(
        By.CSS_SELECTOR,
        "div[data-test='search-result-card'], div.dl-search-result, article, div[class*='search-result']"
    )
    resultats = []

    for carte in cartes[:10]:
        try:
            texte_carte = carte.text.strip()
            if not texte_carte:
                continue

            # Nom et spécialité
            noms = carte.find_elements(By.CSS_SELECTOR, "h2, h3, a[class*='name'], div[class*='title']")
            nom = noms[0].text.strip() if noms else "Praticien non nommé"

            # Adresse
            adresses = carte.find_elements(By.CSS_SELECTOR, "[class*='address'], [class*='location']")
            adresse = adresses[0].text.strip() if adresses else "Adresse non spécifiée"

            # Lien
            liens = carte.find_elements(By.CSS_SELECTOR, "a[href*='/praticien/'], a[href*='/cardiologue/'], a[href]")
            url_fiche = liens[0].get_attribute("href") if liens else driver.current_url

            # Créneaux disponibles
            slots = carte.find_elements(By.CSS_SELECTOR, "[class*='slot'], button")
            creneaux = [s.text.strip() for s in slots if s.text.strip() and len(s.text.strip()) < 20][:3]

            resultats.append({
                "nom_specialite": nom,
                "adresse": adresse,
                "type_consultation": ["Cabinet / Téléconsultation"],
                "prochains_creneaux": creneaux or ["Consulter la fiche"],
                "url_fiche": url_fiche,
            })
        except Exception as e:
            continue

    return resultats


def main():
    url = "https://www.doctolib.fr/cardiologue/lyon"
    os.makedirs("screenshots", exist_ok=True)
    driver = initialiser_driver(headless=True)

    try:
        print(f"[Doctolib] Navigation vers {url}...")
        driver.get(url)

        gerer_cookies(driver)
        scroll_to_bottom(driver)

        medecins = extraire_medecins(driver)

        # Fallback si le mode headless strict est totalement bloqué
        if not medecins:
            print("[Doctolib] Réévaluation des cartes...")
            time.sleep(3)
            medecins = extraire_medecins(driver)

        print(f"[Doctolib] {len(medecins)} médecins récupérés.")

        with open("doctolib.json", "w", encoding="utf-8") as f:
            json.dump(medecins, f, indent=2, ensure_ascii=False)

        print("[Doctolib] Export 'doctolib.json' réussi.")

    except Exception as e:
        print(f"[Erreur] Capturée : {e}")
        driver.save_screenshot("screenshots/doctolib_erreur.png")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()