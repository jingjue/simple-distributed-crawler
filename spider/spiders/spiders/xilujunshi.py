# -*-coding:utf-8-*- 、
# Team : upcedu.nlp
# Author：dongshou
# Splitter: 王振琦
# Date ：2021/10/15 下午4:01
# Describe ：西陆军事

import requests
from scrapy import Selector

from base.utils import get_uid_by_name
from base.utils.time import get_date, gen_id
from loguru import logger
from spiders.items import WeiboItem
from spiders.spiders import BaseSpider


class XiLu(BaseSpider):
    name = "西陆军事"

    def __init__(self, one_project_name="default",**kwargs):
        super(XiLu, self).__init__(one_project_name, logger)

    def parse_single_page(self, response, **kwargs):
        try:
            # url = response.meta.get("url")
            url = "http://junshi.xilu.com/20211014/1000010001187554.html"
            url_header = "/".join(url.split("/")[0:-1])
            resp = Selector(text=response.text)
            tiexue = WeiboItem()
            title = resp.xpath("//div[@class='wap_vip']/h1/span/text()").get()
            # title = self.try_get_title(response,title)
            account = resp.xpath("//div[@class='name-x left']/text()").get()
            if not account:
                tiexue["account"] = "西陆军事"
            else:
                tiexue["account"] = account
            tiexue["weibo_id"] = get_uid_by_name(title + str(gen_id()))
            tiexue["mid"] = tiexue["weibo_id"]
            tiexue["uid"] = get_uid_by_name(tiexue["account"])

            # 内容存在翻页的情况
            content = ''
            for p in resp.xpath('//div[@class="contain_detail_cnt f18"]/p'):
                result = p.xpath("./text()").get()
                if result:
                    content += result.strip().replace("\n", "")
            urls = resp.xpath('//div[@class="pagination f14"]/a')
            for item in urls:
                next_url = url_header + "/" + item.xpath("./@href").get()
                num = item.xpath("string(.)").get()
                if num == "下一页" or num == '1':
                    continue
                next_content = self.parse_content(next_url, headers=headers)
                if next_content:
                    content += next_content

            tiexue["content"] = content
            tiexue["title"] = title
            tiexue["date"] = resp.xpath('/html/body/div[2]/div/div[1]/div[1]/div/div/div[4]/div[3]').get()
            tiexue["now_date"] = get_date()
            tiexue["platform"] = "西陆军事"
            return tiexue
        except Exception as e:
            logger.exception(f"【西陆军事】具体内容解析出错 {e}")
            return

    def parse_content(self, url, headers):
        response = requests.get(url, headers=headers)
        try:
            resp = Selector(response)
            results = resp.xpath('//div[@class="contain_detail_cnt f18"]/p')
            content = ''
            for p in results:
                result = p.xpath("./text()").get()
                if result:
                    content += result.strip()
            return content.replace("\r\n", "").replace("\xa0", "")
        except Exception as e:
            logger.exception(f"【西陆军事】内容中的下一页解析出错 {e}")
            return


if __name__ == '__main__':
    url = "http://www.xilu.com/20220512/1000010001208091.html"
    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Referer': 'https://www.baidu.com/link?url=ImagoC3DE1p0D55S7qbzXrjJ3sGeO3nC9BwzL8q75Wtil8_pJOWqeNA2dRgp8r3n&wd=&eqid=f4b4737e0001ccbe0000000361693525',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    xilu = XiLu()
    response = requests.get(url)
    a = xilu.parse_single_page(response)
    print(a)
