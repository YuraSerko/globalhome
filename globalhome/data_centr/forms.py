# -*- coding=utf-8 -*-
from django import forms
from models import Address_dc_full, Units, Ports, Sockets, Zakazy, Tariff, \
                   Data_centr_payment, Priority_of_services
from django.utils.safestring import mark_safe
from django.forms.widgets import SelectMultiple, CheckboxInput, Select, RadioInput, SubWidget
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.html import conditional_escape, format_html, format_html_join
from itertools import chain
from django.forms.util import flatatt, to_current_timezone
from billing.models import BillserviceAccountTarif, BillserviceAccount, BillservicePrepaidMinutes
from internet.models import Internet_city, Internet_street, Internet_house, Connection_address
from telnumbers.models import TelNumbersGroup
import datetime, calendar
from dateutil.relativedelta import relativedelta
from data_centr.views import add_record_in_priority_of_services, real_section_name
import copy
from django.conf import settings  # @UnusedImport
from django.db import connections, transaction
from payment.models import Billservice_transaction
from internet.billing_models import SubAccount

from django.utils.translation import ugettext as _
from models import Zakazy
class ZakazyForm(forms.ModelForm):

    class Meta(object):
        model = Zakazy

    def __init__(self, *args, **kwargs):
        super(ZakazyForm, self).__init__(*args, **kwargs)
        self.fields['main_zakaz'].label = _(u'Родительский заказ')
        # self.fields['count_ip'].label = _(u'Количество ip')
        # self.fields['server'].label = _(u'Сервер')
        # self.fields['server_assembly'].label = _(u'Серверная сборка')
        # self.fields['adress_dc'].label = _(u'Постоянный адрес') # Почему-то не находит 'adress_dc' поле(KeyError,
        # self.fields['id'].label = _(u'Номер заказа') # Почему-то не находит 'id' поле, через verbose_name работает.


dict_abbr_for_person = {1:u'ю', 2:u'ф', 3:u'к', 4:u'о'}

@python_2_unicode_compatible
class MyRadioInput(SubWidget):
    """
    An object used by RadioFieldRenderer that represents a single
    <input type='radio'>.
    """

    def __init__(self, name, value, attrs, choice, index):
        self.name, self.value = name, value
        self.attrs = attrs
        self.choice_value = force_text(choice[0])
        self.choice_label = force_text(choice[1])
        self.index = index

    def __str__(self):
        return self.render()

    def render(self, name=None, value=None, attrs=None, choices=()):
        name = name or self.name
        value = value or self.value
        attrs = attrs or self.attrs
        if 'id' in self.attrs:
            label_for = format_html(' for="{0}_{1}"', self.attrs['id'], self.index)
        else:
            label_for = ''
        choice_label = force_text(self.choice_label)
        return format_html(u'<label{0}>{1} <span>{2}</span></label>', label_for, self.tag(), choice_label)

    def is_checked(self):
        return self.value == self.choice_value

    def tag(self):
        if 'id' in self.attrs:
            self.attrs['id'] = '%s_%s' % (self.attrs['id'], self.index)

        final_attrs = dict(self.attrs, type='radio', name=self.name, value=self.choice_value)
        if self.is_checked():
            final_attrs['checked'] = 'checked'
        return format_html(u'<input{0} />', flatatt(final_attrs))

@python_2_unicode_compatible
class MyRadioFieldRenderer(object):
    """
    An object used by RadioSelect to enable customization of radio widgets.
    """

    def __init__(self, name, value, attrs, choices):
        self.name, self.value, self.attrs = name, value, attrs
        self.choices = choices

    def __iter__(self):
        for i, choice in enumerate(self.choices):
            my_attrs = self.attrs.copy()
            try:
                if choice[1].status_port not in (2,):
                    my_attrs['disabled'] = 'disabled'
            except:
                pass
            try:
                if choice[1].status_socket not in (2,):
                    my_attrs['disabled'] = 'disabled'
            except:
                pass
            yield MyRadioInput(self.name, self.value, my_attrs, choice, i)

    def __getitem__(self, idx):
        choice = self.choices[idx]  # Let the IndexError propogate
        return MyRadioInput(self.name, self.value, self.attrs.copy(), choice, idx)

    def __str__(self):
        return self.render()

    def render(self):
        """Outputs a <ul> for this set of radio fields."""
        return format_html(u'<ul class="cols">\n{0}\n</ul>',
                           format_html_join('\n', u'<li>{0}</li>',
                                            [(force_text(w),) for w in self]
                                            ))

class MyRadioSelect(Select):
    renderer = MyRadioFieldRenderer

    def __init__(self, *args, **kwargs):
        # Override the default renderer if we were passed one.
        renderer = kwargs.pop('renderer', None)
        if renderer:
            self.renderer = renderer
        super(MyRadioSelect, self).__init__(*args, **kwargs)

    def subwidgets(self, name, value, attrs=None, choices=()):
        for widget in self.get_renderer(name, value, attrs, choices):
            yield widget

    def get_renderer(self, name, value, attrs=None, choices=()):
        """Returns an instance of the renderer."""
        if value is None: value = ''
        str_value = force_text(value)  # Normalize to string.
        final_attrs = self.build_attrs(attrs)
        choices = list(chain(self.choices, choices))
        return self.renderer(name, str_value, final_attrs, choices)

    def render(self, name, value, attrs=None, choices=()):
        return self.get_renderer(name, value, attrs, choices).render()

    def id_for_label(self, id_):
        # RadioSelect is represented by multiple <input type="radio"> fields,
        # each of which has a distinct ID. The IDs are made distinct by a "_X"
        # suffix, where X is the zero-based index of the radio field. Thus,
        # the label for a RadioSelect should reference the first one ('_0').
        if id_:
            id_ += '_0'
        return id_


class MyCheckboxSelectMultiple(SelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name,)
        output = ['<ul class="cols">']
        # Normalize to strings
        str_values = set([force_text(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                if option_label.status_unit in (2,):
                    final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i),)
                    if 'disabled' in final_attrs:
                        del final_attrs['disabled']
                else:
                    final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i),)
                    final_attrs['disabled'] = 'disabled'
                label_for = format_html(' for="{0}"', final_attrs['id'])
            else:
                label_for = ''
            cb = CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_text(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = force_text(option_label)
            output.append(format_html('<li><label{0}>{1} <span>{2}</span></label></li>',
                                      label_for, rendered_cb, option_label))
        output.append('</ul>')
        return mark_safe('\n'.join(output))

    def id_for_label(self, id_):
        # See the comment for RadioSelect.id_for_label()
        if id_:
            id_ += '_0'
        return id_


class RuleCheckboxSelectMultiple(SelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        spis_available_rules_choice = []
        spis_mandatory_rules_choice = []
        available_rule_qs = Rules_for_restore_zakaz.objects.filter(service_type=self.attrs['service_type_init'])
        if available_rule_qs:
            for i in available_rule_qs[0].rules.all().order_by('name_rule'):
                spis_available_rules_choice.append(i.id)
            for i in available_rule_qs[0].mandatory_rules.all().order_by('name_rule'):
                spis_mandatory_rules_choice.append(i.id)

        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name,)
        output = ['<ul class="cols" id="id_spis_rules">']
        # Normalize to strings
        str_values = set([force_text(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                if option_value in spis_available_rules_choice:
                    rule_obj = Spis_rules_for_restore_zakaz.objects.get(id=option_value)
                    final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i),)
                    if 'checked' in final_attrs:
                        del final_attrs['checked']
                    if 'onclick' in final_attrs:
                        del final_attrs['onclick']
                    if 'disabled' in final_attrs:
                        del final_attrs['disabled']
                    if option_value in spis_mandatory_rules_choice:
                        final_attrs['checked'] = 'checked'
                        final_attrs['onclick'] = 'window.event.returnValue=false'
                    if rule_obj.action_on_change:
                        final_attrs['onclick'] = 'check_rule(this, "%s")' % rule_obj.action_on_change
                else:
                    final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i),)
                    final_attrs['disabled'] = 'disabled'
                label_for = format_html(' for="{0}"', final_attrs['id'])
            else:
                label_for = ''
            cb = CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_text(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = force_text(option_label)
            output.append(format_html(u'<li><label{0}>{1} <span>{2}</span></label></li>',
                                      label_for, rendered_cb, option_label))
        output.append('</ul>')
        return mark_safe('\n'.join(output))

    def id_for_label(self, id_):
        # See the comment for RadioSelect.id_for_label()
        if id_:
            id_ += '_0'
        return id_


class ChangeRackInAddress(forms.Form):
    rack = forms.ChoiceField()
    def __init__(self, data=None, choices=[], rack_init=''):
        self.data = data
        super(ChangeRackInAddress, self).__init__(data=data)
        self.fields["rack"].choices = choices
        if rack_init:
            self.fields["rack"].initial = rack_init.id


class ChangeUnitInAddress(forms.Form):
    zakaz_id = 0
    unit = forms.MultipleChoiceField(widget=MyCheckboxSelectMultiple(),)
    def __init__(self, data=None, choices=[], spis_units='', zakaz_id=0):
        self.data = data
        super(ChangeUnitInAddress, self).__init__(data=data)
        if zakaz_id:
            self.zakaz_id = zakaz_id
        self.fields["unit"].choices = choices
        self.fields["unit"].initial = spis_units

    def clean(self):
        cleaned_data = self.cleaned_data
        zakaz_obj = Zakazy.objects.get(id=self.zakaz_id)
        if not zakaz_obj.server.count_unit == len(self.cleaned_data['unit']):
            raise forms.ValidationError(u'Не верное количество юнитов! Необходимо %s, Вы выбрали %s.' \
                                        % (zakaz_obj.server.count_unit, len(self.cleaned_data['unit'])))
        else:
            first_unit = self.cleaned_data['unit'][0]
            last_unit = self.cleaned_data['unit'][-1]
            if not int(last_unit) - int(first_unit) + 1 == zakaz_obj.server.count_unit:
                raise forms.ValidationError(u'Вы выбрали не последовательные юниты!')
        return cleaned_data


class ChangeSockettInAddress(forms.Form):
    socket = forms.ChoiceField(widget=MyRadioSelect(),)
    def __init__(self, data=None, choices=[], socket_init=''):
        self.data = data
        super(ChangeSockettInAddress, self).__init__(data=data)
        self.fields["socket"].choices = choices
        if socket_init:
            self.fields["socket"].initial = socket_init.id


class ChangeSwitchInAddress(forms.Form):
    switch = forms.ChoiceField()
    def __init__(self, data=None, choices=[], switch_init=''):
        self.data = data
        super(ChangeSwitchInAddress, self).__init__(data=data)
        self.fields["switch"].choices = choices
        if switch_init:
            self.fields["switch"].initial = switch_init.id


class ChangeBlockSocketInAddress(forms.Form):
    block_socket = forms.ChoiceField()
    def __init__(self, data=None, choices=[], block_socket_init=''):
        self.data = data
        super(ChangeBlockSocketInAddress, self).__init__(data=data)
        self.fields["block_socket"].choices = choices
        if block_socket_init:
            self.fields["block_socket"].initial = block_socket_init.id


class ChangePortInAddress(forms.Form):
    port = forms.ChoiceField(widget=MyRadioSelect(),)
    def __init__(self, data=None, choices=[], port_init=''):
        self.data = data
        super(ChangePortInAddress, self).__init__(data=data)
        self.fields["port"].choices = choices
        if port_init:
            self.fields["port"].initial = port_init.id


class ReadonlyFileInput(forms.Widget):
    def __init__(self, obj, attrs=None):
        self.object = obj
        super(ReadonlyFileInput, self).__init__(attrs)
    def render(self, name, value, attrs=None):
        return mark_safe(u'<p>%s</p>' % value)


class Address_dc_full_Admin_Form(forms.ModelForm):
    class Meta(object):
        model = Address_dc_full
        fields = ('id', 'name', 'rack', 'date_create',)
    units = forms.CharField(required=False)
    switch = forms.CharField(required=False)
    ports = forms.CharField(required=False)
    block_of_socket = forms.CharField(required=False)
    sockets = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super(Address_dc_full_Admin_Form, self).__init__(*args, **kwargs)
        instance = kwargs['instance']
        units_qs = Units.objects.filter(address=instance)
        units = ', '.join(str(units_obj.number_unit) for units_obj in units_qs)
        ports_qs = Ports.objects.filter(adrress=instance)
        ports = ', '.join(str(ports_obj.number_port) for ports_obj in ports_qs)
        sockets_qs = Sockets.objects.filter(adrress=instance)
        sockets = ', '.join(str(sockets_obj.number_socket) for sockets_obj in sockets_qs)

#        self.fields['id'].widget = ReadonlyFileInput(self)
#        self.fields['id'].required = False
        self.fields['name'].widget = ReadonlyFileInput(self)
        self.fields['name'].required = False
        self.fields['rack'].widget = ReadonlyFileInput(self)
        self.fields['rack'].required = False
        self.fields['date_create'].widget = ReadonlyFileInput(self)
        self.fields['date_create'].required = False
        self.fields['units'].initial = u'%s' % units if units else u'-'
        self.fields['units'].widget = ReadonlyFileInput(self)
        self.fields['ports'].initial = u'%s' % ports if ports else u'-'
        self.fields['ports'].widget = ReadonlyFileInput(self)
        self.fields['switch'].initial = u'%s' % ports_qs[0].switch if ports_qs else u'-'
        self.fields['switch'].widget = ReadonlyFileInput(self)

        self.fields['sockets'].initial = u'%s' % sockets if sockets else u'-'
        self.fields['sockets'].widget = ReadonlyFileInput(self)
        self.fields['block_of_socket'].initial = u'%s' % sockets_qs[0].block_of_socket if sockets_qs else u'-'
        self.fields['block_of_socket'].widget = ReadonlyFileInput(self)


class AccountInternetForm(forms.Form):
    account = forms.ChoiceField()
    def __init__(self, data=None):
        self.data = data
        super(AccountInternetForm, self).__init__(data=data)
        account_choice = [(0, '---')]
        for i in BillserviceAccount.objects.all().order_by('username'):
            account_choice.append((i.id, i.username))
        self.fields['account'].choices = account_choice

    def clean_account(self):
        account = self.cleaned_data['account']
        if not int(account):
            raise forms.ValidationError(u'Укажите логин')
        else:
            return self.cleaned_data


class TariffInternetForm(forms.Form):
    tariff = forms.ChoiceField()
    def __init__(self, data=None, type_account=''):
        self.data = data
        super(TariffInternetForm, self).__init__(data=data)
        tariff_choice = [(0, '---')]
        if type_account:
            for i in Tariff.objects.filter(service_type__id=8, for_person__id__in=type_account, individual=False, archive=False).order_by('speed_inet'):
                type_account = ','.join('%s' % dict_abbr_for_person[i.id] for i in i.for_person.all())
                tariff_choice.append((i.id, u'%s %s %s' % (type_account, u'%s Мбит/сек' % i.speed_inet, i.name)))
        self.fields['tariff'].choices = tariff_choice

    def clean_tariff(self):
        tariff = self.cleaned_data['tariff']
        if not int(tariff):
            raise forms.ValidationError(u'Укажите тариф')
        else:
            return self.cleaned_data


class CityInternetForm(forms.Form):
    city = forms.ChoiceField()
    def __init__(self, data=None):
        self.data = data
        super(CityInternetForm, self).__init__(data=data)
        city_choice = [(0, '---')]
        for i in Connection_address.objects.filter().order_by('city__city').distinct('city__city'):
            city_choice.append((i.city.id, i.city))
        self.fields['city'].choices = city_choice

    def clean_city(self):
        city = self.cleaned_data['city']
        if not int(city):
            raise forms.ValidationError(u'Укажите город')
        else:
            return self.cleaned_data


class StreetInternetForm(forms.Form):
    street = forms.ChoiceField()
    def __init__(self, data=None, city_init=''):
        self.data = data
        super(StreetInternetForm, self).__init__(data=data)
        street_choice = [(0, '---')]
        if city_init:
            street_qs = Connection_address.objects.filter(city__id=city_init).order_by('street__street').distinct('street__street')
            for i in street_qs:
                street_choice.append((i.street.id, i.street))
        self.fields['street'].choices = street_choice

    def clean_street(self):
        street = self.cleaned_data['street']
        if not int(street):
            raise forms.ValidationError(u'Укажите улицу')
        else:
            return self.cleaned_data


class HouseInternetForm(forms.Form):
    house = forms.ChoiceField()
    def __init__(self, data=None, street_init=''):
        self.data = data
        super(HouseInternetForm, self).__init__(data=data)
        house_choice = [(0, '---')]
        if street_init:
            house_qs = Connection_address.objects.filter(street__id=street_init).order_by('house__house').distinct('house__house')
            for i in house_qs:
                house_choice.append((i.house.id, i.house))
        self.fields['house'].choices = house_choice

    def clean_house(self):
        house = self.cleaned_data['house']
        if not int(house):
            raise forms.ValidationError(u'Укажите дом')
        else:
            return self.cleaned_data


class ZakazForm(forms.Form):
    zakaz = forms.ChoiceField(label=u'Заказ')
    def __init__(self, data=None, zakaz_init=''):
        self.data = data
        super(ZakazForm, self).__init__(data=data)
        zakazy_qs = Zakazy.objects.all().order_by('id')
        zakazy_choice = [('', '---')]
        for i in zakazy_qs:
            zakazy_choice.append((i.id, u'%s (%s)' % (i.id, i.service_type)))
        self.fields['zakaz'].choices = zakazy_choice
        if zakaz_init:
            self.fields['zakaz'].initial = zakaz_init



class ShowAttr(object):
    def get_show(self):
        return self._show
    def set_show(self, value):
        self._show = value
    show = property(get_show, set_show)

class MethodField(object):
    def get_method(self):
        return self._method
    def set_method(self, value):
        self._method = value
    def get_dependent(self):
        return self._dependent
    def set_dependent(self, value):
        self._dependent = value

    method = property(get_method, set_method)
    dependent = property(get_dependent, set_dependent)

from django.forms import BooleanField, ChoiceField, CharField
class MyBooleanField(BooleanField, ShowAttr, MethodField):
    pass

class MyChoiceField(ChoiceField, ShowAttr, MethodField):
    pass

class MyIntegerField(CharField, ShowAttr, MethodField):
    pass


class ReactivateZakaz(forms.Form):
    activate_zakaz = MyBooleanField(label=u'Активировать заказ')
    restore_payment = MyBooleanField(required=False, label=u'Действия с оплатой и приоритетом')
    prolong_payment_period = MyBooleanField(required=False, label=u'Продлить срок оплаты')
    count_day = MyIntegerField(required=False, label=u'На какое количество дней')
    to_pay = MyBooleanField(required=False, label=u'Оплатить за текущий месяц')
    def __init__(self, data=None, bill_acc_obj=''):
        self.data = data
        super(ReactivateZakaz, self).__init__(data=data)
        self.fields['activate_zakaz'].widget.attrs = {'onclick':'window.event.returnValue=false', 'checked':'checked'}
        self.fields['restore_payment'].widget.attrs = {'onclick':'show_payment()'}
        self.fields['prolong_payment_period'].widget.attrs = {'onclick':'show_count_day()'}
        self.fields['prolong_payment_period'].show = False
        self.fields['count_day'].show = False
        self.fields['to_pay'].show = False
        # здесь прописываем методы для полей
        self.fields['activate_zakaz'].method = 'met_activate_zakaz'
        self.fields['restore_payment'].method = 'met_restore_payment'
        # здесь указываем зависит ли поле от какого-нибудь другого
        self.fields['activate_zakaz'].dependent = False
        self.fields['restore_payment'].dependent = False
        self.fields['prolong_payment_period'].dependent = True
        self.fields['count_day'].dependent = True
        self.fields['to_pay'].dependent = True

    def call_method(self, field, zakaz_obj):
        print 'call_method'
        result = eval('self.%s(zakaz_obj)' % field.field.method)
        return result

    def met_activate_zakaz(self, zakaz_obj):
        if self.cleaned_data['activate_zakaz']:
            zakaz_obj.status_zakaza_id = 2
            zakaz_obj.date_deactivation = None
            zakaz_obj.save()
            return True
        return False


    def met_restore_payment(self, zakaz_obj):
        try:
            prolong_payment_period = self.data.has_key('prolong_payment_period')
            to_pay = self.data.has_key('to_pay')
            now = datetime.datetime.now()
            last_month = False
            # определяем за какой месяц неуплата
            payment_qs = Data_centr_payment.objects.filter(bill_account=zakaz_obj.bill_account, zakaz=zakaz_obj, year=now.year, month=now.month, postdate=True)
            if not payment_qs:
                date_last_month = now - relativedelta(months=1)
                payment_qs = Data_centr_payment.objects.filter(bill_account=zakaz_obj.bill_account, zakaz=zakaz_obj, year=date_last_month.year, month=date_last_month.month, postdate=True)
                last_month = True
                if not payment_qs:
                    return False
            # выполняем действия в независимости от месяца неуплаты
            payment_qs[0].postdate = False
            payment_qs[0].message_on_warning = 0
            payment_qs[0].save()
            priority_qs = Priority_of_services.objects.filter(bill_account=zakaz_obj.bill_account, zakaz_id=zakaz_obj.id)
            if not priority_qs:
                add_record_in_priority_of_services(zakaz_obj)
            # вот тут пошло разделение
            if last_month:
                new_payment_obj = copy.copy(payment_qs[0])
                new_payment_obj.id = None
                new_payment_obj.year = now.year
                new_payment_obj.month = now.month
                new_payment_obj.every_month = True
                new_payment_obj.cost = zakaz_obj.cost
                new_payment_obj.save()
                cost = payment_qs[0].cost
                # здесь оплатить за предыдущий месяц
                section_name = real_section_name(zakaz_obj)

                transaction_obj = Billservice_transaction(
                                                          bill=section_name,
                                                          account=zakaz_obj.bill_account,
                                                          type_id='ZAKAZ_PAY',
                                                          approved=True,
                                                          summ='-%s' % cost,
                                                          description=u'Оплата заказа №%s' % zakaz_obj.id,
                                                          created=now,
                                                          )
                transaction_obj.save()
                payment_qs[0].payment_date = now
                payment_qs[0].save()
            # а вот здесь пошли по выбранным пунктам
            if prolong_payment_period:
                if not last_month:
                    bill_acc_obj = zakaz_obj.bill_account
                    count_day = self.data['count_day']
                    date_paid = now + relativedelta(days=int(count_day))
                    idle_time = (date_paid - zakaz_obj.date_activation).days
                    bill_acc_obj.idle_time = idle_time
                    bill_acc_obj.save()
            if to_pay:
                if last_month:
                    cost = new_payment_obj.cost
                else:
                    cost = payment_qs[0].cost
                section_name = real_section_name(zakaz_obj)
                transaction_obj = Billservice_transaction(
                                                          bill=section_name,
                                                          account=zakaz_obj.bill_account,
                                                          type_id='ZAKAZ_PAY',
                                                          approved=True,
                                                          summ='-%s' % cost,
                                                          description=u'Оплата заказа №%s' % zakaz_obj.id,
                                                          created=now,
                                                          )
                transaction_obj.save()
                if last_month:
                    new_payment_obj.payment_date = now
                    new_payment_obj.save()
                else:
                    payment_qs[0].payment_date = now
                    payment_qs[0].save()
            return True
        except:
            return False

    def clean_restore_payment(self):
        print 'clean_restore_payment'
        zakaz_obj = Zakazy.objects.get(id=self.zakaz_id)
        restore_payment = self.data.has_key('restore_payment')
        if restore_payment:
            prolong_payment_period = self.data.has_key('prolong_payment_period')
            to_pay = self.data.has_key('to_pay')

            self.fields['prolong_payment_period'].show = True
            self.fields['to_pay'].show = True


            now = datetime.datetime.now()
            last_month = False
            payment_qs = Data_centr_payment.objects.filter(bill_account=zakaz_obj.bill_account, zakaz=zakaz_obj, year=now.year, month=now.month, postdate=True)
            if not payment_qs:
                date_last_month = now - relativedelta(months=1)
                payment_qs = Data_centr_payment.objects.filter(bill_account=zakaz_obj.bill_account, zakaz=zakaz_obj, year=date_last_month.year, month=date_last_month.month, postdate=True)
                last_month = True
                if not payment_qs:
                    raise forms.ValidationError(u'Вы не можете восстановить оплату у данного заказа')
            if not last_month:
                if not (prolong_payment_period or to_pay):
                    raise forms.ValidationError(u"Выберите хотя бы один пункт")
        return self

    def clean_count_day(self):
        print 'clean_count_day'
        prolong_payment_period = self.cleaned_data['prolong_payment_period']
        count_day = self.cleaned_data['count_day']
        if prolong_payment_period:
            self.fields['prolong_payment_period'].show = True
            self.fields['to_pay'].show = True
            self.fields['count_day'].show = True
            if not count_day:
                raise forms.ValidationError(u"Введите количество дней")
            else:
                if not count_day.isdigit():
                    raise forms.ValidationError(u"Введите целое число")
        else:
            self.fields['count_day'].show = False
        return self

class RulesInetZakaz(ReactivateZakaz):
    restore_connection_inet = MyBooleanField(label=u'Восстановить доступ в интернет')
    def __init__(self, data=None, bill_acc_obj=''):
        self.data = data
        super(RulesInetZakaz, self).__init__(data=data)
        self.fields['restore_connection_inet'].widget.attrs = {'onclick':'window.event.returnValue=false', 'checked':'checked'}
        # здесь прописываем методы для полей
        self.fields['restore_connection_inet'].method = 'met_restore_connection_inet'
        # здесь указываем зависит ли поле от какого-нибудь другого
        self.fields['restore_connection_inet'].dependent = False

    def met_restore_connection_inet(self, zakaz_obj):
        if self.cleaned_data['restore_connection_inet']:
            bill_account = zakaz_obj.bill_account
            bill_account.status = 1
            bill_account.save()
#            subaccount = SubAccount.objects.filter(account=zakaz_obj.bill_account)
#            if subaccount:
#                subaccount[0].nas_id = None
#                subaccount[0].save()
            return True
        return False


class RulesExternalNumber(ReactivateZakaz):
    restore_number = MyBooleanField(label=u'Закрепить номер за пользователем')
    restore_free_minutes = MyBooleanField(label=u'Пересчитать бесплатные минуты')
    fix_to_group = MyBooleanField(required=False, label=u'Закрепить за группой')
    groups = MyChoiceField(label=u'Группа', required=False)
    def __init__(self, data=None, bill_acc_obj=''):
        self.data = data
        super(RulesExternalNumber, self).__init__(data=data)
        spis_fields = ['restore_number', 'restore_free_minutes']
        for i in spis_fields:
            self.fields[i].widget.attrs = {'onclick':'window.event.returnValue=false', 'checked':'checked'}
        self.fields['fix_to_group'].widget.attrs = {'onclick':'show_group()'}
        self.fields['groups'].show = False

        groups_choice = [('', '---')]
        if bill_acc_obj:
            groups_qs = TelNumbersGroup.objects.filter(account=bill_acc_obj)
            for i in groups_qs:
                groups_choice.append((i.id, u'%s' % i.name))
        self.fields['groups'].choices = groups_choice
        # здесь прописываем методы для полей
        self.fields['restore_number'].method = 'met_restore_number'
        self.fields['restore_free_minutes'].method = 'met_restore_free_minutes'
        self.fields['fix_to_group'].method = 'met_fix_to_group'
        # здесь указываем зависит ли поле от какого-нибудь другого
        self.fields['restore_number'].dependent = False
        self.fields['restore_free_minutes'].dependent = False
        self.fields['fix_to_group'].dependent = False
        self.fields['groups'].dependent = True

    def met_restore_number(self, zakaz_obj):
        if self.cleaned_data['restore_number']:
            ext_number_obj = zakaz_obj.ext_numbers.all()[0]
            ext_number_obj.account = zakaz_obj.bill_account
            ext_number_obj.is_free = False
            ext_number_obj.is_reserved = False
            ext_number_obj.assigned_at = datetime.datetime.now()
            ext_number_obj.date_deactivation = None
            ext_number_obj.save()
            return True
        return False

    def met_restore_free_minutes(self, zakaz_obj):
        if self.cleaned_data['restore_free_minutes']:
            free_minutes_qs = BillservicePrepaidMinutes.objects.filter(zakaz_id=zakaz_obj.id)
            if not free_minutes_qs:
                last_day = int(calendar.mdays[datetime.date.today().month])
                day = float(calendar.mdays[datetime.date.today().month] - datetime.datetime.now().day + 1)
                free_minutes = zakaz_obj.tariff.free_minutes
                free_minutes = float(free_minutes) / float(last_day) * float(day)
                free_minutes_obj = BillservicePrepaidMinutes(
                                                            zone_id=zakaz_obj.tariff.tel_zone,
                                                            minutes=free_minutes,
                                                            account_id=zakaz_obj.bill_account.id,
                                                            service_id=0,
                                                            date_of_accrual=datetime.datetime.now(),
                                                            zakaz_id=zakaz_obj.id,
                                                            )
                free_minutes_obj.save()
            return True
        return False

    def met_fix_to_group(self, zakaz_obj):
        if self.cleaned_data['fix_to_group']:
            group_id = self.data['groups']
            group = TelNumbersGroup.objects.get(id=group_id)
            ext_number_obj = zakaz_obj.ext_numbers.all()[0]
            ext_number_obj.phone_numbers_group = group
            ext_number_obj.save()
            return True
        return False

    def clean_groups(self):
        print 'clean_groups'
        fix_to_group = self.cleaned_data['fix_to_group']
        groups = self.cleaned_data['groups']
        if fix_to_group:
            self.fields['groups'].show = True
            if not groups:
                raise forms.ValidationError(u"Выберите группу")
        else:
            self.fields['groups'].show = False
        return self


class AccountColocationForm(forms.Form):
    equipment_name = forms.CharField(required=True)
    height_unit = forms.ChoiceField(widget=forms.Select(attrs={'onchange':'change_unit(this)'}),)
    size = forms.ChoiceField(widget=forms.Select(attrs={'onchange':'cost_all_zakaz(this)'}),)
    inet_channel = forms.ChoiceField(widget=forms.Select(attrs={'onchange':'change_channel(this)'}),)
    inet_speed = forms.ChoiceField(widget=forms.Select(attrs={'onchange':'cost_all_zakaz(this)'}),)
    count_ip = forms.ChoiceField(widget=forms.Select(attrs={'onchange':'cost_all_zakaz(this)'}),)
    count_socket = forms.ChoiceField(widget=forms.Select(attrs={'onchange':'cost_all_zakaz(this)'}),)
    count_electro = forms.ChoiceField(widget=forms.Select(attrs={'onchange':'cost_all_zakaz(this)'}),)
    def __init__(self, data=None, *args, **kwargs):
        self.data = data
        super(AccountColocationForm, self).__init__(data=data, *args, **kwargs)
        choice_unit, choice_ip, choice_socket, choice_electro, choice_speed = [], [], [], [], []
        for i in range(1, 9):
            choice_unit.append((i, i))
            choice_socket.append((i, i))
        choice_unit.append(('tower', 'Tower'))
        choice_size = [('1', u'до 60'), ('2', u'до 80'), ('3', u'до 100')]
        for i in range(1, 7):
            choice_ip.append((i, i))
        for i in range(400, 1600, 100):
            choice_electro.append((i, u'%s Вт' % i))
        choice_channel = [('not_garant', u'Не гарантированный'), ('garant', u'Гарантированный')]
        tariff_queryset = Tariff.objects.filter(service_type=12, garant=False)
        for tariff in tariff_queryset:
            cost = u'%s руб.*' % (tariff.price_id.cost / 1.18) if tariff.price_id.cost > 0 else u'беспл.'
            choice_speed.append((tariff.id, u'%s Мбит/сек (%s)' % (tariff.speed_inet, cost)))
        self.fields['height_unit'].choices = choice_unit
        self.fields['size'].choices = choice_size
        self.fields['inet_channel'].choices = choice_channel
        self.fields['inet_speed'].choices = choice_speed
        self.fields['count_ip'].choices = choice_ip
        self.fields['count_socket'].choices = choice_socket
        self.fields['count_electro'].choices = choice_electro

    def clean_height_unit(self):
        print 'clean unit = %s' % self.cleaned_data['height_unit']
        tower = True if self.cleaned_data['height_unit'] in ('tower',) else False
        if not tower:
            choice_size = [('1', u'до 60'), ('2', u'до 80'), ('3', u'до 100')]
        else:
            tariff_qs = Tariff.objects.filter(section_type=2, service_type__id=2, tower_casing=True)
            choice_size = []
            for tariff_obj in tariff_qs:
                choice_size.append(('%s' % tariff_obj.id, '%sx%sx%s' % (tariff_obj.width, tariff_obj.height, tariff_obj.depth,)))
        self.fields['size'].choices = choice_size
        return self.cleaned_data['height_unit']

    def clean_inet_channel(self):
        choice_speed = []
        garant = True if self.cleaned_data['inet_channel'] in ('garant',) else False
        tariff_queryset = Tariff.objects.filter(service_type=12, garant=garant).order_by('speed_inet')
        for tariff in tariff_queryset:
            cost = u'%s р.*' % (tariff.price_id.cost / 1.18) if tariff.price_id.cost > 0 else u'беспл.'
            choice_speed.append((tariff.id, u'%s Мбит/с (%s)' % (tariff.speed_inet, cost)))
        self.fields['inet_speed'].choices = choice_speed
        return self.cleaned_data['inet_channel']


class AccountRackForm(forms.Form):
    size_rack = forms.ChoiceField(widget=forms.Select(attrs={'onchange':'change_size_rack(this)'}),)
    depth = forms.ChoiceField(widget=forms.Select(attrs={'onchange':'cost_all_zakaz(this)'}),)
    inet_channel = forms.ChoiceField(widget=forms.Select(attrs={'onchange':'change_channel(this)'}),)
    inet_speed = forms.ChoiceField(widget=forms.Select(attrs={'onchange':'cost_all_zakaz(this)'}),)
    count_ip = forms.ChoiceField(widget=forms.Select(attrs={'onchange':'cost_all_zakaz(this)'}),)
    count_socket = forms.ChoiceField(widget=forms.Select(attrs={'onchange':'cost_all_zakaz(this)'}),)
    count_electro = forms.ChoiceField(widget=forms.Select(attrs={'onchange':'cost_all_zakaz(this)'}),)
    def __init__(self, data=None, *args, **kwargs):
        self.data = data
        super(AccountRackForm, self).__init__(data=data, *args, **kwargs)
        choice_ip, choice_socket, choice_electro, choice_speed = [], [], [], []
#        tariff_size = Tariff.objects.filter(service_type__id=1)
        choice_size = [('1', u'1/1 (42 юнита)'), ('126', u'1/2 (20 юнитов)')]
        choice_depth = [('1', '60 см'), ('2', '80 см'), ('3', '100 см')]
        for i in range(16, 81):
            choice_socket.append((i, i))
        for i in range(10, 51):
            choice_ip.append((i, i))
        for i in range(5000, 21000, 1000):
            choice_electro.append((i, u'%s Вт' % i))
        choice_channel = [('not_garant', u'Не гарантированный'), ('garant', u'Гарантированный')]
        tariff_queryset = Tariff.objects.filter(service_type__id=12, garant=False)
        for tariff in tariff_queryset:
            cost = u'%s руб.*' % (tariff.price_id.cost / 1.18) if tariff.price_id.cost > 0 else u'беспл.'
            choice_speed.append((tariff.id, u'%s Мбит/сек (%s)' % (tariff.speed_inet, cost)))
        self.fields['size_rack'].choices = choice_size
        self.fields['depth'].choices = choice_depth
        self.fields['inet_channel'].choices = choice_channel
        self.fields['inet_speed'].choices = choice_speed
        self.fields['count_ip'].choices = choice_ip
        self.fields['count_socket'].choices = choice_socket
        self.fields['count_electro'].choices = choice_electro

    def clean_size_rack(self):
        print 'clean_size_rack'
        size_rack = self.cleaned_data['size_rack']
        tariff_rack = Tariff.objects.get(id=size_rack)
        max_unit = 42

        max_ip = 50
        choice_ip = []
        for i in range(tariff_rack.ip, max_ip / (max_unit / int(tariff_rack.unit)) + 1):
            choice_ip.append(('%s' % i, '%s' % i))
        self.fields['count_ip'].choices = choice_ip

        max_socket = 80
        choice_socket = []
        for i in range(int(tariff_rack.socket), max_socket / (max_unit / int(tariff_rack.unit)) + 1):
            choice_socket.append(('%s' % i, '%s' % i))
        self.fields['count_socket'].choices = choice_socket

        max_electro = 20000
        choice_electro = []
        step = 1000 if int(tariff_rack.unit) in (42,) else 500
        for i in range(int(tariff_rack.electricity), max_electro / (max_unit / int(tariff_rack.unit)) + step, step):
            choice_electro.append(('%s' % i, u'%s Вт' % i))
        self.fields['count_electro'].choices = choice_electro
        return self.cleaned_data['size_rack']

    def clean_inet_channel(self):
        print 'clean_inet_channel'
        choice_speed = []
        garant = True if self.cleaned_data['inet_channel'] in ('garant',) else False
        tariff_queryset = Tariff.objects.filter(service_type=12, garant=garant).order_by('speed_inet')
        for tariff in tariff_queryset:
            cost = u'%s р.*' % (tariff.price_id.cost / 1.18) if tariff.price_id.cost > 0 else u'беспл.'
            choice_speed.append((tariff.id, u'%s Мбит/с (%s)' % (tariff.speed_inet, cost)))
        self.fields['inet_speed'].choices = choice_speed
        return self.cleaned_data['inet_channel']

