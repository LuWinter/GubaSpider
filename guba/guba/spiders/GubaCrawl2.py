from .GubaCrawl import GubacrawlSpider


class Gubacrawl2Spider(GubacrawlSpider):
    name = "GubaCrawl2"
    custom_settings = {"JOBDIR": "jobdir/2"}