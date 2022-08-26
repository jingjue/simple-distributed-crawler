"""
    @Author 王振琦
    @Splitter 王振琦
    @Date 2021/10/17 09:39
    @Describe 人民日报
"""

import requests
from scrapy import Selector
from loguru import logger

from base.utils import get_uid_by_name
from base.utils.time import gen_id, get_date
from conf.default import Default_hot
from spiders.items import WeiboItem
from spiders.spiders import BaseSpider


class PeoplePaper(BaseSpider):
    name = "人民日报"

    def __init__(self, one_project_name="default",**kwargs):
        super(PeoplePaper, self).__init__(one_project_name, logger)

    def parse_page(self, response, **kwargs):
        pp_item = WeiboItem()
        resp = Selector(response)
        article = resp.xpath("//div[@class='article-box']/div[@class='article']")
        atl_ps = article.xpath("./div[@id='ozoom']/p")
        keyword = response.meta.get("keyword")

        content = ""
        for atl_p in atl_ps:
            content_item = atl_p.xpath("./text()").get()
            content += content_item

        h3 = article.xpath("./h3/text()")
        h1 = article.xpath("./h1/text()")
        h2 = article.xpath("./h2/text()")
        title_h3 = ""
        title_h1 = ""
        title_h2 = ""
        if (len(h3) > 0):
            title_h3 = h3.get() + " "
        if (len(h1) > 0):
            title_h1 = h1.get() + " "
        if (len(h2) > 0):
            title_h2 = h2.get()
        title = title_h3 + title_h1 + title_h2

        date_str = article.xpath("./p[@class='sec']/span[@class='date']").xpath("./text()").get()
        account = str.split(date_str, " ")[10].split("\r\n")[0]
        date = str.split(date_str, " ")[30].split("\r\n\xa0\r\n")[0]

        title = self.try_get_title(response, title)
        pp_item["account"] = account
        pp_item["uid"] = get_uid_by_name(account)
        pp_item["weibo_id"] = get_uid_by_name(title + str(gen_id()))
        pp_item["mid"] = get_uid_by_name(keyword)
        pp_item["content"] = content
        pp_item["title"] = title
        pp_item["hot"] = Default_hot
        pp_item["date"] = date
        pp_item["now_date"] = get_date()
        pp_item["platform"] = "人民日报"
        return pp_item


if __name__ == '__main__':
    url = "http://paper.people.com.cn/rmrb/html/2022-04/18/nw.D110000renmrb_20220418_1-01.htm"
    headers = {
        'Proxy-Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'If-None-Match': '"6169e6c7-892f"',
        'If-Modified-Since': 'Fri, 15 Oct 2021 20:38:31 GMT',
    }
    response = requests.get(url, headers=headers)
    response.encoding = "UTF-8"
    resp = Selector(response)
