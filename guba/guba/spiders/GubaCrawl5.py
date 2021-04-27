from .GubaCrawl import GubacrawlSpider


class Gubacrawl5Spider(GubacrawlSpider):
    name = "GubaCrawl5"
    custom_settings = {"JOBDIR": "jobdir/5"}
