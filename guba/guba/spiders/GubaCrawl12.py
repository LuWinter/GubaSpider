from .GubaCrawl import GubacrawlSpider


class GubaCrawl12Spider(GubacrawlSpider):
    name = 'GubaCrawl12'
    custom_settings = {'JOBDIR': 'jobdir/12'}
