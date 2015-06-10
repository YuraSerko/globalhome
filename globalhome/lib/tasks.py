# -*- coding=utf-8 -*-

from celery.decorators import task
from celery.decorators import periodic_task
from celery.task.schedules import crontab
from datetime import timedelta
import os
import sys
import time
from lib.smsc import SMSC
import urllib2
from devinotele import rest_service
import time
from celery import Task
from lib.smsc import SMSC

class MyTask(Task):
    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        if self.max_retries == self.request.retries:
            print "MAX RETRIES OVER !!!"
            print status
            # If max retries is equal to task retries do something

@task(base=MyTask, max_retries=3)
def send_sms_task1(to_number, sms_text, log=None):
    login = 'GlobalHome01'
    password = 'Ndjhtw@#4'
    host = 'https://integrationapi.net/rest'
    # print "aaaa"
    try:
        rest = rest_service.RestApi(login, password, host)
        message_ids = rest.send_message('GlobalHome', to_number, sms_text)
    except (urllib2.URLError, urllib2.HTTPError) as error:
        # print(error.code, error.msg)
        if log:
            log.add("send_sms except %s" % str(error))
        print "aaaa11error"
        print error
        raise send_sms_task.retry(args=[to_number, sms_text], exc=error, countdown=30)  # повторяет таск
        return False


    # message_ids = rest.send_message('адрес отправителя', 'номер получателя', 'Hello, world!')
    # statistics = rest.get_statistics(datetime.date(2012, 3, 12), datetime.date(2012, 5, 8))
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

    return True

@task(base=MyTask, max_retries=3)
def send_sms_task(to_number, sms_text, log=None):
    try:
        smsc = SMSC()
        r = smsc.send_sms(to_number, sms_text)
        if r[1] > "0":
            return True
        else:
            return False
    except Exception as error:
        # print(error.code, error.msg)
        if log:
            log.add("send_sms except %s" % str(error))
        # print "aaaa11error"
        raise send_sms_task.retry(args=[to_number, sms_text], exc=error, countdown=30)  # повторяет таск
        return False
    return True

if __name__ == '__main__':
    send_sms_task('375256182928', 'test_sms', log=None)
