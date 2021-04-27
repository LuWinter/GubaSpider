from .GubaCrawl import GubacrawlSpider


class GubaCrawl15Spider(GubacrawlSpider):
    name = 'GubaCrawl15'
    custom_settings = {'JOBDIR': 'jobdir/15'}
