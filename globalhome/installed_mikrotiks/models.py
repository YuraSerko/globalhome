# -*-coding=utf-8-*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from mac_address_field import MACAddressField, MACAddressesField
from netaddr import *
from django.utils import six
from django import forms
import datetime
from django.db.models import IntegerField
from internet.models import Connection_address
from datetime import timedelta


TYPE_OF_SETTINGS = [
                    ['primary', 'Первичный'],
                    ['secondary', 'Вторичный'],
                    ['user', 'Пользовательский'],
                    ['reserve', 'Резервный']
                    ]
DIC_TYPE_OF_SETTINGS = {'primary':'Первичный', 'secondary':'Вторичный', 'user':'Пользовательский', 'reserve': 'Резервный'}

from netfields import InetAddressField, CidrAddressField
from netfields.forms import InetAddressFormField, CidrAddressFormField


class MyInetAddressField(InetAddressField):
    def form_class(self):
        return InetAddressFormField

    def to_python(self, value):
        return (self.python_type()(value) if value else '')



class MyCidrAddressField(CidrAddressField):
    def form_class(self):
        return CidrAddressFormField

    def to_python(self, value):
        return (self.python_type()(value) if value else '')

class Autofield(models.AutoField):
    def formfield(self, **kwargs):
        defaults = {'form_class': forms.IntegerField}
        defaults.update(kwargs)
        return super(models.AutoField, self).formfield(**defaults)



class Mikrotik(models.Model):
    id = Autofield(primary_key=True)
    ip_address = MyInetAddressField(blank=True, max_length=17, verbose_name=u'IP адрес', default='')
    MAC_addresses = MACAddressesField(max_length=23, verbose_name=u"MAC адреса", unique=True)
    parent = models.ForeignKey('self', blank=True, null=True)
    name_of_mikrotik = models.CharField(blank=True, max_length=50, verbose_name=u'Имя') #, default=''
    street = models.CharField(max_length=32, verbose_name=u"Улица")
    house = models.IntegerField(verbose_name=u"номер дома")
    corpse = models.CharField(blank=True, max_length=8, verbose_name=u'Корпус')
    porch = models.IntegerField(null=True, verbose_name=u"Подъезд")
    floor = models.CharField(null=True, blank=True, verbose_name=u"Этаж", max_length=10)
    additionalAdress = models.CharField(blank=True, max_length=255, verbose_name=u'Дополнительный адрес')
    mikrotik_model = models.ForeignKey('MikrotikModel', null=True, blank=True, verbose_name=u'Модель')
    installer_name = models.ForeignKey('Installer', blank=True, null=True, verbose_name=u'Кто установил')
    installer = models.CharField(blank=True, max_length=64, verbose_name=u'Кто установил')
    address = models.IntegerField(null=True, verbose_name=u'Адрес')
    date_installation = models.DateField(blank=True, verbose_name=u'Дата установки')
    last_day_of_test = models.DateField(null=True, blank=True, verbose_name=u'Дата окончания тестового периода')
    used_ipsubnet = MyCidrAddressField(blank=True, max_length=24, verbose_name=u'Используемая ip-подсеть', default='')
    type_of_settings = models.CharField(max_length=24, choices=TYPE_OF_SETTINGS, verbose_name=u'Тип настроек')
    notation = models.CharField(blank=True, verbose_name=u'Примечание', max_length=255)
    is_installed = models.BooleanField(verbose_name=u'Установлен', default=True)
    count_of_second_mikrotiks = models.IntegerField(verbose_name=u'Количество вторичных микротиков', default=0)
    field_for_search = models.CharField(blank=True, verbose_name=u'Поле для поиска', max_length=500)
    flat = models.CharField(blank=True, verbose_name=u'Номер квартиры', max_length=127)
    upload_speed = models.FloatField(blank=True, verbose_name=u'Скорость отдачи Мбит/с')
    download_speed = models.FloatField(blank=True, verbose_name=u'Скорость приёма Мбит/с')


    def save_all(self, *args, **kwargs):
        miks = Mikrotik.objects.all().filter(type_of_settings='user')
        print len(miks)
        for mik in miks:
            if mik.notation:
                print mik.id
                address = Connection_address.objects.get(id=int(mik.address))
                mik.name_of_mikrotik = mik.notation.encode('trans').replace(' ', '').lower()
                mik.field_for_search = "%s%s%s%sp%se%s%s" % (address.city.city.replace(' ', ''),
                                        address.street.street_type.replace(' ', ''),
                                        address.street.street.replace(' ', ''),
                                        address.house.house,
                                        mik.porch,
                                        mik.floor, mik.notation.replace(' ', '').lower())
                super(Mikrotik, mik).save(*args, **kwargs)


    def get_address(self):
        return Connection_address.objects.get(id=self.address)

    def __unicode__(self):
        return ('%s %s') % (self.name_of_mikrotik, str(self.ip_address) if self.ip_address else self.MAC_addresses)



    def save(self, *args, **kwargs):
        self.parent = (None if self.type_of_settings == 'primary' else self.parent)
        self.used_ipsubnet = ('' if not(self.type_of_settings == 'primary') else self.used_ipsubnet)
        self.count_of_second_mikrotiks = (0 if not(self.type_of_settings == 'primary') else self.count_of_second_mikrotiks)
        self.flat = ('' if not(self.type_of_settings == 'user') else self.flat)
        if not self.date_installation:
            self.date_installation = datetime.date.today()
        self.porch = (None if self.type_of_settings == 'primary' else self.porch)
        self.floor = ('' if self.type_of_settings == 'primary' else self.floor)
        self.last_day_of_test = self.last_day_of_test if(self.last_day_of_test) else (self.date_installation + timedelta(60))
        self.MAC_addresses = str(self.MAC_addresses).upper()
        self.used_ipsubnet = ('' if self.type_of_settings == 'secondary' else self.used_ipsubnet)
        self.field_for_search = ''

        try:
            if not self.name_of_mikrotik:
                if self.address:
                    address = Connection_address.objects.get(id=int(self.address))
                    if(self.type_of_settings == 'user') and self.notation:
                        self.name_of_mikrotik = self.notation.encode('trans').replace(' ', '').lower()
                        self.field_for_search = "%s%s%s%sp%se%s%s" % (address.city.city.replace(' ', ''),
                                                                address.street.street_type.replace(' ', ''),
                                                                address.street.street.replace(' ', ''),
                                                                address.house.house,
                                                                self.porch,
                                                                self.floor, self.notation.replace(' ', '').lower())
                    else:
                        self.name_of_mikrotik = "%s%s%s" % (address.street.street.encode('trans').replace(' ', '').lower(), \
                                                                  address.house.house.encode('trans').replace(' ', '').lower(),
                                                                  '' if self.type_of_settings == 'primary' else'p%se%s' % (self.porch, self.floor.encode('trans').replace(' ', '').lower()))
                        self.field_for_search = "%s%s%s%sp%se%s" % (address.city.city.replace(' ', ''),
                                                                address.street.street_type.replace(' ', ''),
                                                                address.street.street.replace(' ', ''),
                                                                address.house.house,
                                                                self.porch,
                                                                self.floor)
                    self.name_of_mikrotik = self.name_of_mikrotik.replace('/', '-')
        except Connection_address.DoesNotExist():
            pass
        super(Mikrotik, self).save(*args, **kwargs)
        self.__create_mac_addresses()
        self.field_for_search += ''.join(i.MAC_address for i in MACaddress.objects.filter(mikrotik=self))
        super(Mikrotik, self).save(*args, **kwargs)
#         self.save_all()


    def __create_mac_addresses(self):
        objsMAC = []
        for i in MACaddress.objects.filter(mikrotik=self).values('MAC_address'):
            objsMAC.append(i.get('MAC_address'))
        mac = self.MAC_addresses
        mac_split = mac.split('-')
        mac_end = mac_split[1]
        pref_mac = mac_split[0][:-len(mac_end)]
        mac_start = mac_split[0][len(pref_mac):]
        macaddrs = []
        for m in xrange(int(mac_start.replace(":", ""), 16), int(mac_end.replace(":", ""), 16) + 1):
            r = hex(m)[2:].upper().zfill(len(mac_start.replace(":", "")))
            res = []
            for i in range (0, len(r) / 2):
                res.append(r[i * 2:i * 2 + 2])
            macaddrs.append(pref_mac + ':'.join(res))
        for i in MACaddress.objects.all().filter(mikrotik=self):
            if not(i.MAC_address in macaddrs):
                i.delete()
        for i in macaddrs:
            if not(i in objsMAC):
                macaddr = MACaddress(MAC_address=i, mikrotik_id=self.id)
                macaddr.save()





class MikrotikModel(models.Model):
    name = MACAddressField(blank=True, max_length=16, verbose_name='Модель', unique=True)
    class Meta:
        verbose_name = _(u"Модель микротика")
        verbose_name_plural = _(u"Модели микротика")

    def __unicode__(self):
        return self.name


class Installer(models.Model):
    name = models.CharField(blank=True, max_length=64, verbose_name=u'Кто установил')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _(u"Установщик")
        verbose_name_plural = _(u"Установщики")


class MACaddress(models.Model):
    MAC_address = MACAddressField(blank=True, max_length=17, verbose_name=u"MAC адрес", unique=True)
    mikrotik = models.ForeignKey(Mikrotik)

    def __unicode__(self):
        return self.MAC_address

    def save(self, *args, **kwargs):
        self.MAC_address = str(self.MAC_address).upper()
        super(MACaddress, self).save(*args, **kwargs)

    class Meta:
        ordering = (u"MAC_address",)
        verbose_name = _(u"MAC адрес")
        verbose_name_plural = _(u"MAC адреса")


from south.modelsinspector import add_introspection_rules
rules = [
    (
        (Autofield,), [],
        {
            "null": ["null", {"default": True}],
            "blank": ["blank", {"default": True}],
        }
    ),
    (
        (MyInetAddressField,), [],
        {
            "null": ["null", {"default": True}],
            "blank": ["blank", {"default": True}],
        }
    ),
    (
        (MyCidrAddressField,), [],
        {
            "null": ["null", {"default": True}],
            "blank": ["blank", {"default": True}],
        }
    ),
]
add_introspection_rules(rules, ["^installed_mikrotiks\.models\.MyInetAddressField"])
add_introspection_rules(rules, ["^installed_mikrotiks\.models\.Autofield"])
add_introspection_rules(rules, ["^installed_mikrotiks\.models\.MyCidrAddressField"])


