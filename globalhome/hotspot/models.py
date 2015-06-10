# -*- coding=UTF-8 -*-


from django.db import models
from django.conf import settings
from settings import BILLING_DB
from billing.models import BillserviceAccount
from lib.mail import send_email
from django.contrib.auth.models import User
import trans
# from data_centr.models import Tariff


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

NAS_LIST = (
                (u'mikrotik2.8', u'MikroTik 2.8'),
                (u'mikrotik2.9', u'MikroTik 2.9'),
                (u'mikrotik3', u'Mikrotik 3'),
                (u'mikrotik4', u'Mikrotik 4'),
                (u'mikrotik5', u'Mikrotik 5'),
                (u'common_radius', u'Общий RADIUS интерфейс'),
                (u'common_ssh', u'common_ssh'),
                (u'cisco', u'cisco'),
                (u'localhost', u'localhost'),
                )

class IPPool(models.Model):
    name = models.CharField(max_length=255)
    # 0 - VPN, 1-IPN
    type = models.IntegerField()
    start_ip = models.IPAddressField()
    end_ip = models.IPAddressField()
    next_ippool = models.ForeignKey("IPPool", blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = u"IP РїСѓР»"
        verbose_name_plural = u"IP РїСѓР»С‹"
        permissions = (
           ("ippool_view", u"РџСЂРѕСЃРјРѕС‚СЂ"),
           )
    def __unicode__(self):
        return u"%s-%s" % (self.start_ip, self.end_ip)

class IPInUse(models.Model):
    pool = models.ForeignKey(IPPool)
    ip = models.CharField(max_length=255)
    datetime = models.DateTimeField()
    disabled = models.DateTimeField(blank=True, null=True)
    dynamic = models.BooleanField(default=False)

class Games_Section(models.Model):
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=200)
    def __unicode__(self):
        return self.name

class Games(models.Model):
    game_name = models.CharField(max_length=200, verbose_name=u"Название игры")
    banner = models.TextField(verbose_name=u'Баннер')
    description = models.TextField(verbose_name=u"Описание")
    section = models.CharField(max_length=200, null=True, blank=True)
    section2 = models.CharField(max_length=200, null=True, blank=True)
    section_game = models.ManyToManyField(Games_Section, default=1, verbose_name=u'Раздел игры')
    img = models.CharField(max_length=200, verbose_name=u"Изображение")
    http = models.CharField(max_length=200, verbose_name=u"Ссылка")

    def __unicode__(self):
        return self.game_name

    class Meta:
        ordering = ['game_name']
        verbose_name = "Игру"
        verbose_name_plural = u'Игры'




class Nas(models.Model):
    """
    /ip firewall address-list add address=$ipaddress list=allow_ip comment=$user_id
    /ip firewall address-list remove $user_id
    """
    type = models.CharField(choices=NAS_LIST, max_length=32, default='mikrotik3')
    identify = models.CharField(verbose_name=u'RADIUS идентификатор сервера доступа', max_length=255)
    name = models.CharField(verbose_name=u'Идентификатор сервера доступа', help_text=u"Используется дли идентификации сервера доступа. Смотрите настройки /system identity print", max_length=255, unique=True)
    ipaddress = models.CharField(verbose_name=u'IP адрес сервера доступа', max_length=255)
    secret = models.CharField(verbose_name=u'Секретная фраза', help_text=u"Смотрите вывод команды /radius print", max_length=255)
    login = models.CharField(verbose_name=u'Имя для доступа к серверу по SSH', max_length=255, blank=True, default='admin')
    password = models.CharField(verbose_name=u'Пароль для доступа к серверу по SSH', max_length=255, blank=True, default='')
    # description = models.TextField(verbose_name=u'Описание', blank=True, default='')
    allow_pptp = models.BooleanField(verbose_name=u'Разрешить серверу работать с PPTP', default=True)
    allow_pppoe = models.BooleanField(verbose_name=u'Разрешить серверу работать с PPPOE', default=True)
    allow_ipn = models.BooleanField(verbose_name=u'Сервер поддерживает IPN', help_text=u"IPN - технология, которая позволяет предоставлять доступ в интернет без установления VPN соединения с сервером доступа", default=True)
    user_add_action = models.TextField(verbose_name=u'Действие при создании пользователя', blank=True, null=True)
    user_enable_action = models.TextField(verbose_name=u'Действие при разрешении работы пользователя', blank=True, null=True)
    user_disable_action = models.TextField(verbose_name=u'Действие при запрещении работы пользователя', blank=True, null=True)
    user_delete_action = models.TextField(verbose_name=u'Действие при удалении пользователя', blank=True, null=True)
    vpn_speed_action = models.TextField(max_length=255, blank=True, default="")
    ipn_speed_action = models.TextField(max_length=255, blank=True, default="")
    reset_action = models.TextField(max_length=255, blank=True, default="")
    confstring = models.TextField(verbose_name="Конфигурация по запросу", blank=True, default='')
    subacc_disable_action = models.TextField(blank=True, default="")
    subacc_enable_action = models.TextField(blank=True, default="")
    subacc_add_action = models.TextField(blank=True, default="")
    subacc_delete_action = models.TextField(blank=True, default="")
    subacc_ipn_speed_action = models.TextField(blank=True, default="")
    snmp_version = models.CharField(verbose_name=u'Версия SNMP', max_length=10, blank=True, null=True)
    speed_vendor_1 = models.TextField(blank=True, default="")
    speed_vendor_2 = models.TextField(blank=True, default="")
    speed_attr_id1 = models.TextField(blank=True, default="")
    speed_attr_id2 = models.TextField(blank=True, default="")
    speed_value1 = models.TextField(blank=True, default="")
    speed_value2 = models.TextField(blank=True, default="")
    acct_interim_interval = models.IntegerField(default=60, blank=True, null=True)
    data_centr_tarif = models.ForeignKey('data_centr.Tariff', blank=True, null=True)


    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        db_table = 'nas_nas'


class ActiveSession(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID")
    # account_id = models.IntegerField()
    account = models.ForeignKey(BillserviceAccount, related_name="hotspot_activesession_acc", blank=True, null=True)
    # subaccount_id = models.IntegerField()
    subaccount = models.ForeignKey('internet.SubAccount', related_name="hotspot_activesession_sub", blank=True, null=True)  # BillserviceSubAccount
    sessionid = models.CharField(max_length=255, blank=True)
    date_start = models.DateTimeField(blank=True, null=True)
    date_end = models.DateTimeField(null=True, blank=True)
    framed_ip_address = models.CharField(max_length=255, blank=True, default='')
    bytes_in = models.IntegerField(null=True, blank=True)
    bytes_out = models.IntegerField(null=True, blank=True)
    session_time = models.IntegerField()  # IntegerField(default=0, null=True,blank=True)


    # Атрибут радиуса Acct-Session-Id
    # Время последнего обновления
    interrim_update = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    # Время старта сессии
    # Время конца сессии
    # Атрибут радиуса Calling-Station-Id. IP адрес или мак-адрес
    caller_id = models.CharField(max_length=255, blank=True)
    # Атрибут радиуса Called-Station-Id (IP адрес или имя сервиса для PPPOE)
    # called_id=models.CharField(max_length=255, blank=True)

    # Атрибут радиуса Acct-Output-Octets
    # Атрибут радиуса NAS-IP-Address
    nas_id = models.CharField(max_length=255, blank=True)

    nas_int = models.ForeignKey(Nas, related_name="hotspot_nas", blank=True, null=True)
    # nas_int=models.CharField(max_length=255, blank=True)
    # Атрибут радиуса Acct-Session-Time
    # Нужно определить каким образом клиент подключился к серверу
    framed_protocol = models.CharField(max_length=32, choices=SERVICE_TYPES)
    # Атрибут радиуса Acct-Input-Octets
    # Выставляется в случае, если был произведён платёж
    session_status = models.CharField(max_length=32, choices=SESSION_STATUS, null=True, blank=True)
    speed_string = models.CharField(max_length=255, blank=True, null=True)
    acct_terminate_cause = models.CharField(max_length=128, blank=True, default='')
    # speed_changed = models.BooleanField(blank=True, default=False)

    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB

    class Meta:
        managed = False
        db_table = 'radius_activesession'
        verbose_name = u'Активная radius сессия'
        verbose_name_plural = u'Активные radius сессии'

    def __unicode__(self):
        return u"%s" % self.sessionid


#
# class Switch(models.Model):
#    manufacturer = models.CharField(max_length=250, blank=True, default='')
#    model = models.CharField(max_length=500, blank=True, default='')
#    name = models.CharField(max_length=500, blank=True, default='')
#    sn = models.CharField(max_length=500, blank=True, default='')
#    city = models.IntegerField(db_column='city_id')
#    street = models.IntegerField(db_column='street_id')
#    house = models.IntegerField(db_column='house_id')
#    place = models.TextField(blank=True, default='')#место установки
#    comment = models.TextField(blank=True, default='')#
#    ports_count = models.IntegerField(blank=True, default=0)
#    broken_ports = models.TextField(blank=True, default='')#через запятую
#    uplink_ports = models.TextField(blank=True, default='')#через запятую
#    protected_ports = models.TextField(blank=True, default='')#через запятую
#    monitored_ports = models.TextField(blank=True, default='')
#    disabled_ports = models.TextField(blank=True, default='')
#    snmp_support = models.BooleanField(default=False)
#    snmp_version = models.CharField(max_length=10, blank=True, default='v1')#version
#    snmp_community = models.CharField(max_length=128, blank=True, default='')#
#    ipaddress = models.IPAddressField(blank=True, default=None)
#    macaddress = models.CharField(max_length=32, blank=True, default='')
#    management_method = models.IntegerField(blank=True, default=1)
#    option82 = models.BooleanField(default=False)
#    option82_auth_type = models.IntegerField( blank=True, null=True)#1-port, 2 - mac+port, 3-mac
#    secret = models.CharField(max_length=128, blank=True, default='')
#    identify = models.CharField(max_length=128, blank=True, default='')
#    username = models.CharField(max_length=256, blank=True, default='')
#    password = models.CharField(max_length=256, blank=True, default='')
#    enable_port = models.TextField(blank=True, default='')
#    disable_port = models.TextField(blank=True, default='')
#    option82_template = models.TextField(blank=True, default='')
#    remote_id = models.TextField(blank=True, default='')
#
#    def __unicode__(self):
#        return u"%s" % self.name




# class BillserviceSubAccount(models.Model):
#    account = models.ForeignKey(BillserviceAccount, related_name='subaccounts')
#    username = models.CharField(max_length=512, blank=True)
#    password = models.CharField(max_length=512, blank=True)
#    ipn_ip_address = models.CharField(max_length= 10, blank=True,null=True, default='0.0.0.0')
#
#    #ipn_ip_address = IPNetworkField(blank=True,null=True, default='0.0.0.0'))
#
#    ipn_mac_address = models.CharField(blank=True, max_length=17, default='')
#    vpn_ip_address = models.IPAddressField(blank=True,null=True,  default='0.0.0.0')
#    allow_mac_update = models.BooleanField(default=False)
#    nas = models.ForeignKey('Nas', blank=True, null=True) #on_delete = models.SET_NULL)
#    ipn_added = models.BooleanField()
#    ipn_enabled = models.BooleanField()
#    ipn_sleep = models.BooleanField()
#    need_resync = models.BooleanField()
#    speed = models.TextField(blank=True)
#    switch = models.ForeignKey('Switch', blank=True, null=True)# on_delete = models.SET_NULL)
#    switch_port = models.IntegerField(blank=True, null=True)
#    allow_dhcp = models.BooleanField(blank=True, default=False)
#    allow_dhcp_with_null = models.BooleanField(blank=True, default=False)
#    allow_dhcp_with_minus = models.BooleanField(blank=True, default=False)
#    allow_dhcp_with_block = models.BooleanField(blank=True, default=False)
#    allow_vpn_with_null = models.BooleanField(blank=True, default=False)
#    allow_vpn_with_minus = models.BooleanField(blank=True, default=False)
#    allow_vpn_with_block = models.BooleanField(blank=True, default=False)
#    allow_ipn_with_null = models.BooleanField(blank=True, default=False)
#    allow_ipn_with_minus = models.BooleanField(blank=True, default=False)
#    allow_ipn_with_block = models.BooleanField(blank=True, default=False)
#    associate_pptp_ipn_ip = models.BooleanField(blank=True, default=False)
#    associate_pppoe_ipn_mac = models.BooleanField(blank=True, default=False)
#    ipn_speed = models.TextField(blank=True)
#    vpn_speed = models.TextField(blank=True)
#    allow_addonservice = models.BooleanField(blank=True, default=False)
#    vpn_ipinuse = models.ForeignKey(IPInUse, blank=True, null=True, related_name='subaccount_vpn_ipinuse_set')# on_delete=models.SET_NULL)
#    ipn_ipinuse = models.ForeignKey(IPInUse, blank=True, null=True, related_name='subaccount_ipn_ipinuse_set') #on_delete=models.SET_NULL)
#    vpn_ipv6_ip_address = models.CharField(blank=True, null=True, max_length=128, default='::')
#    vpn_ipv6_ipinuse = models.ForeignKey(IPInUse, blank=True, null=True, related_name='subaccount_vpn_ipv6_ipinuse_set') #, on_delete=models.SET_NULL)
#    #ipn_ipv6_ip_address = models.TextField(blank=True, null=True)
#    vlan = models.IntegerField(blank=True, null=True)
#    allow_mac_update = models.BooleanField(blank=True, default=False)
#    ipv4_ipn_pool = models.ForeignKey(IPPool, blank=True, default=None, null=True, related_name='subaccount_ipn_ippool_set') #, on_delete=models.SET_NULL)
#    ipv4_vpn_pool = models.ForeignKey(IPPool, blank=True, default=None, null=True, related_name='subaccount_vpn_ippool_set') #, on_delete=models.SET_NULL)

#    def save(self, *args, **kwargs):
#        kwargs['using'] = settings.BILLING_DB
#
#    def __unicode__(self):
#        return u"%s" % self.username
class Prefecturs(models.Model):
    name = models.CharField(u"Название организации", max_length=512, unique=True)
    adress = models.CharField(max_length=512)
    tel_numbers = models.CharField(max_length=512)
    fax = models.CharField(max_length=512, blank=True)
    subway_station = models.CharField(max_length=512)
    web_site = models.CharField(max_length=512, blank=True)
    email = models.CharField(max_length=512, blank=True)
    x = models.CharField(max_length=512)
    y = models.CharField(max_length=512)
    add_information = models.CharField(max_length=512, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'prefecturs'
        verbose_name = u'Префектура'
        verbose_name_plural = u'Префектуры'

class DistrictAdministration(models.Model):
    prefecturs = models.ForeignKey(Prefecturs, null=True, blank=True)
    name = models.CharField(max_length=512)
    adress = models.CharField(max_length=512)
    tel_numbers = models.CharField(max_length=512)
    fax = models.CharField(max_length=512, blank=True)
    subway_station = models.CharField(max_length=512, blank=True)
    web_site = models.CharField(max_length=512, blank=True)
    email = models.CharField(max_length=512, blank=True)
    x = models.CharField(max_length=512, blank=True)
    y = models.CharField(max_length=512, blank=True)
    add_information = models.CharField(max_length=512, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'district_administration'
        verbose_name = u'Районная управа'
        verbose_name_plural = u'Районные управы'

class HomeAdministration(models.Model):
    district_administration = models.ForeignKey(DistrictAdministration, null=True, blank=True, verbose_name=u'Администрация района')
    name = models.CharField(max_length=512)
    adress = models.CharField(max_length=512)
    tel_numbers = models.CharField(max_length=512)
    fax = models.CharField(max_length=512, blank=True)
    subway_station = models.CharField(max_length=512, blank=True)
    web_site = models.CharField(max_length=512, blank=True)
    email = models.CharField(max_length=512, blank=True)
    x = models.CharField(max_length=512, blank=True)
    y = models.CharField(max_length=512, blank=True)
    add_information = models.CharField(max_length=512, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'home_administration'
        verbose_name = u'Администрация дома'
        verbose_name_plural = u'Управляющие органзации домов'

import datetime
class HotSpotRate(models.Model):
    date = models.DateField()
    char_code = models.CharField(max_length=100,)
    nominal = models.IntegerField(max_length=512,)
    name = models.CharField(max_length=512,)
    value = models.DecimalField(max_digits=6, decimal_places=2,)
    def subtraction(self):
        return self.value - HotSpotRate.objects.get(char_code=self.char_code, date=self.date - datetime.timedelta(1)).value
    class Meta:
        db_table = 'hot_spot_rate'
        verbose_name = u'Курс валюты'
        verbose_name_plural = u'Курсы валют'

class HotSpotWeatger(models.Model):
    temp_now = models.CharField(max_length=100,)
    temp_d_n = models.CharField(max_length=100,)
    spr_class = models.CharField(max_length=100,)
    title = models.CharField(max_length=100, null=True)
    date = models.DateField(null=True)
    class Meta:
        db_table = 'hot_spot_weather'
        verbose_name = u'Погода'
        verbose_name_plural = u'Погода'




class HotSpotQueryStatistic(models.Model):
    query_string = models.CharField(max_length=512, blank=True, null=True)
    date_time = models.DateTimeField(auto_now_add=True, null=True)
    class Meta:
        db_table = 'hot_spot_query_statistic'
        verbose_name = u'Поисковой запрос'
        verbose_name_plural = u'Поисковые запросы'

class HotSpotReview(models.Model):
    contact_face = models.CharField(max_length=512, blank=True, null=True, verbose_name=u'Контактное лицо')
    adres = models.CharField(max_length=512, blank=True, null=True, verbose_name=u'Адрес')
    mail = models.EmailField(verbose_name=u'Email')
    telnumber = models.CharField(max_length=15, blank=True, null=True, verbose_name=u'Номер телефона')
    text = models.TextField(blank=True, null=True, verbose_name=u'Текст')
    was_treated = models.BooleanField(default=False, verbose_name=u'Обработано')
    type = models.CharField(max_length=15, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True, null=True, verbose_name=u'Дата подачи')
    class Meta:
        db_table = 'hot_spot_review'
        verbose_name = u'Отзыв'
        verbose_name_plural = u'Отзывы'

    def send_info_mail(self, subject):
        message = u''' 
                       Адрес: %(adress)s
             Контактное лицо: %(contact_face)s
              Номер телефона: %(tel_namber)s
           Электронная почта: %(mail)s
                        Дата: %(date)s                      
                  Информация: %(info)s
                   Обработан: %(running_state)s           
                '''
        message = message % { 'adress' : self.adres,
                             'contact_face' : self.contact_face,
                             'tel_namber' : self.telnumber,
                             'date' :  self.date,
                             'info' : self.text,
                             'running_state' : self.was_treated,
                             'mail':self.mail

                                                         }
        all = User.objects.filter(groups__id=2)
        email_list = []
        for user in all:
            email_list.append(user.email)
        send_email(subject, message, u'Globalhome.mobi', email_list)

class HotSpotComplaint(HotSpotReview):
    class Meta:
        proxy = True
        db_table = 'hot_spot_complaint'
        verbose_name = u'Жалоба'
        verbose_name_plural = u'Жалобы'


class MainNews(models.Model):
    title_news = models.CharField(max_length=1000, blank=True, null=True, verbose_name=u'Заголовок новости')
    discription_news = models.TextField(blank=True, null=True, verbose_name=u'Кр. описание новости')
    link_news = models.CharField(max_length=1000, blank=True, null=True, verbose_name=u'Адрес новости')
    img_news = models.CharField(max_length=1000, blank=True, null=True, verbose_name=u'Изображене новости')
    portal_name = models.CharField(max_length=512, blank=True, null=True, verbose_name=u'Имя новостного портала')
    portal_link = models.CharField(max_length=512, blank=True, null=True, verbose_name=u'Адрес портала')
    portal_diskription = models.CharField(max_length=512, blank=True, null=True, verbose_name=u'Слоган портала')
    portal_copyright = models.CharField(max_length=512, blank=True, null=True, verbose_name=u'Сopyright')
    date_get_news = models.DateField(auto_now_add=True, null=True, verbose_name=u'Дата получения новости')
    news_type = models.CharField(max_length=512, blank=True, null=True, verbose_name=u'Раздел новостей')
    img_news_root = models.CharField(max_length=1000, blank=True, null=True, verbose_name=u'Путь к файлу картинки')
    class Meta:
        db_table = 'hot_spot_main_news'
        verbose_name = u'Новость'
        verbose_name_plural = u'Новости'


#====================================================================================================
# модель для хранения стран, столиц и идентнификаторов для погодных api
class WeatherCountries(models.Model):
    id = models.AutoField(primary_key=True)
    country_rus_name = models.CharField(max_length=100,)
    city_rus_name = models.CharField(max_length=100,)
    country_eng_name = models.CharField(max_length=100,)
    city_eng_name = models.CharField(max_length=100,)
    yandex_city_id = models.IntegerField()
    openweathermap_name = models.CharField(max_length=100,)
    region_id = models.IntegerField()
    class Meta:
        db_table = 'hot_spot_weather_countries'
        verbose_name = u'Страна для погоды'
        verbose_name_plural = u'Страны для погоды'

#===================================================================================================
# модель для хранения погоды взятой с API
class MobiWeather(models.Model):
    # id = models.AutoField(primary_key=True)
    source_name = models.CharField(max_length=100,)
    # city = models.CharField(max_length=100,)
    taking_date = models.DateTimeField(blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    date_date_time = models.IntegerField(blank=True, null=True)
    cloud = models.CharField(max_length=100,)
    temp_from = models.FloatField()
    temp_to = models.FloatField()
    wind_speed = models.FloatField()
    wind_dir = models.CharField(max_length=5)
    pressure = models.FloatField()
    humidity = models.FloatField()
    city_weather_id = models.ForeignKey(WeatherCountries, blank=True, null=True)
    class Meta:
        db_table = 'hot_spot_mobi_weather'
        verbose_name = u'Моби погода'
        verbose_name_plural = u'Моби погода'

#======================================================================================================
ORGANIZATION_TYPE_CHOICES = (
        (1, u'drugstores'),
        (2, u'banks'),
        (3, u'restaurant'),
    )
#======================================================================================================
# модель для хранения уникальных организаций
class MobiOrganizationsUnique(models.Model):
    id = models.AutoField(primary_key=True)
    org_type = models.IntegerField(choices=ORGANIZATION_TYPE_CHOICES)
    yan_id = models.IntegerField()
    org_name = models.CharField(max_length=300,)
    location = models.CharField(max_length=300,)
    address = models.CharField(max_length=300,)
    url = models.CharField(max_length=300,)
    phone = models.CharField(max_length=300,)
    hours = models.CharField(max_length=300,)
    x = models.DecimalField(max_digits=16, decimal_places=10, blank=True, null=True)
    y = models.DecimalField(max_digits=16, decimal_places=10, blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    equal_coord_range = models.IntegerField(null=True)
    deleted = models.BooleanField(default=False, blank=True)

    class Meta:
        db_table = 'hot_spot_mobi_organizations_unique'

# модель для хранения заявок от пользователя на изменения данных по организации
class MobiOrganizationsUserChanges(models.Model):
    id = models.AutoField(primary_key=True)
    org_id = models.ForeignKey(MobiOrganizationsUnique)
    u_org_name = models.CharField(max_length=300, null=True, blank=True, verbose_name=u'Название')
    u_address = models.CharField(max_length=300, null=True, blank=True, verbose_name=u'Адрес')
    u_url = models.CharField(max_length=300, null=True, blank=True, verbose_name=u'Адрес сайта')
    u_phone = models.CharField(max_length=300, null=True, blank=True, verbose_name=u'Телефон')
    u_hours = models.CharField(max_length=300, null=True, blank=True, verbose_name=u'Часы работы')
    user_name = models.CharField(max_length=300, blank=True, verbose_name=u'Пользователь')
    user_email = models.CharField(max_length=300, blank=True, verbose_name=u'Адрес почты пользователя')
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name=u'Время создания заявки')
    applied = models.BooleanField(default=False, blank=True, verbose_name='Заявка обработана')
    to_del = models.BooleanField(default=False, blank=True, verbose_name='Удалить организацию')

    def __unicode__(self):

        return  u'%s %s' % (self.org_id.org_name, self.id)


    def org_name_original(self):
        return u'%s' % (self.org_id.org_name)
    org_name_original.short_description = u'Название организации'

    class Meta:
        db_table = 'hot_spot_mobi_organization_user_changes'
        verbose_name = (u'Заявка пользователя на исправления организаций')
        verbose_name_plural = (u'Заявки пользователя на исправления организаций')
#================================================================================================


VIDEO_TYPE_CHOICES = (
        (1, u'Фильмы'),
        (2, u'Серилы'),
    )





class VideoGenre(models.Model):
    id = models.AutoField(primary_key=True)
    translit_genre = models.CharField(max_length=100, blank=True, verbose_name=u'Транслит имя')
    genre = models.CharField(max_length=100, verbose_name=u'Имя жанра')
    # def __unicode__(self):
    #    return str(self.genre.encode('utf-8'))
    def f_translit_genre(self):
        return self.genre.encode('trans')
    class Meta:
        db_table = "hot_spot_video_genre"
        verbose_name = u'Жанр'
        verbose_name_plural = u'Жанры'

class Video_Rate(models.Model):
    id = models.AutoField(primary_key=True, verbose_name=u'ID фильма')
    rating_votes = models.CharField(max_length=300, verbose_name=u'Колличество голосов')
    rating_score = models.CharField(max_length=300, verbose_name=u'Рейтинг')
    def __unicode__(self):
        return str(self.id)
    class Meta:
        db_table = 'rate_video'
        verbose_name = u'Рейтинг сайта'
        verbose_name_plural = u'Рейтинг сайта'

class Comments_Of_Video(models.Model):
    commentator_name = models.CharField(max_length=300, verbose_name=u'Имя')
    comment_content = models.CharField(max_length=5000, verbose_name=u'Текст комментария')
    add_to_site = models.BooleanField(default='', verbose_name=u'Добавлен на сайт')
    def __unicode__(self):
        return str(self.id)
    class Meta:
        db_table = 'hotspot_video_comments'
        verbose_name = u'комментарий'
        verbose_name_plural = u'Комментарии к видео'


class HotSpot_Bad_Video_Link(models.Model):
    contact_face = models.CharField(max_length=512, blank=True, null=True, verbose_name=u'Контактное лицо')
    mail = models.EmailField(verbose_name=u'Email', blank=True, null=True)
    text = models.TextField(blank=True, null=True, verbose_name=u'Текст')
    broken_video_id = models.CharField(max_length=400, blank=True, null=True, verbose_name=u'Id неработающего видео')
    class Meta:
        db_table = 'hot_spot_bad_video_link'
        verbose_name = u'Неработающее видео'
        verbose_name_plural = u'Неработающее видео'


class Video(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    source = models.IntegerField()
    internal_number = models.IntegerField(null=True, blank=True)
    orig_title = models.CharField(max_length=300, verbose_name=u'Оригинальное название', blank=True)
    title = models.CharField(max_length=300, blank=True, verbose_name=u'Название')
    video_type = models.IntegerField(choices=VIDEO_TYPE_CHOICES, blank=True, verbose_name=u'Тип видео')
    genres = models.ManyToManyField(VideoGenre, null=True, blank=True, verbose_name=u'Жанры')
    genres_client_view = models.CharField(max_length=100, blank=True)
    year = models.CharField(max_length=100, blank=True, verbose_name=u'Год')
    country = models.CharField(max_length=300, blank=True, verbose_name=u'Страна')
    description = models.CharField(max_length=6000, blank=True, verbose_name=u'Описание')
    time = models.CharField(max_length=100, blank=True, verbose_name=u'Время')
    rating = models.IntegerField(null=True, blank=True, verbose_name=u'ID Кинопоиска')
    imdb_id = models.IntegerField(null=True, blank=True, verbose_name=u'ID Imdb')
    rating_by = models.CharField(max_length=1000, blank=True)
    image_link = models.CharField(max_length=200, blank=True, verbose_name=u'Ссылка изображения')
    player_video_url = models.CharField(max_length=9200, verbose_name=u'Ссылка на видео', unique=True)
    premiere_date = models.CharField(max_length=100, blank=True, verbose_name=u'Дата премьеры')
    age_restrictions = models.CharField(max_length=100, blank=True)
    quality = models.CharField(max_length=100, blank=True, verbose_name=u'Качество')
    sound = models.CharField(max_length=100, blank=True)
    budget = models.CharField(max_length=100, blank=True, verbose_name=u'Бюджет')
    director = models.CharField(max_length=100, blank=True)
    cast = models.CharField(max_length=600, blank=True)
    screenplay = models.CharField(max_length=600, blank=True)
    kp_rating = models.CharField(max_length=600, null=True, blank=True, verbose_name=u'Рейтинг кинопоиска')
    imdb_rating = models.CharField(max_length=600, null=True, blank=True, verbose_name=u'imdb рейтинг')
    label_text = models.CharField(default=1, max_length=50000, blank=True)
    one_serial_links = models.CharField(default=1, max_length=50000, blank=True)
    date_aded = models.DateTimeField(default=None, null=True, blank=True, verbose_name=u'Дата добавления')
    translit_video_name = models.CharField(max_length=400, null=True, blank=True, unique=True)
    site_rating = models.ForeignKey(Video_Rate, blank=True, null=True, verbose_name=u'Рейтинг сайта')
    # voted_ip = models.CharField(null = True, blank=True, max_length = 9000000, verbose_name = u'Проголосовавший ip')
    comments_m2m = models.ManyToManyField(Comments_Of_Video, blank=True, null=True, verbose_name=u'ID комментария')
    id_gid_film = models.CharField(max_length=1000, null=True, blank=True, unique=True)
    def rate_site(self):
        if self.site_rating:
            div = float(self.site_rating.rating_score) / float(self.site_rating.rating_votes)
            rating = round(div , 3)
            return rating
        else:
            return "Нет рейтинга"
    class Meta:
        db_table = 'hot_spot_video'
        verbose_name = u'Видео'
        verbose_name_plural = u'Видео'
        # unique_together = ('orig_title', 'id')
        # unique_together = ('title', 'id')

#=============================================================================================================================

  
    