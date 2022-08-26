# -*-coding:utf-8-*- 、
# Team : upcedu.nlp
# Author：dongshou
# Date ：2021/9/23 下午8:54
# Describe ：

import inspect
import os
import sys

import loguru

sys.path.append('/home/users/CT/pycharmproject/spiders/')
import pandas as pd
from sqlalchemy import Column, String, create_engine, Integer, Float, Boolean, DateTime, Text, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base, AbstractConcreteBase
import datetime
from base.loadconfig import Config
from base.utils import merge_str
from base.utils.time import get_time, to_datetime

Base = declarative_base()
root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


class EventU(AbstractConcreteBase, Base):
    __abstract__ = True
    __tablename__ = 'content'
    account = Column(String(50))
    weibo_id = Column(String(50), primary_key=True)
    mid = Column(String(50))
    uid = Column(String(50))
    content = Column(Text)
    father = Column(String(100))
    likes = Column(Integer)
    retweet = Column(Integer)  # 转发
    comment = Column(Integer)
    comment_list = Column(Text)  # 评论
    retweet_list = Column(Text)
    like_list = Column(Text)
    title = Column(String(100))
    hot = Column(Float)
    date = Column(String(50))  # 微博日期
    now_date = Column(String(50))  # 给当天得时间
    platform = Column(String(50))

    @classmethod
    def get_primary_key(cls):
        return cls.weibo_id

    def tolist(self):
        return [getattr(self, key.name) for key in self.__table__.columns]
        # return [self.account, self.uid, self.comtent, self.likes, self.retweet, self.comment, self.comment_list,
        #         self.retweet_list, self.title, self.hot, self.date, self.event_date, self.platform]

    def todict(self):
        """
        将数据转为dict
        :return:
        """
        params = {}
        for name in self.__table__.columns:
            params[name.name] = getattr(self, name.name)
        return params

    def get_by_id(self, session):
        cls = self.__class__
        result = session.query(cls).filter(cls.weibo_id == self.weibo_id)
        # session.commit()
        return result

    def to_dict(self):
        return self.todict()

    def merge(self, other):
        if isinstance(other, Event):
            if self.like_list != 'None' or self.like_list:
                other.like_list = merge_str(self.like_list, other.like_list)
            if self.comment_list != 'None' or self.comment_list:
                other.comment_list = merge_str(self.comment_list, other.comment_list)
            if self.retweet_list != 'None' or self.retweet_list:
                other.retweet_list = merge_str(self.retweet_list, other.retweet_list)
            return other
        else:
            return other

    @classmethod
    def from_item(cls, item):
        """
        从item实例化Event()
        :param item:
        :return:
        """
        params = {}
        for key in cls.__table__.columns:
            params[key.name] = item[key.name]
        if isinstance(params["retweet_list"], list):
            params["retweet_list"] = "/".join(map(str, params["retweet_list"]))
        if isinstance(params["comment_list"], list):
            params["comment_list"] = "/".join(map(str, params["comment_list"]))
        return cls(**params)


class Event(EventU):
    __tablename__ = 'content'
    __mapper_args__ = {'polymorphic_identity': 'wukelan_content', 'concrete': True}


class CommentU(AbstractConcreteBase, Base):
    __tablename__ = 'comment'
    __abstract__ = True
    mid = Column(String(50))
    weibo_id = Column(String(50), primary_key=True)
    account = Column(String(50))
    uid = Column(String(50), primary_key=True)  # uid
    date = Column(String(50))  # 微博日期
    now_date = Column(String(50))  # 给当天得时间
    content = Column(Text)
    likes = Column(Integer)

    @classmethod
    def from_item(cls, item):
        """
        从item实例化Event()
        :param item:
        :return:
        """
        params = {}
        for key in cls.__table__.columns:
            params[key.name] = item[key.name]
        return cls(**params)

    def todict(self):
        """
        将数据转为dict
        :return:
        """
        params = {}
        for name in self.__table__.columns:
            params[name.name] = getattr(self, name.name)
        return params

    def to_dict(self):
        return self.todict()

    def get_by_id(self, session):
        cls = self.__class__
        result = session.query(cls).filter(cls.weibo_id == self.weibo_id, cls.uid == self.uid)
        # session.commit()
        return result

    @classmethod
    def get_primary_key(cls):
        return cls.weibo_id, cls.uid


class Comment(CommentU):
    __tablename__ = 'wukelan_content'
    __mapper_args__ = {'polymorphic_identity': 'wukelan_content', 'concrete': True}


class User(Base):
    __tablename__ = 'users_raw'
    account = Column(String(50))
    uid = Column(String(50), primary_key=True)  # uid
    location = Column(String(10))
    follows = Column(Integer)  # 关注数量
    follow_list = Column(Text)
    fan_list = Column(Text)
    fans = Column(Integer)
    gender = Column(String(10))  # 性别
    brief = Column(String(1000))
    label = Column(String(100))
    verified = Column(String(10))  # 是否认证
    user_friend = Column(Integer)
    all_content = Column(Integer)
    history_weibo = Column(Text)
    credit = Column(String(10))
    career = Column(String(10))
    education = Column(String(20))
    age = Column(String(20))
    create_at = Column(String(50))  # 创建时间

    def tolist(self):
        gender = 0 if self.gender == 'm' else 1
        longtime = (datetime.datetime.strptime(self.created_at, "%Y-%m-%d-%H:%M:%S") - datetime.datetime.strptime(
            '2000-1-1-0:0:0', "%Y-%m-%d-%H:%M:%S")).days
        return [float(self.city), float(eval(self.verified)), float(self.followers_count), float(self.province),
                float(self.friends_count), float(gender), float(longtime), float(self.verified_type)]

    def todict(self):
        """
        将数据转为dict
        :return:
        """
        params = {}
        for name in self.__table__.columns:
            params[name.name] = getattr(self, name.name)
        return params

    def to_dict(self):
        return self.todict()

    @classmethod
    def from_item(cls, item):
        """
        从item实例化Event()
        :param item:
        :return:
        """
        params = {}
        for key in cls.__table__.columns:
            params[key.name] = item[key.name]
        return cls(**params)

    def get_by_id(self, session):
        cls = self.__class__
        result = session.query(cls).filter(cls.uid == self.uid)
        # session.commit()
        return result

    def merge(self, other):
        """
        合并操作
        :param other:
        :return:
        """
        if isinstance(other, User):
            if self.fan_list != 'None' or self.fan_list:
                other.fan_list = merge_str(self.fan_list, other.fan_list)
            if self.follow_list != 'None' or self.follow_list:
                other.follow_list = merge_str(self.follow_list, other.follow_list)
            if self.history_weibo != 'None' or self.history_weibo:
                other.history_weibo = merge_str(self.history_weibo, other.history_weibo)
            return other
        else:
            return other

    @classmethod
    def get_primary_key(cls):
        return cls.uid


class Device(Base):
    __tablename__ = "device"
    server_id = Column(String(50), primary_key=True)
    ip = Column(String(30))
    username = Column(String(50))
    password = Column(Text)
    address = Column(String(100))
    port = Column(Integer)
    valid = Column(Boolean())

    @classmethod
    def get_primary_key(cls):
        return cls.ip

    @classmethod
    def from_item(cls, item):
        """
        从item实例化Event()
        :param item:
        :return:
        """
        params = {}
        for key in cls.__table__.columns:
            params[key.name] = item[key.name]
        return cls(**params)

    def to_dict(self):
        """
        将数据转为dict
        :return:
        """
        params = {}
        for name in self.__table__.columns:
            params[name.name] = getattr(self, name.name)
        return params

    def get_by_id(self, session):
        cls = self.__class__
        result = session.query(cls).filter(cls.server_id == self.server_id)
        # session.commit()
        return result

    def merge(self, other):
        return other

    def todict(self):
        return self.to_dict()


class Cookie(Base):
    __tablename__ = "cookie"
    id = Column(Integer, primary_key=True)
    cookie = Column(Text)
    user = Column(String(50))
    password = Column(String(50))
    platform = Column(String(50))
    date = Column(DateTime())  # 创立时间
    valid = Column(Boolean())

    @classmethod
    def get_primary_key(cls):
        return cls.id

    @classmethod
    def sql(cls):
        return "select * from cookie"

    def tolist(self):
        return [self.cookie, self.platform, self.date, self.valid]

    def to_dict(self):
        """
        将数据转为dict
        :return:
        """
        params = {}
        for name in self.__table__.columns:
            params[name.name] = getattr(self, name.name)
        return params

    def __getitem__(self, item):
        return getattr(self, item)

    def valify(self):
        """
        检查cookie的有效性
        :return:
        """
        return self.valid

    def get_by_id(self, session):
        cls = self.__class__
        result = session.query(cls).filter(cls.id == self.id)
        # session.commit()
        return result

    def merge(self, other):
        return other


class Mysql:
    def __init__(self, logger=None):
        self.logger = logger
        params = Config().load_config()
        self.engine = create_engine(
            f'mysql+pymysql://{params["user"]}:{params["password"]}@{params["host"]}:{params["port"]}/{params["db_name"]}?charset=utf8&autocommit=true')

        self.session = sessionmaker(bind=self.engine)()
        self.tables = {}
        self.register_table()

    def create_session(self):
        return sessionmaker(bind=self.engine)()

    def register_table(self):
        for name, cls in inspect.getmembers(sys.modules[__name__], inspect.isclass):
            if cls.__base__.__name__ in ["Meta", "Base", "EventU"]:
                self.tables[name] = cls

    def update(self, data):
        """
        如果存在则更新,不存在直接插入
        :param data:
        :return:
        """
        errors = {}
        try:
            if isinstance(data, Base):
                session = self.create_session()
                row = data.get_by_id(session)
                if row.all():
                    new = row.first().merge(data).to_dict()
                    row.update(new)
                else:
                    session.add(data)
                session.commit()
                session.close()
                return errors
            elif isinstance(data, list):
                for item in data:
                    errors.update(self.update(item))
                return errors
        except Exception as e:
            if isinstance(data, Base):
                errors[str(data.__class__)] = data.to_dict()
            self.logger.exception(f"【mysql更新数据出错】")
            session.rollback()
            return errors

    def rm_data(self, table, key, value):
        """
        只能单个数据进行删除
        """
        errors = {}
        session = self.create_session()
        if isinstance(table, str):
            if table in self.tables.keys():
                table = self.tables[table]
            else:
                self.logger.error(f"【表错误】 不存在表{table}")
                errors["table_error"] = f"不存在表{table}"

        if isinstance(key, str):
            if hasattr(table, key):
                key = getattr(table, key)
            else:
                self.logger.error(f"【类属性错误】{table}中没有属性{key}")
                errors["key_error"] = f"【类属性错误】{table}中没有属性{key}"
        session.query(table).filter(key == value).delete()
        session.commit()
        session.close()
        return errors

    def save(self, data):
        session = self.create_session()
        try:
            if isinstance(data, Base):
                session.add(data)
                session.commit()
                self.logger.info(f"【MYSQL】保存数据到表{data.__tablename__}")
            elif isinstance(data, list):
                for item in data:
                    session.add(item)
                session.commit()
                self.logger.info(f"【MYSQL】保存多种数据")
        except:
            session.rollback()
            session.close()
            self.logger.exception(f"【mysql保存出错】{data.__tablename__}")
        finally:
            session.close()

    def get_all_sorted_by_date(self, table):
        """
        获取表中的所有数据
        :param table:
        :return:
        """
        return self.execute(f"select * from {table} order by `date` ASC ", )

    def query(self, table, key, value):
        """
        要检索的键名和值
        table:要检索的表所属类的名称，即关键字class后面的字符
        :param key:
        :param value:
        :return:
        """
        session = self.create_session()
        if isinstance(table, str):
            if table in self.tables.keys():
                table = self.tables[table]
            else:
                self.logger.error(f"【表错误】 不存在表{table}")
                exit(0)
        if isinstance(key, str):
            if hasattr(table, key):
                key = getattr(table, key)
            else:
                self.logger.error(f"【类属性错误】{table}中没有属性{key}")
                exit(0)
        data = session.query(table).filter(key == value).all()
        session.close()
        if data:
            return data
        else:
            return []

    def exit(self, table_name):
        """
        判断数据库中是否存在该表
        :param table_name:
        :return:
        """

        return self.engine.dialect.has_table(self.engine.connect(), table_name)

    def normalize_date(self, row):
        time = to_datetime(row["date"])
        if not time:
            return row["now_date"]
        else:
            return time

    def sql2csv(self, table, dirs="/src/data/"):
        dataframe = pd.read_sql(sql=f"select * from {table}", con=self.engine)
        if "hot" in dataframe.columns:
            dataframe = dataframe.drop(labels="hot", axis=1)
        if table == "content":
            dataframe["date"] = dataframe.apply(self.normalize_date, axis=1)
            dataframe = dataframe.sort_values(by="date", ascending=True)
        dataframe.to_csv(root + dirs + "news_raw.csv", index=False)
        self.alter_table_name(table)

    def alter_table_name(self, table_name):
        """
        table:cls 表类 或者str
        :param table:
        :return:
        """
        # 更改表名,建新表
        new_table_name = table_name + '_' + str(get_time()).split(' ')[0].replace('-', '_') + '_' + \
                         str(get_time()).split(' ')[1].replace(':', '_').replace('.', '_')
        sql = f"alter table {table_name} rename to {new_table_name}"
        self.session.execute(sql)
        if "_" in table_name and table_name != 'users_raw':
            info = table_name.split("_")
            self.create_new_table(eval(info[1]), info[0])
        else:
            self.create_all()

    def create_all(self):
        Base.metadata.create_all(self.engine)

    def execute(self, sql):
        session = self.create_session()
        result = session.execute(sql)
        session.close()
        return result.all()

    def get_all_cookie(self):
        cookies = self.session.query(Cookie).all()
        valid_cookies = []
        for cookie in cookies:
            if cookie.valid:
                valid_cookies.append(cookies)
        return valid_cookies

    def get_all_account(self):
        """
        无效cookie也返回
        """
        session = self.create_session()
        cookies = session.query(Cookie).all()
        session.close()
        return cookies

    def query_cookie(self, table, key, value):
        cookies = self.query(table, key, value)
        if cookies:
            valid_cookie = []
            for cookie in cookies:
                if cookie.valid:
                    valid_cookie.append(cookie)
            return valid_cookie
        else:
            return cookies

    def commit(self):
        self.session.commit()

    def query_device(self):
        session = self.create_session()
        res = session.query(Device).all()
        session.close()
        return res

    def update_cookie(self, account: dict):
        """
        如果存在，则更新，否则直接插入
        """
        msg = True
        session = self.create_session()
        current_account = session.query(Cookie).filter(Cookie.id == account.get("id", None)).first()
        if current_account:
            id = account["id"]
            account.pop("id")
            session.query(Cookie).filter(Cookie.id == id).update(account)
        else:
            if len(account) < 6:
                msg = f"{account['platform']} {account['user']}账户信息不完整"
            else:
                session.add(Cookie(**account))
                msg = f"{account['platform']} {account['user']}账户添加成功"
        session.commit()
        session.close()
        return msg

    def delete_one_row(self, table_name, primary_key):
        """
        删除一条数据,不存在也返回true
        :param table:
        :param key:
        :param value:
        :return:
        """
        session = self.create_session()
        table = self.tables.get(table_name, None)
        if table:
            session.query(table).filter(table.get_primary_key() == primary_key).delete()
            session.commit()
            session.close()
            return True, f"{table_name}删除成功 {primary_key}"
        else:
            session.close()
            return False, f"{table_name}表不存在"

    def create_new_table(self, raw_table, table_name):
        """
        创建新表
        :param raw_table_name: 原始表 类
        :param table_name:
        :return:
        """
        table_name = table_name + '_' + str(raw_table.__name__)
        if not self.tables.get(table_name, False):
            table = type(table_name, (raw_table,), {"__tablename__": table_name,
                                                    "__mapper_args__": {"polymorphic_identity": table_name,
                                                                        'concrete': True},
                                                    '__table_args__': {'extend_existing': True}})
            self.tables[table_name] = table

        if not self.exit(table_name):
            self.create_all()  # 在数据库中创建对应的表
        return self.tables[table_name]


if __name__ == '__main__':
    # cookie = Cookie(
    #     cookie='SINAGLOBAL=9799284069437.23.1632574449347; UOR=,,www.baidu.com; XSRF-TOKEN=yXbDtVELnWPVZdJ60g_9bfXv; login_sid_t=948fbd293f5a56a23394ac5304dafa39; cross_origin_proto=SSL; _s_tentry=weibo.com; Apache=2394637346175.228.1637284929169; ULV=1637284929175:20:5:4:2394637346175.228.1637284929169:1636701434918; wb_view_log=1920*10801; WBtopGlobal_register_version=2021111909; ALF=1668823561; SSOLoginState=1637287562; SCF=AuNgJvnLTVwnuZ9uO6iasjhdOpM7dKqO-Fp-JtPuPjkIk3d1WKhvMLnKSQm5mcTyw5CyKj-94GjzAo2BTjJAumo.; SUB=_2A25Mk3baDeRhGeFJ61UW-CjEyTuIHXVv6e8SrDV8PUNbmtAKLW34kW9NfLnItkRvrVPjM8BgJJQNtAv2ydzypfPW; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9Wh7KBKaeHAZnm-HHBzVH5H-5JpX5KzhUgL.FoMNehMN1hqReoM2dJLoIpnLxK-L1hqLB-eLxK-L1h-LB.xke0qX1h-t; WBPSESS=Dt2hbAUaXfkVprjyrAZT_Hg7Tr54UkM3fKJSb-LnCDf5WB_ixvGc1IkwjEGbByIgS68ANX3Uoj4Bir9rFaSpm99739MvATGdL7zNiXmjau0xiPT3tPP_5h-zOcQ4wmVciZpHtyfBSnr2T9z3Na6wlrsmD4V3cP3XxqUzkuAtG-cCR_0sPaXpigcTJCPqOw5k05WPQax-rAanAXQHiCLNVg==',
    #     platform="weibo", date=get_time(), valid=True, user="ct", password="None")
    # # print(cookie)
    # params = {'account': '中国蓝新闻', 'weibo_id': 'KCvYZ0169', 'mid': 4691794090004225, 'uid': 2286092114,
    #           'content': '【震撼！#绍兴超万只白鹭山头翩翩起舞#】10月12日，超一万只白鹭在绍兴市上虞区陈溪乡中心小学后山附近翩翩起舞练绿水青山美好生态的大合唱，演绎出秋水共长天一色的壮丽美景。经专家鉴 \u200b\u200b\u200b',
    #           'father': 0, 'likes': 0, 'retweet': 0, 'comment': 0, 'comment_list': '', 'retweet_list': '',
    #           'title': '共同构建地球生命共同体', 'hot': 0, "date": '2021-10-13 11:19:13', 'platform': 'not acquired'}
    #
    # comment = {'account': '笃笃go',
    #            'content': '长得好像刘亦菲',
    #            'date': '2021-10-13 16:30:52',
    #            'likes': 0,
    #            'mid': '4691875917989690',
    #            'now_date': '2021-10-13 16:34:00',
    #            'uid': 5840431001,
    #            'weibo_id': '1855816273/KCxVQrd7r'}
    # user = {'account': '医药赋哥1963',
    #         'age': 'None',
    #         'all_content': 0,
    #         'brief': '药品监管，外科医生，稽查打假。',
    #         'career': 'None',
    #         'create_at': '2012-06-11 18:57:08',
    #         'credit': '80',
    #         'education': 'None',
    #         'fan_list': '',
    #         'fans': 4621,
    #         'follow_list': '',
    #         'follows': 0,
    #         'gender': 'm',
    #         'history_weibo': 'None',
    #         'label': '',
    #         'location': '湖南',
    #         'uid': '2807283631',
    #         'user_friend': 20000,
    #         'verified': False}
    #
    # m = Comment(**comment)
    # u = User(**user)
    #
    # # e = Event(**params)
    # # print(e.__table__.columns)
    # mysql = Mysql()
    # # print(mysql.delete_one_row("Cookie",17))
    # print(mysql.query("Cookie", "platform", "微博"))
    # print([cookie.to_dict() for cookie in mysql.get_all_account()],sep='\n')
    # print(mysql.update_cookie(cookie.to_dict()))
    # table = mysql.create_new_table(EventU, "default_spider")
    # Base.metadata.create_all(mysql.engine)
    # print(Base.metadata.tables)
    # mysql.create_all()
    # mysql.alter_table_name(User)
    # print(mysql.query_cookie("Cookie","platform","weibo"))
    # mysql.update(u)
    # mysql.sql2csv(table="content")
    # mysql.sql2csv("users_raw")
    # mysql.create_all()
    # print(mysql.tables)
    # mysql.create_table(Cookie.__name__)
    # mysql.save(cookie)
    # for name in Event.__table__.columns:
    #     print(type(name.name))
    # print(mysql.query("User", "uid", 2807283631))
    # print(mysql.session.query(Cookie).all())
    # print(mysql.execute(Cookie.sql()))
    # print(mysql.query(Cookie, Cookie.platform, "weibo")[2].cookie)
    # print(user.query_("1000030044"))
    # print(len("6e550c36-6ae6-31b4-91d2-41d1909f6632"))
    mysql = Mysql()
    # mysql.sql2csv(table='users_raw')
    mysql.create_all()
    mysql = Mysql(logger=loguru.logger)
    # print(type(eval("EventU")))
    mysql.sql2csv(table='BJDAH_EventU')
    # mysql.create_new_table(EventU,)

