"""
待改进：
    1.项目中的所有配置应当保存在数据库或者redis中，不应保存在文件中
        应当新建的表包括
        （1）爬虫项目表：项目名称，项目创建信息，作者，热点爬虫配置，内容爬虫配置，设备配置，账户配置
            热点爬虫配置：热点爬虫名称，启用状态
            内容爬虫配置：内容爬虫名称
            设备配置：设备名称，设备状态
            账户配置：账户名称，启用状态
        （2）定时任务表：name,task,trigger,func,take_para,kwargs
"""

import datetime
import json
from collections import defaultdict
from copy import deepcopy
from threading import Thread
from typing import Union, List
import sys
sys.path.append("/home/spiders/")

import gevent
import pandas as pd
from gevent import monkey

from base.db.Influx import Influx
from base.db.dbSlot import Slot
from base.db.mysql import Mysql, Device, EventU, CommentU
from base.db.redis_ import Redis
from base.utils.time import str_to_datetime
from monitor import *
from monitor.deviceManager import DeviceManager
from monitor.headerManager import HeadManager
from monitor.setting import REDIS_KEYWORD, REDIS_SPIDER_ACC_VALID, DefaultAccount, REDIS_CUSTOM_KEYWORD
from monitor.spiderManager import SpiderManager, HotSpiderManager, SearchSpidersManager
from monitor.timing import JobManager

# 默认的项目配置参数
default_config = {
    "job_manager": {
        "hotsearch": {"name": "hotsearch", "trigger": "interval", "task": "HotSpiderManager.crawl_hot_title",
                      "func": "ProjectManager.crawl_hot_title",
                      "kwargs": {"day": 0, "hour": 0, "minute": 0, "second": 10},
                      "task_para": []},
        "get_request_from_hot": {
            "name": "get_request_from_hot",
            "trigger": "interval",
            "task": "ProjectManager.run_func_by_hot",
            "func": "ProjectManager.get_request_from_keywords_hot",
            "kwargs": {
                "day": 0,
                "hour": 0,
                "minute": 0,
                "second": 7
            },
            "task_para": "ProjectManager.run_func_by_thread"
        },
        "get_request_from_custom": {
            "name": "get_request_from_custom",
            "trigger": "interval",
            "task": "ProjectManager.run_func_by_thread",
            "func": "ProjectManager.get_request_from_keywords_custom",
            "kwargs": {
                "day": 0,
                "hour": 10,
                "minute": 10,
                "second": 7
            },
            "task_para": "ProjectManager.run_func_by_thread"
        },
        "timing_save": {
            "name": "timing_save",
            "trigger": "interval",
            "task": "ProjectManager.run_func_by_thread",
            "func": "ProjectManager.save_config",
            "kwargs": {
                "day": 0,
                "hour": 0,
                "minute": 10,
                "second": 10
            },
            "task_para": "ProjectManager.run_func_by_thread"
        }},
    "projects": [
        {
            "author": "ds",
            "create_time": "2021-10-10 00:00:00",
            "name": "default",
            "desc":"",
            "spider_manager": {"project_name": "default", "spiders": {}},
            "hot_spider_config": {},
            "devices_manager": {},
            "crawl_time": {"start": "2019-01-01 23:23", "end": "2022"},
            "valid": True,
            "account_platforms":[]
        }
    ]
}


class Project:
    def __init__(self, author, name,
                 spider_manager: SpiderManager,
                 database_manager: Slot,
                 devices_manager: DeviceManager,
                 hot_spider_config: dict = {},
                 create_time=None,
                 crawl_time: dict = {},
                 valid: bool = True,
                 desc = "",
                 account_platforms : list=[],
                 **kwargs):
        '''
        :param author: str
        :param name: str
        :param jobmanager: class
        :param spider_manager: class
        :param database_manager: class
        :param devices_manager: class
        '''
        self.create_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') if not create_time else create_time
        self.author = author
        self.name = name
        self.hot_spider_config = hot_spider_config
        self.spider_manager = spider_manager
        self.database_manager = database_manager
        self.device_manager = devices_manager
        self.crawl_time_section = TimeSection(**crawl_time)
        self.valid = valid  # 表示项目是否启用
        self.desc = desc
        self._spider_stauts = defaultdict(dict)

        self.spider_manager.set_spider_status(self._spider_stauts)
        self.check_project_in_device()
        self.update_spider_status()
        self.spider_manager.add_func("update_spider_status_in_devices", self.update_spider_status)
        self.spider_manager.add_func("start_one_spider", self.start_one_spider)
        self.spider_manager.add_func("stop_one_spider", self.stop_one_spider)
        self.account_platforms = set(account_platforms)

        # 初始化项目
        self.create_table_by_project_name()
        self.create_log_dir()

    def update_crawl_time(self, start=None, end=None):
        """
        更新爬虫项目的爬取时间范围
        :param start:
        :param end:
        :return:
        """

        crawl_time = self.crawl_time_section.to_dict()
        if start:
            crawl_time["start"] = start
        if end:
            crawl_time["end"] = end
        self.crawl_time_section = TimeSection(**crawl_time)
        return self.crawl_time_section

    def add_devices(self, server_id):
        """
        添加分布式设备，并启动该设备上的爬虫
        :param ips:
        :return:
        """
        errors = self.device_manager.add_device_from_server_id(server_id)
        self.check_project_in_device()  # 启动分布式设备上的爬虫
        return errors

    def rm_device(self, ips):
        """
        删除分布式设别，并停止该设备上的爬虫
        :param ips:
        :return:
        """
        # 停止该设备上的爬虫
        for ip, device in self.device_manager.valid_devices:
            if ip in ips:
                self.spider_manager.del_project(device)
        errors = self.device_manager.rm_device_from_ip(ips)
        return errors

    def create_table_by_project_name(self):
        """
        根据项目 名称创建表
        :return:
        """
        # 创建内容表
        self.database_manager.mysql.create_new_table(EventU, self.name)
        self.database_manager.mysql.create_all()

        # 创建评论表
        self.database_manager.mysql.create_new_table(CommentU, self.name)
        self.database_manager.mysql.create_all()

        # 创建爬虫项目日志信息数据库
        self.database_manager.influx.create_db(self.name)

    def create_log_dir(self):
        """
        创建日志目录
        :return:
        """
        log_dir = os.path.join(root, 'log', self.name)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

    def spread_monitor(self):
        """
        传播态势监测
        :return:
        """
        data = {}
        table_name = f"{self.name}_spread"
        sql = f"SELECT * FROM {table_name}"
        results = self.database_manager.influx.query(sql, database=self.name)
        if results:
            data_frame = pd.DataFrame(results.get_points(table_name, None))
            data_frame["time"] = data_frame["time"].apply(lambda x: x[0:-4].replace("T", " ") + ":00")
            data_group = data_frame.groupby("time")
            data["x"] = list(data_group.indices.keys())
            data["传播态势"]=data_group["spread"].sum().tolist()
        return data

    def secure_monitor(self, mode="hour"):
        """
        安全态势监测,返回关键词数量最多的15个节点,最多保存15天的数据
        :param mode :按小时划分还是按天划分
        :return:
        """
        all_keyword = defaultdict(int)
        keywords_past = {}
        all_data = {"x":[],"emotion":{"pos":[],"neg":[]},"keywords": defaultdict(list)}
        for past_hour in range(14*24):
            time_name = datetime.datetime.now()-datetime.timedelta(hours=14*24-past_hour)
            table_name = f"{self.name}_secure{time_name.strftime('%Y_%m_%d_%H')}"
            sql = f'SELECT * FROM {table_name}'
            results = self.database_manager.influx.query(sql, database=self.name)
            if results:
                all_data["x"].append(time_name.strftime('%Y:%m:%d %H'))
                data_frame = pd.DataFrame(results.get_points(table_name, None))
                data_frame.fillna(0)
                all_data["emotion"]["pos"].append(float(data_frame["pos"].sum()))
                all_data["emotion"]["neg"].append(float(data_frame["neg"].sum()))
                keywords_past[time_name.strftime('%Y:%m:%d %H')] = data_frame.sum(axis=0).to_dict()
                for key,value in keywords_past[time_name.strftime('%Y:%m:%d %H')].items():
                    all_keyword[key] = value
        if "keyword" in all_keyword: del all_keyword["keyword"]
        if "pos" in all_keyword:del all_keyword["pos"]
        if "neg" in all_keyword:del all_keyword["neg"]
        if "time" in all_keyword:del all_keyword["time"]
        if "project_name" in all_keyword:del all_keyword["project_name"]
        most_common_keywords = dict(sorted(all_keyword.items(),key=lambda x:x[1],reverse=True)[0:10])
        for time_str in all_data["x"]:
            for most_key in most_common_keywords.keys():
                number = keywords_past[time_str].get(most_key,0)
                all_data["keywords"][most_key].append(number)
        return all_data

    def spider_monitor(self, platform):
        """
        返回爬虫的运行状态数据
        :param platform:
        :return:
        """
        # 查询爬虫运行数据
        data = {}
        sql = f'SELECT * FROM "{platform}"'
        results = self.database_manager.influx.query(sql, database=self.name)
        if results:
            data_frame = pd.DataFrame(results.get_points(platform, None))
            data_frame["time"] = data_frame["time"].apply(lambda x: x[0:-4].replace("T", " ") + ":00")
            data_group = data_frame.groupby("time")
            data["x"] = list(data_group.indices.keys())
            data["数据量"] = data_group["item"].sum().tolist()
            data["待请求数量"] = data_group["enqueued"].sum().tolist()
            data["已抓取数量"] = data_group["dequeued"].sum().tolist()
            data["请求量"] = data_group["requested"].sum().tolist()
            data["响应量"] = data_group["response"].sum().tolist()
            data["200"] = data_group["response_200"].sum().tolist()
            data["301"] = data_group["response_301"].sum().tolist()
            data["404"] = data_group["response_404"].sum().tolist()

        # 查询爬虫启动信息
        sql = f'SELECT LAST(start_time) FROM "{platform}_open"'
        results = self.database_manager.influx.query(sql, database=self.name)
        if results:
            data["start_time"] = list(results.get_points(f"{platform}_open", None))[0]["last"]

        # 查询爬虫关闭信息
        sql = f'SELECT LAST(end_time),reason FROM "{platform}_closed"'
        if results:
            results = self.database_manager.influx.query(sql, database=self.name)
            result = list(results.get_points(f"{platform}_closed", None))
            if results and str_to_datetime(result[0]["last"]) > str_to_datetime(data["start_time"]):
                data["end_time"] = result[0]["last"]
                data["closed_reason"] = result[0]["reason"]
            else:
                data["end_time"] = "None"
                data["closed_reason"] = "None"
        return data

    @property
    def custom_keywords(self):
        """
        从redis数据库中加载数据
        :return:
        """
        redis_key = REDIS_CUSTOM_KEYWORD.substitute(project_name=self.name)
        title_keys = self.database_manager.redis.smembers(redis_key)
        return title_keys

    def add_hot_spider(self, spider_name: list):
        """
        添加热点爬虫
        :param spider_name:
        :return:
        """
        errors = {}
        if spider_name:
            for spider in spider_name:
                if self.hot_spider_config.get(spider, False):
                    errors[spider] = "爬虫已经存在"
                else:
                    self.hot_spider_config[spider] = True
                    errors[spider] = "添加成功"
        return errors

    def rm_hot_spider(self, spider_name: list):
        """
        删除热点爬虫
        :param spider_name:
        :return:
        """
        errors = {}
        if spider_name:
            for spider in spider_name:
                if self.hot_spider_config.get(spider, False):
                    self.hot_spider_config.pop(spider)
                    errors[spider] = "删除成功"
                else:
                    errors[spider] = "爬虫不存在"
        return errors

    def check_project_in_device(self):
        """
        检查分布式设备是否存在该项目，不存在则创建
        """
        errors = {}
        for ip, device in self.device_manager.devices.items():
            status, msg = self.spider_manager.get_device_projects(device)
            errors[device["ip"]] = msg
            if status == "device":
                if not self.spider_manager.create_project_in_device(device):  # 在分布式设备上启动scrapyd
                    self.update_device_valid(device)
            elif not status:
                if self.name not in msg:
                    # 创建项目
                    errors[device["ip"]] = self.spider_manager.create_project_in_device(device)
        logger.info(errors)

    def add_custom_keywords(self, keys_info: dict):
        """
        增加自定义爬虫关键词
        """
        if keys_info:
            reids_key = REDIS_CUSTOM_KEYWORD.substitute(project_name=self.name)
            title_keywords = [keys_info.get("title", None) + "_" + keyword for keyword in keys_info["keywords"]]
            self.database_manager.redis.sadd(reids_key, *title_keywords)

    def rm_custom_keywords(self, keys_info: dict):
        """
        删除自定义爬虫关键词
        """
        if keys_info:
            redis_key = REDIS_CUSTOM_KEYWORD.substitute(project_name=self.name)
            title_keywords = [keys_info.get("title", None) + "_" + keyword for keyword in keys_info["keywords"]]
            self.database_manager.redis.srem(redis_key, *title_keywords)

    def update_account(self, platforms):
        """
        更新本爬虫账户,返回更新后的结果
        platforms={"微博":{"add":[],"rm":[]}}
        """
        acc = {}
        for platform, param in platforms.items():
            self.account_platforms.add(platform)
            redis_key = convert_to_pinyin(REDIS_SPIDER_ACC_VALID.substitute(project_name=self.name, platform=platform))
            print(redis_key)
            if param["rm"]:
                self.database_manager.redis.srem(redis_key, *param["rm"])  # 删除
            if param["add"]:
                self.database_manager.redis.sadd(redis_key, *param["add"])  # 添加
            acc[platform] = list(self.database_manager.redis.smembers(redis_key))
        return acc

    def get_account_info(self):
        """
        获取当前项目下的所有爬虫账户
        """
        acc = {}
        for platform in self.account_platforms:
            redis_key = convert_to_pinyin(REDIS_SPIDER_ACC_VALID.substitute(project_name=self.name, platform=platform))
            acc[platform] = list(self.database_manager.redis.smembers(redis_key))
        return acc

    def start_spider(self):
        """
        启动爬虫项目，启动该爬虫项目下的所有爬虫,并返回报错信息
        """
        errors = {}
        self.valid = True
        for device in self.device_manager.valid_devices:
            errors[device["ip"]], device_error = self.spider_manager.start_all(device)
            if device_error:
                self.update_device_valid(device)
        # self.update_spider_status()
        return errors

    def del_spider(self, spider_name: Union[str, list]):
        """
        删除爬虫
        """
        errors = {}
        valid_devices = self.device_manager.valid_devices
        if not valid_devices:
            return {"error": "没有可用设备"}
        for device in valid_devices:
            errors[device["ip"]], device_error = self.spider_manager.del_spider(device, spider_name)
            if device_error:
                self.update_device_valid(device)
        return errors

    def start_one_spider(self, spider_name):
        """
        启动单个爬虫,并返回报错信息
        """
        self.valid = True
        errors = {}
        valid_devices = self.device_manager.valid_devices
        if not valid_devices:
            return {"error": "没有可用设备"}
        for device in valid_devices:
            server_id = f"{device['ip']}:{device['port']}"
            if self.spider_manager.check_spider_finished(server_id, spider_name):
                status, error = self.spider_manager.start(device, spider_name)
                if error:
                    errors[device["ip"]] = error
                    if status == "device":
                        self.update_device_valid(error["device"])
                else:
                    # 启动成功
                    errors[device["ip"]] = False
                # 更新数据库中爬虫的状态
            else:
                errors[device["ip"]] = False
        # self.update_spider_status()
        return errors

    def __del__(self):
        for device in self.device_manager.valid_devices:
            self.spider_manager.del_project(device)

    def update_device_valid(self, device):
        """
        更新数据库中设备的状态
        :param ip:
        :param valid:
        :return:
        """
        print(device, device.to_item())
        device["valid"] = False
        self.database_manager.mysql.update(Device(**device.to_item()))

    def stop(self):
        """
        停止爬虫项目，停止该爬虫项目下的所有爬虫
        """
        self.valid = False
        errors = {}
        valid_devices = self.device_manager.valid_devices
        if not valid_devices:
            return {"error": "没有可用设备"}
        for device in valid_devices:
            errors[device["ip"]] = self.spider_manager.stop_all(device)
        # self.update_spider_status()
        return errors

    def stop_one_spider(self, spider_name):
        """
        停止单个爬虫
        """
        errors = {}
        valid_devices = self.device_manager.valid_devices
        if not valid_devices:
            return {"error": "没有可用设备"}
        for device in valid_devices:
            status, error = self.spider_manager.stop(device, spider_name)
            if error:
                errors[device["ip"]] = error
                if status == "device":
                    self.update_device_valid(error["device"])
            else:
                # 停止成功
                errors[device["ip"]] = False
            # 更新数据库中爬虫的状态
        # self.update_spider_status()
        return errors

    def update_spider_status(self):
        """
        更新爬虫状态
        """
        for device in self.device_manager.valid_devices:
            if device:
                self.spider_manager.update_spider_status(device)

    def update_hot_spider_config(self, new_hot_spider_status: dict):
        error = {}
        for platform, status in new_hot_spider_status.items():
            if self.hot_spider_config.get(platform):
                self.hot_spider_config[platform] = status
            else:
                message = f"更改热点爬虫，爬虫项目{self.name} 不存在热点爬虫{platform}"
                error[platform] = message
                logger.warning(message)
        return self.hot_spider_config, error

    @property
    def valid_hot_spider(self):
        platforms = set()
        for platform, status in self.hot_spider_config.items():
            if status:
                platforms.add(platform)
        return platforms

    def generate_config(self):
        return {"create_time": self.create_time, "author": self.author, "name": self.name, "desc": self.desc,
                "spider_manager": self.spider_manager.generate_config(),
                "hot_spider_config": self.hot_spider_config,
                "devices_manager": self.device_manager.generate_config(),
                "crawl_time": self.crawl_time_section.to_dict(),
                "valid": self.valid,
                "account_platforms":list(self.account_platforms)}

    @classmethod
    def from_params(cls, params, dbslot):
        params["spider_manager"] = SpiderManager.from_params(params["spider_manager"])
        params["devices_manager"] = DeviceManager.from_params(params["name"], params["devices_manager"], dbslot)
        return cls(database_manager=dbslot, **params)


class ProjectManager(metaclass=SignalInstance):
    """
    在PM中实例化热点爬虫管理和检索爬虫管理，在将爬取到的url保存到相应的爬虫项目中
    定时任务目前只支持对热点爬虫和检索爬虫进行定时,并且检索爬虫将在热点爬虫运行结束后启动
    热点管理和自定义关键词
    1。热点管理：
    （1）爬虫项目定义热点，选择关键词，后端对所有项目的热点平台进行统计，统一爬取相应平台的热点，保存到redis数据库中
    （2）检索爬虫从相应的redis数据库中获取关键词后，获取该关键词对应的url,在保存到相应的爬虫项目的request 队列当中
    2.自定义关键词
    （1）爬虫能够自定义相应的关键词，新建redis数据库，在redis数据中新建字段 spdier:project_name:custom:keywords用来保存自定义关键词
    （2）自定义关键词的来源：用户自己的输入，用户从热点列表中的选择。

    程序逻辑：
    1.首先判断爬虫项目是否存在自定义关键词，若存在则先取出自定义关键词进行爬取。
    2.再判断爬虫项目是否开启了热点爬虫，若存在则进行热点爬虫。
    """

    def __init__(self, job_manager: JobManager = None, hot_spider_manager: HotSpiderManager = None):
        self.projects = {}
        self.hot_spider_manager = hot_spider_manager  #
        self.job_manager = job_manager
        self.dbslot = Slot(Mysql(logger), Redis(), influx=Influx())
        self.create_from_config()
        self.search_spider_manager = SearchSpidersManager(self.dbslot)
        self._header_manager = HeadManager()

        self.save_stopwords_to_redis()

    def save_stopwords_to_redis(self):
        """
        将停用词加载到缓存当中
        """
        stopwords_path = os.path.join(root,"src","stopwords")
        logger.info("redis 初始化停用词")
        for file in os.listdir(stopwords_path):
            with open(os.path.join(stopwords_path,file),mode='r',encoding='utf-8') as f:
                stopwords = [stopword.strip() for stopword in f.readlines()]
                self.dbslot.redis.sadd("STOPWORDS",*stopwords)

    def platforms(self):
        """
        热点爬虫的平台
        """
        platforms = set()
        for project in self.projects.values():
            platforms = platforms | project.valid_hot_spider
        return platforms

    def get_all_devices(self):
        devices = {}
        for device in self.dbslot.mysql.query_device():
            info = device.to_dict()
            del info["password"]
            devices[info["server_id"]] = info
        return devices

    def add_devices(self, devices: Union[List[dict], dict], cover=False):
        """
        系统添加分布式设备
        1。是否覆盖原有数据
        2.统计报错信息
        cover:是否覆盖原数据
        """
        errors = {}
        if cover:
            device_instance = []
            if isinstance(devices, dict):
                devices["password"] = encryption(devices["password"])
                devices["server_id"] = devices["ip"] + ":" + str(devices["port"])
                device_instance.append(Device(**devices))
            elif isinstance(devices, List):
                for device in devices:
                    device["password"] = encryption(device["password"])
                    device["server_id"] = device["ip"] + ":" + str(device["port"])
                    device_instance.append(Device(**device))
            errors.update(self.dbslot.mysql.update(device_instance))
            return errors
        else:
            if isinstance(devices, dict):
                devices["server_id"] = devices["ip"] + ":" + str(devices["port"])
                if not self.dbslot.mysql.query("Device", "server_id", devices["server_id"]):
                    devices["password"] = encryption(devices["password"])
                    self.dbslot.mysql.save(Device(**devices))
                else:
                    errors[devices["ip"]] = f"数据库中存在相同的ip {devices['ip']}"
                return errors
            else:
                for device in devices:
                    errors.update(self.add_devices(device, cover))
                return errors

    def rm_devices(self, ips: List):
        """
        删除分布式设备
        """
        errors = {}
        for ip in ips:
            errors.update(self.dbslot.mysql.rm_data("Device", "server_id", ip))
        return errors

    def create_from_config(self):
        """
        从配置文件中初始化项目
        """
        config = self.load_config()
        if not config:
            config = default_config
        projects = {}
        for param in config["projects"]:
            name = param["name"]
            merge_dict = deepcopy(default_config["projects"][0])
            merge_dict.update(param)
            projects[name] = Project.from_params(param, self.dbslot)
        self.projects = projects

        self.hot_spider_manager = HotSpiderManager(self.platforms, self.dbslot)
        self.job_manager = JobManager()
        self.init_timing_job_from_param(config["job_manager"])

    def add_proj(self, project: Project):
        self.projects[project.name] = project

    def del_proj(self, project_name: str):
        if project_name in self.projects:
            del self.projects[project_name]
            return {"code": "200", "message": f"删除项目{project_name}成功"}
        else:
            return {"code": "300", "message": f"项目{project_name}不存在"}

    @staticmethod
    def load_config():
        try:
            with open(os.path.join(root, 'conf', 'pm.json'), mode='r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except:
            return None

    def generate_config(self):
        params = {"projects": []}
        for name, project in self.projects.items():
            params["projects"].append(project.generate_config())
        params["job_manager"] = self.job_manager.generate_config()
        return params

    def save_config(self, *args):
        params = self.generate_config()
        with open(os.path.join(root, 'conf', 'pm.json'), mode='w', encoding="utf8") as f:
            json.dump(params, f, ensure_ascii=False)
        logger.info("保存配置成功")

    def add_timing_job_from_param(self, param):
        """
        增加定时任务
        :param param:
        :return:
        """
        param = self.get_callable_from_param(param)
        return self.job_manager.add_job_to_scheduler(param)

    def update_timing_job(self, params):
        """
        更新定时任务
        :param param:
        :return:
        """
        msg = {}
        for name, param in params.items():
            param = self.get_callable_from_param(param)
            if self.job_manager.job_exist(param["name"]):
                if self.job_manager.update_job_to_scheduler(param):
                    msg[name] = "更新成功"
                else:
                    msg[name] = "更新失败"
            else:
                if self.job_manager.add_job_to_scheduler(param):
                    msg[name] = "添加成功"
                else:
                    msg[name] = "添加失败"
        return msg

    def create(self, params):
        """
        params:{"name":projname,spiders:{"微博":True,...},}
        """
        if params["name"] in self.projects:
            logger.warning(f"E 创建项目 项目名称{params['name']}已经存在")
            logger.warning(f"{params}")
            return {"code": 300, "message": f"项目名称{params['name']}已经存在"}
        try:
            merge_dict = deepcopy(default_config["projects"][0])
            merge_dict.update(params)
            project = Project.from_params(merge_dict, self.dbslot)
            self.projects[project.name] = project
            logger.info(f"C 创建项目 创建项目{params['name']}")
            return {"code": 200, "message": project.generate_config()}
        except Exception as e:
            logger.exception(f"E 创建项目 {params['name']} 失败 {e}")
            logger.error(f"{params}")
            return {"code": 500, "message": f"E 创建项目 创建项目{params['name']} 失败"}

    def __getitem__(self, item: Union[str, int]) -> Union[Project, bool]:
        if isinstance(item, str):
            if item in self.projects:
                return self.projects[item]
        elif isinstance(item, int):
            return list(self.projects.values())[item]
        return False

    def merge_crawl_time(self, names: list):
        time = TimeSection(get_date(), get_date())
        project_time = {}
        for name in names:
            time = time | self[name].crawl_time_section
            project_time[name] = self[name].crawl_time_section
        return time, project_time

    def merge_crawl_platform(self, names):
        """
        获取内容爬虫所需要的平台
        {h1:[c1,c2,...],h2:[c2,c3,...],...}
        {h1:[p1,p2,...],}
        :return {hot_spider:set[content_spider],...},{hot_spider:set[project1,project2]}
        """
        hot_map_content = defaultdict(set)
        hot_map_project = defaultdict(set)
        for name in names:
            project = self[name]
            for hot_spider in project.valid_hot_spider:
                hot_map_project[hot_spider].add(name)
                hot_map_content[hot_spider] |= project.spider_manager.get_valid_platform()

        return hot_map_content, hot_map_project

    def crawl_hot_title(self, *args):
        """
        !!!以线程启动该任务
        """
        self.hot_spider_manager.crawl_hot()

    def get_request_from_keywords_custom(self, *args):
        """
        !!!以线程启动该任务，该任务内以协程的方式启动
        对自定义关键词进行爬取
        1.获取那个关键词对应那个项目，根据内容爬虫平台决定将url放入那个队列
        2.将获取到的url 保存到redis数据库中的对应的项目request队列中
        """
        keywords_pro = defaultdict(set)  # 保存关键词对应的项目
        keywords_pla = defaultdict(set)  # 保存关键词对应的平台
        keywords_title = {}
        for name, project in self.projects.items():
            for title_keyword in project.custom_keywords:
                keywords_pro[title_keyword].add(name)
                keywords_pla[title_keyword] |= project.spider_manager.get_valid_platform()
        # coroutines = []  # 协程池
        self.start_finished_spider_every_interval(self.get_valid_project())
        for keyword, project_names in keywords_pro.items():
            crawl_time, project_times = self.merge_crawl_time(list(keywords_pro[keyword]))
            platforms = list(keywords_pla[keyword])

            self.search_spider_manager.crawl_by_keyword(
                project_names,
                project_times,
                platforms,
                crawl_time,
                keyword
            )
            # 添加协程任务
        #     coroutines.append(
        #         self.search_spider_manager.crawl_by_keyword(
        #             project_names,
        #             project_times,
        #             platforms,
        #             crawl_time,
        #             keyword
        #         )
        #     )
        # gevent.joinall(coroutines)

    def get_valid_project(self):
        """
        获取启用的爬虫项目
        :return:
        """
        valid_projects = []
        for name, project in self.projects.items():
            if project.valid:
                valid_projects.append(name)
        return valid_projects

    def start_finished_spider_every_interval(self, project_names):
        """
        在每个定时任务区间，重新启动内容爬虫
        :param project_names:
        :return:
        """
        for name in project_names:
            self[name].start_spider()

    def get_request_from_keywords_hot(self, *args):
        """
        对热点内容进行搜索
        !!!以线程启动该任务,该任务内以协程的方式启动
        1.先从redis中取出所有爬虫项目中所有的关键词
        2.根据该关键词，使用所有的内容爬虫去检索
        3.在将检索结果保存到不同的爬虫项目，不同的内容爬虫中
        """
        # pool = AsyncPool(maxsize=1000)
        project_names = self.get_valid_project()  # 有效的爬虫平台
        hot_content, hot_project = self.merge_crawl_platform(project_names)  # {platform:project}
        crawl_time, project_times = self.merge_crawl_time(project_names)
        # coroutines = []
        self.start_finished_spider_every_interval(project_names)
        for platform, map_contents in hot_content.items():
            redis_key = REDIS_KEYWORD.substitute(platform=platform)
            keywords = self.dbslot.redis.smembers(redis_key)
            # gevent.monkey.patch_all(thread=False)

            for keyword in keywords:
                # coroutines.append(gevent.spawn(
                #     self.search_spider_manager.crawl_by_keyword(
                #         all_content_spider_platforms[platform],
                #         project_times,
                #         [platform],
                #         crawl_time,
                #         keyword
                #     )
                # ))
                self.search_spider_manager.crawl_by_keyword(
                    list(hot_project[platform]),
                    project_times,
                    list(map_contents),
                    crawl_time,
                    keyword
                )

        # gevent.joinall(coroutines)

    def run_func_by_thread(self, func, *args):
        """
        以线程的方式启动函数func
        """
        task = Thread(target=func, args=args)
        task.setDaemon(True)  # 设置守护进程
        task.start()

    def get_account_from_db(self):
        """
        从msyql数据库中获取可用的账户信息
        """
        accounts = self.dbslot.mysql.get_all_account()
        info = defaultdict(dict)
        for account in accounts:
            acc_info = {"user": account.user, "valid": account.valid,
                        "date": account.date.strftime("%Y-%m-%d %H:%M:%S"), "id": account.id,
                        "platform": account.platform, "cookie": account.cookie, "password": account.password}
            info[account.platform][acc_info["user"]] = acc_info
        return info

    def update_sys_account(self, account_infos: list):
        """
        更新账户信息
        """
        errors = []
        for account in account_infos:
            new_account = deepcopy(DefaultAccount)
            new_account.update(account)
            msg = self.dbslot.mysql.update_cookie(new_account)
            errors.append(msg)
        return errors

    def rm_sys_account(self, account_ids: list):
        """
        删除账户信息
        """
        errors = {}
        for account_id in account_ids:
            status, msg = self.dbslot.mysql.delete_one_row("Cookie", account_id)
            errors[account_id] = msg
        return errors

    def init_timing_job_from_param(self, params):
        """
        更新当前的定时任务信息
        {"name":{"name":,...},...}
        task的要求的值："get_request_from_keywords_custom","get_request_from_keywords_hot","crawl_hot_title"
        返回当前定时任务的信息
        """
        try:
            self.job_manager.stop()
        except:
            pass
        for name, param in params.items():
            param = self.get_callable_from_param(param)
            self.job_manager.add_job_from_param(param)

        self.job_manager.start()
        return self.job_manager.generate_config()

    def get_callable_from_param(self, param):
        """
        根据函数名称替换函数
        :param param:
        :return:
        """
        func = param["func"].split(".")
        param["task"] = self.run_func_by_thread  # 将任务函数更新为线程的方式
        param["func"] = getattr(self, func[-1])  # 将任务函数更新为线程的参数
        return param

    def delete_timing_job(self, name):
        """
        删除定时任务
        """
        status, msg = self.job_manager.delete_job(name)
        return status, msg


if __name__ == '__main__':
    pm = ProjectManager()
    # pm.get_request_from_keywords_hot()
    print(pm["eWuChongTu"].secure_monitor())
    # print(pm["default"].device_manager.valid_devices[0].to_dict())
    # pm.create(default_config["projects"][0])
    # pm.save_config()
    # pm["default"].start_spider()
    # pm["default"].update_spider_status()
    # print(1,pm["default"]._spider_stauts)

    # time.sleep(3600)
    print(pm["default"].spider_monitor("微博"))
    # print(pm.merge_crawl_platform(pm.get_valid_project()))
    # device = [{
    #     "ip": "180.201.163.245",
    #     "username": "chase",
    #     "password": "qwe",
    #     "address": "/home/chase/",
    #     "port": "22",
    #     "valid": True
    # }]
    # print(pm.add_devices(device, cover=True))
