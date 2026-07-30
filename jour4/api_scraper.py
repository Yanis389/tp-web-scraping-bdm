import asyncio
import json
import os
import time
import httpx

# API cible : API JSON de Quotes to Scrape
BASE_URL = "https://quotes.toscrape.com/api/quotes?page={page}"
MAX_CONCURRENT_REQUESTS = 3
TOTAL_PAGES = 10
OUTPUT_FILE = "data/quotes_api.json"


async def fetch_page(client: httpx.AsyncClient, page: int, semaphore: asyncio.Semaphore) -> list:
    async with semaphore:
        url = BASE_URL.format(page=page)
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            quotes = data.get("quotes", [])
            print(f"[API] Page {page} récupérée ({len(quotes)} citations)")
            return quotes
        except Exception as e:
            print(f"[ERREUR] Échec de la récupération de la page {page}: {e}")
            return []


async def main():
    start_time = time.perf_counter()
    os.makedirs("data", exist_ok=True)
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    headers = {
        "User-Agent": "IPSSI-Master-DataScraper/1.0 (+contact@ipssi.fr)",
        "Accept": "application/json",
    }

    async with httpx.AsyncClient(headers=headers) as client:
        tasks = [fetch_page(client, page, semaphore) for page in range(1, TOTAL_PAGES + 1)]
        results = await asyncio.gather(*tasks)

    # Aplatir la liste des résultats
    all_quotes = [item for sublist in results for item in sublist]

    # Formater les données
    cleaned_data = [
        {
            "auteur": q.get("author", {}).get("name"),
            "citation": q.get("text"),
            "tags": q.get("tags", []),
        }
        for q in all_quotes
    ]

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

    elapsed = time.perf_counter() - start_time
    print(f"\n[SUCCÈS] {len(cleaned_data)} citations enregistrées dans '{OUTPUT_FILE}' en {elapsed:.2f}s")


if __name__ == "__main__":
    asyncio.run(main())