# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

from base.utils import get_uid_by_name
from base.utils.time import get_time, get_date


class WeiboItem(scrapy.Item):
    """
    账户名称，账户uid，微博内容，点赞，转发，评论，转发列表，标题，热度，日期，事件日期，平台
    """
    # define the fields for your item here like:
    account = scrapy.Field()
    weibo_id = scrapy.Field()  # 不存在根据title生成
    mid = scrapy.Field()  # 查询方面，统一内容标识符？ 不存在则根据keyword+平台+其他 生成
    uid = scrapy.Field()  # 用户uid
    content = scrapy.Field()
    father = scrapy.Field()  # 用来表示其父亲节点，计转发了那条微博
    likes = scrapy.Field()
    retweet = scrapy.Field()
    comment = scrapy.Field()
    retweet_list = scrapy.Field()
    comment_list = scrapy.Field()
    like_list = scrapy.Field()
    title = scrapy.Field()
    hot = scrapy.Field()
    date = scrapy.Field()  # 微博发出的时间
    now_date = scrapy.Field()  # 爬取信息的时间
    platform = scrapy.Field()

    def handle_None(self, logger):
        """
        处理空值
        :return:
        """
        for key in self.fields.keys():
            if key not in self._values:
                if key == "weibo_id":
                    self[key] = get_uid_by_name(str(self.try_get("title", "")) + get_date())
                elif key == "mid":
                    text = str(self.try_get("title", "")) + str(self.try_get("platform", "")) + get_date()
                    self[key] = get_uid_by_name(text)
                elif key in ["now_date", "date"]:
                    self[key] = get_time()
                else:
                    self[key] = None
        return True

    def try_get(self, item, default):
        if item in self._values:
            return self[item]
        else:
            return default


class CommentItem(scrapy.Item):
    mid = scrapy.Field()
    weibo_id = scrapy.Field()
    account = scrapy.Field()
    uid = scrapy.Field()
    date = scrapy.Field()
    now_date = scrapy.Field()
    content = scrapy.Field()
    likes = scrapy.Field()

    def handle_None(self, logger):
        """
        处理空值
        :return:
        """
        for key in self.fields.keys():
            if key not in self._values:
                if key == "mid":
                    logger.error("爬取的数据中没有mid，缺少主键")
                    return False
                self[key] = None
        return True


class UserItem(scrapy.Item):
    """
     账户名称，账户uid，地理位置，关注数量，粉丝数量，个人简介，标签，用户微博，用户粉丝，
    """
    account = scrapy.Field()
    uid = scrapy.Field()
    location = scrapy.Field()
    follows = scrapy.Field()  # 关注数量
    follow_list = scrapy.Field()  # 关注列表
    fans = scrapy.Field()
    fan_list = scrapy.Field()
    gender = scrapy.Field()
    brief = scrapy.Field()
    label = scrapy.Field()
    verified = scrapy.Field()
    user_friend = scrapy.Field()  # 相互关注的数量
    all_content = scrapy.Field()  # 用户微博总数量
    history_weibo = scrapy.Field()
    credit = scrapy.Field()
    career = scrapy.Field()
    education = scrapy.Field()
    age = scrapy.Field()
    create_at = scrapy.Field()

    def handle_None(self, logger):
        """
        处理空值
        :return:
        """
        for key in self.fields.keys():
            if key not in self._values:
                if key == "uid":
                    logger.error("爬取的数据中没有uid，缺少主键")
                    return False
                self[key] = None
        return True


Default_Weibo_Item = {
    "account": None,
    "weibo_id": None,  # 不存在根据title生成
    "mid": None,  # 查询方面，统一内容标识符？ 不存在则根据keyword+平台+其他 生成
    "uid": None,  # 用户uid
    "content": None,
    "father": None,  # 用来表示其父亲节点，计转发了那条微博
    "retweet": None,
    "comment": None,
    "retweet_list": None,
    "comment_list": None,
    "like_list": None,
    "title": None,
    "hot": None,
    "date": None,  # 微博发出的时间
    "now_date": get_time(),  # 爬取信息的时间
    "platform": None
}

Default_Comment_Item = {
    "mid": None,
    "weibo_id": None,
    "account": None,
    "uid": None,
    "date": None,
    "now_date": get_time(),
    "content": None,
    "likes": None
}

Default_User_Item = {
    "account": None,
    "uid": None,
    "location": None,
    "follows": None,  # 关注数量
    "follow_list": None,  # 关注列表
    "fans": None,
    "fan_list": None,
    "gender": None,
    "brief": None,
    "label": None,
    "verified": None,
    "user_friend": None,  # 相互关注的数量
    "all_content": None,  # 用户微博总数量
    "history_weibo": None,
    "credit": None,
    "career": None,
    "education": None,
    "age": None,
    "create_at": get_time()
}

if __name__ == '__main__':
    w = WeiboItem()
    w["title"] = "发士大夫"
    w.handle_None(None)
    print(w)
