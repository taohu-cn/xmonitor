# -*- coding: utf-8 -*-
# __author__: taohu

# import sys
# reload(sys)
# sys.setdefaultencoding("utf-8")

from xmonitor import settings
import sys
import time
import json
import copy


class DataStore(object):
    """processing the reported data , do some data optimiaztion and save it into redis DB"""

    def __init__(self, client_id, service_name, data, redis_obj):
        """
        :param client_id:
        :param service_name:
        :param data: the client reported service clean data
        :return:
        """
        self.py_version = sys.version.split('.')[0]
        self.client_id = client_id
        self.service_name = service_name
        self.data = data
        self.redis_conn_obj = redis_obj
        self.process_and_save()

    def converter(self, data):
        if self.py_version == '3':
            if type(data) is bytes:
                data = str(data, encoding='utf-8')
        elif self.py_version == '2':
            data = str(data)
        return data

    def process_and_save(self):
        """
        :func: processing data and save into redis
        :return:
        """
        if self.data["status"] == 0:

            # for key, data_store_definition in {'latest': [0, 600]}.items()
            for key, data_store_definition in settings.STATUS_DATA_OPTIMIZATION.items():
                data_series_key_in_redis = "StatusData_%s_%s_%s" % (self.client_id, self.service_name, key)

                last_point_from_redis = self.redis_conn_obj.lrange(data_series_key_in_redis, -1, -1)
                if not last_point_from_redis:  # the key doesn't exist in redis, then generate a timestamp
                    self.redis_conn_obj.rpush(data_series_key_in_redis, json.dumps([None, time.time()]))

                if data_store_definition[0] == 0:  # save Real-time data
                    self.redis_conn_obj.rpush(data_series_key_in_redis, json.dumps([self.data, time.time()]))

                else:  # data might needs to be optimized
                    last_saved_data_b = self.redis_conn_obj.lrange(data_series_key_in_redis, -1, -1)[0]
                    last_saved_data_s = self.converter(last_saved_data_b)
                    last_saved_data_j = json.loads(last_saved_data_s)
                    last_point_data, last_point_save_time = last_saved_data_j

                    # 超出更新时间间隔, 取最新数据, 再次生成优化的数据
                    if time.time() - last_point_save_time >= data_store_definition[0]:
                        lastest_data_key_in_redis = "StatusData_%s_%s_latest" % (self.client_id, self.service_name)
                        data_set = self.get_data_slice(lastest_data_key_in_redis, data_store_definition[0])

                        if data_set:
                            # 优化数据集
                            optimized_data = self.get_optimized_data(data_series_key_in_redis, data_set)
                            if optimized_data:
                                self.save_optimized_data(data_series_key_in_redis, optimized_data)

                # 同时确保数据在redis中的存储数量不超过settings中指定 的值
                if self.redis_conn_obj.llen(data_series_key_in_redis) >= data_store_definition[1]:
                    self.redis_conn_obj.lpop(data_series_key_in_redis)  # 删除最旧的一个数据
        else:
            print("report data is invalid::", self.data)
            raise ValueError

    def get_data_slice(self, lastest_data_key, optimization_interval):
        """
        :param lastest_data_key:
        :param optimization_interval: e.g: 600, means get latest 10 mins real data from redis
        :return:
        """
        all_real_data = self.redis_conn_obj.lrange(lastest_data_key, 1, -1)
        # all_real_data = self.converter(all_real_data)
        data_set = []
        for item in all_real_data:
            data = json.loads(self.converter(item))
            if len(data) == 2:
                service_data, last_save_time = data
                if time.time() - last_save_time <= optimization_interval:  # filter this data point out
                    data_set.append(data)
                else:
                    pass
        return data_set

    def save_optimized_data(self, data_series_key_in_redis, optimized_data):
        """
        save the optimized data into db
        :param data_series_key_in_redis:
        :param optimized_data:
        :return:
        """
        self.redis_conn_obj.rpush(data_series_key_in_redis, json.dumps([optimized_data, time.time()]))

    def get_optimized_data(self, data_set_key, data_set):
        """
        calculate out ava,max,min,mid value from raw service data set
        :param data_set_key: where the optimized data needed to save to in redis db
        :param data_set: [ [{'steal': '0.00', ..., 'status': 0}, 1480485017.90692], ..., ]
        :param data_set: [ [{'data': {'em1': {'t_out': '0.00', 't_in': '0.00'}, ...,}, 'status': 0}, 1480506115.061609]]
        :return:
        """
        optimized_dic = {}  # set a empty dic, will save optimized data later
        service_data_keys = data_set[0][0].keys()  # [iowait, idle, system...] 或者 [data]
        first_service_data_point = data_set[0][0]  # use this to build up a new empty dic

        if "data" not in service_data_keys:  # means this dic has no subdic, works for service like cpu,memory
            for key in service_data_keys:
                optimized_dic[key] = []  # {'nice': [], 'idle': [], ..., 'system': []}

            # 把数据按照指标转储成列表形式
            for service_data_item, last_save_time in data_set:  # service_data_item: {}, last_save_time: timestamp
                for k, v in service_data_item.items():
                    optimized_dic[k].append(round(float(v), 2))

            for service_k, v_list in optimized_dic.items():
                avg_res = self.get_average(v_list)
                max_res = self.get_max(v_list)
                min_res = self.get_min(v_list)
                mid_res = self.get_mid(v_list)
                optimized_dic[service_k] = [avg_res, max_res, min_res, mid_res]
            print(optimized_dic)
        else:
            """
            has sub dic, inside key is "data".
            works for a service has multiple independent items, like many ethernet/disks and so on.
            first_service_data_point: {'data': {'em1': {'t_out': '0.00', 't_in': '0.00'}, ...,}, 'status': 0}
            """
            # 生成数据存储字典的格式
            for service_item_key, v_dic in first_service_data_point["data"].items():
                optimized_dic[service_item_key] = {}
                for k2, v2 in v_dic.items():
                    optimized_dic[service_item_key][k2] = []  # {etho0:{t_in:[],t_out:[]}}

            tmp_data_dic = copy.deepcopy(optimized_dic)
            if tmp_data_dic:  # some times this tmp_data_dic might be empty due to client report err
                for service_data_item, last_save_time in data_set:
                    for service_index, val_dic in service_data_item["data"].items():  # service_index: eth0, eth1...
                        for service_item_sub_key, val in val_dic.items():  # service_item_sub_key: t_in, t_out

                            tmp_data_dic[service_index][service_item_sub_key].append(round(float(val), 2))

                for service_k, v_dic in tmp_data_dic.items():
                    for service_sub_k, v_list in v_dic.items():
                        avg_res = self.get_average(v_list)
                        max_res = self.get_max(v_list)
                        min_res = self.get_min(v_list)
                        mid_res = self.get_mid(v_list)
                        optimized_dic[service_k][service_sub_k] = [avg_res, max_res, min_res, mid_res]

            else:
                print("\033[41;1mMust be sth wrong with client report data\033[0m")
        print("optimized empty dic:", optimized_dic)

        return optimized_dic

    def get_average(self, data_set):
        """
        calc the avg value of data set
        :param data_set:
        :return:
        """
        if len(data_set) > 0:
            res = sum(data_set) / len(data_set)
            return round(res, 2)
        else:
            return 0

    def get_max(self, data_set):
        """
        calc the max value of the data set
        :param data_set:
        :return:
        """
        if len(data_set) > 0:
            return max(data_set)
        else:
            return 0

    def get_min(self, data_set):
        """
        calc the minimum value of the data set
        :param data_set:
        :return:
        """
        if len(data_set) > 0:
            return min(data_set)
        else:
            return 0

    def get_mid(self, data_set):
        """
        calc the mid value of the data set
        :param data_set:
        :return:
        """
        data_set.sort()
        # [1,4,99,32,8,9,4,5,9]
        # [1,3,5,7,9,22,54,77]
        if len(data_set) > 0:
            return data_set[int(len(data_set) / 2)]
        else:
            return 0
