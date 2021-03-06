# -*- coding: utf-8 -*-
# __author__: taohu

# import sys
# reload(sys)
# sys.setdefaultencoding("utf-8")

from api import models
import json
import time
from api.byte_to_str import ByteToStr


class ClientHandler(object):
    def __init__(self, client_id):
        self.client_id = client_id
        self.client_configs = {
            "services": {}
        }

    def fetch_configs(self):
        host_obj = models.Host.objects.get(id=self.client_id)
        template_list = list(host_obj.templates.select_related())

        for host_group in host_obj.groups.select_related():
            template_list.extend(host_group.templates.select_related())

        for template in template_list:
            for service in template.services.select_related():  # loop each service
                self.client_configs["services"][service.name] = [service.plugin_name, service.interval]

        return self.client_configs


def get_host_triggers(host_obj):
    # host_obj = models.Host.objects.get(id=2)
    triggers = []
    for template in host_obj.templates.select_related():
        triggers.extend(template.triggers.select_related())
    for group in host_obj.groups.select_related():
        for template in group.templates.select_related():
            triggers.extend(template.triggers.select_related())

    return set(triggers)


class TriggersView(object):
    def __init__(self, request, redis):
        self.request = request
        self.redis = redis

    def fetch_related_filters(self):
        by_host_id = self.request.GET.get("by_host_id")
        print("\033[1;33m %s \033[0m" % __file__, "fetch_related_filters", "host id:", by_host_id)
        # by_host_id = self.request.GET.get("by_host_id")
        host_obj = models.Host.objects.get(id=by_host_id)
        trigger_dic = {}
        if by_host_id:
            trigger_match_keys = "host_%s_trigger_*" % by_host_id
            trigger_keys = self.redis.keys(trigger_match_keys)
            print(trigger_keys)
            for key in trigger_keys:
                data = json.loads(self.redis.get(key))
                if data.get("trigger_id"):
                    trigger_obj = models.Trigger.objects.get(id=data.get("trigger_id"))
                    data["trigger_obj"] = trigger_obj
                data["host_obj"] = host_obj
                trigger_dic[key] = data

        return trigger_dic


class StatusSerializer(ByteToStr):
    """展示所有主机列表"""

    def __init__(self, request, redis):
        self.request = request
        self.redis = redis
        super(StatusSerializer, self).__init__()

    def by_hosts(self):
        """
        serialize all the hosts
        :return:
        """
        host_obj_list = models.Host.objects.all()
        host_data_list = []
        for h in host_obj_list:
            host_data_list.append(self.single_host_info(h))
        return host_data_list

    def single_host_info(self, host_obj):
        """
        serialize single host into a dic
        :param host_obj:
        :return:
        """
        data = {
            "id": host_obj.id,
            "name": host_obj.name,
            "ip": host_obj.ip,
            "status": host_obj.get_status_display(),
            "uptime": None,
            "last_update": None,
            "total_services": None,
            "ok_nums": None,

        }

        # for uptime
        uptime = self.get_host_uptime(host_obj)
        self.get_triggers(host_obj)
        if uptime:
            data["uptime"] = uptime[0]["uptime"]
            data["last_update"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(uptime[1]))

        # for triggers
        data["triggers"] = self.get_triggers(host_obj)

        return data

    def get_host_uptime(self, host_obj):
        """
        get host uptime data
        :param host_obj:
        :return:
        """

        redis_key = "StatusData_%s_Life_latest" % host_obj.id
        last_data_point = self.redis.lrange(redis_key, -1, -1)
        if last_data_point:
            last_data_point = self.converter(last_data_point[0])
            last_data_point, last_update = json.loads(last_data_point)
            return last_data_point, last_update

    def get_triggers(self, host_obj):
        trigger_keys = self.redis.keys("host_%s_trigger_*" % host_obj.id)
        # print("trigger keys:",trigger_keys)
        """ (1,"Information"),
        (2,"Warning"),
        (3,"Average"),
        (4,"High"),
        (5,"Diaster"), """
        trigger_dic = {
            1: [],
            2: [],
            3: [],
            4: [],
            5: []
        }

        for trigger_key in trigger_keys:
            trigger_data = self.redis.get(trigger_key)
            if trigger_key.endswith("None"):
                trigger_dic[4].append(json.loads(trigger_data))
            else:
                trigger_id = trigger_key.split("_")[-1]
                trigger_obj = models.Trigger.objects.get(id=trigger_id)
                trigger_dic[trigger_obj.severity].append(json.loads(trigger_data))

        # print("triiger data",trigger_dic)
        return trigger_dic
