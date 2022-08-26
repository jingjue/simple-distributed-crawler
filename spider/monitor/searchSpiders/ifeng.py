"""
    @Author 王振琦
    @Splitter 王振琦
    @Date 2021/10/17 09:39
    @Describe 人民日报
"""

import json
import time

import requests
import scrapy

from monitor import logger


class Ifeng:
    name = "凤凰网"

    def __init__(self):
        pass

    def get_request_from_keyword(self, headers, search_url, keyword, *args, **kwargs):
        try:
            query_time = int(round(time.time() * 1000))
            # 过滤掉视频新闻，仅获取只包含图片的新闻
            query_url = search_url.substitute(keyword=keyword, page=1) + str(query_time)
            query_response = requests.get(query_url, headers=headers)  # 通过URL获取响应
            # 删除掉响应中多余的字符'getSoFengDataCallback('和')'并转换为JSON
            jsonObj = json.loads(query_response.text.replace("getSoFengDataCallback(", "").replace(")", ""))
            total = jsonObj["data"]["total"]
            if total > 0:
                page_total = jsonObj["data"]["totalPage"]  # 获取该关键词相关数据的页数
                # 分页查询数据
                for i in range(1, page_total + 1):
                    url =  search_url.substitute(keyword=keyword, page=i) + str(query_time)
                    response = requests.get(url)
                    jsonObj = json.loads(response.text.replace("getSoFengDataCallback(", "").replace(")", ""))
                    # 开始解析JSON
                    for item in jsonObj["data"]["items"]:
                        item["title"].replace("<em>", "").replace("</em>", "")  # 删除title文字中的<em></em>标签
                        item_url = item["url"]
                        new_url = "https:" + item_url  # 把链接补全
                        meta = {
                            "platform": "凤凰网",
                            "keyword": keyword,
                            "callback": 'parse_single_page',
                            "ifeng_id": '0',
                            "father": '0'
                        }
                        yield scrapy.Request(new_url, meta=meta)
        except Exception as e:
            logger.exception(f"E 凤凰网检索{e}")
            yield None


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
    for a in ifeng.get_request_from_keyword(headers, military_url, "陕西暴雨"):
        print(a)
