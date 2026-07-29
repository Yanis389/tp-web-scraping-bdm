import scrapy
from allocine.items import FilmItem

class FilmsSpider(scrapy.Spider):
    name = "films"
    allowed_domains = ["allocine.fr"]
    start_urls = ["https://www.allocine.fr/film/meilleurs/"]

    custom_settings = {
        "DOWNLOAD_DELAY": 1.0,
        "ROBOTSTXT_OBEY": True,
    }

    def parse(self, response):
        for link in response.css("h2.meta-title a::attr(href)").getall():
            yield response.follow(link, callback=self.parse_film)

        next_page = response.css("a.button--right::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_film(self, response):
        # Titre propre
        titre = response.css("h1::text").get() or response.css(".titlebar-title::text").get() or ""
        
        # Réalisateur : cibler spécifiquement la section direction
        realisateur = response.css(".meta-body-direction .blue-link::text").get() or \
                      response.css(".meta-body-direction a::text").get() or ""

        # Année / Date
        annee = response.css(".date::text").get() or response.css(".meta-body-item strong::text").get() or ""

        # Notes
        notes = response.css(".stareval-note::text").getall()
        note_presse = notes[0] if len(notes) > 0 else ""
        note_spectateurs = notes[1] if len(notes) > 1 else (notes[0] if len(notes) == 1 else "")

        yield FilmItem(
            titre=titre.strip(),
            annee=annee.strip(),
            realisateur=realisateur.strip(),
            note_presse=note_presse,
            note_spectateurs=note_spectateurs,
            url=response.url,
        )