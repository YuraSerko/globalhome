# -*-coding=utf-8-*-
from django import forms
from models import Mikrotik, MACaddress
from django.core.exceptions import ValidationError
from django.forms.fields import Field, FileField
from netaddr import IPNetwork
from django.utils.translation import ugettext_lazy as _
from netaddr import IPAddress
from internet.models import Connection_address

EMPTY_VALUES = (None, '', [], (), {})
class ModelChoiceField(forms.ModelChoiceField):

     def to_python(self, value):
         if value in EMPTY_VALUES:
             return None
         return value

class MikrotikForm(forms.ModelForm):
    ip_address = forms.CharField(required=True, label=u'IP адрес')
    used_ipsubnet = forms.CharField(required=True, label=u'Используемая IP подсеть')
    address = ModelChoiceField(queryset=Connection_address.objects.select_related().order_by('street__street_type', 'street__street', 'house__house'), label=u'Адрес')
    class Meta:
        model = Mikrotik
        fields = ['id', 'name_of_mikrotik', 'type_of_settings', 'ip_address', 'used_ipsubnet', 'MAC_addresses', 'parent', 'count_of_second_mikrotiks', 'address', 'corpse', \
                  'porch', 'floor', 'flat', 'additionalAdress', 'mikrotik_model', 'installer_name', 'date_installation', 'last_day_of_test', 'is_installed', 'notation', ]
        widgets = {
            'notation': forms.Textarea(attrs={'cols':65, 'rows':2, 'style':"resize:Vertical;"}),
        }
    def __init__(self, *args, **kwargs):
        super(MikrotikForm, self).__init__(*args, **kwargs)
        if (kwargs.has_key('initial')):
            try:
                parent = self.Meta.model.objects.get(id=int(kwargs['initial']['_parent']))
                self.fields['type_of_settings'].initial = 'secondary'
                self.fields['parent'].initial = parent.id
                self.fields['address'].initial = parent.address
            except Exception as e:
                print e
        self.fields['MAC_addresses'].initial = 'D4:CA:6D:'
        self.fields['porch'].required = False 
        self.fields['floor'].required = False
#         self.fields['parent'].queryset = self.Meta.model.objects.all().filter(type_of_settings='primary').order_by('name_of_mikrotik', 'ip_address')
    
 

    def _clean_fields(self):
        type_of_settings = ''
        for name, field in self.fields.items():
            value = field.widget.value_from_datadict(self.data, self.files, self.add_prefix(name))
            try:
                if name == 'ip_address':
                    if not(type_of_settings != 'primary' and not(value)):
                        lst = []
                        for i in Mikrotik.objects.all().values('ip_address'):
                            lst.append(i['ip_address'])
                        if value and name in super(MikrotikForm, self).changed_data and value in lst:
                            raise ValidationError(_(u"Введёный IP адрес уже существует"))
                        try:
                            IPAddress(value)
                        except Exception as e:
                            raise ValidationError(str(e))
                if (name == 'MAC_addresses') and value:
                    value = str(value).upper()
                    self.macaddrs = []
                    try:
                        mac_split = value.split('-')
                        mac_end = mac_split[1]
                        pref_mac = mac_split[0][:-len(mac_end)]
                        mac_start = mac_split[0][len(pref_mac):]
                        for m in xrange(int(mac_start.replace(":", ""), 16), int(mac_end.replace(":", ""), 16) + 1):
                            r = hex(m)[2:].upper().zfill(2)
                            res = []
                            for i in range (0, len(r) / 2):
                                res.append(r[i * 2:i * 2 + 2])
                            self.macaddrs.append(pref_mac + ':'.join(res))
                    except:
                        raise ValidationError("Range of mac_addresses is invalid. Please check it.")
                    if(len(self.macaddrs) != 6):
                        raise ValidationError(_(u"Длина диапазона MAC адресов должна быть равной 6. Текущая длина = %s" % len(self.macaddrs)))
                    mac_search = MACaddress.objects.all().filter(MAC_address__in=self.macaddrs).exclude(mikrotik_id=id) if id else MACaddress.objects.all().filter(MAC_address__in=self.macaddrs)
                    if mac_search:
                        raise ValidationError(_(u"Введёный диапазон пересекается с уже существующими MAC адресами"))
                    
                if name == 'floor' or name == 'porch':
                    if type_of_settings != 'primary' and not(value):
                        raise ValidationError(_(u"Поле %s - обязательно для заполнения" % (self.fields[name].label)))

                if name == 'used_ipsubnet' and value:
                    value = ('' if not(type_of_settings == 'primary') else value)
                    networks = [str(ip) for ip in (IPNetwork(value) if value else [])]
                    mikrotiks = Mikrotik.objects.all().exclude(id=id) if id else Mikrotik.objects.all()
                    for i in mikrotiks:
                        others_networks = [str(ip) for ip in (IPNetwork(i.used_ipsubnet) if i.used_ipsubnet else [])]
                        ip_subnet_search = [str(ip) for ip in others_networks if ip in networks]
                        if (ip_subnet_search):
                            raise ValidationError(_(u"Введёная используемая IP подсеть пересекается с существующими подсетями"))
                if name == 'id':
                    id = value
                if name == 'type_of_settings' and value:
                    type_of_settings = value
                
                if (name == 'flat' or name == 'notation')and not(value) and type_of_settings == 'user':
                    raise ValidationError(_(u"Поле %s - обязательно для заполнения" % (self.fields[name].label)))
                
                if isinstance(field, FileField):
                    initial = self.initial.get(name, field.initial)
                    value = field.clean(value, initial)
                else:
                    value = field.clean(value)
                self.cleaned_data[name] = value
                if hasattr(self, 'clean_%s' % name):
                    value = getattr(self, 'clean_%s' % name)()
                    self.cleaned_data[name] = value

            except ValidationError as e:
                if not(((name == 'ip_address' or name == 'used_ipsubnet') and (type_of_settings != 'primary') or name == 'parent' and \
                        type_of_settings == 'primary') and not(value)):
                    self._errors[name] = self.error_class(e.messages)
                    if name in self.cleaned_data:
                        del self.cleaned_data[name]
                else:
                    self.cleaned_data[name] = value
            except Exception as e:
                try:
                    self._errors[name] = self.error_class([u''.join(x for x in e.message), ])
                except:
                    self._errors[name] = self.error_class([str(e), ])
                if name in self.cleaned_data:
                    del self.cleaned_data[name]

