# -*- coding=utf-8 -*-

# from django.conf import settings
from django.conf.urls import *
# from django.contrib import admin

urlpatterns = patterns('fs.views',

    # url(r'^disable_forward/$', 'disable_forward'),



    # ##record_talk
    url(r'^list_record_tariff/$', 'list_record_talk_tariff', name="list_record_talk_tariff"),
    url(r'^deactivate_tariff/$', 'deactivate_tariff', name="deactivate_tariff"),
    url(r'^activation_tariff/(?P<tariff_id>\d+)/$', 'activation_tariff', name="activation_tariff"),
    url(r'^change_activation_tariff/(?P<tariff_id>\d+)/$', 'change_activation_tariff', name="change_activation_tariff"),
    url(r'^create_record_talk/$', 'create_record_talk', name="create_record_talk"),
    url(r'^delete/(?P<record_id>\d+)/$', 'delete_record_talk', name="delete_record_talk"),
    url(r'^edit/(?P<record_id>\d+)/$', 'edit_record_talk', name="edit_record_talk"),
    url(r'^listen/(?P<record_id>\d+)/$', 'listen_record_talk', name="listen_record_talk"),
    url(r'^change_tariff/$', 'list_record_talk_tariff_change', name="list_record_talk_tariff_change"),
    url(r'^myarchive/$', 'myarchive', name="myarchive"),
    url(r'^myarchive/(?P<numb>\d+)/$', 'myarchive', name="myarchive_one"),
)

