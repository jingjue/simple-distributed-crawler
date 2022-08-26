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
from string import Template
from urllib import parse

import scrapy

from monitor import logger


class Yanhuangcq:
    name = "炎黄春秋"

    def __init__(self):
        pass

    def get_request_from_keyword(self, headers, search_url, keyword, *args, **kwargs):
        cookies = {
            '_pk_id.5.9039': '84d204df7529509b.1634088127.',
            '_pk_ref.5.9039': '%5B%22%22%2C%22%22%2C1634107026%2C%22https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3Djyyjg3nNnZn6vcZ6jOGDSJZxYgjIfPz1SGb-Zh4kdb3%26wd%3D%26eqid%3De945b1ae000010960000000361667e83%22%5D',
            '_pk_ses.5.9039': '1',
        }
        try:
            url = search_url.substitute(keyword=keyword)
            meta = {
                "platform": "炎黄春秋",
                "keyword": keyword,
                "callback": 'parse_single_page',
                "yanhuangcq_id": '0',
                "father": '0'
            }
            yield scrapy.Request(url, headers=headers, cookies=cookies, meta=meta)
        except Exception as e:
            logger.exception(f"E 炎黄春秋检索{e}")
            yield None


if __name__ == '__main__':
    url = Template("http://www.yhcqw.com/cms/content/fullSearchList?jsonpCallback=jQuery111104702743438657311_1634108383319&page=1&rows=1000000&keyWord=$keyword&siteID=1&_=1634108383320")
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
    keyword = "中华民国"
    # search_url = str.format(url, parse.quote(keyword))
    yh = Yanhuangcq()
    for a in yh.get_request_from_keyword(headers=headers, search_url=url, keyword=keyword):
        print(a)
