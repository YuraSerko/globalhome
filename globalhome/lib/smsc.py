# -*-coding=utf-8-*-
# SMSC.RU API (www.smsc.ru) версия 1.0 (30.05.2011)


import urllib, smtplib
from time import sleep
from datetime import datetime


# Вспомогательные функции
def urlencode(s):
    return urllib.quote(str(s))

def ifs(cond, val1, val2):
    if cond:
        return val1
    return val2


# Класс для взаимодействия с сервером smsc.ru

class SMSC(object):
    # def __init__(self, ):


    # Метод отправки SMS
    #
    # обязательные параметры:
    #
    # phones - список телефонов через запятую или точку с запятой
    # message - отправляемое сообщение
    #
    # необязательные параметры:
    #
    # translit - переводить или нет в транслит (1 или 0)
    # time - необходимое время доставки в виде строки (DDMMYYhhmm, h1-h2, 0ts, +m)
    # timezone - часовой пояс относительно Москвы в виде строки (-1, 0, 2)
    # id - идентификатор сообщения. Представляет собой 32-битное число в диапазоне от 1 до 2147483647.
    # flash - flash сообщение (1 или 0)
    # sender - имя отправителя (Sender ID)
    # charset - кодировка сообщения (utf-8 или koi8-r), по умолчанию используется utf-8
    # query - строка дополнительных параметров, добавляемая в URL-запрос ("valid=01:00&maxsms=3")
    #
    # возвращает массив (<id>, <количество sms>, <стоимость>, <баланс>) в случае успешной отправки
    # либо массив (<id>, -<код ошибки>) в случае ошибки

    def send_sms(self, phones, message, translit=False, time="", id=0, flash=False, sender=False, charset="utf-8", timezone="", query=""):
        m = self._smsc_send_cmd("send", "cost=3&phones=" + urlencode(phones) + "&mes=" + urlencode(message) +
                    "&translit=" + ifs(translit, "1", "0") + "&id=" + str(id) + "&flash=" + ifs(flash, "1", "0") +
                    ifs(sender == False, "", "&sender=" + urlencode(sender)) + "&charset=" + charset +
                    ifs(time, "time=" + urlencode(time) + "&tz=" + timezone, "") + ifs(query, "&" + query, ""))

        # (id, cnt, cost, balance) или (id, -error)

        if SMSC_DEBUG:
            if m[1] > "0":
                print "Сообщение отправлено успешно. ID: " + m[0] + ", всего SMS: " + m[1] + ", стоимость: " + m[2] + " руб., баланс: " + m[3] + " руб."
            else:
                print "Ошибка №" + m[1][1:] + ifs(m[0] > "0", ", ID: " + m[0], "")

        return m


    # SMTP версия метода отправки SMS

    def send_sms_mail(self, phones, message, translit=False, time="", id=0, flash=False, sender="", charset="utf-8", timezone=""):
        server = smtplib.SMTP(SMTP_SERVER)
        # server.set_debuglevel(1)

        if SMTP_LOGIN:
            server.login(SMTP_LOGIN, SMTP_PASSWORD)

        server.sendmail(SMTP_FROM, "send@send.smsc.ru", "Content-Type: text/plain; charset=" + charset + "\n\n" +
                            SMSC_LOGIN + ":" + SMSC_PASSWORD + ":" + str(id) + ":" + time +
                            ifs(timezone, "," + timezone, "") + ":" + ifs(translit, "1", "0") + "," +
                            ifs(flash, "1", "0") + "," + sender + ":" + phones + ":" + message)
        server.quit()


    # Метод получения стоимости SMS
    #
    # обязательные параметры:
    #
    # phones - список телефонов через запятую или точку с запятой
    # message - отправляемое сообщение
    #
    # необязательные параметры:
    #
    # translit - переводить или нет в транслит (1 или 0)
    # sender - имя отправителя (Sender ID)
    # charset - кодировка сообщения (utf-8 или koi8-r), по умолчанию используется utf-8
    #
    # возвращает массив (<стоимость>, <количество sms>) либо массив (0, -<код ошибки>) в случае ошибки

    def get_sms_cost(self, phones, message, translit=False, sender=False, charset="utf-8"):
        m = self._smsc_send_cmd("send", "cost=1&phones=" + urlencode(phones) + "&mes=" + urlencode(message) +
                    ifs(sender == False, "", "&sender=" + urlencode(sender)) + "&charset=" + charset +
                    "&translit=" + ifs(translit, "1", "0"))

        # (cost, cnt) или (0, -error)

        if SMSC_DEBUG:
            if m[1] > "0":
                print "Стоимость рассылки: " + m[0] + " руб. Всего SMS: " + m[1]
            else:
                print "Ошибка №" + m[1][1:]

        return m

    # Метод проверки статуса отправленного SMS
    #
    # id - ID cообщения
    # phone - номер телефона
    #
    # возвращает массив (<статус>, <время изменения>) либо массив (0, -<код ошибки>) в случае ошибки

    def get_status(self, id, phone):
        m = self._smsc_send_cmd("status", "phone=" + urlencode(phone) + "&id=" + str(id))

        # (status, time) или (0, -error)

        if SMSC_DEBUG:
            if m[1] >= "0":
                tm = ""
                if m[1] > "0":
                    tm = str(datetime.fromtimestamp(int(m[1])))
                print "Статус SMS = " + m[0] + ifs(m[1] > "0", ", время изменения статуса - " + tm, "")
            else:
                print "Ошибка №" + m[1][1:]

        return m

    # Метод получения баланса
    #
    # без параметров
    #
    # возвращает баланс в виде строки или False в случае ошибки

    def get_balance(self):
        m = self._smsc_send_cmd("balance")  # (balance) или (0, -error)

        if SMSC_DEBUG:
            if len(m) < 2:
                print "Сумма на счете: " + m[0] + " руб."
            else:
                print "Ошибка №" + m[1][1:]

        return ifs(len(m) > 1, False, m[0])


    # ВНУТРЕННИЕ МЕТОДЫ

    # Метод чтения URL

    def _smsc_read_url(self, url):
        if SMSC_POST or len(url) > 2000:
            m = url.split('?', 2)
            data = urllib.urlopen(m[0], m[1])
        else:
            data = urllib.urlopen(url)

        ret = data.read()

        return ret

    # Метод вызова запроса. Формирует URL и делает 3 попытки чтения

    def _smsc_send_cmd(self, cmd, arg=""):
        url = ifs(SMSC_HTTPS, "https", "http") + "://smsc.ru/sys/" + cmd + ".php?login=" + urlencode(SMSC_LOGIN) + "&psw=" + urlencode(SMSC_PASSWORD) + "&fmt=1&" + arg

        i = 0
        ret = ""

        while ret == "" and i < 3:
            if i > 0:
                sleep(2)

            ret = self._smsc_read_url(url)

            i += 1

        if ret == "":
            if SMSC_DEBUG:
                print "Ошибка чтения адреса: " + url
            ret = ","  # фиктивный ответ

        return ret.split(",")



# Константы для настройки библиотеки
SMSC_LOGIN = "globalhome"  # логин клиента
SMSC_PASSWORD = "u[!@#"  # пароль или MD5-хеш пароля в нижнем регистре
SMSC_POST = True  # использовать метод POST
SMSC_HTTPS = True  # использовать HTTPS протокол
SMSC_DEBUG = True  # флаг отладки

# Константы для отправки SMS по SMTP
SMTP_FROM = "send@smsc.ru"  # e-mail адрес отправителя
SMTP_SERVER = "send.smsc.ru"  # адрес smtp сервера
SMTP_LOGIN = ""  # логин для smtp сервера
SMTP_PASSWORD = ""  # пароль для smtp сервера

if __name__ == '__main__':
    # Examples:
    smsc = SMSC()
    sms = """Podrobnosti: Globalhome.su
    Telefon dlya aktivacii: +74996383000
    Login: 11111
    Pin: 11111"""
    r = smsc.send_sms("79154957812", sms)
    print r
    smsc.send_sms_mail("79999999999", "test2", flash=True)
    r = smsc.get_status(5, "375256182928")
    print r
    print smsc.get_balance()
