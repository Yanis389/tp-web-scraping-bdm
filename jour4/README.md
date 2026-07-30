# ⚡ TP Jour 4 : APIs Cachées, Asynchronisme & Playwright

**Développeur :** Yanis Helali  
**Formation :** Mastère Dev, Data & IA — IPSSI  
**Sujets traités :** Reverse Engineering d'APIs REST (httpx/asyncio) & Automation Playwright

---

## 🎯 1. Synthèse et Choix Techniques

Ce TP explore les approches avancées de collecte de données pour surmonter les limitations des scrapers synchrones et des interfaces dynamiques complexes.

### Pourquoi `httpx` + `asyncio` pour les APIs REST ?
- **Performance Asynchrone :** Réalisation simultanée des requêtes I/O sans bloquer l'exécuteur Python.
- **Réduction du temps d'exécution :** Gain de temps multiplicatif par rapport aux requêtes séquentielles `requests`.
- **Contrôle de débit (*Rate Limiting*) :** Utilisation d'un `asyncio.Semaphore` pour éviter les blocages IP (HTTP 429).

### Pourquoi Playwright par rapport à Selenium ?
- **Architecture Moderne :** Connexion directe via le protocole Chrome DevTools (CDP).
- **Attente Automatique (*Auto-waiting*) :** Elimination des erreurs `ElementNotFound` sans recourir à des `sleep` arbitraires.
- **Exécution Headless Optimisée :** Empreinte mémoire réduite et performances supérieures en environnement CI/CD.

---

## 📊 2. Benchmark d'Exécution

| Méthode | Outil | Temps moyen (10 pages) | Mode d'accès |
| :--- | :--- | :--- | :--- |
| **Scraping API Asynchrone** | `httpx` + `asyncio` | ~0.8s | Reconstitution des endpoints JSON |
| **Automation Navigateur** | `Playwright (Headless)` | ~2.4s | Execution du moteur V8 & DOM dynamique |

---

## 🚀 3. Exécution & Vérification

```bash
# Activation de l'environnement virtuel et installation
source ../.venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# Exécution du scraper API asynchrone
python api_scraper.py

# Exécution du scraper Playwright
python playwright_scraper.py