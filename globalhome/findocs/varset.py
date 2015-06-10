# coding: utf-8
from content.TemplateVars import Variable, VarValue
from findocs.models import FinDocSignApplication, FinDocSigned, FinDocSignedZakazy, FinDoc
from findocs.views import Package_on_connection_of_service
from django.db import connections, transaction
from django.conf import settings
from findocs import get_signed
from data_centr.models import Zakazy, Tariff, Price, Service_type, Servers
from data_centr.views import cost_dc, cost_calculation, cost_activated_zakaz, colocation_cost_zakaz, rack_cost_zakaz
from data_centr.forms import AccountColocationForm, AccountRackForm
from content.views import perewod
from django.contrib.auth.models import User
from account.models import Profile
from externalnumbers.models import ExternalNumber
from django.core.urlresolvers import reverse
from django.http import Http404
from account.content_varset import GetVariables as gv
from account.models import ADDRESS_TYPE_LEGAL, ADDRESS_TYPE_POSTAL, ADDRESS_TYPE_PHYSICAL
import datetime
from django.db.models import Q
from dateutil.relativedelta import relativedelta  # @UnresolvedImport
from django.forms.formsets import formset_factory
from account.forms import AddressLegalForm, AddressPostalForm, ProfileJuridicalDataMainForm, ProfileJuridicalDataAdditionalForm, ProfileJuridicalDataIgnoredForm
import log
# imports
from django.core.exceptions import ObjectDoesNotExist

def GetVariables():
    class FinDocVarValue(VarValue):

        def getValue(self):

            findocapp_id = self.init_kwargs.get("findocapp_id")

            # получаем юзера из заявки
            findoc_app_user_obj = FinDocSignApplication.objects.get(pk=findocapp_id)
            findoc_app_user = findoc_app_user_obj.assigned_to
            #======================================================
            option = self.kwargs.get("option")
            request = self.init_kwargs["request"]
            user = findoc_app_user  # из заявки
            # user = request.user  #orig


            # пакет из GET данных
            try:
                pack_id = request.GET['pack_id']
            except KeyError:
                pass

            try:
                zakaz_id = request.GET['zakaz_id']
                url_after_sign_got = '/account/equipment_rent_list/zakaz/' + str(zakaz_id) + '/'
            except KeyError:
                pass


            profile_obj = Profile.objects.get(user=user)
            con = connections[settings.GLOBALHOME_DB2].cursor()


            def get_zayavka():
                #con = connections[settings.GLOBALHOME_DB2].cursor()
                findoc = FinDocSignApplication.objects.get(id=findocapp_id)
                params_data = findoc.unpickle_params()
                return params_data


            if   option == "findoc_number":
                return findocapp_id

            elif option == 'number_act_arenda_obor':
                try:
                    findoc_sign_zak = FinDocSignedZakazy.objects.get(zakaz_id=zakaz_id, fin_doc__findoc__slug='dogovor_arendi_serverov')
                    # находим заказы относящиеся к этому договору
                    zakazy_exist = FinDocSignedZakazy.objects.filter(fin_doc__id=findoc_sign_zak.fin_doc.id)
                    # считаем их количество
                    col = 0
                    for i in zakazy_exist:
                        try:
                            # посчитаем все заказы у которых есть подписанный договор 'akt_priema_peredachi_oborudovaniya_2'
                            find_zak_to_calc = FinDocSignedZakazy.objects.get(zakaz_id=i.zakaz_id, fin_doc__findoc__slug='akt_priema_peredachi_oborudovaniya_2')
                            col = col + 1
                        except FinDocSignedZakazy.DoesNotExist:
                            pass
                    col = col + 2
                    log.add(col)
                    return col
                except:
                    return 1  # orig








            elif option == 'number_arenda_obor':
                try:
                    package_obj = Package_on_connection_of_service.objects.get(user=user, activate=True, deactivate=False, activate_admin=False, id=pack_id)
                except:
                    try:
                        package_obj = Package_on_connection_of_service.objects.get(user=user, activate=True, deactivate=False, activate_admin=False, url_after_sign=url_after_sign_got)
                    except:
                        package_obj = Package_on_connection_of_service.objects.get(user=user, activate=False, deactivate=False)  # orig


                try:
                    findocsign_queryset = package_obj.findoc_sign.filter(findoc__slug='dogovor_arendi_serverov')  # orig
                    findocsign_obj = findocsign_queryset[0]  # orig
                    return findocsign_obj.id
                except:
                    findoc_sign_zak = FinDocSignedZakazy.objects.get(zakaz_id=zakaz_id, fin_doc__findoc__slug='dogovor_arendi_serverov')
                    return findoc_sign_zak.fin_doc.id

            elif option == 'date_arenda_obor':
                try:
                    package_obj = Package_on_connection_of_service.objects.get(user=user, activate=True, deactivate=False, activate_admin=False, id=pack_id)
                except:
                    try:
                        package_obj = Package_on_connection_of_service.objects.get(user=user, activate=True, deactivate=False, activate_admin=False, url_after_sign=url_after_sign_got)
                    except:
                        package_obj = Package_on_connection_of_service.objects.get(user=user, activate=False, deactivate=False)  # orig

                try:
                    findocsign_queryset = package_obj.findoc_sign.filter(findoc__slug='dogovor_arendi_serverov')  # orig
                    findocsign_obj = findocsign_queryset[0]  # orig
                except:
                    findoc_sign_zak = FinDocSignedZakazy.objects.get(zakaz_id=zakaz_id, fin_doc__findoc__slug='dogovor_arendi_serverov')
                    findocsign_obj = FinDocSigned.objects.get(id=findoc_sign_zak.fin_doc.id)
                return datetime.datetime.strftime(findocsign_obj.signed_at, "%d.%m.%Y")

            elif option == 'equipment_arenda_obor':
                try:
                    package_obj = Package_on_connection_of_service.objects.get(user=user, activate=True, deactivate=False, activate_admin=False, id=pack_id)
                except:
                    try:
                        package_obj = Package_on_connection_of_service.objects.get(user=user, activate=True, deactivate=False, activate_admin=False, url_after_sign=url_after_sign_got)
                    except:
                        package_obj = Package_on_connection_of_service.objects.get(user=user, activate=False, deactivate=False)  # orig
                data = eval(package_obj.data)
                spis_equipment = data['spis_equipment']
                table = ''
                i = 0
                for key, value in spis_equipment.iteritems():
                    i += 1
                    tariff_obj = Tariff.objects.get(id=key)
                    table += '''
                         <tr>
                             <td style='text-align:center'>%s</td>
                             <td>%s</td>
                             <td style='text-align:center'>%s</td>
                             <td></td>
                         </tr>
                         ''' % (i, tariff_obj.equipment, value)
                return table



            elif option == 'findoc_number_poddelka':
                findoc_sign = FinDocSigned.objects.get(findoc__slug='telematic_data_centr', signed_by__id=user.id, cancellation_date__isnull=True)
                return findoc_sign.id
            elif option == 'date_poddelka':
                month_texts2 = (u"января", u"февраля", u"марта", u"апреля", u"мая", u"июня", u"июля", u"августа",
                                u"сентября", u"октября", u"ноября", u"декабря")
                findoc_sign = FinDocSigned.objects.get(findoc__slug='telematic_data_centr', signed_by__id=user.id, cancellation_date__isnull=True)
                date_poddelka = u'«%s» %s %s' % (findoc_sign.signed_at.day, month_texts2[findoc_sign.signed_at.month - 1], findoc_sign.signed_at.year)
                return date_poddelka

            elif option == "telematic_data_centr":
                sd = get_signed(user, "telematic_data_centr")
                return sd.id
            elif option == "telematic_services_contract":
                sd = get_signed(user, "telematic_services_contract")
                return sd.id
            elif option == "localphone_services_contract":
                sd = get_signed(user, "localphone_services_contract")
                return sd.id
            elif option == "remove_number_oferta":
                package_obj = Package_on_connection_of_service.objects.get(user=user, activate=False, deactivate=False)
                data = eval(package_obj.data)
                slugs_list_temp = package_obj.slugs_document
                slugs_list = slugs_list_temp.split(', ')
                count_oferta = slugs_list.count('remove_dogovor_oferta')
                log.add( u'%s/ОФ' % data['dogovor_oferta'][count_oferta - 1])
                return u'%s/ОФ' % data['dogovor_oferta'][count_oferta - 1]
            elif option == "remove_date_dogovor_oferta":
                package_obj = Package_on_connection_of_service.objects.get(user=user, activate=False, deactivate=False)
                data = eval(package_obj.data)
                slugs_list_temp = package_obj.slugs_document
                slugs_list = slugs_list_temp.split(', ')
                count_oferta = slugs_list.count('remove_dogovor_oferta')
                findoc_sign_obj = FinDocSigned.objects.get(id=data['dogovor_oferta'][count_oferta - 1])
                date_oferta = datetime.datetime(findoc_sign_obj.signed_at.year, findoc_sign_obj.signed_at.month, findoc_sign_obj.signed_at.day).date()
                log.add(datetime.datetime.strftime(date_oferta, "%d.%m.%Y"))
                return datetime.datetime.strftime(date_oferta, "%d.%m.%Y")
            elif option == "findoc_name":
                findoc = FinDocSignApplication.objects.get(id=findocapp_id)
                return findoc.findoc.name
            elif option == "findoc_display_name":
                findoc = FinDocSignApplication.objects.get(id=findocapp_id)
                return findoc.findoc.display_name
            elif option == "service_name":
                cur = connections[settings.BILLING_DB].cursor()
                cur2 = connections[settings.GLOBALHOME_DB2].cursor()

                cur2.execute("SELECT for_services FROM fin_docs_applications WHERE id=%s;", (findocapp_id,))
                service_id = cur2.fetchone()
                cur.execute("SELECT comment FROM billservice_addonservice WHERE id=%s;", (service_id[0],))
                for_service = cur.fetchone()
                transaction.commit_unless_managed(using=settings.BILLING_DB)
                transaction.commit_unless_managed(using=settings.GLOBALHOME_DB2)
                return for_service[0]
            elif option == "service_price":
                cur = connections[settings.BILLING_DB].cursor()
                cur2 = connections[settings.GLOBALHOME_DB2].cursor()

                cur2.execute("SELECT for_services FROM fin_docs_applications WHERE id=%s;", (findocapp_id,))
                service_id = cur2.fetchone()
                cur.execute("SELECT cost FROM billservice_addonservice WHERE id=%s;", (service_id[0],))
                service_summ = cur.fetchone()[0]
                transaction.commit_unless_managed(using=settings.BILLING_DB)
                transaction.commit_unless_managed(using=settings.GLOBALHOME_DB2)
                service_summ_s_NDS = int(service_summ) * 1.18
                return service_summ_s_NDS

            elif option == "application_number_tdc":
#                 if profile_obj.is_juridical:
                sd = get_signed(user, "telematic_data_centr")
                if sd is not None:
                    con.execute("SELECT findoc_id FROM fin_docs_signeds WHERE id=%s;", (sd.id,))
                    findoc_id = con.fetchone()[0]
                    con.execute("SELECT count(*) FROM fin_docs_signeds WHERE applied_to_id=%s;", (findoc_id,))
                    count = con.fetchone()[0]
                    transaction.commit_unless_managed(using=settings.GLOBALHOME_DB2)
                    return count + 1
                else:
                    return 1
            elif option == "application_number_tdc_for_free_inet":
                if profile_obj.is_juridical:
                    sd = get_signed(user, "telematic_data_centr")
                    con.execute("SELECT findoc_id FROM fin_docs_signeds WHERE id=%s;", (sd.id,))
                    findoc_id = con.fetchone()[0]
                    con.execute("SELECT count(*) FROM fin_docs_signeds WHERE applied_to_id=%s;", (findoc_id,))
                    count = con.fetchone()[0]
                    transaction.commit_unless_managed(using=settings.GLOBALHOME_DB2)
                    return count + 1
                else:
                    return 1

#                 else:
#                    sd = get_signed(user, "telematic_data_centr")
#                    con.execute("SELECT findoc_id FROM fin_docs_signeds WHERE id=%s;", (sd.id,))
#                    findoc_id = con.fetchone()[0]
#                    con.execute("SELECT count(*) FROM fin_docs_signeds WHERE applied_to_id=%s;", (findoc_id,))
#                    count = con.fetchone()[0]
#
#                    params_data = get_zayavka()
#                    service_type = ''
#                    redirect_after_sign = params_data["redirect_after_sign"]
#                    zakaz_id = ''
#                    for i in reversed(range(len(redirect_after_sign))):
#                        if redirect_after_sign[i].isdigit():
#                            zakaz_id += redirect_after_sign[i]
#                    zakaz_id = zakaz_id[::-1]
#                    zakaz = Zakazy.objects.get(id = zakaz_id)
#                    if zakaz.service_type.id in (8, ):
#                        findoc_sign = FinDocSignedZakazy.objects.get(zakaz_id = zakaz.id, fin_doc__findoc__slug='dogovor_oferta')
#                     return u''
            elif option == "application_number_lsc":
                try:
                    cur = connections[settings.GLOBALHOME_DB2].cursor()
                    sd = get_signed(user, "localphone_services_contract")
                    cur.execute("SELECT findoc_id FROM fin_docs_signeds WHERE id=%s;", (sd.id,))
                    findoc_id = cur.fetchone()[0]
                    cur.execute("SELECT count(*) FROM fin_docs_signeds WHERE applied_to_id=%s;", (findoc_id,))
                    count = cur.fetchone()[0]
                    transaction.commit_unless_managed(using=settings.GLOBALHOME_DB2)
                except Exception, e:
                    log.add(e)
                    count = -1
                return count + 1

            elif option == "number_application_for_tdc":
                params_data = get_zayavka()
                zakaz_id = ''
                redirect_after_sign = params_data["redirect_after_sign"]
                for i in reversed(range(len(redirect_after_sign))):
                    if redirect_after_sign[i].isdigit():
                        zakaz_id += redirect_after_sign[i]
                zakaz_id = zakaz_id[::-1]
                zakaz_obj = Zakazy.objects.get(id=zakaz_id)
                if zakaz_obj.service_type.id in (8, 13):  # добавил для аренды оборудования
                    return ''
                fin_doc_zakaz = FinDocSignedZakazy.objects.get(zakaz_id=zakaz_id, fin_doc__findoc__slug='usluga_peredachi_dannyh_s_predoplatoi')
                application = FinDocSigned.objects.get(id=fin_doc_zakaz.fin_doc.id, cancellation_date=None)
                cur2 = connections[settings.GLOBALHOME_DB2].cursor()
                cur2.execute("SELECT template_id FROM fin_docs WHERE slug=%s;", ("telematic_data_centr",))
                template_id = cur2.fetchone()[0]
                transaction.commit_unless_managed(using=settings.GLOBALHOME_DB2)
                try:
                    cur2.execute("SELECT count(id) FROM fin_docs_signeds WHERE id<=%s and applied_to_id=%s;", (application.id, template_id,))
                    count_application = cur2.fetchone()[0]
                    transaction.commit_unless_managed(using=settings.GLOBALHOME_DB2)
                    return u'приложения № %s' % count_application
                except Exception, e:
                    log.add('error = %s' % e)


            elif option == "number_application_for_lsc":
                cur2 = connections[settings.GLOBALHOME_DB2].cursor()
                try:
                    params_data = get_zayavka()
                    zakaz_id = ''
                    redirect_after_sign = params_data["redirect_after_sign"]
                    ext_number_id = ''
                    for i in reversed(range(len(redirect_after_sign))):
                        if redirect_after_sign[i].isdigit():
                            ext_number_id += redirect_after_sign[i]
                    ext_number_id = ext_number_id[::-1]
                    profile_obj = Profile.objects.get(user=user)
                    bill_obj = profile_obj.billing_account
                    ext_number_obj = ExternalNumber.objects.get(id=ext_number_id)
                    zakaz_obj = Zakazy.objects.get(ext_numbers=ext_number_obj, bill_account=bill_obj)
                    fin_doc_zakaz = FinDocSignedZakazy.objects.get(zakaz_id=zakaz_obj.id, fin_doc__findoc__slug='localphone_orderform')
                    application = FinDocSigned.objects.get(id=fin_doc_zakaz.fin_doc.id, cancellation_date=None)
                    cur2.execute("SELECT template_id FROM fin_docs WHERE slug=%s;", ("localphone_services_contract",))
                    template_id = cur2.fetchone()[0]
                except Exception, e:
                    log.add("error_number_application_for_lsc: %s" % e)
                try:
                    cur2.execute("SELECT count(id) FROM fin_docs_signeds WHERE id<=%s and applied_to_id=%s;", (application.id, template_id,))
                    count_application = cur2.fetchone()[0]
                except Exception, e:
                    log.add("error_number_application_for_lsc_2: %s" % e)
                    count_application = ''
                transaction.commit_unless_managed(using=settings.GLOBALHOME_DB2)
                return count_application

            elif option == "number_dop_sogl_izmeneniya":
                if profile_obj.is_juridical:
                    return ''
                package_obj = Package_on_connection_of_service.objects.get(user=user, activate=False, deactivate=False)
                url_after_sign = package_obj.url_after_sign
                zakaz_id = ''
                for i in reversed(range(len(url_after_sign))):
                    if url_after_sign[i].isdigit():
                        zakaz_id += url_after_sign[i]
                zakaz_id = zakaz_id[::-1]
                zakaz_obj = Zakazy.objects.get(id=zakaz_id)
                if zakaz_obj.service_type.id in (10,):
                    zakaz_obj = Zakazy.objects.get(id=zakaz_obj.main_zakaz)
                fin_doc = FinDoc.objects.get(slug='dop_soglashenie_izmenenie_internet')
                try:
                    fin_doc_sign_zakazy = FinDocSignedZakazy.objects.filter(zakaz_id=zakaz_obj.id, fin_doc__findoc=fin_doc)
                except Exception, e:
                    log.add(e)
                log.add(u' %s %s' % ('№'.decode('utf-8'), len(fin_doc_sign_zakazy) + 1))
                return u' %s %s' % ('№'.decode('utf-8'), len(fin_doc_sign_zakazy) + 1)

            elif option == 'number_dogovor_oferta':
                log.add('number_dogovor_oferta')
                if profile_obj.is_juridical:
                    sd = get_signed(user, "telematic_data_centr")
                    return u'%s %s' % ('№'.decode('utf-8'), sd.id)
                package_obj = Package_on_connection_of_service.objects.get(user=user, activate=False, deactivate=False)
                url_after_sign = package_obj.url_after_sign
                zakaz_id = ''
                for i in reversed(range(len(url_after_sign))):
                    if url_after_sign[i].isdigit():
                        zakaz_id += url_after_sign[i]
                zakaz_id = zakaz_id[::-1]
                zakaz_obj = Zakazy.objects.get(id=zakaz_id)
                if zakaz_obj.section_type == 2:
                    if zakaz_obj.service_type.id == 11:
                        fin_doc = FinDoc.objects.get(slug='dogovor_arendi_serverov')
                    elif zakaz_obj.service_type.id in (1, 2,):
                        fin_doc = FinDoc.objects.get(slug='usluga_peredachi_dannyh_s_predoplatoi')
                    fin_doc_sign_zakaz = FinDocSignedZakazy.objects.get(zakaz_id=zakaz_obj.id, fin_doc__findoc=fin_doc)
                    return u' %s %s' % ('№'.decode('utf-8'), fin_doc_sign_zakaz.fin_doc.id)
                fin_doc = FinDoc.objects.get(slug='dogovor_oferta')

                if zakaz_obj.service_type.id in (10,):
                    zakaz_obj = Zakazy.objects.get(id=zakaz_obj.main_zakaz)
                try:
                    fin_doc_sign_zakaz = FinDocSignedZakazy.objects.get(zakaz_id=zakaz_obj.id, fin_doc__findoc=fin_doc)
                except Exception, e:
                    log.add(e)
                log.add(u'%s/ОФ' % fin_doc_sign_zakaz.fin_doc.id)
                return u'ОФЕРТЫ %s %s/ОФ' % ('№'.decode('utf-8'), fin_doc_sign_zakaz.fin_doc.id)

            elif option == 'date_dogovor_oferta':
                if profile_obj.is_juridical:
                    sd = get_signed(user, "telematic_data_centr")
                    return sd.signed_at.strftime("%d.%m.%Y")
                package_obj = Package_on_connection_of_service.objects.get(user=user, activate=False, deactivate=False)
                url_after_sign = package_obj.url_after_sign
                zakaz_id = ''
                for i in reversed(range(len(url_after_sign))):
                    if url_after_sign[i].isdigit():
                        zakaz_id += url_after_sign[i]
                zakaz_id = zakaz_id[::-1]
                zakaz_obj = Zakazy.objects.get(id=zakaz_id)
                if zakaz_obj.service_type.id in (10,):
                    zakaz_obj = Zakazy.objects.get(id=zakaz_obj.main_zakaz)
                if zakaz_obj.service_type.id == 11:
                    fin_doc = FinDoc.objects.get(slug='dogovor_arendi_serverov')
                elif zakaz_obj.service_type.id == 1:
                    fin_doc = FinDoc.objects.get(slug='usluga_peredachi_dannyh_s_predoplatoi')
                elif zakaz_obj.service_type.id == 2:
                    fin_doc = FinDoc.objects.get(slug='usluga_peredachi_dannyh_s_predoplatoi')
                else:
                    fin_doc = FinDoc.objects.get(slug='dogovor_oferta')
                try:
                    fin_doc_sign_zakaz = FinDocSignedZakazy.objects.get(zakaz_id=zakaz_obj.id, fin_doc__findoc=fin_doc)
                except Exception, e:
                    log.add(e)
                date_oferta = datetime.datetime(fin_doc_sign_zakaz.fin_doc.signed_at.year, fin_doc_sign_zakaz.fin_doc.signed_at.month, fin_doc_sign_zakaz.fin_doc.signed_at.day).date()
                log.add(datetime.datetime.strftime(date_oferta, "%d.%m.%Y"))
                return datetime.datetime.strftime(date_oferta, "%d.%m.%Y")

            elif option == "ezernet_speed":
                try:
                    package_obj = Package_on_connection_of_service.objects.get(user=user, activate=False, deactivate=False)
                    data = eval(package_obj.data)
                    tariff_obj = Tariff.objects.get(id=data['speed_inet_id'])
                    return int(tariff_obj.speed_inet)
                except:
                    return '100'

            elif option == "speed_inet_in_oferta":
                package_obj = Package_on_connection_of_service.objects.get(user=user, activate=False, deactivate=False)
                url_after_sign = package_obj.url_after_sign
                zakaz_id = ''
                for i in reversed(range(len(url_after_sign))):
                    if url_after_sign[i].isdigit():
                        zakaz_id += url_after_sign[i]
                zakaz_id = zakaz_id[::-1]
                zakaz_obj = Zakazy.objects.get(id=zakaz_id)
                if zakaz_obj.service_type.id in (10,):
                    zakaz_obj = Zakazy.objects.get(id=zakaz_obj.main_zakaz)
                data = eval(package_obj.data)

                if zakaz_obj.date_activation > datetime.datetime.now():
                    tariff_obj = zakaz_obj.tariff
                else:
                    if data.has_key('new_ip'):
                        tariff_obj = zakaz_obj.tariff
                    elif data.has_key('tariff_id'):
                        tariff_obj = Tariff.objects.get(id=data['tariff_id'])
                    else:
                        tariff_obj = zakaz_obj.tariff
                log.add('zakaz_obj = %s' % zakaz_obj.service_type.id)
#                if zakaz_obj.service_type.id == 11:
#                    port_id = Zakazy.objects.get(main_zakaz=zakaz_id, service_type__id=12)
#                    obj = Zakazy.objects.get(id=port_id.id)
#                    inet = 123
                if zakaz_obj.service_type.id == 2:
                    inet = u'100 Мбит/сек(не гарантированный канал)'
                elif zakaz_obj.service_type.id == 1:
                    inet = u'100 Мбит/сек(не гарантированный канал)'
#                   log.add(u'%s Мбит' % tariff_obj.speed_inet)
                if tariff_obj.speed_inet:
                    return u'%s Мбит(%s канал)' % (tariff_obj.speed_inet, u'гарантированный' if tariff_obj.garant else u'не гарантированный')
                else:
                    return u"%s" % inet

            elif option == 'abonenka_cost_in_oferta':
                package_obj = Package_on_connection_of_service.objects.get(user=user, activate=False, deactivate=False)
                url_after_sign = package_obj.url_after_sign
                zakaz_id = ''
                for i in reversed(range(len(url_after_sign))):
                    if url_after_sign[i].isdigit():
                        zakaz_id += url_after_sign[i]
                zakaz_id = zakaz_id[::-1]
                zakaz_obj = Zakazy.objects.get(id=zakaz_id)
                if zakaz_obj.service_type.id == 11:
                    try:
                        server_id, count_ip = zakaz_obj.server.id, zakaz_obj.count_ip
                        speed_obj = Zakazy.objects.get(main_zakaz=zakaz_id, service_type__id=12)
                        speed_inet_id = speed_obj.tariff.id
                        cost = cost_str = cost_calculation(server_id, count_ip, speed_inet_id)
                        return cost
                    except Exception, e:
                        log.add(e)
                if zakaz_obj.service_type.id in (10,):
                    zakaz_obj = Zakazy.objects.get(id=zakaz_obj.main_zakaz)
                data = eval(package_obj.data)
                if zakaz_obj.date_activation > datetime.datetime.now():
                    cost = zakaz_obj.cost
                else:
                    if data.has_key('new_ip'):
                        cost = zakaz_obj.cost
                    elif data.has_key('tariff_id'):
                        tariff_obj = Tariff.objects.get(id=data['tariff_id'])
                        cost = tariff_obj.price_id.cost
                    else:
                        cost = zakaz_obj.cost
                log.add(cost)
                return u'%s р.' % (cost / 1.18)

            elif option == 'cost_ip_in_oferta':
                package_obj = Package_on_connection_of_service.objects.get(user=user, activate=False, deactivate=False)
                url_after_sign = package_obj.url_after_sign
                zakaz_id = ''
                for i in reversed(range(len(url_after_sign))):
                    if url_after_sign[i].isdigit():
                        zakaz_id += url_after_sign[i]
                zakaz_id = zakaz_id[::-1]
                zakaz_obj = Zakazy.objects.get(id=zakaz_id)
                if zakaz_obj.service_type.id in (1, 2, 11,):
                    tariff_obj = Tariff.objects.get(id=41)

                else:
                    tariff_obj = Tariff.objects.get(id=26)
                return u'%s р.' % (tariff_obj.price_id.cost / 1.18)

            elif option == 'count_ip_in_oferta':
                package_obj = Package_on_connection_of_service.objects.get(user=user, activate=False, deactivate=False)
                url_after_sign = package_obj.url_after_sign
                zakaz_id = ''
                for i in reversed(range(len(url_after_sign))):
                    if url_after_sign[i].isdigit():
                        zakaz_id += url_after_sign[i]
                zakaz_id = zakaz_id[::-1]
                zakaz_obj = Zakazy.objects.get(id=zakaz_id)
                data = eval(package_obj.data)
                if zakaz_obj.section_type == 2:
                    if zakaz_obj.service_type.id in (2, 11,):
                        zakazy_ip_queryset = Zakazy.objects.filter(Q(service_type__id=10) & Q(main_zakaz=zakaz_obj.id) & Q(status_zakaza=2) & \
                                                           (Q(date_deactivation__isnull=True)))  # | Q(date_deactivation__gt=datetime.datetime.now())))

                        count_ip = len(zakazy_ip_queryset)
                        log.add("count ip %s" % count_ip)
                        if data.has_key('new_ip'):
                            count_new_ip = int(data['new_ip'])
                            count_ip = count_ip + count_new_ip
                            log.add("new_ip %s" % count_ip)
                        elif data.has_key('spis_ip'):
                            del_ip = data['spis_ip'].split(',')
                            count_del_ip = len(del_ip)
                            count_ip = count_ip - count_del_ip
                            log.add("del_ip %s" % count_ip)

                        return count_ip
                if zakaz_obj.service_type.id in (10,):
                    zakaz_obj = Zakazy.objects.get(id=zakaz_obj.main_zakaz)

                zakazy_ip_queryset = Zakazy.objects.filter(Q(main_zakaz=zakaz_obj.id) & Q(status_zakaza=2) & \
                                                           (Q(date_deactivation=None) | Q(date_deactivation__gt=datetime.datetime.now())))
                count_ip = len(zakazy_ip_queryset)
                if zakaz_obj.date_activation > datetime.datetime.now():
                    if data.has_key('new_ip'):
                        count_new_ip = int(data['new_ip'])
                        count_ip = count_ip + count_new_ip
                    if data.has_key('spis_ip'):
                        del_ip = data['spis_ip'].split(',')
                        count_del_ip = len(del_ip)
                        count_ip = count_ip - count_del_ip
                else:
                    if data.has_key('new_ip'):
                        count_new_ip = int(data['new_ip'])
                        count_ip = count_ip + count_new_ip
                    elif data.has_key('spis_ip'):
                        del_ip = data['spis_ip'].split(',')
                        count_del_ip = len(del_ip)
                        count_ip = count_ip - count_del_ip
                return count_ip

            elif option == 'all_cost_in_oferta':
                package_obj = Package_on_connection_of_service.objects.get(user=user, activate=False, deactivate=False)
                url_after_sign = package_obj.url_after_sign
                zakaz_id = ''
                for i in reversed(range(len(url_after_sign))):
                    if url_after_sign[i].isdigit():
                        zakaz_id += url_after_sign[i]
                zakaz_id = zakaz_id[::-1]
                zakaz_obj = Zakazy.objects.get(id=zakaz_id)
                if zakaz_obj.service_type.id in (10,):
                    zakaz_obj = Zakazy.objects.get(id=zakaz_obj.main_zakaz)
                data = eval(package_obj.data)
                zakazy_ip_queryset = Zakazy.objects.filter(Q(main_zakaz=zakaz_obj.id) & Q(status_zakaza=2) & \
                                                           (Q(date_deactivation=None) | Q(date_deactivation__gt=datetime.datetime.now())))
                count_ip = len(zakazy_ip_queryset)
                log.add(zakaz_obj.section_type)
                log.add(zakaz_obj.service_type.id)
                if zakaz_obj.section_type == 3:
                    if zakaz_obj.date_activation > datetime.datetime.now():
                        if data.has_key('new_ip'):
                            count_new_ip = int(data['new_ip'])
                            count_ip = count_ip + count_new_ip
                        if data.has_key('spis_ip'):
                            del_ip = data['spis_ip'].split(',')
                            count_del_ip = len(del_ip)
                            count_ip = count_ip - count_del_ip
                    else:
                        if data.has_key('new_ip'):
                            count_new_ip = int(data['new_ip'])
                            count_ip = count_ip + count_new_ip
                        elif data.has_key('spis_ip'):
                            del_ip = data['spis_ip'].split(',')
                            count_del_ip = len(del_ip)
                            count_ip = count_ip - count_del_ip

                    if zakaz_obj.date_activation > datetime.datetime.now():
                        cost = zakaz_obj.cost
                    else:
                        if data.has_key('new_ip'):
                            cost = zakaz_obj.cost
                        elif data.has_key('tariff_id'):
                            tariff_obj = Tariff.objects.get(id=data['tariff_id'])
                            cost = tariff_obj.price_id.cost
                        else:
                            cost = zakaz_obj.cost
                    tariff_obj = Tariff.objects.get(id=26)
                    all_cost = cost + tariff_obj.price_id.cost * count_ip
                    return u'%s р.' % (all_cost / 1.18)
                if zakaz_obj.section_type == 2:
                    zakazy_ip_queryset = Zakazy.objects.filter(Q(main_zakaz=zakaz_obj.id) & Q(status_zakaza=2) & Q(service_type__id=10) & \
                                                           (Q(date_deactivation__isnull=True)))  # | Q(date_deactivation__gt=datetime.datetime.now())))
                    count_ip = len(zakazy_ip_queryset)
                    if data.has_key('new_ip'):
                            count_new_ip = int(data['new_ip'])
                            count_ip = count_ip + count_new_ip
                    elif data.has_key('spis_ip'):
                            del_ip = data['spis_ip'].split(',')
                            count_del_ip = len(del_ip)
                            count_ip = count_ip - count_del_ip
                    if zakaz_obj.service_type.id == 11:
                        speed_obj = Zakazy.objects.get(main_zakaz=zakaz_id, service_type__id=12)
                        speed_inet_id = speed_obj.tariff.id
                        all_cost = cost_calculation(zakaz_obj.server.id, count_ip, speed_inet_id)
                    elif zakaz_obj.service_type.id == 2:
                        all_cost = zakaz_obj.cost / 1.18
                        tariff_ip_obj = Tariff.objects.get(id=41)
                        all_cost += (int(count_ip) - 1) * tariff_ip_obj.price_id.cost / 1.18
                    elif zakaz_obj.service_type.id == 1:
                        all_cost = zakaz_obj.cost / 1.18
                        tariff_ip_obj = Tariff.objects.get(id=41)
                        all_cost += (int(count_ip) - 10) * tariff_ip_obj.price_id.cost / 1.18
                    return u'%s р.' % all_cost


            elif option == "date_start_izmeneniya":
                try:
                    package_obj = Package_on_connection_of_service.objects.get(user=user, activate=False, deactivate=False)
                    url_after_sign = package_obj.url_after_sign
                    zakaz_id = ''
                    for i in reversed(range(len(url_after_sign))):
                        if url_after_sign[i].isdigit():
                            zakaz_id += url_after_sign[i]
                    zakaz_id = zakaz_id[::-1]
                    zakaz_obj = Zakazy.objects.get(id=zakaz_id)
                    if zakaz_obj.service_type.id in (10,):
                        zakaz_obj = Zakazy.objects.get(id=zakaz_obj.main_zakaz)
                    data = eval(package_obj.data)
                    now = datetime.datetime.now()
                    if zakaz_obj.date_activation > now:
                        date_start = zakaz_obj.date_activation
                    else:
                        if data.has_key('new_ip'):
                            date_start = now
                        else:
                            date_first_day_this_month = datetime.datetime(now.year, now.month, 1, 0, 0, 0)
                            date_start = date_first_day_this_month + relativedelta(months=1)
                    log.add('start_izm = %s' % datetime.datetime.strftime(date_start, "%d.%m.%Y"))
                except Exception, e:
                    log.add('error = %s' % e)
                return datetime.datetime.strftime(date_start, "%d.%m.%Y")

            elif option == "date_remove_internet":
                now = datetime.datetime.now()
                date_first_day_this_month = datetime.datetime(now.year, now.month, 1, 0, 0, 0)
                date_start = date_first_day_this_month + relativedelta(months=1)
                return datetime.datetime.strftime(date_start, "%d.%m.%Y")

            elif option == "speed_inet":
                try:
                    params_data = get_zayavka()
                    redirect_after_sign = params_data["redirect_after_sign"]
                    package_obj = Package_on_connection_of_service.objects.get(url_after_sign=redirect_after_sign, user=user, activate=False, deactivate=False)
                    data_temp = eval(package_obj.data)
                    tariff_obj = Tariff.objects.get(id=data_temp['tariff'])
                    speed_inet = tariff_obj.speed_inet * 1024
                except:
                    speed_inet = ''
                return speed_inet


            elif option == "cost_inet":
                try:
                    params_data = get_zayavka()
                    redirect_after_sign = params_data["redirect_after_sign"]
                    package_obj = Package_on_connection_of_service.objects.get(url_after_sign=redirect_after_sign, user=user, activate=False, deactivate=False)
                    data_temp = eval(package_obj.data)
                    count_static_ip = data_temp['count_static_ip']
                    tariff_obj = Tariff.objects.get(id=data_temp['tariff'])
                    price_obj = Price.objects.get(id=36)
                    cost_ip = int(count_static_ip) * float(price_obj.cost)
                    cost_inet = (tariff_obj.price_id.cost + cost_ip) / 1.18
                except:
                    cost_inet = ''
                return cost_inet

            elif option == "count_ip_inet":
                try:
                    params_data = get_zayavka()
                    redirect_after_sign = params_data["redirect_after_sign"]
                    package_obj = Package_on_connection_of_service.objects.get(url_after_sign=redirect_after_sign, user=user, activate=False, deactivate=False)
                    data_temp = eval(package_obj.data)
                    count_static_ip = data_temp['count_static_ip']
                except:
                    count_static_ip = ''
                return count_static_ip

            elif option == "table_form_zakaz":
                try:
                    package_obj = Package_on_connection_of_service.objects.get(user=user, activate=False, deactivate=False)
                    request_post = eval(package_obj.data)
                    if request_post.has_key('server_id'):
                        server = Servers.objects.get(id=request_post['server_id'])
                        server_hdd = '<br />'.join(i.__unicode__() for i in server.hdd.exclude(interface_id=3)) or '-'
                        server_ssd = '<br />'.join(i.__unicode__() for i in server.hdd.filter(interface_id=3)) or '-'
                        server_ram = '<br />'.join(i.__unicode__() for i in server.ram.all())
                        inet_speed = Tariff.objects.get(id=request_post['speed_inet_id']).name
                        cost = cost_calculation(server.id, request_post['count_ip'], request_post['speed_inet_id'])
                        log.add(type(cost))
                        cost = '%.2f' % (float(cost) * 1.18)
                        table = u'''
                            <table border="1" style="width: 782px;">
                                <thead>
                                    <tr>
                                        <th style="padding: 5px 5px;">Тариф</th>
                                        <th style="padding: 5px 5px;">Процессор</th>
                                        <th style="padding: 5px 5px;">Память</th>
                                        <th style="padding: 5px 5px;">Диск, HDD</th>
                                        <th style="padding: 5px 5px;">Диск, SSD</th>
                                        <th style="padding: 5px 5px;">Интернет</th>
                                        <th style="padding: 5px 5px;">Кол-во<br/>IP</th>
                                        <th style="padding: 5px 5px;">Цена,<br />руб с НДС</th>
                                    </tr>
                                </thead>
                                <tbody>'''
                        table += u'''
                                    <tr>
                                        <td>%s</td>
                                        <td>%s</td>
                                        <td>%s</td>
                                        <td>%s</td>
                                        <td>%s</td>
                                        <td>%s</td>
                                        <td>%s</td>
                                        <td>%s</td>
                                    </tr>
                                </tbody>
                            </table>
                            ''' % (server.name, server.cpu, server_ram, server_hdd, server_ssd, inet_speed, request_post['count_ip'], cost)
                    elif request_post.has_key('rack'):
                        AccountRackFormSet = formset_factory(AccountRackForm, extra=1)
                        rack_formset = AccountRackFormSet(request_post)
                        if rack_formset.is_valid():
                            table = u'''
                                <table border="1" style="width: 100%">
                                    <thead>
                                        <tr>
                                            <th style="padding: 5px 5px;">Размер<br/>стойки</th>
                                            <th style="padding: 5px 5px;">Глубина<br/>стойки</th>
                                            <th style="padding: 5px 5px;">Интернет</th>
                                            <th style="padding: 5px 5px;">Кол-во<br/>IP</th>
                                            <th style="padding: 5px 5px;">Кол-во<br/>розеток</th>
                                            <th style="padding: 5px 5px;">Электро-<br/>питание</th>
                                            <th style="padding: 5px 5px;">Стоимость<br/>услуги, руб c НДС</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                '''
                            for form in rack_formset:
                                cd = form.cleaned_data
                                cost = rack_cost_zakaz(cd['size_rack'], cd['inet_speed'], cd['count_ip'], cd['count_socket'], cd['count_electro'])
                                cost = '%.2f' % (float(cost) * 1.18)
                                inet_speed = Tariff.objects.get(id=cd['inet_speed']).name
                                size_rack = Tariff.objects.get(id=cd['size_rack']).unit
                                choice_depth = {'1':u'60 см', '2':u'80 см', '3':u'100 см'}
                                table += u'''
                                    <tr>
                                    <td style="padding: 5px 5px;">%s</td>
                                    <td style="padding: 5px 5px;">%s</td>
                                    <td style="padding: 5px 5px;">%s</td>
                                    <td style="padding: 5px 5px;">%s</td>
                                    <td style="padding: 5px 5px;">%s</td>
                                    <td style="padding: 5px 5px;">%s</td>
                                    <td style="padding: 5px 5px;">%s</td>
                                    </tr>
                                    ''' % (size_rack, choice_depth[cd['depth']], inet_speed, cd['count_ip'], \
                                           cd['count_socket'], u'%s Вт' % cd['count_electro'], cost)
                            table += u'''
                                </tbody>
                                </table>'''
                    else:
                        AccountColocationFormSet = formset_factory(AccountColocationForm, extra=1)
                        colocation_formset = AccountColocationFormSet(request_post)
                        table = ''
                        if colocation_formset.is_valid():
                            table = u'''
                                <table border="1" style="width: 100%">
                                    <thead>
                                        <tr>
                                            <th style="padding: 5px 5px;">Название<br/>оборудования</th>
                                            <th style="padding: 5px 5px;">Высота<br/>сервера</th>
                                            <th style="padding: 5px 5px;">Размеры, см</th>
                                            <th style="padding: 5px 5px;">Интернет</th>
                                            <th style="padding: 5px 5px;">Кол-во<br/>IP</th>
                                            <th style="padding: 5px 5px;">Кол-во<br/>розеток, шт</th>
                                            <th style="padding: 5px 5px;">Электро-<br/>питание, Вт</th>
                                            <th style="padding: 5px 5px;">Стоимость<br/>услуги, руб c НДС</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                '''
                            for form in colocation_formset.forms:
                                cd = form.cleaned_data
                                cost = colocation_cost_zakaz(cd['height_unit'], cd['size'], cd['inet_speed'], cd['count_ip'], cd['count_socket'], cd['count_electro'])
                                cost = '%.2f' % (float(cost) * 1.18)
                                if cd['height_unit'] in ('tower',):
                                    tariff_qs = Tariff.objects.filter(section_type=2, service_type__id=2, tower_casing=True)
                                    choice_size = {}
                                    for tariff_obj in tariff_qs:
                                        choice_size['%s' % tariff_obj.id] = '%sx%sx%s' % (tariff_obj.width, tariff_obj.height, tariff_obj.depth)
                                else:
                                    choice_size = {'1':u'до 60', '2':u'до 80', '3':u'до 100'}
                                inet_speed = Tariff.objects.get(id=cd['inet_speed']).name
                                table += u'''
                                    <tr>
                                    <td style="padding: 5px 5px;">%s</td>
                                    <td style="padding: 5px 5px;">%s</td>
                                    <td style="padding: 5px 5px;">%s</td>
                                    <td style="padding: 5px 5px;">%s</td>
                                    <td style="padding: 5px 5px;">%s</td>
                                    <td style="padding: 5px 5px;">%s</td>
                                    <td style="padding: 5px 5px;">%s</td>
                                    <td style="padding: 5px 5px;">%s</td>
                                    </tr>
                                    ''' % (cd['equipment_name'], cd['height_unit'], choice_size[cd['size']], inet_speed, \
                                           cd['count_ip'], cd['count_socket'], cd['count_electro'], cost)
                            table += u'''
                                </tbody>
                                </table>
                                '''
                except Exception, e:
                    import sys, os
                    log.add("e=%s" % str(e).encode('utf-8'))
                    exc_type, exc_obj, exc_tb = sys.exc_info()  # @UnusedVariable
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    log.add("Exception in priority_of_services: file:%s line:%s" % (fname, exc_tb.tb_lineno))
                return table

            elif option == "unit":
                params_data = get_zayavka()
                redirect_after_sign = params_data["redirect_after_sign"]
                package_obj = Package_on_connection_of_service.objects.get(url_after_sign=redirect_after_sign, user=user, activate=False, deactivate=False)
                try:
                    data_temp = eval(package_obj.data)
                    request_post = data_temp
                    hidden_id = request_post["hidden_id"]
                    zayavka = Zakazy.objects.get(id=hidden_id)
                    service_tupe = zayavka.service_type.id
                    if  service_tupe == 11:
                        unit = u'%s unit' % zayavka.server.count_unit
                    else:
                        if zayavka.count_of_units:
                            unit = u'%s unit' % zayavka.count_of_units
                        else:
                            unit = u'до %sx%sx%s см' % (zayavka.tariff.width, zayavka.tariff.height, zayavka.tariff.depth,)
                except:

                    if redirect_after_sign == reverse("rack_zakaz"):
                        unit_obj = Tariff.objects.get(id=1)
                        unit = u'%s unit' % unit_obj.unit
                    elif redirect_after_sign == reverse("colocation_zakaz"):
                        unit = u'%s unit' % request_post["hidden_unit"]
                    elif redirect_after_sign == reverse("add_dedicated_final"):
                        data_temp = eval(package_obj.data)
                        server_id = data_temp["server_id"]
                        unit_object = Servers.objects.get(id=server_id)
                        unit = u'%s unit' % unit_object.count_unit
                return unit

            elif option == "electricity":
                params_data = get_zayavka()
                redirect_after_sign = params_data["redirect_after_sign"]
                package_obj = Package_on_connection_of_service.objects.get(url_after_sign=redirect_after_sign, user=user, activate=False, deactivate=False)
                try:
                    data_temp = eval(package_obj.data)
                    request_post = data_temp
                    hidden_id = request_post["hidden_id"]
                    zayavka = Zakazy.objects.get(id=hidden_id)
                    service_tupe = zayavka.service_type.id
                    if  service_tupe == 11:
                        electricity = zayavka.server.electricity
                    else:
                        electricity = zayavka.electricity
                except:
                    if redirect_after_sign == reverse("rack_zakaz"):
                        electricity_obj = Tariff.objects.get(id=1)
                        electricity = electricity_obj.electricity
                    elif redirect_after_sign == reverse("colocation_zakaz"):
                        electricity = request_post["hidden_electro"]
                    elif redirect_after_sign == reverse("add_dedicated_final"):
                        data_temp = eval(package_obj.data)
                        electricity_obj = Servers.objects.get(id=data_temp["server_id"])
                        electricity = electricity_obj.electricity
                return electricity

            elif option == "port":
                params_data = get_zayavka()
                redirect_after_sign = params_data["redirect_after_sign"]
                package_obj = Package_on_connection_of_service.objects.get(url_after_sign=redirect_after_sign, user=user, activate=False, deactivate=False)
                try:
                    data_temp = eval(package_obj.data)
                    request_post = data_temp
                    hidden_id = request_post["hidden_id"]
                    zayavka = Zakazy.objects.get(id=hidden_id)
                    port = zayavka.count_of_port
                except:
                    if redirect_after_sign == reverse("colocation_zakaz"):
                        data_temp = eval(package_obj.data)
                        request_post = data_temp
                        port = request_post["hidden_port"]
                    if redirect_after_sign == reverse("rack_zakaz"):
                        port_obj = Tariff.objects.get(id=1)
                        port = port_obj.port
                    elif redirect_after_sign == reverse("add_dedicated_final"):
                        data_temp = eval(package_obj.data)
                        port_obj = Servers.objects.get(id=data_temp["server_id"])
                        port = port_obj.count_port

                return port

            elif option == "cost":
                params_data = get_zayavka()
                redirect_after_sign = params_data["redirect_after_sign"]
                package_obj = Package_on_connection_of_service.objects.get(url_after_sign=redirect_after_sign, user=user, activate=False, deactivate=False)
                try:
                    data_temp = eval(package_obj.data)
                    try:
                        zakaz_id = data_temp["hidden_id"]
                        zakaz_obj = Zakazy.objects.get(id=zakaz_id)
                        cost = zakaz_obj.cost
#                        server_id, count_ip = zakaz_obj.server.id, zakaz_obj.count_ip
#                        speed_obj = Zakazy.objects.get(main_zakaz=zakaz_id)
#                        speed_inet_id = speed_obj.tariff.id
#                        cost = cost_str = cost_calculation(server_id, count_ip, speed_inet_id)
                    except:
                        request_post = data_temp
                        hidden_id = request_post["hidden_id"]
                        zakazy_obj = Zakazy.objects.get(id=hidden_id)
                        cost = zakazy_obj.cost
                except:
                    if redirect_after_sign == reverse("rack_zakaz"):
                        cost_obj = Tariff.objects.get(id=1)
                        cost_temp = cost_obj.price_id.cost
                        cost = '%.2f' % cost_temp
#                        elif redirect_after_sign == reverse("colocation_zakaz"):
#                            log.add(4)
#                            cost = request_post["hidden_cost"]
                    elif redirect_after_sign == reverse("add_dedicated_final"):
                        server_id, count_ip, speed_inet_id = data_temp['server_id'], data_temp['count_ip'], data_temp['speed_inet_id']
                        cost_str = cost_calculation(server_id, count_ip, speed_inet_id)
                        cost = u'%.2f ' % (float(cost_str))
                    else:
                        zakaz_id = ''
                        for i in reversed(range(len(redirect_after_sign))):
                            if redirect_after_sign[i].isdigit():
                                zakaz_id += redirect_after_sign[i]
                        zakaz_id = zakaz_id[::-1]
                        zakaz = Zakazy.objects.get(id=zakaz_id)
                        cost = zakaz.cost
                return cost

            elif option == "cost_nds":
                log.add('cost_nds')
                params_data = get_zayavka()
                redirect_after_sign = params_data["redirect_after_sign"]
                package_obj = Package_on_connection_of_service.objects.get(url_after_sign=redirect_after_sign, user=user, activate=False, deactivate=False)
                try:
                    data_temp = eval(package_obj.data)
                    try:
                        zakaz_id = data_temp["hidden_id"]
                        zakaz_obj = Zakazy.objects.get(id=zakaz_id)
                        if zakaz_obj.service_type.id in (11,):
                            server_id, count_ip = zakaz_obj.server.id, zakaz_obj.count_ip
                            speed_obj = Zakazy.objects.get(main_zakaz=zakaz_id)
                            speed_inet_id = speed_obj.tariff.id
                            cost = cost_calculation(server_id, count_ip, speed_inet_id)
                            log.add(cost)
                            cost = float(cost)
                            cost = cost * 1.18
                        elif zakaz_obj.service_type.id in (2,):
                            cost = zakaz_obj.cost
                            pod_zakazy_qs = Zakazy.objects.filter(main_zakaz=zakaz_obj.id, status_zakaza__in=[1, 2, 4], cost__gt=0)
                            for pod_zakaz in pod_zakazy_qs:
                                log.add('pod_zakaz = %s' % pod_zakaz.cost)
                                cost += pod_zakaz.cost
                            if zakaz_obj.count_ip > zakaz_obj.tariff.ip:
                                for j in range(zakaz_obj.count_ip - zakaz_obj.tariff.ip):
                                    zakaz_ip = Zakazy(
                                        section_type=2,
                                        status_cost=1,
                                        service_type_id=10,
                                        tariff_id=41,
                                        count_ip=1,
                                        )
                                    cost_one_ip = float(cost_dc(0, zakaz_ip))
                                    log.add('cost_one_ip = %s' % cost_one_ip)
                                    cost += cost_one_ip
                            log.add(cost)
                        elif zakaz_obj.service_type.id in (1,):
                            cost = zakaz_obj.cost
                    except Exception, e:
                        log.add(e)
                        request_post = data_temp
                        hidden_id = request_post["hidden_id"]
                        zakazy_obj = Zakazy.objects.get(id=hidden_id)
                        cost = zakazy_obj.cost / 1.18
                except:
                    if redirect_after_sign == reverse("rack_zakaz"):
                        cost_obj = Tariff.objects.get(id=1)
                        cost_temp = cost_obj.price_id.cost / 1.18
                        cost = '%.2f' % cost_temp
#                    elif redirect_after_sign == reverse("colocation_zakaz"):
#                        cost = request_post["hidden_cost"]
                    elif redirect_after_sign == reverse("add_dedicated_final"):
                        server_id, count_ip, speed_inet_id = data_temp['server_id'], data_temp['count_ip'], data_temp['speed_inet_id']
                        cost_str = cost_calculation(server_id, count_ip, speed_inet_id)
                        cost = u'%.2f ' % (float(cost_str))
                    else:
                        zakaz_id = ''
                        for i in reversed(range(len(redirect_after_sign))):
                            if redirect_after_sign[i].isdigit():
                                zakaz_id += redirect_after_sign[i]
                        zakaz_id = zakaz_id[::-1]
                        zakaz = Zakazy.objects.get(id=zakaz_id)
                        cost = zakaz.cost
                        if zakaz.service_type.id in (8,) and zakaz.count_ip > 0:
                            service_type = Service_type.objects.get(id=10)
                            tariff_obj = Tariff.objects.get(id=26)
                            cost_ip = tariff_obj.price_id.cost / 1.18 * zakaz.count_ip
                            cost = cost + cost_ip
                cost_nds = u"%s руб." % cost
                return cost_nds

            elif option == "cost_nds_in_words":
                params_data = get_zayavka()
                redirect_after_sign = params_data["redirect_after_sign"]
                package_obj = Package_on_connection_of_service.objects.get(url_after_sign=redirect_after_sign, user=user, activate=False, deactivate=False)
                try:
                    data_temp = eval(package_obj.data)
                    try:
                        zakaz_id = data_temp["hidden_id"]
                        zakaz_obj = Zakazy.objects.get(id=zakaz_id)
                        if zakaz_obj.service_type.id in (11,):
                            server_id, count_ip = zakaz_obj.server.id, zakaz_obj.count_ip
                            speed_obj = Zakazy.objects.get(main_zakaz=zakaz_id)
                            speed_inet_id = speed_obj.tariff.id
                            cost = cost_calculation(server_id, count_ip, speed_inet_id)
                            log.add(cost)
                            cost = float(cost)
                            cost = cost * 1.18
                        elif zakaz_obj.service_type.id in (2,):
                            cost = zakaz_obj.cost
                            pod_zakazy_qs = Zakazy.objects.filter(main_zakaz=zakaz_obj.id, status_zakaza__in=[1, 2, 4], cost__gt=0)
                            for pod_zakaz in pod_zakazy_qs:
                                log.add('pod_zakaz = %s' % pod_zakaz.cost)
                                cost += pod_zakaz.cost
                            if zakaz_obj.count_ip > zakaz_obj.tariff.ip:
                                for j in range(zakaz_obj.count_ip - zakaz_obj.tariff.ip):
                                    zakaz_ip = Zakazy(
                                        section_type=2,
                                        status_cost=1,
                                        service_type_id=10,
                                        tariff_id=41,
                                        count_ip=1,
                                        )
                                    cost_one_ip = float(cost_dc(0, zakaz_ip))
                                    log.add('cost_one_ip = %s' % cost_one_ip)
                                    cost += cost_one_ip
                            log.add(cost)
                        elif zakaz_obj.service_type.id in (1,):
                            cost = zakaz_obj.cost
                    except Exception, e:
                        log.add(e)
                        request_post = data_temp
                        hidden_id = request_post["hidden_id"]
                        zakazy_obj = Zakazy.objects.get(id=hidden_id)
                        cost = zakazy_obj.cost / 1.18
                except:
                    if redirect_after_sign == reverse("rack_zakaz"):
                        cost_obj = Tariff.objects.get(id=1)
                        cost_temp = cost_obj.price_id.cost / 1.18
                        cost = '%.2f' % cost_temp
#                    elif redirect_after_sign == reverse("colocation_zakaz"):
#                        cost = request_post["hidden_cost"]
                    elif redirect_after_sign == reverse("add_dedicated_final"):
                        server_id, count_ip, speed_inet_id = data_temp['server_id'], data_temp['count_ip'], data_temp['speed_inet_id']
                        cost_str = cost_calculation(server_id, count_ip, speed_inet_id)
                        cost = u'%.2f ' % (float(cost_str))
                    else:
                        zakaz_id = ''
                        for i in reversed(range(len(redirect_after_sign))):
                            if redirect_after_sign[i].isdigit():
                                zakaz_id += redirect_after_sign[i]
                        zakaz_id = zakaz_id[::-1]
                        zakaz = Zakazy.objects.get(id=zakaz_id)
                        cost = zakaz.cost
                        if zakaz.service_type.id in (8,) and zakaz.count_ip > 0:
                            service_type = Service_type.objects.get(id=10)
                            tariff_obj = Tariff.objects.get(id=26)
                            cost_ip = tariff_obj.price_id.cost / 1.18 * zakaz.count_ip
                            cost = cost + cost_ip
                cost_nds_in_words = perewod(str(cost))
                return cost_nds_in_words.decode("utf-8")

            elif option == "nds":
                params_data = get_zayavka()
                redirect_after_sign = params_data["redirect_after_sign"]
                package_obj = Package_on_connection_of_service.objects.get(url_after_sign=redirect_after_sign, user=user, activate=False, deactivate=False)
                try:
                    data_temp = eval(package_obj.data)
                    try:
                        zakaz_id = data_temp["hidden_id"]
                        zakaz_obj = Zakazy.objects.get(id=zakaz_id)
                        if zakaz_obj.service_type.id in (11,):
                            server_id, count_ip = zakaz_obj.server.id, zakaz_obj.count_ip
                            speed_obj = Zakazy.objects.get(main_zakaz=zakaz_id)
                            speed_inet_id = speed_obj.tariff.id
                            cost = cost_calculation(server_id, count_ip, speed_inet_id)
                            log.add(cost)
                            cost = float(cost)
                            cost = cost * 1.18
                        elif zakaz_obj.service_type.id in (2,):
                            cost = zakaz_obj.cost
                            pod_zakazy_qs = Zakazy.objects.filter(main_zakaz=zakaz_obj.id, status_zakaza__in=[1, 2, 4], cost__gt=0)
                            for pod_zakaz in pod_zakazy_qs:
                                log.add('pod_zakaz = %s' % pod_zakaz.cost)
                                cost += pod_zakaz.cost
                            if zakaz_obj.count_ip > zakaz_obj.tariff.ip:
                                for j in range(zakaz_obj.count_ip - zakaz_obj.tariff.ip):
                                    zakaz_ip = Zakazy(
                                        section_type=2,
                                        status_cost=1,
                                        service_type_id=10,
                                        tariff_id=41,
                                        count_ip=1,
                                        )
                                    cost_one_ip = float(cost_dc(0, zakaz_ip))
                                    log.add('cost_one_ip = %s' % cost_one_ip)
                                    cost += cost_one_ip
                            log.add(cost)
                        elif zakaz_obj.service_type.id in (1,):
                            cost = zakaz_obj.cost
                    except Exception, e:
                        log.add(e)
                        request_post = data_temp
                        hidden_id = request_post["hidden_id"]
                        zakazy_obj = Zakazy.objects.get(id=hidden_id)
                        cost = zakazy_obj.cost / 1.18
                except:
                    if redirect_after_sign == reverse("rack_zakaz"):
                        cost_obj = Tariff.objects.get(id=1)
                        cost_temp = cost_obj.price_id.cost / 1.18
                        cost = '%.2f' % cost_temp
#                    elif redirect_after_sign == reverse("colocation_zakaz"):
#                        cost = request_post["hidden_cost"]
                    elif redirect_after_sign == reverse("add_dedicated_final"):
                        server_id, count_ip, speed_inet_id = data_temp['server_id'], data_temp['count_ip'], data_temp['speed_inet_id']
                        cost_str = cost_calculation(server_id, count_ip, speed_inet_id)
                        cost = u'%.2f ' % (float(cost_str))
                    else:
                        zakaz_id = ''
                        for i in reversed(range(len(redirect_after_sign))):
                            if redirect_after_sign[i].isdigit():
                                zakaz_id += redirect_after_sign[i]
                        zakaz_id = zakaz_id[::-1]
                        zakaz = Zakazy.objects.get(id=zakaz_id)
                        cost = zakaz.cost
                        if zakaz.service_type.id in (8,) and zakaz.count_ip > 0:
                            service_type = Service_type.objects.get(id=10)
                            tariff_obj = Tariff.objects.get(id=26)
                            cost_ip = tariff_obj.price_id.cost / 1.18 * zakaz.count_ip
                            cost = cost + cost_ip
                nds_int = float(cost) / 1.18 * 0.18
                nds_int = '%.2f' % nds_int
                nds = str(nds_int) + u" руб."
                return nds

            elif option == "socket":
                params_data = get_zayavka()
                redirect_after_sign = params_data["redirect_after_sign"]
                package_obj = Package_on_connection_of_service.objects.get(url_after_sign=redirect_after_sign, user=user, activate=False, deactivate=False)
                try:
                    data_temp = eval(package_obj.data)
                    request_post = data_temp
                    hidden_id = request_post["hidden_id"]
                    zakazy_obj = Zakazy.objects.get(id=hidden_id)
                    socket = zakazy_obj.socket
                except:
                    if redirect_after_sign == reverse("colocation_zakaz"):
                        data_temp = eval(package_obj.data)
                        request_post = data_temp
                        socket = request_post["hidden_rozetka"]
                    elif redirect_after_sign == reverse("rack_zakaz"):
                        socket_obj = Tariff.objects.get(id=1)
                        socket = socket_obj.socket
                    elif redirect_after_sign == reverse("add_dedicated_final"):
                        data_temp = eval(package_obj.data)
                        socket_obj = Servers.objects.get(id=data_temp["server_id"])
                        socket = socket_obj.count_sockets
                return socket

            elif option == "ip":
                params_data = get_zayavka()
                redirect_after_sign = params_data["redirect_after_sign"]
                package_obj = Package_on_connection_of_service.objects.get(url_after_sign=redirect_after_sign, user=user, activate=False, deactivate=False)
                try:
                    data_temp = eval(package_obj.data)
                    request_post = data_temp
                    hidden_id = request_post["hidden_id"]
                    zakazy_obj = Zakazy.objects.get(id=hidden_id)
                    ip = len(zakazy_obj.ip.all())
                except:
                    if redirect_after_sign == reverse("colocation_zakaz"):
                        data_temp = eval(package_obj.data)
                        request_post = data_temp
                        ip = request_post["hidden_dop_IP"]
                    elif redirect_after_sign == reverse("rack_zakaz"):
                        ip_obj = Tariff.objects.get(id=1)
                        ip = ip_obj.ip
                    elif redirect_after_sign == reverse("add_dedicated_final"):
                        data_temp = eval(package_obj.data)
                        ip = data_temp["count_ip"]

                return ip

            elif option == "service_type":
                params_data = get_zayavka()
                service_type = ''
                redirect_after_sign = params_data["redirect_after_sign"]  # валится на этой строчке params_data возвращает пустой словарь
                try:
                    package_obj = Package_on_connection_of_service.objects.get(url_after_sign=redirect_after_sign, user=user, activate=False, deactivate=False)
                    data_temp = eval(package_obj.data)
                    request_post = data_temp
                    hidden_id = request_post["hidden_id"]
                    zayavka = Zakazy.objects.get(id=hidden_id)
                    service_type = zayavka.service_type
                except:
                    zakaz_id = ''
                    for i in reversed(range(len(redirect_after_sign))):
                        if redirect_after_sign[i].isdigit():
                            zakaz_id += redirect_after_sign[i]
                    zakaz_id = zakaz_id[::-1]
                    zakaz = Zakazy.objects.get(id=zakaz_id)
                    if zakaz.service_type.id in (8,):
                        service_type = u'%s (%s, %s Мбит/сек)' % (zakaz.service_type, zakaz.tariff.name, zakaz.tariff.speed_inet)
                    else:
                        service_type = zakaz.service_type
                    log.add('service_type = %s ' % service_type)

                return service_type

            elif option == "service_type_for_free_inet":
                service_type = Service_type.objects.get(id=8)
                package_obj = Package_on_connection_of_service.objects.get(user=user, activate=False, deactivate=False)
                param = eval(package_obj.data)
                tariff_obj = Tariff.objects.get(id=param['tariff_id'])
                service_type = u'%s (%s, %s Мбит/сек)' % (service_type, tariff_obj.name, tariff_obj.speed_inet)
                return service_type

            elif option == "equipment":
                params_data = get_zayavka()
                redirect_after_sign = params_data["redirect_after_sign"]
                package_obj = Package_on_connection_of_service.objects.get(url_after_sign=redirect_after_sign, user=user, activate=False, deactivate=False)
                data_temp = eval(package_obj.data)
                try:
                    request_post = data_temp
                    hidden_id = request_post["hidden_id"]
                    zayavka = Zakazy.objects.get(id=hidden_id)
                    service_tupe = zayavka.service_type.id
                    if  service_tupe == 11:
                        equipment = u'%s' % zayavka.server.name
                    else:
                        equipment = zayavka.equipment
                except:
                    if redirect_after_sign == reverse("add_dedicated_final"):
                        equipment_obj = Servers.objects.get(id=data_temp['server_id'])
                        equipment = u"%s" % equipment_obj.name
                return equipment
            elif option == 'dop_uslugi_in_act':
                try:
                    log.add('dop_uslugi_in_act')
                    params_data = get_zayavka()
                    service_type = ''
                    spis_podzakaz = ''
                    redirect_after_sign = params_data["redirect_after_sign"]
                    package_obj = Package_on_connection_of_service.objects.get(url_after_sign=redirect_after_sign, user=user, activate=False, deactivate=False)
                    if package_obj.data:
                        data_temp = eval(package_obj.data)
                        data = data_temp
                    else:
                        data = {}
                    if data.has_key('zakazy_on_activation'):
                        zakaz_id = data['zakazy_on_activation'][0]
                    if data.has_key('spis_podzakaz'):
                        spis_podzakaz = data['spis_podzakaz']
                    elif data.has_key('hidden_id'):
                        zakaz_id = data['hidden_id']
                    else:
                        zakaz_id = ''
                        for i in reversed(range(len(redirect_after_sign))):
                            if redirect_after_sign[i].isdigit():
                                zakaz_id += redirect_after_sign[i]
                        zakaz_id = zakaz_id[::-1]
                    zakaz = Zakazy.objects.get(id=zakaz_id)
                    if zakaz.service_type.id in (8,):
                        count_ip = 0
                        if spis_podzakaz:
                            zakazy_ip_queryset = Zakazy.objects.filter(main_zakaz=zakaz.id, status_zakaza=2)
                            for zakaz_obj_ip in zakazy_ip_queryset:
                                if zakaz_obj_ip.id in spis_podzakaz:
                                    count_ip = count_ip + 1
                        else:
                            count_ip = zakaz.count_ip
                        if count_ip > 0:
                            tr_table = ''
                            service_type = Service_type.objects.get(id=10)
                            tariff_obj = Tariff.objects.get(id=26)
                            cost = tariff_obj.price_id.cost / 1.18
                            tr_table = tr_table + '<tr>\
                                                    <td style="text-align: center; vertical-align: middle;">%s</td>\
                                                    <td>%s</td>\
                                                    <td style="text-align: center; vertical-align: middle;">%s</td>\
                                                    <td style="text-align: center; vertical-align: middle;">%s</td>\
                                                    <td style="text-align: center; vertical-align: middle;">%s</td>\
                                                    <td style="text-align: center; vertical-align: middle;">%s</td>\
                                                    </tr>' % (2, u'%s' % service_type, count_ip, u'шт', cost, cost * zakaz.count_ip)
                            return tr_table
                        else:
                            return ''
                    elif zakaz.service_type.id in (2, 11):
                        tr_table = ''
                        i = 1
                        pod_zakazy_qs = Zakazy.objects.filter(main_zakaz=zakaz.id, status_zakaza__in=[1, 2, 4], cost__gt=0)
                        for pod_zakaz in pod_zakazy_qs:
                            i += 1
                            tr_table = tr_table + '<tr>\
                                                    <td style="text-align: center; vertical-align: middle;">%s</td>\
                                                    <td>%s</td>\
                                                    <td style="text-align: center; vertical-align: middle;">%s</td>\
                                                    <td style="text-align: center; vertical-align: middle;">%s</td>\
                                                    <td style="text-align: center; vertical-align: middle;">%s</td>\
                                                    <td style="text-align: center; vertical-align: middle;">%s</td>\
                                                    </tr>' % (i, u'%s' % pod_zakaz.tariff.name, 1, u'шт', pod_zakaz.cost, pod_zakaz.cost)
                        if zakaz.count_ip > zakaz.tariff.ip:
                            for j in range(zakaz.count_ip - zakaz.tariff.ip):
                                i += 1
                                zakaz_ip = Zakazy(
                                    section_type=2,
                                    status_cost=1,
                                    service_type_id=10,
                                    tariff_id=41,
                                    count_ip=1,
                                    )
                                cost_one_ip = float(cost_dc(0, zakaz_ip))
                                tr_table = tr_table + '<tr>\
                                                        <td style="text-align: center; vertical-align: middle;">%s</td>\
                                                        <td>%s</td>\
                                                        <td style="text-align: center; vertical-align: middle;">%s</td>\
                                                        <td style="text-align: center; vertical-align: middle;">%s</td>\
                                                        <td style="text-align: center; vertical-align: middle;">%s</td>\
                                                        <td style="text-align: center; vertical-align: middle;">%s</td>\
                                                        </tr>' % (i, u'%s' % zakaz_ip.service_type, 1, u'шт', cost_one_ip, cost_one_ip)

                        return tr_table
                    else:
                        return ''
                except Exception, e:
                    import os, sys
                    log.add("Exception in create_check: '%s'" % e)
                    exc_type, exc_obj, exc_tb = sys.exc_info()  # @UnusedVariable
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    log.add("Exception in create_check: file:%s line:%s" % (fname, exc_tb.tb_lineno))
                    return ''

            elif option == "date_application":
                sd = get_signed(user, "telematic_data_centr")
                return sd.signed_at.strftime("%d.%m.%Y")
            elif option == "date_application_tsc":
                sd = get_signed(user, "telematic_services_contract")
                return sd.signed_at.strftime("%d.%m.%Y")
            elif option == "date_application_lsc":
                sd = get_signed(user, "localphone_services_contract")
                return sd.signed_at.strftime("%d.%m.%Y")
            elif option == "external_number_for_blank_na_otkr":
                params_data = get_zayavka()
                ext_number_id = ''
                redirect_after_sign = params_data["redirect_after_sign"]
                for i in reversed(range(len(redirect_after_sign))):
                    if redirect_after_sign[i].isdigit():
                        ext_number_id += redirect_after_sign[i]
                ext_number_id = ext_number_id[::-1]
                ext_number_obj = ExternalNumber.objects.get(id=ext_number_id)
                return ext_number_obj.number
            elif option == 'number_doc_requisites':
                package_obj = Package_on_connection_of_service.objects.get(user=user, activate=False, deactivate=False)
                data = eval(package_obj.data)
                spis_slugs = data['spis_slugs']
                slug = spis_slugs[0]
                sd = get_signed(user, slug)
                return sd.id
            elif option == 'date_application_requisites':
                package_obj = Package_on_connection_of_service.objects.get(user=user, activate=False, deactivate=False)
                data = eval(package_obj.data)
                spis_slugs = data['spis_slugs']
                slug = spis_slugs[0]
                sd = get_signed(user, slug)
                return sd.signed_at.strftime("%d.%m.%Y")

            elif option == 'line_read_point':
                package_obj = Package_on_connection_of_service.objects.get(user=user, activate=False, deactivate=False)
                data = eval(package_obj.data)
                spis_slugs = data['spis_slugs']
                slug = spis_slugs[0]
                sd = get_signed(user, slug)
                if slug in ('telematic_services_contract'):
                    point = '9.2.'
                elif slug in ('telematic_data_centr'):
                    point = '66'
                elif slug in ('localphone_services_contract'):
                    point = '12.2.'
                line = u'1. Читать пункт № %s к договору № %s от %s в следующей редакции:' % (point, sd.id, sd.signed_at.strftime("%d.%m.%Y"))
                return line

            elif option == 'spis_dogovor_for_change_of_requisites':
                dict_id_findoc = FinDocSigned.objects.filter(Q(signed_by=user) & Q(findoc__slug__in=['telematic_services_contract',
                                                                                                 'telematic_data_centr',
                                                                                                 'localphone_services_contract',
                                                                                                 'dogovor_oferta']) & \
                                                             (Q(cancellation_date=None) | Q(cancellation_date__gt=datetime.datetime.now()))).values('id')
                spis_id = [str(i["id"]) for i in dict_id_findoc]
                str_id = ', '.join(spis_id)
                return str_id

            elif option == 'points_of_contracts':
                package_obj = Package_on_connection_of_service.objects.get(user=user, activate=False, deactivate=False)
                data = eval(package_obj.data)
#                try:
#                    data_profile = data['profile']
#                except:
#                    data_profile = {}
                request_post = data['request_post']
                spis_slugs = data['spis_slugs']
                slug = spis_slugs[0]
                profile = Profile.objects.get(user=user)

                legal_form = profile.legal_form + ' ' if profile.legal_form else ''
                if profile.is_juridical:
                    try:
                        company_name_or_family = u"«" + profile.company_name + u"»"
                    except:
                        company_name_or_family = u" " + profile.company_name + u" "
                if not profile.is_juridical:
                    last_name = profile.last_name
                    first_name = profile.first_name
                    second_name = profile.second_name
                    company_name_or_family = last_name + " " + first_name + " " + second_name

                if slug in ('telematic_services_contract'):
                    point_abonent = u'9.2. Абонент'
                elif slug in ('telematic_data_centr'):
                    point_abonent = u'66. КЛИЕНТ'
                elif slug in ('localphone_services_contract'):
                    point_abonent = u'12.2. КЛИЕНТ'

                requisites = '''
                    <table border="1" cellpadding="0" cellspacing="0">
                    <tbody>
                        <tr>
                            <td style="width:175px;">
                                <p>
                                    <strong><u>%(point_abonent)s</u></strong><strong>:</strong></p>
                            </td>
                            <td style="width:516px;">
                                <p><strong><u>%(legal_form)s%(user_company_name)s</u></strong><strong><u></u></strong></p>
                            </td>
                        </tr>'''
                requisites = requisites % {
                                           "point_abonent": point_abonent,
                                           "legal_form": legal_form,
                                           "user_company_name": company_name_or_family,
                                           }

                if profile.is_juridical:
                    table_address = '''
                        <tr>
                            <td style="width:175px; height:42px; vertical-align: top;">
                                    <u>%(str_jur_address)s</u>:
                            </td>
                            <td style="width:516px; height:42px; vertical-align: top;">
                                    %(user_address_legal)s
                            </td>
                        </tr>
                        <tr>
                            <td style="width:175px; height:42px; vertical-align: top;">
                                    <u>%(str_fact_address)s:</u>
                            </td>
                            <td style="width:516px; height:42px; vertical-align: top;">
                                    %(user_address_postal)s
                            </td>
                        </tr>
                        <tr>
                            <td style="width:175px; height:42px; vertical-align: top;">
                                    <u>%(str_postal_address)s</u>:
                            </td>
                            <td style="width:516px; height:42px; vertical-align: top;">
                                    %(user_address_postal)s
                            </td>
                        </tr>'''
                    address_legal = profile.address(ADDRESS_TYPE_LEGAL)
                    legal_address_form = AddressLegalForm(request_post.copy(), instance=address_legal, prefix='address_legal')
                    legal_address_form.is_valid()
                    changed_data_address_legal = legal_address_form.changed_data
                    country = legal_address_form.cleaned_data['country'] if 'country' in changed_data_address_legal else getattr(address_legal, 'country')
                    state = legal_address_form.cleaned_data['state'] if 'state' in changed_data_address_legal else getattr(address_legal, 'state')
                    zipcode = legal_address_form.cleaned_data['zipcode'] if 'zipcode' in changed_data_address_legal else getattr(address_legal, 'zipcode')
                    city = legal_address_form.cleaned_data['city'] if 'city' in changed_data_address_legal else getattr(address_legal, 'city')
                    address_line = legal_address_form.cleaned_data['address_line'] if 'address_line' in changed_data_address_legal else getattr(address_legal, 'address_line')
                    user_address_legal = ','.join(x for x in [country, state, zipcode, city, address_line])

                    address_postal = profile.address(ADDRESS_TYPE_POSTAL)
                    address_postal_form = AddressPostalForm(request_post.copy(), instance=address_postal, prefix='address_postal')
                    address_postal_form.is_valid()
                    changed_data_address_postal = address_postal_form.changed_data
                    country = address_postal_form.cleaned_data['country'] if 'country' in changed_data_address_postal else getattr(address_postal, 'country')
                    state = address_postal_form.cleaned_data['state'] if 'state' in changed_data_address_postal else getattr(address_postal, 'state')
                    zipcode = address_postal_form.cleaned_data['zipcode'] if 'zipcode' in changed_data_address_postal else getattr(address_postal, 'zipcode')
                    city = address_postal_form.cleaned_data['city'] if 'city' in changed_data_address_postal else getattr(address_postal, 'city')
                    address_line = address_postal_form.cleaned_data['address_line'] if 'address_line' in changed_data_address_postal else getattr(address_postal, 'address_line')
                    user_address_postal = ','.join(x for x in [country, state, zipcode, city, address_line])

                    table_address = table_address % {
                                             "str_jur_address" : u'Юридический адрес',
                                             "str_fact_address": u'Фактический адрес',
                                             "str_postal_address": u'Почтовый адрес',
                                             "user_address_legal": user_address_legal,
                                             "user_address_postal": user_address_postal,
                                             }
#                if not profile.is_juridical:
#                    table_address = '''
#                    <tr>
#                        <td style="width:175px; height:42px; vertical-align: top;"><u>%(str_phys_address)s</u>
#                        </td>
#                        <td style="width:516px; height:42px; vertical-align: top;">%(phys_address)s
#                        </td>
#                    </tr>'''
#                    address_physical = profile.address(ADDRESS_TYPE_PHYSICAL)
#                    if data.has_key('address_physical'):
#                        data_physical = data['address_physical']
#                        if data_physical.has_key('country'):
#                            country = data_physical['country']
#                        else:
#                            country = address_physical.country
#                        if data_physical.has_key('state'):
#                            state = data_physical['state']
#                        else:
#                            state = address_physical.state
#                        if data_physical.has_key('zipcode'):
#                            zipcode = data_physical['zipcode']
#                        else:
#                            zipcode = address_physical.zipcode
#                        if data_physical.has_key('city'):
#                            city = data_physical['city']
#                        else:
#                            city = address_physical.city
#                        if data_physical.has_key('address_line'):
#                            address_line = data_physical['address_line']
#                        else:
#                            address_line = address_physical.address_line
#                        user_address_physical = ','.join(x for x in \
#                                                       [country,
#                                                        state,
#                                                        zipcode,
#                                                        city,
#                                                        address_line])
#                    else:
#                        user_address_physical = address_physical
#                    table_address = table_address % {
#                                             "str_phys_address": u'Физический адрес',
#                                             "phys_address": user_address_physical,
#                                             }

                requisites += table_address

                if profile.is_juridical:
                    requisites += '''
                        <tr>
                            <td style="width:175px; height:42px; vertical-align: top;">
                                    <u>%(inn_kpp)s</u>:
                            </td>
                            <td style="width:516px; height:42px; vertical-align: top;">
                                <p>
                                    %(user_inn)s</p>
                            </td>
                        </tr>
                        <tr>
                            <td style="width:175px; height:42px; vertical-align: top;">
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
                                <p>
                                    %(okpo)s%(user_okpo)s</p>
                            </td>
                        </tr>'''

                    corporate_form_additional = ProfileJuridicalDataAdditionalForm(request_post.copy(), instance=profile, prefix='corporate')
                    corporate_form_ignored = ProfileJuridicalDataIgnoredForm(request_post.copy(), instance=profile, prefix='corporate')
                    corporate_form_additional.is_valid()
                    corporate_form_ignored.is_valid()
                    changed_data_corporate_form_additional = corporate_form_additional.changed_data
                    changed_data_corporate_form_ignored = corporate_form_ignored.changed_data
                    user_inn = getattr(profile, 'bank_address')
                    user_kpp = getattr(profile, 'kpp')
                    user_bank_name = corporate_form_additional.cleaned_data['bank_name'] if 'bank_name' in changed_data_corporate_form_additional else getattr(profile, 'bank_name')
                    user_settlement_account = corporate_form_additional.cleaned_data['settlement_account'] if 'settlement_account' in changed_data_corporate_form_additional else getattr(profile, 'settlement_account')
                    user_correspondent_account = corporate_form_additional.cleaned_data['correspondent_account'] if 'correspondent_account' in changed_data_corporate_form_additional else getattr(profile, 'correspondent_account')
                    user_bik = corporate_form_additional.cleaned_data['bik'] if 'bik' in changed_data_corporate_form_additional else getattr(profile, 'bik')
                    user_okpo = corporate_form_additional.cleaned_data['okpo'] if 'okpo' in changed_data_corporate_form_additional else getattr(profile, 'okpo')
                    requisites = requisites % {
                                               "inn_kpp": u'ИНН / КПП',
                                               "bank_requisites": u'Банковские реквизиты',
                                               "bank": u'Банк: ',
                                               "rs": u'р/с: ',
                                               "ks": u'к/с: ',
                                               "bik": u'БИК: ',
                                               "okpo": u'ОКПО: ',
                                               "user_inn": user_inn + u'/' + user_kpp,
                                               "user_bank_name": user_bank_name,
                                               "user_settlement_account": user_settlement_account,
                                               "user_correspondent_account": user_correspondent_account,
                                               "user_bik": user_bik,
                                               "user_okpo": user_okpo,
                                               }
#                if not profile.is_juridical:
#                    requisites += '''<tr>
#                            <td style="width:175px; height:42px; vertical-align: top;">
#                                    <u>%(str_passport)s</u>:
#                            </td>
#                            <td style="width:516px; height:42px; vertical-align: top;">
#                                <p>
#                                    %(str_pasport_serial)s%(pasport_serial)s</p>
#                                <p>
#                                    %(str_when_given_out)s%(when_given_out)s</p>
#                                <p>
#                                    %(str_by_whom_given_out)s%(by_whom_given_out)s</p>
#                            </td>
#                        </tr>'''
#                    if data_profile.has_key('pasport_serial'):
#                        pasport_serial = data_profile['pasport_serial']
#                    else:
#                        pasport_serial = profile.pasport_serial
#                    if data_profile.has_key('when_given_out'):
#                        when_given_out = data_profile['when_given_out']
#                    else:
#                        when_given_out = profile.when_given_out
#                    if data_profile.has_key('by_whom_given_out'):
#                        by_whom_given_out = data_profile['by_whom_given_out']
#                    else:
#                        by_whom_given_out = profile.by_whom_given_out
#                    requisites = requisites % {
#                                               "str_passport": u'Паспортные данные',
#                                               "str_pasport_serial": u'Номер паспорта: ',
#                                               "pasport_serial": pasport_serial,
#                                               "str_when_given_out": u'Когда выдан: ',
#                                               "when_given_out": when_given_out,
#                                               "str_by_whom_given_out": u'Кем выдан: ',
#                                               "by_whom_given_out": by_whom_given_out,
#                                               }

                phones = corporate_form_ignored.cleaned_data['phones'] if 'phones' in changed_data_corporate_form_ignored else getattr(profile, 'phones')
                requisites += '''
                                <tr>
                                    <td style="width:175px;">
                                        <p>
                                            <u>%(number_word)s</u>:</p>
                                    </td>
                                    <td style="width:516px;">
                                        <p>
                                            %(phones)s</p>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="width:175px;">
                                        <p>
                                            <u>E-mail</u>:</p>
                                    </td>
                                    <td style="width:516px;">
                                        <p>
                                            %(user_email)s</p>
                                    </td>
                                </tr>
                            </tbody>
                        </table>'''
                requisites = requisites % {
                                           "number_word": u'Тел. / Факс',
                                           "phones": phones,
                                           "user_email": user.email,
                                           }
                return requisites


            return ""


    result = [
        Variable(
            "findoc_number",
            u"Номер текущего подписываемого документа",
            FinDocVarValue(option="findoc_number")
        ),

        Variable(
            "number_act_arenda_obor",
            u"Номер текущего подписываемого документа",
            FinDocVarValue(option="number_act_arenda_obor")
        ),
        Variable(
            "equipment_arenda_obor",
            u"Номер текущего подписываемого документа",
            FinDocVarValue(option="equipment_arenda_obor")
        ),
        Variable(
            "number_arenda_obor",
            u"Номер текущего подписываемого документа",
            FinDocVarValue(option="number_arenda_obor")
        ),
        Variable(
            "date_arenda_obor",
            u"Номер текущего подписываемого документа",
            FinDocVarValue(option="date_arenda_obor")
        ),


        Variable(
            "findoc_number_poddelka",
            u"Номер текущего подписываемого документа",
            FinDocVarValue(option="findoc_number_poddelka")
        ),
        Variable(
            "date_poddelka",
            u"Номер текущего подписываемого документа",
            FinDocVarValue(option="date_poddelka")
        ),


        Variable(
            "telematic_data_centr",
            u"Номер телематического договора дата-центра, к которому прикрепляется приложение",
            FinDocVarValue(option="telematic_data_centr")
        ),
        Variable(
            "telematic_services_contract",
            u"Номер телематического договора на голос",
            FinDocVarValue(option="telematic_services_contract")
        ),
        Variable(
            "localphone_services_contract",
            u"Номер договора на местную телефонную связь",
            FinDocVarValue(option="localphone_services_contract")
        ),
        Variable(
            "remove_number_oferta",
            u"Номер договора оферты, во время расторжения этого договора",
            FinDocVarValue(option="remove_number_oferta")
        ),
        Variable(
            "remove_date_dogovor_oferta",
            u"Дата подписания договора оферты, во время расторжения этого договора",
            FinDocVarValue(option="remove_date_dogovor_oferta")
        ),
        Variable(
            "findoc_name",
            u"Название текущего подписываемого документа",
            FinDocVarValue(option="findoc_name")
        ),
        Variable(
            "findoc_display_name",
            u"Отображаемое имя текущего подписываемого документа",
            FinDocVarValue(option="findoc_display_name")
        ),
        Variable(
            "service_name",
            u"Название оборудования",
            FinDocVarValue(option="service_name")
        ),
        Variable(
            "service_price",
            u"Цена услуги с ндс",
            FinDocVarValue(option="service_price")
        ),
        Variable(
            "application_number_tdc",
            u"Номер приложения по отношению к телематическому договору дата-центра",
            FinDocVarValue(option="application_number_tdc")
        ),
        Variable(
            "application_number_tdc_for_free_inet",
            u"Номер приложения по отношению к телематическому договору дата-центра для бесплатного интернета",
            FinDocVarValue(option="application_number_tdc_for_free_inet")
        ),
        Variable(
            "number_application_for_tdc",
            u"Номер приложения по отношению к телематическому договору дата-центра (при уже существующем приложении)",
            FinDocVarValue(option="number_application_for_tdc")
        ),
        Variable(
            "number_application_for_lsc",
            u"Номер приложения по отношению к договору местной телефонной связи(при уже существующем приложении)",
            FinDocVarValue(option="number_application_for_lsc")
        ),
        Variable(
            "application_number_lsc",
            u"Возвращает номера текущего подписываемого договора по отношению к договору местной телефонной связи",
            FinDocVarValue(option="application_number_lsc")
        ),
        Variable(
            "number_dop_sogl_izmeneniya",
            u"Возвращает номер текущего подписываемого соглашения об изменении услуги интернет по отношению к договору оферты",
            FinDocVarValue(option="number_dop_sogl_izmeneniya")
        ),

        Variable(
            "number_dogovor_oferta",
            u"Возвращает номер договора оферты примыкающего к заказу",
            FinDocVarValue(option="number_dogovor_oferta")
        ),

        Variable(
            "date_dogovor_oferta",
            u"Возвращает дату подписания договора оферты примыкающего к заказу",
            FinDocVarValue(option="date_dogovor_oferta")
        ),

        Variable(
            "speed_inet_in_oferta",
            u"Скорость интернета для договоры оферты",
            FinDocVarValue(option="speed_inet_in_oferta")
        ),

        Variable(
            "abonenka_cost_in_oferta",
            u"Абонентская плата услуги интернет для договоры оферты",
            FinDocVarValue(option="abonenka_cost_in_oferta")
        ),

        Variable(
            "cost_ip_in_oferta",
            u"Стоимость ip-адреса для договоры оферты",
            FinDocVarValue(option="cost_ip_in_oferta")
        ),

        Variable(
            "count_ip_in_oferta",
            u"Количество ip-адресов для договоры оферты",
            FinDocVarValue(option="count_ip_in_oferta")
        ),

        Variable(
            "all_cost_in_oferta",
            u"Итоговая сумма услуги интернет для договоры оферты",
            FinDocVarValue(option="all_cost_in_oferta")
        ),

        Variable(
            "date_start_izmeneniya",
            u"Дата вступления изменений конфигурации для договоры оферты",
            FinDocVarValue(option="date_start_izmeneniya")
        ),

        Variable(
            "date_remove_internet",
            u"Дата прекращения услуги интернет для договоры оферты",
            FinDocVarValue(option="date_remove_internet")
        ),

        Variable(
            "speed_inet",
            u"Скорость интернета в Кб",
            FinDocVarValue(option="speed_inet")
        ),
        Variable(
            "cost_inet",
            u"Стоимость услуги 'Доступ в интернет'",
            FinDocVarValue(option="cost_inet")
        ),
        Variable(
            "count_ip_inet",
            u"Количество статических IP-адресов для доступа в интернет'",
            FinDocVarValue(option="count_ip_inet")
        ),
        Variable(
            "unit",
            u"Количество юнитов / высота сервера",
            FinDocVarValue(option="unit")
        ),
        Variable(
            "electricity",
            u"Потребляемая мощностью, Вт",
            FinDocVarValue(option="electricity")
        ),
        Variable(
            "port",
            u"Количество портов коммутатора",
            FinDocVarValue(option="port")
        ),
        Variable(
            "cost",
            u"Стоимость услуги",
            FinDocVarValue(option="cost")
        ),
        Variable(
            "cost_nds",
            u"Стоимость услуги c НДС",
            FinDocVarValue(option="cost_nds")
        ),
        Variable(
            "cost_nds_in_words",
            u"Стоимость услуги c НДС прописью",
            FinDocVarValue(option="cost_nds_in_words")
        ),
        Variable(
            "nds",
            u"НДС",
            FinDocVarValue(option="nds")
        ),
        Variable(
            "socket",
            u"Количество розеток",
            FinDocVarValue(option="socket")
        ),
        Variable(
            "ip",
            u"Количество IP адресов",
            FinDocVarValue(option="ip")
        ),
        Variable(
            "service_type",
            u"Тип заказываемой услуги",
            FinDocVarValue(option="service_type")
        ),

        Variable(
            "service_type_for_free_inet",
            u"Тип заказываемой услуги для бесплатного интернета",
            FinDocVarValue(option="service_type_for_free_inet")
        ),

        Variable(
            "equipment",
            u"Возвращает тип оборудования при заказе услуги colocation",
            FinDocVarValue(option="equipment")
        ),
        Variable(
            "dop_uslugi_in_act",
            u"Возвращает в акт приемки-передачи выполненных работа в таблицу строку строку с количеством ip-адресов",
            FinDocVarValue(option="dop_uslugi_in_act")
        ),
        Variable(
            "date_application",
            u"Дата подписания телематического договора",
            FinDocVarValue(option="date_application")
        ),
        Variable(
            "date_application_lsc",
            u"Дата подписания договора местной телефонной связи",
            FinDocVarValue(option="date_application_lsc")
        ),
        Variable(
            "date_application_tsc",
            u"Дата подписания телематического договора на голос",
            FinDocVarValue(option="date_application_tsc")
        ),

        Variable(
            "external_number_for_blank_na_otkr",
            u"Номер, который пользователь сейчас собирается удалить",
            FinDocVarValue(option="external_number_for_blank_na_otkr")
        ),
        Variable(
            "number_doc_requisites",
            u"Номер договора, к которому прикрепляется доп.соглашение (для изменения реквизитов)",
            FinDocVarValue(option="number_doc_requisites")
        ),

        Variable(
            "date_application_requisites",
            u"Дата подписания договора, к которому прикрепляется доп.соглашение (для изменения реквизитов)",
            FinDocVarValue(option="date_application_requisites")
        ),
        Variable(
            "points_of_contracts",
            u"Возвращает исправленный пункт из договора для доп.соглашения (для изменения реквизитов)",
            FinDocVarValue(option="points_of_contracts")
        ),
        Variable(
            "line_read_point",
            u"Возвращает строку 'Читать пункт ...' для доп.соглашения (для изменения реквизитов)",
            FinDocVarValue(option="line_read_point")
        ),
        Variable(
            "spis_dogovor_for_change_of_requisites",
            u"Возвращает список договоров, в которых должны быть изменены реквизиты",
            FinDocVarValue(option="spis_dogovor_for_change_of_requisites")
        ),
        Variable(
            "ezernet_speed",
            u"Возвращает скорость портов коммутатора в услуге 'Услуга сервера'",
            FinDocVarValue(option="ezernet_speed")
        ),

        Variable(
            "table_form_zakaz",
            u"Возвращает таблицу с оборудованием, которое пользователь заказывает у нас",
            FinDocVarValue(option="table_form_zakaz")
        ),


    ]

    return result




