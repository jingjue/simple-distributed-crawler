# Name:         yingping.py
# Description:
# Author:       东寿
# Date:         2022/8/6

import requests
import scrapy as scrapy
from scrapy import Selector

from monitor import logger


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


class YingP:
    name = "大众点评"

    def __init__(self):
        pass

    def get_request_from_keyword(self, headers, search_url, keyword, *args, **kwargs):
        try:
            search_url = "https://www.jupingdz.com/"
            response = requests.get(search_url, headers=headers_)
            if response.status_code!=200:
                return None
            resp = Selector(response)
            for url_xpath in resp.xpath("//ul[@class='ui_list cl']//h3[@class='clr']//a/@href"):
                url = url_xpath.get()
                meta = {"callback":"parse_page","url":url}
                yield scrapy.Request(url, headers=headers_, meta=meta)

        except Exception as e:
            logger.exception(f"E 大众点评{e}")

