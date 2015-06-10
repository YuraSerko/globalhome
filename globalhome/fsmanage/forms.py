# -*- coding=utf-8 -*-
from django import forms
from account.models import get_all_user_choices, filter_for_admin
from django.utils.translation import ugettext_lazy as _



class AdminOnlineCallsFilter(forms.Form):
    choices = filter_for_admin()
    caller_number = forms.CharField(required=False)
    called_number = forms.CharField(required=False)

    account = forms.ChoiceField(
        required=False,
        choices=choices
    )


    account1 = forms.ChoiceField(
        required=False,
        choices=choices
    )
    called_account = forms.ChoiceField(
        required=False,
        choices=choices
    )

    length_choice = forms.ChoiceField(
        required=False,
        choices=(("0", _(u"All")), ("1", _(u"Zero length")), ("2", _(u"Non-zero length")),)
    )

    check_choice = forms.ChoiceField(
        required=False,
        choices=(("0", _(u"All")), ("1", _(u"Check")), ("2", _(u"Invoice")), ("3", _(u"Act")),)
    )

