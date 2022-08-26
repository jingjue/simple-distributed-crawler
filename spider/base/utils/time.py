# -*-coding:utf-8-*- 、
# Team : upcedu.nlp
# Author：dongshou
# Date ：2021/9/24 上午11:35
# Describe ：
import os
import time
import datetime
import random
from loguru import logger
root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


def get_date():
    return get_time().strftime("%Y-%m-%d %H:%M:%S")


def str_to_datetime(string):
    return datetime.datetime.strptime(string, "%Y-%m-%d %H:%M:%S")


def gen_id():
    return get_date() + str(random.randint(0, 10000))


def get_time():
    return datetime.datetime.now()


def get_last_time(day=1):
    """
    获取一段时间以前的日期
    :param day:
    :return:
    """
    return get_time() - datetime.timedelta(days=day)

def get_last_time_str(day=1):
    return (get_time() - datetime.timedelta(days=day)).strftime("%Y-%m-%d %H:%M:%S")


def build_path():
    '''
    路径生成模块
    返回path，即md文件最终路径
    '''
    # 解决存储路径
    time_name = time.strftime('%Y{y}%m{m}%d{d}%H{h}', time.localtime()).format(y='年', m='月', d='日', h='点')
    year_path = time.strftime('%Y{y}', time.localtime()).format(y='年')
    month_path = time.strftime('%m{m}', time.localtime()).format(m='月')
    all_path = root + f"/keywords/" + year_path + '/' + month_path
    if not os.path.exists(all_path):
        # 创建多层路径
        os.makedirs(all_path)
    # 最终文件存储位置
    root_ = all_path + "/"
    path = root_ + time_name + '.csv'
    return path


def zh_time_change(time):
    """
    9月25日 22:23 时间格式变换
    :param time:
    :return:
    """
    try:
        month = int(time.split("月")[0])
        day = int(time.split("月")[1].split("日")[0])
        handler = time.split(" ")[1].split(":")
        year = get_time().year
        return datetime.datetime(year=year, month=month, day=day, hour=int(handler[0]), minute=int(handler[1]))
    except Exception as e:
        logger.exception(f"E 时间解析错误{e}")

def gelin_time_change(time):
    """
    Sat Sep 25 13:28:26 +0800 2021
    """
    return datetime.datetime.strptime(time, '%a %b %d %H:%M:%S %z %Y').strftime("%Y-%m-%d %H:%M:%S")


def get_time_num():
    """
    获取当前时间戳
    :return:
    """
    return int(datetime.datetime.timestamp(get_time()))


def get_age(time):
    """
    1977-02-18 水瓶座
    """
    time = time.split(" ")[0]
    age = datetime.datetime.now() - datetime.datetime.strptime(time, "%Y-%m-%d")
    return age


def people_time_change(time):
    """
    处理人民网时间数据格式
    "
					2021年10月04日15:52 | 来源："
    """
    time = time[1:-1].strip().split("|")[0].strip()
    return datetime.datetime.strptime(time, "%Y年%m月%d日%H:%M").strftime("%Y-%m-%d %H:%M:%S")


def qiushi_time_change(time):
    """
    处理qiushi网时间数据格式
    "

    """
    return datetime.datetime.strptime(time, "%Y年%m月%d日 %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")


def zhihu_time_change(time):
    """
    处理知乎的时间，时间格式存在两种情况，“2015-01-29 14:20” “10-19 03:23”
    :param time:
    :return:
    """
    num = time.count("-")
    if num == 1:  # “10-19 03:23”
        new_time = datetime.datetime.strptime(time, "%m-%d %H:%M")
        new_time = new_time.replace(year=datetime.datetime.now().year, second=0).strftime("%Y-%m-%d %H:%M:%S")
    elif num == 2:

        new_time = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M").strftime("%Y-%m-%d %H:%M:%S")
    else:
        new_time = get_date()
    return new_time


def baidu_time_change(time):
    """
    处理知乎的时间，时间格式存在两种情况，“2015-01-29 14:20” “10-19 03:23”
    :param time:
    :return:
    """
    num = time.count("-")
    if num == 1:  # “10-19 03:23”
        new_time = datetime.datetime.strptime(time, "%m-%d %H:%M")
        new_time = new_time.replace(year=datetime.datetime.now().year, second=0).strftime("%Y-%m-%d %H:%M:%S")
    elif num == 2:
        time = "20" + time
        new_time = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M").strftime("%Y-%m-%d %H:%M:%S")
    else:
        new_time = get_date()
    return new_time


def people_time_from_url(url):
    """
    http://env.people.com.cn/n1/2019/0801/c1010-31268730.html
    :param url:
    :return:
    """
    try:
        result = url.split(".cn/")[1].split("/")
        if 'n2' in url:
            result = url.split("n2/")[1].split("/")
        elif 'n1' in url:
            result = url.split("n1/")[1].split("/")
        year = int(result[0])
        month = int(result[1][0:2])
        day = int(result[1][2:])
        time = datetime.datetime(year, month, day)
        return time
    except:
        logger.error(f"【url error】url:{url}")
        return False


def get_delta_time(time1):
    """
    获取time1与现在时间的差值
    :param time1: 默认单位为day
    :return:day
    """
    try:
        if isinstance(time1, str):
            time1 = str_to_datetime(time1)
        now = get_time()
        return (now - time1).days
    except Exception as e:
        logger.exception(f"E 时间差计算错误{e}")


def to_datetime(time):
    if not time or time == "not acquired":
        return False
    elif "月" in time:
        return qiushi_time_change(time)
    else:
        num = time.count(":")
        if num == 1:
            format = "%Y-%m-%d %H:%M"
        else:
            format = "%Y-%m-%d %H:%M:%S"
        return datetime.datetime.strptime(time.split(".")[0], format)

if __name__ == '__main__':
    # url = "http://env.people.com.cn/n1/2019/0801/c1010-31268730.html"
    # time1 = people_time_from_url(url)
    # print(get_delta_time(time1))
    # print(build_path())
    # print(str(gen_id()))
    # print(to_datetime("2010-07-28 09:15:15"))
    # print(gelin_time_change("Mon Feb 07 18:25:46 +0800 2011"))
    a = get_date()
    print(a)
    print(str(get_time()))
    b = str(get_date())
    print((to_datetime(a)-to_datetime(b)).days)
