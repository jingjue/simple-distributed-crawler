# -*-coding:utf-8-*- 、
# Team : upcedu.nlp
# Author：dongshou
# Date ：2021/10/18 上午11:36
# Describe ：
import requests
from loguru import logger
from scrapy import Selector

from base.utils import get_uid_by_name
from base.utils.text_preprocess import mweibo_xpath_content
from base.utils.time import get_date

from conf.default import Default_father, Default_list, Default_hot, Default_num
from spiders.items import WeiboItem
from spiders.spiders import BaseSpider


class QGLT(BaseSpider):
    name = "强国论坛"

    def __init__(self, one_project_name,**kwargs):
        super(QGLT, self).__init__(one_project_name, logger)

    def page_parse(self, response, **kwargs):
        url = response.url
        url_num = url.split("/")[-1].split(".")[0]
        try:
            resp = Selector(response)
            qglt = WeiboItem()
            qglt["account"] = resp.xpath("//div[@class='clearfix']").xpath("string(.)").get().strip()
            qglt["title"] = resp.xpath("//div[@class='navBar']/h2").xpath('string(.)').get().replace("\t", "").replace(
                "\r\n", "")
            qglt["title"] = self.try_get_title(response, qglt["title"])
            qglt["weibo_id"] = get_uid_by_name(qglt["title"] + url_num + qglt["account"])
            qglt["mid"] = qglt["weibo_id"]
            qglt["uid"] = qglt["account"]
            content_url = self._header_manager.fill_url("content", self.platform, url_num=url_num)
            content_response = requests.get(content_url, headers=self.headers)
            try:
                content = str(mweibo_xpath_content(content_response.text)).replace("\xa0", ""). \
                    replace("\u3000", "").replace("\n", "").replace("\r\n", "").replace(" ", "").replace("　", "")
                qglt["content"] = content
            except:
                logger.exception(f"【强国论坛】文章内容解析出错 {response.text[0:100]}")
                return
            qglt["father"] = Default_father
            qglt["likes"] = int(resp.xpath("//span[@class='readNum']/text()").get())
            qglt["comment"] = int(resp.xpath("//span[@class='replayNum']/text()").get())
            qglt["retweet"] = Default_num
            qglt["retweet_list"] = Default_list
            qglt["comment_list"] = Default_list
            qglt["hot"] = Default_hot
            qglt["date"] = resp.xpath("//span[@class='float_l mT10']").xpath("string(.)").get().replace("\xa0", "")[12:]
            qglt["now_date"] = get_date()
            qglt["platform"] = "强国论坛"
            yield qglt
        except Exception as e:
            logger.exception(f"E 强国论坛错误{e}")
