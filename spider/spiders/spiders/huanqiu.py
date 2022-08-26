"""
    @Author 王振琦
    @Splitter 王振琦
    @Date 2021/10/17 09:39
    @Describe 环球网
"""

import requests
from scrapy import Selector
from loguru import logger

from base.utils import get_uid_by_name
from base.utils.time import get_date, gen_id
from spiders.items import WeiboItem
from spiders.spiders import BaseSpider



class Huanqiu(BaseSpider):
    name = "环球网"

    def __init__(self, one_project_name="default",**kwargs):
        super(Huanqiu, self).__init__(one_project_name, logger)

    def parse_single_page(self, response, **kwargs):
        resp = Selector(response)
        keyword = response.meta.get("keyword")

        account_tag = resp.xpath("//div[@class='t-container']//div[@class='metadata-info']//span[@class='source']//a")
        if 0 == len(account_tag):
            account_tag = resp.xpath(
                "//div[@class='t-container']//div[@class='metadata-info']//span[@class='source']/span")
        account = account_tag.xpath("./text()").get()

        title_tag = resp.xpath("//div[@class='t-container']/div[@class='t-container-title']/h3")
        title = title_tag.xpath("./text()").get()

        time_tag = resp.xpath("//div[@class='t-container']//div[@class='metadata-info']//p[@class='time']")
        date = str.split(time_tag.xpath("./text()").get(), " ")[0]

        psgs = resp.xpath("//section[@data-type='rtext']//p")
        content = ""
        for psg in psgs:
            if 0 != len(psg.xpath("./text()")):
                content_item = psg.xpath("./text()").get()
                content += content_item

        huanqiu_item = WeiboItem()
        title = self.try_get_title(response, title)
        huanqiu_item["account"] = account
        huanqiu_item["uid"] = get_uid_by_name(account)
        huanqiu_item["weibo_id"] = get_uid_by_name(title + str(gen_id()))
        huanqiu_item["mid"] = get_uid_by_name(keyword)
        huanqiu_item["content"] = content
        huanqiu_item["title"] = title
        huanqiu_item["date"] = date
        huanqiu_item["now_date"] = get_date()
        huanqiu_item["platform"] = "环球网"
        return huanqiu_item


if __name__ == '__main__':
    url = "http://go.huanqiu.com/article/47fPi1vgllu"
    headers = {
        'authority': 'www.huanqiu.com',
        'cache-control': 'max-age=0',
        'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cookie': 'REPORT_UID_=CjodCqFD3LtKf7uuQ5cRNZrJYK0gTKMd; UM_distinctid=17c157cdb891af-0a2608eaa0b2c8-a7d173c-1fa400-17c157cdb8a574; _ma_tk=haf2xadtlyczelwjydrey76pnqrt1q7y; _ma_starttm=1634301033533; _ma_is_new_u=0; Hm_lvt_1fc983b4c305d209e7e05d96e713939f=1632448077,1632464248,1632646057,1634301034; CNZZDATA1000010102=1237754809-1632441932-https%253A%252F%252Fwww.baidu.com%252F%7C1634365484; Hm_lpvt_1fc983b4c305d209e7e05d96e713939f=1634369707',
        'if-modified-since': 'Sat, 16 Oct 2021 07:35:03 GMT',
    }
    response = requests.get(url, headers)
    huanqiu = Huanqiu()
    huanqiu.parse_single_page(response)
