# -*-coding:utf-8-*- 、
# Team : upcedu.nlp
# Author：dongshou
# Date ：2021/9/25 上午11:02
# Describe ：配置全局数据库管理
from base.db.Influx import Influx
from base.db.mysql import Mysql
from base.db.redis_ import Redis


class Slot:
    def __init__(self, mysql: Mysql, redis: Redis = None, neo4j=None, influx: Influx = None):
        """

        :param kwargs:
        """
        self.mysql = mysql
        self.redis = redis
        self.neo4j = neo4j
        self.influx = influx


dbslot = Slot(Mysql(), Redis())
