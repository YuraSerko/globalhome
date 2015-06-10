# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from captcha.fields import CaptchaField



class CheckForm(forms.Form):

    email = forms.EmailField(max_length=128, label=_('Enter email'), required = True)
#    pin = forms.CharField(widget = forms.PasswordInput, max_length=128, label=_('Enter pin Cards'), required = True)
#    captcha = CaptchaField(label=_(u'Enter symbols'), required=True)

class SearchHostelForm(forms.Form):
    
    number = forms.IntegerField(required = False)
    hostel_number = forms.CharField(required = False)
    floor = forms.IntegerField(required = False)
    room = forms.IntegerField(required = False)
    length_choice = forms.ChoiceField(
        required = False,
        choices = (("0", _(u"All")), ("1", _(u"Active")), ("2", _(u"Unavailable")),)
    )
    university_name = forms.ChoiceField(
        required = False,
        choices = (("0", _(u"All")), ("1", _(u"RGGRU")),)
    )