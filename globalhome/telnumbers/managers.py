# coding: utf-8
from django.db import models
from django.conf import settings
from consts import REGIONS

class FreeExternalNumbersManager(models.Manager):
    def get_query_set(self):
        qs = super(FreeExternalNumbersManager, self).get_query_set().using(settings.BILLING_DB)
        reg_c = []
        for reg in REGIONS:
            reg_c.append(reg[0])
        return qs.filter(phone_numbers_group__isnull = True, region__in = reg_c)

    def using(self, *args, **kwargs):
        return self.get_query_set()


