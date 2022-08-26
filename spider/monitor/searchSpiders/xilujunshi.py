# -*-coding:utf-8-*- 、
# Team : upcedu.nlp
# Author：dongshou
# Splitter: 王振琦
# Date ：2021/10/15 下午4:01
# Describe ：西陆军事
from string import Template

import requests
import scrapy
from scrapy import Selector

from monitor import logger


class XiLu:
    name = "西陆军事"

    def __init__(self):
        pass

    def get_request_from_keyword(self, headers, search_url, keyword, *args, **kwargs):
        try:
            response = requests.get(url=search_url.substitute(), headers=headers)
            response.encoding = "UTF-8"
            resp = Selector(response)
            meta = {"name": "xilujunshi", "callback": "parse_single_page"}
            # 今日推荐
            result = resp.xpath('//a[@target="_blank"]')
            for labela in result:
                url = labela.xpath("./@href").get()
                if 'http://' in url and "xilu" in url and len(url) > 24:
                    meta["url"] = url
                    yield scrapy.Request(url, headers=headers, meta=meta)
        except Exception as e:
            logger.exception(f"E 西陆军事检索{e}")
            yield None


if __name__ == '__main__':
    url = Template("http://junshi.xilu.com/")
    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Referer': 'https://www.baidu.com/link?url=ImagoC3DE1p0D55S7qbzXrjJ3sGeO3nC9BwzL8q75Wtil8_pJOWqeNA2dRgp8r3n&wd=&eqid=f4b4737e0001ccbe0000000361693525',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    xilu = XiLu()
    for a in xilu.get_request_from_keyword(headers=headers, search_url=url, keyword=""):
        print(a.url)
