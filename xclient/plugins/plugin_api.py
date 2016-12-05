# -*- coding: utf-8 -*-
# __author__: taohu

# import sys
# reload(sys)
# sys.setdefaultencoding("utf-8")

from xclient.plugins.linux import life_status, cpu, memory, network, host_alive


def sign_of_life():
    return life_status.monitor()


def get_linux_cpu():
    return cpu.monitor()


def host_alive_check():
    return host_alive.monitor()


def GetNetworkStatus():
    return network.monitor()


def get_memory_info():
    return memory.monitor()
