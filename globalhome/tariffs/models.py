# coding: utf-8
from django.db import models
from billing.models import BillingManager
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
import settings
from datetime import datetime

class TelZoneGroup(models.Model):
    """
        Модель - группа телефонных зон
    """
    name = models.CharField(max_length=255, unique=True, verbose_name=_(u"Telzone group name"))
    var_slug = models.CharField(max_length=255, unique=True, verbose_name=_(u"Variable slug"))

    objects = BillingManager()

    def save(self, *args, **kwargs):
        kwargs["using"] = settings.BILLING_DB
        return super(TelZoneGroup, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

    class Meta:
        managed = True
        db_table = "tel_zone_groups"
        ordering = ("name",)
        verbose_name = _(u"Telzone group")
        verbose_name_plural = _(u"Telzone groups")


class TelZone(models.Model):
    """
        Модель - телефонная зона со своим id и именем. Так же тут предполагаю хранить локализованные названия зон
    """
    name = models.CharField(max_length=255, unique=True, verbose_name=_(u"Telzone name"))
    group = models.ForeignKey(TelZoneGroup, verbose_name=_(u"Telzone group"))
    ru_RU = models.CharField(max_length=255, verbose_name=_(u"Russian telzone name"), blank=True, null=True)

    objects = BillingManager()

    def save(self, *args, **kwargs):
        kwargs["using"] = settings.BILLING_DB
        return super(TelZone, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.ru_RU or self.name
        # return self.name

    class Meta:
        managed = True
        db_table = "tel_zones"
        ordering = ("name",)
        verbose_name = _(u"Telzone")
        verbose_name_plural = _(u"Telzones")


class TelCode(models.Model):
    """
        Модель - телефонный код указанной телефонной зоны
    """
    tel_zone = models.ForeignKey(TelZone, verbose_name=_(u"Telzone"))

    code = models.CharField(max_length=20, verbose_name=_(u"Code"), null=False, blank=False)

    objects = BillingManager()

    def save(self, *args, **kwargs):
        kwargs["using"] = settings.BILLING_DB
        return super(TelCode, self).save(*args, **kwargs)

    @property
    def tel_zone_name(self):
        return unicode(self.tel_zone)

    def __unicode__(self):
        return unicode(self.tel_zone) + u" : " + self.code

    class Meta:
        managed = True
        db_table = "tel_code"
        ordering = ("tel_zone", "code")
        verbose_name = _(u"Telcode")
        verbose_name_plural = _(u"Telcodes")


class TariffGroup(models.Model):
    """
        Модель - тарифная группа пользователей
    """
    group_name = models.CharField(max_length=255, unique=True, verbose_name=_(u"Tariff group name"))

    objects = BillingManager()

    def save(self, *args, **kwargs):
        k = str(self.id)
        kwargs["using"] = settings.BILLING_DB
        return super(TariffGroup, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        from billing.models import BillserviceAccount
        try:
            bacs = BillserviceAccount.objects.filter(group_id=self.id)
        except:
            bacs = []

        for bac in bacs:
            bac.group_id = 1
            bac.save()

        return super(TariffGroup, self).delete(*args, **kwargs)

    def __unicode__(self):
        return self.group_name

    class Meta:
        managed = True
        db_table = "billservice_groups"
        verbose_name = _(u"Tariff group")
        verbose_name_plural = _("Tariff groups")


class TariffsManager(BillingManager):
    def get_query_set(self):
        qs = super(TariffsManager, self).get_query_set()
        need_new = False
        for item in qs:
            if item.is_active == None:
                need_new = True
                item.is_active = item.is_active_check()
                item.save()

        if need_new:
            qs = super(TariffsManager, self).get_query_set()

        return qs


class Tariff(models.Model):
    """
        Это модель для представления тарифа
    """

    billing_group = models.ForeignKey(TariffGroup, verbose_name=_(u"Tariff group"))
    tel_zone = models.ForeignKey(TelZone, verbose_name=_(u"Telzone"))
    price = models.FloatField(verbose_name=_(u"Price"))
    start_date = models.DateField(verbose_name=_(u"Start date"), default=datetime.now().date())
    end_date = models.DateField(verbose_name=_(u"End date"), null=True, blank=True)

    is_active = models.BooleanField(verbose_name=_(u"Is active"))  # такое фейковое поле получается по сути... но без него не пашет фильтр ну никак

    objects = TariffsManager()

    def get_start_date(self):
        return str(self.start_date.strftime("%d.%m.%Y"))
    get_start_date.short_description = _(u"Start date")

    def get_end_date(self):
        null_str = u"\u221E"  # символ бесконечности
        if self.end_date:
            if type(self.end_date) is datetime:
                self.end_date = self.end_date.date()
            if self.end_date < datetime.max.date():
                return str(self.end_date.strftime("%d.%m.%Y"))
            else:
                return null_str
        else:
            return null_str
    get_end_date.short_description = _(u"End date")


    def is_active_check(self, custom_date=''):
        try:
            custom_date = datetime.strptime(custom_date, '%d-%m-%Y').date() if custom_date else datetime.now().date()
        except:
            custom_date = datetime.now().date()
        if type(self.start_date) == datetime:
            self.start_date = self.start_date.date()
        if self.end_date:
            if type(self.end_date) == datetime:
                self.end_date = self.end_date.date()
        if custom_date >= self.start_date:
            if self.end_date:
                if custom_date >= self.end_date:
                    return False
                else:
                    return True
            else:
                return True
        else:
            return False


    def save(self, *args, **kwargs):
        self.is_active = self.is_active_check()
        if not self.end_date:
            self.end_date = datetime.max.date()

        def ddate(d):
            if type(d) is datetime:
                return d.date()
            else:
                return d

        # вот тут еще закрываю тарифы соответствующей зоны

        no_close_tariffs = kwargs.get("no_close_tariffs")
        if not no_close_tariffs is None:
            del kwargs["no_close_tariffs"]

        if no_close_tariffs is None or no_close_tariffs == False:
            tfs = Tariff.objects.filter(tel_zone=self.tel_zone, billing_group=self.billing_group)
            for t in tfs:
                if ddate(t.start_date) < ddate(self.start_date):
                    if ddate(t.end_date) > ddate(self.end_date):
                        # появляется хвост справа
                        new_t = Tariff()
                        new_t.billing_group = t.billing_group
                        new_t.tel_zone = t.tel_zone
                        new_t.price = t.price
                        new_t.start_date = ddate(self.end_date)
                        new_t.end_date = t.end_date
                        new_t.save(no_close_tariffs=True)
                    else:
                        # просто закрываем старый тариф
                        if ddate(t.end_date) > ddate(self.start_date):
                            t.end_date = ddate(self.start_date)
                            t.save(no_close_tariffs=True)
                else:
                    # правая часть схемы
                    if ddate(t.end_date) <= ddate(self.end_date):
                        t.delete()
                    else:
                        t.start_date = ddate(self.end_date)
                        t.save(no_close_tariffs=True)

        return super(Tariff, self).save(*args, **kwargs)

    def __unicode__(self):
        return "%s : %s, %s" % (self.billing_group.group_name, self.tel_zone, self.price)

    class Meta:
        db_table = "tel_price"
        ordering = ("tel_zone",)
        verbose_name = _(u"Tariff")
        verbose_name_plural = _("Tariffs")



class UploadTariffs(models.Model):
    class Meta:
        verbose_name = _("Upload tariffs from CSV file")
        verbose_name_plural = _("Upload tariffs from CSV file")
        managed = False
        _

class tuts(models.Model):
    class Meta:
       verbose_name_plural = "Массавая рассылка почты"
       managed = False




