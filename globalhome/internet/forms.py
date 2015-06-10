# coding: utf-8
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms.forms import BaseForm
from django.forms import ModelForm
from internet.models import Connection_address, Connection_address_map, ConectionInputHomeAdmin, ScheduleConnectionInternet
from models import Internet_street, Internet_house, Internet_city
from internet import models
from  yandex_maps import api
from django.conf import settings
from django.db.models import Max
from lib.mail import send_email
from django.contrib.auth.models import User
class VpnAuthForm(forms.Form):
    login = forms.CharField(
        max_length=64,
        required=True,
        widget=forms.TextInput(),
        label=_(u'Введите логин для авторизации по впн'),
        )

    password = forms.CharField(
        max_length=64,
        required=True,
        widget=forms.PasswordInput(),
        label=_(u'Введите пароль'),
        )

    password_check = forms.CharField(
        max_length=64,
        required=True,
        widget=forms.PasswordInput(),
        label=_(u'Повторите пароль'),
        )


class VpnFormEdit(VpnAuthForm):
    login = forms.CharField(
        max_length=64,
        required=False,
        widget=forms.TextInput(attrs={'readonly':'readonly'}),
        label=(u'Ваш логин'),
        )

    password = forms.CharField(
        max_length=64,
        required=True,
        widget=forms.PasswordInput(),
        label=_(u'Введите новый пароль'),
        )

class Internet_street_form(ModelForm):
    class Meta:
        model = Internet_street
        fields = ('street',)

class Connection_address_Admin_Form(forms.ModelForm):

    street_types = forms.ChoiceField(required=False,
        choices=models.STREET_TYPE_CHOICES, initial='улица', label=u'Тип улицы',
    )
    street1 = forms.CharField(max_length=250, label=u'Улица и номер дома', help_text=u'Например, Новый Арбат 1-3с6   или    Щербаковская 53к2', widget=forms.TextInput(attrs={'size':'45'}))
    district_administration = forms.CharField(max_length=250, required=False, label=u'Администрация района', widget=forms.TextInput(attrs={'size':'95', 'readonly':'readonly'}))
    prefectura = forms.CharField(max_length=250, label=u'Префктура', required=False, widget=forms.TextInput(attrs={'size':'95', 'readonly':'readonly'}))
    
    class Meta:
        model = Connection_address
        fields = ('persons', 'city', 'street_types', 'street1', 'floors', 'entrances', 'notes',
                  'readiness_degree0', 'readiness_degree1', 'readiness_degree2', 'readiness_degree3',
                  'readiness_degree4', 'readiness_degree5', 'readiness_degree6', 'readiness_degree7', 'home_administration')
        widgets = {
        'persons': forms.SelectMultiple(attrs={'style':"height:75px;"}),
        }


    def __init__(self, *args, **kwargs):
        super(Connection_address_Admin_Form, self).__init__(*args, **kwargs)

        if self.instance.id:
            self.fields['street1'].initial = (self.instance.street.street) + " " + (self.instance.house.house)
            self.fields['street_types'].initial = self.instance.street.street_type
            try:
                self.fields['prefectura'].initial = self.instance.home_administration.all()[0].district_administration.prefecturs.name
                self.fields['district_administration'].initial = self.instance.home_administration.all()[0].district_administration.name
            except:
                pass


    def save(self, commit=True, *args, **kwargs):
        t = super(Connection_address_Admin_Form, self).save(commit=False, *args, **kwargs)
        # find house\street
        
        street1 = self.cleaned_data["street1"]
        street_type1 = self.cleaned_data["street_types"]
        separator = street1.rfind(" ")
        # street
        strstreet = street1[:separator]
        try:
            objstreet = Internet_street.objects.get(street=strstreet, street_type=street_type1)
        except Internet_street.DoesNotExist:
            objstreet = Internet_street(street_type=street_type1.encode("utf-8"), street=strstreet)
            objstreet.save()
        t.street_id = objstreet.id
        # end of street
        # house
        strhouse = street1[separator + 1:]
        try:
            objhouse = Internet_house.objects.get(house=strhouse)
        except Internet_house.DoesNotExist:
            objhouse = Internet_house(house=strhouse)
            objhouse.save()
        t.house_id = objhouse.id
        # end of house
        # add coordinates
        try: 
            t.x = self.coordinates[0]
            t.y = self.coordinates[1]
        except: 
            pass
        # end adding coordinates
        if commit:
            t.save()
        return t


    def clean(self, *args, **kwargs):
        cleaned_data = super(Connection_address_Admin_Form, self).clean(*args, **kwargs)
        street1 = self.cleaned_data["street1"]
        street_type1 = self.cleaned_data["street_types"]
        city = self.cleaned_data["city"]
        # check for existing address
        separator = street1.rfind(" ")
            # street
        strstreet = street1[:separator]
            # house
        strhouse = street1[separator + 1:]
        idexist = self.instance.id
        addressexist = Connection_address.objects.filter(city__city=city, street__street=strstreet, street__street_type=street_type1, house__house=strhouse)
        if (addressexist and not(idexist)):
            raise forms.ValidationError("Такой адрес уже есть")
        # end of checking existing address
                # api yandex key
        api_key = settings.YANDEX_MAPS_API_KEY
        st = street1.encode('utf-8')
        st1 = street_type1.encode('utf-8')
        address = str(city) + " " + str(st1) + " " + str(st)
        # geocoding yandex
        pos = api.geocode(api_key, address)
        if ((pos[0] != None) and (pos[1] != None)):  # если геокодирование вернуло результаты
            self.coordinates = [pos[0], pos[1]]
            if (str(city) != 'Москва') and (str(city) != 'Санкт-Петербург'):
                    self.coordinates = [None, None]
            elif not (((37.17 < float(pos[0]) < 37.86) and (55.54 < float(pos[1]) < 55.93) and (str(city) == 'Москва')) or ((29.75 < float(pos[0]) < 30.55) and (59.78 < float(pos[1]) < 60.11) and (str(city) == 'Санкт-Петербург'))):
                raise forms.ValidationError("Проверьте название улицы и номер дома")
                
        return cleaned_data

class Connection_address_map_Admin_Form(Connection_address_Admin_Form):
    pass
    class Meta:
        model = Connection_address
        fields = ('persons', 'city', 'street_types', 'street1', 'floors', 'entrances', 'notes',
                  'readiness_degree0', 'readiness_degree1', 'readiness_degree2', 'readiness_degree3',
                  'readiness_degree4', 'readiness_degree5', 'readiness_degree6', 'readiness_degree7', 'home_administration')
        widgets = {
        'persons': forms.SelectMultiple(attrs={'style':"height:75px;"}),
        'notes':forms.Textarea,
        }


class Form_insert_home_administration(forms.ModelForm):
    street_types = forms.ChoiceField(required=False, choices=models.STREET_TYPE_CHOICES, label=u'Тип улицы',)
    street1 = forms.CharField(max_length=250, label=u'Улица ', help_text=u'Например, Новый Арбат или Щербаковская ', widget=forms.TextInput(attrs={'size':'45'}))
    home_numbers = forms.CharField(label=u'Названия домов', help_text=u'Введите номера домов через запятую', widget=forms.Textarea())
    class Media:
        
        css = { 'all': (settings.MEDIA_URL + 'css/style_for_admin_form.css' ,
                        ) }
#         js = (settings.MEDIA_URL + 'js/script_reg_users_check.js',)

    class Meta:
        model = ConectionInputHomeAdmin
        fields = ('city', 'street_types', 'street1', 'home_administration', 'readiness_degree',)
        widgets = { 
        'home_administration': forms.CheckboxSelectMultiple(attrs={'style':"list-style : none; " })
        } 
                                             
    def __init__(self, *args, **kwargs):
        super(Form_insert_home_administration, self).__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['street1'].initial = self.instance.street.street 
            self.fields['street_types'].initial = self.instance.street.street_type
            self.fields['home_numbers'].initial = self.instance.house.house
            
            
        
    def save(self, commit=True, *args, **kwargs):
        t = super(Form_insert_home_administration, self).save(commit=False, *args, **kwargs)
        # find house\street
        
        i = 0
        for home in self.homes:
            if home != "":
                if t.id:
                    if i == 0:
                            pass                       
                    else:
                        t.id = t.id + 1
                else:
                        max_id = Connection_address.objects.all().aggregate(Max('id'))
                        t.id = (max_id['id__max']) + 1
            # street        
                try:
                    objstreet = Internet_street.objects.get(street__icontains=self.cleaned_data["street1"].encode("utf-8"), street_type=self.cleaned_data["street_types"].encode("utf-8"))
                except Internet_street.DoesNotExist:
                    objstreet = Internet_street(street_type=self.cleaned_data["street_types"].encode("utf-8"), street=self.cleaned_data["street1"])
                    objstreet.save() 
                t.street_id = objstreet.id
            # end of street
            # house
                try:
                    objhouse = Internet_house.objects.get(house=home)
                except Internet_house.DoesNotExist:
                    objhouse = Internet_house(house=home)
                    objhouse.save()
                t.house_id = objhouse.id
            # end of house
            # add coordinates
                j = 0
                t.x = self.coordinates[i][j]
                j += 1
                t.y = self.coordinates[i][j]
                i += 1
            # end adding coordinates
                t.save()  
                for admf in self.cleaned_data["home_administration"]:   
                    t.home_administration.add(admf.id)
        return t  
        

        
        
    def clean(self, *args, **kwargs):
        cleaned_data = super(Form_insert_home_administration, self).clean(*args, **kwargs)
        form = super(Form_insert_home_administration, self)
        if form.is_valid():
            
            # api yandex key
            api_key = settings.YANDEX_MAPS_API_KEY
            splited_home = self.cleaned_data["home_numbers"].split(',')
            coordinates, homes = [], []
            for home in splited_home:
                if home != "":
                    try: 
                        check_adress = ConectionInputHomeAdmin.objects.get(street__street__icontains=self.cleaned_data["street1"].encode("utf-8"), house__house=home)
                    except:
                        homes.append(home)
            
            if  homes == []:
                raise forms.ValidationError("ВСЕ введённые дома уже есть в базе ")
            else:           
                self.homes = homes            
                for home in homes:            
                    address = str(self.cleaned_data["city"]) + " " + str(self.cleaned_data["street_types"].encode('utf-8')) + " " + str(self.cleaned_data["street1"].encode('utf-8')) + " " + str(home.encode('utf-8'))            
                    # geocoding yandex
                    pos = api.geocode(api_key, address)
                    if pos[0] == None and pos[1] == None:
                        raise forms.ValidationError("Неудаётся получить координаты-нет ответа от YANDEX")                   
                    if (str(self.cleaned_data["city"]) != 'Москва') and (str(self.cleaned_data["city"]) != 'Санкт-Петербург'):
                        self.coordinates = [None, None]
                    elif not (((37.17 < float(pos[0]) < 37.86) and (55.54 < float(pos[1]) < 55.93) and (str(self.cleaned_data["city"]) == 'Москва')) or ((29.75 < float(pos[0]) < 30.55) and (59.78 < float(pos[1]) < 60.11) and (str(self.cleaned_data["city"]) == 'Санкт-Петербург'))):
                        raise forms.ValidationError("Проверьте название улицы и номер дома")                      
                    coordinates.append([pos[0], pos[1]])
                self.coordinates = coordinates
        return cleaned_data
    
class FormScheduleConnectionInternrt(forms.ModelForm):

    porch = forms.CharField(max_length=250, label=u'Подъезд', help_text=u'Например 1', widget=forms.TextInput(attrs={'size':'45', }))
    flat = forms.CharField(max_length=250, label=u'Квартира', help_text=u'Например 21', widget=forms.TextInput(attrs={'size':'45'})) 
    date = forms.CharField(max_length=250, label=u'Дата', widget=forms.TextInput(attrs={'size':'45', 'readonly':"readonly" }))
    time = forms.CharField(max_length=250, label=u'Время', widget=forms.TextInput(attrs={'size':'45', 'readonly':"readonly"}))
    contact_face = forms.CharField(max_length=250, label=u'Контактное лицо', help_text=u'Например Антон', widget=forms.TextInput(attrs={'size':'45'}))
    tel_namber = forms.CharField(max_length=250, label=u'Номер телефона', help_text=u'Например, +7 495 777 777 777 ', widget=forms.TextInput(attrs={'size':'45'}))
#     table_id = forms.CharField(max_length=250, widget=forms.TextInput(attrs={'size':'45', 'readonly':"readonly"})  )
    
     
     
    class Meta:
        model = ScheduleConnectionInternet
        fields = ('adress', 'porch', 'flat', 'contact_face', 'tel_namber', 'date', 'time', 'add_info', 'running_state',)
        
        
    def __init__(self, *args, **kwargs):
        super(FormScheduleConnectionInternrt, self).__init__(*args, **kwargs)
#         if self.instance.id:   
        conn_all = Connection_address.objects.select_related().all().order_by('street__street', 'street__street_type', 'house__house')
        conn_list = []
        conn_list.append((' ', '---------'))
        for conn in conn_all:
            conn_list.append((conn.id, conn.street.street + u' ' + conn.street.street_type + u' ' + conn.house.house))
        self.fields['adress'].choices = conn_list
            
            
    def save(self, commit=False, *args, **kwargs):
        t = super(FormScheduleConnectionInternrt, self).save(commit=False, *args, **kwargs)
        distr = self.instance.adress.home_administration.all()[0].district_administration.id
        t.district = distr
        # print self.cleaned_data["adress"].__unicode__()
        message = u''' 
                       Адрес: %(adress)s
                     Подъезд: %(porch)s
                    Квартира: %(flat)s
             Контактное лицо: %(contact_face)s
              Номер телефона: %(tel_namber)s
                        Дата: %(date)s
                       время: %(time)s
   Дополнительная информация: %(add_info)s
        Состояние выполнения: %(running_state)s
                '''
        message = message % { 'adress' : self.cleaned_data["adress"].__unicode__(),
                             'porch' : self.cleaned_data["porch"],
                             'flat' : self.cleaned_data["porch"],
                             'contact_face' : self.cleaned_data["contact_face"],
                             'tel_namber' : self.cleaned_data["tel_namber"],
                             'date' :  self.cleaned_data["date"],
                             'time' : self.cleaned_data["time"],
                             'add_info' : self.cleaned_data["add_info"],
                             'running_state' : self.cleaned_data["running_state"]
                                                         }
        all = User.objects.filter(groups__id=2)
        email_list = []
        for user in all:
            email_list.append(user.email)
        send_email(u'Заявка на подключение INTERNET', message, u'Globalhome.su', email_list)
        return t  
        

    
    
    
            
