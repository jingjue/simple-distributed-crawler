from loguru import logger
from spiders.items import WeiboItem

from spiders.spiders import BaseSpider


class Zhihu(BaseSpider):
    name = "知乎"

    def __init__(self, one_project_name="default", **kwargs):
        super(Zhihu, self).__init__(one_project_name, logger)

    def page_parse(self, response, **kwargs):
        yield None
