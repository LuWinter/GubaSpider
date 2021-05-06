import requests
from guba.guba.ProxyPool.db import RedisClient, PoolEmptyError
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
        print("成功获取%s个代理" % len(proxy_list))
        time.sleep(10)

    def crawl_yiniuyun_proxy(self):
        """
        抓取亿牛云代理，有效时长为2分钟
        :return: 代理
        """
        proxy_url = "http://ip.16yun.cn:817/myip/pl/16938025-b3b0-4b21-b458-946ab5a619b6/?s=kqipittuiz&u=1352252075%40qq.com"
        response = requests.get(url=proxy_url)
        proxy_list = response.text.split(sep="\r\n")
        for proxy in proxy_list:
            self.redis.add(proxy=proxy, value=1, ex=115)
        print("成功获取%s个代理" % len(proxy_list))
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
                    self.crawl_yiniuyun_proxy()
                except PoolEmptyError:
                    print("代理池获取器关闭")
                    break
                except Exception:
                    print("代理池获取器发生错误, 30秒后进入重试")
                    time.sleep(30)
            else:
                print("代理池已满，30秒后开始继续获取代理")
                time.sleep(30)


if __name__ == "__main__":
    getter = Getter()
    getter.run()
