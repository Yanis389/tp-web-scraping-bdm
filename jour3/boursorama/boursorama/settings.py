BOT_NAME = "boursorama"

SPIDER_MODULES = ["boursorama.spiders"]
NEWSPIDER_MODULE = "boursorama.spiders"

USER_AGENT = "IPSSI-scraper (+contact@ipssi.fr)"

ROBOTSTXT_OBEY = True

DOWNLOAD_DELAY = 1.0
RANDOMIZE_DOWNLOAD_DELAY = True

ITEM_PIPELINES = {
    "boursorama.pipelines.SQLitePipeline": 300,
}

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"