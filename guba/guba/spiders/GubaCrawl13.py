from .GubaCrawl import GubacrawlSpider


class GubaCrawl13Spider(GubacrawlSpider):
    name = 'GubaCrawl13'
    custom_settings = {'JOBDIR': 'jobdir/13'}
