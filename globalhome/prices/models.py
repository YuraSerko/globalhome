# coding: utf-8
from django.db import models
from billing.managers import BillingManager
import settings
from django.utils.translation import ugettext_lazy as _

class PricesGroup(models.Model):
    name = models.CharField(max_length = 255, verbose_name = _("Prices group name"))
    description = models.TextField(blank = True, null = True, verbose_name = _(u"Description"))
    slug = models.SlugField(unique = True, verbose_name = _("Slug for variablesets"))
    
    #objects = BillingManager()
    
    #def save(self, *args, **kwargs):
    #    kwargs["using"] = settings.BILLING_DB
    #    return super(PricesGroup, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return self.name
    
    def delete(self, *args, **kwargs):
        if self.id != 1:
            super(PricesGroup, self).delete(*args, **kwargs)
        #@todo: тут еше надо перекинуть всех пользователей этой группы в группу по умолчанию
    
    class Meta:
        db_table = "prices_groups"
        verbose_name = _(u"Prices group")
        verbose_name_plural = _(u"Prices groups")
        ordering = ("name",)
        app_label = "billing"
    

class Price(models.Model):
    group = models.ForeignKey(PricesGroup, verbose_name = "Prices group")
    name = models.CharField(max_length = 255, verbose_name = _("Price name"))
    value = models.DecimalField(max_digits = 10, decimal_places = 2, verbose_name = _(u"Price value"))
    description = models.TextField(blank = True, null = True, verbose_name = _(u"Description"))
    slug = models.SlugField(verbose_name = _("Slug for variablesets"))
    
    #objects = BillingManager()
    
    #def save(self, *args, **kwargs):
    #    kwargs["using"] = settings.BILLING_DB
    #    return super(Price, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return self.name + u" (" + unicode(self.group) + u")"

    class Meta:
        db_table = "prices_values"
        verbose_name = _(u"Price")
        verbose_name_plural = _(u"Prices")
        ordering = ("name",)
        app_label = "billing"

