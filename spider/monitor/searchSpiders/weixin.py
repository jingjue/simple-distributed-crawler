"""
    @Author <UNK>
    @Splitter 王振琦
    @Date <UNK>
    @Describe 微信
"""

import requests
import scrapy
from scrapy import Selector

from monitor import logger


class Weixin:
    name = "微信"

    def __init__(self):
        pass

    def get_request_from_keyword(self, headers, search_url, keyword, *args, **kwargs):
        params = (
            ('type', '2'),
            ('ie', 'utf8'),
            ('s_from', 'hotnews'),
        )
        cookies = {
            'ABTEST': '0|1632473526|v1',
            'IPLOC': 'CN3702',
            'SUID': 'E246A7779F22A40A00000000614D91B6',
            'weixinIndexVisited': '1',
            'SUV': '0055E9D278E0DD08614D91B8D4FC3378',
            'SNUID': 'EF4DAC7B0B0EC1B4D0E11FC90C8E1258',
            'JSESSIONID': 'aaac23-7Kzbz26rEoqhUx',
        }
        try:
            for page in range(16):
                url = search_url.substitute(keyword=keyword, page=page)
                response = requests.get(url, headers=headers, params=params, cookies=cookies, timeout=10)
                html = Selector(text=response.text)
                results = html.xpath("//div[@class='txt-box']//a//@href").extract()
                for res in results:
                    url = 'https://weixin.sogou.com/' + res
                    meta = {
                        "url": url,
                        "name": "baidu",
                        "platform": "weixin",
                        "keyword": keyword,
                        "callback": "parse_page"
                    }
                    yield scrapy.Request(url=url, meta=meta, dont_filter=False)
        except Exception as e:
            logger.exception(f"E 西陆军事检索{e}")
            yield None


if __name__ == '__main__':
    search_url = 'https://weixin.sogou.com/weixin?query={}&s_from=hotnews&type=2&page={}&ie=utf8'
    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        'sec-ch-ua-mobile': '?0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Accept-Language': 'zh,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    weixin = Weixin()
    for a in weixin.get_request_from_keyword(headers=headers, search_url=search_url, keyword=""):
        print(a)