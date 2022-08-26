# encoding: utf-8
'''
  @author: Suncy
  @contact: scyuige@163.com
  @team: UPC.nlp
  @file: tieba.py
  @time: 2021/10/18 10:03
  @desc:
'''
import json

from loguru import logger
from scrapy import Selector

from base.utils import get_uid_by_name
from base.utils.time import get_time, gen_id
from spiders.items import WeiboItem
from spiders.spiders import BaseSpider


class Tieba(BaseSpider):
    name = "贴吧"

    def __init__(self, one_project_name, **kwargs):
        super(Tieba, self).__init__(one_project_name, logger)

    def page_parse(self, response, **kwargs):
        try:
            '''百度贴吧每一个吧的楼层clss都不一样'''
            html = Selector(text=response.text)
            com_list = html.xpath("//div[contains(@class,'l_post')]")
            title = html.xpath("//div[contains(@class,'core_title_wrap_bright')]//text()").extract()
            index = title.index("只看楼主")
            title = title[:index]
            title = ''.join(i for i in title)
            title = self.try_get_title(response, title)
            for com in com_list:
                tieba_item = WeiboItem()
                tieba_item["platform"] = "贴吧"
                tieba_item["now_date"] = get_time()
                tieba_item['title'] = title

                account = com.xpath("./div[@class='d_author']//li[@class='d_name']//a//text()").get()
                tieba_item['account'] = account

                time = com.xpath(".//div[contains(@class,'core_reply_tail')]//text()").extract()
                if time:
                    tieba_item['date'] = time[-1]
                else:
                    time = json.loads(com.xpath("./@data-field").get())
                    if time['content']['date']:
                        time = time['content']['date']
                    else:
                        time = get_time()
                    tieba_item['date'] = time

                contents = com.xpath(
                    ".//div[contains(@class,'d_post_content') and contains(@class,'j_d_post_content')]//text()").extract()
                contents = str.strip(''.join(i for i in contents))
                tieba_item['content'] = contents

                tieba_item["weibo_id"] = get_uid_by_name(account + gen_id())
                tieba_item["mid"] = tieba_item["weibo_id"]
                tieba_item["uid"] = tieba_item["weibo_id"]
                yield tieba_item
                # print(tieba_item)
        except Exception as e:
            logger.exception(f"E 贴吧错误{e}")


if __name__ == '__main__':
    tieba = Tieba()
