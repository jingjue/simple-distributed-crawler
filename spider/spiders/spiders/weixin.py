from scrapy import Selector
from loguru import logger

from base.utils.time import get_time
from spiders.items import WeiboItem
from spiders.spiders import BaseSpider


class Weixin(BaseSpider):
    name = "微信"

    def __init__(self, one_project_name,**kwargs):
        super(Weixin, self).__init__(one_project_name, logger)

    def parse_page(self, response, **kwargs):
        try:
            weixin_item = WeiboItem()
            weixin_item['platform'] = "微信"
            weixin_item['now_date'] = get_time()
            html = Selector(text=response.text)
            account = html.xpath("//div[@id='meta_content']//a//text()").extract()
            if account:
                account = account[0].strip()
                weixin_item["account"] = account
            time = html.xpath("//div[@id='meta_content']//em//text()").extract()
            if time:
                pass
            context = html.xpath("//div[@class='rich_media_content ']//span//text()").extract()
            if context:
                context = ','.join(str(i) for i in context)
                weixin_item["content"] =  context
            weixin_item["title"] = self.try_get_title(response,None)
            yield weixin_item
        except Exception as e:
            logger.exception(f"E 微信检索{e}")
            yield None


if __name__ == '__main__':
    weixin = Weixin()
    print(weixin.hot_search())
    # keyword="孟晚舟"
    # weixin.get_request_from_keyword(keyword)

    # response=requests.get("https://mp.weixin.qq.com/s?src=11&timestamp=1633698062&ver=3362&signature=RQZKHalkPU7sz-J1BGe0ei1PuHh5u2IVENQSbfDCfR2peB4gObtBvJHrjgwK995qVQuBTdEaBGQkJjzkCwwcs5YaBk6OOdhojS1dZ9meZ1skTnwh7gPTLx-txnTaULp5&new=1",headers=weixin.headers, params=weixin.params, cookies=weixin.cookies,timeout=10)
    # html=Selector(text=response.text)
    # account=html.xpath("//div[@id='meta_content']//a//text()").extract()[0]
    # account=account.strip()
    # time=html.xpath("//div[@id='meta_content']//em//text()").extract()
    # context=html.xpath("//div[@class='rich_media_content ']//span//text()").extract()
    # context=','.join(str(i) for i in context)
    # print(account,time,context)
