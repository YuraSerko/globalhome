# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from captcha.fields import CaptchaField



class ContactForm(forms.Form):

    login = forms.CharField(max_length=128, label=_('Enter login Cards'), required = True)
    pin = forms.CharField(widget = forms.PasswordInput, max_length=128, label=_('Enter pin Cards'), required = True)
    captcha = CaptchaField(label=_(u'Enter symbols'), required=True)