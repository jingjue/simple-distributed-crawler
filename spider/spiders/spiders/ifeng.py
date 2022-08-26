"""
    @Author 王振琦
    @Splitter 王振琦
    @Date 2021/10/08 08:54
    @Describe 凤凰网
"""
import time

import requests
from loguru import logger

from base.utils import get_uid_by_name
from base.utils.text_preprocess import ifeng_extract_script
from base.utils.time import gen_id, get_date
from spiders.items import WeiboItem
from spiders.spiders import BaseSpider


class Ifeng(BaseSpider):
    name = "凤凰网"

    def __init__(self, one_project_name="default",**kwargs):
        super(Ifeng, self).__init__(one_project_name, logger)

    def parse_single_page(self, response, **kwargs):
        resp_data = ifeng_extract_script(response.text)
        doc_data = resp_data["docData"]
        account = doc_data["subscribe"]["catename"]
        title = doc_data["title"]
        content = ""
        content_org = doc_data["contentData"]["contentList"][0]["data"]
        if (str == type(content_org)):
            content = content_org.replace("<p>", "").replace("</p>", "")
        date = str(time.localtime(time.time()).tm_year) + "/" + str.split(doc_data["newsTime"], " ")[0]
        keyword = response.meta.get("keyword")
        if not content:
            return
        ifeng_item = WeiboItem()
        title = self.try_get_title(response, title)
        ifeng_item["account"] = account
        ifeng_item["uid"] = get_uid_by_name(account)
        ifeng_item["weibo_id"] = get_uid_by_name(title + str(gen_id()))
        ifeng_item["mid"] = get_uid_by_name(keyword)
        ifeng_item["content"] = content

        ifeng_item["title"] = title
        ifeng_item["date"] = date
        ifeng_item["now_date"] = get_date()
        ifeng_item["platform"] = "凤凰网"
        print(ifeng_item)
        return ifeng_item


if __name__ == '__main__':
    base_url = "https://ishare.ifeng.com/c/s/v002w--7x6jJkkKGunBumBzLtsnSYE--rJEG-_0Ukmf61g8uk4__"
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
    response = requests.get(url=base_url, headers=headers)
    ifeng.parse_single_page(response)
