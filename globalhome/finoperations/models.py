# coding: utf-8
from django.db import models
from finoperations.consts import OPERATION_TYPES, operation_str_by_int
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from lib.utils import get_now

class BalanceOperation(models.Model):
    operation_type = models.IntegerField(choices = OPERATION_TYPES, verbose_name = _(u"Operation type"))
    user = models.ForeignKey(User, verbose_name = _(u"User"))
    value = models.DecimalField(max_digits = 14, decimal_places = 2, verbose_name = _(u"Value changes"))
    cause = models.CharField(max_length = 255, verbose_name = _(u"Cause"))
    
    date = models.DateTimeField(default = get_now, verbose_name = _(u"Date of operation"))
    
    def __unicode__(self):
        return _(u"%(operation)s %(value)s to user %(user)s") % {
            "operation": operation_str_by_int(self.operation_type),
            "value": self.value,
            "user": self.user,
            "cause": self.cause
        } 
    
    class Meta:
        db_table = "finoperations_balance"
        ordering = ("-date",)
        verbose_name = _(u"Balance operation")
        verbose_name_plural = _(u"Balance operations")
        app_label = "billing"
    



