import datetime
import json
# from string import Template

import requests
import scrapy as scrapy

from monitor import logger
# from spiders.spiders.qiushi import Qiushi


class Qiushi_search:
    name = "求是"

    def __init__(self):
        pass

    def get_request_from_keyword(self, headers, search_url, keyword, *args, **kwargs):
        try:
            page_url = search_url.substitute(page=1, keyword=keyword)
            page_response = requests.get(page_url, headers=headers, timeout=10)
            page_json = json.loads(page_response.text[14:-2])
            page_count = page_json['pageCount'] + 1
            for i in range(1, page_count):
                url = search_url.substitute(page=i, keyword=keyword)
                response = requests.get(url, headers=headers, timeout=10)
                json_response = json.loads(response.text[14:-2])
                for res in json_response['results']:
                    url = res['url']
                    meta = {"url": url, "name": "qiushi", "platform": "qiushi", "keyword": keyword,
                            "callback": "page_parse"}
                    yield scrapy.Request(url=url, headers=headers, meta=meta, dont_filter=False,
                                         )
        except Exception as e:
            logger.exception(f"E 求是错误{e}")

if __name__ == '__main__':
    header =  {
      "Connection": "keep-alive",
      "Cache-Control": "max-age=0",
      "Upgrade-Insecure-Requests": "1",
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
      "Accept-Language": "zh,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6",
      "If-Modified-Since": "Tue, 07 Sep 2021 07:24:05 GMT"
    }
    search_url = Template("http://so.news.cn/qiushi/more?callback=jsonpCallback&page=$page&keyword=$keyword&searchword=(LinkTitle%3D%E5%AD%9F%E6%99%9A%E8%88%9F+or+IntroTitle%3D%E5%AD%9F%E6%99%9A%E8%88%9F+or+SubTitle%3D%E5%AD%9F%E6%99%9A%E8%88%9F)+AND+PubTime+%3E%3D%272020.10.15%27&orderby=RELEVANCE&_=1634290554883")
    a = Qiushi_search()
    for i in a.get_request_from_keyword(header, search_url, '美国是祸乱世界的“伏地魔”'):
        print(i.url)
        response = requests.get(i.url, headers=header)
        response.encoding='utf-8'
        a = Qiushi('')
        for j in a.page_parse(response):
            print(j)
