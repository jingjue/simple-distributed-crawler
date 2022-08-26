"""
包含热点爬虫管理，爬虫管理，检索爬虫管理
涉及到多线程，应当保证数据库连接安全
"""
import importlib
import inspect
import os
from collections import defaultdict
from typing import Union, List
import sys
sys.path.append("/home/spiders")

import requests
import scrapy
from requests import Request
from scrapy.utils.request import request_fingerprint
from scrapy_redis import picklecompat
from scrapyd_api import ScrapydAPI

from base.db.dbSlot import Slot
from conf.default import Default_Project_Path
from monitor import root, to_unicode, convert_to_pinyin
from monitor.cookieManager import CookieManager
from monitor.headerManager import HeadManager
from monitor.setting import REDIS_REQUEST, REDIS_KEYWORD, REDIS_DUPLICATION
from monitor.shell import SSH, scp
from monitor.titleManager import TitleManager
from monitor import logger


class HotSpiderManager:
    def __init__(self, platforms: list, dbslot: Slot):
        self.platforms = platforms
        self.all_hot_spider = self.register_hot_spider()
        self._head_manager = HeadManager()
        self._dbslot = dbslot
        self._title_manager = TitleManager()
        self._cookie_manager = CookieManager(None, self._dbslot)

    def crawl_hot(self):
        """
        以多线程启动该函数
        """
        self._title_manager.wipe_data()  # 清空关键词数据，防止重复
        for platform in self.platforms():
            spider = self.all_hot_spider[platform]
            headers = self._head_manager.get_head(platform)
            hot_url = self._head_manager.get_hot_url(platform)
            cookie = self._cookie_manager.refresh_cookie(platform)
            if cookie:
                headers['Cookie'] = cookie["cookie"]
            status, title = spider.get_title(headers, hot_url)
            if status:
                self._title_manager[platform] += title
            else:
                if title:
                    self._cookie_manager.check_cookie(cookie, platform, title)

        self.save_titles_to_redis()

    def register_hot_spider(self) -> dict:
        """
        注册热点爬虫
        """
        hot_spider_dir = os.path.join(root, 'monitor', "hotSpiders")
        hot_spiders = {}
        for file in os.listdir(hot_spider_dir):
            if "__init__" in file or not file.endswith('.py'):
                continue
            x = importlib.import_module(f"monitor.hotSpiders.{file.split('.')[0]}")
            for name, cls in inspect.getmembers(x, inspect.isclass):
                if getattr(cls, "name", False):
                    hot_spiders[cls.name] = cls()
        return hot_spiders

    def save_titles_to_redis(self):
        self._title_manager.persist(self._dbslot)


class SearchSpidersManager:
    """
    检索爬虫，在相应的爬虫网站上进行检索，并将url保存到不同爬虫项目的redis数据库中
    """

    def __init__(self, dbslot: Slot):
        super(SearchSpidersManager, self).__init__()
        self.spiders = self.register_search_spiders()
        self.dbslot = dbslot

        self._head_manager = HeadManager()
        self._title_manager = TitleManager()
        self._cookie_manager = CookieManager(None, self.dbslot)
        self._serializer = picklecompat

    def register_search_spiders(self):
        """
        注册检索爬虫
        return : {platform:search_spider_instance}
        """
        search_spider_dir = os.path.join(root, 'monitor', "searchSpiders")
        search_spiders = {}
        for file in os.listdir(search_spider_dir):
            if "__init__" in file or not file.endswith('.py'):
                continue
            x = importlib.import_module(f"monitor.searchSpiders.{file.split('.')[0]}")
            for name, cls in inspect.getmembers(x, inspect.isclass):
                if getattr(cls, "name", False):
                    search_spiders[cls.name] = cls()
        return search_spiders

    def crawl_by_keyword(self, project_names, project_times, platforms, crawl_time, keyword):
        """
        根据关键词检索，并将检索结果保存到相应项目的爬虫数据库中
        project_names:该关键词属于哪些爬虫项目
        projects_times:这些爬虫项目对时间的要求
        platforms:应当使用哪些平台去检索关键词
        crawl_time:全部爬虫项目的合并时间
        """
        for platform in platforms:
            self.crawl_by_keyword_signal_platform(project_names, platform, keyword, crawl_time, project_times)
            # 从对应的redis数据库中删除keyword
            redis_key = REDIS_KEYWORD.substitute(platform=platform)
            self.dbslot.redis.srem(redis_key, keyword)
            # try:
            #     logger.info(f"热点爬虫 {platform} 删除关键词 {keyword}")
            # except:
            #     # 日志文件在切分时候，loguru在多线程的情况下会报错，因此暂停1秒，等待文件切分结束
            #     # 好像bug不是这个原因
            #     # 详细情况见 https://www.cnblogs.com/davytitan/p/15846193.html
            #     logger.error(f"loguru 切分报错，热点爬虫 {platform} 删除关键词 {keyword}")

    def request_seen(self, request, redis_key_dup):
        """
        判断request是否存在
        :param request:
        :param redis_key_dup:保存fp的rediskey
        :return:
        """
        fp = request_fingerprint(request)
        return self.dbslot.redis.sadd(redis_key_dup, fp) == 0

    def crawl_by_keyword_signal_platform(self, project_names, platform, keyword, crawl_time, project_times):
        """
        判断检索的结果是否符合爬虫项目的要求，如果符合，则保存到对应的redis数据库中
        """
        title = None
        if "_" in keyword:
            title = keyword.split("_")[0]
            keyword_only = keyword.split("_")[1]
        else:
            keyword_only = keyword
        requests = self.get_request_from_keyword(platform, keyword_only, **crawl_time.to_dict())
        for project_name in project_names:
            redis_key = convert_to_pinyin(REDIS_REQUEST.substitute({"project_name": project_name, "platform": platform}))
            redis_key_dup = convert_to_pinyin(REDIS_DUPLICATION.substitute({"project_name": project_name, "platform": platform}))
            requeset_num = 0
            for request_instance in requests:
                if isinstance(request_instance, scrapy.Request):
                    request = self.encoder_request(request_instance)
                    date = request["meta"].get("date", False)
                    if title:
                        request["meta"]["title"] = title
                    if date and date not in project_times[project_names]:
                        continue
                    request["meta"]["project_name"] = project_name
                    serializer_request = self._serializer.dumps(request)
                    # 添加request去重机制，基于request_fingerprint
                    if not self.request_seen(request_instance, redis_key_dup):
                        self.dbslot.redis.insert(redis_key, serializer_request)
                        requeset_num += 1
            logger.info(f"{platform}  关键词：{keyword} 共检索到 {requeset_num}条 有效request")

    def encoder_request(self, request):
        """
        对request进行编码，以便分布式爬虫从redis中加载
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

    def get_request_from_keyword(self, platform, keyword, **kwargs) -> list:
        """
        从相应的平台上进行检索，获取url，并将url保存到相应的redis爬虫项目的request中
        打算采用协程或者线程的方法进行
        kwargs:用来表示高级检索的信息，即开始时间和结束时间
        search_url:必为高级检索url,里面包含的信息有<<<开始时间，结束时间，下一页，关键词>>>,统一采用string.Template的模板。
        """
        search_url = self._head_manager.get_search_url(platform)
        content_url = self._head_manager.get_content_url(platform)
        if not search_url:
            return []
        headers = self._head_manager.get_head(platform)
        cookie = self._cookie_manager.refresh_cookie(platform)
        if cookie:
            headers["cookie"] = cookie["cookie"]
        requests = []
        for request in self.spiders[platform].get_request_from_keyword(headers, search_url, keyword, content_url,**kwargs):
            if isinstance(request, scrapy.Request):
                if not request.meta.get("callback", False):
                    logger.warning(f"{platform} request callback is None")
                else:
                    requests.append(request)
            elif isinstance(request, str):
                self._cookie_manager.check_cookie(cookie, platform, request)
            # print(request)
            cookie = self._cookie_manager.refresh_cookie(platform)
            if cookie:
                headers["cookie"] = cookie["cookie"]
        return requests


class SpiderManager:
    def __init__(self, project_name, spiders: dict = {}):
        self.project_name = project_name
        self.spiders = spiders  # 存在哪些爬虫,key:value,key标识爬虫，value标识爬虫的启用状态,保存到redis中动态更新
        self._spider_job_id = defaultdict(dict)
        self.spider_info = defaultdict(dict)

    def create_project_in_device(self, device):
        """
        创建爬虫项目
        :param device:
        :return:
        """
        # 将项目scp到远程
        # scr_server = {
        #     "source": Default_Project_Path,
        #     "target": device["address"],
        #     "password": device["password"],
        #     "username": device["username"],
        #     "ip": device["ip"]
        # }
        # scp(scr_server, logger)  默认已经开启docker服务
        return self.start_scrapyd_in_device(device)

    def start_scrapyd_in_device(self, device):
        """
        在远程device上启动scrapyd
        :param device:
        :return:
        """
        ssh = SSH(host=device["ip"], port=22, username=device["username"], password=device["password"])
        stauts, msg = ssh.connect()
        if not stauts:
            # 项目创建失败
            return None
        logger.info(f"部署项目,{device['ip']}:{device['port']} {self.project_name}")
        return {"msg": "项目部署成功",
                "result": ssh.send_command(
                    f"docker exec -it spider_{device['port']} bash -c 'cd /app && scrapyd-deploy -p {self.project_name}'")}
        # ssh.send_command(f"cd {device['address']} && nohup scrapyd & ")
        # return {"msg": "scrapyd启动成功",
        #         "result": ssh.send_command(f"cd {device['address']} && scrapyd-deploy  -p {self.project_name}")}

    def add(self, platform: Union[List[str], str]):
        """
        如果添加成功，则返回False,否则返回报错信息
        这个模式写的乱七八糟的，直接传过来一个list不行吗？画蛇添足，不想改了，能跑就行，还有一些其它的类似这种错误
        """
        errors = defaultdict(dict)
        if isinstance(platform, str):
            if platform not in self.spiders:
                error = getattr(self, "start_one_spider")(platform)  # 启动爬虫，返回爬虫的启动状态
                for ip, status in error.items():
                    if status:
                        errors[platform][ip] = status
                    else:
                        self.spiders[platform] = True
            else:
                # 当爬虫已经在配置文件中，但在scrapyd中不存在时，会使返回的爬虫为空，需要检查爬虫的状态，判断是否需要重新启动
                errors[platform] = f"爬虫项目{self.project_name}中，爬虫{platform} 已经存在"
            return errors
        elif isinstance(platform, list):
            for spider in platform:
                errors.update(self.add(spider))
            return errors

    def set_spider_status(self, spider_status):
        """
        添加一个属性 爬虫状态
        用来保存爬虫的运行状态 ,爬虫的运行状态有padding,running,finished
        :param spider_status:
        :return:
        """
        self._spider_status = spider_status

    def add_func(self, name, func):
        """
        添加所有爬虫的运行状态
        :param name:
        :param func:
        :return:
        """
        setattr(self, name, func)

    def get_all_content_spdier(self):
        """
        获取所有的内容爬虫
        """
        content_spider_dir = os.path.join(root, 'spiders', "spiders")
        content_spiders = []
        for file in os.listdir(content_spider_dir):
            if "__init__" in file or not file.endswith('.py'):
                continue
            x = importlib.import_module(f"spiders.spiders.{file.split('.')[0]}")
            for name, cls in inspect.getmembers(x, inspect.isclass):
                if getattr(cls, "name", False):
                    content_spiders.append(cls.name)
        return content_spiders

    def update_spider_status(self, device):
        """
        获取一个设备下整个项目下的内容爬虫的运行状态
        """
        try:

            scrapyd = ScrapydAPI(f"http://{device['ip']}:{device['port']}")
            server_id = f"{device['ip']}:{device['port']}"

            spider_status = scrapyd.list_jobs(self.project_name)
            if spider_status:
                self._spider_status = defaultdict(dict)
                for status in ["finished", "pending", "running"]:
                    for info in spider_status[status]:
                        info_ = {"start_time": info.get("start_time", "None")[:19], "status": status,
                                 "job_id": info["id"]}
                        self._spider_status[server_id][info["spider"]] = info_
                        if info["spider"] in self.spiders:
                            self._spider_job_id[server_id][info["spider"]] = info["id"]
                if not self._spider_status[server_id]:
                    self._spider_status[server_id] = {}

            else:
                return {"status": "error", "msg": "获取爬虫状态失败"}
        except requests.exceptions.ConnectionError:
            # 设备连接失败
            logger.warning(f"连接设备失败：{device['ip']} {device['port']}")
            self._spider_status = defaultdict(dict)
            return "device", {"device": device}
        except Exception as e:
            logger.error(f"{device['ip']} {device['port']} 项目名称{self.project_name} 或爬虫名称 错误或scrapyd 没有启动 {e}")
            self._spider_status = defaultdict(dict)
            return "spider", {"spider": f"{device['ip']} {device['port']}项目名称或爬虫名称错误,或scrapyd 没有启动 {e}"}

    def stop(self, device, platform):
        """
        停止某个爬虫
        通过scrapyd 实现停止某个爬虫,并查看爬虫状态，如果停止失败则返回报错信息
        爬虫停止成功，则返回False,否则返回报错信息
        :param device:
        :param platform:
        """
        scrapyd = ScrapydAPI(f"http://{device['ip']}:{device['port']}")
        try:
            server_id = f"{device['ip']}:{device['port']}"
            scrapyd.cancel(self.project_name, self._spider_job_id[server_id][platform])
            logger.info(f"分布式设备{device['ip']} {device['port']} 中爬虫{platform}停止成功")
            self._spider_job_id[server_id].pop(platform)
            return False, None
        except KeyError as ke:
            logger.warning(f"KeyError {ke} {device['ip']} {device['port']} {platform} 可能没启动")
            return "keyerror", f"KeyError {ke} {device['ip']} {device['port']} {platform} 可能没启动"
        except requests.exceptions.ConnectionError:
            # 设备连接失败
            logger.warning(f"连接设备失败：{device['ip']} {device['port']}")
            return "device", {"device": device}
        except Exception as e:
            logger.warning(f"{device['ip']} {device['port']} 项目名称{self.project_name} 或爬虫名称{platform}错误 {e}")
            return "spider", {"spider": f"{device['ip']} {device['port']} 项目名称或爬虫名称错误 {e}"}

    def get_valid_platform(self):
        """
        获取开启的爬虫平台
        """
        platforms = set()
        for platform, status in self.spiders.items():
            if status:
                platforms.add(platform)
        return platforms

    def del_spider(self, device, platform: Union[List[str], str]):
        """
        删除一个爬虫
        :param device:
        :param platform:
        :return:
        """
        errors = {}
        device_error = True
        if isinstance(platform, str):
            if platform and platform in self.spiders:
                status, error = self.stop(device, platform)
                if not error or status == "keyerror":
                    logger.info(f"分布式设备{device['ip']} {device['port']}中爬虫{platform}删除成功")
                    self.spiders.pop(platform)
                    # self._spider_status[device["ip"]].pop(platform)
                else:
                    errors[platform] = error
                    if status == "device":
                        device_error = False
            else:
                errors[platform] = f"爬虫项目{self.project_name}中，爬虫{platform} 不存在"
                device_error = False
            return errors, device_error
        elif isinstance(platform, list):
            for item in platform:
                errors, device_error = self.del_spider(device, item)
            return errors, device_error

    def get_device_projects(self, device):
        """
        获取爬虫平台上的所有项目名称
        :param device:
        :return:
        """
        try:
            scrapyd = ScrapydAPI(f"http://{device['ip']}:{device['port']}")
            projects = scrapyd.list_projects()
            return False, projects
        except requests.exceptions.ConnectionError:
            # 设备连接失败
            logger.warning(f"连接设备失败：{device['ip']} {device['port']}")
            return "device", {"status": "error", "msg": "连接设备失败"}
        except Exception as e:
            logger.warning(f"{device['ip']} {device['port']}项目名称{self.project_name} 或爬虫名称错误 {e}")
            return "spider", {"spider": f"{device['ip']} {device['port']}项目名称或爬虫名称错误 {e}"}

    def del_project(self, device):
        """
        删除爬虫项目
        :param device:
        :return:
        """
        scrapyd = ScrapydAPI(f"http://{device['ip']}:{device['port']}")
        try:
            if scrapyd.delete_project(self.project_name):
                logger.info(f"在{device['ip']} {device['port']}上 删除爬虫项目成功")
                return True, None
            else:
                return False, f"在{device['ip']} {device['port']}上删除项目失败"
        except requests.exceptions.ConnectionError:
            logger.warning(f"连接设备失败：{device['ip']} {device['port']}")
            return False, f"连接设备失败：{device['ip']} {device['port']}"
        except Exception as e:
            logger.warning(f"{device['ip']} {device['port']}项目名称{self.project_name} 错误？{e}")
            return False, f"{device['ip']} {device['port']}项目名称{self.project_name} 错误？ {e}"

    def start(self, device, platform):
        """
        开启某个爬虫
        通过scrapyd 实现启动某个爬虫,并查询爬虫的启动状态,同时判断是否能够连接远程设备，
        如果不能，则更新数据库中远程设备信息，返回报错信息
        如果爬虫启动成功，则返回False,否则返回报错信息
        """
        # 1通过命令行启动项目
        # 检查项目的启动状态
        scrapyd = ScrapydAPI(f"http://{device['ip']}:{device['port']}")
        try:
            server_id = f"{device['ip']}:{device['port']}"
            jobid = scrapyd.schedule(self.project_name, platform, one_project_name=self.project_name)
            self._spider_job_id[server_id][platform] = jobid
            return False, None
        except requests.exceptions.ConnectionError:
            # 设备连接失败
            logger.warning(f"{device['ip']} {device['port']}连接失败")
            return "device", {"device": device}
        except Exception as e:
            logger.warning(f"{device['ip']} {device['port']} 项目名称{self.project_name} 或爬虫名称{platform}错误 {e}")
            return "spider", {"spider": f"{device['ip']} {device['port']}项目名称或爬虫名称错误 {e}"}

    def check_spider_finished(self, ip, platform):
        """
        检查爬虫的状态，如果为finished或者None,则返回true,否则返回false
        :param ip:
        :param platform:
        :return:
        """
        info = self._spider_status[ip].get(platform, None)
        if info and info["status"] in ["pending", "running"]:
            return False
        return True

    def start_all(self, device):
        """
        启动一个分布式设备爬虫并返回报错信息
        :param device:
        :return:
        """
        info = {}
        device_error = False
        getattr(self, "update_spider_status_in_devices")()  # 更新爬虫状态
        for platform, value in self.spiders.items():
            server_id = f"{device['ip']}:{device['port']}"
            if value and self.check_spider_finished(server_id, platform):
                status, error = self.start(device, platform)
                self.spiders[platform] = True
                if error:
                    info[platform] = error
                    if status == "device":
                        device_error = True
        return info, device_error

    def stop_all(self, device):
        """
        停止一个分布式设备上的爬虫
        """
        errors = {}
        device_error = True
        for platform, value in self.spiders.items():
            sever_id = f"{device['ip']}:{device['port']}"
            if self._spider_status[sever_id][platform] != "finished":
                status, error = self.stop(device, platform)
                self.spiders[platform] = False
                if error:
                    errors[platform] = error
                    if status == "device":
                        device_error = False
        return errors, device_error

    def generate_config(self):
        """
        生成该类的配置信息
        """
        return {"project_name": self.project_name, "spiders": self.spiders}

    def get_pro_spider(self):
        """
        获取爬虫的状态：
        原则：以远程的爬虫信息为主
        现有问题：1.项目和分布式设备上的爬虫不一致问题
        self._spider_status:分布式设备上的爬虫信息
        :return:
        """
        spider_info = defaultdict(dict)
        getattr(self, "update_spider_status_in_devices")()
        for server_id, spiders_info in self._spider_status.items():

            for spider, label in self.spiders.items():
                spider_info[server_id][spider] = {"status": "未启动", "start_time": "None", "label": label}
            for spider, info in spiders_info.items():
                if spider not in self.spiders:
                    # 不在配置文件中的爬虫
                    if info["status"] in ["pending", "running"]:
                        self._spider_job_id[server_id][spider] = info["job_id"]
                        if all(self.stop_one_spider(spider).values()):
                            # 关闭在分布式设备上启动的爬虫，关闭失败则登记信息
                            info["device_status"] = "在分布式设备上启动，未在服务中登记"
                            spider_info[server_id][spider] = info
                else:
                    # 在配置文件中的信息
                    if not self.spiders[spider]:
                        # 配置文件禁用该爬虫
                        if not all(self.stop_one_spider(spider).values()):
                            # 禁用成功
                            info["status"] = "finished"
                    spider_info[server_id][spider].update(info)
        return spider_info

    @classmethod
    def from_params(cls, params):
        return cls(**params)

    def update_from_dict(self, spider_status):
        """
        根据前端传递的爬虫状态来更新爬虫，返回更新后的爬虫状态
        """
        errors = {}
        for platform, flag in spider_status.items():
            if platform in self.spiders:
                # 该爬虫项目中存在该爬虫
                if flag:
                    # 启动爬虫
                    errors[platform] = self.start_one_spider(platform)  # 启动一个爬虫
                    if not all(errors[platform].values()):
                        self.spiders[platform] = True
                else:
                    # 禁用爬虫
                    errors[platform] = self.stop_one_spider(platform)
                    if not all(errors[platform].values()):
                        self.spiders[platform] = False
            else:
                errors[platform] = f"爬虫项目{self.project_name} 不存在爬虫{platform}"
        return self.get_pro_spider(), errors


if __name__ == '__main__':
    # scrapyd = ScrapydAPI("http://localhost:6800")
    # print(scrapyd.list_projects())
    # print(scrapyd.schedule("test", "微博",one_project_name = "eWuChongTu"))
    # print(scrapyd.list_spiders("test"))
    # print(scrapyd.list_jobs("test"))
    # print(scrapyd.list_projects())
    # print(scrapyd.list_spiders("LTW"))
    # print(scrapyd.schedule("test", "微博"))
    # print(scrapyd.list_jobs("default"))
    # print(scrapyd.delete_project("default"))
    # jobid = scrapyd.schedule("default", "微博", one_project_name="default")
    #
    # print(jobid)
    # print(scrapyd.cancel("default",jobid))
    # from tqdm import tqdm
    #
    # infos = scrapyd.list_jobs("default")
    # for key in ["pending", "running"]:
    #     for info in tqdm(infos[key]):
    #         scrapyd.cancel("default", info["id"])
    # try:
    #     print(scrapyd.schedule("default", "hotsearchd"))
    # except Exception as e:
    #     print(e.__class__)
    # spider = SpiderManager(None)
    # print(spider.get_all_content_spdier())
    # spider = SpiderManager(None)
    # device = {"ip": "180.201.163.246", "password": "123", "address": "/home/users/CT/pycharmproject/spiders",
    #           "username": "chase", "port": 6800}
    # print(spider.create_project_in_device(device))
    
    from base.db.dbSlot import dbslot
    ssm = SearchSpidersManager(dbslot)
    for i,request in enumerate(ssm.get_request_from_keyword("微博","新版新冠防控方案发布")):
        print(i,request)
