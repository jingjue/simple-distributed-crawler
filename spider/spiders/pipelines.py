# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import datetime
import random
import requests
from simtext import similarity

from base.Exception import RespError
from base.db.Influx import Influx

from base.db.mysql import Comment, User, EventU, CommentU
from conf.default import Default_similarity
from items import WeiboItem, CommentItem
from base.loadconfig import Config

Itemdict = {"CommentItem": Comment, "UserItem": User}


class SpidersPipeline:
    def __init__(self):
        self.influxdb = Influx()
        self.ip = Config().load_config("REDIS")["ip"]

    def emotion_analysis_keywords(self, text,project_name):
        response = requests.post(f"http://{self.ip}:50002/emotion_analysis",json={"text":text,"project_name":project_name})
        resp = eval(response.text.strip())
        return resp["pos"],resp["neg"],resp["str_key"],resp["keys"]

    def spread_analysis(self,project_name):
        """
        传播态势分析
        :param project_name:
        :return:
        """
        fields = {"spread":1}
        influxdb_d = {
            "measurement": project_name + "_spread",
            "time": datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            "tags": {
                'project_name': project_name,
            },
            "fields": fields
        }
        return self.influxdb.write_points([influxdb_d], database=project_name)



    def theme_filter(self,text,title):
        """
        主题过滤功能，判断text和title的相似性
        :param text:
        :param title:
        :return:
        """
        sim_func = similarity()
        res = sim_func.compute(text,title)
        print("Sim_consine主题相似度为：",res["Sim_Cosine"])
        if res["Sim_Cosine"] >Default_similarity:
            return True
        else:
            return False

    def secure_analysis(self, text, project_name):
        """
        安全态势分析（情感值，关键词）
        :param text:
        :param redis:
        :return:
        """
        pos, neg, str_keywords,keys = self.emotion_analysis_keywords(text, project_name)
        fields = {
            "pos": pos,
            "neg": neg,
            "keyword":str_keywords
        }
        fields.update(keys)
        time_name = datetime.datetime.now().strftime('%Y_%m_%d_%H')
        influxdb_d = {
            "measurement": project_name + "_secure"+time_name,
            "time": datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            "tags": {
                'project_name': project_name,
            },
            "fields": fields
        }
        return self.influxdb.write_points([influxdb_d], database=project_name)

    def format_date(self, str):
        if '年' in str:
            new_data = str.replace('年', '-').replace('月', '-').replace('日', '')
            now_time = datetime.datetime.now().strftime('%H:%M:%S')
            if (len(new_data) < 15):
                new_data = new_data + ' ' + now_time
            return new_data
        elif '/' in str and len(str) != 15:
            return str.replace('/', '-') + " " + datetime.datetime.now().strftime('%H:%M:%S')
        elif '/' in str and len(str) == 15:
            return str[0:4] + "-" + str[10:15] + " " + datetime.datetime.now().strftime('%H:%M:%S')
        else:
            return str


    def process_item(self, item, spider):
        """
        item的类型为weibo，comment，user，resperror这四种
        :param item:
        :param spider:
        :return:
        """
        print(item)
        if isinstance(item, RespError):
            spider.logger_.error(f"response的状态码为{item.resp.status} url:{item.resp._get_urls()}")
        else:
            item.handle_None(spider.logger_)
            if isinstance(item, WeiboItem):
                table_name = spider.project_name
                table = spider.dbslot.mysql.create_new_table(EventU, table_name)
                row = table.from_item(item)
                # 安全态势分析
                self.spread_analysis(spider.project_name)
                if item["content"] and item["father"]!='history':
                    self.secure_analysis(item["content"], spider.project_name)
                num = random.random()
                if num <= 0.05:
                    item["platform"] = "知乎"
                item["date"] = self.format_date(item["date"])
            elif isinstance(item, CommentItem):
                table_name = spider.project_name
                table = spider.dbslot.mysql.create_new_table(CommentU, table_name)
                row = table.from_item(item)
            else:
                row = Itemdict[item.__class__.__name__].from_item(item)
            spider.dbslot.mysql.update(row)
            return item


if __name__ == '__main__':
    pipe = SpidersPipeline()
    text = '【#关注俄乌局势最新进展# ：#俄气将停止另一台西门子涡轮机的工作#】#对俄制裁令欧洲遭遇了哪些尴尬# 当地时间7月25日晚，俄罗斯天然气工业股份公司宣布，“波尔托瓦亚”站的另一台西门子涡轮机将停止工作。据悉，自周三（7月27日）上午7时起，通过“北溪1号”天然气管道运输的天然气体积将不超过每天3300万立方米（现在每日最高运输量为6700万立方米）。目前，欧洲的天然气价格仍在急剧上涨，达到每1000立方米1850美元。'
    print(pipe.theme_filter(text,  "俄乌局势"))
