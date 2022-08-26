import datetime
import json

import requests
import scrapy as scrapy
from scrapy import Selector

from monitor import logger


class Fuxingwang:
    name = "复兴网"

    def __init__(self):
        pass

    def get_request_from_keyword(self, headers, search_url, keyword, *args, **kwargs):
        try:
                request = requests.get(search_url.substitute(), headers=headers)
                resp = Selector(request)
                infos = resp.xpath('//ul[@class="commonlist"]/li/a')
                for item in infos:
                    url = item.xpath("./@href").get()
                    title = item.xpath("./text()").get()
                    meta = {"name": self.name, "callback": "page_parse", "keyword": title}
                    yield scrapy.Request(url, headers=headers, meta=meta)
        except Exception as e:
            logger.exception(f"E 复兴网错误{e}")

if __name__ == '__main__':
    header = {
      "Connection": "keep-alive",
      "Cache-Control": "max-age=0",
      "Upgrade-Insecure-Requests": "1",
      "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
      "Referer": "https://www.baidu.com/link?url=m8DZ7QudRoRhnB_tdKkbOIgCnschfR5QNmof-xV1BRe&wd=&eqid=ffbbf0e1000ac36600000003616cd8ce",
      "Accept-Language": "zh-CN,zh;q=0.9",
      "If-None-Match": "'616cd717-12535'",
      "If-Modified-Since": "Mon, 18 Oct 2021 02:08:23 GMT"
    }
    # search_url ="https://www.mzfxw.com/"
    # a = Fuxingwang()
    # for i in a.get_request_from_keyword(header, search_url):
    #     print(i)
        # response = requests.get(i.url, headers=header)
        # b = Fuxingwang()
        # for j in b.page_parse(response):
        #     print(j)
