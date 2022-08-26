import random

import pycookiecheat

from base.db.dbSlot import Slot
from base.db.mysql import Cookie, Mysql
from base.utils.time import get_date
from monitor import logger
from monitor.setting import REDIS_SPIDER_ACC_VALID, CanRefreshCookie


class CookieManager:
    def __init__(self, project_name, dbslot, acc_constraint=False):
        """
        决定使用哪些平台账户的cookie 进行爬取
        acc_constraint:限制爬虫使用哪些平台账户
        """
        self.dbslot = dbslot
        self.acc_constraint = acc_constraint
        self.project_name = project_name

    def refresh_cookie(self, platform):
        """
        根据platform,更新cookie信息
        :return:
        """
        if platform == "微博用户":
            platform = "微博"
        cookie = self.dbslot.mysql.query_cookie(table="Cookie", key="platform", value=platform)
        if not cookie:
            if platform in CanRefreshCookie:
                self.refresh_cookie_from_db(platform)
                cookie = self.dbslot.mysql.query_cookie(table="Cookie", key="platform", value=platform)
            if not cookie:
                logger.warning(f"{platform} 数据库中缺少Cookie信息")
                return None
        index = random.randint(0, len(cookie) - 1)
        if cookie[index].valid:
            if self.acc_constraint:
                # 获取该爬虫可用的平台账户
                account_valid = self.dbslot.redis.get_list(
                    REDIS_SPIDER_ACC_VALID.substitute(project_name=self.project_name, platform=platform))
                if cookie[index].user in account_valid:
                    return cookie[index].to_dict()
            else:
                return cookie[index].to_dict()
        else:
            cookie[index].valid = False
            self.dbslot.mysql.commit()
            return None

    def refresh_cookie_from_db(self, platform):
        """
        在version2中已弃用该功能
        """
        return False
        # if platform == '微博':
        #     # 更新系统中所有微博平台的cookie信息
        #     accounts = self.dbslot.mysql.get_all_account()
        #     index = 1
        #     for account in accounts:
        #         if account.platform == platform:
        #             file = "Default" if index == 1 else f"Profile {index}"
        #             cookie = self._get_cookie_from_sqlite(file)
        #             if cookie:
        #                 index += 1
        #                 cookie_dict = account.to_dict()
        #                 cookie_dict["cookie"] = cookie
        #                 self.dbslot.mysql.update_cookie(cookie_dict)
        #     return True
        # else:
        #     return False

    def _get_cookie_from_sqlite(self, name='Default'):
        """
        从chrome的数据库sqlite中获取cookie
        在version2中已弃用该功能
        :return:
        """
        try:
            # url = "https://weibo.com"
            # file = f"/home/chase/.config/google-chrome/{name}/Cookies"
            # cookie_d = pycookiecheat.chrome_cookies(url, file)
            # cookie = ''
            # for index, key in enumerate(cookie_d.keys()):
            #     cookie += key + "=" + cookie_d[key] + "; "
            # return cookie[:-2]
            return None
        except Exception as e:
            # logger.error(e)
            logger.warning("在version2中已弃用该功能")
            return None

    def check_cookie(self, cookie, platform, resp: str):
        """
        检查cookie是否有效,如果无效则更新cookie，若cookie更新失败，则更新数据库信息
        :param resp:
        :return:
        """
        if "login" in resp:
            if not self.refresh_cookie_from_db(platform):
                self.set_cookie_valid(cookie, platform)
                logger.error(f"{platform} cookie失效，请手动更新cookie")
                return False
        else:
            return True

    def set_cookie_valid(self, cookie, platform):
        """
        手动设置cookie无效
        :param platform:
        :return:
        """
        try:
            cookie["valid"] = False
            self.dbslot.mysql.update(Cookie(**cookie))
        except:
            logger.error(f"数据库中没有{platform} cookie数据  {cookie}")

if __name__ == '__main__':
    cm = CookieManager("default",Slot(mysql=Mysql()))
    print(cm.refresh_cookie_from_db("微博"))

