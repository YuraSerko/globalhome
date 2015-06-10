# -*- coding:utf-8 -*-
# $Id$
import os


# from pytils.translit import slugify

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


from feedparser import _sanitizeHTML
from stripogram import html2text

from mails import registry

from settings import CHARSET, LANGUAGES

language_choices = [(x, x) for x in LANGUAGES]


class CustomVar(models.Model):
    code = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

class CustomVarValue(models.Model):
    custom_var = models.ForeignKey(CustomVar)
    language_code = models.CharField(max_length=2, choices=language_choices)
    value = models.TextField()

class Letter(models.Model):
    subject = models.CharField(max_length=100, verbose_name=_(u"Subject"))
    texttemplate = models.TextField(verbose_name=_(u"Plain text template"))
    language_code = models.CharField(max_length=2, choices=language_choices, verbose_name=_(u"Language code"))
    code = models.CharField(max_length=100, choices=registry.get_choices(), verbose_name=_(u"Letter class"))

    def __unicode__(self):
        try:
            return u"%s (%s)" % (self.mail_class.verbose_name, self.language_code)
        except:
            return u"%s (%s)" % (u'Не определен класс', self.language_code)

    @property
    def mail_class(self):
        return registry.get_by_code(self.code)

    def save(self, *args, **kwargs):
        if not self.texttemplate:
            self.texttemplate = html2text(_sanitizeHTML(self.htmltemplate, CHARSET))
        super(Letter, self).save(*args, **kwargs)

    def send(self, to=[], _from=settings.DEFAULT_FROM_EMAIL):
        pass

    class Meta:
        verbose_name = _(u"letter")
        verbose_name_plural = _(u"Letters")

class Attachment(models.Model):
    letter = models.ForeignKey(Letter)
    attached = models.FileField(upload_to=settings.ADMINMAIL_ATTACHMENTS_DIR, verbose_name=_(u"File"))
    mime = models.CharField(max_length=50, editable=False, blank=True, null=True, verbose_name=_('Mime'))
    size = models.IntegerField(blank=True, editable=False, null=True, verbose_name=_('Size'))

    def save(self, *args, **kwargs):
        try:  # this will executed for new file only, when self.attached is UploadedFile object
            self.mime = self.attached.file.content_type
            self.size = self.attached.file.size
        except AttributeError:
            pass
        super(Attachment, self).save(*args, **kwargs)


    class Meta:
        verbose_name = _(u"permanent attachment")
        verbose_name_plural = _(u"Permanent attachments")

def get_language_list_status(code):
    """
    Returns tuple of tuples (obj language, bool has_translation)
    @code - mail class code
    """
    letters = list(Letter.objects.select_related().filter(code=code))
    for lng in LANGUAGES:
        try:
            letter = [x for x in letters if x.language_code == lng][0]
        except IndexError:
            letter = None
        yield (lng, letter)

