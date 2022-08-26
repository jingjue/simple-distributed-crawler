import logging
from string import Template

import requests
import scrapy
from loguru import logger

from base.utils.time import gelin_time_change
from conf.default import Default_user_follow_page, Default_user_fans_page, Default_history_weibo_count, \
    Default_history_weibo_page
from spiders.items import UserItem, WeiboItem
from spiders.spiders import BaseSpider


class Weibo_User(BaseSpider):
    name = "微博用户"

    def __init__(self, one_project_name="default",**kwargs):
        super(Weibo_User, self).__init__(one_project_name,logger)

    def parse_user(self, response, **kwargs):
        try:
            result = response.json()["data"]["user"]
            uid = response.meta.get("uid")
            user = UserItem()
            user["account"] = result["screen_name"]
            user["uid"] = result["id"]
            user["location"] = result["location"]
            user["follows"] = result["friends_count"]  # 关注
            user["fans"] = result["followers_count"]  # 粉丝
            user["gender"] = result["gender"]
            user["brief"] = result["description"]
            user["verified"] = result["verified_type"]
            user["user_friend"] = result["friends_count"]
            user["all_content"] = result["statuses_count"]

            detail_url = self._header_manager.fill_url("user_detail", self.platform, uid=uid)
            detail_response = requests.get(detail_url, headers=self.headers, timeout=10)
            try:
                detail_result = detail_response.json()["data"]
                user["credit"] = detail_result["sunshine_credit"]["level"]
                career = detail_result.get("company", False)
                if career:
                    user["career"] = career
                if detail_result.get("education", False):
                    user["education"] = detail_result["education"]["school"]
                user["age"] = detail_result["birthday"]
                user["create_at"] = detail_result["created_at"]

                user_label = []
                for label in detail_result["label_desc"]:
                    user_label.append(label["name"])
                user["label"] = '/'.join(user_label)
            except:
                logger.exception(f"用户详细信息解析出错 {detail_url}，{detail_response.text}")

            # 查找关注列表
            follows_url = self._header_manager.get_universal_url("follows", self.platform)
            if follows_url:
                for follows in self.request_list(user["uid"], follows_url, Default_user_follow_page):
                    if isinstance(follows, UserItem):
                        yield follows
                    else:
                        user["follow_list"] = follows

            # 粉丝列表
            fans_url = self._header_manager.get_universal_url("fans", self.platform)
            for fans in self.request_list(user["uid"], fans_url, Default_user_fans_page):
                if isinstance(fans, UserItem):
                    yield fans
                else:
                    user["fan_list"] = fans

            history_weibo = []
            # 查找历史博文，经分析，已经不需要历史博文了；2021.11.8 又需要了

            count, page = 0, 1
            while count < Default_history_weibo_count and page < Default_history_weibo_page:
                user_history_url = self._header_manager.fill_url("user_history", self.platform, uid=uid, page=page)
                response_ = requests.get(user_history_url, headers=self.headers, timeout=10)
                try:
                    result = response_.json()["data"]["list"]
                    for history in result:
                        weibo = WeiboItem()
                        weibo["account"] = user["account"]
                        weibo["weibo_id"] = history["idstr"]
                        weibo["mid"] = history["mid"]
                        weibo["uid"] = user["uid"]
                        weibo["content"] = history["text_raw"]
                        weibo["father"] = "history"
                        weibo["likes"] = history["attitudes_count"]
                        weibo["retweet"] = history["reposts_count"]
                        weibo["comment"] = history["comments_count"]
                        weibo["retweet_list"] = "None"
                        weibo["comment_list"] = "None"
                        weibo["like_list"] = "None"
                        weibo["title"] = ""
                        weibo["hot"] = 0
                        weibo["date"] = gelin_time_change(history["created_at"])
                        weibo["platform"] = "微博"
                        history_weibo.append(weibo["weibo_id"])
                        yield weibo
                        count += 1
                except:
                    logger.exception(f"【用户历史博文解析出错】{response_.url} {response_.text}")
                page += 1
            user["history_weibo"] = "/".join(history_weibo)
            yield user
        except:
            logger.exception(f"【微博用户解析出错】{response.text}")
            return

    def request_list(self, uid, format_url: Template, page_num):
        """
        爬取用户关注或者粉丝列表
        :param uid:
        :return:
        """

        page = 1
        follows = []
        while page < page_num:
            url = format_url.substitute(uid=uid, page=page)
            response = requests.get(url, headers=self.headers)
            try:
                for resp in response.json()["users"]:
                    resp = dict(resp)
                    try:
                        item = UserItem()
                        item["account"] = resp["screen_name"]
                        item["uid"] = resp["idstr"]
                        item["location"] = resp["location"]
                        item["follows"] = 0  # 返回的信息中没有该条
                        item["follow_list"] = 'None'
                        item["fans"] = resp["followers_count"]
                        item["fan_list"] = 'None'
                        item["gender"] = resp["gender"]
                        item["brief"] = resp["description"]
                        item["label"] = resp.get("ability_tags",None)
                        item["verified"] = resp["verified"]
                        item["user_friend"] = resp["friends_count"]
                        item["all_content"] = 0  # 没有该项数据
                        item["history_weibo"] = 'None'
                        item["credit"] = str(resp["credit_score"])
                        item["create_at"] = gelin_time_change(resp["created_at"])
                        follows.append(item["uid"])
                        yield item
                    except:
                        logger.exception(f"【单个微博用户粉丝或关注列表解析】{resp}")
            except:
                logger.exception(f"【微博用户粉丝或关注列表解析】{response.text}")
                self.check_cookie(response)
            page += 1
        yield '/'.join(follows)

    def make_request_from_data(self, uid):
        """
        从uid构造详细信息
        :param uid:
        :return:
        """
        logging.info("test")
        user_url = self._header_manager.get_universal_url("user", "微博")
        if user_url:
            url = user_url.substitute(uid=uid)
            meta = {"callback": "parse_user", "project_name": self.project_name, "platform": self.platform, "uid": uid}
            return scrapy.Request(url, headers=self.headers, meta=meta)
        else:
            return None
