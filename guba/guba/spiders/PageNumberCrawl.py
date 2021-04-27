from scrapy import Spider, Request
from ..ProxyPool.db import RedisClient
from ..user_agent_pool import UA
from random import choice
import re
from ..items import NumberItem


class PageNumberCrawlSpider(Spider):
    name = 'PageNumberCrawl'
    allowed_domains = ['guba.eastmoney.com']
    start_urls = ['http://guba.eastmoney.com/']

    redis_proxy = RedisClient(db_no=0)
    # redis_stoke_code = RedisClient(db_no=1)
    USER_AGENTS = UA

    def start_requests(self):
        inf = open('D:/PycharmProjects/GubaSpider/A_stoke_codes_20200806_3068.txt', 'r')
        stoke_codes = inf.read().strip().split(sep="\n")
        for stoke_code in stoke_codes:
            stoke_url = "https://guba.eastmoney.com/list,%s.html" % stoke_code
            request = Request(url=stoke_url, callback=self.parse)
            request = self.add_headers(request)
            request.meta["stoke_code"] = stoke_code
            yield request

    def parse(self, response, **kwargs):
        page_check = re.compile('data-popstock="([0-9]{6})"')
        stoke_code = response.meta["stoke_code"]
        if re.search(page_check, response.text):
            Number = NumberItem()
            number_exp = re.compile(r'data-pager="list,[0-9]{6}_\|([0-9]+)\|80\|1"')
            post_number = re.search(number_exp, response.text).group(1)
            page_number = int(post_number) / 80 - 10
            Number["stoke_code"] = stoke_code
            Number["page_number"] = int(page_number)
            print("股票%s共有%s页" % (stoke_code, page_number))
            yield Number
            # self.redis_stoke_code.add(stoke_code, value=int(page_number), ex=None)
        else:
            print("垃圾页面！")
            self.redis_proxy.delete(response.meta["proxy"].lstrip("https://"))
            request = Request(url=response.url, callback=self.parse)
            request.meta["stoke_code"] = stoke_code
            request = self.add_headers(request)
            yield request

    def add_headers(self, request):
        proxy = self.redis_proxy.random()
        request.meta['proxy'] = "https://" + proxy
        user_agent = choice(self.USER_AGENTS)
        request.headers.setdefault('User-Agent', user_agent)
        return request
