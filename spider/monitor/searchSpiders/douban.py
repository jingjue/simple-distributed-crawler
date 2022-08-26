import json

import requests
import scrapy as scrapy

from monitor import logger


class Douban:
    name = "豆瓣"

    def __init__(self):
        pass

    def get_request_from_keyword(self, headers, search_url, keyword, *args, **kwargs):
        try:
            for i in range(0, 800, 20):
                url = search_url.format(i)  # 电影列表
                response = requests.get(url, headers=headers, timeout=50)
                json_response = json.loads(response.text)
                json_response = json_response['data']
                for data in json_response:
                    url = data['url'] + 'comments?sort=new_score&status=P'  # 每一个电影的url
                    print(url)
                    meta = {"url": url, "name": "douban", "platform": "douban", "keyword": keyword,
                            "callback": "page_parse"}
                    yield scrapy.Request(url=url, headers=headers, meta=meta,
                                         dont_filter=False)
        except:
            logger.exception(f"【豆瓣】搜索关键词出错")
            yield
