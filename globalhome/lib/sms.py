#!/usr/bin/env python
# -*-coding=utf-8-*-


from lib.smsc import SMSC
import urllib2
from devinotele import rest_service
import time
from tasks import send_sms_task, send_sms_task1
from datetime import datetime

def send_sms_old(to_number, sms_text):
    smsc = SMSC()
    r = smsc.send_sms(to_number, sms_text)
    if r[1] > "0":
        return True
    else:
        return False

def send_sms1(to_number, sms_text, log=None):
    send_sms_task1.apply_async((to_number, sms_text), eta=datetime.now())
    return True

def send_sms(to_number, sms_text, log=None):
    send_sms_task.apply_async((to_number, sms_text), eta=datetime.now())
    return True
#    """ Пример использования класса RestApi.
#        У REST-сервиса не предусмотрен demo-режим, все действия совершаются в боевом режиме.
#        То есть при вызове функции SendMessage сообщения реально отправляются.
#        Будьте внимательны при вводе адреса отправителя и номеров получателей."""
#
#    login = 'GlobalHome01'
#    password = 'Ndjhtw@#4'
#    host = 'https://integrationapi.net/rest'
#
#    try:
#        rest = rest_service.RestApi(login, password, host)
#    except urllib2.URLError as error:
#        # print(error.code, error.msg)
#        if log:
#            log.add("send_sms except %s" % str(error))
#        return False
#
#    message_ids = rest.send_message('GlobalHome', to_number, sms_text)
#    # message_ids = rest.send_message('адрес отправителя', 'номер получателя', 'Hello, world!')
#    # statistics = rest.get_statistics(datetime.date(2012, 3, 12), datetime.date(2012, 5, 8))
#    st = None
#    limit = 5
#    while st == None or limit:
#        state = rest.get_message_state(message_ids[0])
#        if state['State'] == 0:
#            return True
#        time.sleep(1)
#        limit -= 1
#    if log:
#        log.add("send_sms status %s" % str(state['State']))
#    return True
