"""
参考url：https://zhuanlan.zhihu.com/p/339070615
"""
from string import Template
import pexpect
from monitor import logger

DEPLOY_SPIDER = Template("scrapyd-deploy -p $project_name")  # 发布爬虫项目
PROMPT = ['#', '>>>', '>', '\$', "Packing"]


class SSH:
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = 22
        self.username = username
        self.password = password

    def connect(self):
        command = 'ssh -p {} {}@{}'.format(self.port, self.username, self.host)
        try:
            self.ssh = pexpect.spawn(command)
            logger.info(f'命令: {command}')
            expect_list = [
                'yes/no',
                'password:',
                pexpect.EOF,
                pexpect.TIMEOUT,
            ]
            index = self.ssh.expect(expect_list)
            logger.info(f'匹配到: {index} => {expect_list[index]}')
            if index == 0:
                self.ssh.sendline("yes")
                expect_list = [
                    'password:',
                    pexpect.EOF,
                    pexpect.TIMEOUT,
                ]
                index = self.ssh.expect(expect_list)
                logger.info(f'匹配到: {index} => {expect_list[index]}')
                if index == 0:
                    self.ssh.sendline(self.password)
                    # self.ssh.interact()
                else:
                    logger.error('EOF or TIMEOUT')
            elif index == 1:
                self.ssh.sendline(self.password)
                # self.ssh.interact()
            else:
                logger.error('EOF or TIMEOUT')
            self.ssh.expect(self.username)
            before = self.ssh.before.decode()
            after = self.ssh.after.decode()
            logger.info({"run": f"ssh {self.host}", "before": before, "after": after})
            return True, {"run": f"ssh {self.host}", "before": before, "after": after}
        except Exception as e:
            logger.error({"error": e, "message": "连接失败"})
            return False, {"error": e, "message": "连接失败"}

    def send_command(self, cmd):
        # 执行命令，并返回结果
        self.ssh.sendline(cmd)  # 传递命令
        self.ssh.buffer = b""
        self.ssh.expect(self.username)  # 期望获得的命令提示符
        return self.ssh.before.decode()  # 获取远程打印命令


def scp(server, logger):
    command = f"scp {server['source']} {server['username']}@{server['ip']}:{server['target']}"
    process = pexpect.spawn(command, timeout=30)
    process.buffer = b""
    logger.info(f'命令: {command}')
    expect_list = [
        'password:',
        pexpect.EOF,
        pexpect.TIMEOUT,
    ]
    index = process.expect(expect_list)
    logger.info(f'匹配到: {index} => {expect_list[index]}')
    if index == 0:
        process.sendline(server['password'])
        # process.interact()
    else:
        logger.error('EOF or TIMEOUT')
        return "EOF or TIMEOUT"
    before = process.before.decode()
    after = process.after.decode()
    logger.info({"run": f"scp {server['ip']}", "before": before, "after": after})
    return {"run": f"scp {server['ip']}", "before": before, "after":after,
            "result": process.read().decode().strip()}


if __name__ == '__main__':
    server_ssh = {
        'host': '180.201.163.246',
        'port': '22',
        'username': 'chase',
        'password': '123',
    }
    # ssh(server_ssh, None)

    serve_scp = {
        "source": "./shell.py",
        "target": "/home/users/CT/",
        "password": "123",
        "username": "chase",
        "ip": "180.201.163.246"
    }
    from loguru import logger

    scp(serve_scp, logger)

    # ssh = SSH(host=server_ssh['host'], port=server_ssh['port'], username=server_ssh['username'],
    #           password=server_ssh['password'])
    # ssh.connect()
    # print(ssh.send_command(f"cd /home/users/CT/pycharmproject/spiders/ && nohup scrapyd & "))
    # print(ssh.send_command(f"cd /home/users/CT/pycharmproject/spiders/ && scrapyd-deploy -p test1"))
