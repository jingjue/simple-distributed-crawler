

import requests
import scrapy as scrapy
from scrapy import Selector

from monitor import logger


class QiangguoLT:
    name = "强国论坛"

    def __init__(self):
        pass

    def get_request_from_keyword(self, headers, search_url, keyword, *args, **kwargs):
        try:
                response = requests.get(search_url.substitute(), headers=headers)
                resp = Selector(response)
                info = resp.xpath('//ul[@class="replayList clearfix"]/li/p')
                meta = {"name": 'qiangguoLT', "callback": "page_parse"}
                for item in info:
                    time = item.xpath("./span").xpath("string(.)").get()[6:-1]
                    url = item.xpath("./a/@href").get()
                    yield scrapy.Request(url, headers=headers, meta=meta)
        except Exception as e:
            logger.exception(f"E 强国论坛错误{e}")

if __name__ == '__main__':
    header = {
      "Connection": "keep-alive",
      "Cache-Control": "max-age=0",
      "Upgrade-Insecure-Requests": "1",
      "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
      "Referer": "https://www.baidu.com/link?url=Roe-owpTn1HCV_NWcaGiP3dXZxzZtF15_VEYRV-Za2nWpqjxvJNhCBvke0hNmLDD&wd=&eqid=c4072dc900063ecc00000003616cec6f",
      "Accept-Language": "zh-CN,zh;q=0.9"
    }
    search_url = "http://bbs1.people.com.cn/board/1.html"
    a = QiangguoLT()
    for i in a.get_request_from_keyword(header, search_url):
        print(i)
        response = requests.get(i.url, headers=header)
        a = QGLT()
        for j in a.page_parse(response):
            print(j)


