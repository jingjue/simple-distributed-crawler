import datetime
import json

import requests
import scrapy as scrapy
from scrapy import Selector

from monitor import logger



class Tieba:
    name = "贴吧"

    def __init__(self):
        pass

    def get_request_from_keyword(self, headers, search_url, keyword, *args, **kwargs):
        try:
            for i in range(1, 30):
                url = search_url.substitute(qw=keyword, pn=i)
                response = requests.get(url, headers=headers, timeout=50)
                html = Selector(text=response.text)
                result = html.xpath("//div[@class='s_post']//span//a/@href").extract()
                if result:
                    for res in result:
                        url = 'https://tieba.baidu.com/' + res
                        meta = {"url": url, "name": "tieba", "platform": "tieba", "keyword": keyword,
                                "callback": "page_parse"}
                        yield scrapy.Request(url=url, headers=headers, meta=meta,
                                             dont_filter=False,
                                             )
        except Exception as e:
            logger.exception(f"E 贴吧错误{e}")


if __name__ == '__main__':
    header = {
        "Connection": "keep-alive",
        "sec-ch-ua": "'Chromium';v='92',' Not A;Brand';v='99', 'Google Chrome';v='92'",
        "sec-ch-ua-mobile": "?0",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Referer": "https://tieba.baidu.com/f/search/res?ie=utf-8&qw=%E7%83%88%E5%A3%AB%E7%BA%AA%E5%BF%B5%E6%97%A5",
        "Accept-Language": "zh,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6"
    }
    search_url = "https://tieba.baidu.com/f/search/res?isnew=1&kw=&qw={}&rn=10&un=&only_thread=0&sm=1&sd=&ed=&pn={}"
    a = Tieba()
    for i in a.get_request_from_keyword(header, search_url, '中国石油大学'):
        print(i)
        response = requests.get(i.url, headers=header)
        a = tieba_hotSearch()
        for j in a.page_parse(response):
            print(j)
