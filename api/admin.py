# -*- coding: utf-8 -*-
# __author__: taohu

# import sys
# reload(sys)
# sys.setdefaultencoding("utf-8")
from django.contrib import admin

from api import models


# Register your models here.

class HostAdmin(admin.ModelAdmin):
    list_display = ('id', 'ip', 'status')
    filter_horizontal = ('groups', 'templates')


class HostGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'memo')


class TemplateAdmin(admin.ModelAdmin):
    list_display = ('name',)
    filter_horizontal = ('services', 'triggers')


class ServiceAdmin(admin.ModelAdmin):
    filter_horizontal = ('items',)
    list_display = ('name', 'interval', 'plugin_name')
    # list_select_related = ('items',)


class ServiceIndexAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'data_type')


class TriggerExpressionInline(admin.TabularInline):
    model = models.TriggerExpression
    # exclude = ('memo',)
    # readonly_fields = ['create_date']


class TriggerAdmin(admin.ModelAdmin):
    list_display = ('name', 'severity', 'enabled')
    inlines = [TriggerExpressionInline, ]
    # filter_horizontal = ('expressions',)


class TriggerExpressionAdmin(admin.ModelAdmin):
    list_display = (
        'trigger', 'service', 'service_index', 'specified_index_key', 'operator_type', 'data_calc_func', 'threshold',
        'logic_type')


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'phone', 'weixin', 'email')


admin.site.register(models.Host, HostAdmin)
admin.site.register(models.HostGroup, HostGroupAdmin)
admin.site.register(models.Template, TemplateAdmin)
admin.site.register(models.Service, ServiceAdmin)
admin.site.register(models.Trigger, TriggerAdmin)
admin.site.register(models.TriggerExpression, TriggerExpressionAdmin)
admin.site.register(models.ServiceIndex, ServiceIndexAdmin)
admin.site.register(models.Action)
admin.site.register(models.ActionOperation)
admin.site.register(models.Maintenance)
admin.site.register(models.UserProfile, UserProfileAdmin)
