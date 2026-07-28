# 🎭 TP Jour 2 : Web Scraping Dynamique avec Selenium

**Développeur :** Yanis Helali  
**Formation :** Mastère Dev, Data & IA — IPSSI  
**Sujets traités :** Doctolib (Praticiens & Créneaux) & Les Echos (Titres à la une)

---

## 🎯 1. Synthèse et Choix Techniques

Ce TP explore le pilotage automatisé d'un navigateur web réel via **Selenium 4** pour surmonter les obstacles du web moderne :
- Le rendu dynamique côté client (Single Page Applications / JavaScript).
- La gestion des modales de consentement RGPD (bannières cookies).
- Le chargement différé (*lazy loading*) nécessitant un défilement du viewport.

### Pourquoi Selenium plutôt que `requests` + `BeautifulSoup` ?
Sur des plateformes comme Doctolib ou Les Echos, une requête HTTP brute via `requests` ne retourne qu'un squelette HTML. Les données utiles sont injectées ultérieurement par des scripts JavaScript. 

Lors de l'évaluation sur Les Echos :
- `requests` + `BeautifulSoup` : extrait une structure partielle incomplète sans les cartes de contenu chargées à la volée.
- `Selenium` : exécute le moteur V8 de Chrome, résout la pile JavaScript et permet d'interagir directement avec le DOM réel.

---

## ⚡ 2. Benchmark : Mode Normal vs Mode Headless

Les mesures d'exécution ont été effectuées sur la page d'accueil de Les Echos (temps d'initialisation, navigation, contournement cookies et attente d'apparition du DOM) :

| Mode de navigation | Temps moyen d'exécution | Différence / Gain |
| :--- | :--- | :--- |
| **Mode Normal (Headed)** | ~6.8 s | Référence (Rendu graphique actif) |
| **Mode Headless (`--headless=new`)** | ~2.9 s | **~2.3x plus rapide** |

**Conclusion technique :** Le mode Headless élimine la surcharge liée au rendu graphique de l'interface utilisateur (GPU/Compositing GUI). Il est à privilégier dans les environnements d'intégration continue (CI/CD) et les pipelines de collecte en production.

---

## 🛡️ 3. Gestion de la Robustesse et Sélecteurs de Secours (*Fallbacks*)

Les structures HTML des sites grand public évoluent fréquemment. Afin d'éviter les ruptures de pipeline, une stratégie de sélection résiliente a été intégrée :

1. **Attente Explicite (`WebDriverWait`) :** Remplacement systématique des pauses fixes (`time.sleep`) par l'attente d'événements précis du DOM (`EC.presence_of_element_located`).
2. **Sélecteurs CSS Multiples :** Chaque fonction d'extraction teste une série de sélecteurs de secours si la classe principale a changé (ex: `h2` -> `h3` -> `[class*='name']`).
3. **Capture d'écran de débogage :** En cas d'exception non gérée durant la navigation, le bloc `try/except` déclenche automatiquement un cliché de l'état du navigateur enregistré dans `screenshots/doctolib_erreur.png`.

---

## 🚀 4. Guide d'Exécution

```bash
# 1. Activation de l'environnement et installation
pip install -r requirements.txt

# 2. Exécution du scraper Doctolib
python doctolib_scraper.py

# 3. Exécution du scraper Les Echos & Benchmark
python lesechos_scraper.py