import scrapy

class FilmItem(scrapy.Item):
    titre = scrapy.Field()
    annee = scrapy.Field()
    realisateur = scrapy.Field()
    note_presse = scrapy.Field()       # float
    note_spectateurs = scrapy.Field()  # float
    url = scrapy.Field()