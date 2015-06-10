# -*- coding=utf-8 -*-
from django.conf import settings
from django.conf.urls import patterns, url, include
from django.contrib import admin

urlpatterns = patterns('call_forwarding.views',
    url(r'^$', 'rules_list', name="callforwarding_rules_list"),
    url(r'^edit_rule/(?P<rule_id>\d+)/$', 'rule_edit', name='rule_edit'),
    url(r'^delete_rule/(?P<rule_id>\d+)/$', 'rule_delete', name='rule_delete'),
    url(r'^add_rule/$', 'rule_add', name='rule_add'),
    url(r'^check_rule/$', 'check_rule', name='check_rule'),
)
