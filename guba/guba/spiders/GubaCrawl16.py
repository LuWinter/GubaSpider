from .GubaCrawl import GubacrawlSpider


class GubaCrawl16Spider(GubacrawlSpider):
    name = 'GubaCrawl16'
    custom_settings = {'JOBDIR': 'jobdir/16'}
