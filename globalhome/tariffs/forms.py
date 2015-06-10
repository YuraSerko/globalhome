# coding: utf-8
from django import forms
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _
from models import TariffGroup, TelZoneGroup
# from billing.models import BillserviceAccount
from django.conf import settings
from django.db import transaction

class UploadTariffsForm(forms.Form):
    """
        Форма для загрузки CSV-файла с тарифами
    """

    def get_billing_groups():
        grps = TariffGroup.objects.all()
        choices = []
        for grp in grps:
            choices += [(grp.id, grp.group_name)]
        transaction.commit_unless_managed(using=settings.BILLING_DB)
        return choices

    billing_group = forms.ChoiceField(
        choices=get_billing_groups(),
        label=_(u"Upload to Tariff group")
    )

    file = forms.FileField(
        label=_(u"CSV file"),
        widget=widgets.FileInput(
            attrs={"style" : "width: 50%;" }
        )
    )

    replace_existing_tariffs = forms.ChoiceField(
        choices=(("True", "True"), ("False", "False")),
        label=_(u"Replace existing tariffs"),
        initial="True",
        widget=forms.CheckboxInput(),
        required=False
    )

    ignore_missing_zones = forms.ChoiceField(
        choices=(("True", "True"), ("False", "False")),
        label=_(u"Ignore missing telzones"),
        # initial = "on",
        widget=forms.CheckboxInput(),
        required=False
    )

    add_mobile_codes = forms.ChoiceField(
        choices=(("True", "True"), ("False", "False")),
        label=_(u"Add missing mobile codes"),
        # initial = "on",
        widget=forms.CheckboxInput(),
        required=False
    )



class UploadTariffsForm1(forms.Form):
    pass
    """
        Форма рассылки
    """
    """
        Получаем email адреса
    """








class ChangeTelzoneGroupForm(forms.Form):
    def get_telzone_groups():

        grps = TelZoneGroup.objects.all()
        choices = []
        for grp in grps:
            choices += [(grp.id, grp.name)]
        transaction.commit_unless_managed(using=settings.BILLING_DB)
        return choices

    telzone_group = forms.ChoiceField(
        choices=get_telzone_groups(),
        label=_(u"Select telzone group")
    )




