# -*- encoding: utf-8 -*-
"""
@File    : base.py
@Time    : 2021/7/12 上午10:32
@Author  : dongshou
@Describe: 日志类包含两个日志模型，一个是隐式调用，另一个为显式的调用，隐式调用通过元类来实现，显式调用必须得显式实现
@Software: PyCharm
"""
import logging

import json
import logging.config
import os
from typing import Tuple

logging.getLogger("requests").setLevel(logging.INFO)

root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
path = '/conf/log_config.json'
log_colors_config = {
    'DEBUG': 'cyan',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'red',
}


class Logger():
    def __init__(self, filedir=root, filename=None):
        with open(os.path.join(root, 'conf', 'log_config.json'), "r") as f:
            config = json.load(f)

            if filename:
                if not os.path.exists(filedir):
                    os.makedirs(filedir)
                config["handlers"]["info_file_handler"]["filename"] = os.path.join(filedir,'log', filename + "_info.log")
                config["handlers"]["error_file_handler"]["filename"] = os.path.join(filedir,'log', filename + "_error.log")
            else:
                config["handlers"]["info_file_handler"]["filename"] = os.path.join(filedir, 'log', "info.log")
                config["handlers"]["error_file_handler"]["filename"] = os.path.join(filedir, 'log', "error.log")
            # 设置颜色
            logging.config.dictConfig(config)

    def logger(self, name=None):
        return logging.getLogger(name)

    def initlog(self, who):
        """

        :param who: 表示谁调用了该模块，#要求类重定义__name__(),如果为类，则需要返回类名.方法名
        :return: 返回一个logger
        """
        name = who.__name__
        return self.logger(name)


lg = Logger()
logger = lg.logger()


def method_logger(method):
    def inner(self, *args, **kwargs):
        logger.info(f'====== Call method {method.__name__} of {self} ======')
        ret = method(self, *args, **kwargs)
        return ret

    return inner


# 日志修饰器，用于单个函数的日志操作
def func_logger(func):
    def inner(*args, **kwargs):
        logger.info(f'====== Call func {func.__name__}() ======')
        try:
            ret = func(*args, **kwargs)
            return ret
        except:
            logger.exception("")

    return inner


# 日志元类，用于类中的日志操作
class MetaLogger(type):
    def __new__(self, name: str, bases: Tuple[type], attrs: dict):
        attrs_copy = attrs.copy()
        for key, value in attrs.items():
            if callable(value) and not key.startswith('__'):
                attrs_copy[key] = method_logger(value)
        return type(name, bases, attrs_copy)


if __name__ == "__main__":
    mainlog = lg.logger("mainlogger")
    mainlog.info("test")
