from scrapy import Request, Spider, FormRequest
import re
from ..items import GubaItem
from ..ProxyPool.db import RedisClient
from ..user_agent_pool import headers, request_form_data
import json
import requests
# from time import time


class NewgubacrawlSpider(Spider):
    name = 'NewGubaCrawl'
    allowed_domains = ['guba.eastmoney.com']
    start_urls = ['http://guba.eastmoney.com/']
    # custom_settings = {"JOBDIR": "jobdir/1"}

    redis = RedisClient(db_no=0)
    redis_stoke_code = RedisClient(db_no=2)
    headers = headers
    request_form_data = request_form_data

    def start_requests(self):
        while self.redis_stoke_code.count() != 0:
            stoke_code = self.redis_stoke_code.random()
            web_page_count = self.redis_stoke_code.value(stoke_code)
            self.redis_stoke_code.delete(stoke_code)
            print("开始爬取股票%s, 共有%s页" % (stoke_code, web_page_count))
            for i in range(1, int(web_page_count) + 1):
                base_url = "https://guba.eastmoney.com/list,%s_%s.html" % (stoke_code, i)
                request = Request(url=base_url, callback=self.parse)
                request.meta["stoke_code"] = stoke_code
                request.meta["page_number"] = i
                yield request

    def parse(self, response, **kwargs):
        page_check = re.compile('data-popstock="([0-9]{6})"')
        link_pattern = re.compile(
            'class="l3 a3">(<em class="icon icon_list_img"></em> )?<a href="(/news,[0-9]{6},[0-9]{,15}.html)')
        id_pattern = re.compile('/news,([0-9]{6}),([0-9]+).html')
        text_pattern = re.compile('title="(.+?)">')
        author_pattern = re.compile('data-popper="([0-9]+)"')
        time_pattern = re.compile('a5">(.+?)</span>')
        read_pattern = re.compile('a1">([0-9]+)</span>')
        comment_pattern = re.compile('a2">([0-9]+)</span>')

        stoke_code = response.meta["stoke_code"]
        if re.search(page_check, response.text).group(1) == stoke_code:
            items = re.findall('<div class="articleh normal_post">(.+?)</div>', response.text, re.S)
            for item in items:
                test = re.search(link_pattern, item)
                postItem = GubaItem()
                if test is not None:
                    link = test.group(2)
                    postItem["stoke_code"] = re.search(id_pattern, link).group(1)
                    postItem["post_id"] = re.search(id_pattern, link).group(2)
                    author = re.search(author_pattern, item)
                    if author is not None:
                        postItem["user_id"] = author.group(1)
                    post_time = re.search(time_pattern, item).group(1)
                    postItem["post_time"] = self.add_year(postItem["post_id"], post_time)
                    postItem["post_click_count"] = re.search(read_pattern, item).group(1)
                    text = re.search(text_pattern, item).group(1)
                    if len(text) == 40:
                        self.headers["Referer"] = "https://guba.eastmoney.com/list,%s.html" % stoke_code
                        postItem["post_text"] = self.get_text(page_url="https://guba.eastmoney.com" + link,
                                                              page_headers=self.headers, page_stoke_code=stoke_code, short_text=text)
                    else:
                        postItem["post_text"] = text
                    postItem["post_comment_count"] = re.search(comment_pattern, item).group(1)
                    if int(postItem["post_comment_count"]) > 0:
                        self.request_form_data["param"] = "postid=%s&sort=1&sorttype=1&p=1&ps=30" % postItem["post_id"]
                        self.headers["Referer"] = "https://guba.eastmoney.com" + link
                        comment_url = "https://guba.eastmoney.com/interface/GetData.aspx"
                        comment_request = FormRequest(url=comment_url, formdata=self.request_form_data,
                                                      headers=self.headers, callback=self.get_comment)
                        comment_request.meta["item"] = postItem                              # 向下一层请求传递参数
                        yield comment_request
                    print("%s 成功获取 %s在 %s的帖子 %s" % (
                        self.name, postItem["stoke_code"], postItem["post_time"], postItem["post_id"]))
                    yield postItem
        else:
            print("垃圾页面！")
            self.redis.delete(response.meta["proxy"].lstrip("https://"))
            request = Request(url=response.url, callback=self.parse)
            request.meta["stoke_code"] = stoke_code
            request.meta["page_number"] = response.meta["page_number"]
            yield request

    def get_text(self, page_url, page_headers, page_stoke_code, short_text):
        try:
            proxy = self.redis.random()
            proxies = {'http': 'http://%s' % proxy, 'https': 'https://%s' % proxy}
            response = requests.get(url=page_url, headers=page_headers, proxies=proxies, timeout=7)
            post_info_exp = re.compile('"post":(.+),"rc"')
            post_info = re.search(post_info_exp, response.text)
            if post_info is not None:
                post_info = json.loads(post_info.group(1))
                stoke_code = post_info["post_guba"]["stockbar_code"]
                if stoke_code == page_stoke_code:                                                # 通过页面判断此页是否为正常页面
                    return re.sub(r'<.+?>', '', post_info["post_content"])                       # 帖子正文
        except Exception:
            return short_text

    def get_comment(self, response):
        postItem = response.meta["item"]
        if response.status == 200:
            comment_list = json.loads(response.text)['re']
            if comment_list is not None:
                new_comment = []
                for comment in comment_list:
                    new_item = dict()
                    new_item["reply_id"] = comment["reply_id"]
                    new_item["reply_time"] = comment["reply_publish_time"]
                    new_item["reply_user"] = comment["user_id"]
                    new_item["reply_text"] = comment["reply_text"]
                    new_item["child_reply_count"] = comment["reply_count"]
                    new_comment.append(new_item)
                postItem["comment_list"] = new_comment
                print("%s 成功获取 %s在 %s的帖子 %s" % (
                    self.name, postItem["stoke_code"], postItem["post_time"], postItem["post_id"]))
                yield postItem
            else:
                print("此评论被关闭")
                yield postItem
        else:
            print("提取评论失败！")
            self.redis.delete(response.meta["proxy"].lstrip("https://"))
            self.request_form_data["param"] = "postid=%s&sort=1&sorttype=1&p=1&ps=30" % postItem["post_id"]
            self.headers["Referer"] = "https://guba.eastmoney.com/news,%s,%s.html" % (postItem["stoke_code"],
                                                                                      postItem["post_id"])
            comment_url = "https://guba.eastmoney.com/interface/GetData.aspx"
            comment_request = FormRequest(url=comment_url, formdata=self.request_form_data,
                                          headers=self.headers, callback=self.get_comment)
            comment_request.meta["item"] = postItem                                             # 向下一层请求传递参数
            yield comment_request

    @staticmethod
    def add_year(post_id, post_time):
        post_id = int(post_id)
        if post_id > 992194695:
            return "2021-" + post_time
        elif post_id > 895422020:
            return "2020-" + post_time
        elif post_id > 799843705:
            return "2019-" + post_time
        elif post_id > 739452679:
            return "2018-" + post_time
        elif post_id > 584381032:
            return "2017-" + post_time
        elif post_id > 237929763:
            return "2016-" + post_time
        elif post_id > 139294168:
            return "2015-" + post_time
        elif post_id > 96642499:
            return "2014-" + post_time
        elif post_id > 60253072:
            return "2013-" + post_time
        elif post_id > 47477085:
            return "2012-" + post_time
        elif post_id > 32954396:
            return "2011-" + post_time
        else:
            return "2010-" + post_time
