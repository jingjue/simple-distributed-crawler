import requests
from scrapy import Selector

from monitor.titleManager import Title
from monitor import logger


class People():
    name = "人民网"

    def __init__(self):
        self.society_url = "http://society.people.com.cn/GB/136657/index.html"
        self.internation_url = "http://world.people.com.cn/GB/157278/index.html"
        self.junshi_url = "http://military.people.com.cn/GB/172467/index.html"
        self.search_url = "http://search.people.cn/api-search/front/search"

    def get_title(self, headers, url):
        try:
            title = Title()
            # 社会要闻
            response = requests.get(url=self.society_url, headers=headers)
            response.encoding = 'GBK'
            resp = Selector(response)

            key1 = resp.xpath("//ul[@class='list_16 mt10']/li")
            key2 = resp.xpath("//ul[@class=' list_16 mt10']/li")
            for key in key1:
                title.append(key.xpath("./a/text()").get())
            for key in key2:
                title.append(key.xpath("./a/text()").get())

            # 国际
            response = requests.get(self.internation_url, headers=headers)
            response.encoding = "GBK"
            resp = Selector(response)
            key3 = resp.xpath("//ul[@class='list_ej2  mt20']/li")
            for key in key3:
                title.append(key.xpath("./a/text()").get())

            # 军事
            response = requests.get(self.junshi_url, headers=headers)
            response.encoding = "GBK"
            resp = Selector(response)
            key4 = resp.xpath("//ul[@class='list_16 mt10']/li")
            for key in key4:
                title.append(key.xpath("./a/text()").get())
            key4 = resp.xpath("//ul[@class=' list_16 mt10']/li")
            for key in key4:
                title.append(key.xpath("./a/text()").get())
            return True,title
        except Exception as e:
            logger.error(e)
            return False,None
