# -*-coding:utf-8-*- 、
# Team : upcedu.nlp
# Author：dongshou
# Date ：2021/11/1 下午3:08
# Describe ：redis 数据库操作
import json
from typing import Union
import redis
from base.loadconfig import Config


class Redis:
    def __init__(self):
        self.meta = None
        self.params = Config().load_config("REDIS")
        self.redis = redis.Redis(host=self.params["ip"], port=self.params["port"], db=self.params["db"],
                                 decode_responses=True)

    def init_redis(self):
        self.redis.lpush("hotsearch:uid", json.dumps(self.meta))

    def get(self, name):
        return self.redis.get(name)

    def get_list(self, name):
        """
        获取列表中的所有数据
        :param name:
        :return:
        """
        return self.redis.lrange(name, 0, -1)

    def set(self, name, value):
        self.redis.set(name, value)

    def insert(self, name, value: Union[list, str]):
        if isinstance(value, list):
            self.redis.rpush(name,*value)
        else:
            self.redis.rpush(name, value)

    def delete(self, name):
        """
        删除key
        :param name:
        :return:
        """
        self.redis.delete(name)

    def rm_list(self, name):
        """
        清空队列
        :param name:
        :return:
        """
        self.redis.ltrim(name, -1, 0)

    def rm_value(self, name, count, value):
        """
        count > 0 : 从表头开始向表尾搜索，移除与 VALUE 相等的元素，数量为 COUNT 。
        count < 0 : 从表尾开始向表头搜索，移除与 VALUE 相等的元素，数量为 COUNT 的绝对值。
        count = 0 : 移除表中所有与 VALUE 相等的值。
        """
        self.redis.lrem(name, count, value)

    def rm_namespace(self, namespace):
        """
        循环删除namespace中的key
        """
        keys = self.redis.keys(pattern=f'{namespace}*')
        for key in keys:
            self.delete(key)

    def sadd(self, name, *values):
        """
        向集合添加一个或多个成员
        :param name:
        :param value:
        :return:
        """
        return self.redis.sadd(name, *values)

    def smembers(self, name):
        """
        返回集合中的所有成员
        :param name:
        :return:
        """
        return self.redis.smembers(name)

    def srem(self, name, *values):
        """
        从集合中删除元素
        :param name:
        :param values:
        :return:
        """
        return self.redis.srem(name, *values)


if __name__ == '__main__':
    rdb = Redis()
    # rdb.init_redis()
    # rdb.set(str(picklecompat.dumps("中文")), '1')
    # print(picklecompat.dumps("中文"))
    # print(rdb.get(str(picklecompat.dumps("中文"))))
    # rdb.insert("spider:hotsearch_uid", '2')
    # rdb.insert("test", [1, 2, 3])
    # rdb.rm_value("test", 0, 2)
    # key = "spider:default:微博:request"

    # print(rdb.smembers("spider:keyword:微博"))
    # rdb.rm_list("spider:default:weiboyonghu:request")
    # path = "\\\\upcedu.ml\公共云盘\\nlp\model\\stopwords\\baidu_stopwords.txt"
    # s = set()
    # # with open(path,mode='r',encoding='utf-8') as f:
    # #     for line in f.readlines():
    # #         s.add(line.strip())
    # rdb.sadd("STOPWORDS",*s)
    print("转发" in rdb.smembers("STOPWORDS"))
