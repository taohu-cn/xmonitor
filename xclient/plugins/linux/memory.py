# -*- coding: utf-8 -*-
# __author__: taohu

# import sys
# reload(sys)
# sys.setdefaultencoding("utf-8")
import subprocess
from xclient.plugins.linux.data_format_convert import data_format_convert


def monitor(frist_invoke=1):
    monitor_dic = {
        'SwapUsage': 'percentage',
        'MemUsage': 'percentage',
    }

    cmd = "grep 'MemTotal\|MemFree\|Buffers\|^Cached\|SwapTotal\|SwapFree' /proc/meminfo | awk -F 'kB' '{print $1}'"
    res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    res_err = res.stderr.read()
    res_msg = data_format_convert(res.stdout.read())

    if res_err:  # cmd exec error
        value_dic = {'status': res_err}
    else:
        value_dic = {'status': 0}
        for line in res_msg.split('\n'):
            if not line:
                continue
            key = line.split(':')[0]  # factor name
            value = line.split(':')[1].strip()  # factor value
            value_dic[key] = value

        if monitor_dic['SwapUsage'] == 'percentage':
            value_dic['SwapUsage_p'] = str(100 - int(value_dic['SwapFree']) * 100 / int(value_dic['SwapTotal']))
        # real SwapUsage value
        value_dic['SwapUsage'] = int(value_dic['SwapTotal']) - int(value_dic['SwapFree'])

        MemUsage = int(value_dic['MemTotal']) - (
            int(value_dic['MemFree']) + int(value_dic['Buffers']) + int(value_dic['Cached']))
        if monitor_dic['MemUsage'] == 'percentage':
            value_dic['MemUsage_p'] = str(int(MemUsage) * 100 / int(value_dic['MemTotal']))
        # real MemUsage value
        value_dic['MemUsage'] = MemUsage
    return value_dic


if __name__ == '__main__':
    print(monitor())
