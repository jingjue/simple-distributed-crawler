# -*-coding:utf-8-*- 、
# Team : upcedu.nlp
# Author：dongshou
# Date ：2021/9/24 上午11:35
# Describe ：

import uuid
import socket



def get_uid_by_name(name):
    """
    根据关键字生成uid
    """
    return str(uuid.uuid3(uuid.NAMESPACE_DNS, name))


def get_host_ip():
    """
    查询本机ip地址
    :return:
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


def merge_str(str1, str2):
    """
    合并粉丝列表等
    """
    str1 = set(str1.split("/"))
    str2 = set(str2.split("/"))
    return "/".join(str1 & str2)


def load_txt(path) -> list:
    """
    读取txt文件，并返回list文件
    :param path:
    :return:
    """
    with open(path, mode='r') as f:
        lines = f.readlines()
    return [line.strip() for line in lines]


if __name__ == '__main__':
    # print(get_uid_by_name("岸田文雄当选日本第100任首相"))
    # print(merge_str("asdf/asdf", "we/asdf"))
    # print(load_txt('../../src/hot_words.txt'))
    print(get_ip_address("eth0"))