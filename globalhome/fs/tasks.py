from celery.decorators import task
from celery.decorators import periodic_task
from celery.task.schedules import crontab
from datetime import timedelta
import os
import sys
import time
#sys.path[0] = '../'
#os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from settings import SCRIPT_ROOT

@task()
def delayed_function(id, type_obzvon):
    print id
    #from obzvon import createSSHClient
    print "alalalalalalalalalalalalalalala1"
    try:
#        ssh = createSSHClient(FREESWITCH['fs1']['SSH_HOST'], FREESWITCH['fs1']['SSH_PORT'], FREESWITCH['fs1']['SSH_USER'], FREESWITCH['fs1']['SSH_PASSWORD'])
#        # command = "/usr/local/freeswitch/python/potok_for_obzvon.py %s %s %s" % (model.from_number, model.id, model.file)
#        command = "/usr/local/freeswitch/python/potok_for_obzvon.py %s %s > /usr/local/freeswitch/python/log.log &" % (id, type_obzvon)
#        print command
#        stdin, stdout, stderr = ssh.exec_command(command)
        print "/home/sites/gh/venv/bin/python %s/potok_for_obzvon.py %s %s" % (SCRIPT_ROOT, id, type_obzvon)
        os.system("""/home/sites/gh/venv/bin/python %s/potok_for_obzvon.py %s %s""" % (SCRIPT_ROOT, id, type_obzvon))
    except Exception, e:
        print e