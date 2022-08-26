# -*- encoding: utf-8 -*-
"""
@File    : loadconfig.py
@Time    : 2021/8/7 下午5:08
@Author  : dongshou
@Describe: None
@Software: PyCharm
"""
import configparser
import os


root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


# 导入 configparser包
class BasicConfig(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=defaults)

    def optionxform(self, optionstr):
        return optionstr


class Config():
    def __init__(self, config_dir='conf/db.ini'):
        self.config_dir = self.abs_config_dir(config_dir)

    def abs_config_dir(self, config_dir):
        abs_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if 'conf' in config_dir:
            abs_conf_dir = os.path.join(abs_dir, config_dir)  # 配置文件存放地址,在linux一般采用绝对路径，相对路径会报错
        else:
            abs_conf_dir = os.path.join(abs_dir, 'conf', config_dir)
        return abs_conf_dir

    def num(self, value: str):
        """
        尝试转number
        """
        if value.isdigit():
            return eval(value)
        else:
            return value

    def load_config(self, section="MYSQL", filename=None):
        """
        获取配置信息
        :param section: 配置文件中的section name
        :return:  该section下的所有键值对，{key:value,.....}
        """
        cf = BasicConfig()
        if not filename:
            cf.read(self.config_dir, encoding='utf-8')
        else:
            cf.read(self.abs_config_dir(filename), encoding='utf-8')
        try:
            info_list = cf.items(section)  # 返回的数据为list，[(key,value),....]
            info_dict = {value[0]: self.num(value[1]) for value in info_list}  # 构造成字典的格式
            return info_dict
        except:
            return {}

    def write(self, filename=None, **info):
        """

        **info 需要更改信息，{section:{key:value},...}
        """
        cf = BasicConfig()
        filedir = self.abs_config_dir(filename)
        cf.read(filedir, encoding='utf-8')
        for section, conf in info.items():
            for key, value in conf.items():
                cf.set(section, key, value)
        with open(filedir, mode='w') as f:
            cf.write(f)
        return True


if __name__ == '__main__':
    config = Config()
    print(config.load_config())
