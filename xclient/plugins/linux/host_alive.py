# -*- coding: utf-8 -*-
# __author__: taohu

# import sys
# reload(sys)
# sys.setdefaultencoding("utf-8")
import subprocess
from xclient.plugins.linux.data_format_convert import data_format_convert


def monitor(frist_invoke=1):
    cmd = 'uptime'
    res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    res_msg = data_format_convert(res.stdout.read())

    value_dic = {
        'uptime': res_msg,
        'status': 0
    }
    return value_dic


if __name__ == '__main__':
    print(monitor())
