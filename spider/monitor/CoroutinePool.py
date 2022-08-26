"""
协程池，参考连接：https://www.icode9.com/content-1-776561.html
动态添加任务：
方案是创建一个线程，使事件循环在线程内永久运行
设置守护进程，随着主进程一起关闭
自动停止任务
阻塞任务完成
协程池
队列自带阻塞机制，当队列满了后会阻塞，因此可以取代 asyncio.Semaphore()

！！！已弃用
"""
import asyncio
import queue
from threading import Thread


class AsyncPool(object):
    """
    1. 支持动态添加任务
    2. 支持自动停止事件循环
    3. 支持最大协程数
    """

    def __init__(self, loop=None, maxsize=0):
        """
        初始化
        :param loop:
        :param maxsize: 默认0，不限制队列
        """

        # 获取一个事件循环
        if not loop:
            self.loop = asyncio.new_event_loop()

        # 队列，先进先出，根据队列是否为空判断，退出协程
        self.q = queue.Queue(maxsize)

        self.loop_thread = None
        if self.loop:
            self.start_thread_loop()

    def add(self, item=1):
        """
        添加任务
        :param item:
        :return:
        """
        self.q.put(item)

    def done(self, fn):
        """
        任务完成
        回调函数
        :param fn:
        :return:
        """
        if fn:
            pass
        self.q.get()
        self.q.task_done()

    def wait(self):
        """
        等待任务执行完毕
        :return:
        """
        self.q.join()

    @staticmethod
    def _start_thread_loop(loop):
        """
        运行事件循环
        :param loop: loop以参数的形式传递进来运行
        :return:
        """
        # 将当前上下文的事件循环设置为循环。
        asyncio.set_event_loop(loop)
        # 开始事件循环
        loop.run_forever()

    def start_thread_loop(self):
        """
        运行事件循环
        :return:
        """
        self.loop_thread = Thread(target=self._start_thread_loop, args=(self.loop,))
        # 设置守护进程
        self.loop_thread.setDaemon(True)
        # 运行线程，同时协程事件循环也会运行
        self.loop_thread.start()

    def stop_thread_loop(self, loop_time=1):
        """
        队列为空，则关闭线程
        :param loop_time:
        :return:
        """

        async def _close_thread_loop():
            """
            关闭线程
            :return:
            """
            while True:
                if self.q.empty():
                    self.loop.stop()
                    break
                await asyncio.sleep(loop_time)

        # 等待关闭线程
        asyncio.run_coroutine_threadsafe(_close_thread_loop(), self.loop)

    def submit(self, func, callback=None):
        """
        提交任务到事件循环
        :param func: 异步函数对象
        :param callback: 回调函数
        :return:
        """
        # 将协程注册一个到运行在线程中的循环，thread_loop 会获得一个环任务
        # 注意：run_coroutine_threadsafe 这个方法只能用在运行在线程中的循环事件使用
        future = asyncio.run_coroutine_threadsafe(func, self.loop)

        # 回调函数封装
        def callback_done(_future):
            try:
                if callback:
                    callback(_future)
            finally:
                self.done(_future)

        # 添加回调函数
        future.add_done_callback(callback_done)

    def release(self, loop_time=1):
        """
        释放线程
        :param loop_time:
        :return:
        """
        self.stop_thread_loop(loop_time)

    def running(self):
        """
        获取当前线程数
        :return:
        """
        return self.q.qsize()

if __name__ == '__main__':
    pool = AsyncPool(10)
    pool.add()
