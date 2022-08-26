# coding=utf-8
import json
import os.path
import pathlib
from string import Template

from monitor import *

# 每个爬虫都有获取热点 根据热点查链接 再解析链接这三步，
# 把每个爬虫的这三步都拆开来
# 百度爬虫爬取的是资讯，资讯进不去
# 豆瓣网的主旋律标签失效
# 复兴网url失效
# 环球网无search
# 人民网搜索链接404
# 人民日报无搜索

abs_path = pathlib.Path(__file__).parent.absolute()


class SignalHeadManger(type):
    """
    单例模式，未加锁部分并发执行,加锁部分串行执行,速度降低,保证了数据安全
    """
    _instance_lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            with SignalHeadManger._instance_lock:
                if not hasattr(cls, "_instance"):
                    cls._instance = super(SignalHeadManger, cls).__call__(*args, **kwargs)
        return cls._instance


class HeadManager(metaclass=SignalHeadManger):
    def __init__(self):
        self.filename = os.path.join(abs_path, '..', 'conf', 'header_info.json')
        self.header_dict = self.read_json()

    def read_json(self):
        with open(self.filename, encoding="utf-8") as f:
            header_dict = json.load(f)
        return header_dict

    def update_headers(self, platform, key, value):
        """
        :param type: header,hot_url,hot_info
        """
        try:
            self.header_dict[platform][key] = value
            with open(self.filename, 'w') as f:
                json.dump(self.header_dict, f)
            logger.info(f"{platform} {key} 请求头更新成功")
            return True
        except Exception as e:
            logger.error(f"{platform} {key} 请求头更新失败")
            return False

    def get_head(self, platform):
        if platform == "微博用户":
            platform = "微博"
        return self.header_dict[platform]['header']

    def get_hot_url(self, platform):
        return self.header_dict[platform]['hot_url']

    def get_content_url(self, platform):
        """
        获取内容页url
        :return:
        """
        url = self.header_dict[platform].get("content_url", False)
        if url:
            return Template(url)
        else:
            logger.warning(f"{platform} 不存在内容url")
            return None

    def get_search_url(self, platform):
        search_url = self.header_dict[platform].get("search_url", False)
        if search_url:
            return Template(search_url)
        else:
            logger.warning(f"{platform} 不存在检索url")
            return None

    def get_user_url(self, platform):
        user_url = self.header_dict[platform].get("user_url", False)
        if user_url:
            return Template(user_url)
        else:
            logger.warning(f"{platform} 不存在用户url")
            return None

    def get_universal_url(self, key, platform) -> Template:
        """
        获取指定的url,
        :param key: like，repost,comment
        :param platform:
        :return:
        """
        url = self.header_dict[platform].get(key + "_url", False)
        if url:
            return Template(url)
        else:
            logger.warning(f"{platform} 不存在用户 {key} url")
            return None

    def fill_url(self, key, platform, **kwargs):
        url = self.get_universal_url(key, platform)
        if url:
            return url.substitute(**kwargs)
        else:
            logger.error(f"{platform}平台")
            return None


if __name__ == '__main__':
    h = HeadManager()
