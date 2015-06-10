# coding: utf-8
from django.db import models
from django.utils.translation import ugettext as _

# Create your models here.

class VariableSet(models.Model):
    """
        Модель для представления набора переменных
    """
    name = models.CharField(max_length = 255, verbose_name = _(u"Name"), unique = True)
    module = models.CharField(max_length = 255, verbose_name = _(u"Python module name"))
    description = models.TextField(verbose_name = _(u"Description"), null = True, blank = True)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ("name",)
        verbose_name = _(u"Variable set")
        verbose_name_plural = _(u"Variable sets")
        db_table = "content_varsets"
        app_label = "content"
