# Name:         Influx
# Description:  时序数据库，用来保存爬虫运行过程中的状态
# Author:       东寿
# Date:         2022/4/18

from __future__ import unicode_literals

from influxdb import InfluxDBClient
import sys
sys.path.append("/home/spiders")
from base.loadconfig import Config


class Influx:
    def __init__(self):
        self.params = Config().load_config("INFLUX")
        self.client = InfluxDBClient(host=self.params["ip"], port=self.params["port"], username=self.params["username"],
                                     password=self.params["password"])

    def create_db(self, db_name):
        self.client.create_database(db_name)
        # 更改保存策略
        self.client.create_retention_policy("default", self.params["duration"], '1', default=True, database=db_name)

    def write_points(self, points, database):
        return self.client.write_points(points, database=database)

    def query(self, sql, database):
        return self.client.query(sql, database=database)


if __name__ == '__main__':
    data = {'measurement': '微博', 'time': '2022-04-18T13:30:38Z',
            'tags': {'spider_name': '微博', 'project_name': 'default', 'device': '180.201.129.166'},
            'fields': {'log_info': 11, 'dequeued': 20, 'log_warning': 0,
                       'requested': 20, 'request_bytes': 32560, 'response': 4, 'response_bytes': 13478,
                       'response_200': 4, 'response_301': 0, 'response_404': 0, 'response_num': 4, 'item': 22,
                       'depth': 1, 'filtered': 0, 'enqueued': 12, 'spider_name': '微博'}
            }

    influx = Influx()
    # influx.write_points([data],"default")
    # influx.create_db("")
    # print(influx.client.create_retention_policy("default", '15d', '1', default=True, database="test"))
    # print(influx.client.get_list_retention_policies(database='default'))
    # print(influx.client.alter_retention_policy(''))
    # print(influx.query('SHOW TAG KEYS FROM "微博"',"default"))
    # r = influx.query('SELECT LAST(end_time),reason FROM "微博_closed"', 'default')
    # print(list(r.get_points("微博_closed",None)))
    # data = pd.DataFrame(list(r.get_points("微博_closed",None)))
    # data["time"] =data["time"].apply(lambda x:x[0:-4].replace("T"," ")+":00")
    # sql = 'SELECT * FROM "eWuChongTu_secure"
    sql = 'DELETE eWuChongTu_secure'
    # influx.client.
    results = influx.query(sql, database="default")
    print(results)


