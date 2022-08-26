"""
    @Author 王振琦
    @Splitter 王振琦
    @Date 2021/10/18 17:06
    @Describe 乌有之乡爬虫
"""
import time

import requests
from scrapy import Selector
from loguru import logger

from base.utils import get_uid_by_name
from base.utils.time import gen_id, get_date
from spiders.items import WeiboItem
from spiders.spiders import BaseSpider


class Utopia(BaseSpider):
    name = "乌有之乡"

    def __init__(self, one_project_name="default",**kwargs):
        super(Utopia, self).__init__(one_project_name, logger)

    def parse_single_page(self, response, **kwargs):

        datetime = time.localtime(time.time())
        today_date = time.strftime('%Y-%m-%d', datetime)

        response.encoding = "UTF-8"
        resp = Selector(response)

        keyword = response.meta.get("keyword")
        article_box = resp.xpath("/html/body/div[@class='g-bd']/div[@class='g-mn-1']/div[@class='m-article s-shadow']")
        title = article_box.xpath("./h1/text()").get().replace("<i>", "").replace("</i>", "").replace("\n", "")
        title = self.try_get_title(response,title)
        account = article_box.xpath("./div[@class='m-atc f-cb']/div[@class='f-fl']/span[1]/text()").get()

        content_tags = article_box.xpath("./article/p")
        content = ""
        for tag in content_tags:
            content_item = tag.xpath("./text()").get()
            if content_item is not None:
                content_item = content_item.replace("\u3000\u3000", "")
                content += content_item

        utopia_item = WeiboItem()
        utopia_item["account"] = account
        utopia_item["uid"] = get_uid_by_name(account)
        utopia_item["weibo_id"] = get_uid_by_name(title + str(gen_id()))
        utopia_item["mid"] = get_uid_by_name(keyword)
        utopia_item["content"] = content
        utopia_item["title"] = title
        utopia_item["date"] = today_date
        utopia_item["now_date"] = get_date()
        utopia_item["platform"] = "乌有之乡"

        return utopia_item


if __name__ == '__main__':
    url = "http://www.wyzxwk.com/Article/shiping/2022/04/453395.html"
    headers = {
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
        'Referer': 'http://www.wyzxwk.com/',
    }
    utopia = Utopia()
    response = requests.get(url=url, headers=headers)
    utopia.parse_single_page(response)
