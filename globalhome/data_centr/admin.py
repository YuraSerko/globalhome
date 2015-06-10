# coding: utf-8
from models import Zakazy, Status_zakaza, Status_ip, Service_type, Price, Price_connection, \
                    Tariff, IP, OS, CPU, RAM, HDD, Data_centr_payment, Priority_of_services, \
                    Units, Sockets, Blocks_of_socket, Ports, Switchs, Rack, Address_dc, Type_ram, Limit_connection_service, \
                    Motherboards, Servers, Slots_ram, Slots_hdd, Type_hdd, Server_assembly, Address_dc_full, \
                    Add_free_internet_zakaz, Restore_zakaz, ZakazyDelivery
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _, ugettext  # @UnusedImport
from data_centr.forms import Address_dc_full_Admin_Form
from django.db.models import Q
import datetime
from django.conf import settings  # @UnusedImport
from django.conf.urls import patterns
from lib.decorators import render_to
from django.contrib.admin.views.decorators import staff_member_required
from forms import ChangeRackInAddress, ChangeUnitInAddress, ChangePortInAddress, ChangeSockettInAddress, ChangeSwitchInAddress, \
                    ChangeBlockSocketInAddress, CityInternetForm, StreetInternetForm, HouseInternetForm, AccountInternetForm, \
                    TariffInternetForm, ZakazForm, RulesExternalNumber, RulesInetZakaz
from django.http import HttpResponse
from django.template import Template, Context
from django.utils.html import escape, escapejs
from lib.mail import send_email
from account.models import Profile
from django.contrib.sites.models import Site
from django.utils.safestring import mark_safe
from internet.admin import BillingTariffAdmin
from payment.forms import Billservice_transaction_Admin_Form
from billing.models import BillserviceAccount
from findocs.views import create_package
from django.core.urlresolvers import reverse
from findocs.models import Package_on_connection_of_service
from data_centr.views import cost_dc
from django.http import Http404
from internet.billing_models import SubAccount

# imports
from findocs.models import FinDocTemplate, FinDoc
from lib.transliterate import transliterate
import zipfile, shutil, os
from findocs.models import FinDocSignApplication
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from findocs.models import FinDocSigned
from django.db.models import Count
from findocs.models import FinDocSignedZakazy

def find_address(zakaz_obj, pod_zakaz, rack_qs, find_port=True, find_socket=True, find_unit=True, switchs_qs=[], block_socket_qs=[]):
    def optimize_find(zakaz_obj, pod_zakaz, rack_qs, find_port=True, find_socket=True, find_unit=True, switchs_qs=[], block_socket_qs=[]):
        rack_init = ''
        port_init = ''
        socket_init = ''
        switch_init = ''
        block_socket_init = ''
        ports_qs = ''
        block_socket_qs = block_socket_qs
        socket_qs = ''
        units_qs = ''
        switchs_qs = switchs_qs
        spis_units = []
        for rack_obj in rack_qs:
            if find_port:
                if not switchs_qs:
                    switchs_qs = Switchs.objects.filter(rack=rack_obj)
                for switch_obj in switchs_qs:
                    if port_init:
                        break
                    ports_qs = Ports.objects.filter(switch=switch_obj, speed=pod_zakaz.tariff.speed_inet).order_by('number_port')
                    for port_obj in ports_qs:
                        if port_obj.status_port in (2,):
                            port_init = port_obj
                            switch_init = switch_obj
                            break
                if not port_init:
                    continue
            if find_socket:
                if not block_socket_qs:
                    block_socket_qs = Blocks_of_socket.objects.filter(rack=rack_obj)
                for block_obj in block_socket_qs:
                    if socket_init:
                        break
                    socket_qs = Sockets.objects.filter(block_of_socket=block_obj).order_by('number_socket')
                    for socket_obj in socket_qs:
                        if socket_obj.status_socket in (2,):
                            socket_init = socket_obj
                            block_socket_init = block_obj
                            break
                if not socket_init:
                    continue
            if find_unit:
                units_qs = Units.objects.filter(rack=rack_obj).order_by('number_unit')  # zakaz_obj.server.count_unit
                for unit_obj in units_qs:
                    if unit_obj.status_unit in (2,):
                        spis_units.append(unit_obj)
                        if len(spis_units) == zakaz_obj.server.count_unit:
                            rack_init = rack_obj
                            break
                    else:
                        spis_units = []
            if rack_init:
                break
        return locals()

    var_dc = optimize_find(zakaz_obj, pod_zakaz, rack_qs, True, True, True, switchs_qs, block_socket_qs)
    if not var_dc['rack_init']:
        var_dc = {}
        var_port = optimize_find(zakaz_obj, pod_zakaz, [rack_qs[0]], True, False, False, switchs_qs)
        var_dc['port_init'], var_dc['ports_qs'], var_dc['switchs_qs'], var_dc['switch_init'] = var_port['port_init'], \
        var_port['ports_qs'], var_port['switchs_qs'], var_port['switch_init']
        var_socket = optimize_find(zakaz_obj, pod_zakaz, [rack_qs[0]], False, True, False, switchs_qs, block_socket_qs)
        var_dc['socket_init'], var_dc['socket_qs'], var_dc['block_socket_qs'], var_dc['block_socket_init'] = var_socket['socket_init'], \
        var_socket['socket_qs'], var_socket['block_socket_qs'], var_socket['block_socket_init']
        var_unit = optimize_find(zakaz_obj, pod_zakaz, [rack_qs[0]], False, False, True)
        var_dc['rack_init'], var_dc['spis_units'], var_dc['units_qs'] = var_unit['rack_init'], var_unit['spis_units'], var_unit['units_qs']
    return var_dc


@staff_member_required
def search_device(request, zakaz_id, rack_id, search=''):
    print 'search_rack'
    zakaz_obj = Zakazy.objects.get(id=zakaz_id)
    pod_zakaz = Zakazy.objects.get(main_zakaz=zakaz_id)
    rack_obj = Rack.objects.get(id=rack_id)
    if search == 'unit':
        var_dc = find_address(zakaz_obj, pod_zakaz, [rack_obj], False, False, True)  # @UnusedVariable
        form_unit = ChangeUnitInAddress(None, [(unit_obj.id, unit_obj) for unit_obj in var_dc['units_qs']], [i.id for i in var_dc['spis_units']])
        template = Template('{{ form_unit.unit }}')
        context = Context({"form_unit": form_unit})
    elif search == 'block_of_sockets':
        var_dc = find_address(zakaz_obj, pod_zakaz, [rack_obj], False, True, False)
        form_block_socket = ChangeBlockSocketInAddress(None, [(block_socket_obj.id, block_socket_obj) for block_socket_obj in var_dc['block_socket_qs']], var_dc['block_socket_init'])
        template = Template('{{ form_block_socket.block_socket }}')
        context = Context({"form_block_socket": form_block_socket})
    elif search == 'socket':
        if request.GET.has_key('block_socket_init'):
            block_socket_obj = Blocks_of_socket.objects.get(id=request.GET['block_socket_init'])
            var_dc = find_address(zakaz_obj, pod_zakaz, [rack_obj], False, True, False, [], [block_socket_obj])  # @UnusedVariable
        else:
            var_dc = find_address(zakaz_obj, pod_zakaz, [rack_obj], False, True, False, [])  # @UnusedVariable
        form_socket = ChangeSockettInAddress(None, [(socket_obj.id, socket_obj) for socket_obj in var_dc['socket_qs']], var_dc['socket_init'])
        template = Template('{{ form_socket.socket }}')
        context = Context({"form_socket": form_socket})
    elif search == 'switch':
        var_dc = find_address(zakaz_obj, pod_zakaz, [rack_obj], True, False, False)  # @UnusedVariable
        form_switch = ChangeSwitchInAddress(request.POST.copy(), [(switch_obj.id, switch_obj) for switch_obj in var_dc['switchs_qs']], var_dc['switch_init'])
        template = Template('{{ form_switch.switch }}')
        context = Context({"form_switch": form_switch})
    elif search == 'port':
        if request.GET.has_key('switch_init'):
            switch_obj = Switchs.objects.get(id=request.GET['switch_init'])
            var_dc = find_address(zakaz_obj, pod_zakaz, [rack_obj], True, False, False, [switch_obj])  # @UnusedVariable
        else:
            var_dc = find_address(zakaz_obj, pod_zakaz, [rack_obj], True, False, False)  # @UnusedVariable
        form_port = ChangePortInAddress(None, [(port_obj.id, port_obj) for port_obj in var_dc['ports_qs']], var_dc['port_init'])
        template = Template('{{ form_port.port }}')
        context = Context({"form_port": form_port})
    return HttpResponse(template.render(context))


@staff_member_required
@render_to("search_place_in_dc.html")
def search_place_in_dc(request, zakaz_id):
    print 'search_place_in_dc'
    context = {}
    change_rack_on_depth = {600: [0, 600], 800: [600, 800], 1000:[800, 1000]}
    zakaz_obj = Zakazy.objects.get(id=zakaz_id)
    pod_zakaz = Zakazy.objects.get(main_zakaz=zakaz_id)
    depth = 0
    context['server_depth'] = zakaz_obj.server.depth
    context['count_units'] = zakaz_obj.server.count_unit
    context['speed_port'] = pod_zakaz.tariff.speed_inet
    context['zakaz_id'] = zakaz_id
    for key, value in change_rack_on_depth.items():
        if zakaz_obj.server.depth in range(value[0], value[1]):
            depth = key
            break
    rack_qs = Rack.objects.filter(depth=depth, is_active=True, max_unit_for_server__gte=zakaz_obj.server.count_unit).order_by('name')
    if '_save' in request.POST:
        form_rack = ChangeRackInAddress(request.POST.copy(), [(rack_obj.id, rack_obj) for rack_obj in rack_qs],)
        if form_rack.is_valid():
            rack_obj = Rack.objects.get(id=form_rack.cleaned_data["rack"])
        else:
            return context

        var_dc = find_address(zakaz_obj, pod_zakaz, [rack_obj], False, False, True)
        form_unit = ChangeUnitInAddress(request.POST.copy(), [(unit_obj.id, unit_obj) for unit_obj in var_dc['units_qs']], '', zakaz_id)
        if form_unit.is_valid():
            final_spis_units = var_dc['spis_units']

        var_dc = find_address(zakaz_obj, pod_zakaz, [rack_obj], True, False, False)
        form_switch = ChangeSwitchInAddress(request.POST.copy(), [(switch_obj.id, switch_obj) for switch_obj in var_dc['switchs_qs']], var_dc['switch_init'])
        if form_switch.is_valid():
            switch_obj = Switchs.objects.get(id=form_switch.cleaned_data['switch'])
        else:
            switch_obj = ''

        if switch_obj:
            var_dc = find_address(zakaz_obj, pod_zakaz, [rack_obj], True, False, False, [switch_obj])
        else:
            var_dc = find_address(zakaz_obj, pod_zakaz, [rack_obj], True, False, False, [])
        form_port = ChangePortInAddress(request.POST.copy(), [(port_obj.id, port_obj) for port_obj in var_dc['ports_qs']], var_dc['port_init'])
        if form_port.is_valid():
            final_port_init = Ports.objects.get(id=form_port.cleaned_data['port'])

        var_dc = find_address(zakaz_obj, pod_zakaz, [rack_obj], False, True, False)
        form_block_socket = ChangeBlockSocketInAddress(request.POST.copy(), [(block_socket_obj.id, block_socket_obj) for block_socket_obj in var_dc['block_socket_qs']], var_dc['block_socket_init'])
        if form_block_socket.is_valid():
            block_socket_obj = Sockets.objects.get(id=form_block_socket.cleaned_data['block_socket'])
        else:
            block_socket_obj = ''

        if block_socket_obj:
            var_dc = find_address(zakaz_obj, pod_zakaz, [rack_obj], False, True, False, [], [block_socket_obj])
        else:
            var_dc = find_address(zakaz_obj, pod_zakaz, [rack_obj], False, True, False, [], [])
        form_socket = ChangeSockettInAddress(request.POST.copy(), [(socket_obj.id, socket_obj) for socket_obj in var_dc['socket_qs']], var_dc['socket_init'])
        if form_socket.is_valid():
            final_socket_init = Sockets.objects.get(id=form_socket.cleaned_data['socket'])

        if 5 == len(filter(lambda x: x.is_valid(), [form_unit, form_port, form_socket, form_switch, form_block_socket])):

            addr_obj = zakaz_obj.address_dc

            units_qs = Units.objects.filter(address=addr_obj)
            for unit_obj in units_qs:
                unit_obj.status_unit = 2
                if request.GET.has_key('edit'):
                    unit_obj.address.remove(addr_obj)
                unit_obj.save()

            ports_qs = Ports.objects.filter(adrress=addr_obj)
            for port_obj in ports_qs:
                port_obj.status_port = 2
                if request.GET.has_key('edit'):
                    port_obj.adrress.remove(addr_obj)
                port_obj.save()

            socket_qs = Sockets.objects.filter(adrress=addr_obj)
            for socket_obj in socket_qs:
                socket_obj.status_socket = 2
                if request.GET.has_key('edit'):
                    socket_obj.adrress.remove(addr_obj)
                socket_obj.save()

            if not request.GET.has_key('edit'):
                addr_obj.date_close = datetime.datetime.now()
                addr_obj.save()
                addr_obj = Address_dc(
                              name='%s - %s' % (zakaz_id, rack_obj.name),
                              rack=rack_obj,
                              date_create=datetime.datetime.now(),
                              )
                addr_obj.save()

            for unit_obj in final_spis_units:
                unit_obj.address.add(addr_obj)
                unit_obj.status_unit = 1
                unit_obj.save()
            final_port_init.adrress.add(addr_obj)
            final_port_init.status_port = 1
            final_port_init.save()
            final_socket_init.adrress.add(addr_obj)
            final_socket_init.status_socket = 1
            final_socket_init.save()
            pk_value = addr_obj._get_pk_val()
            return HttpResponse(
                '<!DOCTYPE html><html><head><title></title><script type="text/javascript" src="/static/admin/js/admin/RelatedObjectLookups.js"></script></head><body>'
                '<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");window.close</script></body></html>' % \
                # escape() calls force_text.
                (escape(pk_value), escapejs(addr_obj)))


    else:
        if not rack_qs:
            context['error'] = u'Нет подходящих стоек'
            return context
        var_dc = find_address(zakaz_obj, pod_zakaz, rack_qs, True, True, True)

        form_rack = ChangeRackInAddress(None, [(rack_obj.id, rack_obj) for rack_obj in rack_qs], var_dc['rack_init'])
        form_unit = ChangeUnitInAddress(None, [(unit_obj.id, unit_obj) for unit_obj in var_dc['units_qs']], [i.id for i in var_dc['spis_units']])
        form_switch = ChangeSwitchInAddress(None, [(switch_obj.id, switch_obj) for switch_obj in var_dc['switchs_qs']], var_dc['switch_init'])
        form_port = ChangePortInAddress(None, [(port_obj.id, port_obj) for port_obj in var_dc['ports_qs']], var_dc['port_init'])
        form_block_socket = ChangeBlockSocketInAddress(None, [(block_socket_obj.id, block_socket_obj) for block_socket_obj in var_dc['block_socket_qs']], var_dc['block_socket_init'])
        form_socket = ChangeSockettInAddress(None, [(socket_obj.id, socket_obj) for socket_obj in var_dc['socket_qs']], var_dc['socket_init'])
    context['form_rack'] = form_rack
    context['form_unit'] = form_unit
    context['form_switch'] = form_switch
    context['form_port'] = form_port
    context['form_block_socket'] = form_block_socket
    context['form_socket'] = form_socket
    return context


@staff_member_required
def send_message_about_server(request, zakaz_id):
    zakaz_obj = Zakazy.objects.get(id=zakaz_id)
    profile_obj = Profile.objects.get(billing_account_id=zakaz_obj.bill_account.id)
    current_domain = Site.objects.get_current().domain
    message = u'%s, информируем Вас о том, что Ваш заказ № %s готов для дальнейшей активации (Ваше оборудование установлено и настроено). Для подтверждения, перейдите в личный \
                кабинет и активируйте услугу.\nС уважением, %s' % (profile_obj.user.username, zakaz_id, current_domain)
    send_email(u"%s" % current_domain, message, settings.DEFAULT_FROM_EMAIL, [zakaz_obj.bill_account.email], profile_obj.user.id)
    return HttpResponse('ok')

@staff_member_required
def calculate_cost(request, zakaz_id):
    cost = cost_dc(zakaz_id)
    return HttpResponse(cost)

from django.contrib.auth.models import User
from data_centr.forms import ZakazyForm
from django.utils.html import format_html

#=========================================================================================
# для распечатки
@staff_member_required
@render_to("download_findoc_zakazy_admin.html")
def download_findoc_zakazy_admin(request, doc_number):
    context = {}
    # получим User
    try:
        zakaz_id = request.GET['zakaz_id']
    except:
        raise Http404
    zakazy_obj = get_object_or_404(Zakazy, id=zakaz_id)
    bill_account_id = zakazy_obj.bill_account.id
    user_profile_obj = Profile.objects.get(billing_account_id=bill_account_id)
    user_obj = user_profile_obj.user
    # url_after_sign
    url_after_sign_got = '/account/equipment_rent_list/zakaz/' + str(zakaz_id) + '/'
    # находим нужный FinDoc
    if (doc_number == '1'):
        findoc_obj = FinDoc.objects.get(slug='akt_priema_peredachi_oborudovaniya_2')
    if (doc_number == '2'):
            findoc_obj = FinDoc.objects.get(slug='dop_soglashenie_k_dogovoru_arenda_obor')
    now = datetime.datetime.now()
    # coздаем заявку
    doc = FinDocSignApplication(
                        assigned_at=now,
                        findoc=findoc_obj,
                        assigned_to=user_obj,
                        user_can_cancel=True,
                        service_for_billing="application_from_a_package")
    doc.pickle_params({"redirect_after_sign": url_after_sign_got})
    doc.save()
    app_text = doc.process_text(request=request, findocapp_id=doc.id)
    # удаляем заявку
    doc.delete()
    # здесь непосредственно передатеся текст договора из базы в html ку
    context["application_text"] = app_text
    # создаем документ для скачки
    context["title"] = unicode(findoc_obj)
    context["signed_findoc"] = findoc_obj
    text = app_text.encode('utf-8')
    f_name = transliterate(findoc_obj.name.encode('utf-8'))
    filename = "%s" % f_name + "-" + "-" + "%s" % findoc_obj.id
    out_f = open('%s.doc' % filename, 'w')
    out_f.write(text)
    out_f.close()
    gz1 = zipfile.ZipFile ('%s.zip' % filename, 'w', 8)
    gz1.write(out_f.name)
    gz1.close()
    shutil.move('%s.zip' % filename, 'media/doc/%s.zip' % filename)
    os.remove('%s.doc' % filename)
    if (doc_number == '1'):
        context["display"] = filename
        context["text"] = app_text
        context["zakaz_id"] = zakaz_id

        # посчитаем сколько заказов осталось не подписанными догооворами обратноой передачи обордуования
        # находим номер договра по которому созданы все заказы
        findoc_sign_zak = FinDocSignedZakazy.objects.get(zakaz_id=zakaz_id, fin_doc__findoc__slug='dogovor_arendi_serverov')
        # находим заказы относящиеся к этому договору
        zakazy_exist = FinDocSignedZakazy.objects.filter(fin_doc__id=findoc_sign_zak.fin_doc.id)
        # считаем их количество
        zakazy_exist_colvo = FinDocSignedZakazy.objects.filter(fin_doc__id=findoc_sign_zak.fin_doc.id).count()
        col = 0
        for i in zakazy_exist:
            try:
            # посчитаем все заказы у которых есть подписанный договор 'akt_priema_peredachi_oborudovaniya_2'
                find_zak_to_calc = FinDocSignedZakazy.objects.get(zakaz_id=i.zakaz_id, fin_doc__findoc__slug='akt_priema_peredachi_oborudovaniya_2')
                col = col + 1
            except FinDocSignedZakazy.DoesNotExist:
                pass
        col = zakazy_exist_colvo - col


        # если последний добовляем кнопку далее
        if col == 1:
            context['next_button'] = "<input type = 'button' id='sign-button' style = 'margin-left: 540px!important; position:absolute; background: #2186F0; color:white; border-radius: 5px;' value='" + u"Далее" + "' name='sign' onclick='fun_next()' style='display: inline-block'>"
    if (doc_number == '2'):
        download_button = "<a type = 'button' class='bt bt-blue2' href='/media/doc/" + str(filename) + ".zip' target='_blank'>" + u'СКАЧАТЬ' + " </a>"
        app_text = download_button + app_text
        return HttpResponse(app_text)
    return context
#================================================================================================
# для подписания договра
@staff_member_required
@render_to("sign_findoc_zakazy_admin.html")
def sign_findoc_zakazy_admin(request, param, doc_number):
    context = {}
    try:
        zakaz_id = request.GET['zakaz_id']
    except:
        raise Http404
    # получим номер заказа и user
    zakazy_obj = get_object_or_404(Zakazy, id=zakaz_id)
    bill_account_id = zakazy_obj.bill_account.id
    user_profile_obj = Profile.objects.get(billing_account_id=bill_account_id)
    user_obj = user_profile_obj.user
    # url_after_sign
    url_after_sign_got = '/account/equipment_rent_list/zakaz/' + str(zakaz_id) + '/'


    if (param == '2'):  # ПОДПИСЫВАЕМ ДОГОВОР
        if doc_number == '1':
            findoc_obj = get_object_or_404(FinDoc, slug='akt_priema_peredachi_oborudovaniya_2')
        if doc_number == '2':
            findoc_obj = get_object_or_404(FinDoc, slug='dop_soglashenie_k_dogovoru_arenda_obor')
        # объект User
        # user_obj = get_object_or_404(User, id=user_id)
        now = datetime.datetime.now()
        # создаем объект FinDocSignApplication(заявка)
        doc = FinDocSignApplication(
                        assigned_at=now,
                        findoc=FinDoc.objects.get(id=findoc_obj.id),
                        assigned_to=user_obj,
                        user_can_cancel=True,
                        service_for_billing="application_from_a_package")
        doc.pickle_params({"redirect_after_sign": url_after_sign_got})
        doc.save()
        app_text = doc.process_text(request=request, findocapp_id=doc.id)

        # подписываем документ берем admin slugs
        if doc.findoc.applied_to:
            applied_to_id = doc.findoc.applied_to.id
        else:
            applied_to_id = None
        list_params = doc.sign_with_params_data(user_obj, text=app_text, applied_to_id=applied_to_id)
        package_obj = Package_on_connection_of_service.objects.get(user=user_obj, activate=True, deactivate=False, activate_admin=False, url_after_sign=url_after_sign_got)
        slugs_list_temp = package_obj.slugs_document_admin
        slugs_list = slugs_list_temp.split(', ')
        del slugs_list[0]
        slugs_str = ', '.join(slugs_list)
        package_obj.slugs_document_admin = slugs_str
        findocsigned_obj = FinDocSigned.objects.get(id=list_params["findoc_id"])
        package_obj.findoc_sign.add(findocsigned_obj)
        package_obj.save()
        # сохраним подписаный догвор
        fin_doc_zakaz = FinDocSignedZakazy(
                                               fin_doc=findocsigned_obj,
                                               zakaz_id=zakaz_id,
                                               )
        fin_doc_zakaz.save()
#        print fin_doc_zakaz.id


        # если подписали 2-ой договор
        if doc_number == '2' and param == '2':
            package_obj.activate_admin = True
            package_obj.save()
            return HttpResponse('ok')


        # посчитаем сколько заказов осталось не подписанными догооворами обратноой передачи обордуования
        # находим номер договра по которому созданы все заказы
        findoc_sign_zak = FinDocSignedZakazy.objects.get(zakaz_id=zakaz_id, fin_doc__findoc__slug='dogovor_arendi_serverov')
        # находим заказы относящиеся к этому договору
        zakazy_exist = FinDocSignedZakazy.objects.filter(fin_doc__id=findoc_sign_zak.fin_doc.id)
        # считаем их количество
        zakazy_exist_colvo = FinDocSignedZakazy.objects.filter(fin_doc__id=findoc_sign_zak.fin_doc.id).count()
        col = 0
        for i in zakazy_exist:
            try:
                # посчитаем все заказы у которых есть подписанный договор 'akt_priema_peredachi_oborudovaniya_2'
                find_zak_to_calc = FinDocSignedZakazy.objects.get(zakaz_id=i.zakaz_id, fin_doc__findoc__slug='akt_priema_peredachi_oborudovaniya_2')
                col = col + 1
            except FinDocSignedZakazy.DoesNotExist:
                pass
        col = zakazy_exist_colvo - col


        if col == 0:  # если в пакете больше не осталось не подписанных договор обратной передачи то показываем договор рассторжения
            param = '1'
            doc_number = '2'
        else:
            package_obj.activate_admin = True
            package_obj.save()
            return HttpResponse('ok')


    if param == '1':  # ПОКАЗЫВАЕМ ДОГОВОР
        if doc_number == '1':
            findoc_obj = FinDoc.objects.get(slug='akt_priema_peredachi_oborudovaniya_2')
        if doc_number == '2':
            findoc_obj = FinDoc.objects.get(slug='dop_soglashenie_k_dogovoru_arenda_obor')
        now = datetime.datetime.now()
        # coздаем заявку
        doc = FinDocSignApplication(
                        assigned_at=now,
                        findoc=FinDoc.objects.get(id=findoc_obj.id),
                        assigned_to=user_obj,
                        user_can_cancel=True,
                        service_for_billing="application_from_a_package")
        doc.pickle_params({"redirect_after_sign": url_after_sign_got})
        doc.save()
        app_text = doc.process_text(request=request, findocapp_id=doc.id)
        # удаляем заявку
        doc.delete()
        # здесь непосредственно передатеся текст договора из базы в html ку
        if  doc_number == '1':
            context["application_text"] = app_text
            context["user_id"] = user_obj.id
            context["zakaz_id"] = zakaz_id
            context["zakaz_status"] = zakazy_obj.status_zakaza.id
            return context
        if  doc_number == '2':
            app_text_but = "<input type = 'button' id='sign-button' style = 'margin-left: 540px!important; position:absolute; background: #2186F0; color:white; border-radius: 5px;' value='" + u"Подписать" + "' name='sign' onclick='fun_sign2(" + str(user_obj.id) + "," + str(zakaz_id) + ")' style='display: inline-block'>"
            app_text = app_text + app_text_but
            return HttpResponse(app_text)

    return context

#================================================================================================
class ZakazyAdmin(admin.ModelAdmin):

    fieldsets = [
                 (_(u"General information"), {'fields':['id', 'main_zakaz', 'zakazy_custom_link', 'status_zakaza', 'section_type', 'service_type', 'tariff', 'equipment', 'electricity',
                                 'count_of_units', 'count_of_port', 'socket', 'count_ip', 'ip']}),
                 (_(u"Number information"), {'fields': ['ext_numbers', 'about']}),
                 (_(u"Date information"), {'fields': ['date_create', 'date_activation', 'date_deactivation']}),
                 (_(u"Connection address (for internet)"), {'fields': ['city', 'street', 'house'], 'classes': ['collapse']}),

#                 (_(u"Characteristics exposed by admin"), {'fields': ['port'], 'classes': ['collapse']}),
#                 (_(u"Characteristics inherent in servers"), {'fields': ['os','cpu','ram','hdd'], 'classes': ['collapse']}),
                 (_(u"Information on cost"), {'fields': ['cost', 'connection_cost', 'status_cost']}),
                 (_(u"Информация о размещении"), {'fields': ['server', 'server_assembly', 'address_dc']}),

                 ]
    list_display_links = ('id', 'list_display_custom_link')
    list_display = ('id', 'service_type', 'list_display_custom_link', 'date_create', 'date_activation', 'date_deactivation', 'status_zakaza', 'paid')
    list_select_related = True
    list_filter = ('status_zakaza', 'service_type', 'date_deactivation', 'date_activation')
    search_fields = ('bill_account__username', 'ext_numbers__number', 'ip__name')
    filter_horizontal = ('ip', 'ext_numbers',)
    readonly_fields = ('id', 'zakazy_custom_link', 'inet_login', 'inet_password')
    subAccounts = SubAccount.objects.all()

    def get_changelist(self, request, **kwargs):
        from changelist import SpecialForSearchingChangeList
        return SpecialForSearchingChangeList


    def inet_login(self, instance):
        subaccount = SubAccount.objects.filter(account=instance.bill_account)
        if subaccount:
            return subaccount[0].username
        return ''
    inet_login.short_description = u"Логин"
    inet_login.allow_tags = True

    def inet_password(self, instance):
        subaccount = SubAccount.objects.filter(account=instance.bill_account)
        if subaccount:
            return subaccount[0].password
        return ''
    inet_password.short_description = u"Пароль"
    inet_password.allow_tags = True

    def zakazy_custom_link(self, instance):
        zakazy_my = Zakazy.objects.get(pk=instance.id)
        user = User.objects.get(username=zakazy_my.bill_account)
        return format_html("<a href = '/admin/account/customeraccount/%s/'>%s</a>" % (user.id, user.username))
    zakazy_custom_link.short_description = u"Аккаунт"
    zakazy_custom_link.allow_tags = True
    def list_display_custom_link(self, instance):
        zakazy_my = Zakazy.objects.filter(pk=instance.id).select_related()
        if not len(zakazy_my):
            raise Http404()
        else:
            zakazy_my = zakazy_my[0]
        from account.admin import CustomerAccount
        user = User.objects.get(username=zakazy_my.bill_account)
        u = CustomerAccount.objects.get(username=zakazy_my.bill_account)
        bill_id = zakazy_my.bill_account.id
        zak = zakazy_my.id  # Номер id заказа

        return format_html("<a href = '/admin/account/customeraccount/%s/'>%s</a>" % (user.id, user.username))
        # short_description functions like a model field's verbose_name
    list_display_custom_link.short_description = u"Аккаунт"
    # in this example, we have used HTML tags in the output
    list_display_custom_link.allow_tags = True
    form = ZakazyForm
    # можно ещё оптимизировать, как будет время. хотя и так работает
    def paid(self, obj):
        now = datetime.datetime.now()
        payment_obj = Data_centr_payment.objects.filter((Q(year=now.year) & Q(month=now.month) & Q(bill_account=obj.bill_account) & Q(zakaz=obj.id) & Q(every_month=True)) \
                                                      | (Q(bill_account=obj.bill_account) & Q(zakaz=obj.id) & Q(every_month=False) & Q(payment_date=None)) \
                                                      | (Q(year=now.year) & Q(month=now.month) & Q(bill_account=obj.bill_account) & Q(zakaz=obj.id) & Q(every_month=False)))
        if len(payment_obj) == 1:
            if payment_obj[0].payment_date:
                return True
        return False
    paid.boolean = True

    def get_urls(self):
        urls = super(ZakazyAdmin, self).get_urls()




        my_urls = patterns("", ("^search_place_in_dc/(?P<zakaz_id>\d+)/$", search_place_in_dc), \
                           ("^search_rack/(?P<zakaz_id>\d+)/(?P<rack_id>\d+)/(?P<search>[-\w]+)/$", search_device), \
                           ("^send_message_about_server/(?P<zakaz_id>\d+)/$", send_message_about_server), \
                           ("^calculate_cost/(?P<zakaz_id>\d+)/$", calculate_cost),
                            # добавим url для скачивания и подписания договора

                           ("^download_findoc_zakazy_admin/(?P<doc_number>\d+)/$", download_findoc_zakazy_admin), \
                           ("^sign_findoc_zakazy_admin/(?P<param>\d+)/(?P<doc_number>\d+)/$", sign_findoc_zakazy_admin),)
        return my_urls + urls

    def get_form(self, request, obj=None, **kwargs):


        # form = ZakazyForm
        if  obj:
            if unicode(obj.service_type) == u'Абонентская плата за местный номер':
                # self.exclude = ('equipment', 'electricity',)
                self.fieldsets = [
                 (_(u"General information"), {'fields':['id', 'main_zakaz', 'zakazy_custom_link', 'status_zakaza', 'section_type', 'service_type', 'tariff',  # 'equipment', 'electricity', Закоментил 19.12.2013
                                  ]}),  # 'count_ip', 'ip''count_of_units', 'count_of_port', 'socket', Убрал
                 (_(u"Number information"), {'fields': ['ext_numbers', 'about']}),
                  (_(u"Date information"), {'fields': ['date_create', 'date_activation', 'date_deactivation', 'date_end_test_period']}),
                 # (_(u"Connection address (for internet)"), {'fields': ['city', 'street', 'house'], 'classes': ['collapse']}),
#                 (_(u"Characteristics exposed by admin"), {'fields': ['port'], 'classes': ['collapse']}),
#                 (_(u"Characteristics inherent in servers"), {'fields': ['os','cpu','ram','hdd'], 'classes': ['collapse']}),
                 (_(u"Information on cost"), {'fields': ['cost', 'connection_cost', 'status_cost']}),
                 # (_(u"Information on cost"), {'fields': ['server', 'server_assembly', 'address_dc']}),
                 ]

            elif unicode(obj.service_type) == u'Доступ в интернет':
                self.fieldsets = [
                 (_(u"General information"), {'fields':[ 'id', 'main_zakaz', 'zakazy_custom_link', 'status_zakaza', 'section_type', 'service_type', 'tariff', 'equipment',  # 'electricity', Закоментил 19.12.2013
                                  'count_ip', 'ip']}),  # 'count_of_units', 'count_of_port', 'socket', Убрал
                 (_(u"Number information"), {'fields': [ 'about']}),  # 'ext_numbers', Убрал
                  (_(u"Date information"), {'fields': ['date_create', 'date_activation', 'date_deactivation', 'date_end_test_period']}),
                 (_(u"Connection address (for internet)"), {'fields': ['city', 'street', 'house']}),
                 (_(u"Информация по интернет"), {'fields': [ 'inet_login', 'inet_password']}),  # Логин и пароль заказа
#                 (_(u"Characteristics exposed by admin"), {'fields': ['port'], 'classes': ['collapse']}),
#                 (_(u"Characteristics inherent in servers"), {'fields': ['os','cpu','ram','hdd'], 'classes': ['collapse']}),
                 (_(u"Information on cost"), {'fields': ['cost', 'connection_cost', 'status_cost']}),
                 # (_(u"Information on cost"), {'fields': ['server', 'server_assembly', 'address_dc']}),
                 ]

            elif unicode(obj.service_type) == u'Аренда сервера':
                self.fieldsets = [
                 (_(u"General information"), {'fields':[ 'id', 'main_zakaz', 'zakazy_custom_link', 'status_zakaza', 'section_type', 'service_type', 'tariff', 'equipment', 'electricity',  # 'electricity', Закоментил 19.12.2013
                                 'count_of_units', 'count_of_port', 'socket', 'count_ip', 'ip']}),
                 (_(u"Number information"), {'fields': [ 'about']}),  # 'ext_numbers',
                 (_(u"Date information"), {'fields': ['date_create', 'date_activation', 'date_deactivation', 'date_end_test_period']}),
                 # (_(u"Connection address (for internet)"), {'fields': ['city', 'street', 'house'], 'classes': ['collapse']}),
#                 (_(u"Characteristics exposed by admin"), {'fields': ['port'], 'classes': ['collapse']}),
#                 (_(u"Characteristics inherent in servers"), {'fields': ['os','cpu','ram','hdd'], 'classes': ['collapse']}),
                 (_(u"Information on cost"), {'fields': ['cost', 'connection_cost', 'status_cost']}),
                 (_(u"Информация о размещении"), {'fields': ['server', 'server_assembly', 'address_dc']}),
                 ]
            elif unicode(obj.service_type) == u'Аренда серверных стоек':
                self.fieldsets = [
                 (_(u"General information"), {'fields':[ 'id', 'main_zakaz', 'zakazy_custom_link', 'status_zakaza', 'section_type', 'service_type', 'tariff', 'electricity',  # 'equipment', Закоментил 19.12.2013
                                 'count_of_units', 'count_of_port', 'socket', 'count_ip', 'ip']}),
                 (_(u"Number information"), {'fields': [ 'about']}),  # 'ext_numbers',
                 (_(u"Date information"), {'fields': ['date_create', 'date_activation', 'date_deactivation', 'date_end_test_period']}),
                 # (_(u"Connection address (for internet)"), {'fields': ['city', 'street', 'house'], 'classes': ['collapse']}),
#                 (_(u"Characteristics exposed by admin"), {'fields': ['port'], 'classes': ['collapse']}),
#                 (_(u"Characteristics inherent in servers"), {'fields': ['os','cpu','ram','hdd'], 'classes': ['collapse']}),
                 (_(u"Information on cost"), {'fields': ['cost', 'connection_cost', 'status_cost']}),
                 (_(u"Информация о размещении"), {'fields': ['server', 'server_assembly', 'address_dc']}),
                 ]
            elif unicode(obj.service_type) == u'Размещение оборудования / colocation серверов':
                self.fieldsets = [
                 (_(u"General information"), {'fields':[ 'id', 'main_zakaz', 'zakazy_custom_link', 'status_zakaza', 'section_type', 'service_type', 'tariff', 'equipment', 'electricity',  # 'electricity', Закоментил 19.12.2013
                                 'count_of_units', 'count_of_port', 'socket', 'count_ip', 'ip']}),
#                  (_(u"Number information"), {'fields': [ 'about']}),  # 'ext_numbers',
                 (_(u"Date information"), {'fields': ['date_create', 'date_activation', 'date_deactivation', 'date_end_test_period']}),
                 # (_(u"Connection address (for internet)"), {'fields': ['city', 'street', 'house'], 'classes': ['collapse']}),
#                 (_(u"Characteristics exposed by admin"), {'fields': ['port'], 'classes': ['collapse']}),
#                 (_(u"Characteristics inherent in servers"), {'fields': ['os','cpu','ram','hdd'], 'classes': ['collapse']}),
                 (_(u"Information on cost"), {'fields': ['cost', 'connection_cost', 'status_cost']}),
                 (_(u"Информация о размещении"), {'fields': ['address_dc']}),  # 'server', 'server_assembly',
                 ]
            elif unicode(obj.service_type) == u'Запись разговора':
                self.fieldsets = [
                 (_(u"General information"), {'fields':[ 'id', 'main_zakaz', 'zakazy_custom_link', 'status_zakaza', 'section_type', 'service_type', 'tariff',  # 'equipment', 'electricity', Закоментил 19.12.2013
                                 ]}),  # 'count_of_units', 'count_of_port', 'socket', 'count_ip', 'ip'
                 (_(u"Number information"), {'fields': [ 'about']}),  # 'ext_numbers',
                 (_(u"Date information"), {'fields': ['date_create', 'date_activation', 'date_deactivation']}),
                 # (_(u"Connection address (for internet)"), {'fields': ['city', 'street', 'house'], 'classes': ['collapse']}),
#                 (_(u"Characteristics exposed by admin"), {'fields': ['port'], 'classes': ['collapse']}),
#                 (_(u"Characteristics inherent in servers"), {'fields': ['os','cpu','ram','hdd'], 'classes': ['collapse']}),
                 (_(u"Information on cost"), {'fields': ['cost', 'connection_cost', 'status_cost']}),
                 # (_(u"Information on cost"), {'fields': ['server', 'server_assembly', 'address_dc']}),
                 ]
            elif unicode(obj.service_type) == u'Аренда IP-адреса':
                self.fieldsets = [
                 (_(u"General information"), {'fields':[ 'id', 'main_zakaz', 'zakazy_custom_link', 'status_zakaza', 'section_type', 'service_type', 'tariff',  # 'equipment', 'electricity', Закоментил 19.12.2013
                             'count_ip', 'ip']}),  # 'count_of_units', 'count_of_port', 'socket',
                 (_(u"Number information"), {'fields': [ 'about']}),  # 'ext_numbers',
                 (_(u"Date information"), {'fields': ['date_create', 'date_activation', 'date_deactivation']}),
                 # (_(u"Connection address (for internet)"), {'fields': ['city', 'street', 'house'], 'classes': ['collapse']}),
#                 (_(u"Characteristics exposed by admin"), {'fields': ['port'], 'classes': ['collapse']}),
#                 (_(u"Characteristics inherent in servers"), {'fields': ['os','cpu','ram','hdd'], 'classes': ['collapse']}),
                 (_(u"Information on cost"), {'fields': ['cost', 'connection_cost', 'status_cost']}),
                 # (_(u"Information on cost"), {'fields': ['server', 'server_assembly', 'address_dc']}),
                 ]
            elif unicode(obj.service_type) == u'Аренда порта':
                self.fieldsets = [
                 (_(u"General information"), {'fields':[ 'id', 'main_zakaz', 'zakazy_custom_link', 'status_zakaza', 'section_type', 'service_type', 'tariff',  # 'equipment', 'electricity', Закоментил 19.12.2013
                                 ]}),  # 'count_of_units', 'count_of_port', 'socket', 'count_ip', 'ip'
                 (_(u"Number information"), {'fields': [ 'about']}),  # 'ext_numbers',
                 (_(u"Date information"), {'fields': ['date_create', 'date_activation', 'date_deactivation']}),
                 # (_(u"Connection address (for internet)"), {'fields': ['city', 'street', 'house'], 'classes': ['collapse']}),
#                 (_(u"Characteristics exposed by admin"), {'fields': ['port'], 'classes': ['collapse']}),
#                 (_(u"Characteristics inherent in servers"), {'fields': ['os','cpu','ram','hdd'], 'classes': ['collapse']}),
                 (_(u"Information on cost"), {'fields': ['cost', 'connection_cost', 'status_cost']}),
                 # (_(u"Information on cost"), {'fields': ['server', 'server_assembly', 'address_dc']}),
                 ]
            else:
                self.fieldsets = [
                 (_(u"General information"), {'fields':[ 'id', 'main_zakaz', 'zakazy_custom_link', 'status_zakaza', 'section_type', 'service_type', 'tariff', 'equipment', 'electricity',  # Закоментил 19.12.2013
                                 'count_of_units', 'count_of_port', 'socket', 'count_ip', 'ip']}),
                 (_(u"Number information"), {'fields': ['ext_numbers', 'about']}),
                 (_(u"Date information"), {'fields': ['date_create', 'date_activation', 'date_deactivation']}),
                 (_(u"Connection address (for internet)"), {'fields': ['city', 'street', 'house'], 'classes': ['collapse']}),
#                 (_(u"Characteristics exposed by admin"), {'fields': ['port'], 'classes': ['collapse']}),
#                 (_(u"Characteristics inherent in servers"), {'fields': ['os','cpu','ram','hdd'], 'classes': ['collapse']}),
                 (_(u"Information on cost"), {'fields': ['cost', 'connection_cost', 'status_cost']}),
                 (_(u"Информация о размещении"), {'fields': ['server', 'server_assembly', 'address_dc']}),
                 ]
        else:
            self.fieldsets = [
                 (_(u"General information"), {'fields':[ 'id', 'main_zakaz', 'status_zakaza', 'bill_account', 'section_type', 'service_type', 'tariff', 'equipment', 'electricity',  # Закоментил 19.12.2013
                                 'count_of_units', 'count_of_port', 'socket', 'count_ip', 'ip']}),
                 (_(u"Number information"), {'fields': ['ext_numbers', 'about']}),
                 (_(u"Date information"), {'fields': ['date_create', 'date_activation', 'date_deactivation']}),
                 (_(u"Connection address (for internet)"), {'fields': ['city', 'street', 'house'], 'classes': ['collapse']}),
#                 (_(u"Characteristics exposed by admin"), {'fields': ['port'], 'classes': ['collapse']}),
#                 (_(u"Characteristics inherent in servers"), {'fields': ['os','cpu','ram','hdd'], 'classes': ['collapse']}),
                 (_(u"Information on cost"), {'fields': ['cost', 'connection_cost', 'status_cost']}),
                 (_(u"Информация о размещении"), {'fields': ['server', 'server_assembly', 'address_dc']}),
                 ]

            # self.readonly_fields = ('id',)


        return super(ZakazyAdmin, self).get_form(request, obj=None, **kwargs)


    class Media:
        js = ['/media/js/zakazy_admin.js',
              '/media/js/jquery.min.js',
              '/media/js/chosen.jquery.js',
              '/media/js/chosen_select.js',
              '/media/js/add_page_zakazy_fieldsets.js']
        css = {'all':('/media/css/chosen.css',)}

#    def has_add_permission(self, request):
#        # Nobody is allowed to add
#        return False
#    def has_delete_permission(self, request, obj=None):
#        # Nobody is allowed to delete
#        return False
#    readonly_fields = ('bill_account', 'cpu', 'date_deactivation', 'electricity', 'equipment', 'hdd', 'id', 'ip',
#                        'os', 'port', 'ram', 'service_type', 'socket', 'status_zakaza', 'tariff', 'unit', 'zakaz_date')

class Status_and_all_Admin(admin.ModelAdmin):
    list_display = ('id', 'status', 'about')

class PriceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'cost')

class PriceConnectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'cost')

class Unit_and_all_Admin(admin.ModelAdmin):
    list_display = ('id', 'name', 'about', 'price_id')

class IPAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'section_type', 'status_ip', 'about', 'price_id')
    search_fields = ('name',)

class TariffAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price_id')
    filter_horizontal = ('for_person',)
    list_filter = ('section_type', 'service_type', 'for_person', 'archive',)

class ServiceTypeAdmin(admin.ModelAdmin):
    list_dislay = ('id', 'service_type', 'about')

class Unit_and_PortAdmin(admin.ModelAdmin):
    pass

class DedicatedAdmin(admin.ModelAdmin):
    list_display = ('id', 'tariff')

class StatusServersAdmin(admin.ModelAdmin):
    list_display = ('id', 'status')

class DataCentrPaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'year', 'month', 'bill_account', 'zakaz', 'cost', 'payment_date', 'every_month', \
                    'postdate', 'message_on_warning')
    search_fields = ('bill_account__username', 'zakaz__id')
    list_filter = ('year', 'month', 'every_month', 'postdate', 'payment_date')
    class Media:
        js = ['/media/js/jquery.min.js',
              '/media/js/chosen.jquery.js',
              '/media/js/chosen_select.js']
        css = {'all':('/media/css/chosen.css',)}

class PriorityServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'bill_account', 'zakaz_id', 'priority')
    search_fields = ('bill_account__username', 'zakaz_id')

    class Media:
        js = ['/media/js/jquery.min.js',
              '/media/js/chosen.jquery.js',
              '/media/js/chosen_select.js']
        css = {'all':('/media/css/chosen.css',)}

class ForAllAdmin(admin.ModelAdmin):
    pass

# class Return_payment_admin(admin.ModelAdmin):
#    list_display = [f.name for f in Return_payment._meta.fields]
#    list_filter = ('return_payment', 'send_mail',)

class RackAdmin(admin.ModelAdmin):
    list_display = ['name', 'depth', 'count_unit', 'is_active', 'switchs', 'blocks_of_socket']

    def switchs(self, obj):
        switch_qs = Switchs.objects.filter(rack=obj)
        switch_html = '<br />'.join(switch_obj.name for switch_obj in switch_qs)
        return mark_safe(switch_html)

    def blocks_of_socket(self, obj):
        block_of_socket_qs = Blocks_of_socket.objects.filter(rack=obj)
        block_of_socket_html = '<br />'.join(block_of_socket_obj.name for block_of_socket_obj in block_of_socket_qs)
        return mark_safe(block_of_socket_html)

class LimitConnectionServiceAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Limit_connection_service._meta.fields]
    search_fields = ('bill_acc__username',)
    list_filter = ('service_type',)


class AddressDcFullAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Address_dc_full._meta.fields]
    form = Address_dc_full_Admin_Form
#    readonly_fields = [f.name for f in Address_dc_full._meta.fields]

class ZakazyDeliveryAdmin(admin.ModelAdmin):
    list_display = ['id', 'zakazy_write_off', 'paid', 'delivery_status', 'zakazy_list_view']


from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
csrf_protect_m = method_decorator(csrf_protect)

def search_street(request, city_id):
    form_street_inet = StreetInternetForm(None, int(city_id))
    template = Template('{{ form_street_inet.as_table }}')
    context = Context({"form_street_inet": form_street_inet})
    return HttpResponse(template.render(context))

def search_house(request, street_id):
    form_house_inet = HouseInternetForm(None, int(street_id))
    template = Template('{{ form_house_inet.as_table }}')
    context = Context({"form_house_inet": form_house_inet})
    return HttpResponse(template.render(context))

def search_tariff(request, account_id):
    try:
        profile_obj = Profile.objects.get(billing_account_id=int(account_id))
        type_account = [1] if profile_obj.is_juridical else [2, 3]
        form_tariff_inet = TariffInternetForm(None, type_account)
    except Profile.DoesNotExist:
        form_tariff_inet = TariffInternetForm(None)
    template = Template('{{ form_tariff_inet.as_table }}')
    context = Context({"form_tariff_inet": form_tariff_inet})
    return HttpResponse(template.render(context))

class AddFreeInternetZakazAdmin(admin.ModelAdmin):
    actions = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def queryset(self, request):
        return []

    META = {}  # это нужно
    notifications = {}  # и это нужно

    @csrf_protect_m
    @render_to("admin/free_internet.html")
    def changelist_view(self, request, extra_context=None):
        context = {}
        context["request"] = request
        context["user"] = request.user
        context["title"] = u'Создать заказ на бесплатный интернет'
        context["csrf_token"] = request.COOKIES.get("csrftoken")
        context["app_label"] = Add_free_internet_zakaz._meta.app_label
        context["app_section"] = Add_free_internet_zakaz._meta.verbose_name_plural

        if request.POST:
            form_account_inet = AccountInternetForm(request.POST)
            if form_account_inet.is_valid():
                try:
                    profile_obj = Profile.objects.get(billing_account_id=request.POST['account'])
                    type_account = [1] if profile_obj.is_juridical else [2, 3]
                    form_tariff_inet = TariffInternetForm(request.POST, type_account)
                except Profile.DoesNotExist:
                    form_tariff_inet = TariffInternetForm(request.POST)
            else:
                form_tariff_inet = TariffInternetForm(request.POST)
            form_city_inet = CityInternetForm(request.POST)
            if form_city_inet.is_valid():
                form_street_inet = StreetInternetForm(request.POST, request.POST['city'])
            else:
                form_street_inet = StreetInternetForm(request.POST)
            if form_street_inet.is_valid():
                form_house_inet = HouseInternetForm(request.POST, request.POST['street'])
            else:
                form_house_inet = HouseInternetForm(request.POST)
            if 5 == len(filter(lambda x: x.is_valid(), [form_account_inet, form_tariff_inet, form_city_inet, form_street_inet, form_house_inet])):
                print 'valid'
                try:
                    profile_obj = Profile.objects.get(billing_account_id=request.POST['account'])
                    package_obj = Package_on_connection_of_service.objects.filter(user=profile_obj.user,
                                       activate=False,
                                       deactivate=False)
                    if not package_obj:
                        if not profile_obj.is_juridical:
                            create_package(profile_obj.user,
                                                    reverse('create_zakaz_free_inet'),
                                                    reverse('my_inet'),
                                                    "{'tariff_id':'%s',\
                                                      'city':'%s',\
                                                      'street':'%s',\
                                                      'house':'%s'}" \
                                                      % (request.POST['tariff'], request.POST['city'], \
                                                         request.POST['street'], request.POST['house']),
                                                    ['dogovor_oferta', 'akt_priemki_peredachi_vypoln_rabot_for_free_inet'])
                        else:
                            create_package(profile_obj.user,
                                                    reverse('create_zakaz_free_inet'),
                                                    reverse('my_inet'),
                                                    "{'tariff_id':'%s',\
                                                      'city':'%s',\
                                                      'street':'%s',\
                                                      'house':'%s'}" \
                                                      % (request.POST['tariff'], request.POST['city'], \
                                                         request.POST['street'], request.POST['house']),
                                                    ['telematic_data_centr', 'usluga_peredachi_dannyh_s_predoplatoi_internet', 'akt_priemki_peredachi_vypoln_rabot_for_free_inet'])
                        print 'vse good'
                        request.notifications.add(u'Пакет на подключение для пользователя %s успешно создан!' % (profile_obj.user.username), "success")
                    else:
                        request.notifications.add(u'У пользователя %s есть не закрытый пакет на подключение!' % (profile_obj.user.username), "error")
                except Profile.DoesNotExist:
                    bill_acc_obj = BillserviceAccount.objects.get(id=request.POST['account'])
                    request.notifications.add(u'У пользователя %s нет профиля!' % (bill_acc_obj.username), "error")
        else:
            form_account_inet = AccountInternetForm(None)
            form_tariff_inet = TariffInternetForm(None)
            form_city_inet = CityInternetForm(None)
            form_street_inet = StreetInternetForm(None)
            form_house_inet = HouseInternetForm(None)
        context['form_account_inet'] = form_account_inet
        context['form_tariff_inet'] = form_tariff_inet
        context['form_city_inet'] = form_city_inet
        context['form_street_inet'] = form_street_inet
        context['form_house_inet'] = form_house_inet
        return context


    def get_urls(self):
        urls = super(AddFreeInternetZakazAdmin, self).get_urls()
        my_urls = patterns("", ("^search_street/(?P<city_id>\d+)/$", search_street),
                           ("^search_house/(?P<street_id>\d+)/$", search_house),
                           ("^search_tariff/(?P<account_id>\d+)/$", search_tariff),)
        return my_urls + urls


def get_spis_rules(request, zakaz_id):
    print 'get_spis_rules'
    zakaz_obj = Zakazy.objects.get(id=zakaz_id)
    template = ''
    form_rule = ''
    if zakaz_obj.service_type.id in (3,):
        form_rule = RulesExternalNumber(None, zakaz_obj.bill_account)
    elif zakaz_obj.service_type.id in (8,):
        form_rule = RulesInetZakaz(None, zakaz_obj.bill_account)
    if form_rule:
        template = Template('''
                            {% for field in form_rule %}
                                {% if field.name in spec_fields %}
                                    {% if not field.field.show %}
                                        <tr style="display:none" id="tr_{{ field.name }}">
                                            <th style="float:right">{{ field.label }}</th>
                                            <td>{{ field.errors }}{{ field }}</td>
                                        </tr>
                                    {% else %}
                                        <tr style="display:table-row" id="tr_{{ field.name }}">
                                            <th style="float:right">{{ field.label }}</th>
                                            <td>{{ field.errors }}{{ field }}</td>
                                        </tr>
                                    {% endif %}
                                {% else %}
                                <tr>
                                    <th>{{ field.label }}</th>
                                    <td>{{ field.errors }}{{ field }}</td>
                                </tr>
                                {% endif %}
                            {% endfor %}
                            ''')
        context = Context({"form_rule": form_rule, "spec_fields":['groups', 'prolong_payment_period', 'count_day', 'to_pay']})
    if template:
        return HttpResponse(template.render(context))
    else:
        return HttpResponse('')

def test_zakaz(request, zakaz_obj):
    valid = False
    if zakaz_obj.service_type.id in (3,):
        ext_number_obj = zakaz_obj.ext_numbers.all()[0]
        profile_obj = Profile.objects.get(billing_account_id=zakaz_obj.bill_account.id)
        if not ext_number_obj.auth_user == profile_obj.user.id:
            request.notifications.add(u'Данный номер уже занят другим пользователем!', "error")
            return False, request
        else:
            valid = True
    if zakaz_obj.service_type.id in (8,):
        valid = True
    return valid, request

class RestoreZakazAdmin(admin.ModelAdmin):
    actions = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def queryset(self, request):
        return []

    META = {}
    notifications = {}

    @csrf_protect_m
    @render_to("admin/restore_zakaz.html")
    def changelist_view(self, request, extra_context=None):
        context = {}
        context["request"] = request
        context["user"] = request.user
        context["title"] = u'Восстановить заказ'
        context["csrf_token"] = request.COOKIES.get("csrftoken")
        context["app_label"] = Add_free_internet_zakaz._meta.app_label
        context["app_section"] = Add_free_internet_zakaz._meta.verbose_name_plural
        form_zakazy = ZakazForm(None)
        if not request.POST:
            if request.GET.has_key('zakaz_id'):
                form_zakazy = ZakazForm(None, request.GET['zakaz_id'])
                zakaz_obj = Zakazy.objects.get(id=request.GET['zakaz_id'])
                valid_zakaz, request = test_zakaz(request, zakaz_obj)
                if valid_zakaz:
                    if zakaz_obj.service_type.id in (3,):
                        form_rule = RulesExternalNumber(None, zakaz_obj.bill_account)
                        if form_rule.is_valid():
                            valid_rule = True
                        context['form_rule'] = form_rule
                    if zakaz_obj.service_type.id in (8,):
                        form_rule = RulesInetZakaz(None, zakaz_obj.bill_account)
                        if form_rule.is_valid():
                            valid_rule = True
                        context['form_rule'] = form_rule
        else:
            form_zakazy = ZakazForm(request.POST)
            if form_zakazy.is_valid():
                valid_rule = False
                zakaz_obj = Zakazy.objects.get(id=form_zakazy.cleaned_data['zakaz'])
                if zakaz_obj.service_type.id in (3,):
                    valid_zakaz, request = test_zakaz(request, zakaz_obj)
                    if valid_zakaz:
                        form_rule = RulesExternalNumber(request.POST, zakaz_obj.bill_account)
                        form_rule.zakaz_id = zakaz_obj.id
                        if form_rule.is_valid():
                            valid_rule = True
                        context['form_rule'] = form_rule
                if zakaz_obj.service_type.id in (8,):
                    valid_zakaz, request = test_zakaz(request, zakaz_obj)
                    if valid_zakaz:
                        form_rule = RulesInetZakaz(request.POST, zakaz_obj.bill_account)
                        form_rule.zakaz_id = zakaz_obj.id
                        if form_rule.is_valid():
                            valid_rule = True
                        context['form_rule'] = form_rule
                if valid_rule:
                    result = {}
                    for field in form_rule:
                        if not field.field.dependent and field.data:
                            result_rule = form_rule.call_method(field, zakaz_obj)
                            result['%s' % field.label] = result_rule
                    mess = u'<table>'
                    for item, value in result.items():
                        mess += u'<tr><td>%s</td><td>%s</td>' % (item, \
                                                                 '<img src="/static/admin/img/icon-no.gif" alt="False">' if not value \
                                                                 else '<img src="/static/admin/img/icon-yes.gif" alt="True">')
                    mess += u'</table>'
                    request.notifications.add(mess, "success")
        context['form_zakazy'] = form_zakazy
        context['spec_fields'] = ['groups', 'prolong_payment_period', 'count_day', 'to_pay']
        return context


    def get_urls(self):
        urls = super(RestoreZakazAdmin, self).get_urls()
        my_urls = patterns("", ("^spis_rules/(?P<zakaz_id>\d+)/$", get_spis_rules),)
        return my_urls + urls


# admin.site.register(Dedicated, DedicatedAdmin)
# admin.site.register(Status_servers, StatusServersAdmin)
admin.site.register(Zakazy, ZakazyAdmin)
admin.site.register(Status_zakaza, Status_and_all_Admin)
admin.site.register(Status_ip, Status_and_all_Admin)
admin.site.register(Service_type, ServiceTypeAdmin)
admin.site.register(Price, PriceAdmin)
admin.site.register(Price_connection, PriceConnectionAdmin)
admin.site.register(Tariff, TariffAdmin)
# admin.site.register(Port, Unit_and_PortAdmin)
admin.site.register(IP, IPAdmin)
admin.site.register(OS, Unit_and_all_Admin)
admin.site.register(CPU, ForAllAdmin)
admin.site.register(RAM, ForAllAdmin)
admin.site.register(HDD, ForAllAdmin)
admin.site.register(Data_centr_payment, DataCentrPaymentAdmin)
admin.site.register(Priority_of_services, PriorityServiceAdmin)
admin.site.register(Units, ForAllAdmin)
admin.site.register(Sockets, ForAllAdmin)
admin.site.register(Blocks_of_socket, ForAllAdmin)
admin.site.register(Ports, ForAllAdmin)
admin.site.register(Switchs, ForAllAdmin)
admin.site.register(Rack, RackAdmin)
admin.site.register(Address_dc, ForAllAdmin)
admin.site.register(Type_ram, ForAllAdmin)
admin.site.register(Motherboards, ForAllAdmin)
admin.site.register(Servers, ForAllAdmin)
admin.site.register(Slots_ram, ForAllAdmin)
admin.site.register(Slots_hdd, ForAllAdmin)
admin.site.register(Type_hdd, ForAllAdmin)
admin.site.register(Server_assembly, ForAllAdmin)
admin.site.register(Address_dc_full, AddressDcFullAdmin)
admin.site.register(Limit_connection_service, LimitConnectionServiceAdmin)
admin.site.register(Add_free_internet_zakaz, AddFreeInternetZakazAdmin)
admin.site.register(Restore_zakaz, RestoreZakazAdmin)

# admin.site.register(Return_payment, Return_payment_admin)
admin.site.register(ZakazyDelivery, ZakazyDeliveryAdmin)




