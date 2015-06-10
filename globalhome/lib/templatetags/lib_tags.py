# -*- coding=utf-8 -*-
# $Id$

from django import template

register = template.Library()

@register.simple_tag
def display_model_field(model_object, field_name, no_value=None):
    value = None
    try:
        value = model_object.__getattribute__('get_%s_display' % field_name)()
    except AttributeError:
        try:
            value = model_object.__getattribute__(field_name)
        except AttributeError:
            return u'NULL'
    if not value and no_value:
        return no_value
    return value

