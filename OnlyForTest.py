import requests
import re
from lxml import etree
from guba.guba.items import GubaItem
import json


headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.74",
    'Origin': 'https://guba.eastmoney.com',
    'Referer': 'https://guba.eastmoney.com/list,002074_1.html',
    'Host': 'guba.eastmoney.com'
}
headers_comment = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.74",
    'Origin': 'https://guba.eastmoney.com',
    'Referer': 'https://guba.eastmoney.com/news,002074,1025461213.html',
    'Host': 'guba.eastmoney.com'
}


# 这一段用于测试正则提取帖子链接
# url_content = "https://guba.eastmoney.com/list,002074_7.html"
# response = requests.get(url=url_content, headers=headers)
# post_links_exp = re.compile('class="l3 a3">(<em class="icon icon_list_img"></em> )?<a href="(/news,[0-9]{6},[0-9]{,15}\.html)')
# post_links = re.findall(post_links_exp, response.text)
# print(len(post_links), post_links)
# for i in range(0, len(post_links)):
#     full_link = "https://guba.eastmoney.com" + post_links[i][1]
#     print(i + 1, full_link)


# 这一段是混合了XPATH和正则的页面解析代码
url = "https://guba.eastmoney.com/news,002074,1025461213.html"
response = requests.get(url=url, headers=headers)

post_id_exp = re.compile('/news,[0-9]{6},([0-9]{,15})\.html')
user_id_exp = re.compile('"user_id":"([0-9]+)')
user_age_exp = re.compile('"user_age":"(.+)","user_influ_level"')
post_time_and_ip_exp = re.compile('"post_display_time":"(.+)","post_ip":"(.*)","post_state"')
post_info_exp = re.compile('"post_click_count":([0-9]+),"post_forward_count":([0-9]+),"post_comment_count":([0-9]+),"post_comment_authority":([0-9]+),"post_like_count":([0-9]+)')


def parse_comment_list(comments):
    new_comment = []
    for item in comments:
        new_item = dict()
        new_item["reply_id"] = item["reply_id"]
        new_item["reply_time"] = item["reply_publish_time"]
        new_item["reply_user"] = item["user_id"]
        new_item["reply_text"] = item["reply_text"]
        new_item["child_reply_count"] = item["reply_count"]
        new_comment.append(new_item)
    return new_comment


page_check = re.compile('data-popstock="([0-9]{6})"')
if re.search(page_check, response.text):
    print("正常页面")
    post = GubaItem()
    post["post_id"] = re.search(post_id_exp, url).group(1)
    post["user_id"] = re.search(user_id_exp, response.text).group(1)
    post["user_age"] = re.search(user_age_exp, response.text).group(1)
    post_time_and_ip = re.search(post_time_and_ip_exp, response.text)
    post["post_time"] = post_time_and_ip.group(1)
    post["post_ip"] = post_time_and_ip.group(2)
    post_info = re.search(post_info_exp, response.text)
    post["post_click_count"] = post_info.group(1)
    post["post_forward_count"] = post_info.group(2)
    post["post_comment_count"] = post_info.group(3)
    post["post_comment_authority"] = post_info.group(4)
    post["post_like_count"] = post_info.group(5)
    title = etree.HTML(response.text).xpath('//div[@id="zwconttbt"]/text()')
    title = [sentence.strip() for sentence in title]
    post["post_title"] = "".join(title)
    text = etree.HTML(response.text).xpath('//div[@class="stockcodec .xeditor"]//text()')
    text = [sentence.strip() for sentence in text]
    post["post_text"] = "".join(text)
    print(post)
    if post["post_comment_count"] != '0':
        print("有评论")
        data = {
            'param': 'postid=%s&sort=1&sorttype=1&p=1&ps=30' % "1025461213",
            'path': 'reply/api/Reply/ArticleNewReplyList',
            'env': 2
        }
        comment_url = "https://guba.eastmoney.com/interface/GetData.aspx"
        comment = requests.post(url=comment_url, data=data, headers=headers_comment)
        comment_list = json.loads(comment.text)['re']
        print(comment_list)
        print(parse_comment_list(comment_list))
else:
    print("垃圾页面")
#   剔除代理
#   重置请求

