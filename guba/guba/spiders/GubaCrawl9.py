from .GubaCrawl import GubacrawlSpider


class GubaCrawl9Spider(GubacrawlSpider):
    name = 'GubaCrawl9'
    custom_settings = {'JOBDIR': 'jobdir/9'}
