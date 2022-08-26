# encoding: utf-8
'''
  @author: Suncy
  @license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited. 
  @contact: scyuige@163.com
  @software: garner
  @file: lianhezb.py
  @time: 2021/10/15 11:13
  @desc:
'''
from scrapy import Selector
from loguru import logger

from base.utils.time import get_time, gen_id
from base.utils import *
from spiders.items import WeiboItem
from spiders.spiders import BaseSpider


class lianhezb(BaseSpider):
    name = "联合早报"

    def __init__(self, one_project_name, **kwargs):
        super(lianhezb, self).__init__(one_project_name, logger)

    def page_parse(self, response, **kwargs):
        lianhezb_item = WeiboItem()
        lianhezb_item['platform'] = '联合早报'
        lianhezb_item["now_date"] = get_time()
        html = Selector(text=response.text)
        title = html.xpath("//div[@class='col-lg-12 col-12 article-container min-682']//h1//text()").extract()
        if title:
            lianhezb_item['title'] = title[0]
        else:
            lianhezb_item['title'] = None

        # account = html.xpath("//div[@class='text-track-v1 author-info f14']//div[1]//text()").extract()
        lianhezb_item["title"] = self.try_get_title(response, lianhezb_item['title'])
        lianhezb_item['account'] = '联合早报'
        time = html.xpath("//div[@class='text-track-v1 author-info f14']//div[2]//text()").extract()
        if time:
            lianhezb_item['date'] = time[1]
            # print(time[1])
        contents = html.xpath("//div[@class='col-lg-12 col-12 article-container']//article//p//text()").extract()
        if contents:
            contents = ''.join(i for i in contents)
            lianhezb_item['content'] = contents
            # print(contents)
        lianhezb_item["uid"] = get_uid_by_name(title[0] + gen_id())
        lianhezb_item["mid"] = lianhezb_item["uid"]
        lianhezb_item["weibo_id"] = lianhezb_item["uid"]
        yield lianhezb_item


if __name__ == '__main__':
    lianhezb = lianhezb_hotSearch()
    # lianhezb.get_request_from_keyword("孟晚舟")
