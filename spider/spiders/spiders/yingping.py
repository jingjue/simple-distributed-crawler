# Name:         dazhongdp.py
# Description:  大众点评首页点击电影后跳转页面
# Author:       东寿
# Date:         2022/8/5
import requests
from scrapy import Selector

from spiders.items import WeiboItem
from loguru import logger
from spiders.spiders import BaseSpider

headers_ = {
    'authority': 'www.jupingdz.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'max-age=0',
    # Requests sorts cookies= alphabetically
    'cookie': 'X_CACHE_KEY=15a249794adca2fd648edabd970d50b9; TUtk_2132_saltkey=N0j8q5jo; TUtk_2132_lastvisit=1659746362; TUtk_2132_sid=r770p1; Hm_lvt_912da476ba7494898b3693355f0da9d5=1659749965; Hm_lpvt_912da476ba7494898b3693355f0da9d5=1659749965; TUtk_2132_lastact=1659749963%09home.php%09misc; TUtk_2132_sendmail=1',
    'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
}


class YingP(BaseSpider):
    name = "大众点评"

    def __init__(self, one_project_name="default", **kwargs):
        super(YingP, self).__init__(one_project_name, logger)

    def parse_page(self, response):
        """
        解析大众点评网页中的电影评价网
        :param response:
        :return:
        """
        if response.status_code != 200:
            return None
        resp = Selector(response)
        dazhongdp = WeiboItem()
        dazhongdp["title"] = resp.xpath("//div[@class='cl']/h1/text()").get()
        content = ''
        for index,div in enumerate(resp.xpath("//div[@class='content_middle cl']//td[@id='article_content']/div")):
            if index == 0:
                continue
            content += div.xpath('string(.)').get().strip()
        dazhongdp["content"] = content
        dazhongdp["account"] = resp.xpath("//div[@class='avatar_info cl']//a/text()").get()
        dazhongdp["date"] = resp.xpath("//div[@class='avatar_info cl']//span[1]//text()").get()
        dazhongdp["likes"] = "".join(
            filter(str.isdigit, resp.xpath("//div[@class='avatar_info cl']//span[2]//text()").get()))
        dazhongdp["platform"] = "大众点评"
        return dazhongdp


if __name__ == "__main__":
    yp = YingP()
    url = "https://www.jupingdz.com/article-1419-1.html"
    resp = requests.get(url)

    print(yp.parse_page(resp))
