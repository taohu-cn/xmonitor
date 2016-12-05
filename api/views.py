# -*- coding: utf-8 -*-
# __author__: taohu

# import sys
# reload(sys)
# sys.setdefaultencoding("utf-8")
import json
from xmonitor import settings
from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from api import graphs
from api import models
from api import serializer
from api.serializer import ClientHandler, get_host_triggers
from api.backends import redis_conn
from api.backends import data_optimization
from api.backends import data_processing

REDIS_OBJ = redis_conn.redis_conn(settings)


def index(request):
    return render(request, 'monitor/index.html')


def dashboard(request):
    return render(request, 'monitor/dashboard.html')


def triggers(request):
    return render(request, 'monitor/triggers.html')


def hosts(request):
    host_list = models.Host.objects.all()
    return render(request, 'monitor/hosts.html', {'host_list': host_list})


def host_detail(request, host_id):
    host_obj = models.Host.objects.get(id=host_id)
    return render(request, 'monitor/host_detail.html', {'host_obj': host_obj})


def host_detail_old(request, host_id):
    host_obj = models.Host.objects.get(id=host_id)

    config_obj = ClientHandler(host_obj.id)
    monitored_services = {
        "services": {},
        "sub_services": {}  # 存储一个服务有好几个独立子服务 的监控,比如网卡服务 有好几个网卡
    }

    template_list = list(host_obj.templates.select_related())

    for host_group in host_obj.host_groups.select_related():
        template_list.extend(host_group.templates.select_related())
    print('\033[1;33m %s \033[0m' % __file__, template_list)
    for template in template_list:
        # print(template.services.select_related())

        for service in template.services.select_related():  # loop each service
            print(service)
            if not service.has_sub_service:
                monitored_services['services'][service.name] = [service.plugin_name, service.interval]
            else:
                monitored_services['sub_services'][service.name] = []

                # get last point from redis in order to acquire the sub-service-key
                last_data_point_key = "StatusData_%s_%s_latest" % (host_obj.id, service.name)
                last_point_from_redis = REDIS_OBJ.lrange(last_data_point_key, -1, -1)[0]
                if last_point_from_redis:
                    data, data_save_time = json.loads(last_point_from_redis)
                    if data:
                        service_data_dic = data.get('data')
                        for serivce_key, val in service_data_dic.items():
                            monitored_services['sub_services'][service.name].append(serivce_key)

    return render(request, 'host_detail.html', {'host_obj': host_obj, 'monitored_services': monitored_services})


def hosts_status(request):
    hosts_data_serializer = serializer.StatusSerializer(request, REDIS_OBJ)
    hosts_data = hosts_data_serializer.by_hosts()

    return HttpResponse(json.dumps(hosts_data))


# 获取配置
def client_configs(request, client_id):
    print("--->", client_id)
    config_obj = ClientHandler(client_id)
    config = config_obj.fetch_configs()

    if config:
        return HttpResponse(json.dumps(config))


@csrf_exempt
def service_data_report(request):
    data = json.loads(request.POST['data'])
    client_id = request.POST.get('client_id')
    service_name = request.POST.get('service_name')
    # 数据优化及存储
    data_saveing_obj = data_optimization.DataStore(client_id, service_name, data, REDIS_OBJ)

    # redis_key_format = "StatusData_%s_%s_latest" %(client_id,service_name)
    # data['report_time'] = time.time()
    # REDIS_OBJ.lpush(redis_key_format,json.dumps(data))

    # 在这里同时触发监控
    host_obj = models.Host.objects.get(id=client_id)
    service_triggers = get_host_triggers(host_obj)

    trigger_handler = data_processing.DataHandler(settings, connect_redis=False)
    for trigger in service_triggers:
        trigger_handler.load_service_data_and_calulating(host_obj, trigger, REDIS_OBJ)
    print("service trigger::", service_triggers)

    # 更新主机存活状态
    # host_alive_key = "HostAliveFlag_%s" % client_id
    # REDIS_OBJ.set(host_alive_key,time.time())

    return HttpResponse(json.dumps("---report success---"))


def graphs_gerator(request):
    graphs_generator = graphs.GraphGenerator2(request, REDIS_OBJ)
    graphs_data = graphs_generator.get_host_graph()

    return HttpResponse(json.dumps(graphs_data))


def graph_bak(request):
    # host_id = request.GET.get('host_id')
    # service_key = request.GET.get('service_key')

    # print("graph:", host_id,service_key)

    graph_generator = graphs.GraphGenerator(request, REDIS_OBJ)
    graph_data = graph_generator.get_graph_data()
    if graph_data:
        return HttpResponse(json.dumps(graph_data))


def trigger_list(request):
    trigger_handle_obj = serializer.TriggersView(request, REDIS_OBJ)
    trigger_data = trigger_handle_obj.fetch_related_filters()

    return render(request, 'monitor/trigger_list.html', {'trigger_list': trigger_data})
