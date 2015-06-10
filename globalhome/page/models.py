# -*- coding=UTF-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
import os
from django.core.validators import URLValidator


class LeftBlockMenuPage(models.Model):
    name = models.CharField(max_length=255, verbose_name=u'Название страницы')
    url = models.CharField(max_length=255, verbose_name=u'Ссылка на страницу (без доменнго имени)')
    parent = models.ForeignKey('self', null=True, verbose_name='Из подраздела какой старницы')
    position = models.IntegerField(verbose_name=u'Позиция пункта меню', default=1)
 
    def __unicode__(self):
        name = self.name
        obj = self
        while obj.parent != None:
            name = '%s -> %s' % (obj.parent.name, name)
            obj = obj.parent
        return name




class Send_mail(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    email = models.EmailField(verbose_name=_("To user"))
    user_id = models.IntegerField(null=True, blank=True, verbose_name=_("user_id"))
    subject = models.CharField(max_length=255, verbose_name=_("subject"))
    message = models.TextField(verbose_name=_("message"))
    date = models.DateTimeField(verbose_name=_("date"))
    spis_file = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("spis_file"))
    status_mail = models.BooleanField(default=False, verbose_name=_("status_mails"))
    sender_id = models.IntegerField(null=True, blank=True, verbose_name=_("sender_id"))

    def file_link(self):
        s = []
        if self.spis_file:
            for file in self.spis_file.split(", "):
                s.append('<a href="/media/' + file + '">' + (file[file.rfind('/') + 1:]) + '</a>')
            values = ', '.join(s)
            return values
            self.spis_file.allow_tags = True
        else:
            return "No attachment"
    file_link.allow_tags = True
    file_link.short_description = _(u"spis_file")





    class Meta:
        db_table = "db_send_mail"
        verbose_name = _(u"Send_message")
        verbose_name_plural = _(u"Send_messages")



USERS = (
    ('active', _(u"active_user")),
    ('juridical', _(u"juridical")),
    ('individual', _(u"individual")),
    ('admins', _(u"admins"))
)

class Message(models.Model):
    # The actual data - a pickled EmailMessage
    id = models.AutoField(primary_key=True, blank=True)
    users_type = models.CharField(max_length=13, choices=USERS, verbose_name=_(u"Type_user"))
    subject = models.CharField(max_length=255, verbose_name=_("subject"))
    message = models.TextField(blank=False, verbose_name=_("message"))
#     spis_file = models.FileField(u'File', upload_to="media/", blank=True)
    class Meta(object):
        managed = False



class Sender(models.Model):
    id = models.AutoField(primary_key=True, blank=True, verbose_name=_("To user"))
    user_type = models.CharField(max_length=255, verbose_name=_("Type_user"))
    message = models.TextField(blank=False, verbose_name=_("message"))
    subject = models.CharField(max_length=255, verbose_name=_("subject"))
    user_id = models.IntegerField(blank=False, verbose_name=_("user_id"))
    start_date = models.DateTimeField(verbose_name=_("start_date"))
    stop_date = models.DateTimeField(blank=True , null=True, verbose_name=_("stop_date"))
    common_message = models.IntegerField(blank=False, null=True, verbose_name=_("all_msg"))
    success_message = models.IntegerField(blank=False, null=True, verbose_name=_("success_msg"))
    failed_message = models.IntegerField(blank=True, null=True, verbose_name=_("failed_msg"))



    class Meta:
        verbose_name = _(u"letter")
        verbose_name_plural = _(u"Letters")
#         app_label = string_with_title("CoderPageApp", u"title")



class UserFiles(models.Model):
    sender = models.ForeignKey(Sender, blank=False, null=False)
    file = models.FileField(upload_to="mail_files/", blank=False, null=False, verbose_name=_("attached_file"))

    def filename(self):
        return os.path.basename(self.file.name)
    def file_link(self):
        if self.file:
            return "<a href='%s'>download</a>" % (self.file.url,)
        else:
            return "No attachment"

    file_link.allow_tags = True


class Menu_on_url(models.Model):
    url = models.CharField(max_length=255, null=True, blank=True)
    url_name = models.CharField(max_length=255, null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True)
    name_element = models.CharField(max_length=255)
    def __unicode__(self):
        return u'%s' % self.name_element

    class Meta:
        abstract = True

class Menu_on_globalhome(Menu_on_url):
    pass

class Menu_on_moscowdata(Menu_on_url):
    pass


class Meta_block(models.Model):
    url = models.CharField(max_length=255, unique=True)
    url_name = models.CharField(max_length=255, null=True, blank=True)
    title = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    keywords = models.TextField(null=True, blank=True)
    def __unicode__(self):
        return u'%s' % self.url

    class Meta:
        abstract = True

class Meta_globalhome(Meta_block):
    pass

class Meta_moscowdata(Meta_block):
    pass











