# Name:         weibo
# Description:  微博检索爬虫
# Author:       东寿
# Date:         2022/4/7
# Version:      0.1
import sys
sys.path.append("/home/spiders")
from monitor.setting import SEARCHPAGE
from monitor import logger
from scrapy import Selector
import scrapy
import requests
from string import Template
from urllib import parse
import sys
sys.path.append("/home/spiders")


# class WeiboBak:
#     name = "微博"

#     def __init__(self):
#         pass

#     def get_request_from_keyword(self, headers, search_url, keyword, *args, **kwargs):
#         """
#         根据关键词获取检索结果
#         :param headers:
#         :param cookie:
#         :param search_url:
#         :param keyword:
#         :param kwargs:
#         :return:
#         """
#         try:
#             for page in range(SEARCHPAGE):
#                 kwargs['page'] = page
#                 kwargs['keyword'] = parse.quote(keyword)
#                 search_url_ = search_url.substitute(**kwargs)
#                 response = requests.get(search_url_, headers=headers, timeout=10)
#                 if response.status_code == 200:
#                     news = response.json().get("data", False)
#                     if not news:
#                         logger.info(f"{keyword}检索结果为空,{response.text}")
#                         yield response.text
#                         continue
#                     news = news["cards"]
#                     meta = {"keyword": keyword, "callback": "parse_signal_page"}
#                     for result in news:
#                         try:
#                             if result["card_type"] == 11:
#                                 result = result["card_group"][0]
#                             if result["card_type"] != 9:
#                                 continue
#                             uid = result["mblog"]["user"]["id"]
#                             weibo_id = result["mblog"]["mblogid"]
#                             surl = args[0].substitute(weibo_id=weibo_id)
#                             meta["uid"] = uid
#                             meta["weibo_id"] = weibo_id
#                             meta["father"] = 0
#                             yield scrapy.Request(surl, headers=headers, meta=meta)
#                         except Exception as e:
#                             logger.error(f"E 微博检索 解析出错{e},{result['card_type']}")
#                 else:
#                     logger.error(f"E 微博检索 {keyword} {response.status_code} {search_url_}")
#                     yield response.text
#         except Exception as e:
#             logger.exception(f"E 微博检索{e}")
#             yield None


class Weibo:
    name = "微博"

    def __init__(self):
        pass

    def get_request_from_keyword(self, headers, search_url, keyword, *args, **kwargs):
        """
           根据关键词获取检索结果
           :param headers:
           :param cookie:
           :param search_url:
           :param keyword:
           :param kwargs:
           :return:
        """
        index = 0
        for page in range(SEARCHPAGE):
            kwargs['page'] = page+1
            kwargs['keyword'] = parse.quote(keyword)
            search_url_ = search_url.substitute(**kwargs)
            # search_url_ = f"https://s.weibo.com/weibo?q={parse.quote(keyword)}&page={page+1}"
            response = requests.get(search_url_, headers=headers, timeout=10)
            try:
                if response.status_code != 200:
                    yield response.text
                resp = Selector(response)
                from_hrefs = resp.xpath('//p[@class="from"]/a[1]/@href')
                meta = {"keyword": keyword, "callback": "parse_signal_page"}
                if len(from_hrefs)==0:
                    yield response.text
                for href in from_hrefs:
                    info = href.get().strip()[1:].split("/")
                    meta["weibo_id"] = info[3][0:9]
                    meta["uid"] = info[2]
                    meta["father"] = 0
                    surl = args[0].substitute(weibo_id=meta["weibo_id"])
                    yield scrapy.Request(surl, headers=headers, meta=meta)
                    index += 1
            except Exception as e:
                logger.error(f"E 微博检索{e} {keyword} {response.status_code} {search_url_}")
                yield response.text
        print("inner: ",index) 


if __name__ == '__main__':
    headers = {
        "authority": "rm.api.weibo.com",
        "method": "GET",
        "path": "/2/remind/push_count.json?trim_null=1&with_dm_group=1&with_reminding=1&with_settings=1&exclude_attitude=1&with_chat_group_notice=1&source=2936099636&with_chat_group=1&with_dm_unread=1&callback=__jp3",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9",
        "cookie": "SINAGLOBAL=8115020293746.391.1618406050268; UOR=,,www.baidu.com; SCF=AnWUJToMzNT-9SrDk496VP7ajl-dlV2iHUODDHPbNPc3fKrIwIlU_V8j9h2ZBb9GN3-7I4CnO3sF8j67yXzT6pM.; XSRF-TOKEN=OwQ5HHzEjZS_fITP0o3fAnZW; PC_TOKEN=966157a33d; login_sid_t=6fc87ffae559edcec22ca00a43ea3c6d; cross_origin_proto=SSL; WBStorage=4d96c54e|undefined; _s_tentry=weibo.com; Apache=684634581477.6411.1659936189751; ULV=1659936189761:40:1:1:684634581477.6411.1659936189751:1658804659104; wb_view_log=1536*8641.25; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9Wh7KBKaeHAZnm-HHBzVH5H-5JpX5o275NHD95QNS05NS0nc1hzNWs4Dqcjqi--fiKnci-8hi--fiKnfi-i2P0ecShnf; SSOLoginState=1659936218; SUB=_2A25P9O2KDeRhGeFJ61UW-CjEyTuIHXVsgFhCrDV8PUNbmtANLUjwkW9NfLnItkLjrGPMOMCUhatHnKTPmr0q31Oh; ALF=1691472217; WBPSESS=Dt2hbAUaXfkVprjyrAZT_HaxuVWJ0u8PBhgtsyug_WSPoRGm6Bqjfmyt_eDFipEqroWBCRhtyIG2dpOm7c3uSJFpD8dauB77LTuWjtUFpwggvzvoegLJZs8aYif3LUrHnU9wGvuFsasDT_FPrgJZNcu8xYUT-BDilR1vfrj_BgzmVhYvTSjfowbjh_DwnLeGV4zGK45ZrsBN1qPEqg4XMg==",
        "referer": "https://s.weibo.com/",
        "sec-ch-ua": "'.Not/A)Brand';v='99', 'Google Chrome';v='103', 'Chromium';v='103'",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "script",
        "sec-fetch-mode": "no-cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
    }
    search_url = Template("https://s.weibo.com/weibo?q=$keyword&page=$page")
    keywords = "新版新冠防控方案发布"
    content_url = Template("https://weibo.com/ajax/statuses/show?id=$weibo_id")
    crawl_time = {'start': '2019-01-01 23:23', 'end': '2022-04-13 21:02:58'}

    w = Weibo()
    i = 0
    for r in w.get_request_from_keyword(headers, search_url, keywords, content_url, **crawl_time):
        i += 1
        print(i,r)
