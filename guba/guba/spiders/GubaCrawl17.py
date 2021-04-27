from .GubaCrawl import GubacrawlSpider


class GubaCrawl17Spider(GubacrawlSpider):
    name = 'GubaCrawl17'
    custom_settings = {'JOBDIR': 'jobdir/17'}
