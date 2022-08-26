import pathlib
from collections import defaultdict
from flask import Flask, request, jsonify, send_file
from flask_cors import *
from scrapy_redis.scheduler import Scheduler

from base.db.mysql import Mysql
from monitor.projectManager import ProjectManager

save_time = 3600

app = Flask(__name__)
CORS(app, supports_credentials=True)
PM = ProjectManager()


@app.route("/get_projects_info", methods=["get", "post"])
def get_pro_info():
    project_name = request.get_json().get("project_name")
    if not project_name:
        return {"code": 200, "message": PM.generate_config()}
    else:
        if project_name not in PM.projects.keys():
            return {"code": 300, "message": f"不存在爬虫项目{project_name}"}
        project = PM[project_name]

        return {"code": 200, "message": project.generate_config()}


@app.route("/create_project", methods=["get", "post"])
def create_project():
    """
    创建项目后默认保存
    """
    param = request.get_json()["param"]
    # 前端传过来的参数将会覆盖默认的参数配置
    result = PM.create(param)
    return jsonify(result)


@app.route("/get_custom_keywords", methods=["get", "post"])
def get_custom_keywords():
    """
    获取爬虫项目自定义关键词
    :return:
    """
    project_name = request.get_json().get("project_name")
    project = PM[project_name]
    if not project_name or not project:
        return {"code": 300, "message": f"不存在爬虫项目{project_name}"}
    custom_keywords = []
    for title_keywords in project.custom_keywords:
        info = title_keywords.split("_")
        if len(info) == 2:
            title = info[0]
            keyword = info[1]
        else:
            title = None
            keyword = info[0]
        custom_keywords.append({"title": title, "keyword": keyword})
    return {"code": 200, "message": custom_keywords}


@app.route("/del_project", methods=["get", "post"])
def delete_project():
    """
    删除某个项目
    """
    project_name = request.get_json()["project_name"]
    return {"code": 200, "message": PM.del_proj(project_name)}


@app.route("/update_cs_status", methods=["get", "post"])
def update_content_spider_status():
    """
    更新内容爬虫的状态，启用、停用一个或多个爬虫
    """
    project_name = request.get_json()["project_name"]
    project = PM[project_name]
    if not project_name or not project:
        return {"code": 300, "message": f"不存在爬虫项目{project_name}"}
    spider_status = request.get_json()["spider_status"]
    new_spider_status, error = project.spider_manager.update_from_dict(spider_status)
    return {"code": 200, "spider_status": new_spider_status, "error": error}


@app.route("/update_cs", methods=["get", "post"])
def update_content_spider():
    """
    添加或删除某个爬虫
    """
    project_name = request.get_json()["project_name"]
    project = PM[project_name]
    if not project_name or not project:
        return {"code": 300, "message": f"不存在爬虫项目{project_name}"}
    add_spiders = request.get_json()["add_spiders"]
    rm_spiders = request.get_json()["rm_spiders"]

    errors = {}
    errors.update({"add": project.spider_manager.add(add_spiders)})
    errors.update({"rm": project.del_spider(rm_spiders)})
    return {"code": 200, "errors": errors}


@app.route("/rm_sys_account", methods=["get", "post"])
def rm_sys_account():
    """
    删除系统账号
    """
    id = request.get_json()["id"]
    return {"code": 200, "message": PM.rm_sys_account(id)}


@app.route("/update_hs_status", methods=["get", "post"])
def update_hot_spider_status():
    """
    更新热点爬虫的状态
    """
    project_name = request.get_json()["project_name"]
    project = PM[project_name]
    if not project_name or not project:
        return {"code": 300, "message": f"不存在爬虫项目{project_name}"}

    hs_spider_status = request.get_json()["hs_spider_status"]
    new_spider_status, error = project.update_hot_spider_config(hs_spider_status)
    return {"code": 200, "spider_status": new_spider_status, "error": error}


@app.route("/add_hot_spider", methods=["get", "post"])
def add_hot_spider():
    project_name = request.get_json()["project_name"]
    add_spider = request.get_json()["add_spider"]
    project = PM[project_name]
    if not project_name or not project:
        return {"code": 300, "message": f"不存在爬虫项目{project_name}"}
    return {"code": 200, "message": project.add_hot_spider(add_spider)}


@app.route("/rm_hot_spider", methods=["get", "post"])
def rm_hot_spider():
    project_name = request.get_json()["project_name"]
    rm_spider = request.get_json()["rm_spider"]
    project = PM[project_name]
    if not project_name or not project:
        return {"code": 300, "message": f"不存在爬虫项目{project_name}"}
    return {"code": 200, "message": project.rm_hot_spider(rm_spider)}


@app.route("/add_keyword", methods=["get", "post"])
def add_keywords():
    """
    添加,删除指定关键词，进行监测
    """
    project_name = request.get_json()["project_name"]
    project = PM[project_name]
    if not project_name or not project:
        return {"code": 300, "message": f"不存在爬虫项目{project_name}"}
    add_keywords = request.get_json()["add_keywords"]
    rm_keywords = request.get_json()["rm_keywords"]

    project.add_custom_keywords(add_keywords)
    project.rm_custom_keywords(rm_keywords)

    key_info = []
    for title_keyword in project.custom_keywords:
        info = title_keyword.split("_")
        key_info.append({"title": info[0], "keywords": info[1]})

    return {"code": 200, "message": "添加、删除爬虫项目成功", "keyowrds": key_info}


@app.route("/set_title_custom", methods=["get", "post"])
def set_title_custom():
    project_name = request.get_json()["project_name"]
    project = PM[project_name]
    if not project or not project_name:
        return {"code": 300, "message": f"不存在爬虫项目{project_name}"}
    title = request.get_json()["title"]
    return {"code": 200, "message": project.set_title(title)}


@app.route("/get_device_info", methods=["get", "post"])
def get_device_info():
    project_name = request.get_json()["project_name"]
    project = PM[project_name]
    if not project_name or not project:
        return {"code": 200, "message": PM.get_all_devices()}
    return {"code": 200, "message": project.device_manager.get_devices_info()}


@app.route("/update_pro_device_status", methods=["get", "post"])
def update_project_device_status():
    """
    启用或停用本项目的分布式设备
    """
    project_name = request.get_json()["project_name"]
    project = PM[project_name]
    if not project_name or not project:
        return {"code": 300, "message": f"不存在爬虫项目{project_name}"}
    devices = request.get_json()["devices"]
    error = project.device_manager.update_device_from_params(devices)
    return {"code": 200, "error": error}


@app.route("/update_pro_device", methods=["get", "post"])
def update_project_device():
    """
    添加或删除本项目的分布式设备
    """
    project_name = request.get_json()["project_name"]
    project = PM[project_name]
    if not project_name or not project:
        return {"code": 300, "message": f"不存在爬虫项目{project_name}"}
    add_ips = request.get_json()["add_ip"]
    rm_ips = request.get_json()["rm_ip"]

    errors = {}
    errors["add"] = project.add_devices(add_ips)
    errors["rm"] = project.device_manager.rm_device_from_ip(rm_ips)
    return {"code": 200, "error": errors, "device": project.device_manager.get_devices_info()}


@app.route("/update_sys_device", methods=["get", "post"])
def update_device():
    """
    更新(添加，删除)整个系统的分布式设备列表
    """
    rm_devices = request.get_json()["rm_devices"]
    add_devices = request.get_json()["add_devices"]
    cover = request.get_json()["cover"]  # 重复信息是否覆盖
    return {"code": 200, "add_error": PM.add_devices(add_devices, cover), "rm_error": PM.rm_devices(rm_devices)}


@app.route("/update_pro_account", methods=["get", "post"])
def update_project_account():
    """
    更新本项目爬虫所启用的账户
    update_acc={"weibo":{"add":[],"rm":[]}}
    """
    project_name = request.get_json()["project_name"]
    project = PM[project_name]
    if not project_name or not project:
        return {"code": 300, "message": f"不存在爬虫项目{project_name}"}
    update_acc = request.get_json()["update_acc"]

    current = project.update_account(update_acc)
    return {"code": 200, "current_acc": current}


@app.route("/get_project_hot_spider", methods=["get", "post"])
def get_pro_hot_spider():
    project_name = request.get_json()["project_name"]
    project = PM[project_name]
    if project:
        return {"code": 200, "hot_spider": project.hot_spider_config}
    else:
        return {"code": 200, "msg": f"不存在爬虫项目{project_name}"}


@app.route("/get_account_info", methods=["get", "post"])
def get_account_info():
    project_name = request.get_json()["project_name"]
    all_account = PM.get_account_from_db()
    if not project_name:
        return {"code": 200, "account": all_account}
    project = PM[project_name]
    if project:
        user_dict = project.get_account_info()
        acc_info = defaultdict(dict)
        for platform, infos in user_dict.items():
            print(infos)
            for user in infos:
                acc_info[platform][user] = all_account[platform][user]
        return {"code": 200, "account": acc_info}
    else:
        return {"code": 300, "message": f"不存在爬虫项目{project_name}"}


@app.route("/update_account", methods=["get", "post"])
def update_account():
    """
    更新整个系统的账户信息
    也可以更新cookie信息
    account_infos = [{"platform":"weibo","user":"ct",...}]
    如果是插入数据，则应当具备所有数据
    """
    account_info = request.get_json()["account_infos"]
    return {"code": 200, "msg": PM.update_sys_account(account_info)}


@app.route("/update_timing_job", methods=["get", "post"])
def update_timing_job():
    """
    更新定时任务，定时任务包括：1.热点爬虫的启动时间，2.自定义爬虫固定搜索时间
    整个爬虫项目全局固定一个热点爬虫和关键词爬虫，所以热点爬虫和关键词爬虫的的定时时间统一
    """
    timing_param = request.get_json()["timing_job"]
    info = PM.update_timing_job(timing_param)
    if info:
        return {"code": 200, "timing_job_info": info}


@app.route("/get_timing_job_info", methods=["get", "post"])
def get_timing_job_info():
    return {"code": 200, "job_info": PM.job_manager.generate_config()}


@app.route("/pause_job", methods=["get", "post"])
def pause_job():
    name = request.get_json()["timing_job_name"]
    info = PM.job_manager.pause_job(name)
    return {"code": 200, "msg": info}


@app.route("/start_job", methods=["get", "post"])
def start_job():
    name = request.get_json()["timing_job_name"]
    info = PM.job_manager.resume_job(job_name=name)
    return {"code": 200, "msg": info}


@app.route("/get_all_content_spider", methods=["get", "post"])
def get_all_content_spider():
    return {"code": 200, "content_spiders": PM[0].spider_manager.get_all_content_spdier()}


@app.route("/get_all_hot_spider", methods=["get", "post"])
def get_all_hot_spider():
    return {"code": 200, "hot_spiders": list(PM.hot_spider_manager.all_hot_spider.keys())}


@app.route("/rm_timing_job", methods=["get", "post"])
def delete_timing_job():
    """
    删除定时任务
    :return:
    """
    job_name = request.get_json()["job_name"]
    status, msg = PM.delete_timing_job(job_name)
    if status:
        return {"code": 200, "message": True}
    else:
        return {"code": 200, "message": msg}


@app.route("/update_cookie", methods=["get", "post"])
def update_cookie():
    """
    更新cookie信息
    :return:
    """
    platform = request.get_json()["platform"]
    cookie = request.get_json()["cookie"]
    return {"code": 200, "message": PM.update_sys_account({"platform": platform, "cookie": cookie})}


@app.route("/get_pro_content_spider", methods=["get", "post"])
def get_pro_content_spider():
    """
    获取项目下的内容爬虫
    :return:
    """
    project_name = request.get_json()["project_name"]
    project = PM[project_name]
    if project:
        return {"code": 200, "content": project.spider_manager.get_pro_spider()}


@app.route("/get_headers", methods=["get", "post"])
def get_headers():
    """
    获取请求头信息
    :return:
    """
    return {"code": 200, "headers": PM._header_manager.header_dict}


@app.route("/update_headers", methods=["get", "post"])
def update_headers():
    platform = request.get_json()["platform"]
    key = request.get_json()["key"]
    value = request.get_json()["value"]
    return {"code": 200, "status": PM._header_manager.update_headers(platform, key, value)}


@app.route("/update_pro_crawl_time", methods=["get", "post"])
def update_pro_crawl_time():
    project_name = request.get_json()["project_name"]
    project = PM[project_name]
    crawl_time = request.get_json()["crawl_time"]
    if crawl_time and project:
        return {"code": 200, "status": project.update_crawl_time(start=crawl_time.get("start", None),
                                                                 end=crawl_time.get("end", None))}


@app.route("/sec_monitor", methods=["get", "post"])
def sec_monitor():
    """
    安全态势监测，传递爬虫项目名称，返回安全态势
    """
    project_name = request.get_json()["project_name"]
    mode = request.get_json()["mode"]
    project = PM[project_name]
    if project:
        return {"code": 200, "data": project.secure_monitor(mode)}
    else:
        return {"code": 300, "message": f"不存在爬虫项目{project_name}"}


@app.route("/spider_monitor", methods=["get", "post"])
def spider_monitor():
    """
    爬虫数据量监测
    """
    project_name = request.get_json()["project_name"]
    platform = request.get_json()["platform"]
    project = PM[project_name]
    if project:
        return {"code": 200, "data": project.spider_monitor(platform)}
    else:
        return {"code": 300, "message": f"不存在爬虫项目{project_name}"}


@app.route("/spread_monitor", methods=["get", "post"])
def spread_monitor():
    """
    传播态势监测
    :return:
    """
    project_name = request.get_json()["project_name"]
    project = PM[project_name]
    if project:
        return {"code": 200, "data": project.spread_monitor()}
    else:
        return {"code": 300, "message": f"不存在爬虫项目{project_name}"}


@app.route("/download_news_data", methods=["get", "post"])
def download_news_data():
    """
    爬虫数据量监测
    """
    try:
        project_name = request.get_json()["project_name"]
        table_name = project_name + '_EventU'
        mysql = Mysql()
        mysql.sql2csv(table=table_name)
        path = str(abs_path) + '/src/data/news_raw.csv'
        return send_file(path)
    except:
        return {"code": 201, "message": " 导出用户数据失败 "}


abs_path = pathlib.Path(__file__).parent.absolute()


@app.route("/download_user_data", methods=["get", "post"])
def download_user_data():
    """
    爬虫数据量监测
    """
    try:
        mysql = Mysql()
        mysql.sql2csv(table='users_raw')
        path = str(abs_path) + '/src/data/users_raw.csv'
        return send_file(path)
    except:
        return {"code": 201, "message": " 导出用户数据失败 "}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=50001, debug=False)
