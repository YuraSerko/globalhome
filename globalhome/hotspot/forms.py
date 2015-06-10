# coding: utf-8
from django import forms
from account.forms import first_date_last, first_date_new, first_date_new2, first_date_last2
from hotspot import models
from hotspot.models import Prefecturs, DistrictAdministration, HomeAdministration
from django.conf import settings
from yandex_maps import api

class DepositsHotSpot(forms.Form):
    login = forms.CharField(
        required=True,
        label=u'Логин',
        # help_text=_(u"(без скобок, пробелов и разделителей. Пример abc123")
        )
    pin = forms.CharField(
        required=True,
        label=u'Пин'
       )

class DateFilterForm(forms.Form):

    date_from = forms.DateField(
        required=False,
        input_formats=('%d.%m.%Y',),
        # widget=JqCalendar(),
        widget=forms.DateInput(attrs={'class':"datepicker", 'readonly':'readonly'},),
        label=u'Дата, с',
        initial=first_date_new2().strftime("%d.%m.%Y")  # '01.05.2014' 
    )
    date_to = forms.DateField(
        required=False,
        input_formats=('%d.%m.%Y',),
        # widget=JqCalendar(),
        widget=forms.DateInput(attrs={'class':"datepicker", 'readonly':'readonly'},),
        label=u'Дата, по',
        initial=first_date_last2().strftime("%d.%m.%Y")
    )
    
class PrefectursAdminForm(forms.ModelForm):   
    adress1 = forms.CharField(max_length=250, required=True, label=u'Адрес', help_text=u'Например, Новый Арбат 1-3с6   или    Щербаковская 53к2', widget=forms.TextInput(attrs={'size':'40'}))

    class Meta:
        model = Prefecturs
        fields = ('name', 'adress1', 'tel_numbers', 'fax', 'subway_station', 'web_site', 'email', 'add_information',)

    def __init__(self, *args, **kwargs):
        super(PrefectursAdminForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['adress1'].initial = (self.instance.adress)
        

    def save(self, commit=True, *args, **kwargs):
        t = super(PrefectursAdminForm, self).save(commit=False, *args, **kwargs)
        # find house\street
        
        adress1 = self.cleaned_data["adress1"]
       
        # add coordinates
        t.adress = adress1
        t.x = self.coordinates[1]
        t.y = self.coordinates[0]

        # end adding coordinates
        if commit:
            t.save()
        return t


    def clean(self, *args, **kwargs):
        cleaned_data = super(PrefectursAdminForm, self).clean(*args, **kwargs)
        form = super(PrefectursAdminForm, self)
        if form.is_valid():
            print "valid"
            adress1 = self.cleaned_data["adress1"]
        # api yandex key
            api_key = settings.YANDEX_MAPS_API_KEY
            
            # geocoding yandex
            pos = api.geocode(api_key, adress1.encode('utf-8'))
            print "x %s" % pos[0]
            print "y %s" % pos[1] 
            if pos:
                self.coordinates = [pos[0], pos[1]]
                prefectures_coordinates = Prefecturs.objects.filter(x=pos[1], y=pos[0])
#                 if prefectures_coordinates:
#                     raise forms.ValidationError("Проверьте адрес, такие геокоординаты уже есть")
                if not ((37.17 < float(pos[0]) < 37.86) and (55.54 < float(pos[1]) < 55.93)  or ((29.75 < float(pos[0]) < 30.55) and (59.78 < float(pos[1]) < 60.11))):
                    raise forms.ValidationError("Проверьте адрес")
            else:
                raise forms.ValidationError("не удалось получить геопараметры")
       
            
        return cleaned_data

class DistrictAdministrationAdminForm(forms.ModelForm):   
    adress1 = forms.CharField(max_length=250, required=True, label=u'Адрес', help_text=u'Например, Новый Арбат 1-3с6   или    Щербаковская 53к2', widget=forms.TextInput(attrs={'size':'45'}))

    class Meta:
        model = DistrictAdministration
        fields = ('name', 'adress1', 'tel_numbers', 'fax', 'subway_station', 'web_site', 'email', 'add_information', 'prefecturs',)

    def __init__(self, *args, **kwargs):
        super(DistrictAdministrationAdminForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['adress1'].initial = (self.instance.adress)

    def save(self, commit=True, *args, **kwargs):
        t = super(DistrictAdministrationAdminForm, self).save(commit=False, *args, **kwargs)
        # find house\street
        
        t.adress = self.cleaned_data["adress1"]
        t.x = self.coordinates[1]
        t.y = self.coordinates[0]
        # end adding coordinates
        if commit:
            t.save()
        return t

    def clean(self, *args, **kwargs):
        cleaned_data = super(DistrictAdministrationAdminForm, self).clean(*args, **kwargs)
        form = super(DistrictAdministrationAdminForm, self)
        if form.is_valid():
            adress1 = self.cleaned_data["adress1"]
            
            # api yandex key
            api_key = settings.YANDEX_MAPS_API_KEY
            
            # geocoding yandex
            pos = api.geocode(api_key, adress1.encode('utf-8'))
            print "x %s" % pos[0]
            print "y %s" % pos[1] 
            if pos:
                self.coordinates = [pos[0], pos[1]]
                prefectures_coordinates = DistrictAdministration.objects.filter(x=pos[1], y=pos[0])
                if prefectures_coordinates:
                    raise forms.ValidationError("Проверьте адрес, такие геокоординаты уже есть")
                if not ((36.0 < float(pos[0]) < 40.00) and (55.34 < float(pos[1]) < 56.20)  or ((29.75 < float(pos[0]) < 30.55) and (59.78 < float(pos[1]) < 60.11))):
                    raise forms.ValidationError("Проверьте адрес")
            else:
                raise forms.ValidationError("не удалось получить геопараметры")
        return cleaned_data


class HomeAdministrationAdminForm(forms.ModelForm):   
    adress1 = forms.CharField(max_length=250, required=True, label=u'Адрес', help_text=u'Например, Новый Арбат 1-3с6   или    Щербаковская 53к2', widget=forms.TextInput(attrs={'size':'45'}))

    class Meta:
        model = HomeAdministration
        fields = ('name', 'adress1', 'tel_numbers', 'fax', 'subway_station', 'web_site', 'email', 'add_information', 'district_administration',)

    def __init__(self, *args, **kwargs):
        super(HomeAdministrationAdminForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['adress1'].initial = (self.instance.adress)
    def save(self, commit=True, *args, **kwargs):
        t = super(HomeAdministrationAdminForm, self).save(commit=False, *args, **kwargs)
        # find house\street
        
        t.adress = self.cleaned_data["adress1"]
        t.x = self.coordinates[1]
        t.y = self.coordinates[0]
        # end adding coordinates
        if commit:
            t.save()
        return t

    def clean(self, *args, **kwargs):
        cleaned_data = super(HomeAdministrationAdminForm, self).clean(*args, **kwargs)
        form = super(HomeAdministrationAdminForm, self)
        if form.is_valid():
            adress1 = self.cleaned_data["adress1"]
            
            # api yandex key
            api_key = settings.YANDEX_MAPS_API_KEY
            
            # geocoding yandex
            pos = api.geocode(api_key, adress1.encode('utf-8'))            
            print "x %s" % pos[0]
            print "y %s" % pos[1] 
            if pos:
                self.coordinates = [pos[0], pos[1]]
                prefectures_coordinates = HomeAdministration.objects.filter(x=pos[1], y=pos[0])
#                 if prefectures_coordinates:
#                     raise forms.ValidationError("Проверьте адрес, такие геокоординаты уже есть")
                if not ((36.0 < float(pos[0]) < 40.00) and (55.34 < float(pos[1]) < 56.20)  or ((29.75 < float(pos[0]) < 30.55) and (59.78 < float(pos[1]) < 60.11))):
                    raise forms.ValidationError("Проверьте адрес")
            else:
                raise forms.ValidationError("не удалось получить геопараметры")
        return cleaned_data

class HotSpotReviewForm(forms.Form):
    contact_face = forms.CharField(max_length=512, required=False, label=u'Контактное лицо')
    adres = forms.CharField(max_length=512, required=False, label=u'Адрес')
    mail = forms.EmailField(label=u'Электронная почта', required=False)
    telnumber = forms.CharField(max_length=15, label=u'Номер мобильного', required=False)
    text = forms.CharField(label=u'Отзыв или предложение', widget=forms.Textarea())
    
class HotSpotComplaintForm(HotSpotReviewForm):
    contact_face = forms.CharField(max_length=512, label=u'Контактное лицо')
    adres = forms.CharField(max_length=512, label=u'Адрес')
    mail = forms.EmailField(label=u'Электронная почта', required=False)
    telnumber = forms.CharField(max_length=15, label=u'Номер мобильного')
    text = forms.CharField(label=u'Отзыв или предложение', widget=forms.Textarea())
    
    
    
