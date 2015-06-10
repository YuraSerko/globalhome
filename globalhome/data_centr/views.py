# -*- coding=utf-8 -*-
from django.shortcuts import HttpResponseRedirect, HttpResponse
from lib.decorators import render_to
from models import *
from django.conf import settings  # @UnusedImport
from django.core.mail import EmailMultiAlternatives
from account.models import Profile
from django.utils.translation import ugettext_lazy as _
import datetime
import calendar
from lib.decorators import login_required, limit_con_service
from findocs import get_signed
from findocs.models import FinDocSignedZakazy, Package_on_connection_of_service, Rules_of_drawing_up_documents, Check, Act, Invoice
from findocs.views import create_package
from django.core.urlresolvers import reverse
from content.views import perewod
from content.models import Section_type
from findocs import decorator_for_sign_applications
from findocs.models import FinDocTemplate, FinDocSigned
import log
from dateutil.relativedelta import relativedelta  # @UnresolvedImport
from django.contrib.auth.models import User
from django.db import connections, transaction
import os, sys
from billing.models import BillserviceAccount  # @UnresolvedImport
from django.db.models import Q
from django.db.models import Max, Min
from django.http import Http404
from page.views import panel_base_auth
from fs.models import Record_talk_activated_tariff
from lib.mail import send_email
from page.models import Send_mail
from internet.billing_models import SubAccount
from content.views import pannel_construct
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.db.models import Sum
from internet.models import Connection_address
import copy
from django.utils import simplejson
from account.forms import UserLoginForm2, UserRegistrationForm, UserLoginForm
from django.contrib.auth import login
from account.models import ActionRecord
from lib.cisco_api import Cisco
from settings import CISCO_PASSWORD
from data_centr.models import Ports
from django.contrib.sites.models import Site

dict_count_ip_for_service = {1:50, 2:6, 11:6}

# noinspection PyAugmentAssignment
def cost_dc(hidden_id=0, test_zayavka_obj=''):
    if test_zayavka_obj:
        zayavka = test_zayavka_obj
    else:
        zayavka = Zakazy.objects.get(id=hidden_id)
    cost_tariff = 0
    try:
        if zayavka.tariff and zayavka.status_cost in (1, 2):
            cost_tariff = cost_tariff + float(zayavka.tariff.price_id.cost)
    except:
        pass

#################################################################################################################

    cost_unit_temp = 0
    try:
        if zayavka.count_of_units is not None:
            price_unit = Price.objects.get(id=7)
            cost_unit_temp = (float(zayavka.count_of_units) - float(zayavka.tariff.unit)) * float(price_unit.cost)
    except:
        pass

    cost_port_temp = 0
    try:
        if zayavka.count_of_port is not None:
            price_port = Price.objects.get(id=5)
            cost_port_temp = (float(zayavka.count_of_port) - float(zayavka.tariff.port)) * float(price_port.cost)
    except:
        pass

    cost_socket = 0
    try:
        if zayavka.socket is not None:
            price_socket = Price.objects.get(id=6)
            cost_socket = (float(zayavka.socket) - float(zayavka.tariff.socket)) * float(price_socket.cost)
    except:
        pass


    cost_electricity = 0
    try:
        if zayavka.electricity is not None:
            if zayavka.service_type.id in (1,):
                price_electricity = Price.objects.get(id=123)
            else:
                price_electricity = Price.objects.get(id=4)
            cost_electricity = (float(zayavka.electricity) - float(zayavka.tariff.electricity)) / 100 * float(price_electricity.cost)
    except:
        pass


    cost_ip = 0
#    if zayavka.bill_account.id == 5616:
#        pass
#    else:
#        if zayavka.count_ip:
#            if zayavka.section_type == 2:
#                price_obj = Price.objects.get(id=3)
#                cost_ip = (zayavka.count_ip - zayavka.tariff.ip) * float(price_obj.cost)
#    try:
#        if zayavka.unit.all() != None:
#            for unit_obj in zayavka.unit.all():
#                cost_unit = cost_unit + float(unit_obj.price_id.cost)
#    except:
#        pass

    # тоже самое что и cost_unit
#    cost_port = 0
#    try:
#        if zayavka.port.all() != None:
#            for port_obj in zayavka.port.all():
#                cost_port = cost_port + float(port_obj.price_id.cost)
#    except:
#        pass

#    try:
#        if zayavka.count_ip:
#            if zayavka.date_activation:
#                if zayavka.section_type == 3:
#                    zakazy_queryset = Zakazy.objects.filter(main_zakaz = zayavka.id)
#                    for zakaz_obj in zakazy_queryset:
#                        if zakaz_obj.cost:
#                            cost_ip += zakaz_obj.cost
#                elif zayavka.section_type == 2:
#                    price_obj = Price.objects.get(id = 3)
#                    cost_ip = (zayavka.count_ip - zayavka.tariff.ip) * float(price_obj.cost)
#            else:
#                if zayavka.section_type == 3:
#                    tariff_obj = Tariff.objects.get(service_type__id = 10, for_person__id__in = [zayavka.tariff.for_person.all()[0].id])
#                    cost_ip = zayavka.count_ip * tariff_obj.price_id.cost
#    except:
#        pass

#    cost_ip = 0
#    try:
#        if zayavka.ip.all() is not None:
#            for ip_obj in zayavka.ip.all():
#                if ip_obj.status_ip.id == 3:
#                    cost_ip = cost_ip + float(ip_obj.price_id.cost)
#    except:
#        pass

    cost_temp = cost_unit_temp + cost_port_temp + cost_socket + cost_electricity + cost_tariff + cost_ip
    cost = '%.2f' % cost_temp
    return cost


def add_document_in_dict_for_send(dict_documents_for_send, user_id, type_document, spis_document):
    if dict_documents_for_send.has_key(user_id):
        dict_user_id = dict_documents_for_send[user_id]
        if dict_user_id.has_key(type_document):
            spis_document_temp = dict_user_id[type_document]
            spis_document = list(set(spis_document_temp) | set(spis_document))
        dict_user_id.update({type_document:spis_document})
        dict_documents_for_send[user_id] = dict_user_id
    else:
        dict_documents_for_send.update({user_id:{type_document:spis_document}})
    return dict_documents_for_send


def send_mail_check(dict_documents_for_send):
    print 'send_mail_check'
    # отправка счета на почту
    if not dict_documents_for_send:
        return
    try:
        current_domain = Site.objects.get_current().domain
        for user_id, dict_documents in dict_documents_for_send.items():
            profile_obj = Profile.objects.get(user__id=user_id)
            filename = []
            file_st = []
            for type_document, spis_document in dict_documents.items():
                i = 0
                for id_document in spis_document:
                    i += 1
                    document_obj = eval('%s.objects.get(id = %s)' % (type_document, id_document))
                    name = "%s_%s.doc" % (type_document.decode('utf-8'), i)
                    name_file = "%s_%s.doc" % (type_document.decode('utf-8'), id_document)
                    filename.append(name)
                    file_st.append(name_file)
                    out_f = open(name, 'w')
                    out_f.write(document_obj.text.encode("utf-8"))
                    out_f.close()
            if profile_obj.mail_for_document:
                send_to = profile_obj.mail_for_document
            else:
                send_to = profile_obj.user.email
            print 'cur site = %s' % settings.CURRENT_SITE
            print 'email = %s' % settings.DEFAULT_FROM_EMAIL
            msg = EmailMultiAlternatives(u"документы от www.%s" % current_domain, "", settings.DEFAULT_FROM_EMAIL, [send_to])
            for name in filename:
                msg.attach_file(name)
            msg.send()
            str = ", ".join([item for item in file_st])
            mail_obj = Send_mail(
            	subject=u"документы от www.%s" % current_domain,
            	message=" ",
            	date=datetime.datetime.now(),
            	user_id=user_id,
            	email=send_to,
            	spis_file=str,
            	status_mail=True)
            mail_obj.save()
        for user_id, dict_documents in dict_documents_for_send.items():
            for type_document, spis_document in dict_documents.items():
                for id_document in spis_document:
                    document_obj = eval('%s.objects.get(id = %s)' % (type_document, id_document))
                    document_obj.sent = True
                    document_obj.save()
    except Exception, e:
        log.add("Exception in send_mail: '%s'" % e)
        exc_type, exc_obj, exc_tb = sys.exc_info()  # @UnusedVariable
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        log.add("Exception in send_mail: file:%s line:%s" % (fname, exc_tb.tb_lineno))


#        user_id = cur2.fetchone()[0]
#        i = 1
#        for id in content_check_id:
#            text = ''
#            cur2.execute("SELECT text, type FROM content_check WHERE id=%s;", (id,))
#            content_temp = cur2.fetchall()[0]
#            text = content_temp[0]
#            type_doc = content_temp[1]
#            if type_doc in ('check', 'invoice', 'act'):
#                name = "%s.doc" % type_doc.decode('utf-8')
#            else:
#                name = u'document_%s.doc' % str(i)
#            filename.append(name)
#            out_f = open(name, 'w')
#            out_f.write(text.encode("utf-8"))
#            out_f.close()
#            i += 1
#        cur2.execute("SELECT email FROM auth_user WHERE id=%s;", (user_id,))
#        email = cur2.fetchone()[0]
#        msg = EmailMultiAlternatives(u"документы от www.globalhome.su", "", settings.DEFAULT_FROM_EMAIL, [email])
#        for name in filename:
#            msg.attach_file(name)
#        msg.send()
#        for id in content_check_id:
#            cur2.execute("UPDATE content_check SET sent = %s WHERE id = %s;", (True, id))
#            transaction.commit_unless_managed(settings.GLOBALHOME_DB2)
#    except Exception, e:
#        log.add("Exception in send_mail_check: '%s'" % e)
#        cur2.connection.rollback()
#    else:
#        cur2.connection.commit()


@render_to('physical_servers_%s.html' % settings.SITE_ID)
def dedicated(request):
    context = {}
    context['pannel'] = pannel_construct(request)
    context['pannel'] = pannel_construct(request)
    context['user'] = request.user
    context['current_view_name'] = 'account_data_centr'
    servers = []
    for server in Servers.objects.all():
        server_hdd = "<br />".join(i.__unicode__() for i in server.hdd.exclude(interface_id=3)) or '-'
        server_ssd = "<br />".join(i.__unicode__() for i in server.hdd.filter(interface_id=3)) or '-'
        server_ram = "<br />".join(i.__unicode__() for i in server.ram.all())
        cost = '%.2f' % (server.tariff.price_id.cost / 1.18)
        servers.append({'id':server.id, 'tariff':server.name, 'cpu':server.cpu, 'ram':server_ram,
                        'hdd': server_hdd, 'ssd': server_ssd, 'cost': cost})
    context['servers'] = servers
    if not servers:
        request.notifications.add(u'В настоящий момент нет свободных серверов. Приносим свои извинения за доставленные неудобства.', 'info')
    cpu_qs = CPU.objects.all()
    context['cpu_qs'] = cpu_qs
    context['count_cpu'] = len(cpu_qs) - 1
    context['user'] = request.user
    context['current_view_name'] = 'account_data_centr'
    servers = []
    for server in Servers.objects.filter(count_servers__gte=1):
        server_hdd = "<br />".join(i.__unicode__() for i in server.hdd.exclude(interface_id=3)) or '-'
        server_ssd = "<br />".join(i.__unicode__() for i in server.hdd.filter(interface_id=3)) or '-'
        server_ram = "<br />".join(i.__unicode__() for i in server.ram.all())
        cost = '%.2f' % (server.tariff.price_id.cost / 1.18)
        servers.append({'id':server.id, 'tariff':server.name, 'cpu':server.cpu, 'ram':server_ram,
                        'hdd': server_hdd, 'ssd': server_ssd, 'cost': cost})
    context['servers'] = servers
    if not servers:
        request.notifications.add(u'В настоящий момент нет свободных серверов. Приносим свои извинения за доставленные неудобства.', 'info')
    cpu_qs = CPU.objects.all()
    context['cpu_qs'] = cpu_qs
    context['count_cpu'] = len(cpu_qs) - 1
    return panel_base_auth(request, context)


@render_to('rack_%s.html' % settings.SITE_ID)
def rack(request):
    from data_centr.forms import AccountRackForm
    context = {}
    context['pannel'] = pannel_construct(request)
    AccountRackFormSet = formset_factory(AccountRackForm, extra=1)
    if request.POST.has_key('add'):
        rack_formset = AccountRackFormSet(request.POST)
        if rack_formset.is_valid():
            request_post = {}
            for key, value in request.POST.iteritems():
                request_post[key.encode("utf-8")] = value.encode("utf-8")
            if not request.user.is_anonymous():
                successfully_create = create_package(request.user,
                                        reverse('account_rack'),
                                        reverse('my_data_centr'),
                                        '%s' % request_post,
                                        ['telematic_data_centr', 'usluga_peredachi_dannyh_s_predoplatoi'])
                if not successfully_create:
                    raise Http404
                else:
                    return HttpResponseRedirect(reverse('account_rack'))
            else:
                context['data'] = simplejson.dumps(request_post)
                context['modal'] = True
        else:
            request.notifications.add(u'Пожалуйста, заполните все поля.', 'error')
    else:
        rack_formset = AccountRackFormSet()
    context['rack_formset'] = rack_formset
    context['initial_cost'] = '%.0f' % (Tariff.objects.get(id=1).price_id.cost / 1.18)
    context['user'] = request.user
    context['current_view_name'] = 'account_rack'
    return panel_base_auth(request, context)


from django.forms.formsets import formset_factory
@render_to('colocation_%s.html' % settings.SITE_ID)
def colocation(request):
    from data_centr.forms import AccountColocationForm
    context = {}
    context['pannel'] = pannel_construct(request)
    AccountColocationFormSet = formset_factory(AccountColocationForm, extra=1)
    if request.POST.has_key('add'):
        colocation_formset = AccountColocationFormSet(request.POST)
        if colocation_formset.is_valid():
            request_post = {}
            for key, value in request.POST.iteritems():
                request_post[key.encode("utf-8")] = value.encode("utf-8")
            if not request.user.is_anonymous():
                successfully_create = create_package(request.user,
                                        reverse('account_colocation'),
                                        reverse('my_data_centr'),
                                        '%s' % request_post,
                                        ['telematic_data_centr', 'usluga_peredachi_dannyh_s_predoplatoi'])
                if not successfully_create:
                    raise Http404
                else:
                    return HttpResponseRedirect(reverse('account_colocation'))
            else:
                context['data'] = simplejson.dumps(request_post)
                context['modal'] = True
        else:
            request.notifications.add(u'Пожалуйста, заполните все поля.', 'error')
    else:
        colocation_formset = AccountColocationFormSet()
    context['colocation_formset'] = colocation_formset
    context['initial_cost'] = '%.0f' % (Tariff.objects.get(id=2).price_id.cost / 1.18)
    context['user'] = request.user
    context['current_view_name'] = 'account_colocation'
    return panel_base_auth(request, context)


def step_change_method_auth(request):
    context = {}
    param = simplejson.loads((str(request.GET['data'])).strip('/'))
    context['data'] = simplejson.dumps(param)
    return render_to_response('step_change_method_auth.html', context)


def colocation_step_auth(request):
    from data_centr.forms import AccountColocationForm
    context = {}
    param = {}
    try:
        param = simplejson.loads((str(request.GET['data'])).strip('/'))
        context['data'] = simplejson.dumps(param)
        data = eval(context['data'])
        AccountColocationFormSet = formset_factory(AccountColocationForm, extra=1)
        colocation_formset = AccountColocationFormSet(data)
        if not colocation_formset.is_valid() or not request.GET.has_key('face'):
            return render_to_response("error.html", context)
        else:
            param['face'] = request.GET['face']
            if param['face'] == '0':
                form_reg = UserRegistrationForm()
                context['form_reg'] = form_reg
                return render_to_response("colocation_step_reg.html", context)
            elif param['face'] == '1':
                form_login = UserLoginForm()
                context['form_login'] = form_login
                return render_to_response("colocation_step_login.html", context)
    except:
        return render_to_response("error.html", context)


def rack_step_auth(request):
    from data_centr.forms import AccountRackForm
    context = {}
    param = {}
    try:
        param = simplejson.loads((str(request.GET['data'])).strip('/'))
        context['data'] = simplejson.dumps(param)
        data = eval(context['data'])
        AccountRackFormSet = formset_factory(AccountRackForm, extra=1)
        rack_formset = AccountRackFormSet(data)
        if not rack_formset.is_valid() or not request.GET.has_key('face'):
            return render_to_response("error.html", context)
        else:
            param['face'] = request.GET['face']
            if param['face'] == '0':
                form_reg = UserRegistrationForm()
                context['form_reg'] = form_reg
                return render_to_response("rack_step_reg.html", context)
            elif param['face'] == '1':
                form_login = UserLoginForm()
                context['form_login'] = form_login
                return render_to_response("rack_step_login.html", context)
    except:
        return render_to_response("error.html", context)


def rack_step_login(request):
    from data_centr.forms import AccountRackForm
    context = {}
    param = {}
    try:
        param = simplejson.loads((str(request.GET['data'])).strip('/'))
        context['data'] = simplejson.dumps(param)
        data = eval(context['data'])
        AccountRackFormSet = formset_factory(AccountRackForm, extra=1)
        rack_formset = AccountRackFormSet(data)
        if not rack_formset.is_valid():
            return render_to_response("error.html", context)

        form_login = UserLoginForm(request.GET)
        context['form_login'] = form_login
        if form_login.is_valid():
            user = form_login.user
            if user:
                if user.is_active:
                    login(request, user)
                    data['rack'] = 'rack'
                    successfully_create = create_package(request.user,
                                            reverse('account_rack'),
                                            reverse('my_data_centr'),
                                            '%s' % data,
                                            ['telematic_data_centr', 'usluga_peredachi_dannyh_s_predoplatoi'])
                    if not successfully_create:
                        raise Http404
                    return render_to_response("s8.html", context)
            if user is None:
                return render_to_response("rack_step_login.html", context)
        else:
            context['error_auth'] = True
            return render_to_response("rack_step_login.html", context)
    except Exception, e:
        print e
        return render_to_response("error.html", context)


def colocation_step_login(request):
    from data_centr.forms import AccountColocationForm
    context = {}
    param = {}
    try:
        param = simplejson.loads((str(request.GET['data'])).strip('/'))
        context['data'] = simplejson.dumps(param)
        data = eval(context['data'])
        AccountColocationFormSet = formset_factory(AccountColocationForm, extra=1)
        colocation_formset = AccountColocationFormSet(data)
        if not colocation_formset.is_valid():
            return render_to_response("error.html", context)

        form_login = UserLoginForm(request.GET)
        context['form_login'] = form_login
        if form_login.is_valid():
            user = form_login.user
            if user:
                if user.is_active:
                    login(request, user)
                    successfully_create = create_package(request.user,
                                            reverse('account_colocation'),
                                            reverse('my_data_centr'),
                                            '%s' % data,
                                            ['telematic_data_centr', 'usluga_peredachi_dannyh_s_predoplatoi'])
                    if not successfully_create:
                        raise Http404
                    return render_to_response("s8.html", context)
            if user is None:
                return render_to_response("colocation_step_login.html", context)
        else:
            context['error_auth'] = True
            return render_to_response("colocation_step_login.html", context)
    except:
        return render_to_response("error.html", context)


def colocation_step_reg(request):
    from data_centr.forms import AccountColocationForm
    context = {}
    param = {}
    try:
        param = simplejson.loads((str(request.GET['data'])).strip('/'))
        context['data'] = simplejson.dumps(param)
        data = eval(context['data'])
        AccountColocationFormSet = formset_factory(AccountColocationForm, extra=1)
        colocation_formset = AccountColocationFormSet(data)
        if not colocation_formset.is_valid():
            return render_to_response("error.html", context)

        form_reg = UserRegistrationForm(request.GET)
        context['form_reg'] = form_reg
        if form_reg.is_valid():
            user = form_reg.save()
            ActionRecord.registrations.create_inactive_user_key(
                new_user=user,
                row_password=form_reg.get_row_password(),
                send_email=True,
                )
            successfully_create = create_package(user,
                                    reverse('account_colocation'),
                                    reverse('my_data_centr'),
                                    '%s' % data,
                                    ['telematic_data_centr', 'usluga_peredachi_dannyh_s_predoplatoi'])
            if not successfully_create:
                raise Http404
            return render_to_response("s8_reg.html", context)
        else:
            context['error_auth'] = True
            return render_to_response("colocation_step_reg.html", context)
    except:
        return render_to_response("error.html", context)


def rack_step_reg(request):
    from data_centr.forms import AccountRackForm
    context = {}
    param = {}
    try:
        param = simplejson.loads((str(request.GET['data'])).strip('/'))
        context['data'] = simplejson.dumps(param)
        data = eval(context['data'])
        AccountRackFormSet = formset_factory(AccountRackForm, extra=1)
        rack_formset = AccountRackFormSet(data)
        if not rack_formset.is_valid():
            return render_to_response("error.html", context)

        form_reg = UserRegistrationForm(request.GET)
        context['form_reg'] = form_reg
        if form_reg.is_valid():
            user = form_reg.save()
            ActionRecord.registrations.create_inactive_user_key(
                new_user=user,
                row_password=form_reg.get_row_password(),
                send_email=True,
                )
            data['rack'] = 'rack'
            successfully_create = create_package(request.user,
                                    reverse('account_rack'),
                                    reverse('my_data_centr'),
                                    '%s' % data,
                                    ['telematic_data_centr', 'usluga_peredachi_dannyh_s_predoplatoi'])
            if not successfully_create:
                raise Http404
            return render_to_response("s8_reg.html", context)
        else:
            context['error_auth'] = True
            return render_to_response("rack_step_reg.html", context)
    except:
        return render_to_response("error.html", context)


def ajax_colocation_change_count_ip(request, count_ip):
    count_ip = int(count_ip)
    if ((count_ip < 0) or (count_ip > dict_count_ip_for_service[11])):
        raise Http404
    tariff_obj = Tariff.objects.get(id=41)
    colocation_cost = Tariff.objects.get(id=2)
    cost = colocation_cost.price_id.cost / 1.18
    cost += (int(count_ip) - 1) * tariff_obj.price_id.cost / 1.18
    cost = '%.2f' % cost
    print cost
    return HttpResponse(cost)


@render_to('vds.html')
def vds(request):
    context = {}
    return panel_base_auth(request, context)

def colocation_cost_zakaz(height_unit, size, inet_speed, count_ip, count_socket, count_electro):
    try:
        if height_unit in ('tower',):
            zayavka = Zakazy(
                     section_type=2,
                     service_type_id=2,
                     tariff_id=size,
                     count_ip=count_ip,
                     socket=count_socket,
                     electricity=count_electro,
                     )
        else:
            zayavka = Zakazy(
                     section_type=2,
                     service_type_id=2,
                     tariff_id=2,
                     count_of_units=height_unit,
                     count_ip=count_ip,
                     socket=count_socket,
                     electricity=count_electro,
                     )
        cost_main = float(cost_dc(0, zayavka)) / 1.18


        zakaz_port = Zakazy(
                 section_type=2,
                 service_type_id=12,
                 tariff_id=inet_speed,
                 count_ip=count_ip,
                 )
        cost_port = float(cost_dc(0, zakaz_port)) / 1.18

        cost_ip = 0
        for i, numb_ip in enumerate(range(1, int(count_ip) + 1)):  # @UnusedVariable
            status_cost = 3 if zayavka.tariff.ip >= numb_ip else 1
            zakaz_ip = Zakazy(
                section_type=2,
                status_cost=status_cost,
                service_type_id=10,
                tariff_id=41,
                count_ip=1,
                )
            cost_one_ip = float(cost_dc(0, zakaz_ip)) / 1.18
            cost_ip += cost_one_ip

        cost = '%.0f' % (cost_main + cost_port + cost_ip)
    except Exception, e:
        print e
        cost = u'ошибка'
    return cost


def rack_cost_zakaz(size_rack, inet_speed, count_ip, count_socket, count_electro):
    try:
        zayavka = Zakazy(
                 section_type=2,
                 service_type_id=1,
                 tariff_id=size_rack,
                 count_ip=count_ip,
                 socket=count_socket,
                 electricity=int(count_electro),
                 )
        cost_main = float(cost_dc(0, zayavka)) / 1.18

        zakaz_port = Zakazy(
                 section_type=2,
                 service_type_id=12,
                 tariff_id=inet_speed,
                 count_ip=count_ip,
                 )
        cost_port = float(cost_dc(0, zakaz_port)) / 1.18

        cost_ip = 0
        for i, numb_ip in enumerate(range(1, int(count_ip) + 1)):  # @UnusedVariable
            status_cost = 3 if zayavka.tariff.ip >= numb_ip else 1
            zakaz_ip = Zakazy(
                section_type=2,
                status_cost=status_cost,
                service_type_id=10,
                tariff_id=41,
                count_ip=1,
                )
            cost_one_ip = float(cost_dc(0, zakaz_ip)) / 1.18
            cost_ip += cost_one_ip

        cost = '%.0f' % (cost_main + cost_port + cost_ip)
    except Exception, e:
        print e
        cost = u'ошибка'
    return cost


def ajax_colocation_cost_zakaz(request):
    try:
        height_unit, size, inet_speed, count_ip, count_socket, count_electro = request.GET['height_unit'], \
        request.GET['size'], request.GET['inet_speed'], request.GET['count_ip'], \
        request.GET['count_socket'], request.GET['count_electro']
        cost = colocation_cost_zakaz(height_unit, size, inet_speed, count_ip, count_socket, count_electro)
    except Exception, e:
        print e
    return HttpResponse(cost)


def ajax_rack_cost_zakaz(request):
    try:
        size_rack, inet_speed, count_ip, count_socket, count_electro = request.GET['size_rack'], \
        request.GET['inet_speed'], request.GET['count_ip'], \
        request.GET['count_socket'], request.GET['count_electro']
        cost = rack_cost_zakaz(size_rack, inet_speed, count_ip, count_socket, count_electro)
    except Exception, e:
        print e
    return HttpResponse(cost)


@render_to('dedicated_step_zakaz.html')
def ajax_dedicated_step_zakaz(request, account, server_id):
    print '111111111111111'
    print 'ajax_step_zakaz'
    print account
    print server_id
    context = {}
    server_obj = get_object_or_404(Servers, id=server_id)
    server_hdd = "<br />".join(i.__unicode__() for i in server_obj.hdd.exclude(interface_id=3)) or '-'
    server_ssd = "<br />".join(i.__unicode__() for i in server_obj.hdd.filter(interface_id=3)) or '-'
    server_ram = "<br />".join(i.__unicode__() for i in server_obj.ram.all())
    cost = '%.2f' % (server_obj.tariff.price_id.cost / 1.18)
    server = {'id':server_obj.id, 'tariff':server_obj.name, 'cpu':server_obj.cpu, 'ram':server_ram,
              'hdd': server_hdd, 'ssd': server_ssd, 'cost': cost}
    context['server'] = server
    context['conf'] = False

    tariff_obj = Tariff.objects.get(id=41)
    range_ip, range_speed = [], []
    try:
        for i in range(1, dict_count_ip_for_service[11] + 1):
            if i <= server_obj.tariff.ip:
                range_ip.append({'count':i, 'count_with_cost': u'%s (беспл.)' % i})
            else:
                range_ip.append({'count':i, 'count_with_cost': u'%s (%s руб.*)' % (i, tariff_obj.price_id.cost * (i - server_obj.tariff.ip) / 1.18)})
    except Exception, e:
        print "e=%s" % str(e).encode('utf-8')
        exc_type, exc_obj, exc_tb = sys.exc_info()  # @UnusedVariable
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print "Exception in priority_of_services: file:%s line:%s" % (fname, exc_tb.tb_lineno)
    tariff_queryset = Tariff.objects.filter(service_type=12, garant=False)
    for tariff in tariff_queryset:
        cost = u'%s руб.*' % (tariff.price_id.cost / 1.18) if tariff.price_id.cost > 0 else u'беспл.'
        range_speed.append({'tariff_id':u'%s' % (tariff.id), 'cost':u'%s Мбит/сек (%s)' % (tariff.speed_inet, cost)})
    context['range_ip'] = range_ip
    context['range_speed'] = range_speed
    context['permitted_count_ip'] = dict_count_ip_for_service[11]
    context['account'] = eval(account)
    context['user'] = request.user.username
    return context


def ajax_colocation_change_form_factor(request, type_ff):
    print 'ajax_colocation_change_form_factor'
    choice_unit_id = []
    choice_unit_value = []
    spis_unit = [('1', u'до 60'), ('2', u'до 80'), ('3', u'до 100')]
    if type_ff in ('tower'):
        tariff_qs = Tariff.objects.filter(section_type=2, service_type__id=2, tower_casing=True)
        for tariff_obj in tariff_qs:
            choice_unit_id.append('%s' % tariff_obj.id)
            choice_unit_value.append('%sx%sx%s' % (tariff_obj.width, tariff_obj.height, tariff_obj.depth,))
    elif type_ff in ('unit'):
        for i in spis_unit:
            choice_unit_id.append('%s' % i[0])
            choice_unit_value.append('%s' % i[1])
    string_choice_unit_id = ", ".join(choice_unit_id)
    string_choice_unit_value = ", ".join(choice_unit_value)
    return HttpResponse(u'%s_%s' % (string_choice_unit_id, string_choice_unit_value))


def ajax_rack_change_ip(request, size_rack):
    print 'ajax_rack_change_ip'
    max_ip = 50
    max_unit = 42
    choice_ip = []
    tariff_rack = Tariff.objects.get(id=size_rack)
    for i in range(tariff_rack.ip, max_ip / (max_unit / int(tariff_rack.unit)) + 1):
        choice_ip.append('%s' % i)
    string_choice_ip = ", ".join(choice_ip)
    return HttpResponse(u'%s_%s' % (string_choice_ip, string_choice_ip))


def ajax_rack_change_electro(request, size_rack):
    print 'ajax_rack_change_electro'
    max_electro = 15000
    max_unit = 42
    choice_electro_id = []
    choice_electro_value = []
    tariff_rack = Tariff.objects.get(id=size_rack)
    step = 1000 if int(tariff_rack.unit) in (42,) else 500
    for i in range(int(tariff_rack.electricity), max_electro / (max_unit / int(tariff_rack.unit)) + step, step):
        choice_electro_id.append('%s' % i)
        choice_electro_value.append(u'%s Вт' % i)
    string_choice_electro_id = ", ".join(choice_electro_id)
    string_choice_electro_value = ", ".join(choice_electro_value)
    return HttpResponse(u'%s_%s' % (string_choice_electro_id, string_choice_electro_value))


def ajax_rack_change_socket(request, size_rack):
    print 'ajax_rack_change_socket'
    max_socket = 80
    max_unit = 42
    choice_socket = []
    tariff_rack = Tariff.objects.get(id=size_rack)
    for i in range(int(tariff_rack.socket), max_socket / (max_unit / int(tariff_rack.unit)) + 1):
        choice_socket.append('%s' % i)
    string_choice_socket = ", ".join(choice_socket)
    return HttpResponse(u'%s_%s' % (string_choice_socket, string_choice_socket))


def ajax_change_type_inet(request, type_inet):
    print 'ajax_change_type_inet'
    def get_id_with_speed(garant):
        spis_id = []
        spis_speed = []
        print 'garant = %s' % garant
        tariff_queryset = Tariff.objects.filter(service_type__id=12, garant=garant).order_by('speed_inet')
        print 'len = %s' % tariff_queryset
        for tariff in tariff_queryset:
            print '1'
            cost = u'%s р.*' % (tariff.price_id.cost / 1.18) if tariff.price_id.cost > 0 else u'беспл.'
            spis_id.append(str(tariff.id))
            spis_speed.append(u'%s Мбит/с (%s)' % (tariff.speed_inet, cost))
            string_spis_id = ", ".join(spis_id)
            string_spis_speed = ", ".join(spis_speed)
        return string_spis_id, string_spis_speed
    if type_inet in ('garant',):
        string_spis_id, string_spis_speed = get_id_with_speed(True)
    if type_inet in ('not_garant',):
        string_spis_id, string_spis_speed = get_id_with_speed(False)
    return HttpResponse(u'%s_%s' % (string_spis_id, string_spis_speed))


def cost_calculation(server_id, count_ip, speed_inet_id):
    server_obj = get_object_or_404(Servers, id=server_id)
    tariff_ip_obj = Tariff.objects.get(id=41)
    cost = server_obj.tariff.price_id.cost / 1.18
    cost += (int(count_ip) - 1) * tariff_ip_obj.price_id.cost / 1.18
    tariff_speed_obj = Tariff.objects.get(id=speed_inet_id)
    cost += tariff_speed_obj.price_id.cost / 1.18
    cost = '%.2f' % cost
    return cost


def ajax_dedicated_cost_calculation(request, server_id):
    print 'ajax_dedicated_cost_calculation'
    server_id = int(server_id)
    server_obj = get_object_or_404(Servers, id=server_id)  # @UnusedVariable
    try:
        count_ip, speed_inet_id = int(request.GET['count_ip']), int(request.GET['speed_inet'])
    except:
        raise Http404
    if ((count_ip < 0) or (count_ip > dict_count_ip_for_service[11])):
        raise Http404
    cost = cost_calculation(server_id, count_ip, speed_inet_id)
    print 'cost = %s' % cost
    return HttpResponse(cost)


@render_to('dedicated_step_zakaz.html')
def ajax_dedicated_step_conf(request, account):
    context = {}
    print 'get = %s' % request.GET
    try:
        cpu_id, count_ram, count_hdd, count_ssd = request.GET['cpu_id'], request.GET['count_ram'], request.GET['count_hdd'], request.GET['count_ssd']
    except:
        raise Http404
    cpu = get_object_or_404(CPU, id=cpu_id)
    server = {'tariff': u'Конфигурация', 'cpu':cpu, 'ram': u'%s Мб' % count_ram,
              'hdd': u'%s Гб' % count_hdd, 'ssd': u'%s Гб' % count_ssd, 'cost': u'100'}
    context['server'] = server
    context['cpu_id'], context['ram'], context['hdd'], context['ssd'] = cpu_id, count_ram, count_hdd, count_ssd
    context['conf'] = True
    return context


def ajax_dedicated_step_auth(request, account):
    print 'ajax_dedicated_step_auth'
    param, context = {}, {}
    try:
        account = eval(account)
        if request.GET.has_key('server_id'):
            server_id = int(request.GET['server_id'])
            get_object_or_404(Servers, id=server_id)
            count_ip, speed_inet_id = int(request.GET['count_ip']), int(request.GET['speed_inet'])
        else:
            cpu_id = int(request.GET['cpu_id'])
            get_object_or_404(CPU, id=cpu_id)
            count_ram = int(request.GET['count_ram'])
            count_hdd = int(request.GET['count_hdd'])
            count_ssd = int(request.GET['count_ssd'])
#        count_ip = int(request.GET['count_ip'])
    except:
        raise Http404
    print 'pered try count_ip = %s' % count_ip
    if ((count_ip < 0) or (count_ip > dict_count_ip_for_service[11])):
        raise Http404
    if request.GET.has_key('server_id'):
        param['server_id'], param['count_ip'], param['speed_inet_id'] = server_id, count_ip, speed_inet_id
    else:
        param['cpu_id'], param['count_ram'], param['count_hdd'], param['count_ssd'] = cpu_id, count_ram, count_hdd, count_ssd
#    param['count_ip'] = count_ip
    context['data'] = simplejson.dumps(param)
    if not account:
        param['face'] = request.GET['face']
        print 'face = %s' % param['face']
        context['server_id'] = server_id
        if param['face'] == '0':
            form_reg = UserRegistrationForm()
            context['form_reg'] = form_reg
            return render_to_response("step_reg.html", context)
        elif param['face'] == '1':
            form_login = UserLoginForm2()
            context['form_login'] = form_login
            return render_to_response("step_login.html", context)
        # если пользователь уже в системе
        elif param['face'] == '2':
            successfully_create = create_package(request.user,
                                reverse('add_dedicated_final'),
                                reverse('my_data_centr'),
                                '%s' % param,
                                ['telematic_data_centr', 'dogovor_arendi_serverov', 'akt_priemki_oborudovania', 'usluga_peredachi_dannyh_s_predoplatoi'])
            if not successfully_create:
                print 'not succesfully'
                raise Http404
            return render_to_response("s8.html", context)
    else:
        successfully_create = create_package(request.user,
                                reverse('add_dedicated_final'),
                                reverse('my_data_centr'),
                                '%s' % param,
                                ['telematic_data_centr', 'dogovor_arendi_serverov', 'akt_priemki_oborudovania', 'usluga_peredachi_dannyh_s_predoplatoi'])
        if not successfully_create:
            print 'not succesfully'
            raise Http404
        return HttpResponseRedirect(reverse('add_dedicated_final'))


def ajax_dedicated_step_login(request):
    print 'ajax_dedicated_step_login'
    context = {}
    errors = {}
    form_login = UserLoginForm2(request.GET)
    context['form_login'] = form_login
    print request.GET
    try:
        param = simplejson.loads((str(request.GET['data'])).strip('/'))
    except Exception, e:
        raise Http404
    context['data'] = simplejson.dumps(param)
    context['server_id'] = param['server_id']
    try:
        if form_login.is_valid():
            user = form_login.user
            if user:
                if user.is_active:
                    login(request, user)
                    successfully_create = create_package(request.user,
                                            reverse('add_dedicated_final'),
                                            reverse('my_data_centr'),
                                            '%s' % param,
                                            ['telematic_data_centr', 'dogovor_arendi_serverov', 'akt_priemki_oborudovania', 'usluga_peredachi_dannyh_s_predoplatoi'])
                    if not successfully_create:
                        print 'not succesfully'
                        raise Http404
                    return render_to_response("s8.html", context)
            if user is None:
                errors['error_auth'] = True
                context['errors'] = errors
                return render_to_response("step_login.html", context)
        else:
            errors['error_auth'] = True
            context['errors'] = errors
            return render_to_response("step_login.html", context)
    except Exception, e:
        print e
    else:
        return render_to_response("step_login.html", context)


def ajax_dedicated_step_registration(request):
    print 'ajax_dedicated_step_registration'
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
    context['server_id'] = param['server_id']
    if form_reg.is_valid():
        user = form_reg.save()
        ActionRecord.registrations.create_inactive_user_key(
            new_user=user,
            row_password=form_reg.get_row_password(),
            send_email=True,
            )
        successfully_create = create_package(user,
                                reverse('add_dedicated_final'),
                                reverse('my_data_centr'),
                                '%s' % param,
                                ['telematic_data_centr', 'dogovor_arendi_serverov', 'akt_priemki_oborudovania', 'usluga_peredachi_dannyh_s_predoplatoi'])
        if not successfully_create:
            print 'not succesfully'
            raise Http404
        return render_to_response("s8_reg.html", context)
    else:
        errors['error_auth'] = True
        context['errors'] = errors
        return render_to_response("step_reg.html", context)


@login_required
@decorator_for_sign_applications()
def add_dedicated_final(request):
    print 'add_dedicated_final'
    user_obj = request.user
    profile_obj = Profile.objects.get(user=user_obj)
    bill_acc = BillserviceAccount.objects.get(id=profile_obj.billing_account_id)
    try:
        package_obj = Package_on_connection_of_service.objects.get(user=user_obj, activate=False, deactivate=False)
    except:
        raise Http404
    param = eval(package_obj.data)
    if not param:
        return HttpResponseRedirect(reverse("my_data_centr"))
    if param.has_key('server_id') and param.has_key('count_ip') and param.has_key('speed_inet_id'):
        server = Servers.objects.get(id=int(param['server_id']))
        zakaz = Zakazy(
                 bill_account=bill_acc,
                 section_type=2,
                 status_zakaza_id=1,
                 service_type_id=11,
                 tariff=server.tariff,
                 date_create=datetime.datetime.now(),
                 count_ip=param['count_ip'],
                 server=server,
                 )
        zakaz.save()
        cost = float(cost_dc(zakaz.id))
        zakaz.cost = '%.2f' % cost
        zakaz.save()

        tariff_port = Tariff.objects.get(id=int(param['speed_inet_id']))
        status_cost = 3 if tariff_port.price_id.cost == 0 else 2
        zakaz_port = Zakazy(
                 main_zakaz=zakaz.id,
                 bill_account=bill_acc,
                 section_type=2,
                 status_zakaza_id=1,
                 service_type_id=12,  #аренда порта
                 tariff=tariff_port,
                 date_create=datetime.datetime.now(),
                 count_ip=param['count_ip'],
                 status_cost=status_cost,
                 )
        zakaz_port.save()
        cost = float(cost_dc(zakaz_port.id))
        zakaz_port.cost = '%.2f' % cost
        zakaz_port.save()

    elif param.has_key('cpu_id') and param.has_key('count_ram') and param.has_key('count_hdd') and param.has_key('count_ssd'):
        cpu_obj = CPU.objects.get(id=int(param['cpu_id']))
        server_assembly = Server_assembly(
                                          cpu=cpu_obj,
                                          ram=int(param['count_ram']),
                                          hdd=int(param['count_hdd']),
                                          ssd=int(param['count_ssd']),
                                          )
        server_assembly.save()
        zakaz = Zakazy(
                 bill_account=bill_acc,
                 section_type=2,
                 status_zakaza_id=1,
                 service_type_id=11,
                 date_create=datetime.datetime.now(),
                 count_ip=param['count_ip'],
                 server_assembly=server_assembly,
                )
        zakaz.save()
    package_obj.activate = True
    package_obj.save()

    findocsign_queryset = package_obj.findoc_sign.filter(findoc__slug='usluga_peredachi_dannyh_s_predoplatoi')
    if findocsign_queryset:
        findocsign_obj = findocsign_queryset[0]
    fin_doc_zakaz = FinDocSignedZakazy(
                                       fin_doc=findocsign_obj,
                                       zakaz_id=zakaz.id,
                                       )
    fin_doc_zakaz.save()
    findocsign_queryset = package_obj.findoc_sign.filter(findoc__slug='telematic_data_centr')
    if not findocsign_queryset:
        findocsign_obj = get_signed(profile_obj.user, "telematic_data_centr")
    else:
        findocsign_obj = findocsign_queryset[0]
    fin_doc_zakaz = FinDocSignedZakazy(
                                       fin_doc=findocsign_obj,
                                       zakaz_id=zakaz.id,
                                       )
    fin_doc_zakaz.save()
    findocsign_queryset = package_obj.findoc_sign.filter(findoc__slug='dogovor_arendi_serverov')
    if findocsign_queryset:
        findocsign_obj = findocsign_queryset[0]
    fin_doc_zakaz = FinDocSignedZakazy(
                                       fin_doc=findocsign_obj,
                                       zakaz_id=zakaz.id,
                                       )
    fin_doc_zakaz.save()
    findocsign_queryset = package_obj.findoc_sign.filter(findoc__slug='akt_priemki_oborudovania')
    if findocsign_queryset:
        findocsign_obj = findocsign_queryset[0]
    fin_doc_zakaz = FinDocSignedZakazy(
                                       fin_doc=findocsign_obj,
                                       zakaz_id=zakaz.id,
                                       )
    fin_doc_zakaz.save()

#    rule_obj = Rules_of_drawing_up_documents.objects.get(id=1)
#    spis_rules = Check.group_rules(profile_obj, [rule_obj.id], 'type_check', zakaz.id)
#    content_check_id = Check.create_check(request.user, spis_rules, False, [zakaz.id])
#    dict_documents_for_send = add_document_in_dict_for_send({}, request.user.id, 'Check', content_check_id)
#    send_mail_check(dict_documents_for_send)
    #send_email(u"Заказ на аренду сервера", u"Заказ на аренду сервера №%s" % zakaz.id, settings.DEFAULT_FROM_EMAIL, ["Zz1n@globalhome.su"], request.user.id)
    request.notifications.add(_(u'Заявка на услугу "Аренда сервера" успешно сформирована!'), "success")
    return HttpResponseRedirect(reverse('my_data_centr'))


def dedicated_zakaz(request):
    user_obj = User.objects.get(username=request.user.username)
    message = u'Тип услуги: Аренда выделенного физического сервера' + u'\nТариф: ' + request.POST["tarif"] + u'\nСтоимость услуги: ' + request.POST["cost"] + u'\nИмя юзера: ' + user_obj.username
    send_email("Аренда выделенного физического сервера", "%s" % message, settings.DEFAULT_FROM_EMAIL, ["sales@globalhome.su"], request.user.id)
    unit = request.POST["unit"]
    i = 0
    for symbol in unit:
        print (symbol)
        if symbol in '0123456789':
            i += 1
    unit = unit[:i]
    electro = request.POST["electro"]
    i = 0
    for symbol in electro:
        print (symbol)
        if symbol in '0123456789':
            i += 1
    electro = electro[:i]
    cost = request.POST["cost"]
    i = 0
    for symbol in cost:
        print (symbol)
        if symbol in '0123456789':
            i += 1
    cost = cost[:i]
    cost = str(cost) + " руб."
    zayvki = Zayavki(
                     tip_uslugi=u'Аренда выделенного физического сервера',
                     tarif=request.POST["tarif"],
                     cost=cost,
                     unit=unit,
                     port="1",
                     kol_vo_ip="1",
                     rozetka=None,
                     electro=electro,
                     os=None,
                     cpu=None,
                     ram=None,
                     hdd=None,
                     user_id=user_obj.id,
                     user_name=user_obj.username,
                     zayvka_date=datetime.datetime.now(),
                     )
    zayvki.save()
    return HttpResponseRedirect("/account/demands_dc/")

def main_rack_zakaz(request):
    message = u'Тип услуги: Аренда серверных стоек' + u'\nСтоимость услуги: 35000 руб.' + u'\nФИО заказчика: ' + request.POST["surname"] + u' ' + request.POST["name"] + u' ' + request.POST["patronymic"] + u'\nemail: ' + request.POST["email"] + u'\nКонтактный номер телефона: ' + u'+' + request.POST["phoneNumber"]
    send_email("Аренда серверных стоек", "%s" % message, settings.DEFAULT_FROM_EMAIL, ["sales@globalhome.su"], request.user.id)
    return HttpResponseRedirect('%s#message_send' % reverse('rack'))

def main_colocation_zakaz(request):
    message = u'Тип услуги: Размещение оборудования / colocation серверов' + u'\nСтоимость услуги: ' + request.POST["hidden_cost"] + u'\nФИО заказчика: ' + request.POST["surname"] + u' ' + request.POST["name"] + u' ' + request.POST["patronymic"] + u'\nemail: ' + request.POST["email"] + u'\nКонтактный номер телефона: ' + u'+' + request.POST["phoneNumber"]
    send_email("Размещение оборудования / colocation серверов", "%s" % message, settings.DEFAULT_FROM_EMAIL, ["sales@globalhome.su"], request.user.id)
    return HttpResponseRedirect('%s#message_send' % reverse('colocation'))

@login_required
@limit_con_service([1, 10], 'data centr')
@decorator_for_sign_applications()
def rack_zakaz(request):
    try:
        package_obj = Package_on_connection_of_service.objects.get(user=request.user, activate=False, deactivate=False)
    except Package_on_connection_of_service.DoesNotExist:
        successfully_create = create_package(request.user,
                                reverse('rack_zakaz'),
                                reverse('my_data_centr'),
                                "{'rack':'rack'}",
                                ['telematic_data_centr', 'usluga_peredachi_dannyh_s_predoplatoi'])
        if not successfully_create:
            raise Http404
        else:
            return HttpResponseRedirect(reverse('rack_zakaz'))
    try:
        bill_acc = BillserviceAccount.objects.get(username=request.user.username)
        profile_obj = request.user.get_profile()
        service_type_obj = Service_type.objects.get(id=1)
        tariff_obj = Tariff.objects.get(id=1)
        status_obj = Status_zakaza.objects.get(id=1)
        zayavka = Zakazy(
                         section_type=2,
                         service_type=service_type_obj,
                         tariff=tariff_obj,
                         bill_account=bill_acc,
                         status_zakaza=status_obj,
                         date_create=datetime.datetime.now(),
                         count_of_units=tariff_obj.unit,
                         count_of_port=tariff_obj.port,
                         count_ip=tariff_obj.ip,
                         socket=tariff_obj.socket,
                         electricity=tariff_obj.electricity,
                         )
        zayavka.save()
        findocsign_queryset = package_obj.findoc_sign.filter(findoc__slug='usluga_peredachi_dannyh_s_predoplatoi')
        if findocsign_queryset:
            findocsign_obj = findocsign_queryset[0]
        fin_doc_zakaz = FinDocSignedZakazy(
                                           fin_doc=findocsign_obj,
                                           zakaz_id=zayavka.id,
                                           )
        fin_doc_zakaz.save()
        findocsign_queryset = package_obj.findoc_sign.filter(findoc__slug='telematic_data_centr')
        if not findocsign_queryset:
            findocsign_obj = get_signed(profile_obj.user, "telematic_data_centr")
        else:
            findocsign_obj = findocsign_queryset[0]
        fin_doc_zakaz = FinDocSignedZakazy(
                                           fin_doc=findocsign_obj,
                                           zakaz_id=zayavka.id,
                                           )
        fin_doc_zakaz.save()
        hidden_id = [zayavka.id]
        cost = float(cost_dc(zayavka.id))
        zayavka.cost = '%.2f' % cost
        zayavka.save()
        package_obj.activate = True
        package_obj.save()

#        rule_obj = Rules_of_drawing_up_documents.objects.get(id=1)
#        spis_rules = Check.group_rules(profile_obj, [rule_obj.id], 'type_check', zayavka.id)
#        content_check_id = Check.create_check(request.user, spis_rules, False, [zayavka.id])
#        dict_documents_for_send = add_document_in_dict_for_send({}, request.user.id, 'Check', content_check_id)
#        send_mail_check(dict_documents_for_send)
        return HttpResponseRedirect("/account/demands_dc/")
    except Exception, e:
        log.add("Exception in rack zakaz: '%s'" % e)
        exc_type, exc_obj, exc_tb = sys.exc_info()  # @UnusedVariable
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        log.add("Exception in rack zakaz: file:%s line:%s" % (fname, exc_tb.tb_lineno))
        return HttpResponseRedirect("/account/rack/#zakaz")


@login_required
@limit_con_service([2, 10], 'data centr')
@decorator_for_sign_applications()
def colocation_zakaz(request):
    try:
        package_obj = Package_on_connection_of_service.objects.get(user=request.user, activate=False, deactivate=False)
        data_temp = eval(package_obj.data)
        request.POST = data_temp
    except Package_on_connection_of_service.DoesNotExist:
        if not request.POST.get('equipment') or not request.POST.get("hidden_unit") or \
            not request.POST.get("hidden_port") or not request.POST.get("hidden_rozetka") or \
            not request.POST.get("hidden_electro") or not request.POST.get("hidden_dop_IP"):
            raise Http404
        request_post = {}
        for key, value in request.POST.iteritems():
            request_post[key.encode("utf-8")] = value.encode("utf-8")
        successfully_create = create_package(request.user, \
                                reverse('colocation_zakaz'), \
                                reverse('my_data_centr'), \
                                '%s' % request_post, \
                                ['telematic_data_centr', 'usluga_peredachi_dannyh_s_predoplatoi'])
        if not successfully_create:
            raise Http404
        else:
            return HttpResponseRedirect(reverse('colocation_zakaz'))
    try:
        bill_acc = BillserviceAccount.objects.get(username=request.user.username)
        profile_obj = request.user.get_profile()
        service_type_obj = Service_type.objects.get(id=2)
        tariff_obj = Tariff.objects.get(id=2)
        status_obj = Status_zakaza.objects.get(id=1)
        zayavka = Zakazy(
                         section_type=2,
                         service_type=service_type_obj,
                         tariff=tariff_obj,
                         bill_account=bill_acc,
                         status_zakaza=status_obj,
                         date_create=datetime.datetime.now(),
                         equipment=request.POST["equipment"],
                         count_of_units=str(request.POST["hidden_unit"]),
                         count_of_port=str(request.POST["hidden_port"]),
                         count_ip=int(request.POST["hidden_dop_IP"]),
                         socket=str(request.POST["hidden_rozetka"]),
                         electricity=str(request.POST["hidden_electro"]),
                         )
        zayavka.save()

        findocsign_queryset = package_obj.findoc_sign.filter(findoc__slug='usluga_peredachi_dannyh_s_predoplatoi')
        if findocsign_queryset:
            findocsign_obj = findocsign_queryset[0]
        fin_doc_zakaz = FinDocSignedZakazy(
                                           fin_doc=findocsign_obj,
                                           zakaz_id=zayavka.id,
                                           )
        fin_doc_zakaz.save()
        findocsign_queryset = package_obj.findoc_sign.filter(findoc__slug='telematic_data_centr')
        if not findocsign_queryset:
            findocsign_obj = get_signed(profile_obj.user, "telematic_data_centr")
        else:
            findocsign_obj = findocsign_queryset[0]
        fin_doc_zakaz = FinDocSignedZakazy(
                                           fin_doc=findocsign_obj,
                                           zakaz_id=zayavka.id,
                                           )
        fin_doc_zakaz.save()
        zayavka.save()
        hidden_id = [zayavka.id]
        cost = float(cost_dc(zayavka.id))
        zayavka.cost = '%.2f' % cost
        zayavka.save()
        user_obj = User.objects.get(username=request.user.username)
        package_obj.activate = True
        package_obj.save()
#        rule_obj = Rules_of_drawing_up_documents.objects.get(id=3)
#        spis_rules = Check.group_rules(profile_obj, [rule_obj.id], 'type_check', zayavka.id)
#        content_check_id = Check.create_check(request.user, spis_rules, False, [zayavka.id])
#        dict_documents_for_send = add_document_in_dict_for_send({}, request.user.id, 'Check', content_check_id)
#        send_mail_check(dict_documents_for_send)
        return HttpResponseRedirect("/account/demands_dc/")
    except Exception, e:
        log.add("Exception in collocation: '%s'" % e)
        exc_type, exc_obj, exc_tb = sys.exc_info()  # @UnusedVariable
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        log.add("Exception in collocation: file:%s line:%s" % (fname, exc_tb.tb_lineno))
        return HttpResponseRedirect("/account/colocation/#zakaz")

@login_required
def vds256_zakaz(request):
    user_obj = User.objects.get(username=request.user.username)
    message = u'Тип услуги: Аренда виртуального выделенного сервера' + u'\nТариф: VDS-256' + u'\nСтоимость услуги: 220 руб.' + u'\nОперационная система: ' + request.POST["hidden_os256"] + u'\nИмя юзера: ' + user_obj.username
    send_mail("Аренда виртуального выделенного сервера", "%s" % message, settings.DEFAULT_FROM_EMAIL, ["sales@globalhome.su"])
    zayvki = Zayavki(tip_uslugi='Аренда виртуального выделенного сервера',
                     tarif='VDS-256',
                     cost='220 руб.',
                     os=request.POST["hidden_os256"],
                     cpu='256 МГц',
                     ram='256 Мб',
                     hdd='25.6 Гб',
                     kol_vo_ip='1',
                     user_id=user_obj.id,
                     user_name=user_obj.username,
                     zayvka_date=datetime.datetime.now(),
                     )
    zayvki.save()
    return HttpResponseRedirect("/account/demands_dc/")

def cost_activated_zakaz(zakaz_obj):
    sum_cost = 0
    sum_cost_temp = Zakazy.objects.filter(main_zakaz=zakaz_obj.id).exclude(status_cost__in=[3]).aggregate(total_cost=Sum('cost'))
    if sum_cost_temp['total_cost']:
        sum_cost = float('%.2f' % float(sum_cost_temp['total_cost']))
    cost = zakaz_obj.cost + sum_cost
    cost = '%.2f' % cost
    return cost


@login_required
def view_dc_zayavka(request, zayavka_id):
    print 'view_dc_zayavka'
    try:
        context = {}
        bill_acc = BillserviceAccount.objects.get(username=request.user.username)
        zakaz_obj = get_object_or_404(Zakazy, id=int(zayavka_id), bill_account=bill_acc)
        if not zakaz_obj.date_activation:
            tariff_obj = Tariff.objects.get(id=41)
            cost = zakaz_obj.cost + ((zakaz_obj.count_ip - zakaz_obj.tariff.ip) * tariff_obj.price_id.cost)
            pod_zakazy = Zakazy.objects.filter(main_zakaz=zakaz_obj.id)
            for pod_zakaz in pod_zakazy:
                cost += pod_zakaz.cost
                cost = '%.2f' % cost
        else:
            cost = cost_activated_zakaz(zakaz_obj)
        zakaz_dict = {'id':zakaz_obj.id, 'service_type':zakaz_obj.service_type, 'tariff':zakaz_obj.tariff,
                      'cost':cost}
        zakaz_dict['electricity'] = zakaz_obj.electricity
        zakaz_dict['equipment'] = zakaz_obj.equipment or False
        zakaz_dict['socket'] = zakaz_obj.socket or False
        if zakaz_obj.tariff.width and zakaz_obj.tariff.height and zakaz_obj.tariff.depth:
            zakaz_dict['size_equipment'] = u'до %sx%sx%s' % (zakaz_obj.tariff.width, zakaz_obj.tariff.height, zakaz_obj.tariff.depth,)
        else:
            zakaz_dict['size_equipment'] = False
        if zakaz_obj.date_activation:
            ip = ''
            zakazy_ip_queryset = Zakazy.objects.filter(Q(main_zakaz=zakaz_obj.id) & Q(status_zakaza_id__in=[2, 4]) & Q(service_type_id=10) & \
                                                       (Q(date_deactivation=None) | Q(date_deactivation__gt=datetime.datetime.now())))
            for zakaz_ip in zakazy_ip_queryset:
                for ip_temp in zakaz_ip.ip.all():
                    if zakaz_ip.date_deactivation:
                        date_deactivation = datetime.datetime.strftime(zakaz_ip.date_deactivation, "%d.%m.%Y")
                        ip += str(ip_temp) + ' <font style="color: red;">до %s</font>' % date_deactivation + '<br />'
                    else:
                        ip += str(ip_temp) + '<br />'
            ip = ip.strip('<br />')
            zakaz_dict['ip'] = ip
        else:
            zakaz_dict['count_ip'] = zakaz_obj.count_ip or False
        dict_garant = {True:u'Гарантированный', False:u'Не гарантированный'}
        if zakaz_obj.service_type.id in (11,):
            zakaz_dict['cpu'] = zakaz_obj.server.cpu
            zakaz_dict['ram'] = "<br />".join(i.__unicode__() for i in zakaz_obj.server.ram.all())
            zakaz_dict['hdd'] = "<br />".join(i.__unicode__() for i in zakaz_obj.server.hdd.all())
            zakaz_dict['unit'] = zakaz_obj.server.count_unit
        else:
            zakaz_dict['unit'] = zakaz_obj.count_of_units
        if zakaz_obj.service_type.id in (2, 11):
            zakaz_inet = Zakazy.objects.filter(main_zakaz=zakaz_obj.id, service_type__id=12)
            if zakaz_inet:
                zakaz_dict['inet'] = u'%s, %s Мбит/сек' % (dict_garant[zakaz_inet[0].tariff.garant], zakaz_inet[0].tariff.speed_inet)
        else:
            zakaz_dict['inet'] = u'%s, 100 Мбит/сек' % dict_garant[False]
        if zakaz_obj.status_zakaza_id == 1:
            context['title_modal'] = u'Просмотр заявки'
            context['button_activate'] = True
            context['server_adrress'] = zakaz_obj.address_dc or False
        elif zakaz_obj.status_zakaza_id in [2, 4]:
            context['title_modal'] = u'Просмотр заказа'
            context['button_activate'] = False
        context['zakaz_obj'] = zakaz_dict
    except Exception, e:
        print "e=%s" % str(e).encode('utf-8')
        exc_type, exc_obj, exc_tb = sys.exc_info()  # @UnusedVariable
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print "Exception in priority_of_services: file:%s line:%s" % (fname, exc_tb.tb_lineno)
    return render_to_response("view_dc_zakaz.html", context)


@login_required
def ajax_dc_configuration(request, zakaz_id):
    context = {}
    profile_obj = Profile.objects.get(user=request.user)
    bill_acc = BillserviceAccount.objects.get(id=profile_obj.billing_account_id)
    zakaz_obj = get_object_or_404(Zakazy, id=zakaz_id, bill_account=bill_acc, service_type__id__in=[1, 2, 11])
    zakazy_ip_queryset = Zakazy.objects.filter(Q(main_zakaz=zakaz_obj.id) & Q(status_zakaza=2) & Q(service_type__id=10) & \
                                               (Q(date_deactivation=None) | Q(date_deactivation__gt=datetime.datetime.now()))).order_by('-status_cost')
    spis_ip = []
    tariff_obj = Tariff.objects.get(id=41)
    for zakaz_ip in zakazy_ip_queryset:
        for ip_temp in zakaz_ip.ip.all():
            if zakaz_ip.date_deactivation:
                date_deactivation = datetime.datetime.strftime(zakaz_ip.date_deactivation, "%d.%m.%Y")
            else:
                date_deactivation = ''
            cost = u'беспл.' if zakaz_ip.status_cost in (3,) else u'%s руб.*' % (tariff_obj.price_id.cost / 1.18)
            spis_ip.append({'name': ip_temp.name, 'cost': cost, 'date_deactivation':date_deactivation, 'free': True if zakaz_ip.status_cost in (3,) else False})
    if spis_ip:
        context['spis_ip'] = spis_ip
        context['count_ip'] = len(spis_ip)
    else:
        context['spis_ip'] = False
        context['count_ip'] = 0
    range_ip = []
    try:
        for i in range(1, dict_count_ip_for_service[zakaz_obj.service_type.id] + 1 - len(zakazy_ip_queryset)):
            range_ip.append({'count':i, 'count_with_cost': u'%s (%s руб.*)' % (i, tariff_obj.price_id.cost * i / 1.18)})
    except Exception, e:
        print e
    context['zakaz_id'] = zakaz_id
    context['range_ip'] = range_ip
    context['permitted_count_ip'] = dict_count_ip_for_service[zakaz_obj.service_type.id]
    return render_to_response("dc_configuration.html", context)


@login_required
@decorator_for_sign_applications()
def apply_dc_configuration(request, zakaz_id):
    def configuration(data, spis_ip, new_ip):

        date_first_day_this_month = datetime.datetime(now.year, now.month, 1, 0, 0, 0)
        date_first_day_next_month = date_first_day_this_month + relativedelta(months=1)
        if spis_ip:
            if data.has_key('spis_ip'):
                spis_ip = data['spis_ip'].split(',')
                for ip in spis_ip:
                    zakaz_ip_obj = get_object_or_404(Zakazy, main_zakaz=zakaz_id, bill_account=bill_acc, ip__name=ip, status_cost__in=[1, 2])
                    zakaz_ip_obj.date_deactivation = date_first_day_next_month
                    zakaz_ip_obj.save()
                    if zakaz_ip_obj.date_deactivation == zakaz_ip_obj.date_activation:
                        zakaz_ip_obj.status_zakaza_id = 3
                        zakaz_ip_obj.save()
        if new_ip:
            if data.has_key('new_ip'):

                count_new_ip = int(data['new_ip'])
                spis_ip = IP.objects.filter(section_type=2, status_ip=1).order_by('price_id')
                if count_new_ip <= len(spis_ip):
                    tariff_obj = Tariff.objects.get(id=41)
                    i = 1
                    print spis_ip
                    spis_zakaz = []
                    for ip in spis_ip:
                        if i <= count_new_ip:
                            i += 1
                            ip_obj = IP.objects.get(name=ip)
                            zakaz_ip = Zakazy(
                                main_zakaz=zakaz_obj.id,
                                bill_account=zakaz_obj.bill_account,
                                section_type=2,
                                status_zakaza_id=2,
                                service_type_id=10,
                                tariff=tariff_obj,
                                date_create=datetime.datetime.now(),
                                date_activation=datetime.datetime.now(),
                                date_deactivation=zakaz_obj.date_deactivation,
                                count_ip=1,
                                )
                            zakaz_ip.save()
                            zakaz_ip.ip.add(ip_obj)
                            zakaz_ip.save()
                            cost = float(cost_dc(zakaz_ip.id))
                            zakaz_ip.cost = '%.2f' % cost
                            zakaz_ip.save()
                            ip_obj.status_ip_id = 2
                            ip_obj.save()
                            add_record_in_data_centr_payment(zakaz_ip)
                            add_record_in_priority_of_services(zakaz_ip)
                            findoc_sign_zakaz = FinDocSignedZakazy.objects.get(zakaz_id=zakaz_obj.id, fin_doc__findoc__slug='telematic_data_centr')
                            findoc_sign_zakaz_ip = copy.copy(findoc_sign_zakaz)
                            findoc_sign_zakaz_ip.id = None
                            findoc_sign_zakaz_ip.zakaz_id = zakaz_ip.id
                            findoc_sign_zakaz_ip.save()
                            spis_zakaz.append(zakaz_ip.id)
                    spis_rules = Check.group_rules(profile_obj, [13], 'type_check')
                    print 'spis_rules = %s' % spis_rules
                    content_check_id = Check.create_check(request.user, spis_rules, False, spis_zakaz)
                    print 'content = %s' % content_check_id
                    dict_documents_for_send = add_document_in_dict_for_send({}, request.user.id, 'Check', content_check_id)
                    print 'dict_document = %s' % dict_documents_for_send
                    send_mail_check(dict_documents_for_send)
                else:
                    request.notifications.add(_(u"К сожалению мы не можем Вам выдать такое количество IP-адресов!"), "warning")
        package_obj.activate = True
        package_obj.save()
        findocsign_obj = package_obj.findoc_sign.all()[0]
        fin_doc_zakaz = FinDocSignedZakazy(
                                   fin_doc=findocsign_obj,
                                   zakaz_id=zakaz_obj.id,
                                   )
        fin_doc_zakaz.save()

    profile_obj = Profile.objects.get(user=request.user)
    bill_acc = BillserviceAccount.objects.get(id=profile_obj.billing_account_id)
    zakaz_obj = get_object_or_404(Zakazy, id=zakaz_id, bill_account=bill_acc)
    try:

        package_obj = Package_on_connection_of_service.objects.get(user=request.user, activate=False, deactivate=False)
        print "try"
    except Package_on_connection_of_service.DoesNotExist:
        print "except"
        if not request.GET.has_key('spis_ip') and not request.GET.has_key('new_ip'):
            raise Http404
        request_get = {}
        print " GET -%s" % request.GET
        for key, value in request.GET.iteritems():
            request_get[key.encode("utf-8")] = value.encode("utf-8")

        successfully_create = create_package(request.user, \
                                '/account/demands_dc/apply_configuration/%s/' % zakaz_id,
                                reverse('my_data_centr'),
                                '%s' % request_get,
                                ['dop_soglashenie_izmenenie_internet'],)
        if not successfully_create:
            raise Http404
        else:
            return HttpResponseRedirect('/account/demands_dc/apply_configuration/%s/' % zakaz_id)
    now = datetime.datetime.now()
    data_temp = eval(package_obj.data)
    data = data_temp

#     configuration(data, data.has_key('spis_ip'), data.has_key('new_ip'))
#     request.notifications.add(_(u"Конфигурация успешно изменена!"), "success")
#     return HttpResponseRedirect(reverse("my_data_centr"))
    if zakaz_obj.date_activation > now:
        configuration(data, True, True)
        print 'now'
    elif (data.has_key('new_ip') and (data.has_key('spis_ip'))):
        print "has"
        configuration(data, False, True)
        del data['new_ip']
        for key, value in data.iteritems():
            data_temp[key.encode("utf-8")] = value.encode("utf-8")
        successfully_create = create_package(request.user, \
                                '/account/demands_dc/apply_configuration/%s/' % zakaz_id, \
                                reverse('my_data_centr'), \
                                '%s' % data_temp,
                                ['dop_soglashenie_izmenenie_internet'],)
        if not successfully_create:
            raise Http404
        else:
            return HttpResponseRedirect('/account/demands_dc/apply_configuration/%s/' % zakaz_id)
    else:
        configuration(data, True, True,)
    request.notifications.add(_(u"Конфигурация успешно изменена!"), "success")
    return HttpResponseRedirect(reverse('my_data_centr'))


@login_required
def vds512_zakaz(request):
    user_obj = User.objects.get(username=request.user.username)
    message = u'Тип услуги: Аренда виртуального выделенного сервера' + u'\nТариф: VDS-512' + u'\nСтоимость услуги: 440 руб.' + u'\nОперационная система: ' + request.POST["hidden_os512"] + u'\nИмя юзера: ' + user_obj.username
    send_mail("Аренда виртуального выделенного сервера", "%s" % message, settings.DEFAULT_FROM_EMAIL, ["sales@globalhome.su"])
    zayvki = Zayavki(tip_uslugi='Аренда виртуального выделенного сервера',
                     tarif='VDS-512',
                     cost='440 руб.',
                     os=request.POST["hidden_os512"],
                     cpu='512 МГц',
                     ram='512 Мб',
                     hdd='51.2 Гб',
                     kol_vo_ip='1',
                     user_id=user_obj.id,
                     user_name=user_obj.username,
                     zayvka_date=datetime.datetime.now(),
                     )
    zayvki.save()
    return HttpResponseRedirect("/account/demands_dc/")

@login_required
def vds1024_zakaz(request):
    user_obj = User.objects.get(username=request.user.username)
    message = u'Тип услуги: Аренда виртуального выделенного сервера' + u'\nТариф: VDS-1024' + u'\nСтоимость услуги: 880 руб.' + u'\nОперационная система: ' + request.POST["hidden_os1024"] + u'\nИмя юзера: ' + user_obj.username
    send_mail("Аренда виртуального выделенного сервера", "%s" % message, settings.DEFAULT_FROM_EMAIL, ["sales@globalhome.su"])
    zayvki = Zayavki(tip_uslugi='Аренда виртуального выделенного сервера',
                     tarif='VDS-1024',
                     cost='880 руб.',
                     os=request.POST["hidden_os1024"],
                     cpu='1024 МГц',
                     ram='1024 Мб',
                     hdd='102.4 Гб',
                     kol_vo_ip='1',
                     user_id=user_obj.id,
                     user_name=user_obj.username,
                     zayvka_date=datetime.datetime.now(),
                     )
    zayvki.save()
    return HttpResponseRedirect("/account/demands_dc/")

@login_required
def vds2048_zakaz(request):
    user_obj = User.objects.get(username=request.user.username)
    message = u'Тип услуги: Аренда виртуального выделенного сервера' + u'\nТариф: VDS-2048' + u'\nСтоимость услуги: 1760 руб.' + u'\nОперационная система: ' + request.POST["hidden_os2048"] + u'\nИмя юзера: ' + user_obj.username
    send_mail("Аренда виртуального выделенного сервера", "%s" % message, settings.DEFAULT_FROM_EMAIL, ["sales@globalhome.su"])
    zayvki = Zayavki(tip_uslugi='Аренда виртуального выделенного сервера',
                     tarif='VDS-2048',
                     cost='1760 руб.',
                     os=request.POST["hidden_os2048"],
                     cpu='2048 МГц',
                     ram='2048 Мб',
                     hdd='204.8 Гб',
                     kol_vo_ip='1',
                     user_id=user_obj.id,
                     user_name=user_obj.username,
                     zayvka_date=datetime.datetime.now(),
                     )
    zayvki.save()
    return HttpResponseRedirect("/account/demands_dc/")

@login_required
def vds3072_zakaz(request):
    user_obj = User.objects.get(username=request.user.username)
    message = u'Тип услуги: Аренда виртуального выделенного сервера' + u'\nТариф: VDS-3072' + u'\nСтоимость услуги: 2640 руб.' + u'\nОперационная система: ' + request.POST["hidden_os3072"] + u'\nИмя юзера: ' + user_obj.username
    send_mail("Аренда виртуального выделенного сервера", "%s" % message, settings.DEFAULT_FROM_EMAIL, ["sales@globalhome.su"])
    zayvki = Zayavki(tip_uslugi='Аренда виртуального выделенного сервера',
                     tarif='VDS-3072',
                     cost='2640 руб.',
                     os=request.POST["hidden_os3072"],
                     cpu='3072 МГц',
                     ram='3072 Мб',
                     hdd='307.2 Гб',
                     kol_vo_ip='1',
                     user_id=user_obj.id,
                     user_name=user_obj.username,
                     zayvka_date=datetime.datetime.now(),
                     )
    zayvki.save()
    return HttpResponseRedirect("/account/demands_dc/")

@login_required
def vds_zakaz_hand(request):
    user_obj = User.objects.get(username=request.user.username)
    message = u'Тип услуги: Аренда виртуального выделенного сервера' + u'\nТариф: Создан вручную' + u'\nПроцессор: ' + request.POST["hidden_hand_cpu"] + u' МГц' + u'\nОперативная память: ' + request.POST["hidden_hand_ram"] + u' Мб' + u'\nОбъем жесткого диска: ' + request.POST["hidden_hand_hdd"] + u' Гб' + u'\nКоличество IP адресов: ' + request.POST["hidden_hand_ip"] + u' шт.' + u'\nОперационная система: ' + request.POST["hidden_hand"] + u'\nСтоимость: ' + request.POST["hidden_cost"] + u'\nИмя юзера: ' + user_obj.username
    send_mail("Аренда виртуального выделенного сервера", "%s" % message, settings.DEFAULT_FROM_EMAIL, ["sales@globalhome.su"])
    zayvki = Zayavki(tip_uslugi='Аренда виртуального выделенного сервера',
                     tarif='Создан вручную',
                     cost=request.POST["hidden_cost"],
                     os=request.POST["hidden_hand"],
                     cpu=request.POST["hidden_hand_cpu"],
                     ram=request.POST["hidden_hand_ram"],
                     hdd=request.POST["hidden_hand_hdd"],
                     kol_vo_ip=request.POST["hidden_hand_ip"],
                     user_id=user_obj.id,
                     user_name=user_obj.username,
                     zayvka_date=datetime.datetime.now(),
                     )
    zayvki.save()
    return HttpResponseRedirect("/account/demands_dc/")


def real_section_name(zakaz_obj, payment_obj=None):
    service_type_id = zakaz_obj.service_type.id
    if service_type_id in (3,):
        spis_ext_number = []
        for j in zakaz_obj.ext_numbers.all():
            spis_ext_number.append(j.number)
        ext_numbers = ', '.join([str(x) for x in spis_ext_number]).rstrip(', ')
        section_name = '%s (%s)' % (zakaz_obj.service_type.service, ext_numbers)
    elif service_type_id in (10,):
        ip = zakaz_obj.ip.all()[0]
        section_name = u'%s (%s)' % (zakaz_obj.service_type.service, ip)
    elif service_type_id in (13,):
        if zakaz_obj.delivery:
            section_name = u'%s + Доставка' % (zakaz_obj.service_type.service)
        else:
            section_name = u'%s' % (zakaz_obj.service_type.service)
    else:
        pod_zakazy = Zakazy.objects.filter(main_zakaz=zakaz_obj.id, status_zakaza__id__in=[2, 4], service_type_id=12)
        ports = len(pod_zakazy) if len(pod_zakazy) > 0 else ''
        if ports:
            section_name = u'%s (Заказ № %s + портов: %s шт.)' % (zakaz_obj.service_type.service, zakaz_obj.id, ports)
        else:
            section_name = u'%s (Заказ № %s)' % (zakaz_obj.service_type.service, zakaz_obj.id)
    return section_name

@login_required
@render_to('priority_of_services.html')
def priority_of_services(request):
    profile_obj = Profile.objects.get(user=request.user)
    if profile_obj.is_card:
        raise Http404
    bill_account = profile_obj.billing_account
    # функция для изменения статуса автооплаты
    def check_auto_paid(value):
        bill_account.auto_paid = value
        bill_account.save()
        return value
    # функция которая собирает и передает в html приоритеты и оплаты услуг
    def show_spis_service():
        now = datetime.datetime.now()
        number = 0
        priority = []
        # получаем приоритеты для данного пользователя
        bill_account_obj = BillserviceAccount.objects.get(id=profile_obj.billing_account_id)
        priority_temp = Priority_of_services.objects.filter(bill_account=bill_account_obj).order_by('priority')
        if not priority_temp:
            return '', ''
        # если у пользователя есть услуги (а соответственно и приоритеты, то красивенько всё это компануем)
        for i in priority_temp:
            number += 1
            zakaz_obj = Zakazy.objects.get(id=i.zakaz_id)


            payment_obj = Data_centr_payment.objects.get((Q(year=now.year) & Q(month=now.month) & Q(bill_account=profile_obj.billing_account) & Q(zakaz=zakaz_obj.id) & Q(every_month=True)) \
                                                          | (Q(bill_account=bill_account_obj) & Q(zakaz=zakaz_obj.id) & Q(every_month=False) & Q(payment_date=None)) \
                                                          | (Q(year=now.year) & Q(month=now.month) & Q(bill_account=profile_obj.billing_account) & Q(zakaz=zakaz_obj.id) & Q(every_month=False)))
            section_name = real_section_name(zakaz_obj, payment_obj)
            paid = 'Not paid'
            if payment_obj.payment_date:
                paid = 'Paid'
            else:
                if zakaz_obj.status_zakaza.id in (4,):
                    paid = 'Block'
#            dict_month = {1:'январь', 2:'февраль', 3:'март', 4:'апрель', \
#                          5:'май', 6:'июнь', 7:'июль', 8:'август', 9:'сентябрь', \
#                          10:'октябрь', 11:'ноябрь', 12:'декабрь'}
            if not payment_obj.every_month:
                start_activation = zakaz_obj.date_end_test_period if zakaz_obj.date_end_test_period else zakaz_obj.date_activation
                date_for_paid = u'до %s' % datetime.datetime.strftime(start_activation + relativedelta(days=bill_account_obj.idle_time), "%d.%m.%Y")
            else:
                date_first_day_this_month = datetime.datetime(now.year, now.month, 1, 0, 0, 0)
                date_first_day_next_month = date_first_day_this_month + relativedelta(months=1)
                date_for_paid = u'до %s' % datetime.datetime.strftime(date_first_day_next_month - relativedelta(days=1), "%d.%m.%Y")
#            date_for_paid = '%s %s' % (dict_month[payment_obj.month], payment_obj.year)
            priority.append({"id":i.id, "zakaz_id":zakaz_obj.id, "priority":number, \
                             "cost":payment_obj.cost, "section_name":section_name, "paid":paid, \
                             "date_for_paid":date_for_paid})
        return priority, number
    # начало функции priority_of_services
    context = {}
    save = {}
    priority, number = show_spis_service()
    try:
        # если нажали кнопку "сохранить", то пересохраняем приоритеты услуг
        if request.POST.get("save"):
            for i in range(1, number + 1):
                save[i] = int(request.POST["raw%s" % i])
            for key in save:
                priority_id = save[key]
                priority_obj = Priority_of_services.objects.get(id=priority_id, bill_account=profile_obj.billing_account_id)
                priority_obj.priority = key
                priority_obj.save()
            priority, number = show_spis_service()
            request.notifications.add(_(u"Приоритеты успешно изменены!"), "success")
        # если нажали кнопку оплатить
        elif request.POST.get("paid_services"):
            spis_zakaz_id = request.POST.getlist("checks")
            if spis_zakaz_id:
                write_off_of_money(profile_obj.billing_account, spis_zakaz_id)
                request.notifications.add(_(u"Операция по оплате услуг успешно завершена!"), "success")
            else:
                request.notifications.add(_(u"Вы не выбрали ни одной услуги для оплаты!"), "warning")
            priority, number = show_spis_service()
        # если изменили тип оплаты
        elif request.POST.get("type_oplata"):
            payment_type = request.POST["type_oplata"]
            if payment_type in ('hand',):
                check_auto_paid(False)
            elif payment_type in ('auto',):
                check_auto_paid(True)
            request.notifications.add(_(u"Тип оплаты успешно изменен!"), "success")
    except Exception, e:
        request.notifications.add(_(u"Произошла непредвиденная ошибка!"), "warning")
        log.add("e=%s" % str(e).encode('utf-8'))
        exc_type, exc_obj, exc_tb = sys.exc_info()  # @UnusedVariable
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        log.add("Exception in priority_of_services: file:%s line:%s" % (fname, exc_tb.tb_lineno))
    context['type_payment'] = bill_account.auto_paid
    context['priority_of_services'] = priority
    context["current_view_name"] = "account_show_tariffs"
    return context

# функция, которая добавляет в словарь аккаунт, тип сообщения и номер заказа
def add_text_message(dict_message, type_message, zakaz_obj):
    spis_zakazy = [zakaz_obj.id]
    if dict_message.has_key(zakaz_obj.bill_account.id):
        if dict_message[zakaz_obj.bill_account.id].has_key(type_message):
            dict_message[zakaz_obj.bill_account.id][type_message].append(zakaz_obj.id)
        else:
            dict_message[zakaz_obj.bill_account.id].update({type_message : spis_zakazy})
    else:
        dict_message.update({zakaz_obj.bill_account.id:{type_message : spis_zakazy}})
    return dict_message

# добавляет запись с учетом сегодняшней даты (срабатывает, когда подключаем услугу)
def add_record_in_data_centr_payment(zakaz_obj):
    now = datetime.datetime.now()
    # высчитываем стоимость заказа
    date_activation = datetime.datetime(zakaz_obj.date_activation.year, zakaz_obj.date_activation.month, \
                                        zakaz_obj.date_activation.day, 0, 0, 0)
    date_first_day_this_month = datetime.datetime(now.year, now.month, 1, 0, 0, 0)
    date_first_day_next_month = date_first_day_this_month + relativedelta(months=1)
    count_day_in_month = float(calendar.mdays[datetime.date.today().month])
    count_day_for_pay = date_first_day_next_month - date_activation
    cost = float(zakaz_obj.cost) / float(count_day_in_month) * float(count_day_for_pay.days)
    cost += zakaz_obj.connection_cost.cost
    if zakaz_obj.delivery:
        cost += zakaz_obj.delivery.price_id.cost
    pod_zakazy = Zakazy.objects.filter(main_zakaz=zakaz_obj.id, status_cost=2)
    for pod_zakaz in pod_zakazy:
        cost += float(pod_zakaz.cost) / float(count_day_in_month) * float(count_day_for_pay.days)
    cost_zakaz = '%.2f' % cost
    # добавляем новую запись
    payment = Data_centr_payment(
                                 year=now.year,
                                 month=now.month,
                                 bill_account=zakaz_obj.bill_account,
                                 zakaz=zakaz_obj,
                                 every_month=False,
                                 cost=cost_zakaz,
                                 )
    payment.save()

# добавляет запись с минимальным приоритетом (срабатывает, когда подключаем услугу)
def add_record_in_priority_of_services(zakaz_obj):
    # находим максимальный приоритет у данного пользователя
    max_priority = Priority_of_services.objects.filter(bill_account=zakaz_obj.bill_account).aggregate(Max('priority'))['priority__max']
    # добавляем новую запись
    if not max_priority:
        max_priority = 0
    priority = Priority_of_services(
                                    bill_account=zakaz_obj.bill_account,
                                    zakaz_id=zakaz_obj.id,
                                    priority=max_priority + 1
                                    )
    priority.save()


# функция для принудительного отключения услуги
def compulsory_shutdown_of_service(spis_zakaz_id, status_zakaza=5, end_month=False):
    cur = connections[settings.BILLING_DB].cursor()
    # cur.connection.set_isolation_level(1)
    # cur.connection.commit()
    dict_message = {}
    message = {}
    log.add("***********************************************************************************************************")
    for zakaz_id in spis_zakaz_id:
        with transaction.commit_manually(using=settings.BILLING_DB):
            try:
                zakaz_obj = Zakazy.objects.get(id=zakaz_id)
                if zakaz_obj.bill_account.id == 2971 and status_zakaza == 5:
                    continue
                if zakaz_obj.service_type.id in (10,):
                    zakazy_queryset = Zakazy.objects.filter(ip__name=zakaz_obj.ip.all()[0], bill_account=zakaz_obj.bill_account, date_deactivation=None).exclude(id=zakaz_obj.id)
                    if not zakazy_queryset:
                        ip_obj = IP.objects.get(name=zakaz_obj.ip.all()[0])
                        status_obj = Status_ip.objects.get(id=1)
                        ip_obj.status_ip = status_obj
                        ip_obj.save()
                if zakaz_obj.service_type.id in (8,):
                    bill_account = zakaz_obj.bill_account
                    bill_account.status = 2
                    bill_account.save()
    #                subaccount = SubAccount.objects.filter(account=zakaz_obj.bill_account)
    #                if subaccount:
    #                    subaccount[0].nas_id = 1
    #                    subaccount[0].save()
                if zakaz_obj.section_type == 1:  # если телефония
                    spis_external_number_id = []
                    cur.execute("SELECT externalnumber_id FROM data_centr_zakazy_ext_numbers WHERE zakazy_id = %s;", (zakaz_obj.id,))
                    spis_external_number_id += [x[0] for x in cur.fetchall()]
                    for number_id in spis_external_number_id:
                        cur.execute("UPDATE external_numbers SET phone_numbers_group_id=%s, account_id=%s,\
                        is_free=%s, is_reserved=%s, blocked=%s, date_deactivation=%s WHERE id=%s;", (None, None, False, True, None, datetime.datetime.now(), number_id,))
                    cur.execute("DELETE FROM billservice_prepaid_minutes WHERE zakaz_id=%s", (zakaz_obj.id,))
                if zakaz_obj.service_type.id == 9:
                    if status_zakaza == 5:
                        model = Record_talk_activated_tariff.objects.get(Q(billing_account_id=zakaz_obj.bill_account.id) & \
                                                                        # Q(date_activation__lt=datetime.datetime.now()) & \
                                                                        Q(tariff=2) & \
                                                                        (Q(date_deactivation=None) | Q(date_deactivation__gt=datetime.datetime.now()))\
                                                                        )
                        model.date_deactivation = datetime.datetime.now()
                        model.save()
                if zakaz_obj.service_type.id == 11:
                    ports_qs = Ports.objects.filter(adrress=zakaz_obj.address_dc)
                    if ports_qs:
                        s = Cisco(ports_qs[0].switch.ip, CISCO_PASSWORD)
                        for port_obj in ports_qs:
                            s.disableport(str(port_obj.prefix_interface))
                            port_obj.status_port = 4
                            port_obj.save()
            except Exception, e:
                log.add("Exception in compulsory_shutdown_of_service: '%s'" % e)
                exc_type, exc_obj, exc_tb = sys.exc_info()  # @UnusedVariable
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                log.add("Exception in compulsory_shutdown_of_service: file:%s line:%s" % (fname, exc_tb.tb_lineno))
                transaction.rollback(settings.BILLING_DB)
            else: #если не был исключения
                print 'else'
                #print spis_zakaz_id
                
                status_obj = Status_zakaza.objects.get(id=status_zakaza)
                zakaz_obj.status_zakaza = status_obj
                zakaz_obj.save()
                joint_zakazy = Zakazy.objects.filter(main_zakaz=zakaz_obj.id, status_cost__in=[2, 3], status_zakaza_id__in=[2, 4])
                for joint_zakaz in joint_zakazy:
                    joint_zakaz.status_zakaza = status_obj
                    joint_zakaz.save()
                if status_zakaza == 5:
                    now = datetime.datetime.now()
                    if end_month:
                        date_first_day_this_month = datetime.datetime(now.year, now.month, 1, 0, 0, 0)
                        zakaz_obj.date_deactivation = date_first_day_this_month
                        for joint_zakaz in joint_zakazy:
                            joint_zakaz.date_deactivation = date_first_day_this_month
                            joint_zakaz.save()
                    else:
                        zakaz_obj.date_deactivation = now
                        for joint_zakaz in joint_zakazy:
                            joint_zakaz.date_deactivation = now
                            joint_zakaz.save()
                    zakaz_obj.save()
                    payment_obj = Data_centr_payment.objects.get(payment_date=None, postdate=False, zakaz=zakaz_obj)
                    payment_obj.postdate = True
                    payment_obj.save()
                    limit_qs = Limit_connection_service.objects.filter(bill_acc=zakaz_obj.bill_account, service_type=zakaz_obj.service_type)
                    for limit_obj in limit_qs:
                        limit_obj.count_limit = limit_obj.count_limit - 1
                        limit_obj.save()
                    log.add("Compulsory shutdown zakaz = %s is successfully complete" % zakaz_obj.id)
                    message = add_text_message(dict_message, 'message_shutdown', zakaz_obj)
                else:
                    log.add("Deactivated zakaz = %s is successfully complete" % zakaz_obj.id)
                    message = add_text_message(dict_message, 'message_deactivated', zakaz_obj)
                Priority_of_services.objects.filter(bill_account=zakaz_obj.bill_account, zakaz_id=zakaz_obj.id).delete()
                transaction.commit(using=settings.BILLING_DB)
    log.add("Operation on compulsory shutdown and deactivated of service`s is successfully complete, zakazy=%s" % spis_zakaz_id)
    log.add("***********************************************************************************************************")
    return message

# функция для блокировки услуг
def block_service(spis_zakaz_id):
    cur = connections[settings.BILLING_DB].cursor()
    #cur.connection.set_isolation_level(1)
    #cur.connection.commit()
    dict_message = {}
    log.add("***********************************************************************************************************")
    for zakaz_id in spis_zakaz_id:
        with transaction.commit_manually(using=settings.BILLING_DB):
            transaction.commit(settings.BILLING_DB)
            try:
                zakaz_obj = Zakazy.objects.get(id=zakaz_id)
                status_obj = Status_zakaza.objects.get(id=4)
                zakaz_obj.status_zakaza = status_obj
                zakaz_obj.save()
                joint_zakazy = Zakazy.objects.filter(main_zakaz=zakaz_obj.id, status_cost__in=[2, 3], status_zakaza_id__in=[2, ])
                for joint_zakaz in joint_zakazy:
                    joint_zakaz.status_zakaza = status_obj
                    joint_zakaz.save()
                if zakaz_obj.service_type.id == 3:
                    ext_number = zakaz_obj.ext_numbers.all()[0]
                    ext_number.blocked = True
                    ext_number.save()
                if zakaz_obj.service_type.id == 9:
                    model = Record_talk_activated_tariff.objects.get(Q(billing_account_id=zakaz_obj.bill_account.id) & \
                                                                    # Q(date_activation__lt=datetime.datetime.now()) & \
                                                                    Q(tariff=2) & \
                                                                    (Q(date_deactivation=None) | Q(date_deactivation__gt=datetime.datetime.now()))\
                                                                    )
                    model.blocked = True
                    model.save()
                if zakaz_obj.service_type.id == 11:
                    ports_qs = Ports.objects.filter(adrress=zakaz_obj.address_dc)
                    if ports_qs:
                        s = Cisco(ports_qs[0].switch.ip, CISCO_PASSWORD)
                        for port_obj in ports_qs:
                            s.disableport(str(port_obj.prefix_interface))
                            port_obj.status_port = 4
                            port_obj.save()

                if zakaz_obj.service_type.id in (8,):
                    bill_account = zakaz_obj.bill_account
                    bill_account.status = 2
                    bill_account.save()
    #                subaccounts = SubAccount.objects.filter(account=zakaz_obj.bill_account)
    #                subaccounts[0].nas_id = 1
    #                subaccounts[0].save()
                if zakaz_obj.service_type.id in (10,):
                    subaccount = SubAccount.objects.filter(account=zakaz_obj.bill_account)
                    if subaccount:
                        subaccount[0].vpn_ip_address = '0.0.0.0'
                        subaccount[0].save()
                log.add("Block zakaz = %s is successfully complete" % zakaz_obj.id)
            except Exception, e:
                log.add("Exception in block_service: '%s'" % e)
                exc_type, exc_obj, exc_tb = sys.exc_info()  # @UnusedVariable
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                log.add("Exception in block_service: file:%s line:%s" % (fname, exc_tb.tb_lineno))
                transaction.rollback(settings.BILLING_DB)
            else:
                transaction.commit(settings.BILLING_DB)
        message = add_text_message(dict_message, 'message_block', zakaz_obj)
    log.add("Operation on block_service`s is successfully complete, zakazy=%s" % spis_zakaz_id)
    log.add("***********************************************************************************************************")
    return message

# функция по списанию денег(на входе объет аккаунт из биллинга и список заказов)
@transaction.commit_manually(using='billing')
def write_off_of_money(bill_account, spis_zakazy=[]):
    print 'write_off_of_money'
    # начало функции write_off_of_money
    message = {}
    spis_zakaz_for_compulsory_shutdown = []
    dict_message = {}
    if spis_zakazy and bill_account:
        # делаем подключение к базе
        log.add("***********************************************************************************************************")
        log.add("--------------------- start operation write off of money for bill_account = %s -------------" % bill_account.id)
        cur = connections[settings.BILLING_DB].cursor()
        transaction.commit(settings.BILLING_DB)
        now = datetime.datetime.now()
        # бежим по списку заказов
        for zakaz in spis_zakazy:
            log.add("--------------------- start operation with zakaz = %s --------------" % zakaz)
            # смотрим есть ли у пользователя не уплата по этому заказу
            try:
                payment_obj = Data_centr_payment.objects.get(bill_account=bill_account, zakaz=zakaz, payment_date=None)
            except Data_centr_payment.DoesNotExist:
                log.add("Zakaz = %s is already paid" % zakaz)
                continue

            log.add('4')
            zakaz_obj = Zakazy.objects.get(id=zakaz)
            log.add('5')

            # если заказ деактивирован или отключен, то переходим к следующему заказу (это дополнительная проверка)
            # срабатываем когда скрипт по списанию денег передает все заказы (чтобы в скрипте не делать лишнюю проверку)
            if zakaz_obj.status_zakaza.id in (3, 5):
                log.add('6')
                log.add("Zakaz = %s deactivated or shut down" % zakaz)
                continue
            # если не ежемесячный заказ
            log.add('7')
            if not payment_obj.every_month:
                log.add('8')
                start_activation = zakaz_obj.date_end_test_period if zakaz_obj.date_end_test_period else zakaz_obj.date_activation
                actual_idle_time = now - start_activation
                # проверяем не просрочен ли разовый (не ежемесячный) заказ
                # по сути мы здесь не можем быть, проверка для хакеров, которые ловят момент оплаты на границе окончания времени :)
                if actual_idle_time.days >= bill_account.idle_time:
                    log.add('9')
                    spis_zakaz_for_compulsory_shutdown.append(zakaz_obj.id)
                    continue  #отключаем и высылаем сообщение !!!!!!!!!!!!!!
            elif not ((payment_obj.year == now.year) and (payment_obj.month == now.month)):
                log.add('10')
                # если попали сюда, значит для ежемесячного заказа вышло время оплаты(месяц)
                # по сути мы здесь не можем быть, проверка для хакеров, которые ловят момент оплаты на границе месяцев :)
                spis_zakaz_for_compulsory_shutdown.append(zakaz_obj.id)
                continue  #отключаем и высылаем сообщение !!!!!!!!!!!!!!
            # обновляем объект, чтобы постоянно получать свежий баланс
            log.add('11')
            bill_account = BillserviceAccount.objects.get(id=bill_account.id)
            log.add('12')

            sum_ballance = bill_account.ballance + bill_account.credit
            log.add('13')
            # если баланс + кредит меньше стоимости, то переходим на следующий заказ
            log.add("ballance = %.2f, cost=%.2f" % (sum_ballance, payment_obj.cost))
            log.add("ballance = %s, cost=%s" % (type(sum_ballance), type(payment_obj.cost)))
            if float(sum_ballance) < payment_obj.cost:
                transaction.commit(settings.BILLING_DB)
                log.add("there is not enough money at the bill_account = %s" % bill_account.id)
                continue
            else:
                # иначе пытаемся списать
                log.add("write_off_of_money")
                cost_zakaz = -payment_obj.cost
                with transaction.commit_manually(using=settings.BILLING_DB):
                    transaction.commit(settings.BILLING_DB)
                    try:
                        section_name = real_section_name(zakaz_obj)
                        cur.execute("INSERT INTO billservice_transaction(bill, account_id, type_id, approved, summ, description, created) VALUES(%s, %s, %s, %s, %s, %s, now());", (section_name, bill_account.id, "ZAKAZ_PAY", True, cost_zakaz, u'Оплата заказа №%s' % zakaz))
                        payment_obj.payment_date = now
                        payment_obj.save()
                        if zakaz_obj.status_zakaza.id in (4,):
                            status_obj = Status_zakaza.objects.get(id=2)
                            zakaz_obj.status_zakaza = status_obj
                            zakaz_obj.save()
                            joint_zakazy = Zakazy.objects.filter(main_zakaz=zakaz_obj.id, status_cost__in=[2, 3], status_zakaza_id__in=[4, ])
                            for joint_zakaz in joint_zakazy:
                                joint_zakaz.status_zakaza = status_obj
                                joint_zakaz.save()
                            if zakaz_obj.service_type.id == 3:
                                ext_number = zakaz_obj.ext_numbers.all()[0]
                                ext_number.blocked = False
                                ext_number.save()
                            if zakaz_obj.service_type.id == 9:
                                model = Record_talk_activated_tariff.objects.get(Q(billing_account_id=bill_account.id) & \
                                                                                # Q(date_activation__lt=datetime.datetime.now()) & \
                                                                                Q(tariff=2) & \
                                                                                (Q(date_deactivation=None) | Q(date_deactivation__gt=datetime.datetime.now()))\
                                                                                )
                                model.blocked = False
                                model.save()

                            if zakaz_obj.service_type.id == 11:
                                ports_qs = Ports.objects.filter(adrress=zakaz_obj.address_dc)
                                if ports_qs:
                                    s = Cisco(ports_qs[0].switch.ip, CISCO_PASSWORD)
                                    for port_obj in ports_qs:
                                        s.enableport(str(port_obj.prefix_interface))
                                        port_obj.status_port = 1
                                        port_obj.save()
                            if zakaz_obj.service_type.id in (8,):
                                bill_account = zakaz_obj.bill_account
                                bill_account.status = 1
                                bill_account.save()
    #                            subaccounts = SubAccount.objects.filter(account=zakaz_obj.bill_account)
    #                            subaccounts[0].nas_id = None
    #                            subaccounts[0].save()
                            if zakaz_obj.service_type.id in (10,):
                                subaccount = SubAccount.objects.filter(account=zakaz_obj.bill_account)
                                if subaccount:
                                    ip_address = zakaz_obj.ip.all()[0]
                                    subaccount[0].vpn_ip_address = ip_address.name
                                    subaccount[0].save()
                            message = add_text_message(dict_message, 'message_unblock', zakaz_obj)
                            log.add("Unblock zakaz = %s is successfully complete" % zakaz_obj.id)
                        if not payment_obj.every_month:
                            if ((payment_obj.year != now.year) or (payment_obj.month != now.month)):
                                cost = zakaz_obj.cost
                                pod_zakazy = Zakazy.objects.filter(main_zakaz=zakaz_obj.id, status_zakaza__id__in=[2, 4], status_cost=2)
                                for pod_zakaz in pod_zakazy:
                                    cost += pod_zakaz.cost
                                payment = Data_centr_payment(
                                                             year=now.year,
                                                             month=now.month,
                                                             bill_account=zakaz_obj.bill_account,
                                                             zakaz=zakaz_obj,
                                                             cost=cost,
                                                             )
                                payment.save()
                            if zakaz_obj.service_type.id in (3,):
                                # начисляем бесплатные минуты
                                last_day = int(calendar.mdays[datetime.date.today().month])
                                day = float(calendar.mdays[datetime.date.today().month] - datetime.datetime.now().day + 1)
                                free_minutes = zakaz_obj.tariff.free_minutes
                                free_minutes = float(free_minutes) / float(last_day) * float(day)
                                cur.execute("INSERT INTO billservice_prepaid_minutes(zone_id, minutes, account_id, service_id, date_of_accrual, zakaz_id) VALUES(%s, %s, %s, %s, now(), %s);", (zakaz_obj.tariff.tel_zone, int(free_minutes), zakaz_obj.bill_account.id, 0, zakaz_obj.id))

                    except Exception, e:
                        log.add("Exception in write_off_of_money: '%s'" % e)
                        exc_type, exc_obj, exc_tb = sys.exc_info()  # @UnusedVariable
                        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                        log.add("Exception in write_off_of_money: file:%s line:%s" % (fname, exc_tb.tb_lineno))
                        transaction.rollback(settings.BILLING_DB)
                    else:
                        transaction.commit(settings.BILLING_DB)
                log.add("--------------------- end operation with zakaz = %s --------------" % zakaz)
        # если есть заказы на принудительное отключение, то отключаем их
        if spis_zakaz_for_compulsory_shutdown:
            compulsory_shutdown_of_service(spis_zakaz_for_compulsory_shutdown)
        log.add("--------------------- end operation write off of money for bill_account = %s -------------" % bill_account.id)
        log.add("***********************************************************************************************************")
    print 12345
    print message
    return message

