import requests
from .db import RedisClient
import time

POOL_UPPER_THRESHOLD = 300


class Getter:
    def __init__(self):
        self.redis = RedisClient()

    @staticmethod
    def crawl_proxy():
        """
        获取10个代理
        :return: 代理
        """
        proxy_url = """
        http://ip.16yun.cn:817/myip/pl/f13027d7-7416-4f3d-9405-c8052b6ae8a4/?s=fswdxsblnx&u=1352252075%40qq.com&format=line
        """
        html = requests.get(proxy_url)
        proxies = html.text.split("\r\n")
        return proxies

    def is_over_threshold(self):
        """
        判断是否达到了代理池限制
        :return: True/False
        """
        if self.redis.count() >= POOL_UPPER_THRESHOLD:
            return True
        else:
            return False

    def run(self):
        while True:
            if not self.is_over_threshold():
                present_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                print(present_time, " 正在获取代理...")
                proxies = self.crawl_proxy()
                for proxy in proxies:
                    self.redis.add(proxy)
                time.sleep(10)
            else:
                print("代理池已满")
                break
