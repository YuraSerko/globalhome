# coding: utf-8
# from django.utils.translation import ugettext_lazy as _
from content.TemplateVars import Variable, VarValue
from datetime import datetime
from dateutil.relativedelta import relativedelta  # @UnresolvedImport

def GetVariables():
    month_texts1 = (u"Январь", u"Февраль", u"Март", u"Апрель", u"Май", u"Июнь", u"Июль", u"Август",
        u"Сентябрь", u"Октябрь", u"Ноябрь", u"Декабрь")

    month_texts2 = (u"Января", u"Февраля", u"Марта", u"Апреля", u"Мая", u"Июня", u"Июля", u"Августа",
        u"Сентября", u"Октября", u"Ноября", u"Декабря")

    class DateVarValue(VarValue):
        def getValue(self):
            self.request = self.init_kwargs.get("request")

            value = self.args[0]

            if value:
                now = datetime.now()
                if   value == "datetime_now":
                    return now.strftime("%d.%m.%Y %H:%M:%S")
                elif value == "now_date":
                    # return now.date()
                    return now.strftime("%d.%m.%Y")
                elif value == "now_time":
                    return now.time()
                elif value == "date_str":
                    return now.strftime("%d.%m.%Y")
                elif value == "time_str":
                    return now.strftime("%H:%M:%S")
                elif value == "date_day":
                    return now.day
                elif value == "date_month_num":
                    return now.month
                elif value == "date_month_text1":
                    return month_texts1[now.month - 1]
                elif value == "date_month_text2":
                    return month_texts2[now.month - 1]
                elif value == "date_year":
                    return now.year
                elif value == "date_application":
                    return now.date()
                elif value == "first_day_of_the_next_month":
                    next_month = now + relativedelta(months=1)
                    date_start_next_month_temp = datetime(next_month.year, next_month.month, 1)
                    date_start_next_month = datetime.strftime(date_start_next_month_temp, "%d.%m.%Y")
                    return date_start_next_month
            else:
                return "<kwargs.get('value') is None!>"




    result = [
        Variable(
            "date_datetime_now",
            "Возвращает текущую дату и время (2011-02-03 13:37:31)",
            DateVarValue("datetime_now")
        ),
        Variable(
            "date_now_date",
            "Возвращает текущую дату (2011-02-03)",
            DateVarValue("now_date")
        ),
        Variable(
            "date_now_date_str",
            "Возвращает текущую дату в виде  28.03.2011",
            DateVarValue("date_str")
        ),
        Variable(
            "date_now_time",
            "Возвращает текущее время с микросекундами (13:38:06.062000)",
            DateVarValue("now_time")
        ),
        Variable(
            "date_now_time_str",
            "Возвращает текущее время в виде 13:32:54",
            DateVarValue("date_str")
        ),
        Variable(
            "date_day",
            "Возвращает номер дня месяца (сегодняшнее число)",
            DateVarValue("date_day")
        ),
        Variable(
            "date_month_num",
            "Возвращает номер текущего месяца",
            DateVarValue("date_month_num")
        ),
        Variable(
            "date_month_text1",
            "Возвращает название текущего месяца в форме 'Январь'",
            DateVarValue("date_month_text1")
        ),
        Variable(
            "date_month_text2",
            "Возвращает название текущего месяца в форме 'Января'",
            DateVarValue("date_month_text2")
        ),
        Variable(
            "date_year",
            "Возвращает номер текущего года",
            DateVarValue("date_year")
        ),
        Variable(
            "first_day_of_the_next_month",
            "Возвращает дату (первое число следующего месяца)",
            DateVarValue("first_day_of_the_next_month")
        ),

    ]

    return result





