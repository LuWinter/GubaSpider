# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo
from scrapy.exceptions import DropItem
from twisted.internet import reactor, defer
from .ProxyPool.db import RedisClient


class MongoPipeline:
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_db=crawler.settings.get("MONGO_DB"),
            mongo_uri=crawler.settings.get("MONGO_URI")
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def _insert(self, item, out, spider):
        self.db["Guba_First_Batch_20210427"].insert(dict(item))
        reactor.callFromThread(out.callback, item)

    @defer.inlineCallbacks
    def process_item(self, item, spider):
        out = defer.Deferred()
        reactor.callInThread(self._insert, item, out, spider)
        yield out
        defer.returnValue(item)

    def close_spider(self, spider):
        self.client.close()


class PageNumberPipeline(object):
    def open_spider(self, spider):
        self.redis = RedisClient(db_no=1)
        self.outf = open("Stoke_Page_Number.txt", "w")

    def process_item(self, item, spider):
        stoke_code = item["stoke_code"]
        page_number = item["page_number"]
        self.redis.add(stoke_code, page_number, ex=None)
        self.outf.write("%s %s\n" % (stoke_code, page_number))
        return item

    def close_spider(self, spider):
        self.outf.close()
