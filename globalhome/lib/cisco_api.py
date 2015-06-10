# -*- coding=utf-8 -*-

import getpass
import sys
import telnetlib
DEBUG = False
cisco_errors = {1: 'Not answer',
                2: 'Bad login password',
                3: 'Bad enable password',
                4: 'Can not switch to the configuration mode',
                5: 'Unknown interface',
                6: 'Can not enable port',
                7: 'Can not write configuration',
                }

class CiscoException(Exception):
    def __init__(self, code):
        self.code = code
    def __str__(self):
        return "%s, %s" % (self.code, cisco_errors[self.code])


class Cisco:
    def __init__(self, ip, password):
        self.ip = ip
        self.password = password
        self.tn = None
        self.connected = False
        self.enable_mode = False
        self.config_mode = False

    def connect(self):
        self.tn = telnetlib.Telnet(self.ip, timeout=5)
        if not self.login():
            raise CiscoException(1)
        self.connected = True

    def login(self):
        r = self.tn.read_until("Password:", timeout=5)
        if DEBUG:
            print r
        self.tn.write(self.password + "\n")
        r = self.tn.read_until(">", timeout=5)
        if DEBUG:
            print r
        if r[-1:] != '>':
            raise CiscoException(2)
        return True

    def enable(self):
        if not self.connected:
            self.connect()
        self.tn.write("enable\n")
        r = self.tn.read_until("Password:", timeout=5)
        if DEBUG:
            print r
        self.tn.write(self.password + "\n")
        r = self.tn.read_until("#", timeout=5)
        if DEBUG:
            print r
        if r[-1:] != '#':
            raise CiscoException(3)
        self.enable_mode = True


    def config(self):
        if not self.enable_mode:
            self.enable()
        self.tn.write("conf t\n")
        r = self.tn.read_until("(config)#", timeout=5)
        if DEBUG:
            print r
        if r[-9:] != '(config)#':
            raise CiscoException(4)

        self.config_mode = True



    def enableport(self, port, save_config=True):
        if not self.config_mode:
            self.config()

        self.tn.write("int %s\n" % port)
        r = self.tn.read_until("(config-if)#", timeout=5)
        if DEBUG:
            print r
        if r[-12:] != '(config-if)#':
            raise CiscoException(5)

        self.tn.write("no shutdown\n")
        r = self.tn.read_until("#")
        if DEBUG:
            print r
        if r[-12:] != '(config-if)#':
            raise CiscoException(6)
        self.tn.write("exit\n")
        if save_config:
            self.write_config()

    def write_config(self):
        if self.config_mode:
            self.tn.write("exit\n")
            self.config_mode = False
        if not self.enable_mode:
            self.enable()

        self.tn.write("wr\n")
        r = self.tn.read_until("[OK]", timeout=20)
        if DEBUG:
            print r
        if r[-4:] != '[OK]':
            raise CiscoException(7)
        r = self.tn.read_until("#")
        if DEBUG:
            print r
        return True

    def disableport(self, port, save_config=True):
        if not self.config_mode:
            self.config()

        self.tn.write("int %s\n" % port)
        r = self.tn.read_until("(config-if)#", timeout=5)
        if DEBUG:
            print r
        if r[-12:] != '(config-if)#':
            raise CiscoException(5)

        self.tn.write("shutdown\n")
        r = self.tn.read_until("#")
        if DEBUG:
            print r
        if r[-12:] != '(config-if)#':
            raise CiscoException(6)
        self.tn.write("exit\n")
        if save_config:
            self.write_config()


    def disconnect(self):
        self.tn.close()
        self.connected = False
        self.enable_mode = False
        self.config_mode = False


if __name__ == '__main__':
    DEBUG = True
    # пример использования
    try:
        s = Cisco("172.16.0.129", "rhtgjcnm$%^")
        s.disableport("Fa0/20")
    except Exception as e:
        print e
    else:
        s.disconnect()
