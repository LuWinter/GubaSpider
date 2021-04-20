from scrapy import Request, Spider, FormRequest
import re
from ..items import GubaItem


class GubacrawlSpider(Spider):
    name = 'GubaCrawl'
    allowed_domains = ['guba.eastmoney.com']
    start_urls = ['http://guba.eastmoney.com/']

    request_form_data = {
        'param': 'postid=1025461213&sort=1&sorttype=1&p=1&ps=30',
        'path': 'reply/api/Reply/ArticleNewReplyList',
        'env': 2
    }
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.74",
        'Origin': 'https://guba.eastmoney.com',
        'Referer': 'https://guba.eastmoney.com/list,002074.html',
        'Host': 'guba.eastmoney.com'
    }
    post_id_exp = re.compile('/news,[0-9]{6},([0-9]{,15})\.html')
    user_id_exp = re.compile('"user_id":"([0-9]+)')
    user_age_exp = re.compile('"user_age":"(.+)","user_influ_level"')
    post_time_and_ip_exp = re.compile('"post_display_time":"(.+)","post_ip":"(.*)","post_state"')
    post_info_exp = re.compile('"post_click_count":([0-9]+),"post_forward_count":([0-9]+),"post_comment_count":([0-9]+),"post_comment_authority":([0-9]+),"post_like_count":([0-9]+)')

    def start_requests(self):
        stoke_code = "002074"
        for i in range(1, 3):
            base_url = "https://guba.eastmoney.com/list,%s_%s.html" % (stoke_code, i)
            request = Request(url=base_url, callback=self.parse)
            request.meta["stoke_code"] = stoke_code
            yield request

    def parse(self, response):
        # post_links = response.xpath("//div[@class='articleh normal_post']/span[@class='l3 a3']/a/@href").extract()
        page_check = re.compile('data-popstock="([0-9]{6})"')
        stoke_code = response.meta["stoke_code"]
        if re.search(page_check, response.text):
            print("正常页面")
            pattern = re.compile('/news,[0-9]{6},[0-9]{,15}\.html')
            post_links = re.findall(pattern, response.text)
            for post_link in post_links:
                full_link = "https://guba.eastmoney.com" + post_link
                print(full_link)
                self.headers["Referer"] = "https://guba.eastmoney.com/list,%s.html" % stoke_code
                page_request = Request(url=full_link, callback=self.page_parse, headers=self.headers)
                page_request.meta["stoke_code"] = stoke_code
                # yield page_request
        else:
            print("垃圾页面")
            # 剔除代理
            request = Request(url=response.url, callback=self.parse)
            request.meta["stoke_code"] = stoke_code
            yield request

    def page_parse(self, response):
        page_check = re.compile('data-popstock="([0-9]{6})"')
        stoke_code = response.meta["stoke_code"]
        if re.search(page_check, response.text):                        # 判断是否为正常页面
            postItem = GubaItem()
            postItem["stoke_code"] = stoke_code
            postItem["post_id"] = re.search(self.post_id_exp, response.url).group(1)
            postItem["user_id"] = re.search(self.user_id_exp, response.text).group(1)
            postItem["user_age"] = re.search(self.user_age_exp, response.text).group(1)
            post_time_and_ip = re.search(self.post_time_and_ip_exp, response.text)
            postItem["post_time"] = post_time_and_ip.group(1)
            postItem["post_ip"] = post_time_and_ip.group(2)
            post_info = re.search(self.post_info_exp, response.text)
            postItem["post_click_count"] = post_info.group(1)
            postItem["post_forward_count"] = post_info.group(2)
            postItem["post_comment_count"] = post_info.group(3)
            postItem["post_comment_authority"] = post_info.group(4)
            postItem["post_like_count"] = post_info.group(5)
            title = response.xpath('//div[@id="zwconttbt"]/text()').extract_first().strip()
            postItem["post_title"] = title
            text = response.xpath('//div[@class="stockcodec .xeditor"]//text()').extract()
            text = [sentence.strip() for sentence in text]
            postItem["post_text"] = " ".join(text)
            if postItem["post_comment_count"] != '0':                   # 判断是否有评论
                self.request_form_data["param"] = "postid=%s&sort=1&sorttype=1&p=1&ps=30" % postItem["post_id"]
                self.headers["Referer"] = 'https://guba.eastmoney.com/news,002074,1025461213.html'
                comment_url = "https://guba.eastmoney.com/interface/GetData.aspx"
                comment_request = FormRequest(url=comment_url, formdata=self.request_form_data, headers=self.headers, callback=self.get_comment)
                comment_request.meta["item"] = postItem
                # yield comment_request
            else:
                postItem["comment_list"] = []
                yield postItem
        else:
            print("垃圾页面")
            # 剔除代理
            self.headers["Referer"] = "https://guba.eastmoney.com/list,%s.html" % stoke_code
            page_request = Request(url=response.url, callback=self.page_parse, headers=self.headers)
            page_request.meta["stoke_code"] = stoke_code
            # yield page_request

    def get_comment(self, response):
        pass
