import logging

import scrapy
from scrapy import Selector
from loguru import logger
import requests
from base.utils import get_uid_by_name
from base.utils.time import get_time, zh_time_change, gen_id, baidu_time_change
from conf import default
from spiders.items import WeiboItem
from spiders.spiders import BaseSpider


class baidu_hotSearch(BaseSpider):
    name = "百度"

    def __init__(self, one_project_name="default", **kwargs):
        super(baidu_hotSearch, self).__init__(one_project_name, logger)
        self.name = 'baidu'
        self.hot_urls = ''
        self.search_urls = 'https://www.baidu.com/s?ie=utf-8&medium=2&rtt=1&bsst=1&rsv_dl=news_b_pn&cl=2&wd={}&tn=news&rsv_bp=1&oq=&rsv_btype=t&f=8&x_bfe_rqs=03208&x_bfe_tjscore=0.080000&tngroupname=organic_news&newVideo=12&goods_entry_switch=1&pn={}'
        self.startpage = 0
        self.event = None
        self.account = None

    def page_parse(self, response, **kwargs):
        baidu_item = WeiboItem()
        baidu_item["platform"] = "百度"
        baidu_item["now_date"] = get_time()
        html = Selector(text=response.text)
        title = html.xpath("//div[@class='index-module_articleTitle_28fPT ']//text()").extract()
        if title:
            title = title[0]
        baidu_item["title"] = self.try_get_title(response, title)

        account = html.xpath("//p[@class='index-module_authorName_7y5nA']//text()").extract()
        if account:
            account = account[0]
            baidu_item["account"] = account
        time = html.xpath("//div[@class='index-module_articleSource_2dw16']//span//text()").extract()
        # 获取发布时间
        if time:
            time = time[:2]
            time = ' '.join(str(i) for i in time)
            baidu_item['date'] = baidu_time_change(time.split("布时间: ")[1])
        contents = html.xpath("//div[@class='app-module_leftSection_EaCvy']//p//text()").extract()
        if contents:
            contents = ','.join(i for i in contents)
            baidu_item['content'] = contents
        logging.info(baidu_item.try_get("title", ""))
        logging.info(gen_id())
        baidu_item["uid"] = get_uid_by_name(baidu_item.try_get("title", "") + gen_id())
        baidu_item["mid"] = baidu_item["uid"]
        baidu_item["weibo_id"] = baidu_item["uid"]

        # 获取评论

        yield baidu_item


if __name__ == '__main__':
    baidu = baidu_hotSearch()
    # keyword = "烈士纪念日"
    # g = baidu.get_request_from_keyword(keyword)
    # url = "GET https://wappass.baidu.com/static/captcha/tuxing.html?ak=572be823e2f50ea759a616c060d6b9f1&backurl=https%3A%2F%2Fmbd.baidu.com%2Fnewspage%2Fdata%2Flandingsuper%3Fthird%3Dbaijiahao%26baijiahao_id%3D1732120548671569872%26c_source%3Dduedge&timestamp=1652423094&signature=2409f0ade66fc252803a3fb44f509058"
    # # 测试parse
    # for i in g:
    #     response = requests.get('https://baijiahao.baidu.com/s?id=1693898073551233504&wfr=spider&for=pc',
    #                             headers=baidu.page_headers, timeout=10)
    #     baidu.page_parse(response)
