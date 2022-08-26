# encoding: utf-8
'''
  @author: Suncy
  @splitter: 王振琦
  @license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited. 
  @contact: scyuige@163.com
  @software: garner
  @file: yanhuangcq.py
  @time: 2021/10/13 9:25
  @desc:
'''
import json
import logging
from urllib import parse

import requests
from scrapy import Selector
from loguru import logger

from base.utils import get_uid_by_name
from base.utils.time import get_time, gen_id
from spiders.items import WeiboItem
from spiders.spiders import BaseSpider


class Yanhuangcq(BaseSpider):
    name = "炎黄春秋"

    def __init__(self, one_project_name="default", **kwargs):
        super(Yanhuangcq, self).__init__(one_project_name, logger)

    def parse_single_page(self, response, **kwargs):
        with open("/home/users/Scy/log.text","w") as f:
            f.write(response.text)
        response = response.text[42:][:-3]
        json_response = json.loads(response)
        for res in json_response['rows']:
            yanhuangcq_item = WeiboItem()
            yanhuangcq_item['platform'] = "炎黄春秋"
            yanhuangcq_item['now_date'] = get_time()
            if res['author']:
                yanhuangcq_item['account'] = res['author']
            if res['publishDate']:
                yanhuangcq_item['date'] = res['publishDate'].split(" ")[0]
            if res['text']:
                html = Selector(text=res['text'])
                content = html.xpath('//p//text()').extract()
                content = ''.join(i for i in content)
                yanhuangcq_item['content'] = content
            if res['title']:
                title = res['title']
            else:
                title = None
            # yanhuangcq_item['title'] = self.try_get_title(response, title)
            yanhuangcq_item["weibo_id"] = get_uid_by_name(title + "炎黄春秋" + gen_id())  # Id标识此条新闻
            yanhuangcq_item["mid"] = yanhuangcq_item["weibo_id"]
            yanhuangcq_item["uid"] = yanhuangcq_item["weibo_id"]
            logging.info(yanhuangcq_item)
            yield yanhuangcq_item


if __name__ == '__main__':
    url = 'http://www.yhcqw.com/cms/content/fullSearchList?jsonpCallback=jQuery111104702743438657311_1634108383319&page=1&rows=1000000&keyWord={}&siteID=1&_=1634108383320'
    headers = {
        'Accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Cookie': '_pk_id.5.9039=64bd127280097a81.1650339234.; _pk_ses.5.9039=1',
        'Host': 'www.yhcqw.com',
        'Referer': 'http://www.yhcqw.com/97/97_1.html?hid=%E5%AD%9F%E6%99%9A%E8%88%9F',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    keyword = "陆军"
    search_url = str.format(url, parse.quote(keyword))
    response = requests.get(search_url)
    yh = Yanhuangcq()
    for a in yh.parse_single_page(response):
        print(a)
