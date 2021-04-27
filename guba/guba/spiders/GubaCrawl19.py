from .GubaCrawl import GubacrawlSpider


class GubaCrawl19Spider(GubacrawlSpider):
    name = 'GubaCrawl19'
    custom_settings = {'JOBDIR': 'jobdir/19'}
