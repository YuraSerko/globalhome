# coding: utf-8
from django.db import models
from django.contrib import admin
from django import forms
import datetime
import os
from django.utils.translation import ugettext_lazy as _
from content.models import BaseContent
from prices.models import Price
from findocs.models import FinDoc
from django import forms
from data_centr.models import Tariff
# class Author(models.Model):
#    name = models.CharField(max_lenght = 255)

class Devices(BaseContent):
    # name = models.CharField(max_length = 255, verbose_name='Name')
    url = models.CharField(max_length=255)
    # time = models.DateTimeField(default = datetime.datetime.now)
    img = models.ImageField(upload_to='./uploads/images')
    initial_fee = models.CharField(max_length=255, null=True, blank=True)
    abonent_fee = models.CharField(max_length=255, null=True, blank=True)
    tariff = models.ForeignKey(Tariff)

#    onetime_document = models.ForeignKey(FinDoc, verbose_name = _(u"One-time document"), blank = True, null = True, related_name = "+",
#        help_text = _(u"This document user will sign only one time"))
#    reusable_document = models.ForeignKey(FinDoc, verbose_name = _(u"Reusable document"), blank = True, null = True, related_name = "+",
#        help_text = _(u"This document user will sign every time"))
#    cancel_document = models.ForeignKey(FinDoc, verbose_name = _(u"Cancel document"), blank = True, null = True, related_name = "+",
#        help_text = _(u"This document user will sign when canceling service"))
#    findoc_for_billing = models.CharField(max_length=255)

class ApplicationService(BaseContent):
    service = models.IntegerField(null=False)
    user = models.IntegerField(null=False)
    fin_doc_id = models.CharField(max_length=255)


class UserService(BaseContent):
    service = models.IntegerField(null=False)
    user = models.IntegerField(null=False)
    cost = models.CharField(max_length=255)
    abonent_fee = models.CharField(max_length=255)

