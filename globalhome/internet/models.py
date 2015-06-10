# -*-coding=utf-8-*-

# from billing_models import *
from django.db import models
from django.conf import settings
# import IPy
# from billing.models import BillserviceAccount
# from lib.fields import IPNetworkField, EncryptedTextField
# from django.core.urlresolvers import reverse
# import datetime
# from django.utils.translation import ugettext_lazy as _
from hotspot.models import HomeAdministration


STREET_TYPE_CHOICES = (
        (u'улица', u'улица'),
        (u'проспект', u'проспект'),
        (u'бульвар', u'бульвар'),
        (u'переулок', u'переулок'),
        (u'набережная', u'набережная'),
        (u'шоссе', u'шоссе'),
        (u'проезд', u'проезд'),
        (u'', u''),
    )

READINESS_DEGREE_CHOICES = (
        (0, u'Планируется подключение'),
        (1, u'Установлены центральные ящики'),
        (2, u'Дом подключен к интернет'),
        (3, u'Протянуты кабели'),
        (4, u'Установлены ящики на этажах и сделана оконцовка'),
        (5, u'Установлены микротики и коммутаторы'),
        (6, u'Дом запущен в тест'),
        (7, u'Дом запущен в продакшн'),

    )


class VpnAuth(models.Model):
    login = models.CharField(max_length=64)
    attribute = models.CharField(default="password", max_length=10)
    op = models.CharField(default="==", max_length=3)
    value = models.CharField(max_length=64)
    billing_account_id = models.IntegerField(null=True, blank=True, editable=False)
    visible = models.BooleanField(default=True)
    def __unicode__(self):
        return self.id

    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        return super(VpnAuth, self).save(*args, **kwargs)

    class Meta:
        db_table = "internet_vpn_auth"


class Internet_city(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    city = models.CharField(max_length=50, unique=True)
    def __unicode__(self):
        return self.city

    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        return super(Internet_city, self).save(*args, **kwargs)

    class Meta:
        db_table = "internet_city"
        verbose_name = (u'Города подключения к интернет')
        verbose_name_plural = (u'Города подключения к интернет')


class Internet_street(models.Model):
    id = models.AutoField(primary_key=True, blank=True)

    street_type = models.CharField(max_length=100, choices=STREET_TYPE_CHOICES, default=u'улица')
    street = models.CharField(max_length=200)
    def __unicode__(self):
        # return self.street
        return  u'%s %s' % (self.street_type, self.street)
    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        return super(Internet_street, self).save(*args, **kwargs)

    class Meta:
        db_table = "internet_street"
        ordering = ['street_type', 'street']
        unique_together = ('street_type', 'street')


class Internet_house(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    house = models.CharField(max_length=200, unique=True)
    def __unicode__(self):
        return self.house

    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        return super(Internet_house, self).save(*args, **kwargs)

    class Meta:
        db_table = "internet_house"
        ordering = ['house']

class Internet_persons_for_connection(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    persons = models.CharField(max_length=100)
    def __unicode__(self):
        return self.persons

    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        return super(Internet_persons_for_connection, self).save(*args, **kwargs)

    class Meta:
        db_table = "internet_persons_for_connection"
        verbose_name = (u'Тип адресов подключения к интернет')
        verbose_name_plural = (u'Тип адресов подключения к интернет')


class Connection_address(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    city = models.ForeignKey(Internet_city, verbose_name=u'Город')
    street = models.ForeignKey(Internet_street, verbose_name=u'Улица')
    house = models.ForeignKey(Internet_house, verbose_name=u'Дом')
    x = models.DecimalField(max_digits=16, decimal_places=10, blank=True, null=True)
    y = models.DecimalField(max_digits=16, decimal_places=10, blank=True, null=True)
    persons = models.ManyToManyField(Internet_persons_for_connection, blank=True, null=True, verbose_name=u'Тип подключения к интернету')
    readiness_degree = models.IntegerField(choices=READINESS_DEGREE_CHOICES, default=0, verbose_name=u'Готовность')
    notes = models.CharField(max_length=500, blank=True, null=True, verbose_name=u'Примечаниe')
    floors = models.IntegerField(blank=True, null=True, verbose_name=u'Количество этажей')
    entrances = models.IntegerField(blank=True, null=True, verbose_name=u'Количество подъездов')
    readiness_degree0 = models.BooleanField(blank=True, default=False, verbose_name=u'Планируется подключение')
    readiness_degree1 = models.BooleanField(blank=True, default=False, verbose_name=u'Установлены центральные ящики')
    readiness_degree2 = models.BooleanField(blank=True, default=False, verbose_name=u'Дом подключен к интернет')
    readiness_degree3 = models.BooleanField(blank=True, default=False, verbose_name=u'Протянуты кабели')
    readiness_degree4 = models.BooleanField(blank=True, default=False, verbose_name=u'Установлены ящики на этажах и сделана оконцовка')
    readiness_degree5 = models.BooleanField(blank=True, default=False, verbose_name=u'Установлены микротики и коммутаторы')
    readiness_degree6 = models.BooleanField(blank=True, default=False, verbose_name=u'Дом запущен в тест')
    readiness_degree7 = models.BooleanField(blank=True, default=False, verbose_name=u'Дом запущен в продакшн')

    home_administration = models.ManyToManyField(HomeAdministration, verbose_name=u'Администрация дома') #'hotspot.HomeAdministration'


    def readiness_degree_sost(self):
        text = ""
        p = 0;
        while (p <= 7):
            if (eval("self.readiness_degree%s" % str(p)) == True):
                text = text + READINESS_DEGREE_CHOICES[p][1] + ","
            p = p + 1
        dlina = len(text) - 1
        text_to_field = text[0:dlina]
        return text_to_field
    readiness_degree_sost.short_description = u'Готовность'

    def person_names(self):
        return u" %s" % (u", ".join([Internet_persons_for_connection.persons for Internet_persons_for_connection in self.persons.all()]))
    person_names.short_description = u'Тип подключения к интернету'

    def home_adms(self):
        return u" %s" % (u", ".join([HomeAdministration.district_administration.name for HomeAdministration in self.home_administration.all().distinct('district_administration')]))
    home_adms.short_description = u'Администрация района'

    def __unicode__(self):
        return u'%s %s %s %s' % (self.city.city, self.street.street_type, self.street.street, self.house.house)


    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        return super(Connection_address, self).save(*args, **kwargs)

    class Meta:
        db_table = "internet_connection_address"
        verbose_name = (u'Адреса подключения к интернет')
        verbose_name_plural = (u'Адреса подключения к интернет')
        unique_together = ('city', 'street', 'house')

#   Creating proxy-model
class Connection_address_map(Connection_address):
    def person_names(self):
        return u" %s" % (u", ".join([Internet_persons_for_connection.persons for Internet_persons_for_connection in self.persons.all()]))
    person_names.short_description = u'Тип подк. к инт.'
    def street_name(self):
        return  '%s' % (self.street)
    street_name.short_description = u'Улица'
    class Meta:
        proxy = True
        verbose_name = (u'Адрес подключения к интернет с картой')
        verbose_name_plural = (u'Адреса подключения к интернет с картой')

class ConectionInputHomeAdmin(Connection_address):
    class Meta:
        proxy = True
        verbose_name = (u'Форма ввода администрации дома')
        verbose_name_plural = (u'Форма ввода администрации дома')


class ScheduleConnectionInternet(models.Model):
    adress = models.ForeignKey(Connection_address, null=False, verbose_name=u'Адрес')
    porch = models.CharField(max_length=500, blank=True, null=False, verbose_name=u'Подъезд')
    flat = models.CharField(max_length=500, blank=True, verbose_name=u'Квартира', null=False)
    date = models.CharField(max_length=500, blank=True, null=False, verbose_name=u'Дата')
    time = models.CharField(max_length=500, blank=True, null=False, verbose_name=u'Время')
    contact_face = models.CharField(max_length=500, blank=True, null=False, verbose_name=u'Контактне лицо')
    tel_namber = models.CharField(max_length=500, blank=True, null=False, verbose_name=u'Номер телефона')
    district = models.CharField(max_length=100, null=True)
    add_info = models.CharField(max_length=500, blank=True, null=False, verbose_name=u'Дополнителная информация')
    running_state = models.BooleanField(verbose_name=u'Не выполненено')

    def __unicode__(self):
        return u'%s ' % (self.adress)

    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        return super(ScheduleConnectionInternet, self).save(*args, **kwargs)

    class Meta:
        db_table = "schedule_connection_internet"
        verbose_name = (u'Расписание подключения к Итернет')
        verbose_name_plural = (u'Расписание подключения к Итернет')

