# -*- coding=utf-8 -*-
from BitFunctions import *
import DateUtils

def HaveAnyDateConditions(date_flags):
    """
        Проверяет, есть ли хоть какие-то временнЫе условия
    """
    if date_flags:
        return True
    return False

def HaveTimeOfDayCondition(date_flags):
    """
        Проверяет, есть ли среди временнЫх условий условие по времени дня
    """
    if GetBit(date_flags, 0):
        return True
    return False

def HaveDayOfWeekCondition(date_flags):
    """
        Проверяет, есть ли среди временнЫх условий условие по дню недели
    """
    if GetBit(date_flags, 1):
        return True
    return False

def HaveDayOfMonthCondition(date_flags):
    """
        Проверяет, есть ли среди временнЫх условий условие по дню месяца (число месяца)
    """
    if GetBit(date_flags, 2):
        return True
    return False

def HaveWeekOfMonthCondition(date_flags):
    """
        Проверяет, есть ли среди временнЫх условий условие по неделе месяца
    """
    if GetBit(date_flags, 3):
        return True
    return False

def HaveWeekOfYearCondition(date_flags):
    """
        Проверяет, есть ли среди временнЫх условий условие по неделе года
    """
    if GetBit(date_flags, 4):
        return True
    return False

def HaveMonthOfYearCondition(date_flags):
    """
        Проверяет, есть ли среди временнЫх условий условие по месяцу года
    """
    if GetBit(date_flags, 0):
        return True
    return False

def SetTimeOfDayCondition(date_flags, new_state):
    """
        Возвращает date_flags, в которых условие по времени дня установлено в new_state
    """
    return SetBit(date_flags, 0, new_state)

def SetDayOfWeekCondition(date_flags, new_state):
    """
        Возвращает date_flags, в которых условие по дню недели установлено в new_state
    """
    return SetBit(date_flags, 1, new_state)

def SetDayOfMonthCondition(date_flags, new_state):
    """
        Возвращает date_flags, в которых условие по дню месяца установлено в new_state
    """
    return SetBit(date_flags, 2, new_state)

def SetWeekOfMonthCondition(date_flags, new_state):
    """
        Возвращает date_flags, в которых условие по неделе месяца установлено в new_state
    """
    return SetBit(date_flags, 3, new_state)

def SetWeekOfYearCondition(date_flags, new_state):
    """
        Возвращает date_flags, в которых условие по неделе года установлено в new_state
    """
    return SetBit(date_flags, 4, new_state)

def SetMonthOfYearCondition(date_flags, new_state):
    """
        Возвращает date_flags, в которых условие по месяцу года установлено в new_state
    """
    return SetBit(date_flags, 5, new_state)

def GetDayOfWeekEnabled(date_day_of_week, day):
    """
        Возвращает True, если в date_day_of_week включен бит дня day
    """
    return GetBit(date_day_of_week, day)

def SetDaysOfWeekEnabled(mon, tue, wed, thu, fri, sat, sun):
    """
        Возвращает date_day_of_week, в корором включены заданные дни
    """
    date_day_of_week = 0
    if mon:
        date_day_of_week = SetBit(date_day_of_week, 1, True)
    if tue:
        date_day_of_week = SetBit(date_day_of_week, 2, True)
    if wed:
        date_day_of_week = SetBit(date_day_of_week, 3, True)
    if thu:
        date_day_of_week = SetBit(date_day_of_week, 4, True)
    if fri:
        date_day_of_week = SetBit(date_day_of_week, 5, True)
    if sat:
        date_day_of_week = SetBit(date_day_of_week, 6, True)
    if sun:
        date_day_of_week = SetBit(date_day_of_week, 7, True)
    return date_day_of_week

# =================================================================================
# === Проверка, соответствует ли указанное временное условие указанному времени ===
# =================================================================================
def CheckDateTimeConditions(test_datetime, date_flags, date_time_begin, date_time_end, date_day_of_week):
    """
        Проверяет все включенные условия времени
    """
    if HaveTimeOfDayCondition(date_flags): # если есть условие времени дня
        time = test_datetime.time() # получаем время дня для проверки
        if not (time >= date_time_begin and time < date_time_end): # если это время не входит в заданный интервал
            return False # сразу выходим и возвращаем False

    if HaveDayOfWeekCondition(date_flags): # если есть условие дня недели
        day = DateUtils.GetDayOfWeek(test_datetime) # получить день недели для проверки
        if not GetDayOfWeekEnabled(date_day_of_week, day): # если день недели не потходит
            return False # сразу выходим и возвращаем False

    return True # если дошли досюда - значит все условия успешно пройдены, потому можно вернуть True

def IsNeedForwarding(what_time, date_flags, date_time_begin, date_time_end, date_day_of_week):
    """
        Передаешь этой функции текущее время как datetime.now() и остальные параметры запроса и она выдает True,
        если надо делать переадресацию
    """
    if HaveAnyDateConditions(date_flags):
        return CheckDateTimeConditions(what_time, date_flags, date_time_begin, date_time_end, date_day_of_week)
    else:
        return True




