# coding=utf-8
import sys, os
from celery.decorators import task
from celery.task.schedules import crontab
from urllib2 import quote
import urllib, urllib2, cookielib
import imaplib
import email
from email.header import decode_header
import imaplib, email
from BeautifulSoup import BeautifulSoup
import time
from job.models import HotSpotWorkJobSeekerPersonalData
from job.models import HotSpotWorkWishes
from job.models import HotSpotWorkExperience
from job.models import HotSpotWorkEducationAndSkills
from job.models import HotSpotWorkEducationalInstitution
from job.models import HotSpotWorkEducationAndSkills
from job.models import HotSpotWorkForeignLanguagesProf
from job.models import HotSpotWorkAdditionalEducation
from job.models import HotSpotWorkPortfolio
from job.models import HotSpotWorkResumes
from job.models import HotSpotWorkJobRuCreated
from xml.dom.minidom import *
import imaplib
import random
from lib.mail import send_email
from django.conf import settings



@task
def job_ru_register(username, resume_id, email_specified_by_user):
    print u'register job ru'
    username = username
    resume_id = resume_id
    pas = ''
    for i in xrange(4):
        pas = pas + random.choice('qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM')
        pas = pas + random.choice('1237894560')
    
    # функции
    # вход на сайт job.ru (пользовтель уже зарегестрирован)
    def login_to_job_ru(mail_name, pas):
        login_data = urllib.urlencode({
                                          'tbEmail': mail_name,
                                          'tbPassword': pas,
                                       })
        resp = opener.open('http://ww.job.ru/seeker/login/', login_data)
        resp = opener.open('http://www.job.ru/')
        
    # регистрация ПОЧТОВОГО ЯЩИКА НА GLOBALHOME.MOBI
    # проверка сущеествования логина на доменной почте
    def mail_check_user(loging_to_check):
        token = "ec0a770134ae7ea00b10cd43178c235171cfb39913833eb29abf9e42"
        ADRESS = 'https://pddimp.yandex.ru/check_user.xml?token=' + token + '&login=' + loging_to_check
        file = urllib2.urlopen(ADRESS)
        data = file.read()
        file.close()
        doc = parseString(data)
        result = doc.getElementsByTagName('result')[0].childNodes[0]
        if result.nodeValue == 'exists':
            return False
        else:
            return True
    
    # регистрация
    def mail_reg(login, password):
        token = "ec0a770134ae7ea00b10cd43178c235171cfb39913833eb29abf9e42"
        ADRESS = 'https://pddimp.yandex.ru/reg_user_token.xml?token=' + token + '&u_login=' + login + '&u_password=' + password
        file = urllib2.urlopen(ADRESS)
        data = file.read()
        file.close()
        doc = parseString(data)
        root = doc.documentElement
    
        for q in root.childNodes:
            if q.nodeName == 'error':
                str_ex_er = q.getAttribute('reason')
            if q.nodeName == 'ok':
                str_ex_er = 'ok'
        er_dict = {'badlogin': u'Логин некорректен',
                   'passwd-tooshort': u'Пароль короток',
                   'passwd-toolong': u'Пароль слишком длинный',
                   'occupied': u'Логин уже занят',
                   'passwd-likelogin': u'Пароль и логин совпадают',
                   'login-empty': u'Введите логин',
                   'passwd-empty': u'Введите пароль',
                   'ok': u'Регистрация завершена успешно'}
        str_ex = er_dict[str_ex_er]
        return str_ex_er
    
    
    def final_mail_reg(login_username, pas):
        # Финальная стадия ригистрации
        mail_name = login_username + '@globalhome.mobi'
        sex_yandex_dict = {1:'male',
                           2:'female'
                           }
        
        
        final_reg = 'https://passport.yandex.ru/for/globalhome.mobi?mode=auth'
        
        # print pas
        login_reg_dict = {           
                              'login':mail_name,
                              'passwd':pas,
                                       }
        
        login_reg_data = urllib.urlencode(login_reg_dict)
        resp = opener.open(final_reg, login_reg_data)
        t = resp.read()
        soup = BeautifulSoup(t)
        track_input = soup.find('input', id='track_id')
        
        final_reg_dict = {           
        
                                        'bday':personal_data_obj.birthday.day,
                                        'bmonth':personal_data_obj.birthday.month,
                                        'byear':personal_data_obj.birthday.year,
                                        'eula_accepted':'yes',
                                        'firstname':personal_data_obj.first_name.encode('utf8'),
                                        'hint_answer':'1',  # may not work
                                        'hint_question':'1',  # may not work
                                        'hint_question_id':'99',
                                        'language':'ru',
                                        'lastname':personal_data_obj.second_name.encode('utf8'),
                                        'sex':sex_yandex_dict[personal_data_obj.sex],
                                        'state':'complete_pdd',
                                        'track_id':track_input['value'],
                                       }
        final_reg_data = urllib.urlencode(final_reg_dict)
        resp = opener.open(final_reg, final_reg_data)
        return mail_name, pas
        
        
    # создаем логин и пароль для доменной почты
    def register_domain_mail_login(username, pas):
        uiter = 1
        while uiter < 1000:
            if mail_check_user(username):
                uiter = 1000
                result = mail_reg(username, pas)
                return username, pas
            else:
                uiter = uiter + 1
                username = username + str(uiter)
    
    # заполеняем профиль
    def fill_profile(mail_name, pas):
        # sex
        if personal_data_obj.sex == 1:
            sex = 'rbMale'
        else:
            sex = 'rbFemale'
        # дополнительные номера телефона
        if personal_data_obj.additional_tel_code:
            add_tel_code = personal_data_obj.additional_tel_code
        else:
            add_tel_code = ''
        if personal_data_obj.additional_tel_number:
            add_tel_number = personal_data_obj.additional_tel_number
        else:
            add_tel_number = ''
        ADDRESS = 'http://www.job.ru/seeker/user/cv/create/personal/'
        # print personal_data_obj.id
        # print mail_name
        
        login_data = urllib.urlencode({
                                          '__EVENTARGUMENT': '',
                                          '__EVENTTARGET': 'ctl00$cpH$btNext',
                                          '__VIEWSTATE': '/wEPDwUKMTY5NjYzOTY3OA8WAh4TVmFsaWRhdGVSZXF1ZXN0TW9kZQIBFgJmD2QWAgICDxYCHgdlbmN0eXBlBRNtdWx0aXBhcnQvZm9ybS1kYXRhFgICCw9kFgYCAQ9kFhpmDw8WBB4IQ3NzQ2xhc3MFI2lucHV0c19maWVsZCBmb3JtYXRfbmFtZSB2YWxpZF90ZXh0HgRfIVNCAgJkFgICAQ9kFgICAQ8PFgIeBFRleHRlFgIeCm9ua2V5cHJlc3MFIXJldHVybiBEaXNhYmxlU3VibWl0KGV2ZW50LG51bGwpO2QCAQ8PFgQfAgUjaW5wdXRzX2ZpZWxkIGZvcm1hdF9uYW1lIHZhbGlkX3RleHQfAwICZBYCAgEPZBYCAgEPDxYCHwRlFgIfBQUhcmV0dXJuIERpc2FibGVTdWJtaXQoZXZlbnQsbnVsbCk7ZAICDw8WBB8CBSxpbnB1dHNfZmllbGQgZm9ybWF0X25hbWUgdmFsaWRfdGV4dCBoaWRlYWJsZR8DAgJkFgJmD2QWAgIBDw8WAh8EZRYCHwUFIXJldHVybiBEaXNhYmxlU3VibWl0KGV2ZW50LG51bGwpO2QCAw8PFgQfAgU0aW5wdXRzX2ZpZWxkIGdyb3VwZWRfc2VsZWN0X2JveCBmbG9hdF9sIHZhbGlkX29wdGlvbh8DAgJkZAIEDw8WBB8CBSppbnB1dHNfZmllbGQgZ3JvdXBlZF9zZWxlY3RfYm94IHZhbGlkX2RhdGUfAwICZBYCAgEPZBYCAgEPZBYGZg8PFgIfBGUWAh8FBSFyZXR1cm4gRGlzYWJsZVN1Ym1pdChldmVudCxudWxsKTtkAgIPEA8WBh4NRGF0YVRleHRGaWVsZAUFVmFsdWUeDkRhdGFWYWx1ZUZpZWxkBQNLZXkeC18hRGF0YUJvdW5kZ2QQFQ0K0JzQtdGB0Y/RhgzQr9C90LLQsNGA0YwO0KTQtdCy0YDQsNC70YwI0JzQsNGA0YIM0JDQv9GA0LXQu9GMBtCc0LDQuQjQmNGO0L3RjAjQmNGO0LvRjAzQkNCy0LPRg9GB0YIQ0KHQtdC90YLRj9Cx0YDRjA7QntC60YLRj9Cx0YDRjAzQndC+0Y/QsdGA0YwO0JTQtdC60LDQsdGA0YwVDQABMQEyATMBNAE1ATYBNwE4ATkCMTACMTECMTIUKwMNZ2dnZ2dnZ2dnZ2dnZxYBZmQCBA8PFgIfBGUWAh8FBSFyZXR1cm4gRGlzYWJsZVN1Ym1pdChldmVudCxudWxsKTtkAgUPZBYCZg8PZBYEHgxkYXRhLW1heHNpemUFBzIwOTcxNTIeCGRhdGEtZXh0BRRqcGcsanBlZyxnaWYscG5nLGJtcBYCAgMPZBYCAgEPZBYCAgMQDxYCHghJbWFnZVVybAU0aHR0cDovL2ltZzEuam9iLnJ1L2ZlL3VwbG9hZC9zZWVrZXIvbG9nby9ub19mb3RvLnBuZ2RkZAIGDw8WBB8CBTNpbnB1dHNfZmllbGQgdW5vc3VnZ2VzdCBiaWdfaW5wdXQgdmFsaWRfbXVsdGlzZWxlY3QfAwICZGQCBw8PFgQfAgUzaW5wdXRzX2ZpZWxkIHVub3N1Z2dlc3QgYmlnX2lucHV0IHZhbGlkX211bHRpc2VsZWN0HwMCAmRkAggPDxYEHwIFS2lucHV0c19maWVsZCBtdWx0aV9zdWdnZXN0IGlzc2V0X3Jlc3VsdHMgYmlnX2lucHV0IHZhbGlkX211bHRpc2VsZWN0IGhpZGRlbh8DAgJkZAIJDw8WBB8CBTVpbnB1dHNfZmllbGQgbWlkZGxlX2lucHV0X3NpemUgZm9ybWF0X3RleHQgdmFsaWRfdGV4dB8DAgJkFgICAQ9kFgICAQ8PFgIfBGVkZAIKDw8WBB8CBStpbnB1dHNfZmllbGQgcGhvbmVfZmllbGQgdmFsaWRfc2Vla2VyX3Bob25lHwMCAmQWAgIBD2QWAgIBD2QWAgIDD2QWAgIBDw8WAh8EZWRkAgsPDxYEHwIFK2lucHV0c19maWVsZCBwaG9uZV9maWVsZCB2YWxpZF9zZWVrZXJfcGhvbmUfAwICZBYCAgEPZBYCAgEPZBYCAgMPZBYCAgEPDxYCHwRlZGQCDA8WAh4HVmlzaWJsZWhkAgIPZBYCAgEPFgIfDGcWBmYPDxYEHwIFPGlucHV0c19maWVsZCBtaWRkbGVfaW5wdXRfc2l6ZSBmb3JtYXRfdHJpbSB2YWxpZF9zZWVrZXJfbWFpbB8DAgJkFgICAQ9kFgJmDw8WAh8EZRYCHwUFIXJldHVybiBEaXNhYmxlU3VibWl0KGV2ZW50LG51bGwpO2QCAQ8PFgQfAgUtaW5wdXRzX2ZpZWxkIG1pZGRsZV9pbnB1dF9zaXplIHZhbGlkX3Bhc3N3b3JkHwMCAmQWAmYPZBYCAgEPZBYCAgEPD2QWAh8FBSFyZXR1cm4gRGlzYWJsZVN1Ym1pdChldmVudCxudWxsKTtkAgIPDxYEHwIFGGlucHV0c19maWVsZCB2YWxpZF9jaGVjax8DAgJkZAIEDw8WAh8MZ2RkGAQFHl9fQ29udHJvbHNSZXF1aXJlUG9zdEJhY2tLZXlfXxYGBR5jdGwwMCRjcEgkc2Vla2VyUHJvZmlsZSRyYk1hbGUFHmN0bDAwJGNwSCRzZWVrZXJQcm9maWxlJHJiTWFsZQUgY3RsMDAkY3BIJHNlZWtlclByb2ZpbGUkcmJGZW1hbGUFIGN0bDAwJGNwSCRzZWVrZXJQcm9maWxlJHJiRmVtYWxlBRljdGwwMCRjcEgkY2hrU2hvd1Bhc3N3b3JkBRJjdGwwMCRjcEgkY2JBZ3JlZWQFMGN0bDAwJGNwSCRzZWVrZXJQcm9maWxlJG9ialBob3RvU2VsZWN0b3IkbXZQaG90bw8PZAICZAU6Y3RsMDAkY3BIJHNlZWtlclByb2ZpbGUkb2JqUGhvdG9TZWxlY3RvciR0eHRVcGxvYWRQaG90b05ldw8yiwIAAQAAAP////8BAAAAAAAAAAwCAAAASlRtZUpvYnMsIFZlcnNpb249MS4wLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj0yYjY3NTQ0OWNhZjIxYzBlBQEAAAAdVG1lSm9icy5JTy5GaWxlSXRlbUNvbGxlY3Rpb24DAAAADUxpc3RgMStfaXRlbXMMTGlzdGAxK19zaXplD0xpc3RgMStfdmVyc2lvbgQAABVUbWVKb2JzLklPLkZpbGVJdGVtW10CAAAACAgCAAAACQMAAAAAAAAAAAAAAAcDAAAAAAEAAAAAAAAABBNUbWVKb2JzLklPLkZpbGVJdGVtAgAAAAtkBTdjdGwwMCRjcEgkc2Vla2VyUHJvZmlsZSRvYmpQaG90b1NlbGVjdG9yJHR4dFVwbG9hZFBob3RvDzKLAgABAAAA/////wEAAAAAAAAADAIAAABKVG1lSm9icywgVmVyc2lvbj0xLjAuMC4wLCBDdWx0dXJlPW5ldXRyYWwsIFB1YmxpY0tleVRva2VuPTJiNjc1NDQ5Y2FmMjFjMGUFAQAAAB1UbWVKb2JzLklPLkZpbGVJdGVtQ29sbGVjdGlvbgMAAAANTGlzdGAxK19pdGVtcwxMaXN0YDErX3NpemUPTGlzdGAxK192ZXJzaW9uBAAAFVRtZUpvYnMuSU8uRmlsZUl0ZW1bXQIAAAAICAIAAAAJAwAAAAAAAAAAAAAABwMAAAAAAQAAAAAAAAAEE1RtZUpvYnMuSU8uRmlsZUl0ZW0CAAAAC2SRLG0nGqFteu7RYsLEyPdx7KtpQA==',
                                          'tbEmail': '',
                                          'tbPassword': '',
                                          'ctl00$cpH$seekerProfile$txtSeekerName': personal_data_obj.first_name.encode('utf8'),
                                          'ctl00$cpH$seekerProfile$vpSeekerName_txtValidateState': 'success',
                                          'ctl00$cpH$seekerProfile$txtSeekerSurname': personal_data_obj.second_name.encode('utf8'),
                                          'ctl00$cpH$seekerProfile$vpSeekerSurname_txtValidateState': 'success',
                                          'ctl00$cpH$seekerProfile$txtSeekerMiddleName':  personal_data_obj.last_name.encode('utf8'),
                                          'ctl00$cpH$seekerProfile$vpSeekerMiddleName_txtValidateState': '',
                                          'ctl00$cpH$seekerProfile$GenderGroup': sex,
                                          'ctl00$cpH$seekerProfile$vpGender_txtValidateState': 'success',
                                          'ctl00$cpH$seekerProfile$objDateSelector$txtDay': personal_data_obj.birthday.day,
                                          'ctl00$cpH$seekerProfile$objDateSelector$ddlMonth': personal_data_obj.birthday.month,
                                          'ctl00$cpH$seekerProfile$objDateSelector$txtYear': personal_data_obj.birthday.year,
                                          'ctl00$cpH$seekerProfile$vpSeekerDate_txtValidateState': 'success',
                                          'ctl00$cpH$seekerProfile$objNat$ssNationality$ctlHiddenFieldValue': personal_data_obj.citizenship.jobru_nat_id,
                                          'ctl00$cpH$seekerProfile$vpNationality_txtValidateState': 'success',
                                          'ctl00$cpH$seekerProfile$objCity$ssLocation$ctlHiddenFieldValue': personal_data_obj.living_city.jobru_city_id,
                                          'ctl00$cpH$seekerProfile$vpCity_txtValidateState': 'success',
                                          'ctl00$cpH$seekerProfile$objMetro$objMetro$ctlTextBox': '',
                                          'ctl00$cpH$seekerProfile$objMetro$objMetro$ctlHiddenFieldValues': '',
                                          'ctl00$cpH$seekerProfile$vpMetro_txtValidateState': '',
                                          'ctl00$cpH$seekerProfile$objPhone1_txtEnableState': 'readonly',
                                          'ctl00$cpH$seekerProfile$vpCity_txtValidateState': 'success',
                                          'ctl00$cpH$seekerProfile$objPhone1$txtCountryCode': '7',
                                          'ctl00$cpH$seekerProfile$objPhone1$txtRegionCode': personal_data_obj.main_tel_code,
                                          'ctl00$cpH$seekerProfile$objPhone1$txtPhoneNumber': personal_data_obj.main_tel_number,
                                          'ctl00$cpH$seekerProfile$vpPhone1_txtValidateState': 'success',
                                          'ctl00$cpH$seekerProfile$objPhone2_txtEnableState': '',
                                          'ctl00$cpH$seekerProfile$objPhone2$txtCountryCode': '7',
                                          'ctl00$cpH$seekerProfile$objPhone2$txtRegionCode': add_tel_code,
                                          'ctl00$cpH$seekerProfile$objPhone2$txtPhoneNumber': add_tel_number,
                                          'ctl00$cpH$seekerProfile$vpPhone2_txtValidateState': '',
                                          'ctl00$cpH$txtSeekerEmail': mail_name,
                                          'ctl00$cpH$vpSeekerEmail_txtValidateState': 'success',
                                          'ctl00$cpH$txtSeekerPassword': pas,
                                          'ctl00$cpH$txtSeekerPasswordView': pas,
                                          'ctl00$cpH$chkShowPassword': 'on',
                                          'ctl00$cpH$vpSeekerPassword_txtValidateState': 'success',
                                          'ctl00$cpH$cbAgreed': 'on',
                                          'ctl00$cpH$vpAgreement_txtValidateState': 'success',
                                          '__PREVIOUSPAGE': 'LB_f6boh4d9Eu0SmzO0_qqkjBOpXZoqMeEUfbFfuYjAhTsKoIxEDWzYrsY8Xj_i3PTrY3jW-nFfDT3xB-FzmXeOHiAd7rYVLgDI6Yw2'
                                       })
        
        resp = opener.open(ADDRESS, login_data)
        
        
        
        
    def activate_account(mail_name, pas):
    # вход на почту и активация аккаута
    #     server = "imap.yandex.ru"
    #     print mail_name
    #     print pas
    #     mail = imaplib.IMAP4_SSL(server)
    #     mail.login(mail_name, pas)
    #     mail.list()
    #     mail.select("inbox")  # connect to inbox.
    #     result, data = mail.search(None, 'All')
    #     seeking_num = 0
        i = 5
        # time.sleep(10)
        while i != 0:
            # print i 
            server = "imap.yandex.ru"
            # print mail_name
            # print pas
            mail = imaplib.IMAP4_SSL(server)
            mail.login(mail_name, pas)
            mail.list()
            mail.select("inbox")  # connect to inbox.
            result, data = mail.search(None, 'All')
            seeking_num = 0
            try:
                # print 'try'
                # print data[0]
                for num in data[0].split():  # if noletter error for num in data[0].split() 'NoneType' object has no attribute 'split'
                    rv, data = mail.fetch(num, '(RFC822)')
                    if rv != 'OK':
                        print "ERROR getting message"
                    msg = email.message_from_string(data[0][1])
                    
                    # print 'Message %s: %s' % (num, decode_header(msg['Subject']))
                    # print 'Raw Date:', msg['Date']
                    # print decode_header(msg['Subject'])[0][0]
                    if decode_header(msg['Subject'])[0][0] == 'JOB.RU: Регистрация на сайте' or   decode_header(msg['Subject'])[0][0] == 'JOB.RU: Активация адреса электронной почты':
                        # print 'nnnnnnnnnnnnnnn', num
                        for part in msg.walk():
                            if part.get_content_type() == 'text/plain':
                                seeking_msg = part.get_payload()  # prints the raw text
                i = 0
                # print 'end try'
            except Exception, e:
                # print 'except'
                print e
                time.sleep(1)
                # логинимся на сайте
                login_data = urllib.urlencode({
                                          'tbEmail': mail_name,
                                          'tbPassword': pas,
                                          '__VIEWSTATE':'/wEPDwULLTExNTI1Nzc2MDlkZPzuNiNe3PdEMH8858FButw0DsKA',
                                          ' __EVENTTARGET':'ctl00$ctl10$lbLogin',
                                          '__LASTFOCUS':'',
                                          '__EVENTARGUMENT':'',
                                          '__PREVIOUSPAGE':'za6VPz-P5emDcaWiRuPKZOyNou7qkOg9yxh83R-C_7EuOlbtKHAxM0JUg0o1',
                                          'ctl00$cpH$objFilter$tbKeywords':''
                                       })
                resp = opener.open('http://ww.job.ru/seeker/login/', login_data)
                # print resp.read()
                # resp = opener.open('http://www.job.ru/seeker/user/profile/change-email/')
                # print resp.read()
                # посылаем письмо еще раз
                mail_data = urllib.urlencode({
                                              'ctl00$cpH$txtEmail': mail_name,
                                              '__EVENTARGUMENT':'',
                                              '__EVENTTARGET':'ctl00$cpH$aSendConfirmation',
                                              '__VIEWSTATE':'/wEPDwUKLTk2NjkyMDM1OQ8WAh4TVmFsaWRhdGVSZXF1ZXN0TW9kZQIBFgJmD2QWAgICD2QWAgIMD2QWBAIBDw8WBB4IQ3NzQ2xhc3MFNWlucHV0X2JveF9hcmVhIHZhbGlkX3NlZWtlcl9tYWlsIHZhbGlkX2VtYWlsX2NoYW5naW5nHgRfIVNCAgJkFgICAQ9kFgJmD2QWAgIDDw8WAh4EVGV4dAUVbW0yMDBAZ2xvYmFsaG9tZS5tb2JpFgIeCm9ua2V5cHJlc3MFIXJldHVybiBEaXNhYmxlU3VibWl0KGV2ZW50LG51bGwpO2QCAg8PFgIfAwVSPHNwYW4gc3R5bGU9ImZvbnQtc2l6ZToxNHB4OyBsaW5lLWhlaWdodDoyMnB4OyI+0JjQt9C80LXQvdC40YLRjCDQsNC00YDQtdGBPC9zcGFuPmRkZOk4bdLZXYJ7Qs+/UIXzE1ksfBxK',
                                              'ctl00$cpH$vpMail_txtValidateState':'success'
                                           })
                resp = opener.open('http://www.job.ru/seeker/user/profile/change-email/', mail_data)
                i = i - 1  
                time.sleep(30)
             
        
        act_link_start = seeking_msg.find('Активация аккаунта') + 44
        seeking_msg_cut = seeking_msg[act_link_start:]
        act_link_end = seeking_msg_cut.find('>')
        act_link = seeking_msg_cut[:act_link_end]

        
        
        
        quoted_query = urllib.quote(act_link)
        quoted_query = 'http://' + quoted_query
        try:
            resp = opener.open(quoted_query)
        except Exception, e:
            print e
    
    #========================================================================================================================    
    
    
    
    # BEGIN SCRIPT
#     print 'begin script'
#     a = 'Текст в utf8'
#     b = u'Текст в unicode'
#     print 'a =', type(a), a
#     print 'b =', type(b), b
#     exit()
#     print 'after exit'
    
    
    
    try:
        cre_res_obj = HotSpotWorkJobRuCreated.objects.get(doc_id=resume_id)
    except HotSpotWorkJobRuCreated.DoesNotExist:
        resume_obj = HotSpotWorkResumes.objects.get(id=resume_id)
        personal_data_obj = HotSpotWorkJobSeekerPersonalData.objects.get(id=resume_obj.personal_data.id)
        
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)
        opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:32.0) Gecko/20100101 Firefox/32.0'), ]
    
        
        # проверяем были ли добавлены резюме ранее
        jobru_created_objs = HotSpotWorkJobRuCreated.objects.filter(username=username, type=1)
        if jobru_created_objs.count() == 0:  # 1st resume
            mail_name, pas = register_domain_mail_login(username, pas)
            mail_name, pas = final_mail_reg(mail_name, pas)
            fill_profile(mail_name, pas)
            activate_account(mail_name, pas)
        else:
            for jobru_created_obj in jobru_created_objs:
                mail_name, pos = jobru_created_obj.mobi_mail, jobru_created_obj.mobi_mail_pas
                
        
        # activate_account('mm200@globalhome.mobi', 'Globalhome1')
        # exit() 
        time.sleep(20)
        login_to_job_ru(mail_name, pas)
        
        #------------------------------------------------
        # заполнить опыт работы
        # resume_id
        work_wishes = HotSpotWorkWishes.objects.get(resume__id=resume_id)
        
        # режим работы
        job_ru_work_mode_dict = {1:'rbEmploymentType_Employee',
                                 2:'rbEmploymentType_Contractor',
                                 3:'rbEmploymentType_Tempcontract',
                                 4:'rbEmploymentType_Any',
                                 }
        
        # тип занятости
        job_ru_work_emp_type = {1:'rbEmploymentKind_Constant',
                                2:'rbEmploymentKind_Variable',
                                3:'rbEmploymentKind_Probation',
                                4:'rbEmploymentKind_Volunteering',
                                }
        
        
        # тип работы
        job_ru_work_type = {1:'rbEmploymentPlace_WorkAtOffice',
                            2:'rbEmploymentPlace_WorkAtHome',
                            }
        
        
        # сферы деятельности (словарь вида   972:975;989:991,992)
        activity_fields = {}
        activity_fields_str = ''
        for wsp in work_wishes.specialization.all():
            dict_added = False
            if activity_fields:
                existing_keys = activity_fields.keys()
                for exk in existing_keys:
                    if exk == wsp.activity_field.job_ru_activity_id:
                        temp_val = activity_fields[exk] 
                        activity_fields[exk] = temp_val + ',' + str(wsp.job_ru_spec_id)
                        dict_added = True
            if dict_added == False:
                activity_fields[wsp.activity_field.job_ru_activity_id] = str(wsp.job_ru_spec_id)
            
        for key in activity_fields.keys():
            activity_fields_str = activity_fields_str + str(key) + ":" + activity_fields[key] + ";"
        activity_fields_str = activity_fields_str[:len(activity_fields_str) - 1]
        
        # выбрать регион поиска
        city_str = ''
        for lc in work_wishes.living_city.all():
            city_str = city_str + lc.jobru_city_id + ','
        city_str = city_str[:len(city_str) - 1]  
            
        # дополнительное название резюме
        additional_res_name = ''
        for adn in work_wishes.additional_name.all():
            additional_res_name = additional_res_name + adn.profession + ';'
        additional_res_name = additional_res_name[:len(additional_res_name) - 1]
        
        # зарплата ед. изм.
        salary_um_dict = {1:'711', 2:'712', 3:'713'}
        if work_wishes.salary:
            salary_str = work_wishes.salary
        else:
            salary_str = ''
        
        # exp position
        exp_pos = {1:'694', 2:'695', 3:'696', 4:'697', 5:'698', 6:'699'}
        
        exp_data_dict = { '__EVENTARGUMENT': '',
                                        '__EVENTTARGET': 'ctl00$cpH$btSave',
                                        '__VIEWSTATE':'/wEPDwUKMjExMjEwOTI5NA8WAh4TVmFsaWRhdGVSZXF1ZXN0TW9kZQIBFgJmD2QWAgICD2QWAgILD2QWEAICDw8WBB4IQ3NzQ2xhc3MFM2lucHV0c19maWVsZCB1bm9zdWdnZXN0IGJpZ19pbnB1dCB2YWxpZF9tdWx0aXNlbGVjdB4EXyFTQgICZGQCAw8PFgQfAQVHaW5wdXRzX2ZpZWxkIG51bWJlcl9maWVsZCB2YWxpZF9zYWxhcnkgc3BlY19zYWxhcnlfaW5wdXQgZm9ybWF0X2ludGVnZXIfAgICZBYCAgEPZBYEZg8PFgIeBFRleHRlFgIeCm9ua2V5cHJlc3MFIXJldHVybiBEaXNhYmxlU3VibWl0KGV2ZW50LG51bGwpO2QCAQ8QDxYGHg1EYXRhVGV4dEZpZWxkBQhjdXJUaXRsZR4ORGF0YVZhbHVlRmllbGQFBWN1cklkHgtfIURhdGFCb3VuZGdkEBUDB9GA0YPQsS4H0LTQvtC7LgjQtdCy0YDQvhUDAzcxMQM3MTIDNzEzFCsDA2dnZxYBZmQCBA8PFgQfAQU2aW5wdXRzX2ZpZWxkIG11bHRpX3N1Z2dlc3QgYmlnX2lucHV0IHZhbGlkX211bHRpc2VsZWN0HwICAmRkAgUPDxYEHwEFLGlucHV0c19maWVsZCBncm91cGVkX3NlbGVjdF9ib3ggdmFsaWRfb3B0aW9uHwICAmRkAgYPDxYEHwEFLGlucHV0c19maWVsZCBncm91cGVkX3NlbGVjdF9ib3ggdmFsaWRfb3B0aW9uHwICAmRkAgcPDxYEHwEFLGlucHV0c19maWVsZCBncm91cGVkX3NlbGVjdF9ib3ggdmFsaWRfb3B0aW9uHwICAmRkAggPDxYEHwEFRGlucHV0c19maWVsZCBtdWx0aV9zdWdnZXN0IGJpZ19pbnB1dCBpc3NldF9yZXN1bHRzIHZhbGlkX211bHRpc2VsZWN0HwICAmRkAgkPDxYEHwEFRGlucHV0c19maWVsZCBtdWx0aV9zdWdnZXN0IGlzc2V0X3Jlc3VsdHMgYmlnX2lucHV0IHZhbGlkX211bHRpc2VsZWN0HwICAmRkGAEFHl9fQ29udHJvbHNSZXF1aXJlUG9zdEJhY2tLZXlfXxYSBSNjdGwwMCRjcEgkcmJFbXBsb3ltZW50VHlwZV9FbXBsb3llZQUlY3RsMDAkY3BIJHJiRW1wbG95bWVudFR5cGVfQ29udHJhY3RvcgUlY3RsMDAkY3BIJHJiRW1wbG95bWVudFR5cGVfQ29udHJhY3RvcgUnY3RsMDAkY3BIJHJiRW1wbG95bWVudFR5cGVfVGVtcGNvbnRyYWN0BSdjdGwwMCRjcEgkcmJFbXBsb3ltZW50VHlwZV9UZW1wY29udHJhY3QFHmN0bDAwJGNwSCRyYkVtcGxveW1lbnRUeXBlX0FueQUeY3RsMDAkY3BIJHJiRW1wbG95bWVudFR5cGVfQW55BSNjdGwwMCRjcEgkcmJFbXBsb3ltZW50S2luZF9Db25zdGFudAUjY3RsMDAkY3BIJHJiRW1wbG95bWVudEtpbmRfVmFyaWFibGUFI2N0bDAwJGNwSCRyYkVtcGxveW1lbnRLaW5kX1ZhcmlhYmxlBSRjdGwwMCRjcEgkcmJFbXBsb3ltZW50S2luZF9Qcm9iYXRpb24FJGN0bDAwJGNwSCRyYkVtcGxveW1lbnRLaW5kX1Byb2JhdGlvbgUnY3RsMDAkY3BIJHJiRW1wbG95bWVudEtpbmRfVm9sdW50ZWVyaW5nBSdjdGwwMCRjcEgkcmJFbXBsb3ltZW50S2luZF9Wb2x1bnRlZXJpbmcFKGN0bDAwJGNwSCRyYkVtcGxveW1lbnRQbGFjZV9Xb3JrQXRPZmZpY2UFJmN0bDAwJGNwSCRyYkVtcGxveW1lbnRQbGFjZV9Xb3JrQXRIb21lBSZjdGwwMCRjcEgkcmJFbXBsb3ltZW50UGxhY2VfV29ya0F0SG9tZQUjY3RsMDAkY3BIJGNiQ3ZXb3JrRXhwZXJpZW5jZU5vdEhhdmW/M6lSMJ5wxQDbx7MV+kkmqeCZyw==',
                                        'ctl00$cpH$GroupEmploymentType':job_ru_work_mode_dict[work_wishes.work_mode],  # режим работы
                                        'ctl00$cpH$GroupEmploymentKind':job_ru_work_emp_type[work_wishes.employment_type],  # тип занятости
                                        'ctl00$cpH$GroupEmploymentPlace':job_ru_work_type[work_wishes.work_type],  # тип работы
                                        'ctl00$cpH$ctlEditors$ctlEditorBase$vpAchievements_txtValidateState': 'success',
                                        'ctl00$cpH$ctlEditors$ctlEditorBase$vpCompany_txtValidateState':'success',
                                        'ctl00$cpH$ctlEditors$ctlEditorBase$vpIndustry_txtValidateState':'success',
                                        'ctl00$cpH$ctlEditors$ctlEditorBase$vpPeriod_txtValidateState':'success',
                                        'ctl00$cpH$ctlEditors$ctlEditorBase$vpPosition_txtValidateState':'success',
                                        'ctl00$cpH$ctlEditors$ctlEditorBase$vpTitle_txtValidateState':'success',
                                        'ctl00$cpH$ctlEditors$ctlEditorBase$vpWebAddress_txtValidateState':'',
                                        'ctl00$cpH$ctlEditors$ctlRepeaterEditors$ctl00$ctlEditor$vpAchievements_txtValidateState':'success',
                                        'ctl00$cpH$ctlEditors$ctlRepeaterEditors$ctl00$ctlEditor$vpCompany_txtValidateState':'success',
                                        'ctl00$cpH$ctlEditors$ctlRepeaterEditors$ctl00$ctlEditor$vpIndustry_txtValidateState':'success',
                                        'ctl00$cpH$ctlEditors$ctlRepeaterEditors$ctl00$ctlEditor$vpPeriod_txtValidateState':'success',
                                        'ctl00$cpH$ctlEditors$ctlRepeaterEditors$ctl00$ctlEditor$vpPosition_txtValidateState':'success',
                                        'ctl00$cpH$ctlEditors$ctlRepeaterEditors$ctl00$ctlEditor$vpTitle_txtValidateState':'success',
                                        'ctl00$cpH$ctlEditors$ctlRepeaterEditors$ctl00$ctlEditor$vpWebAddress_txtValidateState':'',
                                        'ctl00$cpH$cvtitle$tbCvTitle$ssPosition$ctlHiddenFieldValue': work_wishes.desirable_position.profession.encode('utf8'),
                                        'ctl00$cpH$cvtitleadditional$tbCvTitleAdditional$msPosition$ctlHiddenFieldValues':additional_res_name.encode('utf8'),
                                        'ctl00$cpH$cvtitleadditional$tbCvTitleAdditional$msPosition$ctlTextBox':'',
                                        'ctl00$cpH$ddlcurid':salary_um_dict[work_wishes.salary_um],
                                        'ctl00$cpH$objSelectWorkField$msWorkFields$ctlHiddenFieldValues':activity_fields_str.encode('utf8'),
                                        'ctl00$cpH$objSelectWorkField$msWorkFields$ctlTextBox':'',
                                        'ctl00$cpH$objlocation$msLocation$ctlHiddenFieldValues':city_str.encode('utf8'),
                                        'ctl00$cpH$objlocation$msLocation$ctlTextBox':'',
                                        'ctl00$cpH$tbcvExpSalaryFrom':salary_str,
                                        'ctl00$cpH$vpCvTitleAdditional_txtValidateState':'success',
                                        'ctl00$cpH$vpCvTitle_txtValidateState':'success',
                                        'ctl00$cpH$vpEmploymentKind_txtValidateState':'',
                                        'ctl00$cpH$vpEmploymentPlace_txtValidateState':'',
                                        'ctl00$cpH$vpEmploymentType_txtValidateState':'',
                                        'ctl00$cpH$vpLocations_txtValidateState':'success',
                                        'ctl00$cpH$vpSalaryFrom_txtValidateState':'success',
                                        'ctl00$cpH$vpWorkFields_txtValidateState':'success',
                                       
                                       }
                                                
        
        
        # !!!!!Не забыть вариант без опыта
        ii = 1
        exps = HotSpotWorkExperience.objects.filter(work_wishes=work_wishes)
        if exps.count() != 0:
            for exp in exps:
                i = str(ii)
                exp_data_dict['experienceAchievements_' + i] = exp.duties_achievements.encode('utf8')
                exp_data_dict['experienceCompanyValue_' + i] = exp.org_name.encode('utf8')
                if not exp.work_end_date:
                    exp_data_dict['experienceStillEmployed_' + i] = 'true'
                    exp_data_dict['experienceEndMonth_' + i] = '1'
                    exp_data_dict['experienceEndYear_' + i] = '2014'
                else:
                    exp_data_dict['experienceEndYear_' + i] = exp.work_end_date.year
                    exp_data_dict['experienceEndMonth_' + i] = exp.work_end_date.month
                exp_data_dict['experienceIndustry_' + i] = exp.branch_activity.job_ru_activity_id
                exp_data_dict['experiencePosition_' + i] = exp_pos[exp.taken_position_level]
                exp_data_dict['experienceStartMonth_' + i] = exp.work_start_date.month
                exp_data_dict['experienceStartYear_' + i] = exp.work_start_date.year
                exp_data_dict['experienceTitleValue_' + i] = exp.position.profession.encode('utf8')
                if not exp.org_site:
                    exp_data_dict['experienceWebAddress_' + i] = 'http://'
                else:
                    exp_data_dict['experienceWebAddress_' + i] = exp.org_site
                ii = ii + 1
        else:
            exp_data_dict['ctl00$cpH$cbCvWorkExperienceNotHave'] = 'on'
        
        exp_data_dict['ctl00$cpH$ctlEditors$ctlHiddenFieldLastId'] = ii
        
        
        
        exp_data = urllib.urlencode(exp_data_dict)
        
        resp = opener.open('http://www.job.ru/seeker/user/cv/create/experience/', exp_data)
        
        
        
        url_to_go = resp.geturl()
        get_param_pos = url_to_go.find('?')
        get_param = url_to_go[get_param_pos:]
        print get_param
        
        
        #==========================================================================================================================================
        # блок образование
        ed_and_skills = HotSpotWorkEducationAndSkills.objects.get(resume__id=resume_id)
        
        # уровень образования
        ed_level_dict = {1:'8',
                         2: '5',
                         3:'4',
                         4:'3',
                         5:'2',
                         6:'1',
                         7:'6',
                         8:'7',
                         
                         }
        # уровень образования
        if ed_and_skills.professional_skills:
            pr_skills_str = ed_and_skills.professional_skills
        else:
            pr_skills_str = ''
        
        
        
        
        edu_data_dict = { '__EVENTARGUMENT': '',
                                      '__EVENTTARGET': 'ctl00$cpH$btSave',
                                      '__VIEWSTATE': '/wEPDwUJMjEyNDEzNzg0DxYCHhNWYWxpZGF0ZVJlcXVlc3RNb2RlAgEWAmYPZBYCAgIPZBYCAgsPZBYOAgIPDxYEHghDc3NDbGFzcwUdaW5wdXRzX2ZpZWxkIHZhbGlkX2xpc3QgZXJyb3IeBF8hU0ICAmQWAgIBD2QWAgIBDxAPFgYeDURhdGFUZXh0RmllbGQFCGVkdVRpdGxlHg5EYXRhVmFsdWVGaWVsZAUFZWR1SWQeC18hRGF0YUJvdW5kZ2QQFQkd0JLRi9Cx0YDQsNGC0Ywg0YPRgNC+0LLQtdC90Ywf0J3QtdC/0L7Qu9C90L7QtSDRgdGA0LXQtNC90LXQtQ7QodGA0LXQtNC90LXQtSXQodGA0LXQtNC90LXQtSDRgdC/0LXRhtC40LDQu9GM0L3QvtC1HNCd0LXQvtC60L7QvdGHLiDQstGL0YHRiNC10LUO0KHRgtGD0LTQtdC90YIM0JLRi9GB0YjQtdC1A01CQRvQo9GH0LXQvdCw0Y8g0YHRgtC10L/QtdC90YwVCQABOAE1ATQBMwEyATEBNgE3FCsDCWdnZ2dnZ2dnZxYBZmQCBA9kFgQCAQ9kFgJmDxYCHgVjbGFzc2RkAgIPFgQfBgULcHNldWRvLWxpbmseCWlubmVyaHRtbAUrKyDQlNC+0LHQsNCy0LjRgtGMINC10YnQtSDQvtC00LjQvSDRj9C30YvQumQCBg8PFgIeBFRleHRlZGQCBw8WAh4LXyFJdGVtQ291bnQCBRYKZg9kFgQCAQ8QD2QWAh4FdmFsdWUFAzcwNmRkZAICDxUBAUFkAgEPZBYEAgEPEA9kFgIfCgUDNzA3ZGRkAgIPFQEBQmQCAg9kFgQCAQ8QD2QWAh8KBQM3MDhkZGQCAg8VAQFDZAIDD2QWBAIBDxAPZBYCHwoFAzcxMGRkZAICDxUBAURkAgQPZBYEAgEPEA9kFgIfCgUDNzA5ZGRkAgIPFQEBRWQCCg8WAh4Fc3R5bGVkFgICAQ8PFgQfAQUzaW5wdXRzX2ZpZWxkIGZ1bGxfc2l6ZSBmb3JtYXRfdHJpbSB2YWxpZF9zZWVrZXJfdXJsHwICAmQWAgIBD2QWAgIBDw8WAh8IZRYCHgpvbmtleXByZXNzBSFyZXR1cm4gRGlzYWJsZVN1Ym1pdChldmVudCxudWxsKTtkAgsPFgIfCwUNZGlzcGxheTpub25lOxYCAgEPDxYEHwEFM2lucHV0c19maWVsZCBmdWxsX3NpemUgZm9ybWF0X3RyaW0gdmFsaWRfc2Vla2VyX3VybB8CAgJkFgICAQ9kFgICAQ8PFgIfCGUWAh8MBSFyZXR1cm4gRGlzYWJsZVN1Ym1pdChldmVudCxudWxsKTtkAgwPFgIfCwUNZGlzcGxheTpub25lOxYCAgEPDxYEHwEFM2lucHV0c19maWVsZCBmdWxsX3NpemUgZm9ybWF0X3RyaW0gdmFsaWRfc2Vla2VyX3VybB8CAgJkFgICAQ9kFgICAQ8PFgIfCGUWAh8MBSFyZXR1cm4gRGlzYWJsZVN1Ym1pdChldmVudCxudWxsKTtkGAEFHl9fQ29udHJvbHNSZXF1aXJlUG9zdEJhY2tLZXlfXxYHBSBjdGwwMCRjcEgkckRsY0lkJGN0bDAwJGNiTGljZW5zZQUgY3RsMDAkY3BIJHJEbGNJZCRjdGwwMSRjYkxpY2Vuc2UFIGN0bDAwJGNwSCRyRGxjSWQkY3RsMDIkY2JMaWNlbnNlBSBjdGwwMCRjcEgkckRsY0lkJGN0bDAzJGNiTGljZW5zZQUgY3RsMDAkY3BIJHJEbGNJZCRjdGwwNCRjYkxpY2Vuc2UFFmN0bDAwJGNwSCRjYkhhc1ZlaGljbGUFE2N0bDAwJGNwSCRjYk1lZEJvb2s19ashcEzxAxPG1ZlbMyD29D2Z4A==',
                                        'ctl00$cpH$ctlAdditionalEditors$ctlRepeaterAdditionalEducations$ctl00$ctlAdditionalEducation$vpSchool_txtValidateState': 'success',
                                        'ctl00$cpH$ctlAdditionalEditors$ctlRepeaterAdditionalEducations$ctl00$ctlAdditionalEducation$vpTitle_txtValidateState': 'success',
                                        'ctl00$cpH$ctlAdditionalEditors$ctlRepeaterAdditionalEducations$ctl00$ctlAdditionalEducation$vpYear_txtValidateState': 'success',
                                        'ctl00$cpH$ctlEditors$ctlRepeaterEditors$ctl00$ctlEditor$vpInstitution_txtValidateState':'success',
                                        'ctl00$cpH$ctlEditors$ctlRepeaterEditors$ctl00$ctlEditor$vpSpecialty_txtValidateState':'success',
                                        'ctl00$cpH$ctlEditors$ctlRepeaterEditors$ctl00$ctlEditor$vpYear_txtValidateState':'success',
                                        'ctl00$cpH$ddleduID':ed_level_dict[ed_and_skills.education_level],
                                        'ctl00$cpH$tbProffesionalSkill':pr_skills_str.encode('utf8'),
                                        'ctl00$cpH$vpEducationLevel_txtValidateState':'success',
                                       
                                       }
        
        
        
        
        KM = {'educationId_1':'',
                                        'educationInstitutionValue_1':'Vjjusfsd',
                                        'educationSpecialty_1':'Skdfhsdh',
                                        'educationYear_1':'2001',
                                          'ctl00_cpH_languageSelector_hidLang_0':'',
                                        'ctl00_cpH_languageSelector_selLvl_0':'',
                                        'ctl00_cpH_languageSelector_validIHidden_0':'',
                                        'additionalEducationSchool_1': '',
                                        'additionalEducationTitle_1':'',
                                        'additionalEducationYear_1': '',
                                         'ctl00$cpH$ctlAdditionalEditors$ctlHiddenFieldLastId':'1',
                                         
                                          'ctl00$cpH$tbP1':'http://',
                                        'ctl00$cpH$tbP2':'http://',
                                        'ctl00$cpH$tbP3':'http://',
                                        'ctl00$cpH$vpPortfolio1_txtValidateState':'success',
                                        'ctl00$cpH$vpPortfolio2_txtValidateState':'success',
                                        'ctl00$cpH$vpPortfolio3_txtValidateState':'success', }
        
        
        
        # водительские права
        if ed_and_skills.driving_license_A == True:
            edu_data_dict['ctl00$cpH$rDlcId$ctl00$cbLicense'] = 'on'
        if ed_and_skills.driving_license_B == True:
            edu_data_dict['ctl00$cpH$rDlcId$ctl01$cbLicense'] = 'on'
        if ed_and_skills.driving_license_C == True:
            edu_data_dict['ctl00$cpH$rDlcId$ctl02$cbLicense'] = 'on'
        if ed_and_skills.driving_license_D == True:
            edu_data_dict['ctl00$cpH$rDlcId$ctl03$cbLicense'] = 'on'
        if ed_and_skills.driving_license_E == True:
            edu_data_dict['ctl00$cpH$rDlcId$ctl04$cbLicense'] = 'on'
        
        # мед справка и личный автомобиль
        if ed_and_skills.has_car == True:
            edu_data_dict['ctl00$cpH$cbHasVehicle'] = 'on'
        if ed_and_skills.has_medical_book == True:
            edu_data_dict['ctl00$cpH$cbMedBook'] = 'on'
        
        
        jj = 1
        # все учебные заведения(минимум одно)
        ed_and_skills = HotSpotWorkEducationAndSkills.objects.get(resume__id=resume_id)
        ed_insts = HotSpotWorkEducationalInstitution.objects.filter(education_and_skills=ed_and_skills)
        for ed_inst in ed_insts:
            j = str(jj)
            edu_data_dict['educationId_' + j] = ''
            edu_data_dict['educationInstitutionValue_' + j] = ed_inst.institution_name.encode('utf8')
            edu_data_dict['educationSpecialty_' + j] = ed_inst.faculty_specialty.encode('utf8')
            edu_data_dict['educationYear_' + j] = ed_inst.graduate_year
            jj = jj + 1
        edu_data_dict['ctl00$cpH$ctlEditors$ctlHiddenFieldLastId'] = jj
        
        
        ll = 0
        # уровни языка
        lan_level_dict = {1:'1', 2:'3', 3:'2'}
        # все иностранные языки
        for_lans = HotSpotWorkForeignLanguagesProf.objects.filter(education_and_skills=ed_and_skills)
        if for_lans.count() > 0:
            for lan in for_lans:
                l = str(ll)
                # print lan.language.language
                edu_data_dict['ctl00_cpH_languageSelector_hidLang_' + l] = lan.language.job_ru_lan_id
                edu_data_dict['ctl00_cpH_languageSelector_validIHidden_' + l] = 'success'
                edu_data_dict['ctl00_cpH_languageSelector_selLvl_' + l] = lan_level_dict[lan.proficiency_language_level]
                ll = ll + 1
                
        
        
        # дополнительное образование
        add = 1
        add_eds = HotSpotWorkAdditionalEducation.objects.filter(education_and_skills=ed_and_skills)
        if add_eds.count() > 0:
            for add_ed in add_eds:
                ad = str(add)
                edu_data_dict['additionalEducationSchool_' + ad] = add_ed.institution_name.encode('utf8')
                edu_data_dict['additionalEducationTitle_' + ad] = add_ed.course_name.encode('utf8')
                edu_data_dict['additionalEducationYear_' + ad] = add_ed.graduate_year_ad
                add = add + 1
            edu_data_dict['ctl00$cpH$ctlAdditionalEditors$ctlHiddenFieldLastId'] = ad
        
        
        
        # портфолио
        pp = 1
        ports = HotSpotWorkPortfolio.objects.filter(education_and_skills=ed_and_skills)
        if ports.count() > 0:
            for port in ports:
                p = str(pp)
                edu_data_dict['ctl00$cpH$tbP' + p] = 'http://' + port.portfolio_link
                edu_data_dict['ctl00$cpH$vpPortfolio' + p + '_txtValidateState'] = 'success'
                pp = pp + 1
                
        
        
                
        edu_data = urllib.urlencode(edu_data_dict)
        edu = 'http://www.job.ru/seeker/user/cv/create/education/' + get_param
        resp = opener.open(edu, edu_data)
        
        
        
        # делаем проверку успешно ли создано резюме
        login_to_job_ru(mail_name, pas)
        preview = 'http://www.job.ru/seeker/user/cv/preview/' + get_param
        resp = opener.open(preview)
        review_resp = resp.read()
        soup = BeautifulSoup(review_resp)
        activation_button = soup.find('a', id='ctl00_cpH_btPublishDown')
        if not activation_button.has_key('disabled'):
            # отправляем на модерацию
            publish_data_dict = { '__EVENTARGUMENT': '',
                                      '__EVENTTARGET': 'ctl00$cpH$btPublishDown',
                                      '__VIEWSTATE': '/wEPDwUJNzQwMzUzODUzDxYCHhNWYWxpZGF0ZVJlcXVlc3RNb2RlAgEWAmYPZBYCAgIPZBYCAgsPZBYOAgQPDxYCHgdWaXNpYmxlaGRkAgUPZBYCZg8WAh8BZxYCAgEPDxYEHghDc3NDbGFzcwUNYnV0dG9uLXN1Ym1pdB4EXyFTQgICFgIeB29uY2xpY2sFWWlmICh0eXBlb2YgX2dhcSAhPSAndW5kZWZpbmVkJykgeyBfZ2FxLnB1c2goWydfdHJhY2tQYWdldmlldycsICcvY2xpY2thbmRzZW5kcmVzdW1lJ10pOyB9ZAIGDxYCHgRUZXh0BRXQsiDRh9C10YDQvdC+0LLQuNC60LVkAgcPZBYCZg8WAh8BZxYCAgEPDxYEHwIFDWJ1dHRvbi1zdWJtaXQfAwICFgIfBAVZaWYgKHR5cGVvZiBfZ2FxICE9ICd1bmRlZmluZWQnKSB7IF9nYXEucHVzaChbJ190cmFja1BhZ2V2aWV3JywgJy9jbGlja2FuZHNlbmRyZXN1bWUnXSk7IH1kAgkPZBYCAgEPFgIfBWVkAgwPDxYCHwFoZGQCEA8PFgIfAWhkZBgDBR5fX0NvbnRyb2xzUmVxdWlyZVBvc3RCYWNrS2V5X18WAQUfY3RsMDAkY3BIJHZTZXR0aW5ncyRjaEF1dG9BcHBseQUVY3RsMDAkY3BIJG12UHVibGlzaFVwDw9kZmQFF2N0bDAwJGNwSCRtdlB1Ymxpc2hEb3duDw9kZmT0BMqtdCLLq/nfoOcMmThx82g5Sw==',
                                       'ctl00$cpH$vSettings$chAutoApply':'on',
                                       'ctl00$cpH$vSettings$tbExclude$msEmployer$ctlHiddenFieldValues':'',
                                       'ctl00$cpH$vSettings$tbExclude$msEmployer$ctlTextBox':'',
                                       'ctl00$cpH$vSettings$vpSalaryFrom_txtValidateState':'',
                                       'ctl00_cpH_vSettings_ctlPanelPopupContainer_visibility':'2',
                                       }
            publish_data = urllib.urlencode(publish_data_dict)
            resp = opener.open(preview, publish_data)  #непосредственно отправка на модерацию!!!!!!!!!!!!!
            jrcr = HotSpotWorkJobRuCreated(username=username, mobi_mail=mail_name, mobi_mail_pas=pas, type=1, doc_id=resume_id, get_param=get_param)
            jrcr.save()
            # отправляем юзеру письмо
            send_email("Вы были зарегестрированы на сайте JOB.RU.", "  Ваша новый почтовый ящик, с которотого вы зарегестрированы на JOB.RU:логин %s, пароль %s;  Ваши логин и пароль на сайте JOB.RU:  лoгин  %s; пароль  %s" % (mail_name.encode('utf8'), pas.encode('utf8'), mail_name.encode('utf8'), pas.encode('utf8')), settings.DEFAULT_FROM_EMAIL, [email_specified_by_user])
    
        
