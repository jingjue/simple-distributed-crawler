"""
爬虫相关的配置参数
1.全局热点关键词的保存规则：base_url:"spider"

2.各个爬虫项目的关键词保存规则：
"""
from string import Template

from base.utils.time import get_date

REDIS_KEYWORD = Template("spider:keyword:$platform")  # 热点爬虫保存关键字地址
REDIS_REQUEST = Template("spider:$project_name:$platform:request")  # 各个爬虫项目保存request的地址
REDIS_DUPLICATION = Template("spider:$project_name:$platform:duplication") # 各个爬虫项目的去重队列
DEFAULT_INTERVAL = 3  # 默认的爬取间隔，从3年前到现在
REDIS_SPIDER_ACC_VALID = Template("spider:$project_name:$platform:account")  # 每个爬虫项目可用的平台账户保存地址
REDIS_CUSTOM_KEYWORD = Template("spider:$project_name:custom_keyword")  # 每个爬虫项目自定义关键词保存地址


SEARCHPAGE = 10  # 每个爬虫项目搜索页数

CanRefreshCookie = ["weibo"]  # 可以刷新cookie的平台

DefaultAccount = {
    "user": "DefaultAccount",
    "password": "DefaultAccount",
    "date": get_date(),
    "valid": True
}