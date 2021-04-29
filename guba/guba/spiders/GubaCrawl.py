from scrapy import Request, Spider, FormRequest
import re
from ..items import GubaItem
from ..ProxyPool.db import RedisClient
from ..user_agent_pool import headers, request_form_data
import json
from time import time


class GubacrawlSpider(Spider):

    name = 'GubaCrawl'
    allowed_domains = ['guba.eastmoney.com']
    start_urls = ['http://guba.eastmoney.com/']
    custom_settings = {"JOBDIR": "jobdir/1"}

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
        stoke_code = response.meta["stoke_code"]
        if re.search(page_check, response.text):
            pattern = re.compile('class="l3 a3">(<em class="icon icon_list_img"></em> )?<a href="(/news,[0-9]{6},[0-9]{,15}\.html)')  # 可以过滤掉一些非常规帖子（如问董秘、资讯）
            post_links = re.findall(pattern, response.text)
            for post_link in post_links:
                full_link = "https://guba.eastmoney.com" + post_link[1]
                print("正在抓取", full_link)
                self.headers["Referer"] = "https://guba.eastmoney.com/list,%s.html" % stoke_code
                page_request = Request(url=full_link, callback=self.page_parse, headers=self.headers)
                page_request.meta["stoke_code"] = stoke_code
                page_request.meta["page_number"] = response.meta["page_number"]
                yield page_request
        else:
            print("垃圾页面！")
            self.redis.delete(response.meta["proxy"].lstrip("https://"))
            request = Request(url=response.url, callback=self.parse)
            request.meta["stoke_code"] = stoke_code
            request.meta["page_number"] = response.meta["page_number"]
            yield request

    def page_parse(self, response):
        postItem = GubaItem()
        post_info_exp = re.compile('"post":(.+),"rc"')
        post_info = re.search(post_info_exp, response.text)
        if post_info is not None:
            post_info = json.loads(post_info.group(1))
            stoke_code = post_info["post_guba"]["stockbar_code"]
            if stoke_code == response.meta["stoke_code"]:                                               # 通过页面判断此页是否为正常页面
                postItem["stoke_code"] = stoke_code                                                     # 股票代码
                postItem["post_id"] = post_info["post_id"]                                              # 帖子ID
                postItem["user_id"] = post_info["post_user"]["user_id"]                                 # 发帖人ID
                postItem["user_age"] = post_info["post_user"]["user_age"]                               # 发帖人吧龄
                postItem["user_is_majia"] = post_info["post_user"]["user_is_majia"]                     # 发帖人是否为马甲
                postItem["user_influence_level"] = post_info["post_user"]["user_influ_level"]           # 发帖人影响力等级
                postItem["post_time"] = post_info["post_publish_time"]                                  # 发帖时间
                postItem["post_click_count"] = post_info["post_click_count"]                            # 帖子点击量
                postItem["post_forward_count"] = post_info["post_forward_count"]                        # 未知统计量
                postItem["post_comment_count"] = post_info["post_comment_count"]                        # 帖子评论量
                postItem["post_comment_authority"] = post_info["post_comment_authority"]                # 帖子权威评论量
                postItem["post_like_count"] = post_info["post_like_count"]                              # 帖子点赞量
                postItem["post_title"] = post_info["post_title"]                                        # 帖子标题
                postItem["post_text"] = re.sub(r'<.+?>', '', post_info["post_content"])                 # 帖子正文
                postItem["post_from"] = post_info["post_from"]                                          # 发帖平台
                postItem["page_number"] = response.meta["page_number"]
                postItem["crawl_time"] = time()                                                         # 获取时间
                comment_number = int(postItem["post_comment_count"])
                if comment_number != 0:                                                                 # 如果有评论，则爬取评论链接
                    self.request_form_data["param"] = "postid=%s&sort=1&sorttype=1&p=1&ps=30" % postItem["post_id"]
                    self.headers["Referer"] = response.url
                    comment_url = "https://guba.eastmoney.com/interface/GetData.aspx"
                    comment_request = FormRequest(url=comment_url, formdata=self.request_form_data,
                                                headers=self.headers, callback=self.get_comment)
                    comment_request.meta["item"] = postItem                                             # 向下一层请求传递参数
                    yield comment_request
                else:
                    postItem["comment_list"] = []                                                       # 没有评论就返回空
                    print("%s 成功获取 %s在 %s的帖子 %s" % (
                        self.name, postItem["stoke_code"], postItem["post_time"], postItem["post_id"]))
                    yield postItem
            else:
                print("垃圾页面！")
                self.redis.delete(response.meta["proxy"].lstrip("https://"))
                self.headers["Referer"] = "https://guba.eastmoney.com/list,%s.html" % stoke_code
                page_request = Request(url=response.url, callback=self.page_parse, headers=self.headers)
                page_request.meta["stoke_code"] = stoke_code
                page_request.meta["page_number"] = response.meta["page_number"]
                yield page_request
        else:
            print("无效页面！" + response.url)

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
            self.headers["Referer"] = "https://guba.eastmoney.com/news,%s,%s.html" % (postItem["stoke_code"], postItem["post_id"])
            comment_url = "https://guba.eastmoney.com/interface/GetData.aspx"
            comment_request = FormRequest(url=comment_url, formdata=self.request_form_data,
                                          headers=self.headers, callback=self.get_comment)
            comment_request.meta["item"] = postItem                                             # 向下一层请求传递参数
            yield comment_request

