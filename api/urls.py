# -*- coding: utf-8 -*-
# __author__: taohu

# import sys
# reload(sys)
# sys.setdefaultencoding("utf-8")

from django.conf.urls import url

from api import views

urlpatterns = [
    # 默认页
    url(r'^$', views.index),
    # 获取配置
    url(r'client/config/(\d+)/$', views.client_configs),
    # 汇报数据
    url(r'client/service/report/$', views.service_data_report),

    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^triggers/$', views.triggers, name='triggers'),
    url(r'hosts/$', views.hosts, name='hosts'),
    url(r'hosts/(\d+)/$', views.host_detail, name='host_detail'),
    url(r'trigger_list/$', views.trigger_list, name='trigger_list'),

    url(r'hosts/status/$', views.hosts_status, name='get_hosts_status'),
    url(r'graphs/$', views.graphs_gerator, name='get_graphs')
]
