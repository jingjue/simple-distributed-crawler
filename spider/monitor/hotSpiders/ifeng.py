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


class Ifeng:
    name = "凤凰网"

    def __init__(self):
        pass

    def get_title(self, headers, url):
        try:
            title = Title()
            # 军事
            response = requests.get(url, headers=headers)
            response.encoding = "UTF-8"
            resp = Selector(response)
            key4 = resp.xpath("//ul[@class='list-1MCUb9Wx']//li//a")
            for key in key4:
                title.append(key.xpath("./text()").get())
            return True, title
        except Exception as e:
            logger.exception(f"url:{url}  {e}")
            return False, None


if __name__ == '__main__':
    base_url = "https://www.ifeng.com/"
    military_url = "https://mil.ifeng.com/"
    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': 'https://www.ifeng.com/',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        "cookie": "prov=cn0531; if_prov=cn0531; city=0532; if_city=0532; weather_city=sd_qd; userid=1632446830545_srzke76177; UM_distinctid=17c156a025b422-030e33b0e1536a-a7d173c-1fa400-17c156a025c839; region_ver=1.2; region_ip=124.129.172.x"
    }
    ifeng = Ifeng()
    a, b = ifeng.get_title(headers, military_url)
    print(b.keywords)
