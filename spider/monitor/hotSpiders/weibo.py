# Name:         weibo.py.bak
# Description:  微博热点爬虫
# Author:       东寿
# Date:         2022/4/7

import requests
from monitor import logger
from monitor.titleManager import Title


class Weibo:
    name = "微博"

    def __init__(self):
        pass

    def get_title(self, headers, url):
        """
        爬取热点爬虫
        :param headers:请求头和cookie相关信息
        :return:
        """
        try:
            print(url)
            response = requests.get(url, headers=headers,timeout=10)
            if response.status_code == 200:
                try:
                    title = Title()
                    resp = response.json()["data"]
                    title.append(resp["hotgov"]["name"])
                    for item in resp["realtime"]:
                        title.append(item["word"])
                    return True, title
                except Exception as e:
                    logger.error("解析热点爬虫失败：{} {}".format(e,response.text))
                    return False,response.text
            else:
                logger.warning("请求失败，状态码：{}".format(response.status_code))
                return False,None
        except Exception as e:
            logger.exception(f"url:{url}  {e}")
            return False,None

if __name__ == '__main__':
    headers = {
      "accept": "application/json, text/plain, */*",
      "accept-encoding": "gzip, deflate, br",
      "accept-language": "zh-CN,zh;q=0.9",
      "referer": "https://weibo.com/search?containerid=100103type%3D1%26q%3D%E5%85%B1%E5%90%8C%E6%9E%84%E5%BB%BA%E5%9C%B0%E7%90%83%E7%94%9F%E5%91%BD%E5%85%B1%E5%90%8C%E4%BD%93%26t%3D0&q=%E5%85%B1%E5%90%8C%E6%9E%84%E5%BB%BA%E5%9C%B0%E7%90%83%E7%94%9F%E5%91%BD%E5%85%B1%E5%90%8C%E4%BD%93",
      "sec-ch-ua": "\"Google Chrome\";v=\"93\", \" Not;A Brand\";v=\"99\", \"Chromium\";v=\"93\"",
      "sec-ch-ua-mobile": "?0",
      "sec-ch-ua-platform": "\"Linux\"",
      "sec-fetch-dest": "empty",
      "sec-fetch-mode": "cors",
      "sec-fetch-site": "same-origin",
      "traceparent": "00-39d0fa273a05b60f3e91ad85ffa0fcc0-b3b5744face2fcff-00",
      "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
      "x-requested-with": "XMLHttpRequest",
      "x-xsrf-token": "8-sppY1kKRpY2ifthSuvTEe_"
    }
    url = "https://weibo.com/ajax/side/hotSearch"
    weibo = Weibo()
    [print(key) for key in  list(weibo.get_title(headers,url)[1].keywords)[0:10]]
