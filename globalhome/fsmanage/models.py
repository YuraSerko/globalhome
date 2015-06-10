# -*- coding=utf-8 -*-
from django.db import models
import time
# Create your models here.
class FSCalls(models.Model):
    class Meta:
       verbose_name_plural = "Онлайн звонки"
       managed = False

# Create your models here.
class sip_registrations(models.Model):
    call_id = models.CharField(max_length=50, primary_key=True)
    #sip_user = models.IntegerField(null=True, blank=True)
    sip_user = models.CharField(max_length=25)
    sip_host = models.CharField(max_length=25)
    presence_hosts = models.CharField(max_length=25)
    contact = models.CharField(max_length=255)
    status = models.CharField(max_length=75)
    rpid = models.CharField(max_length=75)
    expires = models.CharField(max_length=75)
    user_agent = models.CharField(max_length=75)
    server_user = models.CharField(max_length=75)
    server_host = models.CharField(max_length=75)
    profile_name = models.CharField(max_length=75)
    hostname = models.CharField(max_length=75)
    network_ip = models.CharField(max_length=75)
    network_port = models.CharField(max_length=75)
    sip_username = models.CharField(max_length=75)
    sip_realm = models.CharField(max_length=75)
    mwi_user = models.CharField(max_length=75)
    mwi_host = models.CharField(max_length=75)
    orig_server_host = models.CharField(max_length=75)
    orig_hostname = models.CharField(max_length=75)
    sub_host = models.CharField(max_length=75)

    def __unicode__(self):
        return self.sip_user

    def Time_exit(self):
        time_exit = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime(self.expires))
        return time_exit

    class Meta:
        db_table = "sip_registrations"
        verbose_name_plural = "Онлайн регистрации"
        managed = True


class sip_registrations_history(models.Model):
    call_id = models.CharField(max_length=255)
    #sip_user = models.IntegerField(null=True, blank=True)
    sip_user = models.CharField(max_length=25)
    sip_host = models.CharField(max_length=25)
    presence_hosts = models.CharField(max_length=25)
    contact = models.CharField(max_length=255)
    status = models.CharField(max_length=75)
    rpid = models.CharField(max_length=75)
    expires = models.CharField(max_length=75)
    user_agent = models.CharField(max_length=75)
    server_user = models.CharField(max_length=75)
    server_host = models.CharField(max_length=75)
    profile_name = models.CharField(max_length=75)
    hostname = models.CharField(max_length=75)
    network_ip = models.CharField(max_length=75)
    network_port = models.CharField(max_length=75)
    sip_username = models.CharField(max_length=75)
    sip_realm = models.CharField(max_length=75)
    mwi_user = models.CharField(max_length=75)
    mwi_host = models.CharField(max_length=75)
    orig_server_host = models.CharField(max_length=75)
    orig_hostname = models.CharField(max_length=75)
    sub_host = models.CharField(max_length=75)
    datetime = models.DateTimeField()

    def __unicode__(self):
        return self.sip_user

    def Time_exit(self):
        time_exit = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime(self.expires))
        return time_exit

    class Meta:
        db_table = "sip_registrations_history"
        verbose_name_plural = "История регистраций"
        managed = True
