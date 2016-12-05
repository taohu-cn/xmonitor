# -*- coding: utf-8 -*-
# __author__: taohu

# import sys
# reload(sys)
# sys.setdefaultencoding("utf-8")

configs = {
    'HostID': 1,
    "Server": "127.0.0.1",
    "ServerPort": 9001,

    'get': 'api/client/config',  # acquire all the services will be monitored
    'post': 'api/client/service/report',

    'RequestTimeout': 30,
    'ConfigUpdateInterval': 300,  # 5 mins as default

}
