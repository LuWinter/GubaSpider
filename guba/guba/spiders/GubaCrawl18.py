from .GubaCrawl import GubacrawlSpider


class GubaCrawl18Spider(GubacrawlSpider):
    name = 'GubaCrawl18'
    custom_settings = {'JOBDIR': 'jobdir/18'}
