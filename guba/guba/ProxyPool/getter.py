import requests
from guba.guba.ProxyPool.db import RedisClient
import time

POOL_UPPER_THRESHOLD = 1000


class Getter:
    def __init__(self):
        self.redis = RedisClient()

    def crawl_proxy(self):
        """
        这里使用的是星速云代理，获取存活时间在20秒以上的代理
        :return: 代理
        """
        proxy_url = "http://user.xingsudaili.com:25435/jeecg-boot/extractIp/s?uid=1387210378204246017&orderNumber=CN2021042809134535&number=30&wt=text&randomFlag=false&detailFlag=true&useTime=20&region="
        response = requests.get(url=proxy_url)
        proxy_list = response.text.split(sep="<br>")
        for proxy in proxy_list:
            proxy_info = proxy.split(sep=",")
            proxy_use_time = int(proxy_info[4]) - time.time() - 7
            self.redis.add(proxy_info, value=1, ex=proxy_use_time)
        time.sleep(4)

    def crawl_xundaili_proxy(self):
        """
        抓取讯代理，有效时长为五分钟
        :return:代理
        """
        proxy_url = "http://api.xdaili.cn/xdaili-api//greatRecharge/getGreatIp?spiderId=3f349be46a674a9c9e5c9691a3625947&orderno=YZ202092158025JpefA&returnType=2&count=5"
        response = requests.get(url=proxy_url)
        proxy_list = response.json()["RESULT"]
        for proxy in proxy_list:
            proxy_info = proxy["ip"] + ":" + proxy["port"]
            self.redis.add(proxy_info, value=1, ex=290)
        time.sleep(10)

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
                try:
                    self.crawl_xundaili_proxy()
                except Exception:
                    print("代理池获取器发生错误, 30秒后进入重试")
                    time.sleep(30)
            else:
                print("代理池已满")
                break


if __name__ == "__main__":
    getter = Getter()
    getter.run()
