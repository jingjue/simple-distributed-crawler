# Name:         weibo.py
# Description:
# Author:       东寿
# Date:         2022/4/14

import scrapy
from loguru import logger
import requests
from base.utils.time import gelin_time_change, get_date
from conf.default import *
from spiders.items import WeiboItem, CommentItem
from spiders.spiders import BaseSpider

class Weibo(BaseSpider):
    name = "微博"

    def __init__(self, one_project_name="default",**kwargs):
        super(Weibo, self).__init__(one_project_name, logger)

    @logger.catch()
    def parse_signal_page(self, response, **kwargs):
        """
        包括微博本身，转发，评论三个大部分，其中还嵌套了用户信息爬取
        """
        if response.status != 200:
            self.check_cookie(response.text)
            logger.error(f"response.code:{response.status},{response.text}")
            return None
        # 微博本身
        weibo_result = response.json()
        weibo = WeiboItem()
        weibo_id = response.meta.get("weibo_id")
        uid = response.meta.get("uid")
        keyword = response.meta.get("keyword")

        weibo["account"] = weibo_result["user"]["screen_name"]
        weibo["weibo_id"] = weibo_id
        weibo["mid"] = weibo_result["id"]

        weibo["uid"] = uid
        weibo["content"] = weibo_result["text_raw"]
        weibo["likes"] = weibo_result["attitudes_count"]
        weibo["retweet"] = weibo_result["reposts_count"]
        weibo["comment"] = weibo_result["comments_count"]
        weibo["father"] = response.meta.get("father")
        weibo["retweet_list"] = []
        weibo["comment_list"] = []
        weibo["title"] = self.try_get_title(response,keyword)
        weibo["hot"] = 0
        weibo["date"] = gelin_time_change(weibo_result["created_at"])
        weibo["now_date"] = get_date()
        weibo["platform"] = self.platform
        father_weibo_id = str(weibo["uid"]) + "@" + str(weibo["weibo_id"])
        self.enqueue_user(self.get_user_request(uid))  # 将用户信息保存到redis中

        # 处理点赞数据
        likes = []
        like_page, like_count = 1, 0
        while like_page < Default_like_page and like_count < weibo["likes"]:
            url = self._header_manager.fill_url("like", self.platform, uid=weibo["mid"], page=like_page)
            if not url:
                continue
            result = True
            for result in self.request_like(url):
                if not result:
                    break
                if isinstance(result, int):
                    weibo["likes"] = result
                elif isinstance(result, str):
                    likes.append(result)
                else:
                    yield result
                like_count += 1
            if not result:
                break
            like_page += 1
        weibo["like_list"] = "/".join(likes)

        # 处理评论
        comment_page, comment_count = 1, 0
        max_id = 0
        while comment_count < weibo["comment"] and comment_page < Default_comment_page:
            if max_id == 0:
                curl = self._header_manager.fill_url("comment0", self.platform, mid=weibo["mid"], uid=uid)
            else:
                curl = self._header_manager.fill_url("comment1", self.platform, mid=weibo["mid"], uid=uid,
                                                     max_id=max_id)
            if not curl:
                continue
            for item, max_id in self.request_comment(curl, father_weibo_id):
                if isinstance(item, CommentItem):
                    weibo["comment_list"].append(item["uid"])
                yield item
                comment_count += 1
            if max_id == 0:
                break
            comment_page += 1

        # 处理转发数据
        repost_page = 1
        repost_count = 0
        while repost_count < weibo["retweet"] and repost_page < Default_repost_page:
            repost_url = self._header_manager.fill_url("repost", self.platform, mid=weibo["mid"], page=repost_page)
            if not repost_url:
                continue
            for repost_uid, repost_weibo_id in self.request_repost(repost_url):
                weibo["retweet_list"].append(repost_uid)
                # 主要考虑多级转发
                url = self._header_manager.fill_url("content", self.platform, weibo_id=repost_weibo_id)
                meta = {"platform": "weibo", "keyword": keyword, "callback": "parse_signal_page", "uid": repost_uid,
                        "weibo_id": repost_weibo_id, "father": father_weibo_id, "name": self.platform}
                # 内容请求入redis
                yield scrapy.Request(url, headers=self.headers, callback=self.parse_signal_page, meta=meta)
                repost_count += 1
            repost_page += 1
        yield weibo
        logger.info(f"解析微博 url:{response._get_url()} 完毕")

    def request_like(self, url):
        """
        请求点赞数据
        :param url:
        :return:
        """
        response = requests.get(url=url, headers=self.headers, timeout=10)
        likes = []
        try:
            data_list = response.json()["data"]
            if len(data_list) != 0:
                yield int(response.json()["total_number"])
            for data in data_list:
                uid = data["user"]["idstr"]
                likes.append(uid)
                yield uid
                self.enqueue_user(self.get_user_request(uid))
        except:
            self.check_cookie(response.text)
            logger.error(f"[用户点赞数据出错] {response.text}")
            yield False

    def request_repost(self, url):
        """
        获取转发,考虑多级转发吗？
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            reposts = response.json()["data"]
            for result in reposts:
                uid = result["user"]["id"]
                weibo_id = result["mblogid"]
                yield uid, weibo_id
                self.enqueue_user(self.get_user_request(uid))
        except Exception as e:
            logger.error(f"转发数据爬取失败 {e} {response.text}")

    def request_comment(self, url, weibo_id):
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            info = response.json()
            comments = info["data"]
            for result in comments:
                comment = CommentItem()
                comment["date"] = gelin_time_change(result["created_at"])
                comment["now_date"] = get_date()
                comment["weibo_id"] = weibo_id
                comment["content"] = result["text_raw"]
                comment["account"] = result["user"]["screen_name"]
                comment["uid"] = result["user"]["id"]
                comment["mid"] = str(result["id"])
                comment["likes"] = result["like_counts"]
                max_id = result["max_id"]
                yield comment, max_id
                self.enqueue_user(self.get_user_request(comment["uid"]))
        except Exception as e:
            logger.error(f"评论数据爬取失败 {e} {response.text}")

    def get_user_request(self, uid):
        user_url = self._header_manager.get_universal_url("user", self.platform)
        if user_url:
            url = user_url.substitute(uid=uid)
            meta = {"callback": "parse_user", "project_name": self.project_name, "platform": self.platform,"uid":uid}
            return scrapy.Request(url, headers=self.headers, meta=meta)
        else:
            return None


if __name__ == '__main__':
    # url = "https://weibo.com/ajax/statuses/mymblog?uid=2514846743&page=1&feature=0"
    # meta = {"platform": "weibo", "keyword": 'None', "callback": "parse_user", "uid": 1298073802, "name": "weibo"}
    # weibo = weibo_hotSearch()
    # weibo._open(dbslot)
    # response = requests.get(url, headers=weibo.headers)
    # print(response.json())

    # for item in weibo.parse_user(response):
    #     print(item)

    # for request in weibo.get_request_from_keyword("孟晚舟律师称她没有认罪"):
    #     print(request)
    #
    # keyword1 = "北京冬奥会"
    # keyword2 = "孟晚舟律师称她没有认罪"
    # page = 1
    # url = "https://weibo.com/ajax/search/all?containerid=100103type" + parse.quote(
    #     f"=1&q={keyword1}&t=0") + f"&page={page}&count=20"
    # ur2 = "https://weibo.com/ajax/search/all?containerid=100103type" + parse.quote(
    #     f"=1&q={keyword2}&t=0") + f"&page={page}&count=20"
    # print(url)
    # print(ur2)
    # print(parse.quote("=1&q="))
    # print(parse.quote("&t=0"))
    # print(parse.quote(keyword1))
    # print(parse.quote(keyword2))
    weibo = Weibo()
