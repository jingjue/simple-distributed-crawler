import datetime
import json
from string import Template

import requests
import scrapy as scrapy

from monitor import logger


class Lianhezb:
    name = "联合早报"

    def __init__(self):
        pass

    def get_request_from_keyword(self, headers, search_url, keyword, *args, **kwargs):
        try:
            url = search_url.substitute(page=1, keyword=keyword)
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                json_response = json.loads(response.text)
                total_news = json_response['result']['total']
                page_num = int(total_news / 10)
                if page_num > 16 or not page_num:
                    page_num = 16
                for i in range(1, page_num):
                    url = search_url.substitute(page=1, keyword=keyword)
                    response = requests.get(url, headers=headers, timeout=10)
                    json_response = json.loads(response.text)
                    for d in json_response['result']['data']:
                        url = 'https://www.zaobao.com/' + d['url']
                        meta = {"url": url, "name": "lianhezb", "platform": "lianhezb", "keyword": keyword,
                                "callback": "page_parse"}
                        yield scrapy.Request(url=url, headers=headers, meta=meta, dont_filter=False)
            else:
                logger.error(f"E 联合早报错误 {response.status_code} {response.text}")
                yield None
        except Exception as e:
            logger.exception(f"E 联合早报错误{e}")


if __name__ == '__main__':
    header = {
        "Proxy-Connection": "keep-alive",
        "Cache-Control": "max-age=0",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "If-None-Match": "'6169e6c7-892f'",
        "If-Modified-Since": "Fri, 15 Oct 2021 20:38:31 GMT"
    }
    "https://www.zaobao.com/search?pageNo=1&pageSize=10&keywords=石油"
    search_url = Template("https://www.zaobao.com/search?pageNo=$page&pageSize=10&keywords=$keyword")
    a = Lianhezb()
    for i in a.get_request_from_keyword(header, search_url, '中国'):
        print(i)
        # response = requests.get(i.url, headers=header)
        # a = lianhezb_hotSearch()
        # for j in a.page_parse(response):
        #     print(j)
