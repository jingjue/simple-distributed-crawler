# -*-coding:utf-8-*- 、
# Team : upcedu.nlp
# Author：dongshou
# Date ：2021/10/11 上午10:26
# Describe ：处理url

def sweibo_url_pro(url):
    """
    //weibo.com/1036713140/KBkihpPcr?refer_flag=1001030103_"
    :param url:
    :return:
    """
    try:
        info = url.split("?refer")[0][2].split("/")
        uid = info[1]
        weibo_id = info[2]
        return uid, weibo_id
    except:
        return f"【util解析出错】sweibo url解析出错 url：{url}"
