# Name:         dazhongdianpin.py
# Description:  大众点评首页点击电影后跳转页面
# Author:       东寿
# Date:         2022/8/5

from string import Template

import requests
import scrapy as scrapy
from scrapy import Selector
from monitor import logger

url_ = "https://lx1.meituan.net/?d=W3siY2giOiJkaWFucGluZ3dlYiIsInNjIjoiMTUzNio4NjQiLCJ1dWlkIjoiQUFDRERBNTAxNDlBMTFFREFFNDE3Rjk2Rjc4QjM2QTA0NkMyRjA0M0MwRDk0RkVFQkEzNERCNkQ3QUM5NEMyOCIsImN0Ijoid3d3IiwidXRtIjp7InV0bV9zb3VyY2UiOiJkaWFucGluZ3dlYiJ9LCJhcHBubSI6Im1vdmllIiwidWlkIjozMTg0Nzk0ODAxLCJzZGtfZW52Ijoib25saW5lIiwiZXZzIjpbeyJubSI6IlBWIiwidG0iOjE2NTk2OTI1OTI4NzUsIm50IjowLCJpc2F1dG8iOjcsInJlcV9pZCI6IjE4MjZkNjMyZWU5LTMzNTE0LTE4NDIzIiwic2VxIjoxNywibHhfaW5uZXJfZGF0YSI6eyJwYXRoIjoiaHR0cHM6Ly93d3cubWFveWFuLmNvbS9maWxtcyIsImlzSGVhZGxlc3MiOjAsImxhYnYiOjEwMDA2LCJjdiI6InByb2QiLCJ3ZWIiOjEsInByb3h5IjoxLCJidG9hIjp0cnVlLCJhdG9iIjp0cnVlLCJzdGltZSI6MTQyLjEwMDAwMDM4MTQ2OTczLCJwdmlkIjoicHZpZC05MzQzMDUtMjA3MDMwOSIsIm1fbXNpZCI6Im1lbV8xODI2ZDYzMmUzNy05OGMtMWY4LTQxZCIsIm1fc2VxIjoxLCJfYXBpIjoidjMiLCJodCI6ZmFsc2V9LCJ1cmwiOiJodHRwczovL3d3dy5tYW95YW4uY29tL2ZpbG1zP3V0bV9zb3VyY2U9ZGlhbnBpbmd3ZWIiLCJ1cmxyIjoiaHR0cHM6Ly9wYXNzcG9ydC5tYW95YW4uY29tLyIsImNpZCI6ImNfcmhyNWkxbiIsImxhYiI6eyJzdWJuYXZJZCI6MSwiY3VzdG9tIjp7Il9seF9jdiI6InByb2QifX19XSwic3YiOiI0LjIwLjAiLCJtcyI6IjE4MjZkNWMwZTBiLWI2OC00N2EtNGZmIiwiYyI6Im1vdmllIiwibHhpZCI6IjE4MjZkMmM3MDI5YzgtMDI0NjBlNWMwNzM2YzEtMjYwMjFhNTEtMTQ0MDAwLTE4MjZkMmM3MDI5YzgifV0%3D&t=1&r=1826d632eec0&_lxsdk_rnd=1826d632eed1"
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

class DaZhongDP:
    def __init__(self):
        pass

    def get_request_from_keyword(self, headers, search_url, keyword, *args, **kwargs):
        try:
            r1 = requests.get(url_,headers=headers_)  # 大众点评.猫眼每次访问都存在一个前置请求来验证，暂时不知道强制请求生成规律
            resp = requests.get(search_url.substitute(), headers=headers)
            # print(resp.text)
            if resp.status_code!=200:
                return None
            resp = Selector(resp)
            for movie_div in resp.xpath("//div[@class='channel-detail movie-item-title']"):
                # print(movie_div.get())
                url = movie_div.xpath("//a/@href").get()
                title  =movie_div.xpath("//@title").get()
                meta = {"title":title,"callback":"parse_page","url":url}
                yield scrapy.Request("https://www.maoyan.com"+url,headers=headers,meta=meta)
        except Exception as e:
            logger.error(f"E 大众点评 {e}")
            return None



if __name__ == '__main__':
    search_url = Template('https://www.maoyan.com/films?utm_source=dianpingweb')
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Cookie": "uuid_n_v=v1; uuid=AACDDA50149A11EDAE417F96F78B36A046C2F043C0D94FEEBA34DB6D7AC94C28; _lxsdk_cuid=1826d2c7029c8-02460e5c0736c1-26021a51-144000-1826d2c7029c8; _lxsdk=AACDDA50149A11EDAE417F96F78B36A046C2F043C0D94FEEBA34DB6D7AC94C28; _csrf=f894eb215e413ed10f824d47338c2c66699711b6c3756e774fe5874d0a750fba; _lx_utm=utm_source%3Ddianpingweb; Hm_lvt_703e94591e87be68cc8da0da7cbd0be2=1659689005,1659689324; Hm_lpvt_703e94591e87be68cc8da0da7cbd0be2=1659689324; __mta=242455869.1659689005462.1659689124369.1659689324396.9; _lxsdk_s=1826d2c702d-221-984-dcf%7C%7C24",
        "Host": "www.maoyan.com",
        "sec-ch-ua": "'.Not/A)Brand';v='99', 'Google Chrome';v='103', 'Chromium';v='103'",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "'Windows'",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
    }

    dazhongdianping = DaZhongDP()
    for url in dazhongdianping.get_request_from_keyword(headers,search_url,None):
        print(url)