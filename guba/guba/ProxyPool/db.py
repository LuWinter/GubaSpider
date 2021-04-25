import redis

REDIS_HOST = "62.234.150.220"
REDIS_PORT = 6379
REDIS_PASSWORD = 200054
REDIS_KEY = "proxies"


class PoolEmptyError(Exception):
    def __init__(self, error_info='IP代理池为空，无法提供有效代理'):
        # super().__init__(self)
        self.error_info = error_info

    def __str__(self):
        return self.error_info


class RedisClient(object):
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD):
        """
        初始化
        :param host: Redis 地址
        :param port: Redis 端口
        :param password: Redis 密码
        """
        self.db = redis.StrictRedis(host=host, port=port, password=password, decode_responses=True)

    def add(self, proxy):
        """
        向redis添加代理，有效时间为120秒
        :param proxy: 代理
        :return: True/False
        """
        return self.db.set(proxy, 1, ex=120)

    def random(self):
        """
        随机抽取60个有效代理，从中随机选择一个
        :return: 随机代理
        """
        proxies_number = self.count()
        if proxies_number:
            return self.db.randomkey()
        else:
            raise PoolEmptyError

    def delete(self, proxy):
        print('代理', proxy, "移除")
        return self.db.delete(proxy)

    def exist(self, proxy):
        """
        判断代理是否存在
        :param proxy: 代理
        :return: 是否存在
        """
        return self.db.exists(proxy) is not None

    def count(self):
        """
        获取数量
        :return: 数量
        """
        return self.db.dbsize()

    def all(self):
        """
        获取全部代理
        :return: 全部代理列表 (时间戳从2021-01-01到2025-12-31)
        """
        return self.db.keys('*')
