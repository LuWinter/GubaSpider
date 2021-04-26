from .GubaCrawl import GubacrawlSpider


class Gubacrawl3Spider(GubacrawlSpider):
    name = "GubaCrawl3"
    custom_settings = {"JOBDIR": "jobdir/3"}
