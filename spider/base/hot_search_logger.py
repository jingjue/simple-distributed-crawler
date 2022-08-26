# -*-coding:utf-8-*- 、
# Team : upcedu.nlp
# Author：dongshou
# Date ：2021/9/22 下午4:06
# Describe ：定义热点时间爬取的元类

# 日志元类，用于类中的日志操作
from typing import Tuple
from base.logger import logger


def hot_search_logger(method):
    def inner(self, *args, **kwargs):
        ret = method(self, *args, **kwargs)
        logger.info(f'  【爬取关键词】平台：{self.name} 共爬取相关热搜表{len(ret)}')
        return ret

    return inner


def keyword_url_logger(method):
    def inner(self, *args, **kwargs):
        ret = method(self, *args, **kwargs)
        logger.info(f'  【关键词转换】平台：{self.name} {kwargs.get("keyword")}  相关URL共{len(ret[0])}条')
        return ret
    return inner


class meta_hotsearch(type):
    meta_name = 'meta_hot_search'

    def __new__(self, name: str, bases: Tuple[type], attrs: dict):
        attrs_copy = attrs.copy()
        for key, value in attrs.items():
            if key == 'hot_search':
                attrs_copy[key] = hot_search_logger(value)
            elif key == "get_request_by_keyword":
                attrs_copy[key] = keyword_url_logger(value)
        return type(name, bases, attrs_copy)


