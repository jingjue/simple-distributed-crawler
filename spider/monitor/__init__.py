"""
监控程序

可升级的地方：考虑使用aiohttp来爬取热点和检索爬虫,速度快
"""
import math
import os.path
import threading

import pinyin
import rsa
from loguru import logger
import portion as P

from base.utils.time import get_date, get_last_time_str
from monitor.setting import DEFAULT_INTERVAL

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
filename = os.path.basename(__file__)[0:-3]

logger.add(os.path.join(root, "log/run", "info-{time:YYYY-MM-DD}.log"),
           filter=lambda record: "INFO" in record['level'].name, rotation="4000KB", encoding="utf-8", enqueue=True)
logger.add(os.path.join(root, "log/run", "error-{time:YYYY-MM-DD}.log"),
           filter=lambda record: "ERROR" in record['level'].name, rotation="200KB", encoding="utf-8", backtrace=True,
           diagnose=True, enqueue=True)


class SignalInstance(type):
    """
    单例模式，未加锁部分并发执行,加锁部分串行执行,速度降低,保证了数据安全
    """
    _instance_lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            with SignalInstance._instance_lock:
                if not hasattr(cls, "_instance"):
                    cls._instance = super(SignalInstance, cls).__call__(*args, **kwargs)
        return cls._instance


class TimeSection:
    """
    爬虫时间区间
    """

    def __init__(self, start=None, end=None):
        if not end:
            end = get_date()
        if not start:
            start = get_last_time_str(DEFAULT_INTERVAL * 365)
        self.section = P.closed(start, end)

    def __and__(self, other):
        new_section = self.section & other.section
        return TimeSection(new_section.lower, new_section.upper)

    def __or__(self, other):
        new_section = self.section | other.section
        return TimeSection(new_section.lower, new_section.upper)

    @property
    def start(self):
        return self.section.lower

    @property
    def end(self):
        return self.section.upper

    def to_dict(self):
        return {"start": self.start, "end": self.end}

    def __contains__(self, other):
        return other in self.section


def create_keys():  # 生成公钥和私钥
    (pubkey, privkey) = rsa.newkeys(1024)
    pub = pubkey.save_pkcs1()
    with open('../conf/public.pem', 'wb+')as f:
        f.write(pub)

    pri = privkey.save_pkcs1()
    with open('../conf/private.pem', 'wb+')as f:
        f.write(pri)


def encryption(text):
    """
    pass
    """
    with open(os.path.join(root, 'conf', 'public.pem'), 'rb') as publickfile:
        p = publickfile.read()
    pubkey = rsa.PublicKey.load_pkcs1(p)
    original_text = text.encode('utf8')
    crypt_text = rsa.encrypt(original_text, pubkey)
    return str(int.from_bytes(crypt_text, 'big'))  # 加密后的密文


def decrypt(text):
    """
    pass
    """
    text = int(text)
    bytes_required = max(1, math.ceil(text.bit_length() / 8))
    text = text.to_bytes(bytes_required, "big")
    with open(os.path.join(root, 'conf', 'private.pem'), 'rb') as privatefile:
        p = privatefile.read()
    privkey = rsa.PrivateKey.load_pkcs1(p)
    lase_text = rsa.decrypt(text, privkey).decode()
    return lase_text


def to_unicode(text, encoding=None, errors='strict'):
    """Return the unicode representation of a bytes object ``text``. If
    ``text`` is already an unicode object, return it as-is."""
    if isinstance(text, str):
        return text
    if not isinstance(text, (bytes, str)):
        raise TypeError('to_unicode must receive a bytes or str '
                        f'object, got {type(text).__name__}')
    if encoding is None:
        encoding = 'utf-8'
    return text.decode(encoding, errors)


def convert_to_pinyin(text):
    """
    判断是否是汉字，是汉字转为拼音，否则返回原值
    :return:
    """
    return pinyin.get(text, format="strip")


if __name__ == '__main__':
    t1 = TimeSection("2020-01-01 23:23", "2021-10-10")
    t2 = TimeSection("2020-01-01 23:23", "2021-01-10")
    print((t1 | t2).to_dict())
    print(root)
