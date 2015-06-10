# coding: utf-8
# from django.utils.translation import ugettext_lazy as _
from content.TemplateVars import Variable, VarValue
# from billing.models import SignedContract
from account.models import ADDRESS_TYPE_LEGAL, ADDRESS_TYPE_POSTAL, ADDRESS_TYPE_PHYSICAL
from findocs.models import FinDocSigned
from django.contrib.auth.models import User
from models import Profile
from findocs.models import FinDocSignApplication
def GetVariables():

    class UserVarValue(VarValue):

        def getValue(self):
            # self.mark_safe = True
            request = self.init_kwargs.get("request")
            if not request:
                return "<REQUEST not in self.init_kwargs!!!>"
            user = self.init_kwargs.get("user")
            #-----------------------------------
            # добавивим для подписания договора из админки
            try:
                findocapp_id = self.init_kwargs.get("findocapp_id")
                findoc_app_user_obj = FinDocSignApplication.objects.get(pk=findocapp_id)
                user = findoc_app_user_obj.assigned_to
            except:
                pass
            #-----------------------------------
            if user == None:
                user = request.user

            try:
                profile = user.get_profile()
            except:
                return ""

            option = self.args[0]

            if   option == "user_username":
                return user.username
            elif option == "tel_doc":
                try:
                    t = User.objects.get(username=user.username)
                    a = FinDocSigned.objects.get(signed_by=user, findoc=1)

                    return str(a.id)
                except Exception, e:
                    pass
                    return 0
                # print "1"
                # print a

            elif option == "fu":
                t = User.objects.get(username=user.username)
                z = Profile.objects.get(user=t)
                p = z.first_name + " " + z.second_name + " " + z.last_name
                return p

            elif option == "user_date_joined":
                return user.date_joined
            elif option == "user_date_joined":
                return user.date_joined
            elif option == "user_date_joined":
                return user.date_joined
            elif option == "user_date_joined":
                return user.date_joined
            elif option == "user_email":
                return user.email
            elif option == "user_last_login":
                return user.last_login
            
            elif option == "user_address_postal":
                return profile.address(ADDRESS_TYPE_POSTAL)
            elif option == "user_address_legal":
                return profile.address(ADDRESS_TYPE_LEGAL)
            elif option == "user_address_physical":
                return profile.address(ADDRESS_TYPE_PHYSICAL)

            elif option == "user_address_legal_city":
                return profile.addresses.values()[0]["city"]
            elif option == "user_address_legal_country":
                return profile.addresses.values()[0]["country"]
            elif option == "user_address_legal_zipcode":
                return profile.addresses.values()[0]["zipcode"]
            elif option == "user_address_legal_state":
                return profile.addresses.values()[0]["state"]
            elif option == "user_address_legal_address_line":
                return profile.addresses.values()[0]["address_line"]

            elif option == "user_address_physical_city":
                return profile.addresses.values()[2]["city"]
            elif option == "user_address_physical_country":
                return profile.addresses.values()[2]["country"]
            elif option == "user_address_physical_zipcode":
                return profile.addresses.values()[2]["zipcode"]
            elif option == "user_address_physical_state":
                return profile.addresses.values()[2]["state"]
            elif option == "user_address_physical_address_line":
                return profile.addresses.values()[2]["address_line"]

            elif option == "user_address_postal_city":
                return profile.addresses.values()[1]["city"]
            elif option == "user_address_postal_country":
                return profile.addresses.values()[1]["country"]
            elif option == "user_address_postal_zipcode":
                return profile.addresses.values()[1]["zipcode"]
            elif option == "user_address_postal_state":
                return profile.addresses.values()[1]["state"]
            elif option == "user_address_postal_address_line":
                return profile.addresses.values()[1]["address_line"]

            elif option == "legal_form":
                if profile.legal_form:
                    legal_form = profile.legal_form
                else:
                    legal_form = ''
                return legal_form
            elif option == "akcept":
                if not profile.is_juridical:
                    akcept = '''<p align="center">
                                <strong>%(title_akcept)s</strong></p>
                                <p>&ndash;&nbsp;&nbsp;&nbsp;%(point_1)s</p>
                                <p>&ndash;&nbsp;&nbsp;&nbsp;%(point_2)s</p>'''
                    akcept = akcept % {
                                       'title_akcept' : u'АКЦЕПТ ДОГОВОРА',
                                       'point_1' : u'''Свидетельством полного и безоговорочного акцепта (принятия) 
                                            условий данного Договора является предоставление данных о себе и осуществление 
                                            оплаты услуг согласно настоящего Договора.''',
                                       'point_2' : u'''В соответствии со ст. 438 ГК РФ между ОПЕРАТОРОМ и АБОНЕНТОМ настоящий Договор 
                                            считается заключенным, если АБОНЕНТ произвел авансовый платеж 100 % оплату по тарифному плану 
                                            и стоимости подключения.''',
                                       }
                else:
                    akcept = ''
                return akcept
            elif option == "user_company_name":
                if profile.is_juridical == True:
                    company_name_or_family = u"«" + profile.company_name + u"»"
                if profile.is_juridical == False:
                    if profile.last_name:
                        last_name = profile.last_name
                    else:
                        last_name = ""
                    if profile.first_name:
                        first_name = profile.first_name
                    else:
                        first_name = ""
                    if profile.second_name:
                        second_name = profile.second_name
                    else:
                        second_name = ""
                    company_name_or_family = last_name + " " + first_name + " " + second_name
                return company_name_or_family
            elif option == "user_general_director":
                return profile.general_director
            elif option == "sign_face":
                sign_face = ''
                if profile.is_juridical:
                    if profile.sign_face:
                        sign_face = profile.sign_face
                else:
                    try:
                        sign_face = unicode(profile.first_name) + u' ' + unicode(profile.second_name) + u' ' + unicode(profile.last_name)
                    except:
                        pass
                return sign_face
            elif option == "sign_cause":
                if profile.is_juridical == True:
                    sign_cause = profile.sign_cause
                if profile.is_juridical == False:
                    sign_cause = u'паспорта ' + unicode(profile.pasport_serial)
                return sign_cause
            elif option == "address":
                if profile.is_juridical == True:
                    juridical = '''
                        <tr>
                            <td style="width:611px; height:42px; vertical-align: top;">
                                    <u>%(str_jur_address)s</u>:
                            </td>
                            <td style="width:516px; padding-right:50px; height:42px; vertical-align: top;">
                                    %(user_address_legal)s
                            </td>
                        </tr>
                        <tr>
                            <td style="width:611px; height:42px; vertical-align: top;">
                                    <u>%(str_fact_address)s:</u>
                            </td>
                            <td style="width:516px; height:42px;   vertical-align: top;">
                                    %(user_address_postal)s
                            </td>
                        </tr>
                        <tr>
                            <td style="width:611px; height:42px; vertical-align: top;">
                                    <u>%(str_postal_address)s</u>:
                            </td>
                            <td style="width:516px; height:42px; padding-right:300px; vertical-align: top;">
                                    %(user_address_postal)s
                            </td>
                        </tr>'''
                    try:
                        user_address_legal = profile.address(ADDRESS_TYPE_LEGAL)
                    except Exception, e:
                        print e
                    try:
                        user_address_postal = profile.address(ADDRESS_TYPE_POSTAL)
                    except Exception, e:
                        print e
                    juridical = juridical % {
                                             "str_jur_address" : u'Юридический адрес',
                                             "str_fact_address": u'Фактический адрес',
                                             "str_postal_address": u'Почтовый адрес',
                                             "user_address_legal": user_address_legal,
                                             "user_address_postal": user_address_postal,
                                             }
                if profile.is_juridical == False:
                    juridical = '''
                    <tr>
                        <td style="width:611px; height:42px; vertical-align: top;"><u>%(str_phys_address)s</u>
                        </td>
                        <td style="width:516px; height:42px; vertical-align: top;">%(phys_address)s
                        </td>
                    </tr>'''
                    try:
                        address = profile.address(ADDRESS_TYPE_PHYSICAL)
                    except Exception, e:
                        print e
                        address = ''
                    juridical = juridical % {
                                             "str_phys_address": u'Физический адрес',
                                             "phys_address": address,
                                             }
                return juridical
            elif option == "requisites":
                if profile.is_juridical == True:
                    requisites = '''<tr>
                            <td style="width:611px; height:42px; vertical-align: top;">
                                    <u>%(inn_kpp)s</u>:
                            </td>
                            <td style="width:516px; height:42px; vertical-align: top;">
                                <p>
                                    %(user_inn)s</p>
                            </td>
                        </tr>
                        <tr>
                            <td style="width:611px; height:42px; vertical-align: top;">
                                    <u>%(bank_requisites)s</u>:
                            </td>
                            <td style="width:516px; height:42px; vertical-align: top;">
                                <p>
                                    %(bank)s%(user_bank_name)s</p>
                                <p>
                                    %(rs)s%(user_settlement_account)s</p>
                                <p>
                                    %(ks)s%(user_correspondent_account)s</p>
                                <p>
                                    %(bik)s%(user_bik)s</p>
                            </td>
                        </tr>'''
                    try:
                        user_inn = profile.bank_address
                    except Exception, e:
                        print e
                        user_inn = ''
                    try:
                        user_kpp = profile.kpp
                    except Exception, e:
                        print e
                        user_kpp = ''
                    try:
                        user_bank_name = profile.bank_name
                    except Exception, e:
                        print e
                        user_bank_name = ''
                    try:
                        user_settlement_account = profile.settlement_account
                    except Exception, e:
                        print e
                        user_settlement_account = ''
                    try:
                        user_correspondent_account = profile.correspondent_account
                    except Exception, e:
                        print e
                        user_correspondent_account = ''
                    try:
                        user_bik = profile.bik
                    except Exception, e:
                        print e
                        user_bik = ''
                    requisites = requisites % {
                                               "inn_kpp": u'ИНН / КПП',
                                               "bank_requisites": u'Банковские реквизиты',
                                               "bank": u'Банк: ',
                                               "rs": u'р/с: ',
                                               "ks": u'к/с: ',
                                               "bik": u'БИК: ',
                                               "user_inn": user_inn + u'/' + user_kpp,
                                               "user_bank_name": user_bank_name,
                                               "user_settlement_account": user_settlement_account,
                                               "user_correspondent_account": user_correspondent_account,
                                               "user_bik": user_bik,
                                               }
                if profile.is_juridical == False:
                    requisites = '''<tr>
                            <td style="width:611px; height:42px; vertical-align: top;">
                                    <u>%(str_passport)s</u>:
                            </td>
                            <td style="width:516px; height:42px; vertical-align: top;">
                                <p>
                                    %(str_pasport_serial)s%(pasport_serial)s</p>
                                <p>
                                    %(str_when_given_out)s%(when_given_out)s</p>
                                <p>
                                    %(str_by_whom_given_out)s%(by_whom_given_out)s</p>
                            </td>
                        </tr>'''
                    try:
                        pasport_serial = profile.pasport_serial
                    except Exception, e:
                        print e
                        pasport_serial = ''
                    try:
                        when_given_out = profile.when_given_out
                    except Exception, e:
                        print e
                        when_given_out = ''
                    try:
                        by_whom_given_out = profile.by_whom_given_out
                    except Exception, e:
                        print e
                        by_whom_given_out = ''
                    requisites = requisites % {
                                               "str_passport": u'Паспортные данные',
                                               "str_pasport_serial": u'Номер паспорта: ',
                                               "pasport_serial": pasport_serial,
                                               "str_when_given_out": u'Когда выдан: ',
                                               "when_given_out": when_given_out,
                                               "str_by_whom_given_out": u'Кем выдан: ',
                                               "by_whom_given_out": by_whom_given_out,
                                               }

                return requisites
            elif option == "pasport":
                if profile.is_juridical == False:
                    try:
                        pasport = profile.pasport_serial + u', выдан ' + str(profile.when_given_out) + u' ' + profile.by_whom_given_out + u','
                    except Exception, e:
                        print e
                        pasport = ''
                if profile.is_juridical == True:
                    pasport = ''
                return pasport
            elif option == "address_phys_legal":
                if profile.is_juridical == False:
                    try:
                        address_phys_legal = profile.address(ADDRESS_TYPE_PHYSICAL)
                    except Exception, e:
                        print e
                        address_phys_legal = ''
                if profile.is_juridical == True:
                    try:
                        address_phys_legal = profile.address(ADDRESS_TYPE_LEGAL)
                    except Exception, e:
                        user_address_legal = ''
                return address_phys_legal
            elif option == "user_bank_name":
                return profile.bank_name
            elif option == "user_inn":
                return profile.bank_address  # @attention: Проверить, корректно ли это вообще!
            elif option == "user_activated_at":
                return profile.activated_at
            elif option == "user_bik":
                return profile.bik
            elif option == "user_settlement_account":
                return profile.settlement_account
            elif option == "user_correspondent_account":
                return profile.correspondent_account
            elif option == "user_has_external_numbers":
                return profile.has_external_numbers()
            elif option == "user_has_inactive_phones":
                return profile.has_inactive_phones()
            elif option == "user_is_juridical":
                return profile.is_juridical
            elif option == "user_modified_at":
                return profile.modified_at
            elif option == "user_okpo":
                return profile.okpo
            elif option == "user_contact_phone_fax":
                if profile.phones:
                    phones = profile.phones
                else:
                    phones = ''
                return phones
            elif option == "v_lice_user_sign_face":
                sign_face = ''
                if profile.is_juridical:
                    if profile.sign_face_in_a_genitive_case:
                        sign_face = profile.sign_face_in_a_genitive_case
                if profile.is_juridical:
                    v_lice_user_sign_face = u' в лице %s' % sign_face + u","
                else:
                    v_lice_user_sign_face = ''
                return v_lice_user_sign_face
            elif option == "kpp":
                return profile.kpp
    result = [
        Variable(
            "fu",
            u"Полное имя пользавателя",
            UserVarValue("fu")
        ),
        Variable(
            "tel_doc",
            u"Номер договора на телематику",
            UserVarValue("tel_doc")
        ),
              
        Variable(
            "user_username",
            u"Имя пользователя",
            UserVarValue("user_username")
        ),
        Variable(
            "user_email",
            u"Электронная почта пользователя",
            UserVarValue("user_email")
        ),
        Variable(
            "user_date_joined",
            u"Дата регистрации пользователя",
            UserVarValue("user_date_joined")
        ),
        Variable(
            "user_last_login",
            u"Дата последнего входа пользователя",
            UserVarValue("user_last_login")
        ),

        Variable(
            "user_address_postal",
            u"Почтовый адрес",
            UserVarValue("user_address_postal")
        ),
        Variable(
            "user_address_legal",
            u"Юридический адрес",
            UserVarValue("user_address_legal")
        ),
        Variable(
            "user_address_physical",
            u"Физический адрес",
            UserVarValue("user_address_physical")
        ),
        Variable(
            "user_address_physical_city",
            u"Город",
            UserVarValue("user_address_physical_city")
        ),
        Variable(
            "user_address_physical_country",
            u"Страна",
            UserVarValue("user_address_physical_country")
        ),
        Variable(
            "user_address_physical_zipcode",
            u"Почтовый индекс",
            UserVarValue("user_address_physical_zipcode")
        ),
        Variable(
            "user_address_physical_state",
            u"Штат/область",
            UserVarValue("user_address_physical_state")
        ),
        Variable(
            "user_address_physical_address_line",
            u"Полная строка",
            UserVarValue("user_address_physical_address_line")
        ),
        Variable(
            "user_address_physical_city",
            u"Город юридического адреса",
            UserVarValue("user_address_legal_city")
        ),
        Variable(
            "user_address_legal_country",
            u"Страна юридического адреса",
            UserVarValue("user_address_legal_country")
        ),
        Variable(
            "user_address_legal_zipcode",
            u"Почтовый индекс юридического адреса",
            UserVarValue("user_address_legal_zipcode")
        ),
        Variable(
            "user_address_legal_state",
            u"Штат/область юридического адреса",
            UserVarValue("user_address_legal_state")
        ),
        Variable(
            "user_address_legal_address_line",
            u"Полная строка юридического адреса",
            UserVarValue("user_address_legal_address_line")
        ),

        Variable(
            "user_address_postal_city",
            u"Почтовый адрес",
            UserVarValue("user_address_postal_city")
        ),
        Variable(
            "user_address_postal_country",
            u"Страна почтового адреса",
            UserVarValue("user_address_postal_country")
        ),
        Variable(
            "user_address_postal_zipcode",
            u"Почтовый индекс почтового адреса",
            UserVarValue("user_address_postal_zipcode")
        ),
        Variable(
            "user_address_postal_state",
            u"Штат/область почтового адреса",
            UserVarValue("user_address_postal_state")
        ),
        Variable(
            "user_address_postal_address_line",
            u"Штат/область почтового адреса",
            UserVarValue("user_address_postal_address_line")
        ),

        Variable(
            "legal_form",
            u"Правовая форма компании(к примеру ОАО)",
            UserVarValue("legal_form")
        ),
        Variable(
            "akcept",
            u"Возвращет акцепт в договор",
            UserVarValue("akcept")
        ),
        Variable(
            "user_company_name",
            u"Название компании",
            UserVarValue("user_company_name")
        ),
        Variable(
            "user_general_director",
            u"Генеральный директор",
            UserVarValue("user_general_director")
        ),
        Variable(
            "user_sign_face",
            u"Лицо, подписывающее договоры",
            UserVarValue("sign_face")
        ),
        Variable(
            "user_sign_cause",
            u"На основании чего будут подписываться договоры (устав или другое)",
            UserVarValue("sign_cause")
        ),
        Variable(
            "pasport",
            u"Данные паспорта",
            UserVarValue("pasport")
        ),
       Variable(
            "address",
            u"Возвращает кусок таблицы с адресом",
            UserVarValue("address")
        ),
       Variable(
            "address_phys_legal",
            u"Возвращает физический или юридичсекий адрес",
            UserVarValue("address_phys_legal")
        ),
       Variable(
            "requisites",
            u"возвращает кусок таблицы с реквизитами",
            UserVarValue("requisites")
        ),
        Variable(
            "user_bank_name",
            u"Имя банка",
            UserVarValue("user_bank_name")
        ),
        Variable(
            "user_inn",
            u"ИНН",
            UserVarValue("user_inn")
        ),
        Variable(
            "user_activated_at",
            u"Дата активации пользователя",
            UserVarValue("user_activated_at")
        ),
        Variable(
            "user_bik",
            u"БИК",
            UserVarValue("user_bik")
        ),
        Variable(
            "user_settlement_account",
            u"Рассчетный счет",
            UserVarValue("user_settlement_account")
        ),
        Variable(
            "user_correspondent_account",
            u"Корреспондентский счет",
            UserVarValue("user_correspondent_account")
        ),
        Variable(
            "user_has_external_numbers",
            u"Есть ли у пользователя внешние номера?",
            UserVarValue("user_has_external_numbers")
        ),
        Variable(
            "user_has_inactive_phones",
            u"Есть ли у пользователя неактивные номера?",
            UserVarValue("user_has_inactive_phones")
        ),
        Variable(
            "user_is_juridical",
            u"Пользователь - юридическое лицо?",
            UserVarValue("user_is_juridical")
        ),
        Variable(
            "user_modified_at",
            u"Дата изменения информации пользователя?",
            UserVarValue("user_modified_at")
        ),
        Variable(
            "user_okpo",
            u"ОКПО",
            UserVarValue("user_okpo")
        ),
        Variable(
            "user_contact_phone_fax",
            u"Контактный телефон/факс",
            UserVarValue("user_contact_phone_fax")
        ),
        Variable(
            "v_lice_user_sign_face",
            u"Возвращает текст типа: в лице ФИО",
            UserVarValue("v_lice_user_sign_face")
        ),
        Variable(
            "kpp",
            u"КПП",
            UserVarValue("kpp")
        ),
    ]

    return result





