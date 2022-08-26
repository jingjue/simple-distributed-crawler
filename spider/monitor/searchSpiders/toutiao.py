# encoding:utf-8
"""
    @Author <UNK>
    @Splitter 王振琦
    @Date <UNK>
    @Describe 头条
"""
import logging
from string import Template

import requests
import scrapy
from scrapy import Selector

from monitor import logger


class Toutiao:
    name = "头条"

    def __init__(self):
        pass

    def get_request_from_keyword(self, headers, search_url, keyword, *args, **kwargs):
        keyword = keyword.encode('utf-8')
        cookies = {
            '__ac_signature': '_02B4Z6wo00f01MDV78QAAIDAQNcVhmwpjazA9etAAFF-a6',
            'ttcid': '9e272d5d6ba94e1bad155e2d7218aea529',
            'csrftoken': '92cbd3405a233f4059f2aa396f563660',
            '_S_IPAD': '0',
            'tt_webid': '7011051839294735886',
            '_S_WIN_WH': '1920_937',
            '_S_DPR': '1',
            'local_city_cache': '%E9%9D%92%E5%B2%9B',
            's_v_web_id': 'verify_l6ka2hbh_9m3Db80Z_YH1p_4uPA_8N3p_ZbOXfcNCzbul',
            '_tea_utm_cache_24': 'undefined',
            'passport_csrf_token': '660023f368faa2b9933329a3395b33cc',
            'passport_csrf_token_default': '660023f368faa2b9933329a3395b33cc',
            'sso_uid_tt': '5d281d9a9145d50a5b37c2df29f4fb16',
            'sso_uid_tt_ss': '5d281d9a9145d50a5b37c2df29f4fb16',
            'toutiao_sso_user': '48e91653d0941c02449532e2c9b42dc0',
            'toutiao_sso_user_ss': '48e91653d0941c02449532e2c9b42dc0',
            'sid_ucp_sso_v1': '1.0.0-KGM2OGM0MTFlMWViMTlkNDhhYWUwN2FmMzZlNGUyNThkMWM2NzE3MzUKFQiE5IDL8I2BAhDErcKXBhgYOAhACxoCaGwiIDQ4ZTkxNjUzZDA5NDFjMDI0NDk1MzJlMmM5YjQyZGMw',
            'ssid_ucp_sso_v1': '1.0.0-KGM2OGM0MTFlMWViMTlkNDhhYWUwN2FmMzZlNGUyNThkMWM2NzE3MzUKFQiE5IDL8I2BAhDErcKXBhgYOAhACxoCaGwiIDQ4ZTkxNjUzZDA5NDFjMDI0NDk1MzJlMmM5YjQyZGMw',
            'sid_guard': '48e91653d0941c02449532e2c9b42dc0%7C1659934406%7C5184000%7CFri%2C+07-Oct-2022+04%3A53%3A26+GMT',
            'uid_tt': '5d281d9a9145d50a5b37c2df29f4fb16',
            'uid_tt_ss': '5d281d9a9145d50a5b37c2df29f4fb16',
            'sid_tt': '48e91653d0941c02449532e2c9b42dc0',
            'sessionid': '48e91653d0941c02449532e2c9b42dc0',
            'sessionid_ss': '48e91653d0941c02449532e2c9b42dc0',
            'sid_ucp_v1': '1.0.0-KDg4ZmFkY2FlZmFkNzFlY2Y5NTFmMTcwYTg3MzJhOTEwYTg3NmYzY2IKFwiE5IDL8I2BAhDGrcKXBhgYIAw4CEALGgJobCIgNDhlOTE2NTNkMDk0MWMwMjQ0OTUzMmUyYzliNDJkYzA',
            'ssid_ucp_v1': '1.0.0-KDg4ZmFkY2FlZmFkNzFlY2Y5NTFmMTcwYTg3MzJhOTEwYTg3NmYzY2IKFwiE5IDL8I2BAhDGrcKXBhgYIAw4CEALGgJobCIgNDhlOTE2NTNkMDk0MWMwMjQ0OTUzMmUyYzliNDJkYzA',
            'tt_anti_token': 'BRDs1FiBfq0s-dd8f4822020549d9d03a2c1cb56577f334f492091afee7ca2b7598f79ac82f2d',
            'tt_scid': 'GSqws7879Nl9Eg1j2hNjhI85Nm2OXOtSI3RMIwTiV054rjOpFxvvNuu7L2O.Dew812f9',
            'ttwid': '1%7CKikwPzFUPse4ufVzHENGvOw5oetEY9bglPFmtDdTX3A%7C1659934409%7Cf10091c59dc041da26f9ba2bf80c691eec164f8c528bfcdb7548c3d5ea541fdf',
            'MONITOR_WEB_ID': '620fcb55-6203-4989-9927-52ea19dfe451',
            'odin_tt': '7e284d9c5622b960acfefbdcea5a71d45260cbcb5abb4f1451e111757c00de7305b73f1db8587a6766b59d830678275b',
        }
        params = {
            'is_new_connect': '0',
            'is_new_user': '0',
        }
        try:
            for i in range(0, 16):
                url = search_url.substitute(keyword=keyword, page=i).encode('utf-8')
                response = requests.get(url, headers=headers, params=params, cookies=cookies, timeout=10)
                html = Selector(text=response.text)
                results = html.xpath(
                    "//div[@class='flex-1 text-darker text-xl text-medium d-flex align-items-center overflow-hidden']//a//@href").extract()
                for res in results:
                    url = 'https://so.toutiao.com' + res
                    meta = {
                        "url": url,
                        "name": self.name,
                        "platform": "toutiao",
                        "keyword": keyword,
                        "callback": "page_single_parse"
                    }
                    logging.info('search_url',url)
                    yield scrapy.Request(url=url, headers=headers, cookies=cookies, meta=meta, dont_filter=False)
        except Exception as e:
            logger.exception(f"E 头条检索{e}")
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
    toutiao = Toutiao()
    for a in toutiao.get_request_from_keyword(headers=headers, search_url=search_url, keyword="上海方舱：智能服务机器人多场景“上岗”"):
        print(a)
