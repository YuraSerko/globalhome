# coding: utf-8
from lib.decorators import render_to
from lib.decorators import login_required
from billing.models import BillserviceAccount 
from data_centr.models import Zakazy
from django.db.models import Q
from devices.models import Devices
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.utils import simplejson
from account.forms import UserRegistrationForm
from django.shortcuts import render_to_response
from account.forms import UserLoginForm2
from findocs.views import create_package
from django.core.urlresolvers import reverse
from django.contrib.auth import login
from account.models import ActionRecord
from django.shortcuts import HttpResponse
from data_centr.models import Tariff
from findocs.models import FinDocTemplate, FinDoc
from lib.transliterate import transliterate
import zipfile, shutil, os
from findocs.models import FinDocSignApplication, Package_on_connection_of_service, FinDocSigned
import datetime
from django.contrib.auth.models import User
from findocs.views import create_package
from django.core.urlresolvers import reverse 
from account.models import Profile
from data_centr.views import cost_dc
from data_centr.views import add_record_in_data_centr_payment, add_record_in_priority_of_services, write_off_of_money
from findocs.models import FinDocSignedZakazy
from findocs.models import FinDocSignedZakazy, Package_on_connection_of_service, Rules_of_drawing_up_documents, Check
from data_centr.views import cost_dc, add_document_in_dict_for_send, send_mail_check
from devices.models import UserService
from findocs import decorator_for_sign_applications
from dateutil.relativedelta import relativedelta  
from lib.mail import send_email
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from data_centr.models import ZakazyDelivery

#======================================================================================================================
# отображает список всего оборудования пользователя
@login_required
@render_to('equipment_rent_list.html')
def equipment_rent_list(request):
    context = {}
    addr_tel_dict = {}
    
    # если заказ неактивен берем информацию о заказе из пакетов 
    #  pack_spis_equipment - словарь для хранения информации об оборудовании
    pack_spis_equipment = {}
    equipment_string = ""
    package_objs = Package_on_connection_of_service.objects.filter(user=request.user, url_after_sign='/account/add_equipment_rent/', activate=True, deactivate=False, activate_admin=False).order_by('id')
    for package_obj in package_objs:
        data = eval(package_obj.data) 
        spis_equipment = data['spis_equipment']
        for key, value in spis_equipment.iteritems():
            device_obj = Devices.objects.get(tariff=key)
            equipment_string = equipment_string + '<br>' + device_obj.name + ":" + str(value) + u'шт.' + '</br>'
        length_st = len(equipment_string) - 2
        equipment_string_cut = equipment_string[0:length_st + 2]
        pack_spis_equipment[package_obj.id] = equipment_string_cut
        equipment_string = ''  
    # считаем стоимость пакета (создадим словарь packet_cost)
    packet_cost = {}
    cost = 0
    for package_obj in package_objs:
        data = eval(package_obj.data) 
        # сохраним адрес и телефон в отдельный словарь
        try:
            del_address = data['delivery_address']
            tel_number = data['tel_number']
            addrr_telnum = u'Доставка курьером по aдресу ' + del_address + u' тел.' + tel_number
            addr_tel_dict[package_obj.id] = addrr_telnum
        except KeyError:
            addr_tel_dict[package_obj.id] = 'Получать с паспортом по адресу ул. Миклухо-Маклая дом 23'  
        spis_equipment = data['spis_equipment']
        for key, value in spis_equipment.iteritems():
            for i in range(int(value)):  # @UnusedVariable
                device_obj = Devices.objects.get(tariff=key)
                cost = cost + int(device_obj.abonent_fee)
        packet_cost[package_obj.id] = cost 
        cost = 0   
    # словари с номерами пакета и списком оборудования  
    if package_objs:
        context['package_objs'] = package_objs
    if pack_spis_equipment:
        context['pack_spis_equipment'] = pack_spis_equipment
    if packet_cost:
        context['packet_cost'] = packet_cost
    if addr_tel_dict:
        context['addr_tel_dict'] = addr_tel_dict
    

    # если заказ активен
    tariff_device_dict = {}
    bill_acc = BillserviceAccount.objects.get(username=request.user.username)
    cont_zayavki_act = Zakazy.objects.filter(Q(bill_account=bill_acc.id) & Q(section_type=2) & Q(status_zakaza_id__in=[2]) & Q(service_type_id=13)).order_by('id')
    devices_objs = Devices.objects.all()
    for devices_obj in devices_objs:
        tariff_similiar = Tariff.objects.get(id=devices_obj.tariff.id)
        tariff_device_dict[tariff_similiar.id] = devices_obj.id
    devices = Devices.objects.all()  
    if cont_zayavki_act:
        context["cont_zayavki_act"] = cont_zayavki_act
    if tariff_device_dict:
        context["tariff_device_dict"] = tariff_device_dict
    if devices:
        context["devices"] = devices
    context["current_view_name"] = "equipment_list"
    
    # если заказ с доставкой
    delivery = {}
    str_delivery = ''
    bill_acc = BillserviceAccount.objects.get(username=request.user.username)
    cont_zayavki_act = Zakazy.objects.filter(Q(bill_account=bill_acc.id) & Q(section_type=2) & Q(status_zakaza_id__in=[2]) & Q(service_type_id=13)).order_by('id')
    context['spisok_zak'] = cont_zayavki_act
    
    for i in cont_zayavki_act:
        try:
            zak_del_wr_off = ZakazyDelivery.objects.get(zakazy_write_off__id=i.id)
            all_zakaz_to_delivery = zak_del_wr_off.zakazy_list.all()
            for j in all_zakaz_to_delivery:
                device_obj = Devices.objects.get(tariff__id=j.tariff.id)
                str_delivery = str_delivery + '<br>' + str(j.id) + 20 * '&nbsp' + str(device_obj.name) + ';' + '</br>'
            delivery[zak_del_wr_off.id] = str_delivery
            str_delivery = ''
 
        except ZakazyDelivery.DoesNotExist:
            pass

    zak_del_all = ZakazyDelivery.objects.all()
    context['zak_del_all'] = zak_del_all 
    context['delivery'] = delivery
    
    
    return context
#===================================================================================================================
# передаем данные в окно выбора параметров заказа оборудования(список всех типов и данные по выбранному типу оборудования)
@render_to('equipment_rent_step_zakaz.html')
def ajax_equipment_rent_step_zakaz(request, account, device_id):
    context = {}
    # данные о выбранном типе оборудования (записываем в словарь)
    device_descr = get_object_or_404(Devices, id=device_id)
    device = {'device_id':device_descr.id, 'name':device_descr.name, 'abonent_fee':device_descr.abonent_fee,
               'tariff_id':device_descr.tariff.id, 'tariff':device_descr.tariff.name, }
    # данные обо всех существующих видах оборудовния (передаем как queryset)
    devices_queryset = Devices.objects.all()  
    context['devices_queryset'] = devices_queryset
    context['device'] = device
    context['account'] = eval(account)
    context['user'] = request.user.username
    return context

#===================================================================================================
# функция для подсчета стоимости выбранного оборудования
def cost_calculation(device_id, quantity):
    device_descr = get_object_or_404(Devices, id=device_id)
    cost = int(device_descr.abonent_fee) * int(quantity)
    return cost

#===================================================================================================
# по смене в select типа оборудования берем  необходимые параметры(абонентскую плату, тариф, тариф id)
def ajax_change_device_type(request, device_id):
    device_descr = get_object_or_404(Devices, id=device_id)
    try:
        quantity = request.GET['quantity'] 
    except:
        raise Http404
    cost = cost_calculation(device_id, quantity)
    return HttpResponse(u'%s_%s_%s_%s' % (device_descr.abonent_fee, cost, device_descr.tariff.id, device_descr.tariff.name))
   
#===================================================================================================
def ajax_add_item(request):
    device_id_name = ''
    abonent_f = ''
    devices_queryset = Devices.objects.all()
    for i in devices_queryset:
        device_id_name = device_id_name + str(i.id) + "#" + i.name + "~"
        if (abonent_f == ''):
            abonent_f = str(i.abonent_fee)

    return HttpResponse(u'%s?%s' % (device_id_name, abonent_f))


#===================================================================================================
def ajax_equipment_rent_step_auth(request, account):
    param, context = {}, {}
    try:
        account = eval(account)
        if request.GET.get("delivery_address"):
            delivery_address = request.GET['delivery_address']
        if request.GET.get("tel_number"):
            tel_number = request.GET['tel_number']
        
        # сформируем словарь для передачи словарь spis_equipment
        equipments = request.GET['equipments']
        dlina = len(equipments) - 1
        spis_equipment_cut = equipments[0:dlina]
        spis_equipment_arr = spis_equipment_cut.split(',')
        redir = spis_equipment_arr[0].split(":")[0]
        spis_equipment_dev = {}
        spis_equipment = {}
        i = 0
        check_param = 0
        while  (i < len(spis_equipment_arr)):
            dev_arr = spis_equipment_arr[i].split(':')
            # проверяем наличие такого же device_id если есть складываем количество и обновляем тот же элемент словаря
            # если нет заводим новый элемент
            if (not spis_equipment_dev):
                spis_equipment_dev[dev_arr[0]] = dev_arr[1]
            else:
                ks = spis_equipment_dev.keys()
                # проверим новый элемент на совпадение с каждым из существующим элементом
                for k in ks:
                    if (k == dev_arr[0]):
                        spis_equipment_dev[dev_arr[0]] = int(spis_equipment_dev[dev_arr[0]]) + int(dev_arr[1])
                        check_param = 1
                if (check_param == 0): 
                    spis_equipment_dev[dev_arr[0]] = dev_arr[1]
            # обнуляем проверку на сохраненный элемент увеличенный по значению
            check_param = 0     
            # увеличиваем счетчик
            i = i + 1 
        # получили список оборудования таблицы devices теперь получим список оборудования таблицы Tariff
        check_param_tar = 0 
        sp_eq_keys = spis_equipment_dev.keys()
        for sp_eq_key in sp_eq_keys:
            device_obj = Devices.objects.get(id=sp_eq_key)
            if (not spis_equipment):
                spis_equipment[device_obj.tariff_id] = spis_equipment_dev[sp_eq_key]
            else:
                sp_eq_tar_keys = spis_equipment.keys()
                for sp_eq_tar_key in sp_eq_tar_keys:
                    if (sp_eq_tar_key == device_obj.tariff_id):
                        spis_equipment[device_obj.tariff_id] = int(spis_equipment[device_obj.tariff_id]) + int(spis_equipment_dev[sp_eq_key])
                        check_param_tar = 1
                if (check_param_tar == 0): 
                    spis_equipment[device_obj.tariff_id] = spis_equipment_dev[sp_eq_key]
            check_param_tar = 0  
    except:
        raise Http404
    if (request.GET.get("delivery_address")  and request.GET.get("tel_number")):
        delivery_address = request.GET['delivery_address']
        tel_number = request.GET['tel_number']
        # для договора
        param['delivery_address'], param['tel_number'] = delivery_address, tel_number
    param['spis_equipment'] = spis_equipment
    context['data'] = simplejson.dumps(param)
    if not account:
        param['face'] = request.GET['face']
        context['spis_equipment'] = spis_equipment
        context['redir'] = redir
        if param['face'] == '0':
            form_reg = UserRegistrationForm()
            context['form_reg'] = form_reg
            return render_to_response("step_reg3.html", context)
        elif param['face'] == '1':
            form_login = UserLoginForm2()
            context['form_login'] = form_login
            return render_to_response("step_login3.html", context)
        # если пользователь уже в системе
        elif param['face'] == '2':
            # создается запись в таблице package_on_connection_of_service
            # содержащая url после подписания договора и url после отмены подписания договора (2,3 параметры преобразуются функцией reverse)
            # 4 параметр записывает в поле data данные в виде словаря
            # 5 параметр содержит непосредственно списокок slugoв договоров записывается в поле slugs_document
            # successfully_create возвращает true или false
            # добавлеяем все договора кроме 'telematic_services_contract', 'telematic_data_centr', 'localphone_services_contract'
            # если они были подписаны пользователем хотя бы один раз
            successfully_create = create_package(request.user,
                                reverse('add_equipment_rent'),
                                reverse('equipment_rent_list'),
                                '%s' % param,
                                ['dogovor_arendi_serverov'],
                                ['akt_priema_peredachi_oborudovaniya_spisok'],)
            if not successfully_create:
                raise Http404
            return render_to_response("s8.html", context)
    else:
        successfully_create = create_package(request.user,
                                reverse('add_equipment_rent'),
                                reverse('equipment_rent_list'),
                                '%s' % param,
                                ['dogovor_arendi_serverov'],
                                ['akt_priema_peredachi_oborudovaniya_spisok'])
        if not successfully_create:
            raise Http404
        return HttpResponseRedirect(reverse('add_equipment_rent'))

#=============================================================================================
@render_to('sign_findoc_admin.html')
def equipment_rent_sign_doc(request):
    try:
        pack_id = request.GET['pack_id']
    except:
        raise Http404
    package_obj = Package_on_connection_of_service.objects.get(id=pack_id)
    # находим объект User
    user_obj = User.objects.get(id=package_obj.user.id)
    # найдем id для findoc c соответствующим slugs
    findoc_obj = FinDoc.objects.get(slug='akt_priema_peredachi_oborudovaniya_spisok')
    now = datetime.datetime.now()
    # создаем объект FinDocSignApplication(заявка)
    doc = FinDocSignApplication(
                        assigned_at=now,
                        findoc=findoc_obj,
                        assigned_to=user_obj,
                        user_can_cancel=True,
                        service_for_billing="application_from_a_package")
    doc.save()
    app_text = doc.process_text(request=request, findocapp_id=doc.id)
    # подписываем документ берем admin slugs
    if doc.findoc.applied_to:
        applied_to_id = doc.findoc.applied_to.id
    else:
        applied_to_id = None
    list_params = doc.sign_with_params_data(user_obj, text=app_text, applied_to_id=applied_to_id)
    package_obj = Package_on_connection_of_service.objects.get(id=pack_id, user=user_obj, activate=True, deactivate=False, activate_admin=False)
    slugs_list_temp = package_obj.slugs_document_admin
    slugs_list = slugs_list_temp.split(', ')
    del slugs_list[0]
    slugs_str = ', '.join(slugs_list)
    package_obj.slugs_document_admin = slugs_str
    findocsigned_obj = FinDocSigned.objects.get(id=list_params["findoc_id"])
    package_obj.findoc_sign.add(findocsigned_obj)
    package_obj.save()

    # создаем в базе данных запись в таблице data_centr_zakazy
    profile_obj = Profile.objects.get(user=user_obj)
    bill_acc = BillserviceAccount.objects.get(id=profile_obj.billing_account_id)
    try:
        package_obj = Package_on_connection_of_service.objects.get(id=pack_id, user=user_obj, activate=True, deactivate=False, activate_admin=False)
        data = eval(package_obj.data)
    except Package_on_connection_of_service.DoesNotExist:
        if not data('device'):
            raise Http404
    spis_zakaz = []
    now = datetime.datetime.now()
    spis_equipment = data['spis_equipment']
    if  not(data.has_key('delivery_address')) and not(data.has_key('tel_number')):
        data['delivery_address'] = 'no_delivery'
        data['tel_number'] = 'no_delivery'
    else:
        # создаем запись в data_centr_zakazy_delivery
        zakazy_delivery = ZakazyDelivery()
        zakazy_delivery.save()

    for key, value in spis_equipment.iteritems():
        for i in range(int(value)):  # @UnusedVariable
            tariff_obj = Tariff.objects.get(id=key)
            zakaz = Zakazy(
                     bill_account=bill_acc,
                     section_type=2,
                     status_zakaza_id=2,  # ставим статус заказа активен
                     service_type_id=13,
                     tariff=tariff_obj,
                     date_create=now,
                     date_activation=now,
                     delivery_address=data['delivery_address'],
                     delivery_telephone=data['tel_number'],
                     )
            zakaz.save()
            cost = float(cost_dc(zakaz.id))
            zakaz.cost = '%.2f' % cost
            zakaz.save()
            # если нужна доставка записываем в промежуточную таблицуы
            if (zakaz.delivery_address != 'no_delivery') and (zakaz.delivery_telephone != 'no_delivery'):
                zakazy_delivery.zakazy_list.add(zakaz)

            spis_zakaz.append(zakaz.id)
            if i == (int(value) - 1):
                if (zakaz.delivery_address != 'no_delivery') and (zakaz.delivery_telephone != 'no_delivery'):
                    zakazy_delivery.zakazy_write_off = zakaz
                    zakazy_delivery.save()
                    tariff_delivery_obj = Tariff.objects.get(id=112)  # тариф на доставку
                    zakaz.delivery = tariff_delivery_obj
                    zakaz.save()
            add_record_in_data_centr_payment(zakaz)
            add_record_in_priority_of_services(zakaz)
            findocsign_queryset = package_obj.findoc_sign.filter(findoc__slug='dogovor_arendi_serverov')
            findocsign_obj = findocsign_queryset[0]
            fin_doc_zakaz = FinDocSignedZakazy(
                                               fin_doc=findocsign_obj,
                                               zakaz_id=zakaz.id,
                                               )
            fin_doc_zakaz.save()




    package_obj.activate_admin = True
    package_obj.save()
    spis_rules = Check.group_rules(profile_obj, [15], 'type_check', zakaz.id)
    content_check_id = Check.create_check(user_obj, spis_rules, False, spis_zakaz)
    dict_documents_for_send = add_document_in_dict_for_send({}, user_obj.id, 'Check', content_check_id)
    send_mail_check(dict_documents_for_send)
    return HttpResponse()

#=============================================================================================
def ajax_equipment_rent_step_login(request):
    context = {}
    errors = {}
    form_login = UserLoginForm2(request.GET)
    context['form_login'] = form_login
    try:
        param = simplejson.loads((str(request.GET['data'])).strip('/'))
    except Exception, e:
        raise Http404
    context['data'] = simplejson.dumps(param)
    context['redir'] = request.GET['redir']
    try:
        if form_login.is_valid():
            user = form_login.user
            if user:
                if user.is_active:
                    login(request, user)
                    successfully_create = create_package(request.user,
                                reverse('add_equipment_rent'),
                                reverse('equipment_rent_list'),
                                '%s' % param,
                                ['dogovor_arendi_serverov'],
                                ['akt_priema_peredachi_oborudovaniya_spisok'])
                    if not successfully_create:
                        raise Http404
                    return render_to_response("s8.html", context)
            if user is None:
                errors['error_auth'] = True
                context['errors'] = errors
                return render_to_response("step_login3.html", context)
        else:
            errors['error_auth'] = True
            context['errors'] = errors
            return render_to_response("step_login3.html", context)
    except Exception, e:
        print e
    else:
        return render_to_response("step_login3.html", context)


def ajax_equipment_rent_step_registration(request):
    context = {}
    errors = {}
    form_reg = UserRegistrationForm(request.GET)
    context['form_reg'] = form_reg
    try:
        param = simplejson.loads((str(request.GET['data'])).strip('/'))
    except Exception, e:
        print e
        raise Http404
    context['data'] = simplejson.dumps(param)
    context['redir'] = request.GET['redir']
    if form_reg.is_valid():
        user = form_reg.save()
        ActionRecord.registrations.create_inactive_user_key(
            new_user=user,
            row_password=form_reg.get_row_password(),
            send_email=True,
            )
        successfully_create = create_package(request.user,
                                reverse('add_equipment_rent'),
                                reverse('equipment_rent_list'),
                                '%s' % param,
                                ['dogovor_arendi_serverov'],
                                ['akt_priema_peredachi_oborudovaniya_spisok'])
        if not successfully_create:
            raise Http404
        return render_to_response("s8_reg.html", context)
    else:
        errors['error_auth'] = True
        context['errors'] = errors
        return render_to_response("step_reg3.html", context)
#================================================================================

@login_required
@render_to('account/equipment_rent_list.html')
@decorator_for_sign_applications()
def equipment_rent_del_zakaz(request, hidden_id, **kwargs):
    zak = request.GET.get('zakaz_id')
    kwargs['zakaz_id'] = zak
    zakazy_obj = Zakazy.objects.get(id=hidden_id)
    
    
    # запишем список оборудования (тарифы)
    tariff_obj = Tariff.objects.get(id=zakazy_obj.tariff.id)
    param = {}
    spisok = {}
    spisok[tariff_obj.id] = 1
    param['spis_equipment'] = spisok
    
    try:
        package_obj = Package_on_connection_of_service.objects.get(user=request.user, activate=False, deactivate=False)
    except Package_on_connection_of_service.DoesNotExist:
        successfully_create = create_package(request.user,
                                '/account/equipment_rent_list/zakaz/%s/' % hidden_id,
                                reverse('equipment_rent_list'),
                                '%s' % param,
                                [''],
                                ['akt_priema_peredachi_oborudovaniya_2', 'dop_soglashenie_k_dogovoru_arenda_obor', ],
                                )
        
        if not successfully_create:
            raise Http404
        else:
            return HttpResponseRedirect('/account/equipment_rent_list/zakaz/%s/' % hidden_id)
    try:
        profile = Profile.objects.get(user=request.user)
        bac = profile.billing_account
        now = datetime.datetime.now()
        date_next_start_month_temp = now + relativedelta(months=1)
        date_next_start_month = datetime.datetime(date_next_start_month_temp.year, date_next_start_month_temp.month, 1, 0, 0, 0)
        zakaz = Zakazy.objects.get(id=hidden_id)
        if zakaz.bill_account == bac:
            zakaz.date_deactivation = date_next_start_month
            # zakaz.status_zakaza_id = 5
            zakaz.save()
            package_obj.activate = True
            package_obj.save()
            request.notifications.add((u"Заказ успешно деактивирован!"), "success")
        else:
            request.notifications.add((u"Вы попытались удалить не существующий у Вас заказ!"), "warning")
    except:
        raise Http404
    #send_email(u"Новый запрос на деактивацию услуги 'аренда оборудования'", "Заказ № %s ссылка:  http://globalhome.su/admin/data_centr/zakazy/%s/" % (str(hidden_id), str(hidden_id)), settings.DEFAULT_FROM_EMAIL, ["Zz1n@globalhome.su", 'sales@globalhome.su', 'noc@globalhome.su'])
    return HttpResponseRedirect("/account/equipment_rent_list/")
#=========================================================================================================
@login_required
@render_to('account/equipment_rent_list.html')
def del_package(request, package_id):
    try:
        package_obj = Package_on_connection_of_service.objects.get(user=request.user, id=package_id)  
        package_obj.deactivate = True 
        package_obj.save()
        request.notifications.add((u"Заявка успешно деактивирована!"), "success")
    except UserService.DoesNotExist:
        raise Http404
    return HttpResponseRedirect("/account/equipment_rent_list/")


#==========================================================================================================


@login_required
@decorator_for_sign_applications()
def add_equipment_rent(request):
    package_obj = Package_on_connection_of_service.objects.get(user=request.user, activate=False, deactivate=False)
      
    package_obj.activate = True
    package_obj.save()
    #send_email(u"Новый запрос на услугу 'аренда оборудования'", "Пакет № %s ссылка:   http://globalhome.su/admin/findocs/package_on_connection_of_service/%s/" % (package_obj.id, package_obj.id), settings.DEFAULT_FROM_EMAIL, ["Zz1n@globalhome.su", 'sales@globalhome.su', 'noc@globalhome.su']) 
    request.notifications.add(_(u"Заявка успешно добавлена!"), "success")
    return HttpResponseRedirect("/account/equipment_rent_list/")
    


