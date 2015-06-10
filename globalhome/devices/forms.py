# -*- coding: utf-8 -*-
from django import forms
import datetime
from dateutil.relativedelta import relativedelta  # @UnresolvedImport
from account.models import Profile

class sum_for_check(forms.Form):
    sum = forms.FloatField(label=u"Сумма")
    findoc = forms.ChoiceField(widget=forms.RadioSelect(), label=u"Договор по которому будет выставлен счет")
    
    def clean_sum(self):
        sum_temp = self.cleaned_data["sum"]
        if sum_temp < 500:
            raise forms.ValidationError(u'Минимальная сумма счета 500 рублей')
        return sum_temp
    
    def __init__(self, data=None, choices = []):
        self.data = data
        super(sum_for_check, self).__init__(data = data)
        self.fields["findoc"].choices = choices


def first_day_last_month():
    now = datetime.datetime.now()
    last_month = now - relativedelta(months=1)
    first_day_last_month = datetime.datetime(last_month.year, last_month.month, 1)
    return first_day_last_month
   
class write_off_filter_form(forms.Form):

    date_from = forms.DateField(
        required=False,
        input_formats=('%d.%m.%Y',),
        # widget=JqCalendar(),
        widget=forms.DateInput(attrs={'class':"datepicker", 'readonly':'readonly'},),
        label=u'Дата, с',
        initial=first_day_last_month().strftime("%d.%m.%Y")
    )
    date_to = forms.DateField(
        required=False,
        input_formats=('%d.%m.%Y',),
        # widget=JqCalendar(),
        widget=forms.DateInput(attrs={'class':"datepicker", 'readonly':'readonly'},),
        label=u'Дата, по',
        initial=datetime.datetime.now().strftime("%d.%m.%Y")
    )     
    

class email_for_document(forms.ModelForm):
    email_for_document = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super(email_for_document, self).__init__(*args, **kwargs)
        self.fields['email_for_document'].label = u'e-mail адрес'
        
    class Meta:
        model = Profile
        fields = ['email_for_document']
    