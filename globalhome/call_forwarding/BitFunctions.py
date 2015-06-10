# -*- coding=utf-8 -*-
def GetBit(number, index):
    """
        Проверяет, включен ли бит с индексом index в целом числе number
    """
    return bool(number & (1 << index))

def SetBit(number, index, value):
    """
        Устанавливает бит с индексом index в целом числе number в значение value и возвращает результат
    """
    if (value):
        number = number | (1 << index)
    else:
        number = number & (~ (1 << index))
    return number
