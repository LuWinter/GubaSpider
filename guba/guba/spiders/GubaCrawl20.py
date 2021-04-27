from .GubaCrawl import GubacrawlSpider


class GubaCrawl20Spider(GubacrawlSpider):
    name = 'GubaCrawl20'
    custom_settings = {'JOBDIR': 'jobdir/20'}
