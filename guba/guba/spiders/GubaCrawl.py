from scrapy import Request, Spider
import re


class GubacrawlSpider(Spider):
    name = 'GubaCrawl'
    allowed_domains = ['guba.eastmoney.com']
    start_urls = ['http://guba.eastmoney.com/']

    def start_requests(self):
        stoke_code = "002074"
        for i in range(1, 3):
            base_url = "https://guba.eastmoney.com/list,%s_%s.html" % (stoke_code, i)
            yield Request(url=base_url, callback=self.parse)

    def parse(self, response):
        # post_links = response.xpath("//div[@class='articleh normal_post']/span[@class='l3 a3']/a/@href").extract()
        pattern = re.compile('/news,.{,20}\.html')
        post_links = re.findall(pattern, response.text)
        for post_link in post_links:
            full_link = "https://guba.eastmoney.com" + post_link
            print(full_link)
            # yield Request(url=full_link)

