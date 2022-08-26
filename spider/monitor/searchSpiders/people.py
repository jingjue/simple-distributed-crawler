from string import Template
from time import sleep

import requests
import scrapy
from base.utils.time import people_time_from_url, get_delta_time
from monitor import logger
from conf.default import Default_people_page, Default_delta_time
# from spiders.spiders.people import People


class People_search:
    name = "人民网"

    def __init__(self):
        pass

    def get_request_from_keyword(self, headers, search_url, keyword, *args, **kwargs):
        try:
            page = 1
            all_search_page = 10
            while page < Default_people_page and page < all_search_page:
                data = {"key": keyword, "page": page, "limit": 10, "hasTitle": True, "hasContent": True,
                        "isFuzzy": True,
                        "type": 0, "sortType": 2, "startTime": 0, "endTime": 0}
                s = requests.session()
                s.keep_alive = False
                response = requests.post(search_url.substitute(), json=data, headers=headers)
                sleep(5)
                data = response.json()["data"]
                all_search_page = data["pages"]
                results = data["records"]
                for result in results:
                    url = result["url"]
                    if not url:
                        continue
                    date = people_time_from_url(url)
                    if date and get_delta_time(date) > Default_delta_time:
                        continue
                    meta = {"platform": "weibo", "keyword": 'None', "callback": 'page_parse',
                            "weibo_id": '0', "father": '0', "name": 'people'}
                    yield scrapy.Request(url, headers=headers, meta=meta)
                page += 1
        except Exception as e:
            logger.exception(f"E 人民网错误{e}")


if __name__ == '__main__':
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Origin': 'http://search.people.cn',
        'Referer': 'http://search.people.cn/s/?keyword=%E6%8A%97%E7%96%AB&st=0&_=1652337831597',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36',
    }
    search_url = Template("http://search.people.cn/search-platform/front/search")
    a = People_search()
    a.get_request_from_keyword(headers, search_url, '石油')
    for i in a.get_request_from_keyword(headers, search_url, '石油'):
        print(i)
        response = requests.get(i.url, headers=headers)
        response.encoding = 'GBK'
        a = People('')
        for j in a.page_parse(response):
            print(j)
