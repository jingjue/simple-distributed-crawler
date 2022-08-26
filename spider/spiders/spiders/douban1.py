import logging
import re

import scrapy
from scrapy import Selector
from loguru import logger
import requests
from base.utils import get_uid_by_name
from base.utils.time import get_time, zh_time_change, gen_id, baidu_time_change
from conf import default
from monitor.searchSpiders.douban import Douban
from spiders.items import WeiboItem
from spiders.spiders import BaseSpider


class douban_hotSearch(BaseSpider):
    name = "豆瓣"

    def __init__(self, one_project_name="default", **kwargs):
        super(douban_hotSearch, self).__init__(one_project_name, logger)
        self.name = 'douban'
        self.hot_urls = ''
        self.id_urls = 'https://movie.douban.com/review/best/'
        self.full_url='https://movie.douban.com/j/review/{}/full'
        self.startpage = 0
        self.step_size=20
        self.event = None
        self.account = None

    def page_parse(self, response, **kwargs):
        douban_item = WeiboItem()
        douban_item["platform"] = "豆瓣"
        douban_item["now_date"] = get_time()
        text=response.text
        res=''.join(re.findall('[\u4e00-\u9fa5-\，\。]',text))
        content_list=res.split("-")
        douban_item["content"]=res
        douban_item["title"]="豆瓣影评"
        if content_list[7]!="" :
            douban_item["account"]=content_list[10]
        else:
            douban_item["account"]=content_list[8]
        douban_item["uid"] = get_uid_by_name(douban_item.try_get("title", "") + gen_id())
        douban_item["mid"] = douban_item["uid"]
        douban_item["weibo_id"] = douban_item["uid"]
        douban_item['date'] = get_time()
        yield douban_item


if __name__ == '__main__':
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
    # d=Douban()
    # keyword=""
    # search_url= "https://movie.douban.com/review/best/?start={}"
    # g = d.get_request_from_keyword(keyword=keyword,search_url=search_url,headers=headers)
    douban=douban_hotSearch()
    # for i in g:
    response=requests.get("https://movie.douban.com/j/review/14553608/full",headers=headers)
    douban.page_parse(response)
    # keyword = "烈士纪念日"
    # g = baidu.get_request_from_keyword(keyword)
    # url = "GET https://wappass.baidu.com/static/captcha/tuxing.html?ak=572be823e2f50ea759a616c060d6b9f1&backurl=https%3A%2F%2Fmbd.baidu.com%2Fnewspage%2Fdata%2Flandingsuper%3Fthird%3Dbaijiahao%26baijiahao_id%3D1732120548671569872%26c_source%3Dduedge&timestamp=1652423094&signature=2409f0ade66fc252803a3fb44f509058"
    # # 测试parse
    # for i in g:
    #     response = requests.get('https://baijiahao.baidu.com/s?id=1693898073551233504&wfr=spider&for=pc',
    #                             headers=baidu.page_headers, timeout=10)
    #     baidu.page_parse(response)
