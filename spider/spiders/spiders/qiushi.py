# encoding: utf-8
'''
  @author: Suncy
  @license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited. 
  @contact: scyuige@163.com
  @software: garner
  @file: qiushi.py
  @time: 2021/10/15 17:20
  @desc:
'''

from scrapy import Selector
import requests
from loguru import logger

from base.utils.time import get_time, gen_id, qiushi_time_change
from base.utils import *
from loguru import logger
from spiders.items import WeiboItem
from spiders.spiders import BaseSpider


#
class Qiushi(BaseSpider):
    name = "求是"
    cookie = {"platform": "qiushi.hotsearch"}

    def __init__(self, one_project_name, **kwargs):
        super(Qiushi, self).__init__(one_project_name, logger)

    def page_parse(self, response, **kwargs):
        try:
            qiushi_item = WeiboItem()
            qiushi_item['platform'] = '求是'
            qiushi_item["now_date"] = get_time()
            html = Selector(text=response.text)
            title = html.xpath("//div[@class='inner']//h1//text()").extract()

            if title:
                title = title[0]
            else:
                title = html.xpath("//div[@class='headtitle']//h1//text()").extract()
            title = self.try_get_title(response, title)
            qiushi_item["title"] = title
            account = html.xpath("//div[@class='inner']//span//text()").extract()
            if account:
                qiushi_item['account'] = account[1]
            else:
                qiushi_item['account'] = '求是'
            time = html.xpath("//div[@class='inner']//span//text()").extract()
            if time:
                qiushi_item['date'] = qiushi_time_change(time[2].replace('\r\n', ''))
            else:
                time = html.xpath("//div[@class='headtitle']//span//text()").get()
                qiushi_item['date'] = time.strip()
            contents = html.xpath("//div[@class='highlight']//p//text()").extract()
            if contents:
                contents = ''.join(i.strip().replace('\u3000', '').replace("\ax0", "") for i in contents)
                qiushi_item['content'] = contents
            else:
                return
            qiushi_item["uid"] = get_uid_by_name(title[0] + gen_id())
            qiushi_item["mid"] = qiushi_item["uid"]
            qiushi_item["weibo_id"] = qiushi_item["uid"]
            yield qiushi_item
        except Exception as e:
            logger.exception(f"E 求是错误{e}")


if __name__ == '__main__':
    qiushi = qiushi_hotSearch()
    # qiushi.get_request_from_keyword("孟晚舟")
    response = requests.get('http://www.qstheory.cn/dukan/hqwg/2020-12/28/c_1126916891.htm', headers=qiushi.headers,
                            timeout=10)
    qiushi.page_parse(response)
