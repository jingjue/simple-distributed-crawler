"""
定时器,该文件包含Job、JobManager
"""
import inspect
import time
from threading import Thread

from apscheduler.schedulers.background import BackgroundScheduler

from monitor import logger


class Job:
    def __init__(self, name, trigger, kwargs, task, func, task_para=None, **kwargs_):
        '''
        :param name: str
        :param task: 一个函数
        :param trigger: 'interval' or 'data'
        :param kwargs: interval:{"day":3,"hour":17,"minute":9,"second":7}
                       date:datetime(2009, 11, 6, 16, 30, 5)     #只会执行一次
        :param:task_para: ['a','b','c'] (task的参数)
        '''
        super(Job, self).__init__()
        self.name = name
        self.task = task
        self.trigger = trigger  # interval间隔调度，data定时调度
        self.kwargs = kwargs
        self.task_para = task_para
        self.func = func

    def set_trigger(self, new_val: str):
        if new_val != 'interval' and new_val != 'data':
            return False
        else:
            self.trigger = new_val
            return True

    def get_trigger(self):
        return self.trigger

    def set_kwargs(self, new_val):
        self.kwargs = new_val

    def get_kwargs(self):
        return self.kwargs

    def generate_config(self):
        """
        生成配置信息
        """
        return {"name": self.name, "trigger": self.trigger, "task": self.task.__qualname__, "kwargs": self.kwargs,
                "task_para": self.task_para, "func": self.func.__qualname__}

    def update_from_param(self, params):
        """
        更新job的参数
        """
        for name, value in params.items():
            if getattr(self, name, False):
                setattr(self, name, value)

    @classmethod
    def from_config(cls, params):
        """
        注意，params中的task需要在上一级中动态链入
        """
        return cls(**params)


class JobManager:
    def __init__(self, jobs: dict = {}):
        """
        jobs_status:-1,0,1分别表示禁用，暂停，启用
        :param jobs:
        """

        self.jobs = jobs  # name,Job
        self.jobs_instance = {}  # name,job_instance
        self.jobs_status = {}  # name,status
        self.scheduler = BackgroundScheduler()

    def add_jobs(self, job):
        self.jobs[job.name] = job

    def add_job_from_param(self, param: dict):
        job = Job(**param)
        self.add_jobs(job)
        self.jobs_status[job.name] = -1

    def start(self):
        for name, job in self.jobs.items():
            if job.trigger == 'interval':
                job_instance = self.scheduler.add_job(job.task, job.trigger, days=job.kwargs['day'],
                                                      hours=job.kwargs['hour'],
                                                      minutes=job.kwargs['minute'],
                                                      seconds=job.kwargs['second'],
                                                      args=(job.func, job.task_para),
                                                      id=job.name)
                self.jobs_instance[job.name] = job_instance
                self.jobs_status[job.name] = 1
            elif job.trigger == 'date':
                self.scheduler.add_job(job.task, job.trigger, run_date=job.kwargs, args=(job.func, job.task_para))
        self.scheduler.start()

    def add_job_to_scheduler(self, job_params):
        """
        根据配置信息来添加任务
        :param job_params:
        :return:
        """
        try:
            self.add_job_from_param(job_params)
            job = self.jobs[job_params['name']]
            if job.trigger == 'interval':
                job_instance = self.scheduler.add_job(job.task, job.trigger, days=job.kwargs['day'],
                                                      hours=job.kwargs['hour'],
                                                      minutes=job.kwargs['minute'],
                                                      seconds=job.kwargs['second'],
                                                      args=(job.func, job.task_para),
                                                      id=job.name)
                self.jobs_instance[job.name] = job_instance
                self.jobs_status[job.name] = 1
                logger.info(f"添加定时任务，{job_params['name']}")
            elif job.trigger == 'date':
                self.scheduler.add_job(job.task, job.trigger, run_date=job.kwargs, args=(job.func, job.task_para))
                self.jobs_status[job.name] = 1
                logger.info(f"添加定时任务，{job_params['name']}")
        except Exception as e:
            logger.error(f"添加定时任务失败，{job_params},原因：{e}")
            return False

    def update_job_to_scheduler(self, job_params):
        """
        更新定时任务
        :param job_params:
        :return:
        """
        try:
            self.delete_job(job_params["name"])
            self.add_job_to_scheduler(job_params)
            self.jobs[job_params['name']].update_from_param(job_params)
            return True
        except Exception as e:
            logger.exception(f"更新定时任务失败，{job_params},原因：{e}")
            return False

    def job_exist(self, name):
        return name in self.jobs_instance

    def delete_job(self, job_name):
        """
        删除任务
        :param job_name:
        :return:
        """
        if self.jobs.get(job_name,False) and self.jobs_status.get(job_name) != -1:
            job_instance = self.jobs_instance.get(job_name,False)
            if job_instance:
                self.scheduler.remove_job(job_name)

            # self.jobs.pop(job_name)
            self.jobs_instance.pop(job_name)
            self.jobs_status[job_name] = -1
            logger.info("删除任务:%s" % job_name)
            return True, None
        else:
            logger.error("删除任务失败，原因：任务不存在")
            return False, "任务不存在"

    def resume_job(self, job_name):
        """
        恢复暂停的任务
        :param job_name:
        :return:
        """
        if self.jobs.get(job_name) and self.jobs_status.get(job_name,False) == 0:
            self.scheduler.resume_job(job_name)
            self.jobs_status[job_name] = 1
            return f"{job_name}恢复成功"
        else:
            if self.jobs_status.get(job_name,False) == 0:
                logger.error(f"恢复{job_name}任务失败，原因：任务已经是运行状态")
                return False,f"{job_name}已经是运行状态"
            elif self.jobs_status.get(job_name,False) == -1:
                logger.error(f"恢复{job_name}任务失败，原因：任务不存在")
                return False,f"{job_name}不存在"

            return False, f"{job_name}任务不存在"

    def pause_job(self, name):
        if self.jobs.get(name, False):
            self.jobs_instance[name].pause()
            self.jobs_status[name] = 0
            logger.info("暂停任务:%s" % name)
            return True
        else:
            logger.warning("任务:%s不存在" % name)
            return "任务:%s不存在" % name

    def stop(self):
        self.scheduler.shutdown(wait=False)

    def generate_config(self):
        """
        生成配置信息
        """
        jobs = {}
        for job in self.jobs.values():
            jobs[job.name] = job.generate_config()
            jobs[job.name]['status'] = self.jobs_status[job.name]
        return jobs

    @classmethod
    def from_params(cls, params):
        """
        注意，params中的task需要在上一级动态链入
        """
        jobs = {}
        for name, job in params.items():
            jobs[name] = Job.from_config(job)
        return cls(jobs)


if __name__ == '__main__':
    # name, trigger, kwargs, task
    kwargs = {
        "day": 0,
        "hour": 0,
        "minute": 0,
        "second": 3,
    }
    trigger = 'interval'
    para = ['ceshi']


    def aaaa(para):
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        print(para)


    def run_func_by_thread(func, *args):
        """
        以线程的方式启动函数func
        """

        task = Thread(target=func, args=args)
        task.setDaemon(True)  # 设置守护进程
        task.start()


    config = {
        "name": "test",
        "trigger": trigger,
        "task": run_func_by_thread,
        "kwargs": kwargs,
        "task_para": para,
        "func": aaaa
    }

    job = Job.from_config(config)
    test_job_manager = JobManager()
    test_job_manager.add_jobs(job)
    test_job_manager.start()

    time.sleep(10)
    config["name"] = "test2"
    test_job_manager.update_job_to_scheduler(config)
    print(test_job_manager.scheduler.get_jobs())
    print(test_job_manager.jobs_status)
    test_job_manager.pause_job("test")
    print(test_job_manager.jobs_status)
    test_job_manager.resume_job("test")
    print(test_job_manager.jobs_status)
    test_job_manager.delete_job("test")
    print(test_job_manager.jobs_status)
    test_job_manager.resume_job("test")
    print(test_job_manager.jobs_status)
    time.sleep(60)
