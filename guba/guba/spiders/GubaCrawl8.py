from .GubaCrawl import GubacrawlSpider


class GubaCrawl8Spider(GubacrawlSpider):
    name = 'GubaCrawl8'
    custom_settings = {'JOBDIR': 'jobdir/8'}
