# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
import logging
import os
import threading

from scrapy import Request
from scrapy.utils.reqser import request_from_dict
from scrapy_redis import picklecompat
from scrapy.utils.request import request_fingerprint

from base.db.mysql import Mysql
from base.db.redis_ import Redis
from core.spiders import RedisSpider
from monitor import convert_to_pinyin, to_unicode
from monitor.cookieManager import CookieManager
from monitor.headerManager import HeadManager
from monitor.setting import REDIS_REQUEST,REDIS_DUPLICATION

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class SignalSlot(type):
    """
    单例模式，未加锁部分并发执行,加锁部分串行执行,速度降低,保证了数据安全
    对数据库进行封装，确保单例
    """
    _instance_lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            with SignalSlot._instance_lock:
                if not hasattr(cls, "_instance"):
                    cls._instance = super(SignalSlot, cls).__call__(*args, **kwargs)
        return cls._instance


class SSlot(metaclass=SignalSlot):
    def __init__(self, mysql: Mysql = None, redis: Redis = None, neo4j=None):
        """
        :param kwargs:
        """
        self.mysql = mysql
        self.redis = redis
        self.neo4j = neo4j


class BaseSpider(RedisSpider):
    name = None
    redis_key = None
    redis_batch_size = 2

    def __init__(self, one_project_name=None, logger=None, **kwargs):
        self.platform = self.name

        logger.remove(handler_id=None)
        logger.add(f"{root}\log\{one_project_name}\{self.name}.log", encoding="utf-8")
        self.logger_ = logger

        self.project_name = one_project_name
        self.name = convert_to_pinyin(f"{self.name}")  # 改变redis中key的位置
        super(BaseSpider, self).__init__()
        self._header_manager = HeadManager()
        self.dbslot = SSlot(mysql=Mysql(logger), redis=Redis())
        self.cookie_manager = CookieManager(self.project_name, dbslot=self.dbslot)
        self.cookie = None
        self.generate_redis_key()

    def generate_redis_key(self):
        """
        重新构造redis_key
        :return:
        """
        self.redis_key = convert_to_pinyin(
            REDIS_REQUEST.substitute(project_name=self.project_name, platform=self.platform))

    @property
    def headers(self):
        headers = self._header_manager.get_head(self.platform)
        cookie = self.cookie_manager.refresh_cookie(self.platform)
        if cookie:
            headers["cookie"] = cookie["cookie"]
            self.cookie = cookie
        return headers

    def check_cookie(self, response_text):
        self.cookie_manager.check_cookie(self.cookie, self.platform, response_text)

    def encoder_request(self, request):
        """
        对request进行编码，以便分布式爬虫从redis中加载
        :param request:
        :return:
        """
        cb = request.meta["callback"]
        eb = request.meta.get("errorback", None)
        d = {
            'url': to_unicode(request.url),  # urls should be safe (safe_string_url)
            'callback': cb,
            'errback': eb,
            'method': request.method,
            'headers': dict(request.headers),
            'body': request.body,
            'cookies': request.cookies,
            'meta': request.meta,
            '_encoding': request._encoding,
            'priority': request.priority,
            'dont_filter': request.dont_filter,
            'flags': request.flags,
            'cb_kwargs': request.cb_kwargs,
        }
        if type(request) is not Request:
            d['_class'] = request.__module__ + '.' + request.__class__.__name__
        return d

    def make_request_from_data(self, encoded_request):
        obj = picklecompat.loads(encoded_request)
        print("make_request_from_data:",obj)
        return request_from_dict(obj, self)

    def enqueue_user(self, request, platform="微博用户"):
        """
        将用户id保存到redis中，以供用户爬虫
        :param uid:
        :return:
        """
        redis_key_dup = convert_to_pinyin(REDIS_DUPLICATION.substitute({"project_name": self.project_name, "platform": platform}))
        if not self.request_seen(request,redis_key_dup):
            redis_key = REDIS_REQUEST.substitute(project_name=self.project_name, platform=platform)
            redis_key = convert_to_pinyin(redis_key)
            request_dict = picklecompat.dumps(self.encoder_request(request))
            self.dbslot.redis.insert(redis_key, request_dict)
    
    def request_seen(self, request, redis_key_dup):
        """
        判断request是否存在
        :param request:
        :param redis_key_dup:保存fp的rediskey
        :return:
        """
        fp = request_fingerprint(request)
        return self.dbslot.redis.sadd(redis_key_dup, fp) == 0

    def enqueue_content(self, request):
        """
        将用户id保存到redis中，以供用户爬虫
        :param uid:
        :return:
        """
        redis_key = REDIS_REQUEST.substitute(project_name=self.project_name, platform=self.platform)
        redis_key = convert_to_pinyin(redis_key)
        request_dict = picklecompat.dumps(self.encoder_request(request))
        self.dbslot.redis.insert(redis_key, request_dict)

    def try_get_title(self, response, title):
        """
        尝试获取title,使用系统传递过来的title当成title
        :param response:
        :param title：默认title
        :return:
        """
        return response.meta.get("title", title)

    def refresh_cookie(self, *args,**kwargs):
        return self.cookie_manager.refresh_cookie(self.platform)


if __name__ == '__main__':
    # refresh_cookie()
    print(root)
