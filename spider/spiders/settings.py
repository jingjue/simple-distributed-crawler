# Scrapy settings for spiders project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
from core.scheduler import Scheduler
from core.duplication import RFPDupeFilter
from base.loadconfig import Config

BOT_NAME = 'spiders'

SPIDER_MODULES = ['spiders.spiders']
NEWSPIDER_MODULE = 'spiders.spiders'

SCHEDULER_QUEUE_KEY = 'spider:%(project_name)s:%(platform)s:request'
SCHEDULER_DUPEFILTER_KEY = "spider:%(project_name)s:%(platform)s:duplication"

REDIS_START_URLS_AS_SET = False
# Obey robots.txt rules
ROBOTSTXT_OBEY = False
RANDOMIZE_DOWNLOAD_DELAY = True
DOWNLOAD_DELAY = 2

SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.SpiderQueue'
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'spiders.middlewares.SpidersSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    'spiders.middlewares.SpidersDownloaderMiddleware': 543,
# }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
MYEXT_ENABLED = False  # 开启扩展
IDLE_NUMBER = 360  # 配置空闲持续时间单位为 360个 ，一个时间单位为5s
EXTENSIONS = {
    # 'scrapy.extensions.telnet.TelnetConsole': None,
    'spiders.extensions.SpiderStatLogging': 1,
    # 'spiders.extensions.RedisSpiderSmartIdleClosedExensions':500
}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    # 'scrapy_redis.pipelines.RedisPipeline': 300,
    'spiders.pipelines.SpidersPipeline': 300,
}
COOKIES_ENABLED = False

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

SCHEDULER = Scheduler
DUPEFILTER_CLASS = RFPDupeFilter
redis_config = Config().load_config("REDIS")
REDIS_HOST = redis_config["ip"]
REDIS_PORT = redis_config["port"]
HTTPERROR_ALLOWED_CODES = [400]

LOG_LEVEL = "INFO"
LOG_FILE = "log/sys.log"

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'spiders.middlewares.SpidersDownloaderMiddleware': 300
}
# LOG_LEVEL = 'DEBUG'
# DUPEFILTER_DEBUG = True
# SCHEDULER_FLUSH_ON_START = True
