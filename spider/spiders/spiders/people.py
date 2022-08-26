#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    @Author 冬兽
    @Date 2021/10/3 21:32
    @Describe 人民网
"""
import requests
import scrapy
from scrapy import Selector
from loguru import logger

from base.utils import get_uid_by_name
from base.utils.text_preprocess import people_pre_text
from base.utils.time import people_time_change, get_date, gen_id
from spiders.items import WeiboItem
from spiders.spiders import BaseSpider


class People(BaseSpider):
    name = "人民网"

    def __init__(self, one_project_name, **kwargs):
        super(People, self).__init__(one_project_name, logger)

    def page_parse(self, response, **kwargs):
        try:
            resp = Selector(response)
            title = resp.xpath("//div[@class='col col-1 fl']/h1/text()").get()
            date = resp.xpath("//div[@class='col-1-1 fl']/text()").get()
            platform = resp.xpath("//div[@class='col-1-1 fl']/a/text()").get()

            # 人民网标签不统一,存在多种样式，这里只考虑了两种情况，多余删除
            if not title:
                title = resp.xpath("//div[@class='col col-1']/h1/text()").get()
                platform = resp.xpath("//div[@class='col-1-1']/a/text()").get()
                date = resp.xpath("//div[@class='col-1-1']/text()").get()

            date = people_time_change(date)
            account = resp.xpath("//div[@class='edit cf']/text()").get()
            p_list = resp.xpath("//div[@class='rm_txt_con cf']/p/text()")
            content = ''
            for p in p_list:
                content += people_pre_text(p.get())

            people = WeiboItem()
            title = self.try_get_title(response, title)
            people["account"] = account
            people["uid"] = get_uid_by_name(account)
            people["weibo_id"] = get_uid_by_name(title + str(gen_id()))
            people["mid"] = get_uid_by_name(title + str(gen_id()))
            people["content"] = content
            people["title"] = title

            people["date"] = date
            people["now_date"] = get_date()
            people["platform"] = platform
            yield people
        except Exception as e:
            logger.exception(f"E 人民网错误{e}")


if __name__ == '__main__':
    people = People()
    print(people.get_request_from_keyword("岸田文雄当选日本第100任首相"))
