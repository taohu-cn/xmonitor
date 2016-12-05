# -*- coding: utf-8 -*-
# __author__: taohu

# import sys
# reload(sys)
# sys.setdefaultencoding("utf-8")
from django import template
from api import models
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def trigger_context(data):
    expressions = data['positive_expressions']

    html = ''
    for expression_item in expressions:
        expression_obj = models.TriggerExpression.objects.get(id=expression_item['expression_obj'])
        line = '''<p>service:{service} index:{service_index} operator:{operator} func:{calc_func} args:{calc_args}
        threshold:{threshold} calc_res:{calc_res}  real_val:{real_val}
                </p>'''.format(service=expression_obj.service.name,
                               service_index=expression_obj.service_index.name,
                               operator=expression_obj.operator_type,
                               calc_func=expression_obj.data_calc_func,
                               calc_args=expression_obj.data_calc_args,
                               threshold=expression_obj.threshold,
                               calc_res=expression_item.get('calc_res'),
                               real_val=expression_item.get('calc_res_val')
                               )
        html += line

    return mark_safe(html)
