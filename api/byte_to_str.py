# -*- coding: utf-8 -*-
# __author__: taohu

import sys


# reload(sys)
# sys.setdefaultencoding("utf-8")

class ByteToStr(object):
    # def __init__(self, data):
    #     self.data = data

    @staticmethod
    def converter(data):
        if sys.version.split('.')[0] == '3':
            data = str(data, encoding='utf-8')
        elif sys.version.split('.')[0] == '2':
            data = str(data)
        return data
