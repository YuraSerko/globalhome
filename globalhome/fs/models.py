# -*- coding=utf-8 -*-
from django.db import models, connections
from django.contrib import admin
from datetime import datetime, timedelta
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _
from call_forwarding.DateUtils import *
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from settings import BILLING_DB, OBZVON_URL, QUEUE_URL, FREESWITCH
from telnumbers.models import TelNumbersGroup, TelNumber
from externalnumbers.models import ExternalNumber
from django.core.files.storage import FileSystemStorage
from billing.managers import BillingManager
from django.db import transaction
fs = FileSystemStorage(location=OBZVON_URL, base_url='/obzvon')
ivr = FileSystemStorage(location=OBZVON_URL, base_url='/myivr')
FS_QUEUE = FileSystemStorage(location=QUEUE_URL, base_url='/queue')

def get_billing_account_id_for_ivr(instance, filename):
    return '/'.join(['myivr', str(instance.billing_account_id_temp), filename])

## Create your models here.
class create_myivr_temp(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    enabled = models.BooleanField(default=True)  # включено ли данное ивр
    billing_account_id_temp = models.IntegerField()
    number_ivr = models.CharField(max_length=255, default='')  # номер на котором будет ivr
    name = models.CharField(max_length=255, default='')
    external_number = models.CharField(max_length=255, default='')
    external_number_id = models.IntegerField(blank=True, null=True)
    #file_wav = models.CharField(max_length=255, default='')
    file_wav = models.FileField(upload_to=get_billing_account_id_for_ivr, storage=ivr,)
    last_call = models.CharField(max_length=255, default='')  # номер на который звонить если ничего не выбрано в меню
    int_enabled = models.BooleanField(default=True)
    int_numbers = models.CharField(max_length=255, default='')
    number = models.ManyToManyField(TelNumber)
    dtmf_ivr_wait_time = models.IntegerField(default=5000)
    def __unicode__(self):
        return self.id

    class Meta:
        db_table = "create_myivr_temp"

    def save(self, using=BILLING_DB):
        super(create_myivr_temp, self).save(using=using)

    def GetTelNumber(self):
        if self.number.all():
            return self.number.all()[0].tel_number
        elif self.external_number:
            return self.external_number
        else:
            return 'Не закреплено'


class create_myivr(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    billing_account_id = models.IntegerField()
    nabor = models.CharField(max_length=255, default='')
    call = models.CharField(max_length=255, default='')
    id_ivr = models.ForeignKey(create_myivr_temp)  #
    def __unicode__(self):
        return self.id

    class Meta:
        db_table = "create_myivr"

    def save(self, using=BILLING_DB):
        super(create_myivr, self).save(using=using)

class fax_numbers(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    enabled = models.BooleanField(default=True)
    billing_account_id = models.IntegerField()
    name = models.CharField(max_length=255, default='')
    number = models.CharField(max_length=255, default='')
    email = models.CharField(max_length=255, default='')
    def __unicode__(self):
        return self.id

    class Meta:
        db_table = "fax_numbers"

    def save(self, using=BILLING_DB):
        super(fax_numbers, self).save(using=using)

class Voice_mail(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    enabled = models.BooleanField(default=True)
    billing_account_id = models.IntegerField()
    number = models.CharField(max_length=255, default='')
    name = models.CharField(max_length=255, default='')
    email = models.CharField(max_length=255, default='')
    reason = models.CharField(max_length=255, default='')
    messages_new = models.IntegerField(default=0)
    messages_arhive = models.IntegerField(default=0)
    file_hello = models.CharField(max_length=255, default='/usr/local/sounds/all_voicemail.wav')
    wait_time = models.IntegerField(default=60000)
    external_number = models.CharField(max_length=255, default='')
    external_number_id = models.IntegerField(blank=True, null=True)
    def __unicode__(self):
        return self.id

    class Meta:
        db_table = "voice_mail"

    def save(self, using=BILLING_DB):
        super(Voice_mail, self).save(using=using)

    def HaveBusyText(self):
        busy_dict = {'0': 'Нету', '1': 'Безусловная', '2': 'Занято', '3': 'Не доступен', '4': 'Нет ответа'}
        finish = []
        busy = eval(self.reason)
        for item in busy:
            if busy_dict.has_key(item):
                finish.append(busy_dict[item])
        return ", ".join(finish)

class Record_talk_tariff(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    name = models.CharField(max_length=255, default='')
    cost_activation = models.IntegerField(default=0)
    cost_for_min = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    count_save_day = models.IntegerField(default=0)
    record_time = models.IntegerField(default=0)

    def __unicode__(self):
        return self.id

    class Meta:
        db_table = "record_talk_tariff"

    def save(self, using=BILLING_DB):
        super(Record_talk_tariff, self).save(using=using)


class Record_talk(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    enabled = models.BooleanField(default=True)
    billing_account_id = models.IntegerField()
    number = models.CharField(max_length=255, default='')
    record_time_enabled = models.IntegerField(default=0)  # Битовые флаги условий по времени
    record_time_begin = models.TimeField(null=True)  # Начальное время интервала времени дня
    record_time_end = models.TimeField(null=True)  # Конечное время интервала времени дня
    record_type = models.CharField(max_length=255, default="[u'1', u'2']")
    record_day_enabled = models.IntegerField(default=0)  # Битовые флаги условий по времени
    record_day = models.CharField(max_length=255, default="[u'1', u'2', u'3', u'4', u'5', u'6', u'7']", null=True)
    tariff = models.ForeignKey(Record_talk_tariff)  #

    def __unicode__(self):
        return self.id

    class Meta:
        db_table = "record_talk"

    def save(self, using=BILLING_DB):
        super(Record_talk, self).save(using=using)

    def GetCrossRecordTalk(self, using=BILLING_DB, models=None):
        """
            Получаем модель, с которой по условиям пересекается данная или вернем None
        """

        # !!!!!!!!!!!!!!!!!!!!!!! вообще надо бы переписать по крайней мере этот метод

        test = self
        if models == None:
            models = Record_talk.objects.using(using).filter(number=test.number, enabled=True)


        # print models

        # test_t = test.HaveTimeOfDayCondition()
        test_t = test.record_time_enabled
        test_t1 = test.record_time_begin
        test_t2 = test.record_time_end
        # test_d = test.HaveDayOfWeekCondition()
        test_d = test.record_day_enabled
        test_bus = test.record_type
        if test_d:
            test_days = test.record_day
        else:
            test_days = [u'1', u'2', u'3', u'4', u'5', u'6', u'7']

        for model in models:
            # сначала проверим совпадение дней недели
            if model.id != test.id:
                if model.enabled:
                    if model.record_day_enabled:  # если и у текущей модели есть условие дня недели
                        model_days = model.record_day  # получаем включенные дни недели
                    else:  # у текущей модели нету условия дня недели, значит считаем, что все дни включены
                        model_days = [u'1', u'2', u'3', u'4', u'5', u'6', u'7']  # включаем все дни недели

                    if IsCrossDaysRecordTalk(test_days, model_days):
                        print "gra41"
                        if IsCrossTypeRecord(test_bus, model.record_type):
                            print "gra42"
                        # если есть пересечения в днях недели

                        # надо проверить совпадение времени суток
                            if test_t and model.record_time_enabled:  # если есть условие времени и там и там, то
                                if IsCrossTimes(test_t1, test_t2, model.record_time_begin, model.record_time_end):
                                    return model
                            else:  # если условия времени нету ни у того, ни у того
                                return model  # тогда их временные интервалы точно пересекаются, раз пересекаются еще и дни недели


class Record_talk_activated_tariff(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    billing_account_id = models.IntegerField()
    tariff = models.ForeignKey(Record_talk_tariff)  #
    # user_key = models.CharField(max_length = 12, default = '')
    date_create = models.DateTimeField(null=True, blank=True, verbose_name=_(u"Date create"))
    date_activation = models.DateTimeField(null=True, blank=True, verbose_name=_(u"Date activation"))
    date_deactivation = models.DateTimeField(null=True, blank=True, verbose_name=_(u"Date deactivation"))
    blocked = models.BooleanField(default=False)
    def __unicode__(self):
        return self.id

    class Meta:
        db_table = "record_talk_activated_tariff"

    def save(self, using=BILLING_DB):
        super(Record_talk_activated_tariff, self).save(using=using)

class GatewayModel(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    enabled = models.BooleanField(default=True)
    billing_account_id = models.IntegerField()
    tel_group = models.ForeignKey(TelNumbersGroup, blank=True, null=True)  # , related_name = "external_numbers")#, related_name = "+")
    sip_address_original = models.CharField(max_length=255, default='')
    sip_address = models.CharField(max_length=255, default='')
    login = models.CharField(max_length=70, default='')
    password = models.CharField(max_length=128, default='')
    label = models.CharField(max_length=15, blank=True, null=True)
#    tariff = models.ForeignKey(Record_talk_tariff)  #
#    date_create = models.DateTimeField(null=True, blank=True, verbose_name=_(u"Date create"))
#    date_activation = models.DateTimeField(null=True, blank=True, verbose_name=_(u"Date activation"))
#    date_deactivation = models.DateTimeField(null=True, blank=True, verbose_name=_(u"Date deactivation"))
#    blocked = models.BooleanField(default=False)
    def __unicode__(self):
        return self.id

    class Meta:
        db_table = "user_gateway"

    def save(self, using=BILLING_DB):
        super(GatewayModel, self).save(using=using)

def get_billing_account_id(instance, filename):
    return '/'.join(['obzvon', str(instance.billing_account_id), filename])

def get_billing_account_id_doc(instance, filename):
    return '/'.join(['obzvon', str(instance.billing_account_id), 'doc', filename])

class ObzvonModel(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    billing_account_id = models.IntegerField()
    from_number = models.CharField(max_length=255, default='')
    # to_number = models.CharField(max_length=255, default='')
    file = models.FileField(upload_to=get_billing_account_id, storage=fs,)
    file_text = models.FileField(upload_to=get_billing_account_id_doc, storage=fs,)
    status = models.IntegerField(default=0)
    answer_dtmf = models.BooleanField()
    answer_ivr = models.BooleanField()
    dtmf_wait_time = models.IntegerField(default=10000)
    count_call = models.IntegerField(default=1)
    obzvon_ivr = models.ManyToManyField(create_myivr_temp)
    #поля времени запуска отложенного обзовна
    one_times = models.BooleanField()
    obzvon_time_for_one = models.TimeField(null=True)
    date_to = models.DateTimeField(null=True)
    #поля времени запуска повторяющегося обзовна
    many_times = models.BooleanField()
    obzvon_time_enabled = models.BooleanField()
    obzvon_time = models.TimeField(null=True)
    obzvon_day_enabled = models.BooleanField()
    day_of_week = models.CharField(max_length=255, default='')
    obzvon_concretic_day_enabled = models.BooleanField()
    day_of_month = models.CharField(max_length=255, default='')
    min_time = models.TimeField(null=True)
    max_time = models.TimeField(null=True)
    max_min_time_enabled = models.BooleanField()
    date_start = models.DateTimeField(null=True)

    def __unicode__(self):
        return self.id

    class Meta:
        db_table = "user_obzvon"

    def save(self, using=BILLING_DB):
        super(ObzvonModel, self).save(using=using)

class ObzvonNumber(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    billing_account_id = models.IntegerField()
    number = models.CharField(max_length=255, default='')
    add_number = models.CharField(max_length=255, default='')
    status = models.CharField(max_length=255, default='')
    answer_time = models.IntegerField(default=0)
    duration = models.FloatField(default=0)
    id_obzvon = models.ForeignKey(ObzvonModel)
    digits = models.CharField(max_length=10, default='')
    number_from_file = models.BooleanField(default=False)

    def __unicode__(self):
        return self.id

    class Meta:
        db_table = "user_obzvon_number"

    def save(self, using=BILLING_DB):
        super(ObzvonNumber, self).save(using=using)

def queue_get_billing_account_id(instance, filename):
    return '/'.join(['queue', str(instance.billing_account_id), filename])

class Queue(models.Model):
    id = models.AutoField(primary_key = True, blank = True)
    billing_account_id = models.IntegerField()
    name = models.CharField('Название', max_length = 255)
    number_queue = models.IntegerField()
    hello = models.FileField('Приветствие', upload_to = queue_get_billing_account_id, storage = FS_QUEUE)
    chime_list = models.FileField('Периодическое сообщение', upload_to = queue_get_billing_account_id, storage = FS_QUEUE, blank = True)
    chime_freq = models.IntegerField('Интервал для периодического сообщения', blank = True, default = 60)
    hold = models.FileField('Фоновая музыка', upload_to = queue_get_billing_account_id, storage = FS_QUEUE, blank = True)
    client_announce = models.FileField('Сообщение перед соединением с оператором', upload_to = queue_get_billing_account_id, storage = FS_QUEUE, blank = True)
    record_enabled = models.BooleanField()
    time_enabled = models.BooleanField('Указать время работы')
    time_begin = models.TimeField(_(u"Begin time, inclusive"), default = None, null = True, blank = True)
    time_end = models.TimeField(_("End time, not inclusive"), default = None, null = True, blank = True)
    work_day = models.CharField('Выберите дни недели', max_length = 7, blank = True)
    work_announce = models.FileField('Сообщение, если очередь не работает (указано время или дни работы)', upload_to = queue_get_billing_account_id, storage = FS_QUEUE, blank = True)
    created_date = models.DateTimeField()
    internal_numbers = models.ManyToManyField(TelNumber)
    external_numbers = models.ManyToManyField(ExternalNumber)
    say_queue_position = models.BooleanField('Произносить номер позиции')

    objects = BillingManager()

    def __unicode__(self):
        return self.id

    class Meta:
        db_table = 'fs_queue'
        unique_together = (('billing_account_id', 'name'), ('billing_account_id', 'number_queue'))

class Agent(models.Model):
    id = models.AutoField(primary_key = True, blank = True)
    billing_account_id = models.IntegerField()
    internal_number = models.ForeignKey(TelNumber)
    queue = models.ForeignKey(Queue)

    objects = BillingManager()

    def delete_from_freeswitch(self):
        c = connections['billing'].cursor()
        try:
            c.execute("DELETE FROM fifo_outbound WHERE fifo_name = '%s' AND originate_string = '{fifo_member_wait=nowait,ignore_early_media=true,loopback_bowout=false}loopback/%s'" % (self.queue.id, self.internal_number.tel_number))
            transaction.commit_unless_managed(BILLING_DB)
        finally:
            c.close()

    def __unicode__(self):
        return self.id

    class Meta:
        db_table = "fs_agent"

    def save(self, using = BILLING_DB):
        super(Agent, self).save(using = using)


class TelNumbersList(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    billing_account_id = models.IntegerField()
    name = models.CharField(max_length=255, default='')
    call_list = models.BooleanField(default = False)
    # file_text = models.CharField(max_length=255, default='')

    def __unicode__(self):
        return self.id

    class Meta:
        db_table = "tel_numbers_list"

    def save(self, using=BILLING_DB):
        super(TelNumbersList, self).save(using=using)


class TelNumbersListDetailNumbers(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    telnumberslist = models.ForeignKey(TelNumbersList)
    number = models.CharField(max_length=255, default='')
    # number_from_file = models.BooleanField()

    def __unicode__(self):
        return self.id

    class Meta:
        db_table = "tel_numbers_list_detail_numbers"

    def save(self, using=BILLING_DB):
        super(TelNumbersListDetailNumbers, self).save(using=using)


class TelNumbersListNumbers(models.Model):
    # tel_number = models.CharField(max_length = 255, default = '')
    telnumberslist = models.ForeignKey(TelNumbersList)
    telnumber = models.ForeignKey(TelNumber, related_name="inttelnumber_id")
    type_out = models.IntegerField(null=True)
    type_in = models.IntegerField(null=True)

    def save(self, *args, **kwargs):
        kwargs['using'] = BILLING_DB
        return super(TelNumbersListNumbers, self).save(*args, **kwargs)

    class Meta:
        db_table = 'tel_numbers_list_numbers'

class TelNumbersListExtNumbers(models.Model):
    # tel_number = models.CharField(max_length = 255, default = '')
    telnumberslist = models.ForeignKey(TelNumbersList)
    extnumber = models.ForeignKey(ExternalNumber, related_name="exttelnumber_id")
    type_out = models.IntegerField(null=True)
    type_in = models.IntegerField(null=True)

    def save(self, *args, **kwargs):
        kwargs['using'] = BILLING_DB
        return super(TelNumbersListExtNumbers, self).save(*args, **kwargs)

    class Meta:
        db_table = 'tel_numbers_list_extnumbers'

class TelNumbersListGroups(models.Model):
    # tel_number = models.CharField(max_length = 255, default = '')
    telnumberslist = models.ForeignKey(TelNumbersList)
    group = models.ForeignKey(TelNumbersGroup, related_name="group_id")
    type_out = models.IntegerField(null=True)
    type_in = models.IntegerField(null=True)

    def save(self, *args, **kwargs):
        kwargs['using'] = BILLING_DB
        return super(TelNumbersListGroups, self).save(*args, **kwargs)

    class Meta:
        db_table = 'tel_numbers_list_groups'

class NumberTemplateRule(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    number_template_rule = models.CharField(max_length=255, default='')
    name = models.CharField(max_length=255, default='')
    billing_account_id = models.IntegerField()

    def save(self, *args, **kwargs):
        kwargs['using'] = BILLING_DB
        return super(NumberTemplateRule, self).save(*args, **kwargs)

    class Meta:
        db_table = 'number_template_rules'

class NumberTemplates(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    billing_account_id = models.IntegerField()
    name = models.CharField(max_length=255, default='')
    number_template = models.ManyToManyField(NumberTemplateRule)

    def save(self, *args, **kwargs):
        kwargs['using'] = BILLING_DB
        return super(NumberTemplates, self).save(*args, **kwargs)

    class Meta:
        db_table = 'number_template'