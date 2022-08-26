# -*-coding:utf-8-*- 、
# Team : upcedu.nlp
# Author：dongshou
# Date ：2021/10/18 上午10:18
# Describe ：强国论坛
import requests
import scrapy
from scrapy import Selector

from base.utils import get_uid_by_name
from base.utils.time import get_date
from loguru import logger
from spiders.items import WeiboItem
from spiders.spiders import BaseSpider


class FXW(BaseSpider):
    name = "复兴网"

    def __init__(self,one_project_name,**kwargs):
        super(FXW, self).__init__(one_project_name,logger)
        self.url = "fuxingwang"
        self.flag_search = False

    def page_parse(self, response, **kwargs):
        try:
            resp = Selector(response)
            fuxing = WeiboItem()
            fuxing["account"] = resp.xpath('//div[@class="property"]/span[1]/text()').get()[3:]
            fuxing["title"] = resp.xpath("//div[@class='cateLeft article border']/h1/text()").get().strip()
            fuxing["title"] = self.try_get_title(response, fuxing["title"])
            fuxing["weibo_id"] = get_uid_by_name(fuxing["title"] + "复兴网")
            fuxing["mid"] = fuxing["weibo_id"]
            fuxing["uid"] = get_uid_by_name(fuxing["account"])
            content = ''
            for p in resp.xpath("//div[@id='Acontent']/p"):
                content += str(p.xpath("string(.)").get()).strip().replace("\n", " ").replace("\r", " ")
            fuxing["content"] = content
            fuxing["date"] = resp.xpath('//div[@class="property"]/span[2]/text()').get()[5:]
            fuxing["now_date"] = get_date()
            fuxing["platform"] = "复兴网"
            yield fuxing
        except:
            logger.exception(f"【复兴网】文章解析出错解析出错 {response.text}")
            return
