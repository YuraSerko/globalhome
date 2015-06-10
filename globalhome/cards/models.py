# coding: utf-8
import datetime
from django.conf import settings
from django.db import models
from django import template
from django.utils.translation import ugettext_lazy as _
import log
import math
from telnumbers.consts import *
from billing.managers import BillingManager
# from prices.models import PricesGroup
from django.contrib.auth.models import User
# class Author(models.Model):
#    name = models.CharField(max_lenght = 255)
import random, string
from datetime import timedelta
from billing.models import BillserviceAccount, BillserviceSubAccount
import os, sys






class BillserviceCard(models.Model):
    series = models.IntegerField(null=False, blank=False)
    pin = models.CharField(max_length=255, null=True)
    sold = models.DateTimeField(null=True)
    nominal = models.DecimalField(default='0', max_digits=14, decimal_places=2, null=True)
    activated = models.DateTimeField(null=True)
    activated_by_id = models.IntegerField(null=True)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)
    disabled = models.BooleanField(default=False)
    created = models.DateTimeField(null=True)
    template_id = models.IntegerField()  # in version ebs 1.5 not used. need drop
    account_id = models.IntegerField(null=True)
    tarif_id = models.IntegerField()
    nas_id = models.IntegerField(null=True)
    login = models.CharField(max_length=255, default='')
    ip = models.CharField(max_length=20)
    ipinuse_id = models.IntegerField(null=True)
    type = models.IntegerField(null=True)
    ext_id = models.CharField(max_length=255, default='')
    salecard_id = models.IntegerField(null=True)


    class Meta:
        db_table = u'billservice_card'
        managed = True

    objects = BillingManager()

    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        return super(BillserviceCard, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        return super(BillserviceCard, self).delete(*args, **kwargs)

    @staticmethod
    def generate_card(sum, series, sell=True):
        try:
            long = random.randint(4, 8)
            chars = filter(lambda x : x not in ('l', 'L', 'i', 'I', '0', 'O', 'o', 'j', 'J'), string.letters + string.digits)
            pin = ''.join(random.sample(chars, long))
            now = datetime.datetime.now()
            end_date = now + datetime.timedelta(days=1000)
            login = BillserviceCard.rndm(series)
            card = BillserviceCard(series=series , login=login, pin=pin, nominal=sum, tarif_id=21, type=1, start_date=now,
                                    end_date=end_date, created=now, template_id=9, ip='')
            if sell:
                card.sell()
            card.save()
            return card
        except Exception, e:
            print "Exception in generate_card: '%s'" % e
            exc_type, exc_obj, exc_tb = sys.exc_info()  # @UnusedVariable
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print "Exception in generate_card: file:%s line:%s" % (fname, exc_tb.tb_lineno)
            raise Exception(e)

    @staticmethod
    def rndm(series):
        try:
            long = random.randint(4, 8)
            chars = filter(lambda x : x not in ('l', 'L', 'i', 'I', '0', 'O', 'o', 'j', 'J'), string.letters + string.digits)
            login = series + ''.join(random.sample(chars, long))
            try:
                truth = BillserviceAccount.objects.get(username=login)
                return BillserviceCard.rndm(series)
            except BillserviceAccount.DoesNotExist:
                try:
                    truth = BillserviceSubAccount.objects.get(username=login)
                    return BillserviceCard.rndm(series)
                except BillserviceSubAccount.DoesNotExist:
                    try:
                        truth = BillserviceCard.objects.get(login=login)
                        return BillserviceCard.rndm(series)
                    except BillserviceCard.DoesNotExist:
                        return login
        except Exception, e:
            print "Exception in rndm: '%s'" % e
            exc_type, exc_obj, exc_tb = sys.exc_info()  # @UnusedVariable
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print "Exception in rndm: file:%s line:%s" % (fname, exc_tb.tb_lineno)
            raise Exception(e)

    def sell(self):
        sale = BillserviceSaleCard(sum_for_pay=self.nominal, created=datetime.datetime.now())
        sale.save()
        self.salecard_id = sale.id
        self.save()

class BillserviceSaleCard(models.Model):
    dealer_id = models.IntegerField(default='1')
    sum_for_pay = models.IntegerField(null=False)
    paydeffer = models.IntegerField(default='0')
    discount = models.IntegerField(default='0')
    discount_sum = models.IntegerField(default='0')
    prepayment = models.IntegerField(default='0')
    created = models.DateTimeField(null=False)

    class Meta:
        db_table = u'billservice_salecard'
        managed = True

    def save(self, *args, **kwargs):
        kwargs['using'] = settings.BILLING_DB
        return super(BillserviceSaleCard, self).save(*args, **kwargs)



class Card_identification(models.Model):
    card_id = models.ForeignKey(BillserviceCard, null=True, blank=True)
    user_id = models.ForeignKey(BillserviceAccount, null=True, blank=True)
    class Meta:
        db_table = u'card_identification'


