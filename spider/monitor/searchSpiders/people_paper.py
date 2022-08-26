"""
    @Author 王振琦
    @Splitter 王振琦
    @Date 2021/10/17 09:39
    @Describe 人民日报
"""

import datetime

import requests
import scrapy as scrapy
from scrapy import Selector

from monitor import logger


class PeoplePaper:
    name = "人民日报"

    def __init__(self):
        pass

    def get_request_from_keyword(self, headers, search_url, keyword, *args, **kwargs):
        """
        根据关键词获取检索结果
        :param headers: 请求头
        :param cookie: 请求Cookie
        :param search_url: 查找链接
        :param keyword: 关键词
        :param args:
        :param kwargs: 日期相关关键词
        :return:
        """
        try:
            date_str = datetime.datetime.now().strftime("%Y-%m/%d")
            prefix_url = search_url.substitute(date=date_str)
            top_url = prefix_url + "nbs.D110000renmrb_01.htm"
            top_response = requests.get(top_url, headers=headers)
            top_response.encoding = "UTF-8"
            top_resp = Selector(top_response)
            div_xpath = "/html/body/div[@class='main w1000']/div[@class='right right-main']/div[@class='swiper-box']/div[@class='swiper-container']/div[@class='swiper-slide']"
            div_tags = top_resp.xpath(div_xpath)

            meta = {
                "platform": "人民日报",
                "keyword": keyword,
                "callback": 'parse_page',
                "people_paper_id": '0',
                "father": '0'
            }

            for div_tag in div_tags:
                board_link = div_tag.xpath("./a[@id='pageLink']").xpath("./@href").get()
                # 有的链接带“./”
                board_link = board_link.split("./")[-1]
                board_url = prefix_url + board_link
                board_response = requests.get(board_url, headers=headers)
                board_response.encoding = "UTF-8"
                board_resp = Selector(board_response)
                a_xpath = "/html/body/div[@class='main w1000']/div[@class='right right-main']/div[@class='news']/ul[@class='news-list']/li/a"
                a_tags = board_resp.xpath(a_xpath)

                for a_tag in a_tags:
                    link = a_tag.xpath("./@href").get()
                    url = prefix_url + link
                    yield scrapy.Request(url, meta=meta, headers=headers)
        except Exception as e:
            logger.exception(f"E 人民日报检索{e}")
            return None


if __name__ == '__main__':
    url_cxt = "http://paper.people.com.cn/rmrb/html/{}/"
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
    a = PeoplePaper()
    for b in a.get_request_from_keyword(headers, url_cxt, ""):
        print(b)
