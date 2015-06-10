# -*- coding=utf-8 -*-
# $Id: forms.py 249 2010-12-06 13:26:47Z site $

""" FORMS FOR ACCOUNT APP """
from data_centr.models import Zakazy
from billing.models import BillserviceAccount
from django.forms.extras.widgets import SelectDateWidget
from django.contrib.auth.models import User
import time
from django.db import models
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate
from django.conf import settings
from captcha.fields import CaptchaField
from models import *
from fs.models import Voice_mail
from telnumbers.models import TelNumber
from externalnumbers.consts import REGIONS
from externalnumbers.models import ExternalNumber
from django.template.defaultfilters import filesizeformat
from functools import partial
from lib.forms.widgets import SorlThumbnailImageInput
from lib.forms.fields import FakeEmptyFieldFile
from django.utils.safestring import mark_safe
from adminmail.models import Letter
from tariffs.models import TariffGroup
from cards.models import BillserviceCard
from django.forms.extras.widgets import SelectDateWidget
from lib.forms.widgets import JqCalendar
from datetime import datetime, timedelta

from random import randint
import random


class UserRegistrationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given email and password.
    """
    status = forms.CharField(label='',
                             required=False,
                             widget=forms.TextInput(attrs={'readonly':"readonly-------------------------------------------------------------", 'tabindex':"-1"}))
    email = forms.EmailField(label=u"Email", required=True)
    #password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput(), min_length=8, max_length=64, required=True, help_text=u'Пароль должен обязательно содержать заглавные буквы и цифры')
    #password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput, min_length=8, max_length=64, required=True)
    profile = forms.ChoiceField(label=u'Тип аккаунта', choices=((1, u'Физическое лицо'), (2, u'Юридическое лицо')), widget=forms.RadioSelect())
    
    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        #self.fields['username'].label = _(u'User name (login)')
        #self.fields['username'].help_text = (u'Обязательное поле. Введите 3 символа или более. Используйте только буквы, цифры и знаки из набора @/./+/-/_') 
        self.fields['email'].label = _(u"Email")
        self.fields['profile'].initial = 1

    class Media:

        css = { 'all': (settings.MEDIA_URL + 'css/script_reg_users_check.css' ,
                        ) }
        js = (settings.MEDIA_URL + 'js/script_reg_users_check.js',)

    class Meta:
        model = User
        #fields = ['username', 'email']
        fields = ['email']
        
    '''
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(_("The two password fields didn't match."))
        import re
        reg_ex = re.match(r"((.?)[A-Z]{1,}(.*?)[0-9]{1,}(.*?))|((.*?)[0-9]{1,}(.*?)[A-Z]{1,}(.?))", self.cleaned_data['password1'])
        if reg_ex == None:
            raise forms.ValidationError(u"Ваш пароль слишком простой. Используйте заглавные буквы и цифры")
        return password2
    '''
        
    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.is_active = False
        user.site_reg = settings.CURRENT_SITE
        user.is_juridical = True if self.cleaned_data['profile'] in ('2',) else False
        user.username = self.cleaned_data["email"] # add saving user_name as e-mail
        #add password generating
        pas = ''
        amount = randint(6, 10)
        for i in xrange(amount):
            pas = pas + random.choice('qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1237894560')
        user.set_password(pas)
        
        if commit:
            user.save()
        return user
    '''
    def get_row_password(self):
        try:
            return self.cleaned_data['password1']
        except KeyError:
            raise Exception("You should call get_row_password only after form validation")
    '''

    def clean_username(self):
        data = self.cleaned_data['username']
        if data.lower() in settings.BLOCKED_USERNAME:
            raise forms.ValidationError(u'Пользователь с таким именем уже существует')
        try:
            BillserviceCard.objects.get(login=data)
            raise forms.ValidationError(u'Пользователь с таким именем уже существует.')
        except BillserviceCard.DoesNotExist:
            pass
        try:
            int(data)
        except Exception:
            return data
        else:
            raise forms.ValidationError(u'Логин не может состоять только из цифр')
        
    def clean_email(self):
        data_email = self.cleaned_data['email']
        user_objs = User.objects.filter(email=data_email)
        if user_objs.count() >0:
            raise forms.ValidationError(u'Данный адрес электронной почты уже используется на сайте.')
        else:
            return data_email
        
class ResendActivationCodeForm(forms.Form):
    user = forms.CharField(label=u'Имя пользователя', help_text=u'Введите имя пользователя, которое Вы использовали при регистрации.')
    def clean_user(self):
        username = self.cleaned_data['user']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError(u'Пользователь не найден.')
        self.cleaned_data['user'] = user
        return user


class ComplaintForm(forms.Form):
    title = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(),
        label=_(u'Краткая информация по Вашей жалобе'),
        )

    submitter_email = forms.EmailField(
        required=False,
        label=_('Your E-Mail Address'),
        help_text=_(u'Мы можем оповестить Вас как только проблема разрешится'),
        )

    bodytext = forms.CharField(
        widget=forms.Textarea(attrs={'cols' : "50", 'rows': "10", 'style':"resize:vertical;", }),
        label=_('Description of your issue'),
        required=True,
        help_text=_(u'Пожалуйста, будьте максимально информативным, нам пригодятся любые подробности касающиеся Вашей жалобы. '),
        )



class WishInternetForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(),
        label=_(u'Представьтесь'),
        )

    place = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(),
        label=_(u'Место оказания услуги'),
        )

    submitter_email = forms.EmailField(
        required=False,
        label=_('Your E-Mail Address'),
        )

    text = forms.CharField(
        widget=forms.Textarea(attrs={'cols' : "50", 'rows': "10", 'style':"resize:vertical;", }),
        label=_(u'Описание вашей просьбы/жалобы'),
        required=True,
        )



# class FaxForm(forms.ModelForm):
class FaxForm(forms.Form):
    number = forms.ChoiceField(
        # choices = (("v1", "v2111"), ("v3", "v4111")), # левые значения для дебага, всмысле, если я их вижу - значит что-то не так
        label=_("From number"),
        required=False,
        )
#    to_numb = forms.CharField(
#                              label = _('To number'),
#                              max_length=15
#                              )
#    add_number = forms.CharField(
#                                 label = _(u'Добавочный номер'),
#                                 required = False,
#                                 max_length=5
#                                 )
#    filename = forms.ImageField(
#                                label = _('Select the file'),
#                                required = False,
#                                )
#    enabled_size = forms.ChoiceField(
#        choices = (("on", "True"), ("False","False")), # тут надо on для того, чтобы форма проходила валидацию.
#        widget = forms.CheckboxInput(
#            #attrs = {"id" : "time_enabled_checkbox" }
#            ),
#        label = _(u"по ширине"),
#        required = False
#    )


    def __init__(self, model=None, data=None, profile=None, request=None):
        super(FaxForm, self).__init__(data=data)
        self.model = model
        self.profile = profile
        self.request = request
        self.init_error = False
        self.request = request
        if model:
            self.fields["number"].initial = model.number
            if profile:
                numbers = profile.billing_account.phones
                self.fields["number"].choices = []
                for number in numbers:
                    tns = number.tel_number
                    if number.person_name:
                        tns += " (" + number.person_name + ")"
                    self.fields["number"].choices.append((number.tel_number, tns))

                if model.number:
                    self.fields["number"].initial = model.number
#                    self.from_number_value = model.number
                else:
                    if numbers:
                        if numbers[0]:
                            self.fields["number"].initial = numbers[0].tel_number
#                            self.from_number_value = numbers[0].tel_number
                    else:
                        # self.request.notifications.add(_("You have no internal numbers. You should create one first"), "warning")
                        self.init_error = True
            # self.fields["to_numb"].initial = model.to_numb
            # self.fields["filename"].initial = model.filename

######################################

class UserLoginForm(forms.Form):
    username = forms.CharField(required=True, label=_(u'Адрес электронной почты или логин'))
    password = forms.CharField(widget=forms.PasswordInput, label=_(u'Password'), required=True)
    captcha = CaptchaField(label=_(u'Enter symbols'), required=True)

    def __init__(self, *a, **kw):
        super(UserLoginForm, self).__init__(*a, **kw)
        self.user = None

    def clean(self):
        if self._errors:
            return {}
        user_qs = User.objects.filter(username=self.cleaned_data['username'])
        if settings.CURRENT_SITE == 1 or settings.CURRENT_SITE == 2:
            if user_qs:
                if user_qs[0].site_reg != settings.CURRENT_SITE:
                    raise forms.ValidationError(_(u'Please enter a correct username and password. Note that both fields are case-sensitive'))
            self.user = authenticate(username=self.cleaned_data['username'], password=self.cleaned_data['password'])
        elif settings.CURRENT_SITE == 3:
            if user_qs:
                if user_qs[0].site_reg == 2:  # Если пользователь mobi зарегистрирован на MoscowData, то ошибка
                    raise forms.ValidationError(_(u'Please enter a correct username and password. Note that both fields are case-sensitive'))
            self.user = authenticate(username=self.cleaned_data['username'], password=self.cleaned_data['password'])
        if not self.user:
            self.cleaned_data = {}
            raise forms.ValidationError(_(u'Please enter a correct username and password. Note that both fields are case-sensitive'))
        return self.cleaned_data


class UserLoginForm2(forms.Form):
    username = forms.CharField(required=True, label=_(u'Адрес электронной почты или логин'))
    password = forms.CharField(widget=forms.PasswordInput, label=_(u'Password'), required=True)
    captcha = CaptchaField(label=_(u'Enter symbols'), required=True)

    def __init__(self, *a, **kw):
        super(UserLoginForm2, self).__init__(*a, **kw)
        self.user = None

    def clean(self):
        if self._errors:
            return {}
        user_qs = User.objects.filter(username=self.cleaned_data['username'])
        if settings.CURRENT_SITE == 1 or settings.CURRENT_SITE == 2:
            if user_qs:
                if user_qs[0].site_reg != settings.CURRENT_SITE:
                    raise forms.ValidationError(_(u'Please enter a correct username and password. Note that both fields are case-sensitive'))
        self.user = authenticate(username=self.cleaned_data['username'], password=self.cleaned_data['password'])
        if settings.CURRENT_SITE == 3:
            if user_qs:
                if user_qs[0].site_reg == 2:  # Если пользователь mobi зарегистрирован на MoscowData, то ошибка
                    raise forms.ValidationError(_(u'Please enter a correct username and password. Note that both fields are case-sensitive'))
            self.user = authenticate(username=self.cleaned_data['username'], password=self.cleaned_data['password'])
        if not self.user:
            self.cleaned_data = {}
            raise forms.ValidationError(_(u'Please enter a correct username and password. Note that both fields are case-sensitive'))
        return self.cleaned_data

class PasswordResetRequestForm(forms.Form):
    username_reset = forms.CharField(required=True, label=(u'Имя пользователя'),)

    def clean(self):
        cleaned_data = self.cleaned_data
        if cleaned_data:
            try:
                self.user = User.objects.get(username=cleaned_data['username_reset'])
                if self.user.site_reg != settings.CURRENT_SITE:
                    self.user = None
            except User.DoesNotExist:
                self.user = None
        return cleaned_data


class ChangePasswordForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('request').user
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    current_password = forms.CharField(min_length=8,
                               max_length=128,
                               widget=forms.PasswordInput(),
                               label=_('Current password'))
    password = forms.CharField(min_length=8,
                               max_length=128,
                               widget=forms.PasswordInput(),
                               label=_('New password'),
                               help_text=u'Пароль должен обязательно содержать заглавные буквы и цифры')

    password_repeat = forms.CharField(widget=forms.PasswordInput(), label=_(u'Repeat new password:'))

    def clean_current_password(self):
        password = self.cleaned_data.get('current_password', '')
        if not self.user.password == password:
            raise forms.ValidationError(_(u"Invalid password"))
        return password

    def clean_password(self):
        password = self.cleaned_data.get('password', '')
        import re
        reg_ex = re.match(r"((.?)[A-Z]{1,}(.*?)[0-9]{1,}(.*?))|((.*?)[0-9]{1,}(.*?)[A-Z]{1,}(.?))", password)
        if reg_ex == None:
            raise forms.ValidationError(u"Ваш пароль слишком простой. Используйте заглавные буквы и цифры")
        return password

    def clean_password_repeat(self):
        if self.cleaned_data.get('password', '') != self.cleaned_data.get('password_repeat', ''):
            raise forms.ValidationError(_('Entered passwords do not match. Please enter identical passwords into "New password" and "Repeat password" fields.'))
        return self.cleaned_data.get('password_repeat', '')



class SendLetterToBlock(forms.ModelForm):
    class Meta:
        model = Letter
        fields = ['subject', 'texttemplate']
        widgets = {
        'subject': forms.Textarea(attrs={'cols':60, 'rows':2, 'style':"resize:vertical;"}),
        'texttemplate': forms.Textarea(attrs={'cols':60, 'style':"resize:vertical;"})
        }
class ProfilePhisicalDataForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['last_name', 'first_name', 'second_name', 'sex', 'birthday', 'pasport_serial', 'when_given_out', 'by_whom_given_out', 'phones']
        widgets = {
        'birthday': SelectDateWidget(years=range(1900, \
                                     datetime.now().year),
                                     attrs={"style" : "width: 80px;"}),
        'when_given_out': SelectDateWidget(years=range(1900, \
                 datetime.now().year + 1),
                 attrs={"style" : "width: 80px;"}),
        'phones': forms.Textarea(attrs={'cols':65, 'rows':2, 'style':"resize:vertical;"})
        }

    def __init__(self, *args, **kwargs):
        readonly = kwargs.pop('readonly', False)
        super(ProfilePhisicalDataForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            if isinstance(self.fields[f].widget, forms.TextInput) and f not in ['birthday']:
                self.fields[f].widget.attrs = {'size':90}
            if f == 'sex':
                if not bool(self.fields[f].choices[0][0]):
                    self.fields[f].choices = [('', _(u'Not defined'))] + self.fields[f].choices[1:]
        if readonly:
            try:
                profile_id = self.instance.id
                profile_obj = Profile.objects.get(id=profile_id)
                for f in self.fields:
                    value = getattr(profile_obj, f)
                    if f not in ('sex',):
                        if value != None and value:
                            self.fields[f] = ReadOnlyField(label=profile_obj._meta.get_field(f).verbose_name)
                    else:
                        if value in (1, 0):
                            self.fields[f] = ReadOnlyField(label=profile_obj._meta.get_field(f).verbose_name, choices=profile_obj._meta.get_field(f).choices)
            except:
                pass
        # Add to your settings file
        self.CONTENT_TYPES = ['image']
        # 1M - 1048576
        # 2.5MB - 2621440
        # 5MB - 5242880
        # 10MB - 10485760
        # 20MB - 20971520
        # 50MB - 5242880
        # 100MB 104857600
        # 250MB - 214958080
        # 500MB - 429916160
        self.MAX_UPLOAD_SIZE = 1048576

        # Add to a form containing a FileField and change the field names accordingly.


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'is_staff', 'is_active', 'date_joined']
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for f in self.fields:
                self.fields[f].widget.attrs = {'size':90}

from django.forms.util import flatatt

class ReadOnlyWidget(forms.Widget):
    def render(self, name, value, attrs):
        if self.attrs.has_key('choices'):
            choices = self.attrs['choices']
            if choices:
                for i in range(len(choices)):
                    if value == choices[i][0]:
                        value = choices[i][1]
        final_attrs = self.build_attrs(attrs, name=name)
        if hasattr(self, 'initial'):
            value = self.initial
        return "<p %s>%s</p>" % (flatatt(final_attrs), value or '')

    def _has_changed(self, initial, data):
        return False


class ReadOnlyField(forms.FileField):
#    widget = ReadOnlyWidget
    def __init__(self, widget=None, label=None, initial=None, help_text=None, choices=None):
        forms.Field.__init__(self, label=label, initial=initial,
            help_text=help_text, widget=ReadOnlyWidget(attrs={'choices':choices}))
    def clean(self, value, initial):
        self.widget.initial = initial
        return initial

class ProfilePhisicalNotEditForm(ProfilePhisicalDataForm):
    class Meta:
        model = Profile
        fields = ['last_name', 'first_name', 'second_name', 'sex', 'birthday']
        widgets = {
        'birthday': SelectDateWidget(years=range(1900, \
                                     datetime.now().year),
                                     attrs={"style" : "width: 80px;"})
        }
    def __init__(self, data=None, readonly_field=False, *args, **kwargs):
        self.data = data
        super(ProfilePhisicalNotEditForm, self).__init__(data=data, *args, **kwargs)


class ProfilePhisicalDataAdditionalForm(ProfilePhisicalDataForm):
    class Meta:
        model = Profile
        fields = ['pasport_serial', 'when_given_out', 'by_whom_given_out', 'phones']
        widgets = {
        'when_given_out': SelectDateWidget(years=range(1900, \
                 datetime.now().year + 1),
                 attrs={"style" : "width: 80px;"}),
        'phones': forms.Textarea(attrs={'cols':65, 'rows':2, 'style':"resize:vertical;"})
        }


class ProfileCardDataForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['user']

    def __init__(self, *args, **kwargs):
        super(ProfileCardDataForm, self).__init__(*args, **kwargs)




class AddressBaseForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ['address_type', 'phones']
        widgets = {
            'address_line': forms.Textarea(attrs={'cols':65, 'rows':2, 'style':"resize:vertical;"})
        }

    def __init__(self, *args, **kwargs):
        address_type = kwargs.pop('address_type', None)
        readonly = kwargs.pop('readonly', False)
        super(AddressBaseForm, self).__init__(*args, **kwargs)
        if address_type:
            self.instance.address_type = address_type
        for f in self.fields:
            if isinstance(self.fields[f].widget, forms.TextInput):
                self.fields[f].widget.attrs = {'size':90}
                self.fields[f].required = True
        if readonly:
            try:
                address_id = self.instance.id
                address_obj = Address.objects.get(id=address_id)
                for f in self.fields:
                    value = getattr(address_obj, f)
                    if value != None and value:
                        self.fields[f] = ReadOnlyField(label=address_obj._meta.get_field(f).verbose_name)
            except:
                pass

    @property
    def address(self):
        return self.save(commit=False)


class BillingAccountFormIdle(forms.ModelForm):

    class Meta:
        model = BillserviceAccount
        fields = ['idle_time', 'idle_time_for_every_month']

    def __init__(self, *args, **kwargs):
        super(BillingAccountFormIdle, self).__init__(*args, **kwargs)
        self.fields['idle_time'].label = u'Количество дней на оплату'
        self.fields['idle_time'].help_text = u'для первой оплаты'
        self.fields['idle_time_for_every_month'].label = u'Количество дней на оплату'
        self.fields['idle_time_for_every_month'].help_text = u'для последующих оплат'




class ProfileJuridicalDataForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['company_name', 'legal_form', "general_director", "sign_face", "sign_face_in_a_genitive_case", "sign_cause", 'bank_name', \
                  'settlement_account', 'correspondent_account', 'bik', 'bank_address', "kpp", 'okpo', 'phones']
        widgets = {
            'phones': forms.Textarea(attrs={'cols':65, 'rows':2, 'style':"resize:vertical;"}),
        }

    def __init__(self, *args, **kwargs):
        readonly = kwargs.pop('readonly', False)
        super(ProfileJuridicalDataForm, self).__init__(*args, **kwargs)
        for f in self.fields:
            self.fields[f].required = True
            if isinstance(self.fields[f].widget, forms.TextInput):
                self.fields[f].widget.attrs = {'size':90}

            if isinstance(self.fields[f].widget, forms.Textarea):
                self.fields[f].widget.attrs = {'cols':65, 'style':"resize:vertical;"}

            if f == "sign_cause":
                self.fields[f].widget.attrs["value"] = u"Устава"
        if readonly:
            try:
                profile_id = self.instance.id
                profile_obj = Profile.objects.get(id=profile_id)
                for f in self.fields:
                    value = getattr(profile_obj, f)
                    if value != None and value:
                        self.fields[f] = ReadOnlyField(label=profile_obj._meta.get_field(f).verbose_name)
            except:
                pass



class TelNumberForm(forms.ModelForm):
    class Meta:
        model = TelNumber
        fields = ['tel_number', 'password', 'person_name', 'internal_phone', "is_free", "is_blocked_call"]



class BalanceForm(forms.ModelForm):
    class Meta:
        model = BillserviceAccount

        fields = ['ballance', 'credit']
        widgets = {
            'credit': forms.Textarea(attrs={'cols':65, 'rows':1, 'style':"resize:None;"}),
            }


class Zakazy_Custom_Form(forms.ModelForm):
    class Meta:
        model = Zakazy
        fields = ['id', 'service_type', 'date_create', 'date_activation', 'date_deactivation', 'status_zakaza']


class ProfileJuridicalDataMainForm(ProfileJuridicalDataForm):
    class Meta:
        model = Profile
        fields = ['company_name', 'legal_form', 'bank_address', 'kpp']


class ProfileJuridicalDataAdditionalForm(ProfileJuridicalDataForm):
    class Meta:
        model = Profile
        fields = ['bank_name', 'settlement_account', 'correspondent_account', 'bik', 'okpo']


class ProfileJuridicalDataIgnoredForm(ProfileJuridicalDataForm):
    class Meta:
        model = Profile
        fields = ["general_director", "sign_face", "sign_face_in_a_genitive_case", "sign_cause", 'phones']



AddressResidentialForm = partial(AddressBaseForm, address_type=ADDRESS_TYPE_RESIDENTIAL)
AddressLegalForm = partial(AddressBaseForm, address_type=ADDRESS_TYPE_LEGAL)
AddressPostalForm = partial(AddressBaseForm, address_type=ADDRESS_TYPE_POSTAL)
AddressPhysicalForm = partial(AddressBaseForm, address_type=ADDRESS_TYPE_PHYSICAL)

class AccountTypeSelectForm(forms.Form):
    account_type = forms.ChoiceField(choices=(('id_personal', _(u"Personal")), ('id_corporate', _(u"Corporate"))), widget=forms.RadioSelect, label='', required=False)

class AccountTypeSelectFormPhysical(forms.Form):
    account_type = forms.ChoiceField(choices=(('id_personal', _(u"Personal")),), widget=forms.RadioSelect, label='', required=False)

class AccountTypeSelectFormJuridical(forms.Form):
    account_type = forms.ChoiceField(choices=(('id_corporate', _(u"Corporate")),), widget=forms.RadioSelect, label='', required=False)


from django.core.validators import RegexValidator
import re

validate_alnum = RegexValidator(regex=re.compile(r'^[\w]+$'), \
                                message=_(u"You can only use numbers and letters"), \
                                code='alnum')




def first_date():
    now = datetime.now()
    return datetime(now.year, now.month, 1).date()

def first_date_new2():
    delta = timedelta(days=30)
    now = datetime.now() - delta
    return datetime(now.year, now.month, now.day).date()

def first_date_last2():
    now = datetime.now()
    return datetime(now.year, now.month, now.day).date()

def first_date_new():
    now = datetime.now()
    return datetime(now.year, now.month, now.day).date()

def first_date_last():
    delta = timedelta(days=1)
    now = datetime.now() + delta
    return datetime(now.year, now.month, now.day).date()

def last_date():
    now = datetime.now()
    return now.date()


class BalanceFilterForm(forms.Form):

    date_from = forms.DateField(
        required=False,
        input_formats=('%d.%m.%Y',),
        # widget=JqCalendar(),
        widget=forms.DateInput(attrs={'class':"datepicker", 'readonly':'readonly'},),
        label=u'Дата, с',
        initial=first_date_new().strftime("%d.%m.%Y")
    )
    date_to = forms.DateField(
        required=False,
        input_formats=('%d.%m.%Y',),
        # widget=JqCalendar(),
        widget=forms.DateInput(attrs={'class':"datepicker", 'readonly':'readonly'},),
        label=u'Дата, по',
        initial=first_date_last().strftime("%d.%m.%Y")
    )
    caller_number = forms.CharField(required=False)  # , label=u'Вызывающий абонент')
    called_number = forms.CharField(required=False)  # , label=u'Вызывающий абонент')
    group = forms.CharField(required=False)
    call_length_type = forms.ChoiceField(widget=forms.Select, choices=[(1, 'Все разговоры'), (2, 'С нулевой продолжительностью'), (3, 'Состоявшиеся')])
    call_type = forms.ChoiceField(widget=forms.Select, choices=[(1, 'Все'), (2, 'Входящие'), (3, 'Исходящие ')])

class BalanceFaxFilterForm(forms.Form):
    date_from = forms.DateField(
        required=False,
        input_formats=('%d.%m.%Y',),
        # widget=JqCalendar(),
        widget=forms.DateInput(attrs={'class':"datepicker", 'readonly':'readonly'},),
        label=u'Дата, с',
        initial=first_date_new().strftime("%d.%m.%Y")
    )
    date_to = forms.DateField(
        required=False,
        input_formats=('%d.%m.%Y',),
        # widget=JqCalendar(),
        widget=forms.DateInput(attrs={'class':"datepicker", 'readonly':'readonly'},),
        label=u'Дата, по',
        initial=first_date_last().strftime("%d.%m.%Y")
    )
    caller_number = forms.CharField(required=False)  # , label=u'Вызывающий абонент')
    called_number = forms.CharField(required=False)  # , label=u'Вызывающий абонент')


class ChangeBillingGroupForm(forms.Form):
    def get_billing_groups():
        from django.db import transaction
        x = [(grp.id, grp.group_name) for grp in TariffGroup.objects.all()]
        transaction.commit_unless_managed(using=settings.BILLING_DB)
        return x

    billing_group = forms.ChoiceField(
        choices=get_billing_groups(),
        label=_(u"Select tariff group")
    )


class Voicemail(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={"id" : "name_field"}),
        label=_(u"Название"),
        required=False
    )

    email = forms.EmailField(
        widget=forms.TextInput(attrs={'id':'validate1', 'onkeyup':'lol(this, 1)', 'autocomplete':'off'},),
        label=u"Ваш Email адрес",
        required=False
    )
    flags = forms.MultipleChoiceField(
        choices=((1, "Безусловная"), (2, "Занято"), (3, "Не доступен"), (4, "Не отвечает")),
        widget=forms.CheckboxSelectMultiple(),
        label=_(u"Условие голосовой почты"),
        required=False
    )
    wait_time = forms.CharField(
        widget=forms.TextInput(attrs={"id" : "time_field"}),
        label=_(u"Время"),
        required=False
    )
    class Meta:
        model = Voice_mail
        fields = ['email']

    def __init__(self, model=None, data=None, profile=None, request=None):
        super(Voicemail, self).__init__(data=data)
        self.model = model
        self.data = data
        self.profile = profile
        self.request = request
        # пишем в свои поля значения из модели, если она вообще есть
        if model:
            self.fields["name"].initial = model.name
            self.fields["flags"].initial = model.reason
            self.fields["wait_time"].initial = (model.wait_time) / 1000
            self.fields["email"].initial = model.email

class CallTimeRangeForm(forms.Form):
    date_time_begin = forms.TimeField(
        widget=forms.TimeInput(attrs={"id" : "date_time_begin_field"}),
        label=_(u"Начало, включительно. Пример: 10:00"),
        required=False
    )
    date_time_end = forms.TimeField(
        widget=forms.TimeInput(attrs={"id" : "date_time_end_field"}),
        label=_(u"Конец, не включительно. Пример: 11:00"),
        required=False
    )

    def __init__(self, model=None, data=None, profile=None, request=None):
        super(CallTimeRangeForm, self).__init__(data=data)
        self.model = model
        self.data = data
        self.profile = profile
        self.request = request
         # пишем в свои поля значения из модели, если она вообще есть
        if model:
            self.fields["date_time_begin"].initial = model.date_time_begin
            self.fields["date_time_end"].initial = model.date_time_end

    def _model_from_data(self, cleaned_data, src_model=None):
        """
            Получаем модель с заполненными полями из очищенных данных
        """
        if src_model:
            model = src_model
        else:
            model = CallTimeRange()
        # заполняем поля
        if cleaned_data:  # если модель была валидирована
            model.date_time_begin = self.cleaned_data.get("date_time_begin")
            model.date_time_end = self.cleaned_data.get("date_time_end")
            return model

    def clean(self):
        cleaned_data = self.cleaned_data
        date_time_begin = cleaned_data.get("date_time_begin")
        date_time_end = cleaned_data.get("date_time_end")

        if date_time_begin == None:
            self._errors["date_time_begin"] = self.error_class([_(u"Please enter some valid time or disable time block").__unicode__()])
        if date_time_end == None:
            self._errors["date_time_end"] = self.error_class([_(u"Please enter some valid time or disable time block").__unicode__()])

        if date_time_begin != None and date_time_end != None:
            if date_time_begin >= date_time_end:
                self._errors["date_time_end"] = self.error_class([_(u"Введите верный интервал времени или отключите блок уловия времени").__unicode__()])

        # проверяю на пересекаемость условий времени и дня недели
        model = self._model_from_data(cleaned_data, src_model=self.model)
        if model:
            self.ok_model = model
        return cleaned_data

class CallNumberForm(forms.ModelForm):
    number = forms.CharField(
        widget=forms.TextInput(),
        label=_(u"Number"),
        required=True
    )

    class Meta:
        model = CallNumber
        fields = ['number']

    def __init__(self, model=None, data=None, profile=None, request=None):
        super(CallNumberForm, self).__init__(data=data)
        self.model = model
        self.data = data
        self.profile = profile
        self.request = request
         # пишем в свои поля значения из модели, если она вообще есть
        if model:
            self.fields["number"].initial = model.number

    def _model_from_data(self, cleaned_data, src_model=None):
        """
            Получаем модель с заполненными полями из очищенных данных
        """
        if src_model:
            model = src_model
        else:
            model = CallNumberForm()
        # заполняем поля
        if cleaned_data:  # если модель была валидирована
            model.number = self.cleaned_data.get("number")
            return model

    def clean(self):
        profile = self.profile
        cleaned_data = self.cleaned_data
        external = ExternalNumber.objects.filter(number=cleaned_data.get("number"), account=profile.billing_account_id)
        if external:
            self._errors["number"] = self.error_class([_(u"К сожалению Вы не можете добавить звонок на свой же номер.").__unicode__()])
        return cleaned_data
