# -*- coding=utf-8 -*-
# $Id: models.py 241 2010-11-24 12:06:52Z HasK $
from django.db import models
from ConditionCheckFunctions import *
from DateUtils import *
from django.utils.translation import ugettext_lazy as _
from telnumbers.models import TelNumber
from settings import BILLING_DB

class Rule(models.Model):
    """
        Это модель для представления правила переадресации звонка
    """
    billing_account_id = models.IntegerField()
    enabled = models.BooleanField(default=True)  # включено ли данное правило

    # priority = models.IntegerField(default = 0) # приоритет правила

    from_number = models.CharField(max_length=255, default='')  # с какого номера будет переадресация
    to_number = models.CharField(max_length=255, default='')  # на этот номер будет переадресация

    # is_conditional_forwarding = models.BooleanField(default = False)

    date_flags = models.IntegerField(default=0)  # Битовые флаги условий по времени

    date_time_begin = models.TimeField(null=True)  # Начальное время интервала времени дня
    date_time_end = models.TimeField(null=True)  # Конечное время интервала времени дня

    date_day_of_week = models.IntegerField(default=0)  # Битовые флаги дней недели
    date_day_of_month = models.IntegerField(default=0)  # Битовые флаги дней в месяце
    date_week_of_month = models.IntegerField(default=0)  # Битовые флаги недель в месяце (4 недели в месяце)
    date_week_of_year = models.BigIntegerField(default=0)  # Битовые флаги недель в году (52 недель в году)
    date_month = models.IntegerField(default=0)  # Битовые флаги месяца


    busy_flags = models.CharField(max_length=255, default='')  # Битовые флаги условий для условия по факту занятости
    busy_wait_time = models.IntegerField(default=60000)  # Сколько секунд ждать ответа, прежде чем фрисвич решит, что пользователь "не поднял трубку"

    class Meta:
        db_table = "call_forwarding_rules"
        ordering = ['from_number', 'to_number']

    def save(self, using=BILLING_DB):
        if using:
            super(Rule, self).save(using=using)
        else:
            super(Rule, self).save()
        # и записать еще в tel_numbers что есть переадресация
        num = TelNumber.objects.using(using).get(tel_number=self.from_number)
        num.has_forwarding = True
        if using:
            num.save(using=using)
        else:
            num.save()

    def delete(self, using=BILLING_DB):
        rules = Rule.objects.using(using).filter(from_number=self.from_number)
        if rules:
            if len(rules) <= 1:
                num = TelNumber.objects.using(using).get(tel_number=self.from_number)
                num.has_forwarding = False
                num.save(using=using)
        super(Rule, self).delete()

    def HaveAnyDateConditions(self):
        """
            Проверяет, есть ли хоть какие-то временнЫе условия
        """
        return HaveAnyDateConditions(self.date_flags)

    def HaveTimeOfDayCondition(self):
        """
            Проверяет, есть ли среди временнЫх условий условие по времени дня
        """
        return HaveTimeOfDayCondition(self.date_flags)

    def GetDayOfWeekEnabled(self, day):
        """
            Возвращает True, если в date_day_of_week включен бит дня day
        """
        return GetDayOfWeekEnabled(self.date_day_of_week, day)

    def HaveDayOfWeekCondition(self):
        """
            Проверяет, есть ли среди временнЫх условий условие по дню недели
        """
        return HaveDayOfWeekCondition(self.date_flags)

    def HaveDayOfMonthCondition(self):
        """
            Проверяет, есть ли среди временнЫх условий условие по дню месяца (число месяца)
        """
        return HaveDayOfMonthCondition(self.date_flags)

    def HaveWeekOfMonthCondition(self):
        """
            Проверяет, есть ли среди временнЫх условий условие по неделе месяца
        """
        return HaveWeekOfMonthCondition(self.date_flags)

    def HaveWeekOfYearCondition(self):
        """
            Проверяет, есть ли среди временнЫх условий условие по неделе года
        """
        return HaveWeekOfYearCondition(self.date_flags)

    def HaveMonthOfYearCondition(self):
        """
            Проверяет, есть ли среди временнЫх условий условие по месяцу года
        """
        return HaveMonthOfYearCondition(self.date_flags)

    def SetTimeOfDayCondition(self, new_state):
        """
            Меняет date_flags так, что условие по времени дня установлено в new_state
        """
        self.date_flags = SetTimeOfDayCondition(self.date_flags, new_state)

    def SetDayOfWeekCondition(self, new_state):
        """
            Меняет date_flags так, что условие по дню недели установлено в new_state
        """
        self.date_flags = SetDayOfWeekCondition(self.date_flags, new_state)

    def SetDaysOfWeekEnabled(self, mon, tue, wed, thu, fri, sat, sun):
        """
            Возвращает date_day_of_week, в корором включены заданные дни
        """
        self.date_day_of_week = SetDaysOfWeekEnabled(mon, tue, wed, thu, fri, sat, sun)

    def SetDayOfMonthCondition(self, new_state):
        """
            Меняет date_flags так, что условие по дню месяца установлено в new_state
        """
        self.date_flags = SetDayOfMonthCondition(self.date_flags, new_state)

    def SetWeekOfMonthCondition(self, new_state):
        """
            Меняет date_flags так, что условие по неделе месяца установлено в new_state
        """
        self.date_flags = SetWeekOfMonthCondition(self.date_flags, new_state)

    def SetWeekOfYearCondition(self, new_state):
        """
            Меняет date_flags так, что условие по неделе года установлено в new_state
        """
        self.date_flags = SetWeekOfYearCondition(self.date_flags, new_state)

    def SetMonthOfYearCondition(self, new_state):
        """
            Меняет date_flags так, что условие по месяцу года установлено в new_state
        """
        self.date_flags = SetMonthOfYearCondition(self.date_flags, new_state)

# admin.site.register(CallForwardingRule)
    def HaveBusyText(self):
        busy_dict = {'0': 'Нету', '1': 'Безусловная', '2': 'Занято', '3': 'Не доступен', '4': 'Нет ответа'}
        finish = []
        busy = eval(self.busy_flags)
        for item in busy:
            if busy_dict.has_key(item):
                finish.append(busy_dict[item])

        return ", ".join(finish)

    def DayStr(self, i, isShort):
        if isShort:
            if i == 1:
                return _(u"Mon").__unicode__()
            elif i == 2:
                return _(u"Tue").__unicode__()
            elif i == 3:
                return _(u"Wed").__unicode__()
            elif i == 4:
                return _(u"Thu").__unicode__()
            elif i == 5:
                return _(u"Fri").__unicode__()
            elif i == 6:
                return _(u"Sat").__unicode__()
            elif i == 7:
                return _(u"Sun").__unicode__()
        else:
            if i == 1:
                return _(u"Monday").__unicode__()
            elif i == 2:
                return _(u"Tuensday").__unicode__()
            elif i == 3:
                return _(u"Wednesday").__unicode__()
            elif i == 4:
                return _(u"Thursday").__unicode__()
            elif i == 5:
                return _(u"Friday").__unicode__()
            elif i == 6:
                return _(u"Saturday").__unicode__()
            elif i == 7:
                return _(u"Sunday").__unicode__()
        return "???"


    def GetConditionStr(self):
        if self.HaveAnyDateConditions():  # если есть условие по времени
            result = u""
            if self.HaveTimeOfDayCondition():  # если есть условие по времени дня
                result = str(self.date_time_begin)
                if self.date_time_begin.second == 0:
                    result = result[0:-3]
                result += u" - " + str(self.date_time_end)
                if self.date_time_end.second == 0:
                    result = result[0:-3]

            if result:
                result += u", "

            if self.HaveDayOfWeekCondition():  # прикрепляем строку про день недели
                """
                теперь тут надо найти все группы в 3 дня и больше и их указывать надо будет через "-"
                код, конечно, уродлив, но он работает, и более-менее наглядно
                там где в списке days встречаются 2 - надо пропустить и ставить дефис между днями недели
                """

                have_false = False
                days = [0, ]
                for i in range(1, 8):
                    n = int(self.GetDayOfWeekEnabled(i))
                    if n == 0:
                        have_false = True
                    days += [n, ]

                if have_false:
                    days += [0, ]


                    for i in range(1, 8):
                        cur = days[i]
                        pred = days[i - 1]
                        next = days[i + 1]

                        if cur != 0 and pred != 0:
                            days[i] = 2

                        if cur == 1 and next == 0:
                            days[i] = 1

                    # print days
                    res = u""
                    for i in range(1, 8):
                        cur = days[i]
                        pred = days[i - 1]
                        next = days[i + 1]

                        if cur == 1:
                            if pred == 0:  # начало интервала
                                if res:
                                    res += u", "
                                res += self.DayStr(i, True)

                            if pred == 1:
                                if res:
                                    res += u", "
                                res += self.DayStr(i, True)

                            if pred == 2:  # конец интервала
                                res += u"-" + self.DayStr(i, True)

                    result += res
                else:
                    result += _(u"Every day").__unicode__()
            else:
                result += _(u"Every day").__unicode__()

            return result
        else:
            return _(u"Always")

    def GetDaysOfWeek(self):
        if self.HaveDayOfWeekCondition():
            days = []
            for i in range(1, 8):
                days += [self.GetDayOfWeekEnabled(i)]
            return days

    def GetCrossConditionsModel(self, using=BILLING_DB, models=None):
        """
            Получаем модель, с которой по условиям пересекается данная или вернем None
        """

        # !!!!!!!!!!!!!!!!!!!!!!! вообще надо бы переписать по крайней мере этот метод

        test = self
        if models == None:
            models = Rule.objects.using(using).filter(from_number=test.from_number, enabled=True)


        # print models

        test_t = test.HaveTimeOfDayCondition()
        test_t1 = test.date_time_begin
        test_t2 = test.date_time_end
        test_d = test.HaveDayOfWeekCondition()
        test_bus = test.busy_flags
        if test_d:
            test_days = test.GetDaysOfWeek()
        else:
            test_days = [True, True, True, True, True, True, True]

        for model in models:
            # сначала проверим совпадение дней недели
            if model.id != test.id:
                if model.enabled:
                    if model.HaveDayOfWeekCondition():  # если и у текущей модели есть условие дня недели
                        model_days = model.GetDaysOfWeek()  # получаем включенные дни недели
                    else:  # у текущей модели нету условия дня недели, значит считаем, что все дни включены
                        model_days = [True, True, True, True, True, True, True]  # включаем все дни недели

                    if IsCrossDays(test_days, model_days):
                        # print "dadadadadad1" + test_bus +"kakak"
                        print "viv" + str(model.busy_flags) + "viv"
                        if IsCrossBusy(test_bus, model.busy_flags):
                            print "adadadadadad2"
                        # если есть пересечения в днях недели

                        # надо проверить совпадение времени суток
                            if test_t and model.HaveTimeOfDayCondition():  # если есть условие времени и там и там, то
                                if IsCrossTimes(test_t1, test_t2, model.date_time_begin, model.date_time_end):
                                    return model
                            else:  # если условия времени нету ни у того, ни у того
                                return model  # тогда их временные интервалы точно пересекаются, раз пересекаются еще и дни недели

    def __unicode__(self):
        """
            Переводит правило в строку
        """
        '''
        str2 = "id: " + str(self.id) + ", \n" + \
            "from_number: " + str(self.from_number) + ", \n" + \
            "to_number: " + str(self.to_number) + ", \n" + \
            "date_flags: " + str(self.date_flags) + ", \n" + \
            "date_time_begin: " + str(self.date_time_begin) + ", \n" + \
            "date_time_end: " + str(self.date_time_begin) + ", \n" + \
            "date_day_of_week: " + str(self.date_day_of_week) + ", \n" + \
            "GetConditionStr: " + (unicode(self.GetConditionStr())) + "\n"
        '''
        str2 = "id: " + str(self.id) + " from_number: " + str(self.from_number) + " to_number: " + str(self.to_number)
        return str2
