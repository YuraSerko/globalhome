# -*- coding=utf-8 -*-
# Create your views here.
FREESWITCH = {
    'fs1': {
        'SSH_HOST': '192.168.20.12',
        'SSH_USER': 'freeswitch',
        'SSH_PORT': 22,
        'SSH_PASSWORD': 'ahbcdbx!@',
        'ESL_HOST': '192.168.20.12',
        'ESL_PORT': '8021',
        'ESL_PASSWORD': 'ClueCon'
    },

}

import paramiko, scp
from scp import SCPClient

##### Скрипт копирующий файл!!!!
from socket import timeout as SocketTimeout
def createSSHClient(server, port, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client

for x in FREESWITCH:
    print "'%s %s %s %s'" % (FREESWITCH[x]['SSH_HOST'], FREESWITCH[x]['SSH_PORT'], FREESWITCH[x]['SSH_USER'], FREESWITCH[x]['SSH_PASSWORD'])
    ssh = createSSHClient(FREESWITCH[x]['SSH_HOST'], FREESWITCH[x]['SSH_PORT'], FREESWITCH[x]['SSH_USER'], FREESWITCH[x]['SSH_PASSWORD'])
    scp = SCPClient(ssh.get_transport())
    str3 = file_in + '.wav'
    scp.put(str3, "/usr/local/freeswitch/sounds/ru/RU/elena/gh/8000/myivr")
##### Конец скрипта

