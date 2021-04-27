from .GubaCrawl import GubacrawlSpider


class GubaCrawl11Spider(GubacrawlSpider):
    name = 'GubaCrawl11'
    custom_settings = {'JOBDIR': 'jobdir/11'}
