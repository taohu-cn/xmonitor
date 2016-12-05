# -*- coding: utf-8 -*-
# __author__: taohu

# import sys
# reload(sys)
# sys.setdefaultencoding("utf-8")
import subprocess
from xclient.plugins.linux.data_format_convert import data_format_convert


def monitor(frist_invoke=1):
    cmd = 'sar 1 3 | tail -n 1'
    res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    res_err = res.stderr.read()
    res_msg = data_format_convert(res.stdout.read())

    if res_err:
        value_dic = {'status': res_err}
    else:
        user, nice, system, iowait, steal, idle = res_msg.split()[2:]
        value_dic = {
            'user': user,
            'nice': nice,
            'system': system,
            'iowait': iowait,
            'steal': steal,
            'idle': idle,
            'status': 0,
        }
    return value_dic


if __name__ == '__main__':
    print(monitor())
