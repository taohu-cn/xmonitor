# -*- coding: utf-8 -*-
# __author__: taohu

# import sys
# reload(sys)
# sys.setdefaultencoding("utf-8")
import subprocess
from xclient.plugins.linux.data_format_convert import data_format_convert


def monitor():
    cmd = 'uptime'
    res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    res_err = res.stderr.read()
    res_msg = data_format_convert(res.stdout.read())

    if res_err:
        value_dic = {'status': res_err}
    else:
        days = res_msg.split(',')[0].split('up')[1].split('days')[0].strip()
        hours = res_msg.split(',')[1].split(':')[0].strip()
        minutes = res_msg.split(',')[1].split(':')[1].strip()
        load1, load5, load15 = res_msg.split('load average:')[1].split(',')

        value_dic = {
            'uptime': days + 'd ' + hours + 'h ' + minutes + 'm',
            'load1': load1,
            'load5': load5,
            'load15': load15,
            'status': 0
        }
    return value_dic


if __name__ == '__main__':
    print(monitor())
