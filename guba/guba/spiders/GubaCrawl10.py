from .GubaCrawl import GubacrawlSpider


class GubaCrawl10Spider(GubacrawlSpider):
    name = 'GubaCrawl10'
    custom_settings = {'JOBDIR': 'jobdir/10'}
