# coding: utf-8
from django.utils.translation import ugettext_lazy as _
from django.http import Http404, HttpResponseRedirect
from lib.decorators import render_to, login_required
from findocs.models import FinDocSignApplication, FinDocSigned, Package_on_connection_of_service, FinDoc, \
    FinDocSignedZakazy
from findocs import decorator_for_sign_applications
import log
from django.conf import settings  # @UnresolvedImport
from django.core.urlresolvers import reverse
# from findocs import check_for_sign_applications
from devices.models import ApplicationService, UserService
import datetime
from django.db import connections, transaction
import urllib  # @UnusedImport
from externalnumbers.models import ExternalNumber
from lib.transliterate import transliterate
import zipfile, shutil, os
from django.db.models import Q
from account.models import Profile
from dateutil.relativedelta import relativedelta  # @UnresolvedImport
from data_centr.models import Zakazy
from telnumbers.models import TelNumbersZakazy


FINDOCS_NOT_TO_DELETE = ('telematic_services_contract', 'telematic_data_centr', 'localphone_services_contract')#, '800_contract')

def create_package(user_obj, url_after_sign, url_after_cancel, params_data='', slugs=[], slugs_admin=[],):
    try:
        slugs_list = []
        successfully_create = False
        for slug in slugs:
            if slug in FINDOCS_NOT_TO_DELETE: 
                findoc_obj = FinDoc.objects.get(slug=slug)  
                findocsigned_queryset = FinDocSigned.objects.filter(signed_by=user_obj, findoc=findoc_obj, cancellation_date=None)  
                if findocsigned_queryset:  
                    continue  
                else:
                    slugs_list.append(slug) 
            else:
                slugs_list.append(slug) 
        if slugs_list:
            slugs_str = ', '.join(slugs_list)
           
            package_queryset = Package_on_connection_of_service.objects.filter(user=user_obj,
                                                                               activate=False,
                                                                               deactivate=False)
            for package_obj in package_queryset: 
                package_obj.deactivate = True  
                try:
                    data = package_obj.data
                    data = eval(data)
                    for del_number in data['numbers']:
                        if del_number[0:4] in ('7495', '7499'):
                            region = 1
                        elif del_number[0:4] == '7812':
                            region = 2
                        elif del_number[0:4] == '7800':
                            region = 3
                        external_number_obj = ExternalNumber.objects.get(number=del_number)
                        external_number_obj.phone_numbers_group = None
                        external_number_obj.region = region
                        external_number_obj.account = None
                        external_number_obj.is_free = True
                        external_number_obj.is_reserved = False
                        external_number_obj.assigned_at = None
                        external_number_obj.auth_user = None
                        external_number_obj.save()
                    findoc_list = package_obj.findoc_sign.all()
                    for findocsign_obj in findoc_list:
                        if findocsign_obj.findoc.slug not in FINDOCS_NOT_TO_DELETE:
                            findocsign_obj.delete() 
                except:
                    pass
                package_obj.save()
            # запишем slugs для админа в отдельное поле
            slugs_list_admin = []
            for slug_admin in slugs_admin:
                slugs_list_admin.append(slug_admin)
            if slugs_list_admin:
                slugs_str_admin = ', '.join(slugs_list_admin)
            else:
                slugs_str_admin = ''
            # окончание записи slugs для admin     
            
            package_obj = Package_on_connection_of_service(
                                                       user=user_obj,
                                                       url_after_sign=url_after_sign,
                                                       url_after_cancel=url_after_cancel,
                                                       slugs_document=slugs_str,
                                                       data=params_data,
                                                       slugs_document_admin=slugs_str_admin,  # добавляем slugs for admin
                                                       date_create=datetime.datetime.now(),
                                                       
                                                       )
            package_obj.save()
            # если в пакете '/account/add_equipment_rent/' то после создания ставим статус
            if (package_obj.url_after_sign == '/account/add_equipment_rent/'):
                package_obj.package_status = 'Заявка в рассмотрении'
                package_obj.save()
            successfully_create = True
    except Exception, e:
        print "error in create package = %s" % e
    return successfully_create


def data_configuration(profile_obj, service_type_spis, spis_zakaz, spis_podzakaz, spis_zakaz_for_package):
    data = ''
    spis_slugs = []
    service_type_dict_jur_for_zakaz = {1:['telematic_data_centr', 'usluga_peredachi_dannyh_s_predoplatoi', 'akt_priemki_peredachi_vypoln_rabot'], \
                     2:['telematic_data_centr', 'usluga_peredachi_dannyh_s_predoplatoi', 'akt_priema_peredachi_oborudovaniya', 'akt_priemki_peredachi_vypoln_rabot'], \
                     3:['telematic_services_contract', 'localphone_services_contract', 'localphone_orderform'], \
                     8:['telematic_data_centr', 'usluga_peredachi_dannyh_s_predoplatoi_internet', 'akt_priemki_peredachi_vypoln_rabot']}
    service_type_dict_jur_for_zayavka = {8:['telematic_data_centr', 'usluga_peredachi_dannyh_s_predoplatoi_internet']}
    service_type_dict_phys_for_zakaz = {8:['dogovor_oferta', 'akt_priemki_peredachi_vypoln_rabot']}
    service_type_dict_phys_for_zayavka = {8:['dogovor_oferta']}
    spis_ext_number = []
    zakazy_on_activation = []
    # если у пользователя есть услуги с ТЕЛЕФОНИЕЙ
    if 3 in service_type_spis:
        for zakaz_id in spis_zakaz:
            zakaz_obj = Zakazy.objects.get(id=zakaz_id)
            if zakaz_obj.service_type.id == 3:
                for ext_number_obj in zakaz_obj.ext_numbers.all():
                    spis_ext_number.append(ext_number_obj.number)  # собираем список номеров
                spis_zakaz_for_package.remove(zakaz_id)  # здесь собираем список заказов с которыми ещё придется работать
                zakazy_on_activation.append(zakaz_id)  # а здесь заказы с которыми мы работает сейчас
        # получаем список слагов и компонуем data
        spis_slugs = service_type_dict_jur_for_zakaz[3]
        data = {'numbers': spis_ext_number, 'spis_zakaz':spis_zakaz_for_package, 'zakazy_on_activation':zakazy_on_activation, 'spis_podzakaz':spis_podzakaz}
    # если у пользоваля не было телефонии но есть АРЕНДА СЕРВЕРНЫХ СТОЕК, 'spis_podzakaz':spis_podzakaz
    elif 1 in service_type_spis:
        for zakaz_id in spis_zakaz:
            zakaz_obj = Zakazy.objects.get(id=zakaz_id)
            if zakaz_obj.service_type.id == 1:
                spis_zakaz_for_package.remove(zakaz_id)
                zakazy_on_activation.append(zakaz_id)
                spis_slugs = service_type_dict_jur_for_zakaz[1]
                data = {'hidden_id':zakaz_id, 'spis_zakaz':spis_zakaz_for_package, 'zakazy_on_activation':zakazy_on_activation, 'spis_podzakaz':spis_podzakaz}
                break
    # если у пользоваля не было ни телефонии ни аренды серверных стоек, то у него colocation серверов
    elif 2 in service_type_spis:
        for zakaz_id in spis_zakaz:
            zakaz_obj = Zakazy.objects.get(id=zakaz_id)
            if zakaz_obj.service_type.id == 2:
                spis_zakaz_for_package.remove(zakaz_id)
                zakazy_on_activation.append(zakaz_id)
                spis_slugs = service_type_dict_jur_for_zakaz[2]
                data = {'hidden_id':zakaz_id, 'spis_zakaz':spis_zakaz_for_package, 'zakazy_on_activation':zakazy_on_activation, 'spis_podzakaz':spis_podzakaz}
                break
    elif 8 in service_type_spis:
        print '2 spis_zakaz = %s' % spis_zakaz
        for zakaz_id in spis_zakaz:
            print 'zakaz_id = %s' % zakaz_id
            zakaz_obj = Zakazy.objects.get(id=zakaz_id)
            if zakaz_obj.service_type.id == 8:
                print 'spis_zakaz_for_package = %s' % spis_zakaz_for_package
                spis_zakaz_for_package.remove(zakaz_id)
                print '1 spis_zakaz_for_package = %s' % spis_zakaz_for_package
                zakazy_on_activation.append(zakaz_id)
                if profile_obj.is_juridical:
                    if zakaz_obj.date_activation:
                        spis_slugs = service_type_dict_jur_for_zakaz[8]
                    else:
                        spis_slugs = service_type_dict_jur_for_zayavka[8]
                else:
                    if zakaz_obj.date_activation:
                        spis_slugs = service_type_dict_phys_for_zakaz[8]
                    else:
                        spis_slugs = service_type_dict_phys_for_zayavka[8]
                if zakaz_obj.tariff.ip:
                    count_ip = zakaz_obj.count_ip - zakaz_obj.tariff.ip
                else:
                    count_ip = zakaz_obj.count_ip
                data = {'hidden_id':zakaz_id, 'tariff':zakaz_obj.tariff.id, 'count_static_ip': count_ip, \
                        'spis_zakaz':spis_zakaz_for_package, 'zakazy_on_activation':zakazy_on_activation, 'spis_podzakaz':spis_podzakaz}
                break
    return spis_slugs, data


@login_required
@decorator_for_sign_applications()
@render_to('contract_cancellation.html')
def contract_cancellation(request):
    print 'contract_cancellation'
    if request.user.get_profile().is_card:
        raise Http404
    try:
        package_obj = Package_on_connection_of_service.objects.get(user=request.user, activate=False, deactivate=False)
        dict_slug = eval(package_obj.data)
        saved, spis_zakaz, spis_podzakaz = deactivation_zakaz_under_the_contract(request.user, dict_slug)  # @UnusedVariable
        if not saved:
            raise Http404
        package_obj.activate = True
        package_obj.save()
        request.notifications.add(_(u"Договор успешно расторгнут!"), "success") 
    except Package_on_connection_of_service.DoesNotExist:
        pass
    if request.POST:
        if request.POST.get("findoc_id"):
            data_dict = {}
            findocsigned_obj = FinDocSigned.objects.get(id=request.POST["findoc_id"])
            if findocsigned_obj.cancellation_date:
                raise Http404
            if findocsigned_obj.findoc.slug in ['telematic_data_centr', 'localphone_services_contract', 'dogovor_oferta']:
                spis_slugs = ['remove_' + findocsigned_obj.findoc.slug]
                data_dict[findocsigned_obj.findoc.slug] = [findocsigned_obj.id]
            elif findocsigned_obj.findoc.slug in ['telematic_services_contract']:
                spis_slugs = ['remove_telematic_services_contract']
                data_dict[findocsigned_obj.findoc.slug] = [findocsigned_obj.id]
                findocs = FinDocSigned.objects.filter(Q(signed_by=request.user) & Q(findoc__slug='localphone_services_contract'))
                if findocs:
                    spis_slugs.append('remove_localphone_services_contract')
                    data_dict['localphone_services_contract'] = [findocsigned_obj.id]
            else:
                raise Http404
            successfully_create = create_package(request.user, \
                                    reverse('contract_cancellation'), \
                                    reverse('contract_cancellation'), \
                                    '%s' % data_dict,
                                    spis_slugs)
            if not successfully_create:
                raise Http404
            else:
                return HttpResponseRedirect(reverse('contract_cancellation'))
    context = {}
    context["findocs"] = FinDocSigned.objects.filter(Q(signed_by=request.user) & \
                                                     (Q(findoc__slug='telematic_services_contract') | Q(findoc__slug='telematic_data_centr') | Q(findoc__slug='localphone_services_contract') | Q(findoc__slug='dogovor_oferta')))
    context['current_view_name'] = 'account_profile'
    return context


def deactivation_zakaz_under_the_contract(user_obj, dict_slug={}):
    profile_obj = Profile.objects.get(user=user_obj)
    saved = False
    spis_zakaz = []
    spis_podzakaz = []
    if dict_slug:
        findocsigned_queryset = FinDocSigned.objects.filter(signed_by=user_obj, id__in=dict_slug[dict_slug.keys()[0]], cancellation_date=None)
    else:
        findocsigned_queryset = FinDocSigned.objects.filter(Q(signed_by=user_obj) & \
                    (Q(findoc__slug='telematic_services_contract') | Q(findoc__slug='telematic_data_centr') | \
                     Q(findoc__slug='localphone_services_contract') | Q(findoc__slug='dogovor_oferta')) & Q(cancellation_date=None))
    for findocsigned_obj in findocsigned_queryset:
        print 'number dogovor = %s' % findocsigned_obj.id
        if findocsigned_obj.findoc.slug in ['telematic_services_contract', 'localphone_services_contract']:
            section_type = [1]
        elif findocsigned_obj.findoc.slug in ['telematic_data_centr']:
            if profile_obj.is_juridical:
                section_type = [2, 3]
            else:
                section_type = [2]
        elif findocsigned_obj.findoc.slug in ['dogovor_oferta']:
            dict_slug = {'dogovor_oferta':findocsigned_obj.id}
        profile_obj = Profile.objects.get(user=user_obj)
        bill_acc_obj = profile_obj.billing_account
        now = datetime.datetime.now()
        date_next_start_month_temp = now + relativedelta(months=1)
        date_next_start_month = datetime.datetime(date_next_start_month_temp.year, date_next_start_month_temp.month, 1, 0, 0, 0)
        if dict_slug.has_key('dogovor_oferta'):
            spis_zakaz_oferta = []
            findoc_sign_zakazy_queryset = FinDocSignedZakazy.objects.filter(fin_doc__id=dict_slug['dogovor_oferta'])
            for findoc_sign_zakaz in findoc_sign_zakazy_queryset:
                spis_zakaz_oferta.append(findoc_sign_zakaz.zakaz_id)
            zakazy_queryset = Zakazy.objects.filter(id__in=spis_zakaz_oferta)
        else:
            zakazy_queryset = Zakazy.objects.filter(Q(bill_account=bill_acc_obj) & Q(section_type__in=section_type) & Q(date_deactivation=None) & \
                                                    (Q(status_zakaza__id=1) | Q(status_zakaza__id=2) | Q(status_zakaza__id=4)))
        for zakaz_obj in zakazy_queryset:
            spis_zakaz.append(zakaz_obj.id)
            if not zakaz_obj.date_activation:
                zakaz_obj.status_zakaza_id = 3
            zakaz_obj.date_deactivation = date_next_start_month
            zakaz_obj.save()
            if zakaz_obj.date_deactivation == zakaz_obj.date_activation:
                zakaz_obj.status_zakaza_id = 3
                zakaz_obj.save()
            zakazy_ip_queryset = Zakazy.objects.filter(main_zakaz=zakaz_obj.id, date_deactivation=None, status_zakaza=2)
            for zakaz_obj_ip in zakazy_ip_queryset:
                spis_podzakaz.append(zakaz_obj_ip.id)
                zakaz_obj_ip.date_deactivation = date_next_start_month
                zakaz_obj_ip.save()   
                if zakaz_obj_ip.date_deactivation == zakaz_obj.date_activation:
                    zakaz_obj_ip.status_zakaza_id = 3
                    zakaz_obj_ip.save() 
        if findocsigned_obj.findoc.slug in ['telematic_services_contract']:
            telnumber_queryset = TelNumbersZakazy.objects.filter(Q(bill_account=bill_acc_obj) \
                                                                 & Q(date_deactivation=None))
            for telnumber in telnumber_queryset:
                telnumber.date_deactivation = date_next_start_month
                telnumber.save()
        findocsigned_obj.cancellation_date = date_next_start_month
        findocsigned_obj.save()
        saved = True
        spis_zakaz.sort()
    return saved, spis_zakaz, spis_podzakaz


@login_required
@decorator_for_sign_applications()
def resigning_of_contracts(request):
    print 'resigning_of_contracts'
    try:
        package_obj = Package_on_connection_of_service.objects.get(user=request.user, activate=False, deactivate=False)
    except Package_on_connection_of_service.DoesNotExist:
        raise Http404
    profile_obj = Profile.objects.get(user=request.user)
    param_data = eval(package_obj.data)
    if param_data.has_key('package_cancel'):
        spis_zakaz_for_activation = []
        spis_podzakaz = []
        package_obj.deactivate = True
        package_obj.save()
    else:
        spis_zakaz_for_activation = param_data['zakazy_on_activation']
        print 'spis_zakaz_for_activation = %s' % spis_zakaz_for_activation
        spis_podzakaz = param_data['spis_podzakaz']
        package_obj.activate = True
        package_obj.save()
    for zakaz_id in spis_zakaz_for_activation:
        zakaz_obj = Zakazy.objects.get(id=zakaz_id)
        zakaz_obj.date_deactivation = None
        if not zakaz_obj.date_activation:
            zakaz_obj.status_zakaza_id = 1
        zakaz_obj.save()
        zakazy_ip_queryset = Zakazy.objects.filter(main_zakaz=zakaz_obj.id, status_zakaza=2)
        for zakaz_obj_ip in zakazy_ip_queryset:
            if zakaz_obj_ip.id in spis_podzakaz:
                zakaz_obj_ip.date_deactivation = None
                zakaz_obj_ip.save()
        print 'ser = %s' % zakaz_obj.service_type
        if zakaz_obj.service_type.id in (8,):
            print 'suda popal to'
            if not profile_obj.is_juridical:
                slug = 'dogovor_oferta'
            else:
                slug = 'telematic_data_centr'
            findocsign_obj = package_obj.findoc_sign.filter(findoc__slug=slug)
            if findocsign_obj:
                findoc_sign_zakaz = FinDocSignedZakazy.objects.get(zakaz_id=zakaz_obj.id, fin_doc__findoc__slug=slug)
                findoc_sign_zakaz.fin_doc = findocsign_obj[0]
                findoc_sign_zakaz.save()
            for zakaz_obj_ip in zakazy_ip_queryset:
                if zakaz_obj_ip.id in spis_podzakaz:
                    findocsign_obj = package_obj.findoc_sign.filter(findoc__slug=slug)
                    if findocsign_obj:
                        findoc_sign_zakaz = FinDocSignedZakazy.objects.get(zakaz_id=zakaz_obj_ip.id, fin_doc__findoc__slug=slug)
                        findoc_sign_zakaz.fin_doc = findocsign_obj[0]
                        findoc_sign_zakaz.save()
    spis_zakaz = param_data['spis_zakaz']
    spis_zakaz_for_package = spis_zakaz
    service_type_spis = []
    for zakaz_id in spis_zakaz:
        zakaz_obj = Zakazy.objects.get(id=zakaz_id)
        service_type_spis.append(zakaz_obj.service_type.id)
    spis_slugs, data = data_configuration(profile_obj, service_type_spis, spis_zakaz, spis_podzakaz, spis_zakaz_for_package)
    if not (spis_slugs or data):
        request.notifications.add(_(u'Form saved'), 'success')
        return HttpResponseRedirect(reverse('account_profile_edit'))
    successfully_create = create_package(request.user, \
                    reverse('resigning_of_contracts'), \
                    reverse('resigning_of_contracts'), \
                    '%s' % data,
                    spis_slugs)
    if not successfully_create:
        raise Http404
    else:
        return HttpResponseRedirect(reverse('resigning_of_contracts'))


@login_required
# @check_for_sign_applications([])
@render_to("list_signed.html")
def findocs_list_signed(request):

    if request.user.get_profile().is_card:
        raise Http404
    context = {}
    context["current_view_name"] = "account_profile"
    context["title"] = _("List of signed documents")
    context["findocs"] = FinDocSigned.objects.filter(signed_by=request.user).order_by('findoc__name', 'signed_at')
    return context

@login_required
# @check_for_sign_applications([])
@render_to("show_signed.html")
def findocs_show_signed(request, signed_id):

    user = request.user
    profile = user.get_profile()
    if profile.is_card:
        raise Http404

    context = {}
    try:
        sd = FinDocSigned.objects.get(id=signed_id)
    except Exception, e:
        log.add("Exception 1 in findocs.views.findocs_list_signed: '%s'" % e)
        raise Http404
    context["title"] = unicode(sd.findoc)
    context["signed_findoc"] = sd
    context["current_view_name"] = "account_profile"

    # создаем документ для скачки
    text = sd.signed_text.encode('utf-8')
    f_name = transliterate(sd.findoc.display_name.encode('utf-8'))
    filename = "%s" % f_name + "-" + "%s" % profile.id + "-" + "%s" % sd.id
    # filename = filenam.encode('utf-8')
    out_f = open('%s.doc' % filename, 'w')
    out_f.write(text)
    out_f.close()
    gz1 = zipfile.ZipFile ('%s.zip' % filename, 'w', 8)
    gz1.write(out_f.name)
    gz1.close()

    shutil.move('%s.zip' % filename, 'media/doc/%s.zip' % filename)
    os.remove('%s.doc' % filename)
    context["display"] = filename
    return context

@login_required
@render_to("app_sign.html")
def findocs_application_sign(request, app_id):
    user = request.user
    context = {}
    try:
        # таблица fin_docs_applications
        app = FinDocSignApplication.objects.get(id=app_id)
    except Exception, e:
        log.add("Exception 1 in findocs.views.findocs_application_sign: '%s'" % e)
        raise Http404

    if app.assigned_to != user:
        log.add("Somebody tries to sign application with id=%s to user %s. request.user = %s" % (app_id, app.assigned_to, user))
        raise Http404
    # записываем id из таблицы findocs
    context["title"] = unicode(app.findoc)
    context["application"] = app
    # ИМЕННО ЗДЕСЬ ПОДТЯГИВАЕМ ПЕРЕМЕННЫЕ В ШАБЛОН использую метод process_text
    # print "ID FINDOCSIGNAPPLICATION"
    # print app_id
    app_text = app.process_text(request=request, findocapp_id=app_id)
    # print 'APP_TEXT'
    # print app_text
    # здесь непосредственно передатеся текст договора из базы в html ку "app_sign.html"
    context["application_text"] = app_text
    context["user_can_cancel"] = app.user_can_cancel
    no = datetime.datetime.now()
    now = datetime.datetime(no.year, no.month, no.day)
    profile = user.get_profile()
    # а вот тут подписываем
    if request.POST:
        if request.POST.get("sign"):
            if request.POST.get("i_sign_it") == "on":
                cur = connections[settings.BILLING_DB].cursor()
                if app.service_for_billing == 'application_from_a_package':
                    if app.findoc.applied_to:
                        applied_to_id = app.findoc.applied_to.id
                    else:
                        applied_to_id = None
                    
                    list_params = app.sign_with_params_data(user, text=app_text, applied_to_id=applied_to_id)
                    redirect_after_sign = list_params["redirect_after_sign"]
                    package_obj = Package_on_connection_of_service.objects.get(url_after_sign=redirect_after_sign, user=user, activate=False, deactivate=False)
                    slugs_list_temp = package_obj.slugs_document
                    slugs_list = slugs_list_temp.split(', ')
                    del slugs_list[0]
                    slugs_str = ', '.join(slugs_list)
                    package_obj.slugs_document = slugs_str
                    findocsigned_obj = FinDocSigned.objects.get(id=list_params["findoc_id"])
                    package_obj.findoc_sign.add(findocsigned_obj)
                    package_obj.save()
                    return HttpResponseRedirect(redirect_after_sign)


                if app.service_for_billing == "document_for_the_service_connection":

                    try:
                        del_request = ApplicationService.objects.get(fin_doc_id=app.id)
                        url = app.sign(user, request, text=app_text)  # @UnusedVariable
                        if url:
                            return HttpResponseRedirect(url)
                        qwe = int(del_request.service)  # @UnusedVariable
                        cur.execute("SELECT * FROM billservice_addonservice WHERE id=%s;", (del_request.service,))
                        service = cur.fetchone()  # @UnusedVariable
                        # cur.execute("SELECT * FROM billservice_account WHERE id=%s;", (profile.billing_account_id,))
                        # prof = cur.fetchone()

                        cur.execute("SELECT id FROM billservice_accounttarif WHERE account_id=%s;", (profile.billing_account_id,))
                        account_tarif = cur.fetchone()  # @UnusedVariable
                        cur.execute("INSERT INTO billservice_accountaddonservice(service_id, account_id, activated, action_status) VALUES(%s, %s, %s, %s) RETURNING id;", (del_request.service, profile.billing_account_id, now, True))
                        id_for_accountaddonservice = cur.fetchone()  # @UnusedVariable

    #                    cur.execute("INSERT INTO billservice_addonservicetransaction(service_id, service_type, account_id, accountaddonservice_id, accounttarif_id, summ, created, type_id) VALUES(%s, %s, %s, %s, %s, %s, %s, %s);", (del_request.service, service[3], profile.billing_account_id, id_for_accountaddonservice, account_tarif, service[7], now, service[4]))
                        transaction.commit_unless_managed(settings.BILLING_DB)

                        del_request.delete()
                        request.notifications.add(_(u"Service is successfully activated!"), "success")
                        return HttpResponseRedirect(reverse("services"))
                    except UserService.DoesNotExist:
                        raise Http404

                if app.service_for_billing == "document_to_deactivate" and app.findoc.slug == "cancel":

                    try:
                        del_request = ApplicationService.objects.get(name=app.findoc.name)
                        cur.execute("SELECT account_id, action_status FROM billservice_accountaddonservice WHERE id=%s;", (app.for_services,))
                #        if cur.fetchall()[0]:
                        prowerka = cur.fetchall()[0]
                        transaction.commit_unless_managed(settings.BILLING_DB)
                #        else:
                #            request.notifications.add(_(u"Do not attempt to remove the service, Cator you do not!"), "error")
                #            return HttpResponseRedirect(reverse("services"))
                        if prowerka[0] == profile.billing_account_id and prowerka[1] == True:
                            cur.execute("UPDATE billservice_accountaddonservice SET action_status=%s, deactivated=%s WHERE id=%s;", (False, now, app.for_services,))
                            transaction.commit_unless_managed(settings.BILLING_DB)
                            request.notifications.add(_(u"Service successfully removed!"), "success")
                            del_request.delete()
                        else:
                            request.notifications.add(_(u"Do not attempt to remove the service, Cator you do not!"), "error")
                    except UserService.DoesNotExist:
                        raise Http404



                # вот теперь уже подписываем
                url = app.sign(user, request, text=app_text)  # @UnusedVariable
                if url:
                    return HttpResponseRedirect(url)
                return HttpResponseRedirect(reverse("account_profile"))
        if request.POST.get("cancel"):
            if app.user_can_cancel:
                if app.service_for_billing == "application_from_a_package":
                    list_params = app.unpickle_params()
                    redirect_after_sign = list_params["redirect_after_sign"]
                    package_obj = Package_on_connection_of_service.objects.get(url_after_sign=redirect_after_sign, user=user, activate=False, deactivate=False)
                    redirect_after_cancel = package_obj.url_after_cancel
                    findoc_list = package_obj.findoc_sign.all()
                    for findocsign_obj in findoc_list:
                        if findocsign_obj.findoc.slug not in FINDOCS_NOT_TO_DELETE:
                            findocsign_obj.delete()
                    if package_obj.url_after_cancel == reverse('resigning_of_contracts'):
                        data = package_obj.data
                        data = eval(data)
                        data.update({'package_cancel':''})
                        package_obj.data = data
                        package_obj.save()
                        return HttpResponseRedirect(redirect_after_cancel)
                    else:
                        package_obj.deactivate = True
                        package_obj.save()
                        app.delete()
                        if package_obj.data:
                            data = package_obj.data
                            data = eval(data)
                            if data.has_key('numbers'):
                                for del_number in data['numbers']:
                                    if del_number[0:4] in ('7495', '7499'):
                                        region = 1
                                    elif del_number[0:4] == '7812':
                                        region = 2
                                    elif del_number[0:4] == '7800':
                                        region = 3
                                    external_number_obj = ExternalNumber.objects.get(number=del_number)
                                    external_number_obj.phone_numbers_group = None
                                    external_number_obj.region = region
                                    external_number_obj.account = None
                                    external_number_obj.is_free = True
                                    external_number_obj.is_reserved = False
                                    external_number_obj.assigned_at = None
                                    external_number_obj.auth_user = None
                                    external_number_obj.save()
                    return HttpResponseRedirect(redirect_after_cancel)


                if app.service_for_billing == "document_for_the_service_connection":
                    if app.findoc.slug == "cancel":
                        return HttpResponseRedirect(reverse("services"))

                    del_request = ApplicationService.objects.get(fin_doc_id=app.id)
                    del_request.delete()
                    app.delete()
                    request.notifications.add(_(u"Aborted by the user!"), "warning")
                    return HttpResponseRedirect(reverse("services"))

                # если отменяем договор на отключение услуги
                if app.service_for_billing == "document_to_deactivate":
                    app.delete()
                    del_request = ApplicationService.objects.get(name=app.findoc.name)
                    del_request.delete()
                    request.notifications.add(_(u"Aborted by the user!"), "warning")
                    return HttpResponseRedirect(reverse("services"))

                url = app.cancel(request)  # @UnusedVariable
                if url:
                    return HttpResponseRedirect(url)
            return HttpResponseRedirect(reverse("account_profile"))
    return context
