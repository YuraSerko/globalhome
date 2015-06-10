#!/usr/bin/env python
# -*-coding=utf-8-*-


import rest_service
import datetime
import urllib2

""" Пример использования класса RestApi.
    У REST-сервиса не предусмотрен demo-режим, все действия совершаются в боевом режиме.
    То есть при вызове функции SendMessage сообщения реально отправляются.
    Будьте внимательны при вводе адреса отправителя и номеров получателей."""

login = 'GlobalHome01'
password = 'Ndjhtw@#4'
host = 'https://integrationapi.net/rest'

# try:
rest = rest_service.RestApi(login, password, host)
# except urllib2.URLError as error:
#    print(error.code, error.msg)
#    exit()

balance = rest.get_balance()
message_ids = rest.send_message('GlobalHome', '375256182928', 'Hello, world!')
print type(message_ids)
print message_ids
# message_ids = rest.send_message('адрес отправителя', 'номер получателя', 'Hello, world!')
# statistics = rest.get_statistics(datetime.date(2012, 3, 12), datetime.date(2012, 5, 8))
state = rest.get_message_state(message_ids[0])

print rest._session_id, balance, state
