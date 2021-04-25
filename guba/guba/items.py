# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Field, Item


class GubaItem(Item):
    # define the fields for your item here like:
    stoke_code = Field()
    post_id = Field()
    user_id = Field()
    user_age = Field()
    user_is_majia = Field()
    user_influence_level = Field()
    post_time = Field()
    post_click_count = Field()
    post_forward_count = Field()
    post_comment_count = Field()
    post_comment_authority = Field()
    post_like_count = Field()
    post_title = Field()
    post_text = Field()
    post_from = Field()
    comment_list = Field()
