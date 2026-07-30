import asyncio
import json
import os
from playwright.async_api import async_playwright

OUTPUT_FILE = "data/books_playwright.json"
TARGET_URL = "https://books.toscrape.com/"


async def run():
    os.makedirs("data", exist_ok=True)
    print("[PLAYWRIGHT] Lancement du navigateur Chromium Headless...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            viewport={"width": 1280, "height": 800},
        )
        page = await context.new_page()

        print(f"[PLAYWRIGHT] Navigation vers {TARGET_URL}...")
        await page.goto(TARGET_URL, wait_until="networkidle")

        # Extraction via sélecteurs du DOM simulé
        books_elements = await page.query_selector_all("article.product_pod")
        books_data = []

        for book in books_elements:
            title_el = await book.query_selector("h3 a")
            price_el = await book.query_selector(".price_color")
            availability_el = await book.query_selector(".availability")

            title = await title_el.get_attribute("title") if title_el else ""
            price_text = await price_el.inner_text() if price_el else "0"
            availability = await availability_el.inner_text() if availability_el else ""

            # Transformation numérique du prix
            price_clean = float(price_text.replace("£", "").replace("€", "").strip())

            books_data.append(
                {
                    "titre": title.strip(),
                    "prix": price_clean,
                    "disponibilite": availability.strip(),
                }
            )

        await browser.close()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(books_data, f, indent=2, ensure_ascii=False)

    print(f"[SUCCÈS] {len(books_data)} livres extraits via Playwright et enregistrés dans '{OUTPUT_FILE}'")


if __name__ == "__main__":
    asyncio.run(run())