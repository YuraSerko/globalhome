#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import sys

sys.path[0] = '../'
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
#from settings import SCRIPT_ROOT
#from fs.obzvon import createSSHClient
print "ololololololololololo1"
try:
#    ssh = createSSHClient(FREESWITCH['fs1']['SSH_HOST'], FREESWITCH['fs1']['SSH_PORT'], FREESWITCH['fs1']['SSH_USER'], FREESWITCH['fs1']['SSH_PASSWORD'])
#    # command = "/usr/local/freeswitch/python/potok_for_obzvon.py %s %s %s" % (model.from_number, model.id, model.file)
#    command = "/usr/local/freeswitch/python/potok_for_obzvon.py %s %s > /usr/local/freeswitch/python/log.log &" % (sys.argv[1], sys.argv[2])
#    print command
#    stdin, stdout, stderr = ssh.exec_command(command)
    print sys.argv[3]
    os.system("""/home/sites/gh/venv/bin/python %s/potok_for_obzvon.py %s %s""" % (sys.argv[3], sys.argv[1], sys.argv[2]))
except Exception, e:
    print e