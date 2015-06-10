# coding: utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _
from billing.managers import BillingManager
from django.conf import settings
from externalnumbers.consts import *
# import log
from externalnumbers.managers import FreeExternalNumbersManager
from billing.models import BillserviceAccount
from lib.utils import get_now
# from externalnumbers.consts import tarif, dc, dc_group, tarif_group
# from django.contrib.auth.models import User

class ExternalNumber(models.Model):
    """
    Externals (city) numbers
    """
    number = models.CharField(max_length=255)
    phone_numbers_group = models.ForeignKey("TelNumbersGroup", blank=True, null=True)  # , related_name = "external_numbers")#, related_name = "+")
    region = models.IntegerField(default=MOSCOW, choices=REGIONS)
    tarif_group = models.IntegerField(default=1, choices=tarif_group, verbose_name="price_group")
    is_free = models.BooleanField(default=False, verbose_name=_(u"Is free"))
    is_reserved = models.BooleanField(default=True, verbose_name=_(u"Is reserved"))
    auth_user = models.IntegerField(blank=True, null=True)
    sip_address = models.CharField(max_length=100, default=None, verbose_name=_(u"Sip address"), blank=True, null=True)
    dinging = models.BooleanField(default=False)
    # code = models.CharField(max_length=10, default='', verbose_name=_(u"Код"))

    # дату выделения номера сюда запихиваем
    assigned_at = models.DateTimeField(verbose_name=_(u"Assigned at"), blank=True, null=True)

    account = models.ForeignKey(BillserviceAccount, verbose_name=_(u"Account"), blank=True, null=True)
    blocked = models.BooleanField(default=False)
    date_deactivation = models.DateTimeField(null=True, blank=True, verbose_name=_(u"Date deactivation"))

    id_scheme = models.ForeignKey('account.AllScheme', null=True)
    objects = BillingManager()
    free_numbers = FreeExternalNumbersManager()

    def get_zone(self):
        if self.region:
            return get_region_zone(self.region)

    def make_reserved(self):
        print 'tut'
        self.assigned_at = None
        # self.region = None
        self.is_reserved = True
        self.is_free = False
        self.phone_numbers_group = None
        self.account = None
        self.save(no_assigned_at_save=True)

    def make_free(self, region=None):
        self.is_free = True
        self.is_reserved = False
        self.assigned_at = None
        # if region:
        #    self.region = region
        self.phone_numbers_group = None
        self.account = None
        self.save(no_assigned_at_save=True)
    def set_tarif(self, tarif=None):
        if tarif:
            self.tarif_group = tarif
        self.save(no_assigned_at_save=True)

    def set_region(self, region=None):
        if region:
            self.region = region
        self.save(no_assigned_at_save=True)
    '''
    def get_assigned_service(self):
        from services.models import AssignedService, Service
        s = Service.objects.get(slug = "localnumber")
        return AssignedService.get_by_params({ "localnumber_id": self.id }, assigned_to = self.account.get_user(), service = s)
    '''

    def get_service_packet_application(self):
        from services.models import ServicePacketApplication
        try:
            return ServicePacketApplication.filter_by_params(
                { "localnumbers_add_num_id": self.id },
                self.account.get_user,
                packet_slug="localphones_packet"
            )[0]
        except:
            return None

    def get_assigned_service_packet(self):
        from services.models import AssignedServicePacket
        try:
            return AssignedServicePacket.filter_by_params(
                { "localnumbers_add_num_id": self.id },
                self.account.get_user,
                packet_slug="localphones_packet"
            )[0]
        except:
            return None


    def update_free_reserved(self, save=True):
        "Обеспечивает то, что в is_free и в is_reserved хранятся верные значения, судя по region"
        # self.is_free = (self.account is None) and (self.region > 0)
        # self.is_reserved = ((self.region is None) or (self.region == 0)) and (self.account is None)
        # self.is_reserved = False if self.is_free else True
        if save:
            self.save()

    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        assigned_at = kwargs.pop("assigned_at", None)
        if not kwargs.pop("no_assigned_at_save", False):
            if assigned_at:
                self.assigned_at = assigned_at
            else:
                self.assigned_at = get_now()
        # self.update_free_reserved(save=False)
        return super(ExternalNumber, self).save(*args, **kwargs)

    def __unicode__(self):
        rs = self.region_str
        if rs:
            return self.number + u" - " + rs
        else:
            return self.number

    @property
    def region_str(self):
        if self.region:
            for reg in REGIONS:
                if reg[0] == self.region:
                    return reg[1]
        else:
            return u""

    @staticmethod
    def get_free_numbers_by_regions(items=None):
        "Возвращает dict у которого ключ - регион, а значение - список свободных номеров этого региона"
        result = {}
        if not items:
            items = ExternalNumber.free_numbers.all()
        for number in items:
            row = result.get(number.region)
            if row:
                row.append(number)
            else:
                result[number.region] = [number, ]
        return result

    @staticmethod
    def free_numbers_limited(limit):
        all_numbers = ExternalNumber.free_numbers.all()
        reg_counts = {}
        for reg in REGIONS:
            reg_counts[reg[0]] = 0
        for num in all_numbers:
            try:
                if reg_counts[num.region] < limit:
                    reg_counts[num.region] += 1
                    yield num
                else:
                    end = True
                    for k in reg_counts:
                        if reg_counts[k] < limit:
                            end = False
                            break
                    if end:
                        break
            except:
                continue
#     10, 5, 2, 7499
    @staticmethod
    def get_numb_tarif_limit(max, price_group, region, code):
        all = ExternalNumber.free_numbers.all()
        ch = []
        z = 0
        vi = {}
        for t in all:
            if z == max:
                vi = {}
                break
            if t.tarif_group == price_group and region == t.region and t.number[0:4] == code:
                vi = {}
                z += 1
                vi['id'] = t.id
                vi['number'] = t.number
                ch.append(vi)
        return ch

    @staticmethod
    def get_numbers_tarif_limit_random(count, tarif):
        numbers = ExternalNumber.objects.filter(tarif_group=tarif, is_free=True).order_by('?')[:count]
        return numbers

    def get_about(self):
        return ExternalNumberTarif.objects.get(id=self.tarif_group).about


    class Meta:
        db_table = 'external_numbers'
        managed = False
        ordering = ("number",)
        verbose_name = _(u"Local number")
        verbose_name_plural = _(u"Local numbers")
        app_label = "telnumbers"

class ExternalNumberTarif(models.Model):
    name = models.CharField(max_length=255)
    about = models.CharField(max_length=255, default='')
    price_add = models.IntegerField(default=3, choices=tarif)
    price_abon = models.IntegerField(default=4, choices=tarif)
    precode = models.IntegerField(default=0)
    data_centr_tariff = models.ForeignKey('data_centr.Tariff', default=1)
    data_centr_price_connection = models.ForeignKey('data_centr.Price_connection', default=1)

    def __unicode__(self):
        return self.about

    objects = BillingManager()
    class Meta:
        db_table = 'external_numbers_tarif'
        # managed = False
        ordering = ("name",)
        verbose_name = _(u"tarif")
        verbose_name_plural = _(u"tarif")
        app_label = "telnumbers"

class Number800Payments(models.Model):
    tariff = models.ForeignKey(ExternalNumberTarif)
    connect = models.DecimalField(default='0', max_digits=14, decimal_places=2)
    abon = models.DecimalField(default='0', max_digits=14, decimal_places=2)
    guaranteed = models.DecimalField(default='0', max_digits=14, decimal_places=2)
    category = models.DecimalField(default='0', max_digits=14, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(default=None, blank=True, null=True)
    reservation = models.DecimalField(default='0', max_digits=14, decimal_places=2)
    pause = models.DecimalField(default='0', max_digits=14, decimal_places=2)
    month_pause = models.IntegerField(default=0)

    objects = BillingManager()

    class Meta:
        db_table = 'number800_payments'

class Number800Regiones(models.Model):
    name = models.CharField(max_length=255)

    objects = BillingManager()

    class Meta:
        db_table = 'number800_regiones'

class Number800TrafficTariff(models.Model):
    min = models.IntegerField(default=0)
    max = models.IntegerField(default=0)
    region = models.ForeignKey(Number800Regiones)
    cost = models.DecimalField(default='0', max_digits=14, decimal_places=2)

    objects = BillingManager()

    class Meta:
        db_table = 'number800_traffic_tariff'

class Number800Codes(models.Model):
    code = models.CharField(max_length=10)
    region = models.ForeignKey(Number800Regiones)

    objects = BillingManager()

    @staticmethod
    def get_region_by_number(number):
        return Number800Regiones.objects.db_manager(settings.BILLING_DB).raw("SELECT * FROM number800_region_codes WHERE code = substring('%s' from 1 for length(code)) ORDER BY length(code) DESC LIMIT 1" % number)

    class Meta:
        db_table = 'number800_region_codes'


class ExternalNumberUsing(models.Model):
    number = models.ForeignKey(ExternalNumber)  # , related_name = "external_numbers")#, related_name = "+")
    using_at = models.DateField(verbose_name=_(u"Using at"))

    objects = BillingManager()

    class Meta:
        db_table = 'external_numbers_using'
