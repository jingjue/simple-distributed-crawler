# encoding:utf-8
import logging
from string import Template

import requests
from loguru import logger
from scrapy import Selector

from base.utils.time import get_time
# from monitor.searchSpiders.toutiao import Toutiao
from spiders.items import WeiboItem
from spiders.spiders import BaseSpider

class ToutiaoContent(BaseSpider):
    name = "头条"

    def __init__(self, one_project_name="default",**kwargs):
        super(ToutiaoContent, self).__init__(one_project_name, logger)

    def page_single_parse(self, response, **kwargs):
        try:
            toutiao_item = WeiboItem()
            toutiao_item["platform"] = "头条"
            toutiao_item["now_date"] = get_time()
            logging.info('toutiao_text',response.text)
            html = Selector(text=response.text)
            account = html.xpath("//div[@class='article-meta']//a//text()").extract()
            if account:
                account = account[0]
                toutiao_item['account'] = account
            time = html.xpath("//div[@class='article-meta']//span//text()").extract()
            if time:
                if len(time) > 3:
                    time = time[1]
                else:
                    time = time[0]
                toutiao_item['date'] = time
            contents = html.xpath("//div[@class='article-content']//p//text()").extract()
            if contents:
                contents = ','.join(str(i).strip() for i in contents)
                toutiao_item['content'] = contents
            else:
                return None
            title = html.xpath("//div[@class='article-content']//h1//text()").extract()
            if title:
                title = title[0]
            else:
                title = None
            # title = self.try_get_title(response, title)
            toutiao_item['title'] = title
            commentId = response.url.split('/')[3][1:]  # 获取commentId
            toutiao_item["weibo_id"] = commentId  # Id标识此条新闻
            toutiao_item["mid"] = commentId
            toutiao_item["uid"] = commentId
            logging.info(toutiao_item)
            yield toutiao_item

        except Exception as e:
            logger.exception(f"【头条】页面解析报错 {e}")
            yield None




if __name__ == '__main__':
    search_url = Template('https://so.toutiao.com/search?keyword=$keyword&pd=synthesis&source=pagination&dvpf=pc&aid=4916&page_num=$page&search_id=2021100715304401015013503047912E3D&filter_vendor=site&index_resource=site&filter_period=all&min_time=0&max_time=1633591574')
    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        'sec-ch-ua-mobile': '?0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Accept-Language': 'zh,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    cookies = {
        'tt_webid': '7011123276119787038',
        '_S_DPR': '1.25',
        '_S_IPAD': '0',
        'MONITOR_WEB_ID': '7011123276119787038',
        '_S_WIN_WH': '1536_754',
        'ttwid': '1%7C1Ez9zDuow8ub7YaZrr9RTLjEEk10ihjU30SrbadLCRU%7C1633598649%7Ced44c30901695d3191d527907a0cfc5fce061d11e8965c870a6b63b276a7b517',
    }

    toutiao = Toutiao()
    toutiaoC = ToutiaoContent()

    for a in toutiao.get_request_from_keyword(headers=headers, search_url=search_url, keyword="北约“秀肌肉”动作频频"):
        response = requests.get(a.url, headers=headers, cookies=cookies)
        for b in toutiaoC.page_single_parse(response):
            print(b)
