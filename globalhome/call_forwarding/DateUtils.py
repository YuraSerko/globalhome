# -*- coding=utf-8 -*-
"""
    Функции для отпределения дополнителной информации о дате.
    У всех функций первый параметр - datetime (from datetime import datetime)
"""
def GetDayOfWeek(time):
    """
        Определяет номер дня недели
    """
    return time.isoweekday()

def GetDayOfMonth(time):
    """
        Определяет номер дня месяца
    """
    return time.day

def GetWeekOfMonth(time):
    """
        Определяет номер недели месяца
    """
    pn = datetime(time.year, time.month, 1).isoweekday()
    days = time.day + pn - 2
    return ((days / 7) + 1)

def GetWeekOfYear(time):
    """
        Определяет номер недели года
    """
    t1 = datetime(time.year, 1, 1)
    delta = time - t1
    days = delta.days + datetime(time.year, 1, 1).isoweekday() - 1
    return (int(days / 7) + 1)

def GetMonth(time):
    """
        Определяет номер месяца
    """
    return time.month

def IsCrossTimes(time1_begin, time1_end, time2_begin, time2_end):
    if time1_begin <= time2_begin < time1_end:
        return True
    if time2_begin <= time1_begin < time2_end:
        return True
    return False

def IsCrossDays(days1, days2):
    for i, day in enumerate(days1):
        if day == days2[i] == True:
            return True
    return False

def IsCrossBusy(busy_flags, busy2_flags):
    for i in busy_flags:
        for j in eval(busy2_flags):
            if i == j:
                print "lolwtole"
                return True
    return False

def IsCrossDaysRecordTalk(days1, days2):
    for i in days1:
        for j in days2:
            if i == j:
                return True
    return False

def IsCrossTypeRecord(type1, type2):
    for i in type1:
        for j in eval(type2):
            if i == j:
                return True
    return False
