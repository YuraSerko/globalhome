# coding: utf-8

from django.db import models
from django.utils.translation import ugettext_lazy as _
from billing.managers import BillingManager
from consts import *
# from externalnumbers.consts import *
# from externalnumbers.models import ExternalNumber
from django.conf import settings  # @UnresolvedImport
from billing.models import BillserviceAccount  # @UnresolvedImport
# import log
import datetime


class TelNumber(models.Model):
    account = models.ForeignKey(BillserviceAccount, blank=True, null=True, verbose_name=_(u"Account"))
    tel_number = models.CharField(max_length=64, default='', verbose_name=_(u"Internal number"), db_column="username")
    # login = models.CharField(max_length = 255, default = '')
    password = models.CharField(max_length=64, default='', db_column="text_password")
    internal_phone = models.CharField(max_length=5, default='', verbose_name=_(u"Short number"))
    # activated = models.BooleanField(default = False)
    person_name = models.TextField(default='', verbose_name=_(u"Owner name"))
    # is_deleted = models.BooleanField(default = False)
    is_free = models.BooleanField(default=False)
    is_blocked_call = models.IntegerField(default=0)
    template_out_call = models.ForeignKey('fs.NumberTemplates', null=True, default=None)

    objects = BillingManager()

    def __unicode__(self):
        return self.tel_number

    def save(self, *args, **kwargs):
        # log.add("saving TelNumber %s" % self.tel_number)
        super(TelNumber, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # log.add("deleting TelNumber %s" % self.tel_number)
        super(TelNumber, self).delete(*args, **kwargs)

    def get_view_name(self):
        if self.person_name:
            return self.tel_number + " - " + self.person_name
        else:
            return self.tel_number

    @staticmethod
    def get_next_free_number(is_hostel, is_juridical=True, is_mobi=False):
        "Возвращает первый свободный внутренний номер"
        if is_mobi:
            max_number = MAX_MOBI_NUMBER
            min_number = MIN_MOBI_NUMBER
        else:
            if is_juridical and is_hostel:
                max_number = MAX_HOSTEL_NUMBER
                min_number = MIN_HOSTEL_NUMBER
            else:
                if is_juridical:
                    max_number = MAX_JURIDICAL_NUMBER
                    min_number = MIN_JURIDICAL_NUMBER
                else:
                    max_number = MAX_PHYSICAL_NUMBER
                    min_number = MIN_PHYSICAL_NUMBER

        sql = "SELECT * FROM internal_numbers WHERE username::integer<=%s and username::integer>=%s and length(username)=7 ORDER BY username::integer DESC;" % (max_number, min_number)
        res = TelNumber.objects.raw(sql).using(settings.BILLING_DB)
        all_numbers = []
        for r in res:
            all_numbers.append(r.tel_number)

        # print "all_numbers=%s" % all_numbers
        if not all_numbers:
            return min_number

        start_number = all_numbers[0]

        for num in xrange(int(start_number), int(max_number) + 1):
            if str(num) in all_numbers:
                continue
            return str(num)


    @staticmethod
    def create(account, next_number=None, is_juridical=True, password="", person_name="", internal_phone="", save=True, is_mobi=False):
        "Создает новый телефонный номер для указанного аккаунта"
        is_hostel = False
        if account:
            if not next_number:
                next_number = TelNumber.get_next_free_number(is_hostel, is_juridical, is_mobi)
            number = TelNumber(
                account=account,
                tel_number=str(next_number),
                # login = str(next_number), #!!!# login
                # is_deleted = False,
                # activated = True,
            )
            if password:
                number.password = password
            else:
                from common import pwgen
                number.password = pwgen.random_pwd()
            if internal_phone:
                number.internal_phone = internal_phone
            if person_name:
                number.person_name = person_name
            if save:
                number.save()
                number_zakazy = TelNumbersZakazy(
                                                bill_account=account,
                                                date_activation=datetime.datetime.now(),
                                                )
                number_zakazy.save()
                number_zakazy.number.add(number)
                number_zakazy.save()
            return number
        else:
            raise Exception("TelNumber.create(): account is None!")


    def get_external_numbers(self):  # @todo: Переделывать запрос в связи с изменениями в таблице tel_numbers_group_numbers
        '''
        sql = """SELECT * FROM external_numbers a
                 JOIN tel_numbers_group_numbers b
                 ON (b.telnumbersgroup_id=a.phone_numbers_group_id)
                 WHERE b.tel_number=%s"""
        '''
        nums = []
        for group in self.telnumbers_groups.all():
            for num in group.externalnumber_set.all():
                if num not in nums:
                    nums.append(num)
        print nums
        return nums


    class Meta:
        managed = True
        # db_table = 'tel_numbers'
        db_table = "internal_numbers"
        ordering = ("tel_number",)
        verbose_name = _(u"Internal number")
        verbose_name_plural = _(u"Internal numbers")


class TelNumbersGroup(models.Model):
    """
    Таблица для хранения настроек группы номеров
    """

    name = models.CharField(max_length=255, default='', verbose_name=_(u"Group name"))
    type = models.IntegerField(default=PHONE_GROUP_TYPE_TOALL)
    account = models.ForeignKey(BillserviceAccount, verbose_name=_(u"Account"))  # TODO: - check correctness, in database there are no any constraints, this is integer field

    numbers = models.ManyToManyField(TelNumber, verbose_name=_(u"Internal phones"), related_name="telnumbers_groups")

    objects = BillingManager()

    @staticmethod
    def create(name, account, numbers=[]):
        print "numbers_create: %s" % numbers
        obj = TelNumbersGroup(
            name=name,
            account=account
        )
        obj.save()
        for number in numbers:
            print "number_create: %s" % number
            obj.numbers.add(number)
        return obj

    def set_data(self, name, numbers=[]):
        self.name = name
        self.save()
        self.numbers = ""
        for number in numbers:
            self.numbers.add(number)

    @property
    def name_with_numbers(self):
        numbers = self.numbers.all()
        if numbers.count() > 0:
            name = self.name + u" (" + ", ".join([unicode(x) for x in numbers]) + u")"
        else:
            name = self.name
        return name

    @property
    def numbers_str(self):
        return ", ".join([unicode(x) for x in self.numbers.all()])

    @property
    def local_numbers_str(self):
        return ", ".join([num.number for num in self.externalnumber_set.all()])

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        return super(TelNumbersGroup, self).save(*args, **kwargs)

    class Meta:
        db_table = 'tel_numbers_group'
        ordering = ("name",)
        verbose_name = _(u"Group numbers")
        verbose_name_plural = _(u"Groups numbers")
        managed = False

class TelNumbersGroupNumbers(models.Model):
    # tel_number = models.CharField(max_length = 255, default = '')
    telnumbersgroup = models.ForeignKey(TelNumbersGroup)
    telnumber = models.ForeignKey(TelNumber, related_name="telnumber_id")

    objects = BillingManager()

    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        return super(TelNumbersGroupNumbers, self).save(*args, **kwargs)

    class Meta:
        db_table = 'tel_numbers_group_numbers'
        managed = False

'''
def create_group(billservice_account, name, group_type = PHONE_GROUP_TYPE_TOALL):
    group, created = TelNumbersGroup.objects \
                     .get_or_create(account = billservice_account, \
                                    name = name, \
                                    type = group_type)
    return group

def create_tel_numbers_group_numbers(inner_number, group):
    tngn, created = TelNumbersGroupNumbers.objects \
                    .get_or_create(tel_number = inner_number, \
                                   tel_numbers_group = group)
    return tngn
'''


class Status_number(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    status = models.CharField(max_length=75)
    about = models.CharField(max_length=255, null=True, blank=True)
    def __unicode__(self):
        return self.status

    objects = BillingManager()

    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        return super(Status_number, self).save(*args, **kwargs)

    class Meta:
        db_table = "telnumbers_status_number"


class TelNumbersZakazy(models.Model):
    id = models.AutoField(primary_key=True, blank=True)
    number = models.ManyToManyField(TelNumber, verbose_name=_(u"Internal number"))
    bill_account = models.ForeignKey(BillserviceAccount, verbose_name=_(u"Account"))
    date_activation = models.DateTimeField(null=True, blank=True, verbose_name=_(u"Date activation"))
    date_deactivation = models.DateTimeField(null=True, blank=True, verbose_name=_(u"Date deactivation"))
    status_number = models.ForeignKey(Status_number, default=1)

    objects = BillingManager()

    def __unicode__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        return super(TelNumbersZakazy, self).save(*args, **kwargs)

    class Meta:
        managed = True
        db_table = "telnumbers_zakazy"


