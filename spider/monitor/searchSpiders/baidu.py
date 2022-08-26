from string import Template

import requests
import scrapy as scrapy
from scrapy import Selector
from monitor import logger

class Baidu:
    name = "百度"

    def __init__(self):
        pass

    def get_request_from_keyword(self, headers, search_url, keyword, *args, **kwargs):
        try:
            url = search_url.substitute(keyword=keyword, page=0)  # 从第一页开始
            response = requests.get(url, headers=headers, timeout=10)
            html = Selector(text=response.text)
            num_text = html.xpath("//span//text()").extract()[1]  # 从页面中获取有多少篇资讯
            num = "".join(list(filter(str.isdigit, num_text)))
            num = 100 if not num else int(num)
            for i in range(0, num, 10):
                url = search_url.substitute(keyword=keyword, page=i)  # 修改url翻页
                response = requests.get(url, headers=headers, timeout=10)
                html = Selector(text=response.text)
                results = html.xpath("//a[@class='news-title-font_1xS-F']//@href").extract()
                for url in results:
                    meta = {"url": url, "name": "baidu", "platform": "baidu", "keyword": keyword, "callback": "page_parse"}
                    yield scrapy.Request(url=url, meta=meta, dont_filter=False)
        except Exception as e:
            logger.error(f"E 百度检索{e}")
            return None

if __name__ == '__main__':
    search_url = Template("https://www.baidu.com/s?ie=utf-8&medium=2&rtt=1&bsst=1&rsv_dl=news_b_pn&cl=2&wd=$keyword&tn=news&rsv_bp=1&oq=&rsv_btype=t&f=8&x_bfe_rqs=03208&x_bfe_tjscore=0.080000&tngroupname=organic_news&newVideo=12&goods_entry_switch=1&pn=$page")
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
        'sec-ch-ua': "' Not A;Brand';v='99', 'Chromium';v='100', 'Google Chrome';v='100'",
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': "Windows",
    }
    a = Baidu()
    for i in a.get_request_from_keyword(headers, search_url, "专访：靠制裁达不到结束俄乌冲突的预期目标——访匈牙利国"):
        print(i)
