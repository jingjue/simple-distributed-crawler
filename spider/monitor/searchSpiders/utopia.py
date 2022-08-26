"""
    @Author 王振琦
    @Splitter 王振琦
    @Date 2021/10/18 17:06
    @Describe 乌有之乡爬虫
"""

import time

import requests
import scrapy
from scrapy import Selector

from monitor import logger


class Utopia:
    name = "乌有之乡"

    def __init__(self):
        pass

    def get_request_from_keyword(self, headers, search_url, keyword, *args, **kwargs):
        format_url = "http://www.wyzxwk.com/article/ualist/index_{}.html"
        datetime = time.localtime(time.time())
        today_date = time.strftime('%Y-%m-%d', datetime)
        try:
            index = 1
            is_request = True

            response = requests.get(url=search_url.substitute(), headers=headers)
            response.encoding = "UTF-8"
            resp = Selector(response)
            article_box = resp.xpath("/html/body/div[@class='g-bd']")

            while is_request is True:
                # 解析文章列表
                article_list = article_box.xpath("./div[@class='g-mn-1']/div/ul[@class='m-list']/li")
                for article_item in article_list:
                    data_tag = article_item.xpath("./span[@class='s-grey-2 f-fr']")
                    date = str.split(data_tag.xpath("./text()").get(), " ")[0]

                    if today_date == date:
                        a_tag = article_item.xpath(".//a")
                        keyword_item = a_tag.xpath("./text()").get()
                        url = a_tag.xpath("./@href").get()
                        meta = {
                            "platform": "乌有之乡",
                            "keyword": keyword_item,
                            "callback": 'parse_single_page',
                            "utopia_id": '0',
                            "father": '0'
                        }
                        yield scrapy.Request(url, meta=meta, headers=headers)
                    else:
                        is_request = False

                if is_request is True:
                    index += 1
                    url = str.format(format_url, index)
                    response = requests.get(url=url, headers=headers)
                    response.encoding = "UTF-8"
                    resp = Selector(response)
                    article_box = resp.xpath("/html/body/div[@class='g-bd']")
        except Exception as e:
            logger.exception(f"E 乌有之乡检索{e}")
            return None


if __name__ == '__main__':
    base_url = "http://www.wyzxwk.com/article/ualist/index.html"
    headers = {
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
        'Referer': 'http://www.wyzxwk.com/',
    }
    utopia = Utopia()
    for a in utopia.get_request_from_keyword(headers, base_url, ""):
        print(a)
