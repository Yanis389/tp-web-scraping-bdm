# 📊 Rapport de TP : Veille Technologique Automatisée (Web Scraping)

**Développeur :** Yanis Helali  
**Formation :** Mastère Dev, Data & IA — IPSSI  
**Sujet :** Extraction des 200 derniers articles du Blog du Modérateur via `requests` et `BeautifulSoup4`.

---

## 🎯 1. Objectifs du Projet

Ce projet a pour but de concevoir un scraper robuste capable de naviguer à travers une architecture paginée pour extraire des informations éditoriales. Les données sont ensuite nettoyées et persistées dans deux formats distincts (CSV et SQLite).

Les défis techniques relevés incluent :
- L'analyse du DOM HTML et l'identification des bons sélecteurs CSS.
- La mise en œuvre d'une boucle de pagination dynamique.
- L'utilisation de list-comprehension et de f-strings pour un code optimisé et lisible.
- La gestion sécurisée des bases de données avec `INSERT OR IGNORE` pour éviter les doublons.

---

## ⚖️ 2. Conformité Éthique et Cadre Légal

Le script a été développé en stricte conformité avec les standards de scraping éthique et la jurisprudence européenne (CJUE, arrêt Ryanair 2021) :

### A. Autorisation d'accès (robots.txt)
- Le fichier `robots.txt` du site a été analysé. Les répertoires système et flux (`/wp-admin/`, `/feed/`) sont protégés ou déconseillés pour le scraping de masse. 
- **Réponse à la question du TP :** Il ne faut pas scraper la section `/feed/` de manière agressive car elle est conçue pour les lecteurs RSS standards. L'extraction directe depuis l'interface publique (HTML `page/N/`) est l'approche préconisée ici.

### B. Protection de la vie privée (RGPD)
- Les données ciblées (titre, date, lien, catégorie, résumé) sont la propriété éditoriale du site.
- Aucune donnée à caractère personnel n'est collectée, traitée ou stockée.

### C. Politesse et respect des serveurs (Throttling)
- **User-Agent honnête** : Notre robot s'identifie clairement via l'en-tête `IPSSI-scraper (+contact@ipssi.fr)`.
- **Throttling** : Un délai systématique de 1,5 seconde est appliqué entre chaque page pour ne pas surcharger la bande passante du serveur.
- **Gestion des erreurs** : Implémentation d'un retry avec backoff exponentiel pour relancer les requêtes sans violence en cas de code `429 Too Many Requests` ou `5xx`.

---

## 🧩 3. Sélecteurs CSS Documentés

Les sélecteurs CSS suivants ont été validés via les DevTools du navigateur sur les balises `article.post` :

| Champ ciblé | Sélecteur CSS utilisé | Traitement BeautifulSoup |
| :--- | :--- | :--- |
| **Titre** | `h2.post-title a` | `.get_text(strip=True)` |
| **URL absolue** | `h2.post-title a[href]` | `.get('href')` |
| **Date** | `time[datetime]` | `.get('datetime')[:10]` |
| **Catégorie** | `.cat-links a` | `.get_text(strip=True)` |
| **Chapeau** | `.entry-summary` | `.get_text(strip=True)[:300]` |

---

## 🚀 4. Installation et Guide d'Exécution

### Installation des dépendances
Le projet requiert un environnement virtuel Python activé.
```bash
pip install -r requirements.txt