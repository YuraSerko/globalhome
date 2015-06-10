# -*- coding: utf-8 -*-
from django import forms
# from django import models
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_GET
from fs.models import Record_talk, GatewayModel, Queue, Agent, NumberTemplateRule
from settings import BILLING_DB
from django.forms.util import ErrorDict, ErrorList
from django.utils.safestring import mark_safe
from telnumbers.forms import SelectWithAddGroupForm
from account.forms import first_date_last
from widgets import NotClearableFileInput
from django.forms.util import ErrorList
from django.contrib.admin.widgets import FilteredSelectMultiple
from telnumbers.models import TelNumber
from django.contrib.admin.widgets import AdminFileWidget, ManyToManyRawIdWidget
from datetime import datetime
import re


class RecordTalkForm(forms.Form):
    enabled = forms.ChoiceField(
        choices = (("True", "True"), ("False","False")),
        widget = forms.CheckboxInput(),
        label = _(u"Enabled"),
        required = False
    )
    number = forms.ChoiceField(
        choices = (("v1", "v2111"), ("v3", "v4111")),
        label = _(u"На номере"),
        required = True
    )
    record_type = forms.MultipleChoiceField(
        choices = ((1, "Входящие вызовы"), (2, "Исходящие вызовы")),
        widget=forms.CheckboxSelectMultiple(),
        label = _(u"Запись по типу звонка"),
        required = True
    )
    record_time_enabled = forms.ChoiceField(
        choices = (("True", "True"), ("False","False")),
        widget = forms.CheckboxInput(
            #attrs = {"id" : "time_enabled_checkbox" }
            ),
        label = _(u"Specify time of day"),
        required = False
    )
    record_time_begin = forms.TimeField(
        widget = forms.TimeInput(attrs = {"id" : "record_time_begin_field", "value" : '00:00'}),
        label = _(u"Begin time, inclusive"),
        required = False
    )
    record_time_end = forms.TimeField(
        widget = forms.TimeInput(attrs = {"id" : "record_time_end_field", "value" : '23:59'}),
        label = _("End time, not inclusive"),
        required = False
    )
    record_day_enabled = forms.ChoiceField(
        choices = (("True", "True"), ("False","False")),
        widget = forms.CheckboxInput(
            ),
        label = _(u"Указать дни недели для записи"),
        required = False
    )
    record_day = forms.MultipleChoiceField(
        choices = ((1, "Понедельник"), (2, "Вторник"), (3, "Среда"), (4, "Четверг"), (5, "Пятница"), (6, "Суббота"), (7, "Воскресенье")),
        widget=forms.CheckboxSelectMultiple(),
        required = False,
        label = _(u"Выберите дни недели в которые необходимо производить запись разговоров")
    )


    def __init__(self, model = None, data = None, profile = None, request = None, init_number = None):
        super(RecordTalkForm, self).__init__(data = data)
        self.model = model
        self.data = data
        self.profile = profile
        self.request = request
        self.init_error = False
        if model:
            self.fields["enabled"].initial = model.enabled
            self.fields["number"].initial = model.number
            self.fields["record_type"].initial = model.record_type
            if profile:
                numbers = profile.billing_account.phones
                self.fields["number"].choices = []
                for number in numbers:
                    tns = number.tel_number
                    if number.person_name:
                        tns += " (" + number.person_name + ")"
                    self.fields["number"].choices.append( (number.tel_number, tns) )

                if model.number:
                    self.fields["number"].initial = model.number
                    self.from_number_value = model.number
                else:
                    if numbers:
                        if numbers[0]:
                            self.fields["number"].initial = numbers[0].tel_number
                            self.from_number_value = numbers[0].tel_number
                    else:
                        self.request.notifications.add(_("You have no internal numbers. You should create one first"), "warning")
                        self.init_error = True
            if model.record_day_enabled:
                self.fields["record_day_enabled"].initial = True
                self.fields["record_day"].initial = model.record_day
            else:
                self.fields["record_day"].initial = model.record_day
            if model.record_time_enabled:
                self.fields["record_time_enabled"].initial = True
                self.fields["record_time_begin"].initial = model.record_time_begin
                self.fields["record_time_end"].initial = model.record_time_end
            else:
                self.fields["record_time_enabled"].initial = False
                self.fields["record_time_begin"].initial = None
                self.fields["record_time_end"].initial = None

    def _model_from_data(self,  cleaned_data, src_model = None):
        """
            Получаем модель с заполненными полями из очищенных данных
        """
        if src_model:
            model = src_model
        else:
            model = Record_talk()
        # заполняем поля
        if cleaned_data: # если модель была валидирована
            model.enabled = (self.cleaned_data.get("enabled") == "True")
            model.number = self.cleaned_data.get("number")
            model.record_type = self.cleaned_data.get("record_type")

            if cleaned_data.get("record_time_enabled") == "True": # проверяем на переадресацию по времени
                model.record_time_enabled = (self.cleaned_data.get("record_time_enabled") == "True")
                model.record_time_begin = cleaned_data.get("record_time_begin") # сохраняем начальное время
                model.record_time_end = cleaned_data.get("record_time_end") # сохраняем конечное время
            else:                                       # иначе
                model.record_time_enabled = (self.cleaned_data.get("record_time_enabled") == "True")
                model.record_time_begin = None # сбиваем начальное время
                model.record_time_end = None # сбиваем конечное время

            if cleaned_data.get("record_day_enabled") == "True": # проверяем на переадресацию по дню недели
                model.record_day_enabled = (self.cleaned_data.get("record_day_enabled") == "True")
                model.record_day = cleaned_data.get("record_day")
            else: # иначе - отключаем ее
                model.record_day = [u'1',u'2',u'3',u'4',u'5',u'6',u'7']

            return model

    def clean(self):
        cleaned_data = self.cleaned_data

        enabled = (cleaned_data.get("number") == "True")

        number = cleaned_data.get("number")
        if number:
            number = number.strip()

        record_type = cleaned_data.get("record_type")
        record_time_enabled = cleaned_data.get("record_time_enabled")
        record_time_begin = cleaned_data.get("record_time_begin")
        record_time_end = cleaned_data.get("record_time_end")
        record_day_enabled = cleaned_data.get("record_day_enabled")
        if record_type == None:
            self._errors["record_type"] = self.error_class([_(u"Выберите хотя бы один тип вызова.").__unicode__()])

        if record_time_enabled != None:
            if record_time_enabled == u"True":
                # проверяем поля ввода времени
                if record_time_begin == None:
                    self._errors["record_time_begin"] = self.error_class([_(u"Please enter some valid time or disable time block").__unicode__()])
                if record_time_end == None:
                    self._errors["record_time_end"] = self.error_class([_(u"Please enter some valid time or disable time block").__unicode__()])

                if record_time_begin != None and record_time_end != None:
                    if record_time_begin >= record_time_end:
                        self._errors["record_time_end"] = self.error_class([_(u"Введите верный интервал времени или отключите блок уловия времени").__unicode__()])

        if record_day_enabled != None:
            if record_day_enabled == u"True":
                # проверяем коректность ввода дней недели
                # проверяем все чекбоксы, и если все они False - говорим,
                # чтобы пользователь выбрал какие-то дни, или отключил вообще это условие
                if cleaned_data.get("record_day") == []:
                    self._errors["record_day"] = self.error_class([_(u"Выберите хотябы один день недели или отключите блок условия по дню недели").__unicode__()])


        # проверяю на пересекаемость условий времени и дня недели
        model = self._model_from_data(cleaned_data, src_model = self.model)
        if model:
            if model.enabled:
                cross_model = model.GetCrossRecordTalk()
                if cross_model:
                    if self.request:
                        ttt = "return window.open('/account/record_talk/edit/" + str(cross_model.id) + "/','name','height=800,width=800,scrollbars=yes');"
                        #ttt = "return OpenInSmallWindow('/account/record_talk/edit/" + str(cross_model.id) + "/','height=200,width=150,scrollbars=yes');"
                        sttt = _(r'Error! Time of day or days of week is conflicting with <a href="%(link)s" onclick="%(onclick)s">this</a> rule!').__unicode__() % {
                            "link": "#",
                            "onclick": ttt
                        }
                        self.request.notifications.add(
                            mark_safe(sttt),
                            "error"
                        )
                    self.ok_model = None
                else:
                    self.ok_model = model
            else:
                self.ok_model = model
        return cleaned_data


class GatewayForm(SelectWithAddGroupForm):
    enabled = forms.ChoiceField(
        choices = (("True", "True"), ("False","False")),
        widget = forms.CheckboxInput(),
        label = _(u"Enabled"),
        required = False
    )

    sip_address = forms.CharField(
        widget = forms.TextInput( attrs = {"id" : "sip_address"} ),
        label = _("Sip service"),
        required = True
    )
    login = forms.CharField(
        widget = forms.TextInput( attrs = {"id" : "sip_login"} ),
        label = _("Username"),
        required = True
    )
    password = forms.CharField(
        widget=forms.PasswordInput( attrs = {"id" : "sip_password"}, render_value=True ),
        label = _("Password"),
        required = True
    )

    def __init__(self, model = None, data = None, profile = None, request = None, choices = None, settings = None):
        super(GatewayForm, self).__init__(data = data, choices = choices, settings = settings)
        self.model = model
        self.data = data
        self.profile = profile
        self.request = request
        self.init_error = False
        if model:
            self.fields["enabled"].initial = model.enabled
            self.fields["sip_address"].initial = model.sip_address_original
            self.fields["login"].initial = model.login
            self.fields["password"].initial = model.password

class ArticleForm(forms.Form):
    pub_date = forms.IntegerField(
        label = _("Number"),
        required = True
    )

    pub_date_add = forms.IntegerField(
        label = _(u"Добавочный"),
        required = False
    )

from django.forms.widgets import TextInput

class NumberInput(TextInput):
    input_type = 'number'


class Obzvon(forms.Form):
    from_number = forms.ChoiceField(
        choices = (("v1", "v2111"), ("v3", "v4111")),
        label = _("From number"),
        required = True
    )
    filea = forms.FileField(
        label = _(u"Файл для проигрывания"),
        required = False

    )

    file_text = forms.FileField(
        label = _(u"Или выберите файл со списком номеров"),
        required = False
    )

    answer_dtmf = forms.BooleanField(
        label = _(u"Сделать данный обзвон интерактивным"),
        required = False
    )

    answer_ivr = forms.BooleanField(
        label = _(u"Добавить IVR к данному обзвону"),
        required = False
    )

    dtmf_wait_time = forms.CharField(
        widget = forms.TextInput( attrs = {"id" : "dtmf_time_field", "style": "width: 100px;"} ),
        label = _(u"Время ожидания нажатий"),
        required = False
    )

    count_call = forms.ChoiceField(
        choices = (('1', 1), ('2', 2), ('3', 3), ('4', 4), ('5', 5)),
        label = _(u"Количество попыток дозвона"),
        required = True
    )

#    count_call = forms.CharField(
#        widget = NumberInput(attrs = {"id" : "count_call_field", "style": "width: 100px;", 'min': '1', 'max': '5', 'step': '1', 'read_only': 'True'} ),
#        label = _(u"Количество попыток дозвона"),
#        required = False
#    )

    obzvon_time_enabled = forms.ChoiceField(
        choices = (("True", "True"), ("False","False")),
        widget = forms.CheckboxInput(
            #attrs = {"id" : "time_enabled_checkbox" }
            ),
        label = _(u"Specify time of day"),
        required = False
    )

    obzvon_time = forms.TimeField(
        widget = forms.TimeInput(attrs = {"id" : "obzvon_time_field", "value" : '00:00'}),
        label = _(u"Время запуска обзвона"),
        required = False
    )

    obzvon_time_for_one = forms.TimeField(
        widget = forms.TimeInput(attrs = {"id" : "obzvon_time_field", "value" : '00:00'}),
        label = _(u"Время запуска обзвона"),
        required = False
    )

    obzvon_day_enabled = forms.ChoiceField(
        choices = (("True", "True"), ("False","False")),
        widget = forms.CheckboxInput(
            ),
        label = _(u"Указать дни недели для обзвона"),
        required = False
    )

    obzvon_concretic_day_enabled = forms.ChoiceField(
        choices = (("True", "True"), ("False","False")),
        widget = forms.CheckboxInput(
            ),
        label = _(u"Указать конкретный день для обзвона"),
        required = False
    )

    date_to = forms.DateField(
        required=False,
        input_formats=('%d.%m.%Y',),
        # widget=JqCalendar(),
        widget=forms.DateInput(attrs={'class':"datepicker", 'readonly':'readonly'},),
        label=u'Конкретный день:',
        initial=first_date_last().strftime("%d.%m.%Y")
    )

    many_times = forms.ChoiceField(
        choices = (("True", "True"), ("False","False")),
        widget = forms.CheckboxInput(
            ),
        label = _(u"Повторяющийся обзвон"),
        required = False
    )

    one_times = forms.ChoiceField(
        choices = (("True", "True"), ("False","False")),
        widget = forms.CheckboxInput(
            ),
        label = _(u"Отложенный запуск"),
        required = False
    )

    max_min_time_enabled = forms.ChoiceField(
        choices = (("True", "True"), ("False","False")),
        widget = forms.CheckboxInput(
            ),
        label = _(u"Указать время работы обзвона"),
        required = False
    )

    min_time = forms.TimeField(
        widget = forms.TimeInput(attrs = {"id" : "min_time_field", "value" : '00:00'}),
        label = _(u"С"),
        required = False
    )

    max_time = forms.TimeField(
        widget = forms.TimeInput(attrs = {"id" : "max_time_field", "value" : '00:00'}),
        label = _(u"До"),
        required = False
    )


    def __init__(self, model = None, data = None, profile = None, request = None):
        super(Obzvon, self).__init__(data = data)
        self.model = model
        self.data = data
        self.profile = profile
        self.request = request
        self.init_error = False

        # пишем в свои поля значения из модели, если она вообще есть
        if model:
            self.fields["from_number"].initial = model.from_number
            self.fields["filea"].initial = model.file
            self.fields["answer_dtmf"].initial = model.answer_dtmf
            self.fields["answer_ivr"].initial = model.answer_ivr
            self.fields["dtmf_wait_time"].initial = (model.dtmf_wait_time)/1000
            self.fields["count_call"].initial = model.count_call

            self.fields["one_times"].initial = model.one_times
            self.fields["obzvon_time_for_one"].initial = model.obzvon_time_for_one
            if model.date_to:
                self.fields["date_to"].initial = model.date_to.date().strftime("%d.%m.%Y")
            self.fields["many_times"].initial = model.many_times
            self.fields["obzvon_time_enabled"].initial = model.obzvon_time_enabled
            self.fields["obzvon_time"].initial = model.obzvon_time
            self.fields["obzvon_day_enabled"].initial = model.obzvon_day_enabled
            self.fields["obzvon_concretic_day_enabled"].initial = model.obzvon_concretic_day_enabled
            self.fields["max_min_time_enabled"].initial = model.max_min_time_enabled
            self.fields["min_time"].initial = model.min_time
            self.fields["max_time"].initial = model.max_time

            if model.file_text:
                self.fields["file_text"].initial = model.file_text
            # заполняем поле "from_number"
            if profile:
                numbers = profile.billing_account.phones
                self.fields["from_number"].choices = []
                for number in numbers:
                    tns = number.tel_number
                    if number.person_name:
                        tns += " (" + number.person_name + ")"
                    self.fields["from_number"].choices.append( (number.tel_number, tns) )

                if model.from_number:
                    #print 's'
                    self.fields["from_number"].initial = model.from_number
                else:
                    if numbers:
                        if numbers[0]:
                            self.fields["from_number"].initial = numbers[0].tel_number
                    else:
                        self.request.notifications.add(_("You have no internal numbers. You should create one first"), "warning")
                        self.init_error = True
            if request.FILES:
                try:
                    if request.FILES['filea']:
                        self.fields["filea"].initial = request.FILES['filea']
                except Exception, e:
                    print e

                try:
                    if request.FILES['file_text']:
                        self.fields["file_text"].initial = request.FILES['file_text']
                except Exception, e:
                    print e

    def _model_from_data(self,  cleaned_data, src_model = None):
        """
            Получаем модель с заполненными полями из очищенных данных
        """
        if src_model:
            model = src_model
        else:
            model = Obzvon()
        # заполняем поля
        if cleaned_data: # если модель была валидирована
            model.from_number = self.cleaned_data.get("from_number")
            model.file = self.cleaned_data.get("filea")
            model.file_text = self.cleaned_data.get("file_text")
            model.answer_dtmf = self.cleaned_data.get("answer_dtmf")
            model.answer_ivr = self.cleaned_data.get("answer_ivr")
            model.dtmf_wait_time = int(self.cleaned_data.get("dtmf_wait_time"))*1000
            model.count_call = int(self.cleaned_data.get("count_call"))
            print "self.cleaned_data.get(count_call)"
            print int(self.cleaned_data.get("count_call"))
            model.one_times = (self.cleaned_data.get("one_times") == "True")
            model.obzvon_time_for_one = self.cleaned_data.get("obzvon_time_for_one")
            print "self.cleaned_data.get(date_to)"
            print self.cleaned_data.get("date_to")
            model.date_to = self.cleaned_data.get("date_to")
            model.many_times = (self.cleaned_data.get("many_times") == "True")
            model.obzvon_time_enabled = (self.cleaned_data.get("obzvon_time_enabled") == "True")
            model.obzvon_time = self.cleaned_data.get("obzvon_time")
            model.obzvon_day_enabled = (self.cleaned_data.get("obzvon_day_enabled") == "True")
            model.obzvon_concretic_day_enabled = (self.cleaned_data.get("obzvon_concretic_day_enabled") == "True")
            model.max_min_time_enabled = (self.cleaned_data.get("max_min_time_enabled") == "True")
            model.min_time = self.cleaned_data.get("min_time")
            model.max_time = self.cleaned_data.get("max_time")
            return model

    def clean(self):
        cleaned_data = self.cleaned_data
        model = self._model_from_data(cleaned_data, src_model = self.model)
        if model:
            try:
                if cleaned_data.get("filea"):
                    if cleaned_data.get("filea").content_type in ['audio/wav',]:
                        self.ok_model = model
                    else:
                        self.request.notifications.add(
                                    "Ваш файл не подходит. Выберите файл формата .wav",
                                    "error"
                                )
                        self.ok_model = None
                else:
                    if cleaned_data.get("answer_ivr"):
                        self.ok_model = model
                    else:
                        self.request.notifications.add(
                                    "Выберите файл для проигрывания или сделайте обзвон интерактивным c подключением ivr.",
                                    "error"
                                )
                        self.ok_model = None

                if cleaned_data.get("file_text"):
                    if not cleaned_data.get("file_text").content_type in ['text/plain',]:
                        self.request.notifications.add(
                                    "Ваш файл со списком номеров не подходит. Выберите файл формата .txt",
                                    "error"
                                )
                        self.ok_model = None
            except Exception, e:
                print e
                self.ok_model = model
                pass

        return cleaned_data

#asdasdasdasd
class ListNumberDynForm(forms.Form):
    number = forms.IntegerField(
        label = _("Number"),
        required = True
    )

    def __init__(self, *args, **kwargs):
        super(ListNumberDynForm, self).__init__(*args, **kwargs)

class ListNumberForm(forms.Form):
    name = forms.CharField(
        label = _(u"Название списка"),
        required = True
    )


    type_out_in = forms.ChoiceField(
        choices = ((1, "Входящие"), (2, "Исходящие")), # условия переадресации
        widget=forms.RadioSelect(attrs={'onchange':'type_call(this);'}),
        label = _(u"Тип вызова"),
        required = False
    )

    type_out = forms.ChoiceField(
        choices = ((1, "Черный"), (2, "Белый")), # условия переадресации
        widget=forms.RadioSelect(attrs={'onchange':'type_call_pod(this);'}),
        label = _(u"Тип списка для исходящих"),
        required = False
    )

    type_in = forms.ChoiceField(
        choices = ((1, "Черный"), (2, "Белый")), # условия переадресации
        widget=forms.RadioSelect(attrs={'onchange':'type_call_pod(this);'}),
        label = _(u"Тип списка для входящих"),
        required = False
    )

    file_text = forms.FileField(
        label = _(u"Или выберите файл со списком номеров"),
        required = False
    )


    def __init__(self, model = None, data = None, profile = None, request = None, id_type = 1, type_call = 1):
        super(ListNumberForm, self).__init__(data = data)
        self.model = model
        self.data = data
        self.profile = profile
        self.request = request
        self.init_error = False
        # пишем в свои поля значения из модели, если она вообще есть
        if model:
            self.fields["name"].initial = model.name
            try:
                self.fields["type_out_in"].initial = request.GET['call']
            except:
                self.fields["type_out_in"].initial = type_call
                pass
            self.fields["type_out"].initial = id_type
            self.fields["type_in"].initial = id_type
            if request.FILES:
                try:
                    if request.FILES['file_text']:
                        self.fields["file_text"].initial = request.FILES['file_text']
                except Exception, e:
                    print e


    def _model_from_data(self,  cleaned_data, src_model = None):
        """
            Получаем модель с заполненными полями из очищенных данных
        """
        if src_model:
            model = src_model
        else:
            model = TelNumbersList()
        # заполняем поля
        if cleaned_data: # если модель была валидирована
            model.name = self.cleaned_data.get("name")
            model.file_text = self.cleaned_data.get("file_text")
            return model

    def clean(self):
        cleaned_data = self.cleaned_data
        model = self._model_from_data(cleaned_data, src_model = self.model)
        if model:
            try:
                if cleaned_data.get("file_text"):
                    if not cleaned_data.get("file_text").content_type in ['text/plain',]:
                        self.request.notifications.add(
                                    "Ваш файл со списком номеров не подходит. Выберите файл формата .txt",
                                    "error"
                                )
                        self.ok_model = None
                    else:
                        self.ok_model = model
                else:
                    self.ok_model = model
            except Exception, e:
                print e
                self.ok_model = model
                pass
        return cleaned_data
class QueueForm(forms.ModelForm):
    class Meta:
        model = Queue
        fields = ('name', 'hello', 'chime_list', 'hold', 'client_announce', 'record_enabled', 'time_enabled', 'time_begin', 'time_end', 'work_announce', 'say_queue_position', 'chime_freq')

    more_options = forms.ChoiceField(
        choices = (("True", "True"), ("False","False")),
        widget = forms.CheckboxInput(),
        label = _(u"Дополнительные параметры"),
        required = False
    )

    day_enabled = forms.ChoiceField(
        choices = (("True", "True"), ("False","False")),
        widget = forms.CheckboxInput(),
        label = _(u"Указать дни недели"),
        required = False
    )

    work_day = forms.MultipleChoiceField(
            choices = ((1, "Пн"), (2, "Вт"), (3, "Ср"), (4, "Чт"), (5, "Пт"), (6, "Сб"), (7, "Вс")),
            widget = forms.CheckboxSelectMultiple(),
            required = False,
            label = _(u"Выберите дни недели"),
            initial = ['1','2','3','4','5','6','7']
    )

    agents = forms.MultipleChoiceField(
        widget = FilteredSelectMultiple("", is_stacked = False),
        label = u"Операторы очереди"
    )

    def __init__(self, *args, **kwargs):
        super(QueueForm, self).__init__(*args, instance = kwargs.get('instance'))
        self.queue = None
        self.account = kwargs.get('bac').id
        self.fields['agents'].choices = [(a.id, a.get_view_name()) for a in TelNumber.objects.filter(account_id = self.account)]
        if kwargs.get('queue'):
            self.queue = kwargs.get('queue')
            self.fields['hello'].required = False
            self.instance.pk = self.queue.id
        if (self.instance.pk is None):
            self.fields['time_begin'].initial = '09:00'
            self.fields['time_end'].initial = '18:00'
        else:
            self.fields['hello'].required = False
            self.fields['more_options'].initial = not (not self.instance.client_announce and not self.instance.work_announce and not self.instance.chime_list and not self.instance.say_queue_position)
            self.fields['day_enabled'].initial = len(self.instance.work_day) != 7
            self.fields['work_day'].initial = list(self.instance.work_day)
            self.fields['agents'].initial = [a.internal_number_id for a in Agent.objects.filter(queue_id = self.instance.pk)]

    def __get_number_queue(self):
        number = 1
        numbers = [q.number_queue for q in Queue.objects.filter(billing_account_id = self.account)]
        while (number in numbers):
            number += 1
        return number

    def save(self, request = None, commit = True):
        if self.queue:
            if not self.instance.hello:
                self.instance.hello = self.queue.hello
            if self.cleaned_data['hold'] is None:
                self.instance.hold = self.queue.hold
            if self.cleaned_data['chime_list'] is None:
                self.instance.chime_list = self.queue.chime_list
            if self.cleaned_data['client_announce'] is None:
                self.instance.client_announce = self.queue.client_announce
            if self.cleaned_data['work_announce'] is None:
                self.instance.work_announce = self.queue.work_announce
        self.instance.billing_account_id = self.account
        self.instance.created_date = datetime.now()
        if self.cleaned_data['day_enabled'] == 'True':
            self.instance.work_day = ''.join(x for x in self.cleaned_data['work_day'])
        else: self.instance.work_day = '1234567'
        if not self.instance.pk:
            self.instance.number_queue = self.__get_number_queue()
        else: self.instance.number_queue = self.queue.number_queue
        queue = super(QueueForm, self).save(commit=True)
        agents = Agent.objects.filter(queue = queue)
        for intnumber in self.cleaned_data['agents']:
            agent = agents.filter(internal_number_id = intnumber)
            agents = agents.exclude(internal_number_id = intnumber)
            if not (agent and agent[0]):
                agent = Agent(internal_number_id = intnumber, queue = queue, billing_account_id = queue.billing_account_id)
                agent.save()
        for agent in agents:
            agent.delete_from_freeswitch()
        agents.delete()
        return queue

    def clean_name(self):
        if self.queue:
            queues = [q.name for q in Queue.objects.filter(billing_account_id = self.account) if q.name != self.queue.name]
        else: queues = [q.name for q in Queue.objects.filter(billing_account_id = self.account)]
        if self.cleaned_data['name'] in queues:
            raise forms.ValidationError('Такое название очереди уже используется')
        return self.cleaned_data['name']

    def clean_work_day(self):
        if len(self.cleaned_data['work_day']) == 0:
            raise forms.ValidationError('Не выбран ни один день')
        return self.cleaned_data['work_day']

    def clean(self):
        cleaned_data = super(QueueForm, self).clean()
        for file_field in ['hello', 'chime_list', 'hold', 'client_announce', 'work_announce']:
            file = cleaned_data.get(file_field)
            if file and not (file.content_type in ['audio/wav', 'audio/mp3', 'audio/mpeg']):
                self._errors[file_field] = self.error_class([u'Ваш файл не подходит. Выберите файл формата *.wav или *.mp3'])
        if cleaned_data.get('time_begin') >= cleaned_data.get('time_end'):
            self._errors['time_end'] = self.error_class([u'Поле "Конец" должно быть больше поля "Начало"'])
        if cleaned_data.get('chime_freq') < 5:
            self._errors['chime_freq'] = self.error_class([u'Величина интервала должна быть больше 5 секунд'])
        if cleaned_data.get('chime_freq') > 700000000:
            self._errors['chime_freq'] = self.error_class([u'Превышено максимальное значение интервала'])

        return cleaned_data

class NumberDynForm(forms.Form):
    number_dyn = forms.ChoiceField(
        widget = forms.Select(attrs={'type':'comm'}),
        choices = [],
        label = _(u"Внутренний номер"),
        required = True
    )

    def __init__(self, *args, **kwargs):
        numchoices = []
        numchoices.append((0, 'Выберите номер'))
        numbers = kwargs.pop('numbers', None)
        if numbers:
            for num in numbers:
                numchoices.append((num.id, num.get_view_name()))
            self.base_fields["number_dyn"].choices = numchoices
        else:
            self.base_fields["number_dyn"].choices = []

        super(NumberDynForm, self).__init__(*args, **kwargs)

class ExtNumberDynForm(forms.Form):
    extnumber = forms.ChoiceField(
        widget = forms.Select(attrs={'type':'comm'}),
        choices = [],
        label = _(u"Городской номер"),
        required = True
    )

    def __init__(self, *args, **kwargs):
        numchoices = []
        numchoices.append((0, 'Выберите номер'))
        numbers = kwargs.pop('extnumbers', None)
        if numbers:
            for num in numbers:
                numchoices.append((num.id, num.number))
            self.base_fields["extnumber"].choices = numchoices
        else:
            self.base_fields["extnumber"].choices = []

        super(ExtNumberDynForm, self).__init__(*args, **kwargs)


class GroupDynForm(forms.Form):
    group = forms.ChoiceField(
        widget = forms.Select(attrs={'type':'comm'}),
        label = _("Group"),
        required = True
    )

    def __init__(self, *args, **kwargs):
        groupchoices = []
        groupchoices.append((0, 'Выберите группу'))
        existing_groups = kwargs.pop('existing_groups', None)
        if existing_groups:
            for gr in existing_groups:
                groupchoices.append((gr.id, gr.name_with_numbers))

            self.base_fields["group"].choices = groupchoices

        super(GroupDynForm, self).__init__(*args, **kwargs)

class NumberTemplate(forms.Form):
    name_template = forms.CharField(
        label = _(u"Название"),
        required = True
    )
    template = forms.CharField(
        label = mark_safe("""&nbsp;&nbsp;Маска<span class="tooltip">
                            <i></i>
                            <span class="tooltip-i" style="font-size:10px;">Формат правила формата номера:X - любая цифра, []- допустимый диапазон значений, к примеру, [1-6], {} - количество повторений, к примеру, {7} повторений того, что до фигурной скобки, .- завершение анализа номера (могут следовать любые цифры, в любом количестве).Например, 7-ми значный номер может быть определен как XXXXXXX</span>
                        </span>"""),
        required = True
    )
