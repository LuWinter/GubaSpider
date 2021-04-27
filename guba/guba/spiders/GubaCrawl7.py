from .GubaCrawl import GubacrawlSpider


class GubaCrawl7Spider(GubacrawlSpider):
    name = 'GubaCrawl7'
    custom_settings = {'JOBDIR': 'jobdir/7'}
