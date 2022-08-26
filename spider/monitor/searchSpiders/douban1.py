import json

import requests
import scrapy as scrapy
from scrapy import Selector

from monitor import logger


class Douban:
    name = "豆瓣"

    def __init__(self):
        pass


    def get_request_from_keyword(self, headers, search_url, keyword, *args, **kwargs):
        try:
            base_url = "https://movie.douban.com/j/review/{}/full"
            for i in range(0,100,20):
                url=search_url.format(i)
                response = requests.get(url, headers=headers, timeout=50)
                html = Selector(text=response.text)
                review_list=html.xpath('//div[contains(@class,"review-list")]')
                for review in review_list:
                    id_list=review.xpath('.//@data-cid')
                    for id in id_list:
                        url=base_url.format(id.get())
                        meta = {"url": url, "name": "douban", "platform": "douban", "keyword": keyword,
                                "callback": "page_parse"}
                        yield scrapy.Request(url=url, headers=headers, meta=meta,
                                             dont_filter=False)

            # for i in range(0, 800, 20):
            #     url = search_url.format(i)  # 电影列表
            #     response = requests.get(url, headers=headers, timeout=50)
            #     json_response = json.loads(response.text)
            #     json_response = json_response['data']
            #     for data in json_response:
            #         url = data['url'] + 'comments?sort=new_score&status=P'  # 每一个电影的url
            #         print(url)
            #         meta = {"url": url, "name": "douban", "platform": "douban", "keyword": keyword,
            #                 "callback": "page_parse"}
            #         yield scrapy.Request(url=url, headers=headers, meta=meta,
            #                              dont_filter=False)
        except:
            logger.exception(f"【豆瓣】搜索出错")
            yield

if __name__ == '__main__':
    douban = Douban()
    headers = {
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
        "sec-ch-ua": "'Chromium';v='92', ' Not A;Brand';v='99', 'Google Chrome';v='92'",
        "sec-ch-ua-mobile": ",?0",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Accept-Language": "zh,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6"
    }
    search_url= "https://movie.douban.com/review/best/?start={}"
    douban.get_request_from_keyword(headers=headers,search_url=search_url,keyword='')