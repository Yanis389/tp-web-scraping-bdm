import scrapy
from boursorama.items import ActionItem

class CacSpider(scrapy.Spider):
    name = "cac"
    allowed_domains = ["boursorama.com"]
    start_urls = ["https://www.boursorama.com/bourse/actions/palmares/france/"]

    def parse(self, response):
        rows = response.css("table.c-table tbody tr")
        for row in rows:
            cells = row.css("td.c-table__cell")
            if len(cells) < 4:
                cells = row.css("td")
            if len(cells) < 4:
                continue

            link = cells[0].css("a")
            href = link.attrib.get("href", "")
            isin = href.strip("/").split("/")[-1] if href else ""

            try:
                cours = float(cells[1].css("::text").get("0").replace(" ", "").replace(",", ".").strip())
            except (ValueError, TypeError):
                cours = 0.0

            try:
                var_raw = cells[2].css("::text").get("0").replace(" ", "").replace(",", ".").replace("%", "").strip()
                variation = float(var_raw)
            except (ValueError, TypeError):
                variation = 0.0

            try:
                vol_raw = cells[3].css("::text").get("0").replace(" ", "").replace(",", "").strip()
                volume = int(vol_raw)
            except (ValueError, TypeError):
                volume = 0

            libelle = link.css("::text").get("").strip() or cells[0].css("::text").get("").strip()

            if libelle and isin:
                yield ActionItem(
                    libelle=libelle,
                    cours=cours,
                    variation=variation,
                    volume=volume,
                    isin=isin,
                )