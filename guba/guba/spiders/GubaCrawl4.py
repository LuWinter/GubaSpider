from .GubaCrawl import GubacrawlSpider


class Gubacrawl4Spider(GubacrawlSpider):
    name = "GubaCrawl4"
    custom_settings = {"JOBDIR": "jobdir/4"}
