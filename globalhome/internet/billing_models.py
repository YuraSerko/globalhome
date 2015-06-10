# -*-coding=utf-8-*-

from django.db import models
from settings import BILLING_DB
import string
import random
from django.conf import settings
import IPy
from billing.models import BillserviceAccount
from lib.fields import IPNetworkField, EncryptedTextField
from django.core.urlresolvers import reverse
import datetime
from django.utils.translation import ugettext_lazy as _
from hotspot.models import Nas
from cards.models import BillserviceCard

ACCESS_TYPE_METHODS = (
                      ("PPTP", "PPTP"),
                      ("PPPOE", "PPPOE"),
                      ("IPN", "IPN"),
                      ("HotSpot", "HotSpot"),
                      ('HotSpotIp+Mac', 'HotSpotIp+Mac'),
                      ('HotSpotIp+Password', 'HotSpotIp+Password'),
                      ('HotSpotMac', 'HotSpotMac'),
                      ('HotSpotMac+Password', 'HotSpotMac+Password'),
                      ('lISG', 'lISG'),
                      ("DHCP", "DHCP")
                )

PERIOD_CHOISES = (
                ('DONT_REPEAT', _(u'Не повторять')),
                ('DAY', _(u'День')),
                ('WEEK', _(u'Неделя')),
                ('MONTH', _(u'Месяц')),
                ('YEAR', _(u'Год')),
                )

STATUS_CLASS = {
              1:'',
              2:'inactive-light',
              3:'inactive',
              4:'info',
              False: 'inactive',
              }

class Model(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        return super(Model, self).save(*args, **kwargs)

class IPPool(Model):
    name = models.CharField(verbose_name=_(u'Название'), max_length=255)
    # 0 - VPN, 1-IPN
    type = models.IntegerField(verbose_name=_(u'Тип'), choices=((0, _(u"IPv4 VPN")), (1, _(u"IPv4 IPN")), (2, _(u"IPv6 VPN")), (3, _(u"IPv6 IPN")),))
    start_ip = models.GenericIPAddressField(verbose_name=_(u'C IP'))
    end_ip = models.GenericIPAddressField(verbose_name=_(u'По IP'))
    next_ippool = models.ForeignKey("IPPool", verbose_name=_(u'Следующий пул'), blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = _(u"IP пул")
        verbose_name_plural = _(u"IP пулы")
        permissions = (
           ("ippool_view", _(u"Просмотр")),
           )
        db_table = "billservice_ippool"

    def __unicode__(self):
        return u"%s" % self.name

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('ippool_delete'), self.id)

    def get_pool_size(self):

        return IPy.IP(self.end_ip).int() - IPy.IP(self.start_ip).int()

    def get_used_ip_count(self):
        return self.ipinuse_set.filter(disabled__isnull=True).count()


class IPInUse(Model):
    pool = models.ForeignKey(IPPool, verbose_name=_(u'IP пул'))
    ip = models.CharField(max_length=255, verbose_name=_(u'IP адрес'))
    datetime = models.DateTimeField(verbose_name=_(u'Дата выдачи'))
    disabled = models.DateTimeField(blank=True, null=True, verbose_name=_(u'Дата освобождения'))
    dynamic = models.BooleanField(default=False, verbose_name=_(u'Выдан динамически'))
    ack = models.BooleanField(default=False, blank=True, verbose_name=_(u'Подтверждён'))

    class Meta:
        ordering = ['ip']
        verbose_name = _(u"Занятый IP адрес")
        verbose_name_plural = _(u"Занятые IP адреса")
        permissions = (
           ("ipinuse_view", _(u"Просмотр")),
           )
        db_table = "billservice_ipinuse"

    def __unicode__(self):
        return u"%s" % self.ip


def GenPasswd():
    chars = ''
    if settings.PASSWORD_CONTAIN_LETTERS:
        chars += string.letters
    if settings.PASSWORD_CONTAIN_DIGITS:
        chars += string.digits
    newpasswd = ''
    for i in range(settings.PASSWORD_LENGTH):
        newpasswd = newpasswd + random.choice(chars)
    return newpasswd


def GenUsername():
    chars = ''
    if settings.LOGIN_CONTAIN_LETTERS:
        chars += string.letters
    if settings.LOGIN_CONTAIN_DIGITS:
        chars += string.digits
    newpasswd = ''
    for i in range(settings.LOGIN_LENGTH):
        newpasswd = newpasswd + random.choice(chars)
    return newpasswd


class SubAccount(Model):
    # account = models.ForeignKey(Account, related_name='subaccounts')
    account = models.ForeignKey(BillserviceAccount, blank=True, null=True, verbose_name=_(u"Account"))
    username = models.CharField(verbose_name=_(u'Логин'), max_length=512, blank=True)
    password = EncryptedTextField(verbose_name=_(u'Пароль'), blank=True, default='')
    ipn_ip_address = IPNetworkField(blank=True, null=True, default='0.0.0.0')
    ipn_mac_address = models.CharField(blank=True, max_length=17, default='')
    vpn_ip_address = models.IPAddressField(blank=True, null=True, default='0.0.0.0')
    allow_mac_update = models.BooleanField(default=False)
    # nas = models.ForeignKey(Nas, blank=True, null=True, on_delete=models.SET_NULL)
    nas_id = models.IntegerField(blank=True, null=True)
    ipn_added = models.BooleanField(verbose_name=_(u'Добавлен на NAS'))
    ipn_enabled = models.BooleanField(verbose_name=_(u'Включен на NAS'))
    ipn_sleep = models.BooleanField(verbose_name=_(u'не менять IPN статус'))
    need_resync = models.BooleanField()
    speed = models.TextField(blank=True)
    # switch = models.ForeignKey("Switch", blank=True, null=True, on_delete=models.SET_NULL)
    switch_port = models.IntegerField(blank=True, null=True)
    allow_dhcp = models.BooleanField(blank=True, default=False, verbose_name=_(u"Разрешать получать IP адреса по DHCP"))
    allow_dhcp_with_null = models.BooleanField(blank=True, default=False, verbose_name=_(u"Разрешать получать IP адреса по DHCP при нулевом балансе"))
    allow_dhcp_with_minus = models.BooleanField(blank=True, default=False, verbose_name=_(u"Разрешать получать IP адреса по DHCP при отрицатеьлном балансе"))
    allow_dhcp_with_block = models.BooleanField(blank=True, default=False, verbose_name=_(u"Разрешать получать IP адреса по DHCP при наличии блокировок по лимитам или балансу"))
    allow_vpn_with_null = models.BooleanField(blank=True, default=False, verbose_name=_(u"Разрешать RADIUS авторизацию при нулевом балансе"))
    allow_vpn_with_minus = models.BooleanField(blank=True, default=False, verbose_name=_(u"Разрешать RADIUS авторизацию при отрицательном балансе балансе"))
    allow_vpn_with_block = models.BooleanField(blank=True, default=False, verbose_name=_(u"Разрешать RADIUS авторизацию при наличии блокировок по лимитам или балансу"))
    allow_ipn_with_null = models.BooleanField(blank=True, default=False, verbose_name=_(u"Разрешать IPN авторизацию при нулевом балансе"))
    allow_ipn_with_minus = models.BooleanField(blank=True, default=False, verbose_name=_(u"Разрешать IPN авторизацию при отрицательном балансе"))
    allow_ipn_with_block = models.BooleanField(blank=True, default=False, verbose_name=_(u"Разрешать IPN авторизацию при наличии блокировок по лимитам или балансу"))
    associate_pptp_ipn_ip = models.BooleanField(blank=True, default=False, verbose_name=_(u"Привязать PPTP/L2TP авторизацию к IPN IP"))
    associate_pppoe_ipn_mac = models.BooleanField(blank=True, default=False, verbose_name=_(u"Привязать PPPOE авторизацию к IPN MAC"))
    ipn_speed = models.TextField(blank=True, help_text=_(u"Не менять указанные настройки скорости"))
    vpn_speed = models.TextField(blank=True, help_text=_(u"Не менять указанные настройки скорости"))
    allow_addonservice = models.BooleanField(blank=True, default=False, verbose_name=_(u"Разрешить самостоятельную активацию подключаемых услуг на этот субаккаунт"))
    vpn_ipinuse = models.ForeignKey(IPInUse, blank=True, null=True, related_name='subaccount_vpn_ipinuse_set', on_delete=models.SET_NULL)
    ipn_ipinuse = models.ForeignKey(IPInUse, blank=True, null=True, related_name='subaccount_ipn_ipinuse_set', on_delete=models.SET_NULL)
    vpn_ipv6_ip_address = models.GenericIPAddressField(blank=True, null=True)
    vpn_ipv6_ipinuse = models.ForeignKey(IPInUse, blank=True, null=True, related_name='subaccount_vpn_ipv6_ipinuse_set', on_delete=models.SET_NULL)
    ipn_ipv6_ip_address = models.TextField(blank=True, null=True)
    vlan = models.IntegerField(blank=True, null=True)
    allow_mac_update = models.BooleanField(blank=True, default=False, verbose_name=_(u"Разрешить самостоятельно обновлять MAC адрес через веб-кабинет"))
    ipv4_ipn_pool = models.ForeignKey(IPPool, blank=True, default=None, null=True, related_name='subaccount_ipn_ippool_set', on_delete=models.SET_NULL)
    ipv4_vpn_pool = models.ForeignKey(IPPool, blank=True, default=None, null=True, related_name='subaccount_vpn_ippool_set', on_delete=models.SET_NULL)
    ipv6_vpn_pool = models.ForeignKey(IPPool, blank=True, default=None, null=True, related_name='subaccount_ipv6_vpn_ippool_set', on_delete=models.SET_NULL)
    sessionscount = models.IntegerField(verbose_name=_(u"Одноверменных RADIUS сессий на субаккаунт"), blank=True, default=0)

    text_password = models.TextField(blank=True, help_text=_(u"Текстовый пароль"))

    def __unicode__(self):
        return u"%s" % self.username

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('subaccount_delete'), self.id)

    @staticmethod
    def get_vpn_ip_address(vpn_ip_address, ipv4_vpn_pool_id):
        if vpn_ip_address == '0.0.0.0':
            default_ip = vpn_ip_address
            if default_ip:
                default_ip = IPy.IP(default_ip).int()
            pool_id = ipv4_vpn_pool_id
            limit = 1
            term = ''
            pool = IPPool.objects.get(id=pool_id)
            ipinuse = IPInUse.objects.filter(pool=pool, disabled__isnull=True)

            accounts_ip = SubAccount.objects.values_list('ipn_ip_address', 'vpn_ip_address', 'vpn_ipv6_ip_address')
            # if term:
            #    ipinuse = ipinuse.filter(ip__contains=term)
            # accounts_ip = connection.sql("SELECT ipn_ip_address, vpn_ip_address FROM billservice_subaccount")
            # connection.commit()
            ipversion = 4 if pool.type < 2 else  6
            accounts_used_ip = []
            for accip in accounts_ip:
                if accip[0]:
                    accounts_used_ip.append(IPy.IP(accip[0]).int())
                if accip[1]:
                    accounts_used_ip.append(IPy.IP(accip[1]).int())
                if accip[2]:
                    accounts_used_ip.append(IPy.IP(accip[2]).int())



            start_pool_ip = IPy.IP(pool.start_ip).int()
            end_pool_ip = IPy.IP(pool.end_ip).int()

            ipinuse_list = [IPy.IP(x.ip).int() for x in ipinuse]

            ipinuse_list += accounts_used_ip


            # find = False
            res = []
            x = start_pool_ip
            i = 0
            # limit=20
            while x <= end_pool_ip:
                if x not in ipinuse_list and x != default_ip:
                    if not term or term and str(IPy.IP(x, ipversion=ipversion)).rfind(term) != -1:
                        res.append(str(IPy.IP(x, ipversion=ipversion)))
                    if len(res) == limit: break
                    i += 1
                x += 1
            vpn_ip_address = res[0]
        return vpn_ip_address

    @staticmethod
    def set_account(account, vpn_ip_address='0.0.0.0', ipv4_vpn_pool_id=1, commit=False):
        sa_qs = SubAccount.objects.filter(account=account)
        if not sa_qs:
            sa = SubAccount.generate(account, vpn_ip_address, commit=commit)
        else:
            sa = sa_qs[0]
            vpn_ip_address_valid = SubAccount.get_vpn_ip_address(vpn_ip_address, ipv4_vpn_pool_id)
            sa.vpn_ip_address = vpn_ip_address_valid
            sa.save()
        return sa

    @staticmethod
    def generate(account, vpn_ip_address='0.0.0.0', ipv4_vpn_pool_id=1, commit=False):
        while True:
            username = GenUsername()
            try:
                BillserviceAccount.objects.get(username=username)
            except BillserviceAccount.DoesNotExist:
                try:
                    SubAccount.objects.get(username=username)
                except SubAccount.DoesNotExist:
                    try:
                        BillserviceCard.objects.get(login=username)
                    except BillserviceCard.DoesNotExist:
                        break

        password = GenPasswd()
        # если нет статического ip выделяем первый свободный ip из пула
        vpn_ip_address_valid = SubAccount.get_vpn_ip_address(vpn_ip_address, ipv4_vpn_pool_id)
        sa = SubAccount(account=account,
                        username=GenUsername(),
                        password=password,
                        text_password=password,
                        vpn_ip_address=vpn_ip_address_valid,
                        ipv4_vpn_pool_id=ipv4_vpn_pool_id,
                        nas_id=8,
                        allow_dhcp=True,
                        allow_dhcp_with_null=True,
                        allow_dhcp_with_minus=True,
                        allow_dhcp_with_block=True,
                        allow_vpn_with_null=True,
                        allow_vpn_with_minus=True,
                        allow_vpn_with_block=True,
                        allow_ipn_with_null=True,
                        allow_ipn_with_minus=True,
                        )
        if commit:
            sa.save()
        return sa


    class Meta:
        ordering = ['-username']
        verbose_name = _(u"Субаккаунт")
        verbose_name_plural = _(u"Субаккаунт")
        permissions = (
            ("subaccount_view", _(u"Просмотр")),
            ("getmacforip", _(u"Получение mac адреса по IP")),
            )
        db_table = "billservice_subaccount"

    def save(self, *args, **kwargs):
        print 11
        print  'START vpn_ipinuse', self.vpn_ipinuse
        if self.vpn_ipinuse:

            # vpn_pool = IPPool.objects.get(id=ipv4_vpn_pool)
            print 222
            if  str(self.vpn_ip_address) not in ['0.0.0.0', '0.0.0.0/32', '', None]:
                if self.ipv4_vpn_pool:

                    print 333
                    if str(self.vpn_ipinuse.ip) != str(self.vpn_ip_address):
                        obj = IPInUse.objects.get(id=self.vpn_ipinuse.id)
                        obj.disabled = datetime.datetime.now()
                        obj.save()
                        print 444

                        obj = IPInUse(pool=self.ipv4_vpn_pool, ip=self.vpn_ip_address, datetime=datetime.datetime.now())
                        obj.save()
                        self.vpn_ipinuse = obj
                        print "NEW VPN IPINUSE=", self.vpn_ipinuse

                else:
                    obj = self.vpn_ipinuse
                    obj.disabled = datetime.datetime.now()
                    obj.save()
                    self.vpn_ipinuse = None




            elif str(self.vpn_ip_address) in ['', '0.0.0.0', '0.0.0.0/32', '', None]:
                print 666
                obj = self.vpn_ipinuse
                obj.disabled = datetime.datetime.now()
                obj.save()

                self.vpn_ipinuse = None
        elif str(self.vpn_ip_address) not in ['', '0.0.0.0', '0.0.0.0/32', '', None] and self.ipv4_vpn_pool:
            print 777

            ip = IPInUse(pool=self.ipv4_vpn_pool, ip=self.vpn_ip_address, datetime=datetime.datetime.now())
            ip.save()
            self.vpn_ipinuse = ip
            print 888

        # print '1111111', subaccount, vpn_ipinuse, ipn_ipinuse, subaccount.ipv4_vpn_pool
        if self.vpn_ipv6_ipinuse:

            # vpn_pool = IPPool.objects.get(id=ipv4_vpn_pool)
            # print 222
            if  str(self.vpn_ipv6_ip_address) not in ['', '::', ':::', None]:
                if self.ipv6_vpn_pool:

                    if str(self.vpn_ipv6_ipinuse.ip) != str(self.vpn_ipv6_ip_address):
                        obj = IPInUse.objects.get(id=self.vpn_ipv6_ipinuse.id)
                        obj.disabled = datetime.datetime.now()
                        obj.save()
                        # print 444
                        obj = IPInUse.objects.create(pool=self.ipv6_vpn_pool, ip=self.vpn_ipv6_ip_address, datetime=datetime.datetime.now())
                        obj.save()
                        self.vpn_ipv6_ipinuse = obj
                else:
                    obj = self.vpn_ipv6_ipinuse
                    obj.disabled = datetime.datetime.now()
                    obj.save()
                    self.vpn_ipv6_ipinuse = None



            elif str(self.vpn_ipv6_ip_address) in ['', '::', ':::', None]:
                # print 666
                obj = self.vpn_ipv6_ipinuse
                obj.disabled = datetime.datetime.now()
                obj.save()

                self.vpn_ipv6_ipinuse = None
        elif str(self.vpn_ipv6_ip_address) not in ['', '::', ':::', None] and self.ipv6_vpn_pool:

            ip = IPInUse(pool=self.ipv6_vpn_pool, ip=self.vpn_ipv6_ip_address, datetime=datetime.datetime.now())
            ip.save()

            self.vpn_ipv6_ipinuse = ip

        if self.ipn_ipinuse:



            if  str(self.ipn_ip_address) not in ['0.0.0.0', '0.0.0.0/32', '', None]:
                if self.ipv4_ipn_pool:

                    if str(self.ipn_ipinuse.ip) != str(self.ipn_ip_address):
                        obj = IPInUse.objects.get(id=self.ipn_ipinuse.id)
                        obj.disabled = datetime.datetime.now()
                        obj.save()

                        obj = IPInUse(pool=self.ipv4_ipn_pool, ip=self.ipn_ip_address, datetime=datetime.datetime.now())
                        obj.save()
                        self.ipn_ipinuse = obj
                else:
                    obj = self.ipn_ipinuse
                    obj.disabled = datetime.datetime.now()
                    obj.save()
                    self.ipn_ipinuse = None



            elif str(self.ipn_ip_address) in ['', '0.0.0.0', '0.0.0.0/32', '', None]:

                obj = IPInUse.objects.get(id=self.ipn_ipinuse.id)
                obj.disabled = datetime.datetime.now()
                obj.save()
                self.ipn_ipinuse = None
        elif str(self.ipn_ip_address) not in ['', '0.0.0.0', '0.0.0.0/32', '', None] and self.ipv4_ipn_pool:


            ip = IPInUse(pool=self.ipv4_ipn_pool, ip=self.ipn_ip_address, datetime=datetime.datetime.now())
            ip.save()
            self.ipn_ipinuse = ip
        self.ipn_ip_address = self.ipn_ip_address or '0.0.0.0'
        self.vpn_ip_address = self.vpn_ip_address or '0.0.0.0'
        print 'self.vpn_ipinuse', self.vpn_ipinuse
        # kwargs['using'] = settings.BILLING_DB
        return super(SubAccount, self).save(*args, **kwargs)


class TimePeriod(Model):
    name = models.CharField(max_length=255, verbose_name=_(u'Название группы временных периодов'), unique=True)
    # time_period_nodes = models.ManyToManyField(to=TimePeriodNode, blank=True, null=True, verbose_name=_(u'Группа временных периодов')

    def in_period(self):
        for time_period_node in self.time_period_nodes:
            if time_period_node.in_period() == True:
                return True
        return False

    def __unicode__(self):
        return u"%s" % self.name

    class Admin:
        list_display = ('name',)


    class Meta:
        ordering = ['name']
        verbose_name = _(u"Временной период")
        verbose_name_plural = _(u"Временные периоды")
        permissions = (
            ("timeperiod_view", _(u"Просмотр временных периодов")),
            )
        db_table = "billservice_timeperiod"


class AccessParameters(Model):
    # name              = models.CharField(max_length=255, verbose_name=_(u'Название вида доступа')
    access_type = models.CharField(max_length=255, choices=ACCESS_TYPE_METHODS, default='PPTP', blank=True, verbose_name=_(u'Способ доступа'))
    access_time = models.ForeignKey(to=TimePeriod, verbose_name=_(u'Доступ разрешён'), null=True, on_delete=models.SET_NULL)
    # ip_address_pool   = models.ForeignKey(to=IPAddressPool, verbose_name=_(u'Пул адресов', blank=True, null=True)
    ipn_for_vpn = models.BooleanField(verbose_name=_(u'Выполнять IPN действия'), blank=True, default=False)
    # max_limit      = models.CharField(verbose_name=_(u"MAX (kbps)", max_length=64, blank=True, default="")
    # min_limit      = models.CharField(verbose_name=_(u"MIN (kbps)", max_length=64, blank=True, default="")
    # burst_limit    = models.CharField(verbose_name=_(u"Burst", max_length=64, blank=True, default="")
    # burst_treshold = models.CharField(verbose_name=_(u"Burst treshold (kbps)", max_length=64, blank=True, default="")
    # burst_time     = models.CharField(verbose_name=_(u"Burst Time", blank=True, max_length=64, default="")

    max_tx = models.CharField(verbose_name=_(u"MAX tx (kbps)"), max_length=64, blank=True, default="")
    max_rx = models.CharField(verbose_name=_(u"rx (kbps)"), max_length=64, blank=True, default="")
    burst_tx = models.CharField(verbose_name=_(u"Burst tx (kbps)"), max_length=64, blank=True, default="")
    burst_rx = models.CharField(verbose_name=_(u"rx (kbps)"), max_length=64, blank=True, default="")
    burst_treshold_tx = models.CharField(verbose_name=_(u"Burst treshold tx (kbps)"), max_length=64, blank=True, default="")
    burst_treshold_rx = models.CharField(verbose_name=_(u"rx (kbps)"), max_length=64, blank=True, default="")
    burst_time_tx = models.CharField(verbose_name=_(u"Burst time tx (s)"), max_length=64, blank=True, default="")
    burst_time_rx = models.CharField(verbose_name=_(u"rx (s)"), max_length=64, blank=True, default="")
    min_tx = models.CharField(verbose_name=_(u"Min tx (kbps)"), max_length=64, blank=True, default="")
    min_rx = models.CharField(verbose_name=_(u"rx (kbps)"), max_length=64, blank=True, default="")



    # от 1 до 8
    priority = models.IntegerField(verbose_name=_(u"Приоритет"), blank=True, default=8)
    sessionscount = models.IntegerField(verbose_name=_(u"Одноверменных RADIUS сессий на субаккаунт"), blank=True, default=0)

    def __unicode__(self):
        return u"%s/%s" % (self.max_rx, self.max_tx)

    class Admin:
        # ordering = ['name']
        list_display = ('access_type',)


    class Meta:
        verbose_name = _(u"Параметры доступа")
        verbose_name_plural = _(u"Параметры доступа")
        permissions = (
            ("accessparameters_view", _(u"Просмотр параметров доступа")),
            )
        db_table = "billservice_accessparameters"

class TimeAccessService(Model):
    """
    Доступ с тарификацией по времени
    """
    # name              = models.CharField(max_length=255, verbose_name=_(u'Название услуги', unuque=True)
    prepaid_time = models.IntegerField(verbose_name=_(u'Предоплаченное время'), default=0, blank=True)
    reset_time = models.BooleanField(verbose_name=_(u'Сбрасывать  предоплаченное время'), blank=True, default=False)
    tarification_step = models.IntegerField(verbose_name=_(u"Тарифицировать по, c."), blank=True, default=60)
    rounding = models.IntegerField(verbose_name=_(u"Округлять"), default=0, blank=True, choices=((0, _(u"Не округлять")), (1, _(u"В большую сторону")),))


    def __unicode__(self):
        return u"%s" % self.id

    class Admin:
        # ordering = ['name']
        list_display = ('prepaid_time',)


    class Meta:
        verbose_name = _(u"Доступ с учётом времени")
        verbose_name_plural = _(u"Доступ с учётом времени")
        permissions = (
            ("timeaccessservice_view", _(u"Просмотр услуг доступа по времени")),
            )
        db_table = "billservice_timeaccessservice"

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('tariff_timeaccessservice_delete'), self.id)

class TrafficTransmitService(Model):
    # name              = models.CharField(max_length=255, default='', blank=True)
    reset_traffic = models.BooleanField(verbose_name=_(u'Сбрасывать предоплаченный трафик'), blank=True, default=False)
    # Не реализовано в GUI
    # cash_method       = models.CharField(verbose_name=_(u"Списывать за класс трафика", max_length=32,choices=CHOISE_METHODS, blank=True, default=_(u'SUMM', editable=False)
    # Не реализовано в GUI
    # period_check      = models.CharField(verbose_name=_(u"Проверять на наибольший ", max_length=32,choices=CHECK_PERIODS, blank=True, default=_(u'SP_START', editable=False)


    def get_remove_url(self):
        return "%s?id=%s" % (reverse('traffictransmitservice_delete'), self.id)

    class Meta:
        verbose_name = _(u"Доступ с учётом трафика")
        verbose_name_plural = _(u"Доступ с учётом трафика")
        permissions = (
            ("traffictransmitservice_view", _(u"Просмотр")),
            )
        db_table = "billservice_traffictransmitservice"

class SettlementPeriod(Model):
    """
    Расчётный период
    """
    name = models.CharField(max_length=255, verbose_name=_(u'Название'), unique=True)
    time_start = models.DateTimeField(verbose_name=_(u'Начало периода'))
    length = models.IntegerField(blank=True, null=True, default=0, verbose_name=_(u'Период действия в секундах'))
    length_in = models.CharField(max_length=255, choices=PERIOD_CHOISES, null=True, blank=True, default='', verbose_name=_(u'Длина промежутка'))
    autostart = models.BooleanField(verbose_name=_(u'Начинать при активации'), default=False)

    def __unicode__(self):
        return u"%s%s" % ("+" if self.autostart else '', self.name,)

    class Admin:

        list_display = ('name', 'time_start', 'length', 'length_in', 'autostart')

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('settlementperiod_delete'), self.id)

    class Meta:
        ordering = ['name']
        verbose_name = _(u"Расчетный период")
        verbose_name_plural = _(u"Расчетные периоды")
        permissions = (
            ("settlementperiod_view", _(u"Просмотр расчётных периодов")),
            )
        db_table = "billservice_settlementperiod"

class SoftDeleteManager(models.Manager):
    ''' Use this manager to get objects that have a deleted field '''
    def get_query_set(self):
        return super(SoftDeleteManager, self).get_query_set().filter(deleted=False)
    def all_with_deleted(self):
        return super(SoftDeleteManager, self).get_query_set()
    def deleted_set(self):
        return super(SoftDeleteManager, self).get_query_set().filter(deleted=True)


class Tariff(Model):
    name = models.CharField(max_length=255, verbose_name=_(u'Название'), unique=True)
    description = models.TextField(verbose_name=_(u'Описание тарифного плана'), blank=True, default='')
    access_parameters = models.ForeignKey(to=AccessParameters, verbose_name=_(u'Параметры доступа'), null=True, blank=True, on_delete=models.SET_NULL)
    # contracttemplate = models.ForeignKey("ContractTemplate", verbose_name=_(u"Шаблон номера договора"), blank=True, null=True, on_delete=models.SET_NULL)
    time_access_service = models.ForeignKey(to=TimeAccessService, verbose_name=_(u'Доступ с учётом времени'), blank=True, null=True, on_delete=models.SET_NULL)
    traffic_transmit_service = models.ForeignKey(to=TrafficTransmitService, verbose_name=_(u'Доступ с учётом трафика'), blank=True, null=True, on_delete=models.SET_NULL)
    radius_traffic_transmit_service = models.ForeignKey(to="RadiusTraffic", verbose_name=_(u'RADIUS тарификация трафика'), blank=True, null=True, on_delete=models.SET_NULL)
    cost = models.FloatField(verbose_name=_(u'Стоимость пакета'), default=0 , help_text=_(u"Стоимость активации тарифного плана. Целесообразно указать с расчётным периодом. Если не указана-предоплаченный трафик и время не учитываются"))
    reset_tarif_cost = models.BooleanField(verbose_name=_(u'Производить доснятие'), blank=True, default=False, help_text=_(u'Производить доснятие суммы до стоимости тарифного плана в конце расчётного периода'))
    settlement_period = models.ForeignKey(to=SettlementPeriod, blank=True, null=True, verbose_name=_(u'Расчётный период'))
    ps_null_ballance_checkout = models.BooleanField(verbose_name=_(u'Производить снятие денег  при нулевом баллансе'), help_text=_(u"Производить ли списывание денег по периодическим услугам при достижении нулевого балланса или исчерпании кредита?"), blank=True, default=False)
    active = models.BooleanField(verbose_name=_(u"Активен"), default=False, blank=True)
    deleted = models.BooleanField(default=False, blank=True)
    allow_express_pay = models.BooleanField(verbose_name=_(u'Оплата экспресс картами'), blank=True, default=False)
    require_tarif_cost = models.BooleanField(verbose_name=_(u"Требовать наличия стоимости пакета"), default=False, blank=True)
    allow_userblock = models.BooleanField(verbose_name=_(u"Разрешить пользовательскую блокировку"), blank=True, default=False)
    userblock_cost = models.DecimalField(verbose_name=_(u"Стоимость блокировки"), decimal_places=2, max_digits=30, blank=True, default=0)
    userblock_max_days = models.IntegerField(verbose_name=_(u"MAX длительность блокировки"), blank=True, default=0)
    userblock_require_balance = models.DecimalField(verbose_name=_(u"Минимальный баланс для блокировки"), decimal_places=2, max_digits=10, blank=True, default=0)
    allow_ballance_transfer = models.BooleanField(verbose_name=_(u"Разрешить услугу перевода баланса"), blank=True, default=False)
    vpn_ippool = models.ForeignKey("IPPool", verbose_name=_(u"VPN IP пул"), blank=True, null=True, related_name='tariff_vpn_ippool_set', on_delete=models.SET_NULL)
    vpn_guest_ippool = models.ForeignKey("IPPool", verbose_name=_(u"Гостевой VPN IP пул"), blank=True, null=True, related_name='tariff_guest_vpn_ippool_set', on_delete=models.SET_NULL)
    objects = SoftDeleteManager()

    def __unicode__(self):
        return u"%s" % self.name

    class Admin:
        list_display = ('name', 'access_parameters',)


    class Meta:
        ordering = ['name']
        verbose_name = _(u"Тариф")
        verbose_name_plural = _(u"Тарифы")
        permissions = (
           ("tariff_view", _(u"Просмотр")),
            )
        db_table = "billservice_tariff"

    def delete(self):
        if not self.deleted:
            self.deleted = True
            self.save()
            return
        super(Tariff, self).delete()


    def get_row_class(self):
        return STATUS_CLASS.get(self.active)

class AccountTarif(Model):
    account = models.ForeignKey(verbose_name=_(u'Пользователь'), to=BillserviceAccount, related_name='related_accounttarif')
    tarif = models.ForeignKey(to=Tariff, verbose_name=_(u'Тарифный план'), related_name="account_tarif")
    datetime = models.DateTimeField(verbose_name=_(u'C даты'), default='', blank=True)
    periodical_billed = models.BooleanField(blank=True)

    class Admin:
        ordering = ['-datetime']
        list_display = ('account', 'tarif', 'datetime')

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('accounttariff_delete'), self.id)

    def __unicode__(self):
        return u"%s, %s" % (self.account, self.tarif)

    class Meta:
        ordering = ['-datetime']
        verbose_name = _(u"Тариф аккаунта")
        verbose_name_plural = _(u"Тариф аккаунта")
        permissions = (
           ("accounttarif_view", _(u"Просмотр")),
            )
        db_table = "billservice_accounttarif"


class RadiusTraffic(Model):
    direction = models.IntegerField(verbose_name=_(u"Направление"), blank=True, default=2, choices=((0, _(u"Входящий")), (1, _(u"Исходящий")), (2, _(u"Сумма")), (3, _(u"Максимум"))))
    tarification_step = models.IntegerField(verbose_name=_(u"Единица тарификации, кб."), blank=True, default=1024)
    rounding = models.IntegerField(verbose_name=_(u"Округление"), default=0, blank=True, choices=((0, _(u"Не округлять")), (1, _(u"В большую сторону")),))
    prepaid_direction = models.IntegerField(blank=True, default=2, verbose_name=_(u"Предоплаченное направление"), choices=((0, _(u"Входящий")), (1, _(u"Исходящий")), (2, _(u"Сумма")), (3, _(u"Максимум"))))
    prepaid_value = models.IntegerField(verbose_name=_(u"Объём, мб."), blank=True, default=0)
    reset_prepaid_traffic = models.BooleanField(verbose_name=_(u"Сбрасывать предоплаченный трафик"), blank=True, default=False)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    deleted = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = _(u"Услуга тарификации RADIUS трафика")
        verbose_name_plural = _(u"Услуги тарификации RADIUS трафика")
        permissions = (
           ("radiustraffic_view", _(u"Просмотр")),
           )
        db_table = "billservice_radiustraffic"

    def get_remove_url(self):
        return "%s?id=%s" % (reverse('radiustrafficservice_delete'), self.id)


SERVICE_TYPES = (
        (u"PPTP/L2TP", u"PPTP"),
        (u"PPPOE", u"PPPOE"),
        (u"DHCP", u"DHCP"),
        (u"HotSpot", u"HOTSPOT"),
        )
SESSION_STATUS = (
                (u"ACTIVE", u"Активна",),
                (u"NACK", u"Не сброшена",),
                (u"ACK", u"Cброшена",),
                )

# Create your models here.
class ActiveSession(models.Model):
    account = models.ForeignKey(BillserviceAccount, verbose_name=u'Аккаунт')
    subaccount = models.ForeignKey(SubAccount, verbose_name=u'Субаккаунт')
    # Атрибут радиуса Acct-Session-Id
    sessionid = models.CharField(max_length=255, blank=True, verbose_name=u'ID')
    # Время последнего обновления
    interrim_update = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=u'Последнее обновление')
    # Время старта сессии
    date_start = models.DateTimeField(blank=True, null=True, verbose_name=u'Начало')
    # Время конца сессии
    date_end = models.DateTimeField(null=True, blank=True, verbose_name=u'Конец')
    # Атрибут радиуса Calling-Station-Id. IP адрес или мак-адрес
    caller_id = models.CharField(max_length=255, blank=True, verbose_name=u'Caller ID')
    # Атрибут радиуса Called-Station-Id (IP адрес или имя сервиса для PPPOE)
    called_id = models.CharField(max_length=255, blank=True, verbose_name=u'Called ID')
    framed_ip_address = models.CharField(max_length=255, blank=True, default='', verbose_name=u'IP')
    # Атрибут радиуса NAS-IP-Address
    nas_id = models.CharField(max_length=255, blank=True, verbose_name=u'Nas ID')
    nas_int = models.ForeignKey(Nas, blank=True, null=True, verbose_name=u'NAS') #'hotspot.Nas'
    # Атрибут радиуса Acct-Session-Time
    session_time = models.IntegerField(default=0, null=True, blank=True, verbose_name=u'Время')
    # Нужно определить каким образом клиент подключился к серверу
    framed_protocol = models.CharField(max_length=32, choices=SERVICE_TYPES, verbose_name=u'Протокол')
    # Атрибут радиуса Acct-Input-Octets
    bytes_in = models.IntegerField(null=True, blank=True, verbose_name=u'IN')
    # Атрибут радиуса Acct-Output-Octets
    bytes_out = models.IntegerField(null=True, blank=True, verbose_name=u'OUT')
    # Выставляется в случае, если был произведён платёж
    session_status = models.CharField(max_length=32, choices=SESSION_STATUS, null=True, blank=True, verbose_name=u'Статус')
    speed_string = models.CharField(max_length=255, blank=True, null=True)
    acct_terminate_cause = models.CharField(verbose_name=u'Причина разрыва', max_length=128, blank=True, default='')
    # speed_changed = models.BooleanField(blank=True, default=False)
    ipinuse = models.ForeignKey(IPInUse, blank=True, null=True, on_delete=models.SET_NULL)



    class Admin:
        ordering = ['-id']
        list_display = ('account', 'bytes_in', 'bytes_out', 'sessionid', 'date_start', 'interrim_update', 'date_end', 'caller_id', 'called_id', 'session_time', 'session_status')

    class Meta:
        db_table = 'radius_activesession'
        verbose_name = u"RADIUS сессия"
        verbose_name_plural = u"RADIUS сессии"
        permissions = (
           ("activesession_view", u"Просмотр"),
           )

    def get_row_class(self):
        return STATUS_CLASS.get(self.session_status)

    def __unicode__(self):
        return u"%s" % self.sessionid
