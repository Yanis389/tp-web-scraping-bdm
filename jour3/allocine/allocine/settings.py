BOT_NAME = "allocine"

SPIDER_MODULES = ["allocine.spiders"]
NEWSPIDER_MODULE = "allocine.spiders"

USER_AGENT = "IPSSI-scraper (+contact@ipssi.fr)"

ROBOTSTXT_OBEY = True

DOWNLOAD_DELAY = 1.0
RANDOMIZE_DOWNLOAD_DELAY = True

CONCURRENT_REQUESTS = 4
CONCURRENT_REQUESTS_PER_DOMAIN = 2

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1.0
AUTOTHROTTLE_MAX_DELAY = 10.0

RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 429]

ITEM_PIPELINES = {
    "allocine.pipelines.CleanPipeline": 100,
}

FEEDS = {
    "films.json": {"format": "json", "encoding": "utf-8", "overwrite": True, "indent": 2},
    "films.csv": {"format": "csv", "encoding": "utf-8", "overwrite": True},
}

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"