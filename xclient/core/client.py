# -*- coding: utf-8 -*-
# __author__: taohu

# import sys
# reload(sys)
# sys.setdefaultencoding("utf-8"

import time
import sys
from xclient.conf import settings
import json
import threading
from xclient.plugins import plugin_api
from xclient.plugins.linux.data_format_convert import data_format_convert


class ClientHandle(object):
    def __init__(self):
        self.monitored_services = {}
        self.get = "http://%s:%s/%s/%s" % (
            settings.configs['Server'],
            settings.configs["ServerPort"],
            settings.configs['get'],
            settings.configs['HostID'])

        self.post = "http://%s:%s/%s/" % (
            settings.configs['Server'],
            settings.configs["ServerPort"],
            settings.configs['post'])

    # load the latest monitor configs from monitor server
    def load_latest_configs(self):
        latest_configs = self.httpget()
        latest_configs = json.loads(latest_configs)
        self.monitored_services.update(latest_configs)

    def forever_run(self):
        """
        :func: start the client program forever
        :return:
        """
        exit_flag = False
        config_last_update_time = 0
        while not exit_flag:
            # 是否重载配置
            if time.time() - config_last_update_time > settings.configs['ConfigUpdateInterval']:
                self.load_latest_configs()
                config_last_update_time = time.time()

            # self.monitored_services['services'] = {'services': {'Mem': ['n/a', 60], 'CPU': ['n/a', 60]}}
            for service_name, val in self.monitored_services['services'].items():
                # no timestamp in val, means it's the first time to monitor, add 0 as first timestamp
                if len(val) == 2:
                    # self.monitored_services['services'][service_name].append(0)
                    val.append(0)

                monitor_interval = val[1]  # u'监控间隔'
                last_invoke_time = val[2]  # u'上次监控时间'

                if time.time() - last_invoke_time > monitor_interval:  # needs to run the plugin
                    # u'更新时间戳'
                    self.monitored_services['services'][service_name][2] = time.time()

                    # start a new thread to call each monitor plugin
                    t = threading.Thread(target=self.invoke_plugin, args=(service_name, val))
                    t.start()
                    print("Going to monitor [%s]" % service_name)

                else:
                    print("Going to monitor [%s] in [%s] secs" % (service_name,
                                                                  monitor_interval - (time.time() - last_invoke_time)))

            time.sleep(1)

    def invoke_plugin(self, service_name, val):
        """
        invoke the monitor plugin here, and send the data to monitor server after plugin returned data each time
        :param service_name:
        :param val: [pulgin_name,monitor_interval,last_run_time]
        :return:
        """
        report_data = {
            'client_id': 1,
            'service_name': 'Net',
            'data': json.dumps(
                # {'status': 0, 'iowait': '0.00', 'system': '4.55', 'idle': '95.04', 'user': '0.41', 'steal': '0.00',
                #  'nice': '0.00'}
                {'status': 0,
                 'data': {'lo': {'t_in': '79.56', 't_out': '79.56'}, 'em1': {'t_in': '0.00', 't_out': '0.00'},
                          'em4': {'t_in': '0.00', 't_out': '0.00'}, 'em3': {'t_in': '102.65', 't_out': '15.47'},
                          'em2': {'t_in': '0.00', 't_out': '0.00'}}}
            )
        }
        self.httppost(params=report_data)
        # plugin_name = val[0]
        # if hasattr(plugin_api, plugin_name.lower()):
        #     func = getattr(plugin_api, plugin_name)
        #     plugin_callback = func()
        #
        #     report_data = {
        #         'client_id': settings.configs['HostID'],
        #         'service_name': service_name,
        #         'data': json.dumps(plugin_callback)
        #     }
        #
        #     print('---report data:', report_data)
        #     self.httppost(params=report_data)
        # else:
        #     print("\033[31;1mCannot find plugin names [%s] in plugin_api\033[0m" % plugin_name)
        # print('--plugin:', val)

    def httpget(self):
        print('\033[1m33m%s\033[0m' % __file__, self.get)
        if sys.version.split('.')[0] == '3':
            import urllib.request

            req = urllib.request.urlopen(self.get, data=None, timeout=settings.configs['RequestTimeout'])
            callback = data_format_convert(req.read())
            print('\033[1m33m%s\033[0m' % __file__, callback)
            return callback

        elif sys.version.split('.')[0] == '2':
            import urllib
            import urllib2

            req = urllib2.Request(self.get)
            req_data = urllib2.urlopen(req, timeout=settings.configs['RequestTimeout'])
            callback = req_data.read()
            return callback

    def httppost(self, **extra_data):
        print('\033[1m33m%s\033[0m' % __file__, self.post)
        if sys.version.split('.')[0] == '3':
            import urllib.request
            import urllib.parse

            data = urllib.parse.urlencode(extra_data['params'])
            data = data.encode('utf-8')
            request = urllib.request.Request(url=self.post)
            request.add_header("Content-Type", "application/x-www-form-urlencoded;charset=utf-8")
            f = urllib.request.urlopen(request, data)
            callback_msg = f.read().decode('utf-8')
            # print(callback_msg)

            return callback_msg

        elif sys.version.split('.')[0] == '2':
            import urllib
            import urllib2

            data_encode = urllib.urlencode(extra_data['params'])
            req = urllib2.Request(url=self.post, data=data_encode)
            res_data = urllib2.urlopen(req, timeout=settings.configs['RequestTimeout'])
            callback = res_data.read()
            callback = json.loads(callback)
            return callback
