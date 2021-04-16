import scrapy


class GubacrawlSpider(scrapy.Spider):
    name = 'GubaCrawl'
    allowed_domains = ['guba.eastmoney.com']
    start_urls = ['http://guba.eastmoney.com/']

    def parse(self, response):
        pass
