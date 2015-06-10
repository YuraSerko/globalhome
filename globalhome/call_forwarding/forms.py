# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_GET
from models import Rule
from settings import BILLING_DB
from django.forms.util import ErrorDict, ErrorList
from django.utils.safestring import mark_safe

def StrToBool(value):
    if str(value) == "True":
        return True
    else:
        return False

def OnOrFalse(value):
    if value == True:
        return "True"
    else:
        return "False"

def get_phones(billing_account):

    pass

class RuleEditForm(forms.Form):
    enabled = forms.ChoiceField(
        choices = (("True", "True"), ("False","False")), # тут надо on для того, чтобы форма проходила валидацию.
        widget = forms.CheckboxInput(
            #attrs = {"id" : "time_enabled_checkbox" }
            ),
        label = _(u"Enabled"),
        required = False
    )
    from_number = forms.ChoiceField(
        choices = (("v1", "v2111"), ("v3", "v4111")), # левые значения для дебага, всмысле, если я их вижу - значит что-то не так
        label = _("From number"),
        required = False
    )
    #1111111111111111111111111111
    busy_flags = forms.MultipleChoiceField(
        choices = ((1, "Безусловная"), (2, "Занято"), (3, "Не доступен"), (4, "Не отвечает")), # условия переадресации
        widget=forms.CheckboxSelectMultiple(),
        label = _("Type forward"),
        required = False
    )
    to_number = forms.CharField(
        widget = forms.TextInput( attrs = {"id" : "to_number_field"} ),
        label = _("To number"),
        required = True
    )
    busy_wait_time = forms.CharField(
        widget = forms.TextInput( attrs = {"id" : "busy_time_field"} ),
        label = _(u"Wait time before forwarding"),
        required = False
    )
    time_enabled = forms.ChoiceField(
        choices = (("True", "True"), ("False","False")), # тут надо on для того, чтобы форма проходила валидацию.
        widget = forms.CheckboxInput(
            #attrs = {"id" : "time_enabled_checkbox" }
            ),
        label = _(u"Specify time of day"),
        required = False
    )
    date_time_begin = forms.TimeField(
        widget = forms.TimeInput(attrs = {"id" : "date_time_begin_field"}),
        label = _(u"Начало, включительно. Пример: 10:00"),
        required = False
    )
    date_time_end = forms.TimeField(
        widget = forms.TimeInput(attrs = {"id" : "date_time_end_field"}),
        label = _(u"Конец, не включительно. Пример: 11:00"),
        required = False
    )
    dayofweek_enabled = forms.ChoiceField(
        choices = (("True", "True"), ("False","False")), # тут надо on для того, чтобы форма проходила валидацию.
        widget = forms.CheckboxInput(
            #attrs = {"id" : "dayofweek_enabled_checkbox" }
            ),
        label = _(u"Specify day of week"),
        required = False
    )
    # ***********************************************
    # дни недели
    dayofweek_monday = forms.ChoiceField(
        choices = (("True", "True"), ("False","False")), # тут надо on для того, чтобы форма проходила валидацию.
        widget = forms.CheckboxInput(attrs = {"id" : "dayofweek_monday" }),
        required = False
    )
    dayofweek_tuesday = forms.ChoiceField(
        choices = (("True", "True"), ("False", "False")), # тут надо on для того, чтобы форма проходила валидацию.
        widget = forms.CheckboxInput(attrs = {"id" : "dayofweek_tuesday" }),
        required = False
    )
    dayofweek_wednesday = forms.ChoiceField(
        choices = (("True", "True"), ("False","False")), # тут надо on для того, чтобы форма проходила валидацию.
        widget = forms.CheckboxInput(attrs = {"id" : "dayofweek_wednesday" }),
        required = False
    )
    dayofweek_thursday = forms.ChoiceField(
        choices = (("True", "True"), ("False","False")), # тут надо on для того, чтобы форма проходила валидацию.
        widget = forms.CheckboxInput(attrs = {"id" : "dayofweek_thursday" }),
       required = False
    )
    dayofweek_friday = forms.ChoiceField(
        choices = (("True", "True"), ("False","False")), # тут надо on для того, чтобы форма проходила валидацию.
        widget = forms.CheckboxInput(attrs = {"id" : "dayofweek_friday" }),
        required = False
    )
    dayofweek_saturday = forms.ChoiceField(
        choices = (("True", "True"), ("False","False")), # тут надо on для того, чтобы форма проходила валидацию.
        widget = forms.CheckboxInput(attrs = {"id" : "dayofweek_saturday" }),
        required = False
    )
    dayofweek_sunday = forms.ChoiceField(
        choices = (("True", "True"), ("False","False")), # тут надо on для того, чтобы форма проходила валидацию.
        widget = forms.CheckboxInput(attrs = {"id" : "dayofweek_sunday" }),
        required = False
    )
    # ***********************************************



    def __init__(self, model = None, data = None, profile = None, request = None):
        super(RuleEditForm, self).__init__(data = data)
        self.model = model
        self.data = data
        self.profile = profile
        self.request = request
        self.init_error = False

        # пишем в свои поля значения из модели, если она вообще есть
        if model:
            self.fields["enabled"].initial = model.enabled
            self.fields["from_number"].initial = model.from_number
            self.fields["busy_flags"].initial = model.busy_flags

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
                    self.fields["from_number"].initial = model.from_number
                    self.from_number_value = model.from_number
                else:
                    if numbers:
                        if numbers[0]:
                            self.fields["from_number"].initial = numbers[0].tel_number
                            self.from_number_value = numbers[0].tel_number
                    else:
                        self.request.notifications.add(_("You have no internal numbers. You should create one first"), "warning")
                        self.init_error = True



            self.fields["to_number"].initial = model.to_number
            self.fields["busy_wait_time"].initial = (model.busy_wait_time)/1000

            # перебираем все вмереннЫе параметры и заполняем их
            if model.HaveTimeOfDayCondition():
                self.fields["time_enabled"].initial = True
                self.fields["date_time_begin"].initial = model.date_time_begin
                self.fields["date_time_end"].initial = model.date_time_end
            else:
                self.fields["time_enabled"].initial = False
                self.fields["date_time_begin"].initial = None
                self.fields["date_time_end"].initial = None

            # перебираем параметры дня недели
            if model.HaveDayOfWeekCondition():
                self.fields["dayofweek_enabled"].initial = True

                self.fields["dayofweek_monday"].initial = model.GetDayOfWeekEnabled(1)
                self.fields["dayofweek_tuesday"].initial = (model.GetDayOfWeekEnabled(2))
                self.fields["dayofweek_wednesday"].initial = (model.GetDayOfWeekEnabled(3))
                self.fields["dayofweek_thursday"].initial = (model.GetDayOfWeekEnabled(4))
                self.fields["dayofweek_friday"].initial = (model.GetDayOfWeekEnabled(5))
                self.fields["dayofweek_saturday"].initial = (model.GetDayOfWeekEnabled(6))
                self.fields["dayofweek_sunday"].initial = (model.GetDayOfWeekEnabled(7))
            else:
                self.fields["dayofweek_enabled"].initial = False

                self.fields["dayofweek_monday"].initial = False
                self.fields["dayofweek_tuesday"].initial = False
                self.fields["dayofweek_wednesday"].initial = False
                self.fields["dayofweek_thursday"].initial = False
                self.fields["dayofweek_friday"].initial = False
                self.fields["dayofweek_saturday"].initial = False
                self.fields["dayofweek_sunday"].initial = False

    def _model_from_data(self,  cleaned_data, src_model = None):
        """
            Получаем модель с заполненными полями из очищенных данных
        """
        if src_model:
            model = src_model
        else:
            model = Rule()
        # заполняем поля
        if cleaned_data: # если модель была валидирована
            model.enabled = (self.cleaned_data.get("enabled") == "True")


            model.from_number = self.cleaned_data.get("from_number")
            model.to_number = self.cleaned_data.get("to_number")
            model.busy_flags = self.cleaned_data.get("busy_flags")
            model.busy_wait_time = int(self.cleaned_data.get("busy_wait_time"))*1000

            if cleaned_data.get("time_enabled") == "True": # проверяем на переадресацию по времени
                model.SetTimeOfDayCondition(True) # Сохраняем в модель тот факт, что у нас переадресация по времени суток
                model.date_time_begin = cleaned_data.get("date_time_begin") # сохраняем начальное время
                model.date_time_end = cleaned_data.get("date_time_end") # сохраняем конечное время
            else:                                       # иначе
                model.SetTimeOfDayCondition(False) # Сохраняем в модель тот факт, что у нас нет переадресации по времени суток
                model.date_time_begin = None # сбиваем начальное время
                model.date_time_end = None # сбиваем конечное время

            if cleaned_data.get("dayofweek_enabled") == "True": # проверяем на переадресацию по дню недели
                model.SetDayOfWeekCondition(True)
                model.SetDaysOfWeekEnabled(
                    StrToBool(cleaned_data.get("dayofweek_monday")),
                    StrToBool(cleaned_data.get("dayofweek_tuesday")),
                    StrToBool(cleaned_data.get("dayofweek_wednesday")),
                    StrToBool(cleaned_data.get("dayofweek_thursday")),
                    StrToBool(cleaned_data.get("dayofweek_friday")),
                    StrToBool(cleaned_data.get("dayofweek_saturday")),
                    StrToBool(cleaned_data.get("dayofweek_sunday"))
                )
            else: # иначе - отключаем ее
                model.SetDayOfWeekCondition(False)
                model.SetDaysOfWeekEnabled(
                    False,
                    False,
                    False,
                    False,
                    False,
                    False,
                    False
                )


            return model

    def clean(self):
        cleaned_data = self.cleaned_data

        enabled = (cleaned_data.get("to_number") == "True")
        from_number = cleaned_data.get("from_number")

        to_number = cleaned_data.get("to_number")
        if to_number:
            to_number = to_number.strip()

        time_enabled = cleaned_data.get("time_enabled")
        date_time_begin = cleaned_data.get("date_time_begin")
        date_time_end = cleaned_data.get("date_time_end")
        dayofweek_enabled = cleaned_data.get("dayofweek_enabled")

        if to_number:
            if to_number == from_number:
                self._errors["to_number"] = self.error_class([_(u"Please enter another number!").__unicode__()])

        if time_enabled != None:
            if time_enabled == u"True":
                # проверяем поля ввода времени
                if date_time_begin == None:
                    self._errors["date_time_begin"] = self.error_class([_(u"Please enter some valid time or disable time block").__unicode__()])
                if date_time_end == None:
                    self._errors["date_time_end"] = self.error_class([_(u"Please enter some valid time or disable time block").__unicode__()])

                if date_time_begin != None and date_time_end != None:
                    if date_time_begin >= date_time_end:
                        self._errors["date_time_end"] = self.error_class([_(u"Please enter some valid time interval or disable time block").__unicode__()])

        if dayofweek_enabled != None:
            if dayofweek_enabled == u"True":
                # проверяем коректность ввода дней недели

                # проверяем все чекбоксы, и если все они False - говорим,
                # чтобы пользователь выбрал какие-то дни, или отключил вообще это условие
                if \
                    cleaned_data.get("dayofweek_monday") == \
                    cleaned_data.get("dayofweek_tuesday") == \
                    cleaned_data.get("dayofweek_wednesday") == \
                    cleaned_data.get("dayofweek_thursday") == \
                    cleaned_data.get("dayofweek_friday") == \
                    cleaned_data.get("dayofweek_saturday") == \
                    cleaned_data.get("dayofweek_sunday") == u"False":
                    self._errors["dayofweek_enabled"] = self.error_class([_(u"Please select some days of the week or disable this block").__unicode__()])

        # проверяю на пересекаемость условий времени и дня недели
        model = self._model_from_data(cleaned_data, src_model = self.model)
        if model:
            if model.enabled:
                cross_model = model.GetCrossConditionsModel()
                if cross_model:
                    if self.request:
                        ttt = "return OpenInSmallWindow('/account/call_forwarding/edit_rule/" + str(cross_model.id) + "/');"
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

#  ==================================================================================
#  ==================================================================================
#  ==================================================================================
#  ==================================================================================

class RulesListForm(forms.Form):

    def __init__(self, rules = None, request = None):
        self.rules = rules
        self.request = request
        self.enabled_prefix="enabled_"

        self.changes = {}

        if request and rules:
            if request.POST:
                for rule in rules:
                    val = request.POST.get(self.enabled_prefix + str(rule.id)) == "on"
                    if val != rule.enabled:
                        # нашли изменение
                        self.changes[rule] = val

        self.cross_errors = []
        self.cross_warnings = []


    def check_cross_ok(self, using = BILLING_DB):
        """
            Проверяет, что при включении какого-то правила не происходит конфликт правил
        """

        # перебрать изменения
        # для каждого:
        #    если это включение - проверить его на конфликты и включить, если норм
        #    если это выключение - просто выключить

        ###############
        # неет! просто провести все изменения, потом проверить на пересечения, и если они есть - просто отменить все действия и сообщить об ошибке
        ###############

        # внедряем все изменения
        for rule in self.changes.keys():
            rule.enabled = self.changes.get(rule)

        # теперь надо взять все правила из базы и те, что тут есть заменить на те, что есть
        models = []
        for rule in self.changes.keys():
            models += Rule.objects.using(using).filter(from_number = rule.from_number, enabled = True)

        for i in range(len(models)):
            for rule in self.changes.keys():
                if models[i].id == rule.id:
                    models[i] = rule
                    break

        ok = True





        for rule in self.changes.keys():
            if rule.enabled:
                models2 = models[:]
                cnt = True
                while cnt:
                    conflict = rule.GetCrossConditionsModel(models = models2)
                    if conflict:
                        self.cross_errors += [conflict]
                        self.cross_warnings += [rule]

                        models2.remove(conflict)

                        ok = False
                    else:
                        cnt = False

        if not ok:
            errstr = _(u"This changes conflicts with existing rules!").__unicode__()
            self.request.notifications.add( errstr , "error")

        return ok


        '''
        errors = {}
        ok = True
        for rule in self.rules:
        #    if rule.enabled:
                conflict = rule.GetCrossConditionsModel()
                if conflict:
                    #print u"\n--- CONFLICT " + rule.__unicode__() + u"\n --- AND " + conflict.__unicode__()
                    errors[rule] = conflict
                    rule.had_change = False
                    ok = False
                else:
                    checked = (self.request.POST.get(self.enabled_prefix + str(rule.id)) == "True")
                    if bool(checked) != rule.enabled:
                        rule.had_change = True
                        rule.enabled = bool(checked)
                    else:
                        rule.had_change = False
        #    else:
        #        rule.had_change = False

        if not ok:
            errstr = u""
            for r in errors.keys():
                c = errors[r]
                s = _(u'<a href="#" onclick=\'{Link1}\'>This</a> rule conflicts with <a href="#" onclick=\'{Link2}\'>this</a> rule!<br>')
                s = s.format(
                    Link1 = 'return OpenInSmallWindow("/account/call_forwarding/edit_rule/' + str(r.id) + '/");',
                    Link2 = 'return OpenInSmallWindow("/account/call_forwarding/edit_rule/' + str(c.id) + '/");'
                )
                errstr += s

            self.request.notifications.add( errstr , "error")
        '''
        return ok

    def get_changed_rules(self):
        """
            Возвращает правила, которые изменились
        """
        for rule in self.changes.keys():
            rule.enabled = self.changes[rule]
        return self.rules


