# -*- coding: utf-8 -*-
# __author__: taohu

# import sys
# reload(sys)
# sys.setdefaultencoding("utf-8")
from xclient.core import client


class Handler(object):
    def __init__(self, sys_args):
        self.sys_args = sys_args

        self.msg = """
                   start:       start monitor client
                   stop :       stop monitor client
                   """
        self.selfcheck()
        self.command_allowcator()

    # 检查命令格式是否正确
    def selfcheck(self):
        if len(self.sys_args) < 2:
            exit(self.msg)

    # 启动/停止 入口
    def command_allowcator(self):
        if hasattr(self, self.sys_args[1]):
            func = getattr(self, self.sys_args[1])
            return func()
        else:
            exit(self.msg)

    def start(self):
        obj = client.ClientHandle()
        obj.forever_run()

    def stop(self):
        print("stopping the monitor client")
