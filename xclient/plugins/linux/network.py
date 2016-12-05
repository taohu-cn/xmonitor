# -*- coding: utf-8 -*-
# __author__: taohu

# import sys
# reload(sys)
# sys.setdefaultencoding("utf-8")
import subprocess
from xclient.plugins.linux.data_format_convert import data_format_convert


def monitor(frist_invoke=1):
    cmd = 'sar -n DEV 1 5 | grep -v IFACE | grep Average'
    res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    res_err = res.stderr.read()
    res_msg = data_format_convert(res.stdout.read()).strip()

    if res_err:
        value_dic = {'status': res_err, 'data': {}}
    else:
        value_dic = {'status': 0, 'data': {}}
        for line in res_msg:
            line = line.split()
            nic_name, t_in, t_out = line[1], line[4], line[5]
            value_dic['data'][nic_name] = {"t_in": line[4], "t_out": line[5]}

    return value_dic
