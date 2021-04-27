from .GubaCrawl import GubacrawlSpider


class GubaCrawl14Spider(GubacrawlSpider):
    name = 'GubaCrawl14'
    custom_settings = {'JOBDIR': 'jobdir/14'}
