from .GubaCrawl import GubacrawlSpider


class Gubacrawl6Spider(GubacrawlSpider):
    name = "GubaCrawl6"
    custom_settings = {"JOBDIR": "jobdir/6"}
