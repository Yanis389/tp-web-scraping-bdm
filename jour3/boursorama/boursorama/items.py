import scrapy

class ActionItem(scrapy.Item):
    libelle = scrapy.Field()
    cours = scrapy.Field()       # float
    variation = scrapy.Field()   # float
    volume = scrapy.Field()      # int
    isin = scrapy.Field()        # str UNIQUE