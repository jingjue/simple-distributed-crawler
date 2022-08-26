"""
    @Author 王振琦
    @Splitter 王振琦
    @Date 2021/10/17 09:39
    @Describe 环球网
"""
from string import Template

import requests
import scrapy
from scrapy import Selector

from monitor import logger


class Huanqiu:
    name = "环球网"

    def __init__(self):
        pass

    def get_request_from_keyword(self, headers, search_url, keyword, *args, **kwargs):
        try:
            # 热点要闻
            response = requests.get(url=search_url.substitute(), headers=headers)
            response.encoding = "UTF-8"
            resp = Selector(response)
            new_as = resp.xpath("//div[@class='secNewsBlock']//div[@class='secNewsList']//p[@class='listp']//a")
            meta = {
                "platform": "环球网",
                "keyword": keyword,
                "callback": 'parse_single_page',
                "huanqiu_id": '0',
                "father": '0'
            }
            for a_key in new_as:
                yield scrapy.Request(a_key.xpath("./@href").get(), meta=meta, headers=headers)
        except Exception as e:
            logger.exception(f"E 环球网检索{e}")
            return None

if __name__ == '__main__':
    base_url = Template("https://www.huanqiu.com/")
    headers = {
        'authority': 'www.huanqiu.com',
        'cache-control': 'max-age=0',
        'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cookie': 'REPORT_UID_=CjodCqFD3LtKf7uuQ5cRNZrJYK0gTKMd; UM_distinctid=17c157cdb891af-0a2608eaa0b2c8-a7d173c-1fa400-17c157cdb8a574; _ma_tk=haf2xadtlyczelwjydrey76pnqrt1q7y; _ma_starttm=1634301033533; _ma_is_new_u=0; Hm_lvt_1fc983b4c305d209e7e05d96e713939f=1632448077,1632464248,1632646057,1634301034; CNZZDATA1000010102=1237754809-1632441932-https%253A%252F%252Fwww.baidu.com%252F%7C1634365484; Hm_lpvt_1fc983b4c305d209e7e05d96e713939f=1634369707',
        'if-modified-since': 'Sat, 16 Oct 2021 07:35:03 GMT',
    }
    huanqiu = Huanqiu()
    for a in huanqiu.get_request_from_keyword(headers, base_url, "中国"):
        print(a)