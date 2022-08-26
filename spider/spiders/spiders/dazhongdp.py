# Name:         dazhongdp.py
# Description:  大众点评首页点击电影后跳转页面
# Author:       东寿
# Date:         2022/8/5
import requests
import scrapy
from scrapy import Selector

from loguru import logger
from spiders.items import WeiboItem
from spiders.spiders import BaseSpider
import time

url_ = "https://lx1.meituan.net/?d=W3siY2giOiJkaWFucGluZ3dlYiIsInNjIjoiMTUzNio4NjQiLCJ1dWlkIjoiQUFDRERBNTAxNDlBMTFFREFFNDE3Rjk2Rjc4QjM2QTA0NkMyRjA0M0MwRDk0RkVFQkEzNERCNkQ3QUM5NEMyOCIsInVpZCI6MzE4NDc5NDgwMSwiY3QiOiJ3d3ciLCJ1dG0iOnsidXRtX3NvdXJjZSI6ImRpYW5waW5nd2ViIn0sImFwcG5tIjoibW92aWUiLCJzZGtfZW52Ijoib25saW5lIiwiZXZzIjpbeyJubSI6IlBWIiwidG0iOjE2NTk3NDc4MzI2ODksIm50IjowLCJpc2F1dG8iOjcsInJlcV9pZCI6IjE4MjcwYWUxMzZmLTE5NjQ5LTM1MjUwIiwic2VxIjoyLCJseF9pbm5lcl9kYXRhIjp7InBhdGgiOiJodHRwczovL3d3dy5tYW95YW4uY29tL2ZpbG1zLzEzOTcwMTYiLCJpc0hlYWRsZXNzIjowLCJsYWJ2IjoxMDAwNiwiY3YiOiJwcm9kIiwid2ViIjoxLCJwcm94eSI6MSwiYnRvYSI6dHJ1ZSwiYXRvYiI6dHJ1ZSwic3RpbWUiOjI2Ni42MDAwMDAzODE0Njk3LCJwdmlkIjoicHZpZC00MzE2NzIxLTUzNTY4OCIsIm1fbXNpZCI6Im1lbV8xODI3MGFlMTJmMS1jYjQtNzNhLTIiLCJtX3NlcSI6MSwiX2FwaSI6InYzIiwiaHQiOmZhbHNlfSwidXJsIjoiaHR0cHM6Ly93d3cubWFveWFuLmNvbS9maWxtcy8xMzk3MDE2IiwidXJsciI6Imh0dHBzOi8vd3d3Lm1hb3lhbi5jb20vZmlsbXM%2FdXRtX3NvdXJjZT1kaWFucGluZ3dlYiIsImNpZCI6ImNfNDd3cmNnZyIsImxhYiI6eyJpZCI6IjEzOTcwMTYiLCJjdXN0b20iOnsiX2x4X2N2IjoicHJvZCJ9fX1dLCJzdiI6IjQuMjAuMCIsIm1zIjoiMTgyNzBhZTBmNDUtNDMtMzg2LWE3YSIsImMiOiJtb3ZpZSIsImx4aWQiOiIxODI2ZDJjNzAyOWM4LTAyNDYwZTVjMDczNmMxLTI2MDIxYTUxLTE0NDAwMC0xODI2ZDJjNzAyOWM4In1d&t=1&r=18270ae13770&_lxsdk_rnd=18270ae137a1"
headers_={
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    "Content-Type": "text/plain",
    "Host": "lx1.meituan.net",
    "Origin": "https://www.maoyan.com",
    "Referer": "https://www.maoyan.com/",
    "sec-ch-ua": "\".Not/A)Brand\";v=\"99\", \"Google Chrome\";v=\"103\", \"Chromium\";v=\"103\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
}

class DaZhongDP(BaseSpider):
    name = "大众点评"

    def __init__(self,one_project_name="default", **kwargs):
        super(DaZhongDP, self).__init__(one_project_name, logger)


    def parse_page(self,response):
        """
        解析大众点评网页中的电影评价网
        :param response:
        :return:
        """
        r1 = requests.get(url_, headers=headers_)  #请求之前必须访问一次
        url = response.meta["url"]
        resp = requests.get(url, headers=headers_)
        if resp.status_code!= 200:
            return None
        resp = Selector(resp)
        dazhongdp = WeiboItem()
        dazhongdp["title"] = resp.xpath("//h1/text()").get()
        dazhongdp["platform"] = "大众点评"
        for comment_li in resp.xpath("//li[@class='comment-container ']"):
            dazhongdp["account"] = comment_li.xpath("//div[@class='user']/span[1]/text()").get()
            dazhongdp["date"] =  comment_li.xpath("//div[@class='time']/@title").get()
            dazhongdp["content"] = comment_li.xpath("//div[@class='comment-content']/text()").get()
            dazhongdp["likes"] = comment_li.xpath("//div[@class='approve ']/span[@class='num']/text()").get()
            yield dazhongdp










