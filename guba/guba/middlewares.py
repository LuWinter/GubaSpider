# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from twisted.internet.error import TimeoutError, ConnectionRefusedError, \
    ConnectError, ConnectionLost, TCPTimedOutError, ConnectionDone
from twisted.internet import defer
from scrapy.core.downloader.handlers.http11 import TunnelError
from .ProxyPool.db import RedisClient
from random import choice
from .user_agent_pool import UA
from scrapy import Request
# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class GubaSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class GubaDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    ALL_EXCEPTIONS = (defer.TimeoutError, TimeoutError, ConnectionRefusedError, ConnectionDone,
                      ConnectError, ConnectionLost, TCPTimedOutError, TunnelError)
    redis = RedisClient(db_no=0)
    USER_AGENTS = UA

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        proxy = self.redis.random()
        request.meta["proxy"] = "https://" + proxy
        user_agent = choice(self.USER_AGENTS)
        request.headers.setdefault('User-Agent', user_agent)
        return None

    def process_response(self, request, response, spider):
        if str(response.status).startswith('4') or str(response.status).startswith('5'):
            proxy = request.meta["proxy"].lstrip("https://")
            self.redis.delete(proxy)
            request.meta["proxy"] = self.redis.random()
            return request
        return response

    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.ALL_EXCEPTIONS):
            print('Got %s' % exception)
            proxy = request.meta["proxy"].lstrip("https://")
            self.redis.delete(proxy)
            request.meta["proxy"] = self.redis.random()
            return request
        print("Not prepared exceptions:", exception)

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
