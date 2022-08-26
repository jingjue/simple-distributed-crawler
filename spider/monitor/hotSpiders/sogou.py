"""
    @Author 王振琦
    @Splitter 王振琦
    @Date 2021/10/17 09:39
    @Describe 人民日报
"""

import requests
from scrapy import Selector

from monitor.titleManager import Title
from monitor import logger


class Sogou():
    name = "搜狗"

    def __init__(self):
        pass

    def get_title(self, headers, url):
        try:
            title = Title()
            response = requests.get(url=url, headers=headers)
            response.encoding = "GBK"
            resp = Selector(response)
            div_tags = resp.xpath("//*[@id='mil']/div[@class='news-channel-list']/div[@class='channel-list']")
            for div_tag in div_tags:
                list_tags = div_tag.xpath("./ul/li")
                for list_tag in list_tags:
                    a_title = list_tag.xpath("./a/@title").get()
                    title.append(a_title)
            return True, title
        except Exception as e:
            logger.exception(f"url:{url}  {e}")
            return False, None


if __name__ == '__main__':
    base_url = "https://news.sogou.com/mil.shtml"
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': 'SUID=2EFEE1708930A40A0000000062133C13; SUV=1648519191933492; SMYUV=1648519191933368; UM_distinctid=17fd3669deb482-05f3cd78384fd7-9771a3f-1fa400-17fd3669decbb1; ariaDefaultTheme=null; ssuid=9641808190; IPLOC=CN3702; SNUID=F19ABD756F6AB3816E02C4E76FFB6F78; GOTO=Af99044; toutiao_city_news=%E5%8C%97%E4%BA%AC; _ga=GA1.2.2127609069.1650289709; _gid=GA1.2.1204745515.1650289709; ld=5lllllllll2AgQZ9lllllpJNbWylllllpdaCXZllllYlllll9klll5@@@@@@@@@@; newsCity=%u9752%u5C9B; LSTMV=357%2C566; LCLKINT=3199',
        'Host': 'news.sogou.com',
        'Referer': 'https://news.sogou.com/index.shtml',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': 'Windows',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36'
    }
    sogou = Sogou()
    a, b = sogou.get_title(headers=headers, url=base_url)
    print(b.keywords)
