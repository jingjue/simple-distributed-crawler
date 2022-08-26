from string import Template
from urllib import parse

import scrapy

from monitor import logger


class Zhihu:
    name = "知乎"

    def __init__(self):
        pass

    def get_request_from_keyword(self, headers, search_url, keyword, *args, **kwargs):
        try:
            yield None
        except Exception as e:
            logger.exception(f"E 知乎{e}")
            yield None